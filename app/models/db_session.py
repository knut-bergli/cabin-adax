from pathlib import Path
from typing import Optional, Annotated, Any, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlmodel import SQLModel
from sqlmodel.sql.expression import Select, SelectOfScalar

_engine: Optional[AsyncEngine] = None
_async_session: Optional[AsyncSession] = None
_async_session_maker: Optional[async_sessionmaker] = None


# Removes SQLModel error warning
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore


async def create_database_and_tables() -> None:
    """
    Creates the database and initializes all tables.

    This function asynchronously establishes a connection to the database
    using the provided engine, creates the database schema, and initializes
    all defined tables using the metadata of the SQLModel.

    Raises
    ------
    No exceptions are explicitly raised by this function itself, but any
    errors related to the database connection or schema creation might
    surface during its execution.
    """
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call global_init_database() first.")
    async with _engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def global_init_database(db_file: str) -> None:
    """
    Initializes the global database connection and session maker.

    This function sets up the database engine and session factory for
    asynchronous interactions with the database. It ensures the specified
    database file's parent directory is created if it doesn't exist and
    configures an SQLite connection using the provided database file
    path. Finally, it initiates the process to create necessary
    database tables.

    Arguments:
        db_file: str
            The file path for the SQLite database, specifying the location
            where the database file should be stored.

    Returns:
        None
    """
    global _engine
    global _async_session_maker

    if _async_session_maker is not None:
        return

    folder = Path(db_file).parent
    folder.mkdir(parents=True, exist_ok=True)

    conn_str = 'sqlite+aiosqlite:///' + db_file.strip()

    # echo = False to prevent logging to sys.stdout via SQLAlchemy's internal mechanism.
    _engine = create_async_engine(conn_str, echo=False, future=True, connect_args={"check_same_thread": False})
    _async_session_maker = async_sessionmaker(_engine, autocommit=False, autoflush=False, expire_on_commit=False)

    await create_database_and_tables()


async def get_async_session() -> AsyncGenerator[AsyncSession | Any, Any]:
    """
    Provides an asynchronous generator for creating and managing a database session.

    This function ensures that a new asynchronous session is created using the
    session factory and yielded. The session is managed effectively and can
    be used within an asynchronous context. It simplifies working with databases
    while ensuring proper lifecycle management.

    Yields:
        AsyncSession | Any: An asynchronous database session object that can
        be used for performing database operations.

    """
    if _async_session_maker is None:
        from app.config.load_environment import get_settings, resolve_path
        db_file = resolve_path('cabin_hub_storage/db') / get_settings().DB_NAME
        await global_init_database(str(db_file))

    if _async_session_maker is None:
        raise RuntimeError("Database could not be initialized.")

    async with _async_session_maker() as db:
        yield db
        # try:
        #     yield db
        # finally:
        #     await db.close()


db_dependency: type[AsyncSession] = Annotated[AsyncSession, Depends(get_async_session)]
