from core import pool_math
from utils.coingecko_token_ids import COINGECKO_IDS


price_aero = pool_math.get_token_price_USD("EURC")
if price_aero is not None:
    print(f"Precio de AERO: ${price_aero}")
else:
    print("No se pudo obtener el precio de AERO.")

