from core import tokens
from core import contracts
import requests
from decimal import Decimal
from utils.coingecko_token_ids import COINGECKO_IDS

import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Funcion para saber valor de liquidez real
def get_amounts_from_liquidity(w3, pos, sqrt_price_x96,):

    # Defino parametros a usar
    liquidity = pos.liquidity
    tick_lower = pos.tick_lower
    tick_upper = pos.tick_upper
    token0_address = pos.token0
    token1_address = pos.token1
    token0_info = tokens.get_token_info(w3, token0_address) # Diccionario, 0-name, 1-symbol, 2-decimals
    token1_info = tokens.get_token_info(w3, token1_address)

    # 1. Convertir ticks a precios sqrt
    sqrt_price = sqrt_price_x96 / (2 ** 96)
    sqrt_price_lower = 1.0001 ** (tick_lower / 2)
    sqrt_price_upper = 1.0001 ** (tick_upper / 2)

    if sqrt_price <= sqrt_price_lower:
        # Precio por debajo del rango: TODO en token0
        amount0 = liquidity * (sqrt_price_upper - sqrt_price_lower) / (sqrt_price_lower * sqrt_price_upper)
        amount1 = 0
    elif sqrt_price < sqrt_price_upper:
        # Dentro del rango: tienes ambos tokens
        amount0 = liquidity * (sqrt_price_upper - sqrt_price) / (sqrt_price * sqrt_price_upper)
        amount1 = liquidity * (sqrt_price - sqrt_price_lower)
    else:
        # Precio por encima del rango: TODO en token1
        amount0 = 0
        amount1 = liquidity * (sqrt_price_upper - sqrt_price_lower)

    amount0_legible = from_wei(amount0, token0_info['decimals'])
    amount1_legible = from_wei(amount1, token1_info['decimals'])

    return amount0_legible, amount1_legible

# Funcion para ver si estoy o no en rango
def is_in_range(price_tick_lower, price_tick_upper, price_tick):


    if price_tick > price_tick_upper:
        range_print = "FUERA DE RANGO, superado por arriba."
        range_bool = False
    elif price_tick < price_tick_lower:
        range_print = "FUERA DE RANGO, superado por abajo."
        range_bool = False
    else:
        range_print = "DENTRO DE RANGO, estas recibiendo fees."
        range_bool = True

    return range_print, range_bool
    
    
# Convertir un tick a un precio legible (token1/token0) teniendo en cuenta decimales
def tick_to_price(tick, decimals_token0, decimals_token1):
    raw_price = 1.0001 ** tick
    adjusted_price = raw_price * (10 ** (decimals_token0 - decimals_token1))
    return adjusted_price

# Convertir de wei a legible
def from_wei(amount, decimals):
    return amount / (10 ** decimals)

# Cache para no hacer dos peticiones al mismo precio de una iteraccion
_price_cache = {} # es un diccionario vacio

# Saca los precios de los tokens en USD
def get_token_price_USD(token_symbol: str) -> float:

    token_symbol = token_symbol.upper()

    # Devuelve desde la caché si ya se pidió antes
    if token_symbol in _price_cache:
        return _price_cache[token_symbol]


    if token_symbol not in COINGECKO_IDS:
        logging.error(f"[Error] Símbolo '{token_symbol}' no está definido en el diccionario de IDs de Coingecko.")
        return None
    
    token_id = COINGECKO_IDS[token_symbol]

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": token_id,
        "vs_currencies": "usd"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        price = data[token_id]['usd']
        _price_cache[token_symbol] = price  # Guarda en caché
        return price

    except requests.RequestException as e:
        logging.error(f"[Error] Error al consultar el precio de {token_symbol}: {e}")
        return None
    except KeyError:
        logging.error(f"[Error] Respuesta inválida de Coingecko para {token_symbol}: {KeyError}")
        return None
    

def calculate_pnl(token0_initial_amount, token1_initial_amount, initial_liquidity_USD, liquidity_per_token, actual_price_token0, actual_price_token1, all_rewards_to_USD, staked_fees_token0, staked_fees_token1) -> dict:
    
    # Asigno parametros
    posicion_inicial = initial_liquidity_USD
    actual_liquidity_usd = liquidity_per_token[0]*actual_price_token0 + liquidity_per_token[1]*actual_price_token1
    staked_fees_token0_usd = staked_fees_token0 * actual_price_token0
    staked_fees_token1_usd = staked_fees_token1 * actual_price_token1
    actual_fees_usd = staked_fees_token0_usd + staked_fees_token1_usd
    posicion_actual = actual_liquidity_usd + all_rewards_to_USD + actual_fees_usd
    
    # Simular cuánto valdrían los tokens hoy si simplemente los hubieras holdeado
    hodl_value = (
    token0_initial_amount * actual_price_token0 +
    token1_initial_amount * actual_price_token1
    )

    # Impermanent loss, tambien conocido como divergence_loss
    imp_loss = hodl_value - actual_liquidity_usd
    il_percent = ((-1)*imp_loss / posicion_inicial)*100 if posicion_inicial != 0 else 0

    # Calculo PnL
    pnl_usd = posicion_actual - posicion_inicial # La pos_actual(act_liq + fees + rewards) menos la pos_inicial
    pnl_percent = (pnl_usd / posicion_inicial)*100 if posicion_inicial != 0 else 0.0

    pnl_usd_revert = actual_fees_usd + all_rewards_to_USD - imp_loss # Formula de revert.com
    pnl_percent_revert = (pnl_usd_revert / posicion_inicial)*100 if posicion_inicial != 0 else 0.0  

    # Calculo ROI (%) = (ganancia neta / inv. inicial) *100 
    # Ganancia neta = (pos. actual + fees + rewards) - inv. inicial
    ganancia_neta = posicion_actual - posicion_inicial
    roi = (ganancia_neta / posicion_inicial) * 100
    
    return {
        "pnl_usd": pnl_usd,
        "pnl_usd_revert": pnl_usd_revert,
        "pnl_percent": pnl_percent,
        "pnl_percent_revert": pnl_percent_revert,
        "actual_liquidity_usd": actual_liquidity_usd,
        "impermanent_loss": (-1)*imp_loss,
        "staked_fees_token0_usd": staked_fees_token0_usd,
        "staked_fees_token1_usd": staked_fees_token1_usd,
        "il_percent": il_percent,
        "roi": roi
    }

# Leer las fees stakeades en el gauge contract por token
# def input_staked_fees(_token0_info, _token1_info):

#     token0_info = _token0_info
#     token1_info = _token1_info
    
#     while True:
#         try:
#             fees_token0 = float(input(f"\nIntroduce las fees que tienes de {token0_info['symbol']}: "))
#             fees_token1 = float(input(f"Introduce las fees que tienes de {token1_info['symbol']}: "))
#             if fees_token0 < 0 or fees_token1 < 0:
#                 print("Por favor, introduce números positivos.")
#                 continue
#             return fees_token0, fees_token1
#         except ValueError:
#             print("Entrada inválida. Por favor, introduce un número válido.")
    
