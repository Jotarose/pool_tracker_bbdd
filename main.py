from web3 import Web3 # Importo la liberia para web3
from dotenv import load_dotenv # Para interactuar con env
# Tengo que cargarlo primero para poder cargar bien la BBDD
load_dotenv() # Carga las variables del .env, disponibles globalmente

import os # Sirve para acceder a las variables de entorno
import logging
from core import positions
from db.database import init_db
from db.save_positions import save_snapshot


# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv() # Carga las variables del .env, disponibles globalmente
RPC_URL = os.getenv("RPC_URL")

# Conexion al nodo RPC
w3 = Web3(Web3.HTTPProvider(RPC_URL))


# Funcion principal
def main():

    init_db()  # ✅ crea la tabla si no existe

    if not w3.is_connected():
        logging.error("❌ Error al conectar con la blockchain.")
        return
    
    logging.info("✅ Conectado a la blockchain correctamente.")
    
    configs = positions.load_pool_configs()

    for config in configs:

        wallet = config['wallet_address']
        nft = config['nft_position_manager']
        logging.info(f"Procesando wallet {wallet}, NFT {nft}...")

        try:
            full_position_info = positions.get_full_position_info(w3, config)
            save_snapshot(full_position_info)
        except Exception as e:
            logging.exception(f"⚠️ Error procesando {wallet} / {nft}: {e}")

   

# Ejecucion del codigo
if __name__ == "__main__":
    main()