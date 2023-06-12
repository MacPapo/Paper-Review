"""empty message

Revision ID: 61e214ada9a5
Revises: 
Create Date: 2023-06-11 18:47:40.018517

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '61e214ada9a5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('draft',
    sa.Column('did', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('did')
    )
    op.create_table('pdf',
    sa.Column('id', postgresql.BYTEA(), nullable=False),
    sa.Column('filename', sa.String(length=256), nullable=False),
    sa.Column('key', postgresql.BYTEA(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('uid', sa.String(length=16), nullable=False),
    sa.Column('username', sa.String(length=32), nullable=False),
    sa.Column('first_name', sa.String(length=32), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('birthdate', sa.Date(), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('sex', postgresql.ENUM('M', 'F', 'Other', name='gender_enum'), nullable=False),
    sa.Column('nationality', sa.String(length=32), nullable=True),
    sa.Column('phone', sa.String(length=16), nullable=True),
    sa.Column('department', sa.String(length=50), nullable=True),
    sa.Column('type', postgresql.ENUM('researcher', 'reviewer', name='user_type'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('uid')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_uid'), ['uid'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('draft_pdf',
    sa.Column('pdf_id', postgresql.BYTEA(), nullable=True),
    sa.Column('draft_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['draft_id'], ['draft.did'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['pdf_id'], ['pdf.id'], ondelete='CASCADE')
    )
    op.create_table('researcher',
    sa.Column('rsid', sa.String(length=16), nullable=False),
    sa.ForeignKeyConstraint(['rsid'], ['user.uid'], ),
    sa.PrimaryKeyConstraint('rsid')
    )
    op.create_table('reviewer',
    sa.Column('rvid', sa.String(length=16), nullable=False),
    sa.Column('pdf_id', postgresql.BYTEA(), nullable=False),
    sa.ForeignKeyConstraint(['pdf_id'], ['pdf.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['rvid'], ['user.uid'], ),
    sa.PrimaryKeyConstraint('rvid'),
    sa.UniqueConstraint('pdf_id')
    )
    op.create_table('project',
    sa.Column('pid', sa.Integer(), nullable=False),
    sa.Column('rsid', sa.String(length=16), nullable=True),
    sa.ForeignKeyConstraint(['rsid'], ['researcher.rsid'], ),
    sa.PrimaryKeyConstraint('pid')
    )
    op.create_table('reportdraft',
    sa.Column('rdid', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('rvid', sa.String(length=16), nullable=True),
    sa.Column('pid', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=256), nullable=False),
    sa.Column('reference', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['pid'], ['project.pid'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['rvid'], ['reviewer.rvid'], ),
    sa.PrimaryKeyConstraint('rdid')
    )
    op.create_table('version',
    sa.Column('vid', sa.Integer(), nullable=False),
    sa.Column('version_number', sa.Integer(), nullable=False),
    sa.Column('project_title', sa.String(length=256), nullable=False),
    sa.Column('project_description', sa.Text(), nullable=False),
    sa.Column('project_status', postgresql.ENUM('Approved', 'Submitted', 'Requires changes', 'Not Approved', name='status_enum'), nullable=True),
    sa.Column('pid', sa.Integer(), nullable=True),
    sa.Column('draft_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['draft_id'], ['draft.did'], ),
    sa.ForeignKeyConstraint(['pid'], ['project.pid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('vid'),
    sa.UniqueConstraint('draft_id')
    )
    op.create_table('pdf_version',
    sa.Column('pdf_id', postgresql.BYTEA(), nullable=True),
    sa.Column('version_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['pdf_id'], ['pdf.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['version_id'], ['version.vid'], ondelete='CASCADE')
    )
    op.create_table('report',
    sa.Column('rid', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('pid', sa.Integer(), nullable=True),
    sa.Column('rvid', sa.String(length=16), nullable=True),
    sa.Column('rdraft_id', sa.Integer(), nullable=True),
    sa.Column('reference', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['pid'], ['project.pid'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['rdraft_id'], ['reportdraft.rdid'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reference'], ['report.rid'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['rvid'], ['reviewer.rvid'], ),
    sa.PrimaryKeyConstraint('rid'),
    sa.UniqueConstraint('rdraft_id')
    )
    op.create_table('report_draft_pdf',
    sa.Column('pdf_id', postgresql.BYTEA(), nullable=True),
    sa.Column('draft_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['draft_id'], ['reportdraft.rdid'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['pdf_id'], ['pdf.id'], ondelete='CASCADE')
    )
    op.create_table('pdf_report',
    sa.Column('pdf_id', postgresql.BYTEA(), nullable=True),
    sa.Column('report_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['pdf_id'], ['pdf.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['report_id'], ['report.rid'], ondelete='CASCADE')
    )
    op.create_table('report_version',
    sa.Column('report_id', sa.Integer(), nullable=True),
    sa.Column('version_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['report_id'], ['report.rid'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['version_id'], ['version.vid'], ondelete='CASCADE')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('report_version')
    op.drop_table('pdf_report')
    op.drop_table('report_draft_pdf')
    op.drop_table('report')
    op.drop_table('pdf_version')
    op.drop_table('version')
    op.drop_table('reportdraft')
    op.drop_table('project')
    op.drop_table('reviewer')
    op.drop_table('researcher')
    op.drop_table('draft_pdf')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_uid'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    op.drop_table('pdf')
    op.drop_table('draft')
    # ### end Alembic commands ###