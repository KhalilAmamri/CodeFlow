"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
# ============================================================================
# ALEMBIC MIGRATION SCRIPT TEMPLATE
# ============================================================================
# This template is used by Flask-Migrate to generate database migration scripts
# It provides the basic structure for upgrade and downgrade operations

# Alembic operation imports for database schema modifications
from alembic import op
import sqlalchemy as sa

# Additional imports for custom migration operations
${imports if imports else ""}

# ============================================================================
# MIGRATION METADATA
# ============================================================================

# Revision identifiers, used by Alembic for version control
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


# ============================================================================
# MIGRATION OPERATIONS
# ============================================================================

def upgrade():
    """
    Upgrade database schema to this revision.
    
    This function contains the operations needed to transform the database
    from the previous revision to the current one. It is executed when
    running 'flask db upgrade'.
    
    Operations typically include:
    - Creating new tables
    - Adding new columns
    - Modifying existing columns
    - Creating indexes or constraints
    """
    ${upgrades if upgrades else "pass"}


def downgrade():
    """
    Downgrade database schema from this revision.
    
    This function contains the operations needed to reverse the changes
    made in the upgrade function. It is executed when running
    'flask db downgrade'.
    
    Operations typically include:
    - Dropping tables
    - Removing columns
    - Reverting column modifications
    - Dropping indexes or constraints
    """
    ${dowgrades if downgrades else "pass"}
