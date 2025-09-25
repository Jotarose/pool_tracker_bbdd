# Aerodrome Liquidity Pool Position Tracker

Este proyecto permite monitorizar y analizar posiciones de liquidez en pools DeFi, obteniendo métricas como PnL, impermanent loss, recompensas y más. Utiliza Web3 para interactuar con contratos inteligentes y almacena los datos en una base de datos SQL.

## Características

- Conexión a la blockchain mediante Web3.
- Obtención y análisis de posiciones NFT en pools.
- Cálculo de métricas financieras (PnL, ROI, impermanent loss, etc.).
- Almacenamiento de snapshots históricos en base de datos.
- Visualización y análisis de posiciones mediante graficos generados con mathplotlib.
- Automatización mediante GitHub Actions.

## Estructura del Proyecto
```` ├── main.py # Script principal: conecta, analiza y guarda posiciones 
 ├── run_plot.py # Script para visualizar posiciones 
 ├── core/ # Lógica principal: contratos, posiciones, matemáticas de pools 
 ├── db/ # Modelos y utilidades de base de datos 
 ├── analysis/ # Scripts de análisis y visualización 
 ├── config/ # Configuración de pools 
 ├── utils/ # Utilidades, modelos y ABIs 
 ├── requirements.txt # Dependencias del proyecto 
 ├── .env # Variables de entorno (no subir a git) 
 └── README.md
````
 
## Instalación

1. **Clona el repositorio:**
   ```sh
   git clone https://github.com/tuusuario/pool-position-tracker.git
   cd pool-position-tracker

2. **Crea un entorno virtual y activa:**
- python -m venv .venv
- source .venv/bin/activate  # En Windows: .venv\Scripts\activa

3. **Instala las dependencias:**
pip install -r requirements.txt

4. **Configura las variables de entorno**
- Crea un archivo .env con tus claves
- Tambien configura los pools en /config/pools_config.json
- RPC_URL=tu_rpc_url
- DATABASE_URL=sqlite:///positions.db

Uso:
- Ejecutar el seguimiento y guardado de posiciones: python [main.py](http://_vscodecontentref_/4)
- Visualizar posiciones y análisis: python [run_plot.py](http://_vscodecontentref_/5)

Automatización
El proyecto incluye un workflow de GitHub Actions para ejecutar el seguimiento cada 6 horas automáticamente. Consulta .github/workflows/run-cron.yml.

## English

This project allows you to monitor and analyze liquidity positions in DeFi pools, providing metrics such as PnL, impermanent loss, rewards, and more. It uses Web3 to interact with smart contracts and stores the data in an SQL database.

## Features

- Connects to the blockchain using Web3.  
- Retrieves and analyzes NFT positions in pools.  
- Calculates financial metrics (PnL, ROI, impermanent loss, etc.).  
- Stores historical snapshots in a database.  
- Visualizes and analyzes positions with charts generated using Matplotlib.  
- Automation through GitHub Actions.

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/pool-position-tracker.git
   cd pool-position-tracker
   
2. **Create and activate a virtual environment::**
- python -m venv .venv
- source .venv/bin/activate  # On Windows: .venv\Scripts\activate

3. **Install the dependencies:***
- pip install -r requirements.txt

4. **Set up enviroments variables:**
- Create a .env file with your keys:
   - RPC_URL=your_rpc_url
   - DATABASE_URL=sqlite:///positions.db
- Also configure the pools in /config/pools_config.json

Usage:
- Run tracking and save positions: python main.py
- Visualize positions and analysis: python run_plot.py

Automation
- The project includes a GitHub Actions workflow that runs the tracking automatically every 6 hours.
See .github/workflows/run-cron.yml.


Licencia
MIT
