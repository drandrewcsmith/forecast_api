"""empty message

Revision ID: 24d126496d4c
Revises:
Create Date: 2018-01-08 08:56:44.023986

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '24d126496d4c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "create table example ( "
        "    id int primary key "
        ")"
    )


def downgrade():
    op.execute('drop table if exists example')
