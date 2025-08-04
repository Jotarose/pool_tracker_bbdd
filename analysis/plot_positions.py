import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from db.query_positions import get_snapshots_by_position
from core import positions

def plot_roi_over_time(wallet, nft_positions):

    # Acepta un solo string o una lista
    if isinstance(nft_positions, str):
        nft_positions = [nft_positions]

    plt.figure(figsize=(10, 5))

    for nft in nft_positions:
        snapshots = get_snapshots_by_position(wallet, nft)
        if not snapshots:
            print(f"⚠️ No hay datos para NFT {nft}")
            continue

        timestamps = [s.timestamp for s in snapshots]
        rois = [s.roi for s in snapshots]
        plt.plot(timestamps, rois, marker='o', label=f'NFT {nft}')

    if not plt.gca().has_data():
        print("❌ No hay datos para mostrar.")
        return

    plt.title(f'ROI Over Time - Wallet: {wallet}')
    plt.xlabel('Timestamp')
    plt.ylabel('ROI')
    plt.grid(True)
    plt.legend()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m %H:%M'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.show()


def plot_pnl_over_time(wallet, nft_positions):
    # Acepta un solo string o una lista
    if isinstance(nft_positions, str):
        nft_positions = [nft_positions]

    plt.figure(figsize=(10, 5))

    for nft in nft_positions:
        snapshots = get_snapshots_by_position(wallet, nft)
        if not snapshots:
            print(f"⚠️ No hay datos para NFT {nft}")
            continue

        timestamps = [s.timestamp for s in snapshots]
        pnls = [s.pnl_percent for s in snapshots]
        plt.plot(timestamps, pnls, marker='o', label=f'NFT {nft}')

    if not plt.gca().has_data():
        print("❌ No hay datos para mostrar.")
        return

    plt.title(f'PnL Over Time - Wallet: {wallet}')
    plt.xlabel('Timestamp')
    plt.ylabel('PNL')
    plt.grid(True)
    plt.legend()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m %H:%M'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.show()

# Funcion para elegir la cartera    
def elegir_wallet():
    configs = positions.load_pool_configs()

    # Obtener wallets únicas
    wallets = sorted(set(config["wallet_address"] for config in configs))

    print("🔍 Elige una wallet:\n")
    for idx, wallet in enumerate(wallets, 1):
        print(f"{idx}. {wallet}")

    while True:
        try:
            eleccion = int(input("\nIntroduce el número de la wallet: "))
            if 1 <= eleccion <= len(wallets):
                return wallets[eleccion - 1]
            else:
                print("❌ Número fuera de rango.")
        except ValueError:
            print("❌ Entrada no válida. Debe ser un número.")

# Funcion para elegir varios nft_positions_manager
def elegir_varios_nfts(wallet):
    configs = positions.load_pool_configs()

    # Filtra todas las configuraciones para la wallet
    wallet_positions = [cfg for cfg in configs if cfg["wallet_address"] == wallet]

    if not wallet_positions:
        print("❌ No se encontraron posiciones para la wallet.")
        return []

    # Extrae los nft_position_manager de cada configuración (cada una es una posición)
    nfts = [pos["nft_position_manager"] for pos in wallet_positions]

    print(f"\n🔍 Elige una o varias posiciones NFT de la wallet {wallet} (separadas por coma):\n")
    for idx, nft in enumerate(nfts, 1):
        print(f"{idx}. {nft}")

    while True:
        entrada = input("\nIntroduce los números de los NFT (ej: 1,3): ")
        try:
            indices = [int(x.strip()) for x in entrada.split(",")]
            if all(1 <= idx <= len(nfts) for idx in indices):
                # Devuelve las configuraciones completas para los nft elegidos
                return [wallet_positions[idx - 1]['nft_position_manager'] for idx in indices]
            else:
                print("❌ Algún número está fuera de rango.")
        except ValueError:
            print("❌ Entrada no válida. Usa solo números separados por coma.")

    
    # Menú de selección
def menu_selec(wallet, nft_positions):    
    while True:
        print("\n¿Qué gráfico quieres generar?")
        print("1. ROI")
        print("2. PNL")
        print("3. Ambos")
        opcion = input("Selecciona una opción (1/2/3): ").strip()

        if opcion == "1":
            plot_roi_over_time(wallet, nft_positions)
            break
        elif opcion == "2":
            plot_pnl_over_time(wallet, nft_positions)
            break
        elif opcion == "3":
            plot_roi_over_time(wallet, nft_positions)
            plot_pnl_over_time(wallet, nft_positions)
            break
        else:
            print("❌ Opción no válida. Intenta con 1, 2 o 3.")