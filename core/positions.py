import json
from datetime import datetime, timezone
from core import pool_math
from core import contracts
from core import tokens
from utils.models import MyPositionInfo

# Funcion para cargar todas las configuraciones de los pools
def load_pool_configs(filepath="config/pools_config.json"):
    with open(filepath, "r") as f:
        data = json.load(f)

    flat_configs = []
    for wallet in data:

        wallet_address = wallet['wallet_address']

        for position in wallet['positions']:
            flat_configs.append({
                "wallet_address": wallet_address,
                "nft_position_manager": position['nft_position_manager'],
                "pool_contract": position['pool_contract'],
                "amm_contract": position['amm_contract'],
                "gauge_contract": position['gauge_contract'],
                "initial_position": position['initial_position'],
                "staked_fees": position['staked_fees']
            })

    return flat_configs


# Funcion para obtener la posicion tal y como la quiero ver
def get_full_position_info(w3, config) -> MyPositionInfo:

    # CARGO CONFIGURACION DE UN POOL
    wallet_address = config['wallet_address']
    nft_position_manager = config['nft_position_manager']

    # Contratos
    pool_contract_position = contracts.get_pool_contract(w3, config['pool_contract']['address'], config['pool_contract']['abi_path'])
    # list_contract_functions(pool_contract_position)
    pool_contract_amm = contracts.get_pool_contract(w3, config['amm_contract']['address'], config['amm_contract']['abi_path'])
    pool_contract_gauge = contracts.get_pool_contract(w3, config['gauge_contract']['address'], config['gauge_contract']['abi_path'])
    
    # Datos en crudo de la posicion
    position_raw = contracts.get_position_info_raw(pool_contract_position, nft_position_manager)
    slot0_data = contracts.get_slot0_data(pool_contract_amm)  # Es un dataclass
    sqrt_price_x96 = slot0_data.sqrtPriceX96
    
    token0_info = tokens.get_token_info(w3, position_raw.token0)
    token1_info = tokens.get_token_info(w3, position_raw.token1)

    # Logica de calculo separada
    liquidity_per_token = pool_math.get_amounts_from_liquidity(w3, position_raw, sqrt_price_x96)  # Calcular cantidades de cada token según liquidez y rango
    actual_price_token0 = pool_math.get_token_price_USD(token0_info['symbol'])
    actual_price_token1 = pool_math.get_token_price_USD(token1_info['symbol'])
    price_tick_lower = pool_math.tick_to_price(position_raw.tick_lower, token0_info['decimals'], token1_info['decimals'])
    price_tick_upper = pool_math.tick_to_price(position_raw.tick_upper, token0_info['decimals'], token1_info['decimals'])
    price_tick_pool = pool_math.tick_to_price(slot0_data.tick, token0_info['decimals'], token1_info['decimals'])
    range_print, range_bool = pool_math.is_in_range(price_tick_lower, price_tick_upper, price_tick_pool)


    # Asigno automaticamente las staked_fees desde el json para automatizar.
    #staked_fees_token0, staked_fees_token1 = pool_math.input_staked_fees(token0_info, token1_info)
    staked_fees_token0 = config['staked_fees']['token0']
    staked_fees_token1 = config['staked_fees']['token1']

    # Obtengo las REWARDS en AERO no reclamadas que me da el pool
    non_claimed_rewards = float(contracts.get_rewards(w3, pool_contract_gauge, wallet_address, nft_position_manager))
    aero_price_in_usd = pool_math.get_token_price_USD("AERO")
    non_claimed_rewards_to_usd = non_claimed_rewards*aero_price_in_usd
    claimed_rewards = config["gauge_contract"]["claimed_rewards"]
    all_rewards = non_claimed_rewards + claimed_rewards
    all_rewards_to_usd = all_rewards * aero_price_in_usd

    # Obtengo la posicion inicial
    initial_pos = config['initial_position']
    mint_date_dt = datetime.fromisoformat(initial_pos['mint_date'].replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    time_in_pool = now - mint_date_dt
   
    
    token0_initial_position = initial_pos['token0']
    token1_initial_position = initial_pos['token1']
    initial_liquidity_USD = token0_initial_position * initial_pos["price_token0_USD"] + token1_initial_position * initial_pos["price_token1_USD"]

    # Calculo el PnL personalizado con las rewards -> es un diccionario
    pnl_custom = pool_math.calculate_pnl(
        token0_initial_position, 
        token1_initial_position, 
        initial_liquidity_USD, 
        liquidity_per_token, 
        actual_price_token0, 
        actual_price_token1, 
        all_rewards_to_usd, 
        staked_fees_token0, 
        staked_fees_token1
        )

    # Dataclass limpio con los datos procesados
    return MyPositionInfo(
        wallet_address = wallet_address,
        nft_position_manager = nft_position_manager,
        mint_date_dt = mint_date_dt,
        time_in_pool = time_in_pool,

        token0_address=position_raw.token0,
        token1_address=position_raw.token1,
        token0_name=token0_info['name'],
        token1_name=token1_info['name'],
        token0_symbol=token0_info['symbol'],
        token1_symbol=token1_info['symbol'],
        token0_decimals=token0_info['decimals'],
        token1_decimals=token1_info['decimals'],
        actual_price_token0 = actual_price_token0,
        actual_price_token1 = actual_price_token1,

        liquidity_token0=liquidity_per_token[0],
        liquidity_token1=liquidity_per_token[1],

        price_tick_lower = price_tick_lower,
        price_tick_upper = price_tick_upper,
        is_in_range_print = range_print,
        is_in_range_bool = range_bool,
        actual_pool_price = price_tick_pool, # Precio token0/token1
        aero_price_in_usd = aero_price_in_usd,

        non_claimed_rewards=non_claimed_rewards,
        non_claimed_rewards_to_usd=non_claimed_rewards_to_usd,
        claimed_rewards = claimed_rewards,
        all_rewards = all_rewards,
        all_rewards_to_usd = all_rewards_to_usd,

        staked_fees_token0 = staked_fees_token0,
        staked_fees_token1 = staked_fees_token1,

        token0_initial_position = token0_initial_position,
        token1_initial_position = token1_initial_position,
        initial_liquidity_USD = initial_liquidity_USD,

        pnl_usd = pnl_custom["pnl_usd"],
        pnl_percent = pnl_custom["pnl_percent"],
        pnl_usd_revert = pnl_custom["pnl_usd_revert"],
        pnl_percent_revert = pnl_custom["pnl_percent_revert"],
        actual_liquidity_usd = pnl_custom["actual_liquidity_usd"],
        impermanent_loss = pnl_custom["impermanent_loss"],
        il_percent = pnl_custom["il_percent"],
        staked_fees_token0_usd = pnl_custom["staked_fees_token0_usd"],
        staked_fees_token1_usd = pnl_custom["staked_fees_token1_usd"],
        roi = pnl_custom["roi"]
    )

# Funcion para imprimir una barra grafica en funcion del rango de precios
def print_price_range_bar(mypositioninfo, bar_width=30):

    p = mypositioninfo

    lower = p.price_tick_lower
    upper = p.price_tick_upper
    current = p.actual_pool_price
    pair_label = f"{p.token0_symbol}/{p.token1_symbol}"

# Normalizar posición actual entre [0, 1]
    if upper == lower:
        pos = 0.5
    else:
        pos = (current - lower) / (upper - lower)

    # Clamp entre [0, 1] para el marcador
    marker_index = int(pos * bar_width)

    bar = ["─"] * bar_width

    # Marcar fuera de rango con flechas
    if pos < 0:
        bar[0] = "⇤"
        marker_index = 0
    elif pos > 1:
        bar[-1] = "⇥"
        marker_index = bar_width - 1
    else:
        bar[marker_index] = "▲"

    # Crear los extremos con sus símbolos
    left = f"{lower:.5f} {pair_label}"
    right = f"{upper:.5f} {pair_label}"

    bar_str = "".join(bar)

    # Imprimir rango
    print(f"\nRANGO DE PRECIOS ELEGIDO {pair_label}:\n")
    print(f"{left} {bar_str} {right}")
    print(f"{' ' * (len(left) + 1 + marker_index)}│")
    print(f"{' ' * (len(left) + 1 + marker_index)}{current:.5f} (Precio actual)")
    print()

def print_pnls(mypositioninfo):
    p = mypositioninfo

    print("="*70)
    print(f"{'💰 RESULTADOS DE LA POSICIÓN (PnL)':^70}")
    print("-"*70)
    print(f"{'🔹 PnL CUSTOM':<36} | {'🔸 PnL REVERT (con IL)':<33}")
    print("-" * 70)

    print(f"{'PnL (USD)':<20}: $ {round(p.pnl_usd, 2):<8.2f}      | PnL (USD): $ {round(p.pnl_usd_revert, 2):<10.2f}")
    print(f"{'PnL (%)':<20}: {f'{round(p.pnl_percent, 2):.2f} %':<10}      | PnL (%): {f'{round(p.pnl_percent_revert, 2):.2f} %':<10}")
    print("-" * 70)
    print(f"{'Impermanent Loss':<15}: {f'{round(p.impermanent_loss, 2):.2f} $':<19} | IL (%): {f'{round(p.il_percent, 2):.2f} %':>10}")
    print(f"{'Retorno de inversion -> ROI (%)':<15}: {f'{round(p.roi, 2):.2f} %':<19}")

    print()

# Funcion para imprimir la fecha y tiempo en el pool
def print_time_in_pool(mypositioninfo):
    
    p = mypositioninfo
    days = p.time_in_pool.days
    hours = p.time_in_pool.seconds // 3600
    minutes = (p.time_in_pool.seconds % 3600) // 60

    print("📅  Fecha de minteo:", p.mint_date_dt.strftime("%b-%d-%Y %I:%M:%S %p UTC"))
    print(f"⏱️  Tiempo en el pool: {days} días, {hours} horas, {minutes} minutos")

    return None

# Funcion para imprimir la posicion del pool
def print_myPositionInfo(mypositioninfo): 
    
    p = mypositioninfo

    # Mostrar resultados por pantalla
    print(f"\n📊 Posición NFT: {p.nft_position_manager} — Pool: {p.token0_symbol}/{p.token1_symbol}")
    print("="*70)

    # Cabecera con columnas
    print(f"{'🔹 POSICIÓN INICIAL':<35} | {'🔸 POSICIÓN ACTUAL':<35}")
    print("-"*70)

     # Liquidez total
    print(f"{'Liquidez (USD)':<35} | {'Liquidez (USD)':<35}")
    print(f"$ {round(p.initial_liquidity_USD, 2):<33.2f} | $ {round(p.actual_liquidity_usd, 2):<35.2f}")
    print()

     # Token0 comparativa
    print(f"{p.token0_symbol + ' inicial':<35} | {p.token0_symbol + ' actual':<35}")
    print(f"{round(p.token0_initial_position, 2):<35.2f} | {round(p.liquidity_token0, 2):<35.2f}")
    print()

    # Token1 comparativa
    print(f"{p.token1_symbol + ' inicial':<35} | {p.token1_symbol + ' actual':<35}")
    print(f"{round(p.token1_initial_position, 2):<35.2f} | {round(p.liquidity_token1, 2):<35.2f}")
    print()

    # Tiempo en el pool
    print_time_in_pool(mypositioninfo)
    print()

    # Barra del rango de precios
    print_price_range_bar(p)
    print(f"El precio actual es de {round(p.actual_pool_price,7)} {p.token0_symbol}/{p.token1_symbol} --> {p.is_in_range_print}")
    print()

    # PnL e impermanent loss
    print_pnls(p)
    print()

    print("="*70)
    print(f"{'💰 RECOMPENSAS Y FEES':^70}")
    print("-"*70)

    # Rewards
    print(f"{'🔹 Rewards no reclamadas':<37} | {round(p.non_claimed_rewards,2):>8} AERO = {round(p.non_claimed_rewards_to_usd,2):>8} $USD")
    print(f"{'🔸 Total Rewards (claimed + unclaimed)':<35} | {round(p.all_rewards,2):>8} AERO = {round(p.all_rewards_to_usd,2):>8} $USD")


    print()

    # Fees
    print(f"{f'💵 Fees en {p.token0_symbol}':<35} | {round(p.staked_fees_token0,2):>8} {p.token0_symbol} = {round(p.staked_fees_token0_usd,2):>8} $USD")
    print(f"{f'💵 Fees en {p.token1_symbol}':<35} | {round(p.staked_fees_token1,2):>8} {p.token1_symbol} = {round(p.staked_fees_token1_usd,2):>8} $USD")
    print()

    # Precio actual AERO
    print(f"\nPrecio actual del AERO en USD segun Coingecko: {p.aero_price_in_usd} $USD")

    
    return None