# Funcion para guardar los datos de la posicion
from datetime import datetime
from .database import SessionLocal
from .models import PositionSnapshot
from datetime import datetime, timezone
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_snapshot(position):
    session = SessionLocal()
    try:
        snapshot = PositionSnapshot(
            timestamp=datetime.now(timezone.utc),
            wallet=position.wallet_address,
            nft_position_manager=position.nft_position_manager,
            roi=position.roi,
            pnl_usd=position.pnl_usd,
            pnl_percent=position.pnl_percent,
            pnl_usd_revert = position.pnl_usd_revert,
            pnl_percent_revert = position.pnl_percent_revert,
            liquidity_usd=position.actual_liquidity_usd,
            rewards_usd=position.all_rewards_to_usd,
            staked_fees_token0_usd = position.staked_fees_token0_usd,
            staked_fees_token1_usd = position.staked_fees_token1_usd,
            is_in_range = position.is_in_range_bool
        )
        session.add(snapshot)
        session.commit()
    except Exception as e:
        logger.error("❌ Error al guardar snapshot:", e)
        session.rollback()
    finally:
        session.close()
