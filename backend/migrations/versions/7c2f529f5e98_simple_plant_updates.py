"""simple_plant_updates

Revision ID: 7c2f529f5e98
Revises: 
Create Date: 2025-05-18 09:56:40.763024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c2f529f5e98'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Simple plant updates without complex checks."""
    
    # 1. Создаем связь plant-tag
    op.create_table('plant_tag',
        sa.Column('plant_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('plant_id', 'tag_id')
    )
    op.create_index('ix_plant_tag_plant', 'plant_tag', ['plant_id'], unique=False)
    op.create_index('ix_plant_tag_tag', 'plant_tag', ['tag_id'], unique=False)
    
    # 2. Добавляем новые столбцы в plants
    op.add_column('plants', sa.Column('life_cycle', sa.String(length=50), nullable=True))
    op.add_column('plants', sa.Column('watering_frequency', sa.String(length=50), nullable=True))
    op.add_column('plants', sa.Column('light_level', sa.String(length=50), nullable=True))
    op.add_column('plants', sa.Column('temperature_min', sa.Float(), nullable=True))
    op.add_column('plants', sa.Column('temperature_max', sa.Float(), nullable=True))
    op.add_column('plants', sa.Column('humidity_level', sa.String(length=50), nullable=True))
    op.add_column('plants', sa.Column('is_toxic', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('plants', sa.Column('fertilizing_frequency', sa.String(length=50), nullable=True))
    op.add_column('plants', sa.Column('repotting_frequency', sa.String(length=50), nullable=True))
    op.add_column('plants', sa.Column('care_difficulty', sa.String(length=50), nullable=True))
    op.add_column('plants', sa.Column('care_tips', sa.Text(), nullable=True))
    op.add_column('plants', sa.Column('common_problems', sa.Text(), nullable=True))
    op.add_column('plants', sa.Column('propagation_methods', sa.Text(), nullable=True))
    op.add_column('plants', sa.Column('notes', sa.Text(), nullable=True))
    
    # 3. Создаем индексы
    op.create_index('idx_plant_care_difficulty', 'plants', ['care_difficulty'], unique=False)
    op.create_index('idx_plant_watering_light', 'plants', ['watering_frequency', 'light_level'], unique=False)


def downgrade() -> None:
    """Restore original state."""
    
    # Удаляем индексы
    op.drop_index('idx_plant_watering_light', table_name='plants')
    op.drop_index('idx_plant_care_difficulty', table_name='plants')
    
    # Удаляем столбцы
    op.drop_column('plants', 'notes')
    op.drop_column('plants', 'propagation_methods')
    op.drop_column('plants', 'common_problems')
    op.drop_column('plants', 'care_tips')
    op.drop_column('plants', 'care_difficulty')
    op.drop_column('plants', 'repotting_frequency')
    op.drop_column('plants', 'fertilizing_frequency')
    op.drop_column('plants', 'is_toxic')
    op.drop_column('plants', 'humidity_level')
    op.drop_column('plants', 'temperature_max')
    op.drop_column('plants', 'temperature_min')
    op.drop_column('plants', 'light_level')
    op.drop_column('plants', 'watering_frequency')
    op.drop_column('plants', 'life_cycle')
    
    # Удаляем plant_tag
    op.drop_index('ix_plant_tag_tag', table_name='plant_tag')
    op.drop_index('ix_plant_tag_plant', table_name='plant_tag')
    op.drop_table('plant_tag')