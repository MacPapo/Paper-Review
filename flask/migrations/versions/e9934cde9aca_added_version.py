"""added version

Revision ID: e9934cde9aca
Revises: 3a31af6bf550
Create Date: 2023-05-05 13:28:00.671391

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e9934cde9aca'
down_revision = '3a31af6bf550'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('version',
    sa.Column('vid', sa.Integer(), nullable=False),
    sa.Column('nversion', sa.Integer(), nullable=False),
    sa.Column('PName', sa.String(length=64), nullable=False),
    sa.Column('PDescription', sa.Text(), nullable=False),
    sa.Column('PState', postgresql.ENUM('Approved', 'Sumbmitted', 'Requires changes', 'Not Approved', name='status_enum'), nullable=True),
    sa.Column('pid', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['pid'], ['project.pid'], ),
    sa.PrimaryKeyConstraint('vid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('version')
    # ### end Alembic commands ###
