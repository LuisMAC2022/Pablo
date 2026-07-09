from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from app.config import get_settings
from app.models import Base


config = context.config

settings = get_settings()
# Alembic debe usar la misma URL de base de datos que la aplicación, no un
# valor duplicado en alembic.ini.
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Base.metadata es el contrato que usa Alembic para comparar los modelos ORM
# contra el esquema real durante `alembic revision --autogenerate`.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecuta migraciones sin abrir una conexión DBAPI.

    Alembic emite SQL usando la URL configurada; esto permite revisar o generar
    scripts en entornos donde no se debe conectar directamente a la base de datos.
    """

    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones con una conexión real a la base de datos."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
