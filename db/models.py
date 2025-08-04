# Definiremos como queremos que sean las tablas.
# Con sqlalchemy puedo trabajar con BBDD usando python puro, no tengo que usar sentencias SQL directamente.
from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PositionSnapshot(Base):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)
    wallet = Column(String)
    nft_position_manager = Column(String)
    roi = Column(Float)
    pnl_usd = Column(Float)
    pnl_percent = Column(Float)
    pnl_usd_revert = Column(Float)
    pnl_percent_revert = Column(Float)
    liquidity_usd = Column(Float)
    rewards_usd = Column(Float)
    staked_fees_token0_usd = Column(Float)
    staked_fees_token1_usd = Column(Float)
    is_in_range = Column(Boolean)
