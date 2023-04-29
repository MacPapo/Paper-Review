"""Add User, Researcher, PDF Table

Revision ID: 135962f82c84
Revises: 
Create Date: 2023-04-29 22:17:55.939117

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '135962f82c84'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pdf',
    sa.Column('id', postgresql.BYTEA(), nullable=False),
    sa.Column('key', postgresql.BYTEA(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('uid', sa.String(length=16), nullable=False),
    sa.Column('first_name', sa.String(length=32), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('birthdate', sa.DateTime(), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('sex', postgresql.ENUM('M', 'F', 'Other', name='gender_enum'), nullable=True),
    sa.Column('nationality', sa.String(length=32), nullable=True),
    sa.Column('phone', sa.String(length=16), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('uid')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_uid'), ['uid'], unique=False)

    op.create_table('researcher',
    sa.Column('rsid', sa.String(length=16), nullable=False),
    sa.ForeignKeyConstraint(['rsid'], ['user.uid'], ),
    sa.PrimaryKeyConstraint('rsid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('researcher')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_uid'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    op.drop_table('pdf')
    # ### end Alembic commands ###
