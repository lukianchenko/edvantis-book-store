"""empty message

Revision ID: 31457bf25c7b
Revises: a10477f3d4d9
Create Date: 2022-08-15 09:10:37.884204

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '31457bf25c7b'
down_revision = 'a10477f3d4d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('books', 'book_cover')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('book_cover', postgresql.BYTEA(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###