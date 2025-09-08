"""Add is_admin to User model

Revision ID: 212ebd3c6140
Revises: fc362fcdb5aa
Create Date: 2025-09-08

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '212ebd3c6140'
down_revision = 'fc362fcdb5aa'
branch_labels = None
depends_on = None

def upgrade():
    # Add the column with a temporary server_default=False to backfill existing rows
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(
            sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.false())
        )
    # Remove the server_default afterwards to avoid keeping a default at the DB level
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('is_admin', server_default=None)

def downgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('is_admin')