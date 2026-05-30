"""Database models and async session factory."""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class SignalModel(Base):
    __tablename__ = "signals"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    agent: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    summary: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_data: Mapped[dict] = mapped_column(JSON, default={})
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default={})
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InsightModel(Base):
    __tablename__ = "insights"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    narrative: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String)
    recommended_actions: Mapped[list] = mapped_column(JSON, default=[])
    affected_domains: Mapped[list] = mapped_column(JSON, default=[])
    signal_ids: Mapped[list] = mapped_column(JSON, default=[])
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WatchlistModel(Base):
    __tablename__ = "watchlist"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)  # competitor|customer|vendor
    domain: Mapped[str] = mapped_column(String)    # gtm|finance|security|all


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
