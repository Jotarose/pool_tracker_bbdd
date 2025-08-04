from db.database import SessionLocal
from db.models import PositionSnapshot

def get_all_snapshots():
    session = SessionLocal()
    try:
        snapshots = session.query(PositionSnapshot).all()
        return snapshots
    finally:
        session.close()

def get_snapshots_by_position(wallet: str, nft_position_manager: str):
    session = SessionLocal()
    try:
        snapshots = session.query(PositionSnapshot).filter(
            PositionSnapshot.wallet == wallet,
            PositionSnapshot.nft_position_manager == nft_position_manager
        ).order_by(PositionSnapshot.timestamp).all()
        return snapshots
    finally:
        session.close()
