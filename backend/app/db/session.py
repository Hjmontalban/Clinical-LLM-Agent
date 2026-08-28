import json
import logging
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class ResearchRecord(Base):
    __tablename__ = "research_queries"

    id = Column(String, primary_key=True)
    question = Column(Text, nullable=False)
    status = Column(String, default="queued")
    result_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)


class PaperRecord(Base):
    __tablename__ = "papers"

    id = Column(String, primary_key=True)
    title = Column(Text, nullable=False)
    abstract = Column(Text, nullable=True)
    authors = Column(Text, nullable=True)
    year = Column(Integer, nullable=True)
    journal = Column(String, nullable=True)
    doi = Column(String, nullable=True)
    pmid = Column(String, nullable=True)
    pmcid = Column(String, nullable=True)
    url = Column(String, nullable=True)
    source = Column(String, nullable=True)
    study_type = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


_db_initialized = False
engine = None
async_session = None


def _get_engine():
    global engine, async_session
    if engine is None:
        settings = get_settings()
        connect_args = {}
        if settings.database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            connect_args=connect_args,
        )
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine


async def init_db() -> None:
    global _db_initialized
    if _db_initialized:
        return
    eng = _get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    _db_initialized = True
    logger.info("Database initialized")


class ResearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, research_id: str, question: str) -> ResearchRecord:
        record = ResearchRecord(id=research_id, question=question, status="queued")
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get(self, research_id: str) -> ResearchRecord | None:
        result = await self.session.execute(
            select(ResearchRecord).where(ResearchRecord.id == research_id)
        )
        return result.scalar_one_or_none()

    async def update(self, research_id: str, status: str, result: dict | None = None) -> None:
        record = await self.get(research_id)
        if not record:
            return
        record.status = status
        if result is not None:
            record.result_json = json.dumps(result, default=str)
        if status == "completed":
            record.completed_at = datetime.now(timezone.utc)
        await self.session.commit()

    async def list_recent(self, limit: int = 20) -> list[ResearchRecord]:
        result = await self.session.execute(
            select(ResearchRecord).order_by(ResearchRecord.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def save_paper(self, paper_id: str, data: dict) -> None:
        existing = await self.session.get(PaperRecord, paper_id)
        if existing:
            return
        record = PaperRecord(
            id=paper_id,
            title=data.get("title", ""),
            abstract=data.get("abstract"),
            authors=json.dumps(data.get("authors", [])),
            year=data.get("year"),
            journal=data.get("journal"),
            doi=data.get("doi"),
            pmid=data.get("pmid"),
            pmcid=data.get("pmcid"),
            url=data.get("url"),
            source=data.get("source"),
            study_type=data.get("study_type"),
            metadata_json=json.dumps(data),
        )
        self.session.add(record)
        await self.session.commit()

    async def get_paper(self, paper_id: str) -> PaperRecord | None:
        return await self.session.get(PaperRecord, paper_id)


async def get_db_session() -> AsyncSession:
    factory = get_session_factory()
    return factory()


def get_session_factory():
    _get_engine()
    return async_session
