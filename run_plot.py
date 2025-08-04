from analysis import plot_positions

# Elegir la wallet y las posiciones a analizar.
wallet = plot_positions.elegir_wallet()
nft_positions = plot_positions.elegir_varios_nfts(wallet)


plot_positions.menu_selec(wallet, nft_positions)