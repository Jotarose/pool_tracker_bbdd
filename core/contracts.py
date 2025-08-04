from web3 import Web3
from utils.models import PositionInfoRaw
from utils.models import Slot0Info
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Funcion que carga un contrato dado su ABI y ADDRESS
def get_pool_contract(w3, address: str, abi_path: str):
    try:
        with open(abi_path) as f:
            abi = json.load(f)
    except FileNotFoundError:
        logging.exception(f"ERROR: No se encontró el archivo ABI en {abi_path}: {FileNotFoundError}")
        return None
    except json.JSONDecodeError:
        logging.exception(f"ERROR: Archivo ABI no es un JSON válido: {json.JSONDecodeError}")
        return None
    
    contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)
    return contract

# Funcion para listar las funciones publicas del contrato
def list_contract_functions(contract):
    logging.info("\nFunciones públicas del contrato de posicion:")
    for func in contract.all_functions():
        print(f"- {func.fn_name}")


# Funcion para obtener la posicion actual dentro de un pool 
def get_position_info_raw(contract, token_id) -> PositionInfoRaw:

    try:

        pos = contract.functions.positions(token_id).call() # Saco mi posicion en el contrato.
        
        # Creo un diccionario con toda la informacion de mi posicion bien documentada
        return PositionInfoRaw(
            nonce=pos[0],
            operator=pos[1],
            token0=pos[2], # Direccion del token0
            token1=pos[3], # Direccion del token1
            fee=pos[4], # The fee associated with the pool, lo que cobra el pool por tx - fee * 0.0001 (%) - NO LO TENGO CLARO
            tick_lower=pos[5], # Limite inferior de rango de mi posicion - En unidades cambiadas --> 
            tick_upper=pos[6], # Limite superior de rango de mi posicion
            liquidity=pos[7], # Liquidez mia depositada. - Entero, usar formulas para convertir
            fee_growth_inside0_Last_X128=pos[8], # Acumulado de fees de token0 en mi rango - Dividir por 2^128
            fee_growth_inside1_Last_X128=pos[9], # Acumulado de fees de token1 en mi rango - Dividir por 2^128
            tokens_owed_0=pos[10], # Fees no recolectados del token0 expresado en wei
            tokens_owed_1=pos[11], # Fees no recolectados del token1 expresado en wei
        )

        print("\n📊 Datos detallados de la posición:")
        for k, v in position_info_raw.items():
            print(f"- {k}: {v}")

    
    except Exception as e:
        print(f"❌ Error al obtener la posición: {e}")
        return None


# Slot 0 - Para sacar informacion importante del contrato del pool_AMM
def get_slot0_data(pool_contract) -> Slot0Info:
    try:
        slot0 = pool_contract.functions.slot0().call()
        return Slot0Info(
            sqrtPriceX96=slot0[0],
            tick=slot0[1],
            observationIndex=slot0[2],
            observationCardinality=slot0[3],
            observationCardinalityNext=slot0[4],
            unlocked=slot0[5]
        )
    except Exception as e:
        logging.error(f'❌ Error al obtener slot0(): {e}')
        return None

# Funciones para sacar el feeGrowthGlobal
def get_feeGrowthGlobal_0_X128(pool_contract):
    try:
        feeGrowthGlobal_0_X128 = pool_contract.functions.feeGrowthGlobal0X128.call()

        return feeGrowthGlobal_0_X128
    
    except Exception as e:
        logging.error(f'❌ Error al obtener feeGrowthGlobal0X128: {e}')
        return None
    
def get_feeGrowthGlobal_1_X128(pool_contract):
    try:
        feeGrowthGlobal_1_X128 = pool_contract.functions.feeGrowthGlobal1X128.call()

        return feeGrowthGlobal_1_X128
    
    except Exception as e:
        logging.error(f"❌ Error al obtener feeGrowthGlobal1X128: {e}")
        return None
    
def get_rewards(w3, pool_contract_gauge, wallet_address, nft_position_manager):

    # Necesito convertir la direccion de wallet en formato checksum que me pide la funcion
    account = w3.to_checksum_address(wallet_address)
    rewards = pool_contract_gauge.functions.earned(account, nft_position_manager).call() # Funcion del contrato (ABI) que me devuelve las rewards para una NFT position
    rewards_human = w3.from_wei(rewards, 'ether')

    return rewards_human

