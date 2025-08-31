# ============================================================================
# FLASK-MIGRATE ENVIRONMENT CONFIGURATION
# ============================================================================
# This file configures the Alembic migration environment for Flask applications
# It handles database engine configuration, metadata setup, and migration execution

# Standard library imports for logging configuration
import logging
from logging.config import fileConfig

# Flask imports for application context access
from flask import current_app

# Alembic imports for migration framework
from alembic import context

# ============================================================================
# ALEMBIC CONFIGURATION SETUP
# ============================================================================

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


# ============================================================================
# DATABASE ENGINE CONFIGURATION
# ============================================================================

def get_engine():
    """
    Retrieve the database engine from Flask-SQLAlchemy.
    
    This function handles compatibility between different versions of Flask-SQLAlchemy.
    It attempts to get the engine using the newer API first, then falls back to
    the legacy method if needed.
    
    Returns:
        Engine: SQLAlchemy database engine instance
    
    Raises:
        AttributeError: If database engine cannot be retrieved
    """
    try:
        # This works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # This works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    """
    Get the database connection URL as a string.
    
    This function retrieves the database URL from the engine and formats it
    properly for Alembic configuration, handling special characters and
    password encoding.
    
    Returns:
        str: Formatted database connection URL
    """
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# ============================================================================
# METADATA AND CONFIGURATION SETUP
# ============================================================================

# Add your model's MetaData object here for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# Set the database URL in Alembic configuration
config.set_main_option('sqlalchemy.url', get_engine_url())

# Get the target database instance from Flask-SQLAlchemy
target_db = current_app.extensions['migrate'].db

# Other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_metadata():
    """
    Retrieve the database metadata for migration operations.
    
    This function handles both single and multiple metadata scenarios,
    ensuring compatibility with different SQLAlchemy configurations.
    
    Returns:
        MetaData: Database metadata object for migrations
    """
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


# ============================================================================
# MIGRATION EXECUTION FUNCTIONS
# ============================================================================

def run_migrations_offline():
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    
    This mode is useful for generating SQL scripts without requiring
    a live database connection.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine and associate
    a connection with the context. This is the standard mode for
    applying migrations to a live database.
    
    This function also includes a callback to prevent auto-migration
    generation when there are no schema changes detected.
    """

    # This callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # Reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    # Configure revision directives processing
    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    # Get database connection
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()


# ============================================================================
# MIGRATION EXECUTION ENTRY POINT
# ============================================================================

# Determine which migration mode to use based on context
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
