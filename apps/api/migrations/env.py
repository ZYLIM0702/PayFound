from alembic import context
from sqlalchemy import engine_from_config, pool
from app.database import Base, DATABASE_URL
from app import models
from app.connectors import models as connector_models
from app.intelligence import models as intelligence_models
from app.pos_plugin import models as pos_plugin_models
from app import basket as basket_models  # noqa: F401

config = context.config
config.set_main_option('sqlalchemy.url', DATABASE_URL.replace('%', '%%'))
target_metadata = Base.metadata

if context.is_offline_mode():
    context.configure(url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = engine_from_config(config.get_section(config.config_ini_section), prefix='sqlalchemy.', poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True, render_as_batch=connection.dialect.name == 'sqlite')
        with context.begin_transaction():
            context.run_migrations()
