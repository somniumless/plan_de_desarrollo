"""Migracion inicial despues de resetear BD

Revision ID: 70edb2aa9fc7
Revises: 
Create Date: 2025-05-28 11:07:45.755453

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70edb2aa9fc7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('documento',
    sa.Column('documento_id', sa.String(length=20), nullable=False),
    sa.Column('usuario_id', sa.String(length=20), nullable=False),
    sa.Column('nombre', sa.String(length=255), nullable=False),
    sa.Column('tipo', sa.Enum('PDF', 'DOCX', 'XLSX', 'PPTX', 'JPG', 'PNG', 'TXT', 'OTRO', name='tipodocumento'), nullable=False),
    sa.Column('tamaño_mb', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('fecha_subida', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('ubicacion_almacenamiento', sa.String(length=512), nullable=True),
    sa.Column('hash_archivo', sa.String(length=64), nullable=True),
    sa.Column('eliminado', sa.Boolean(), nullable=True),
    sa.CheckConstraint('tamaño_mb > 0', name='check_tamaño_mb_positive'),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.usuario_id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('documento_id')
    )
    op.create_table('version_documento',
    sa.Column('version_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('documento_id', sa.String(length=20), nullable=False),
    sa.Column('numero_version', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.String(length=20), nullable=False),
    sa.Column('fecha_modificacion', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('cambios', sa.Text(), nullable=True),
    sa.Column('hash_version', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['documento_id'], ['documento.documento_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.usuario_id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('version_id'),
    sa.UniqueConstraint('documento_id', 'numero_version', name='uk_documento_version')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('version_documento')
    op.drop_table('documento')
    # ### end Alembic commands ###
