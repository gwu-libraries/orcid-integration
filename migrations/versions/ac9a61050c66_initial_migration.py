"""Initial migration.

Revision ID: ac9a61050c66
Revises: 
Create Date: 2024-04-26 13:11:48.534267

"""
from alembic import op
import sqlalchemy as sa
from orcidflask.models import EncryptedValue


# revision identifiers, used by Alembic.
revision = 'ac9a61050c66'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userId', sa.String(length=80), nullable=False),
    sa.Column('access_token', EncryptedValue(), nullable=False),
    sa.Column('refresh_token', EncryptedValue(), nullable=False),
    sa.Column('expires_in', sa.Integer(), nullable=False),
    sa.Column('token_scope', sa.String(length=80), nullable=False),
    sa.Column('orcid', sa.String(length=80), nullable=False),
    sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('token')
    # ### end Alembic commands ###
