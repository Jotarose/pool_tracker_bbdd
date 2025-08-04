from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class PositionInfoRaw:
    nonce: int  # uint96 en la blockchain, en Python lo representamos como int (no hay uint)
    operator: str  # dirección Ethereum, que es un string (hex)
    token0: str  # dirección Ethereum (hex string)
    token1: str  # dirección Ethereum (hex string)
    fee: int  # uint24, lo representamos como int
    tick_lower: int  # int24, representamos como int normal
    tick_upper: int  # int24, representamos como int normal
    liquidity: int  # uint128, representamos como int (Python puede manejar enteros grandes)
    fee_growth_inside0_Last_X128: int  # uint256, lo que ha crecido el fee dentro del rango cuando se actualizó la posición por última vez
    fee_growth_inside1_Last_X128: int  # uint256, idem
    tokens_owed_0: int  # uint128, idem
    tokens_owed_1: int  # uint128, idem

@dataclass
class Slot0Info:
    sqrtPriceX96: int  # uint160, representamos como int
    tick: int  # int24, representamos como int
    observationIndex: int  # uint16, representamos como int
    observationCardinality: int  # uint16, representamos como int
    observationCardinalityNext: int  # uint16, representamos como int
    unlocked: bool  # boolean

@dataclass
class MyPositionInfo:
    wallet_address: str
    nft_position_manager: int
    mint_date_dt: datetime
    time_in_pool: timedelta

    token0_address: str  # dirección Ethereum del token0 (hex string)
    token1_address: str  # dirección Ethereum del token1 (hex string)
    token0_name: str # string con el nombre completo del token0
    token1_name: str # string con el nombre completo del token1
    token0_symbol: str # string con el nombre corto del token0
    token1_symbol: str # string con el nombre corto del token1
    token0_decimals: int # Numero de decimales del token0
    token1_decimals: int # Numero de decimales del token1
    liquidity_token0: float # Cantidad del token0 en el pool
    liquidity_token1: float # Cantidad del token1 en el pool
    actual_price_token0: float
    actual_price_token1: float
    actual_liquidity_usd: float

    price_tick_lower: float  # Rango inferior elegido en precio del token1
    price_tick_upper: float  # Rango superior elegido en precio del token2
    is_in_range_print: str # String que me confirma si el precio del token1 esta dentro de mis rangos
    is_in_range_bool: bool
    actual_pool_price: float # Precio actual del token 1 en el pool de liquidez
    aero_price_in_usd: float
    
    staked_fees_token0: float # fees staked del token0 en token0
    staked_fees_token1: float # fees staked del token1 en token1
    staked_fees_token0_usd: float
    staked_fees_token1_usd: float

    non_claimed_rewards: float # Recomepensas que otorga el POOL no recogidas
    non_claimed_rewards_to_usd: float # Convierto las recompensas en USD con la API de Coingecko
    claimed_rewards: float # Se introducen a mano
    all_rewards: float
    all_rewards_to_usd: float
    
    token0_initial_position: float # Cantidad inicial token0 medida en su token
    token1_initial_position: float # Cantidad inicial token1 medida en su token
    initial_liquidity_USD: float # Liquidez inicial total en USD

    pnl_usd: float # El PnL customizado en dolares
    pnl_percent: float # El PnL en terminos de % respecto a la posicion inicial
    pnl_usd_revert: float # Calculo del PnL con el IMP_LOSS asi lo hacen en revert.com
    pnl_percent_revert: float
    impermanent_loss: float # Diferencia de valor entre holdear desde el inicio o meterse en el pool
    il_percent: float # lo mismo en porcentaje
    roi: float # ROI (%) = (ganancia_neta / inversion_inicial)*100