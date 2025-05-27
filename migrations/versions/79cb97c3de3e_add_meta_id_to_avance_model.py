from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '79cb97c3de3e'
down_revision = '70f4def57069'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('Avance', sa.Column('meta_id', sa.String(length=20), nullable=True)) 
    op.create_foreign_key(op.f('fk_avance_meta_id'), 'Avance', 'Meta', ['meta_id'], ['meta_id'])
    # ### end Alembic commands ###


def downgrade():
    op.drop_constraint(op.f('fk_avance_meta_id'), 'Avance', type_='foreignkey')
    op.drop_column('Avance', 'meta_id')
    # ### end Alembic commands ###