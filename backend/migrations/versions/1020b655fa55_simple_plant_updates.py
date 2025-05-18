"""simple_plant_updates

Revision ID: 1020b655fa55
Revises: 
Create Date: 2025-05-18 14:18:21.373969

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1020b655fa55'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Создание всех таблиц для растений"""
    
    # 1. Создаем таблицу plant_categories
    op.create_table('plant_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['plant_categories.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_plant_categories_name', 'plant_categories', ['name'], unique=True)
    
    # 2. Создаем таблицу climate_zones
    op.create_table('climate_zones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('zone_number', sa.Integer(), nullable=False),
        sa.Column('min_temperature', sa.Float(), nullable=True),
        sa.Column('max_temperature', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_climate_zones_name', 'climate_zones', ['name'], unique=True)
    op.create_index('ix_climate_zones_zone_number', 'climate_zones', ['zone_number'], unique=True)
    
    # 3. Создаем таблицу tags
    op.create_table('tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tags_name', 'tags', ['name'], unique=True)
    
    # 4. Создаем основную таблицу plants
    op.create_table('plants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # Основная информация
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('latin_name', sa.String(length=150), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Характеристики роста
        sa.Column('height_min', sa.Float(), nullable=True),
        sa.Column('height_max', sa.Float(), nullable=True),
        sa.Column('growth_rate', sa.Enum('FAST', 'MODERATE', 'SLOW', name='growthrate'), nullable=True),
        
        # Тип растения и жизненный цикл
        sa.Column('plant_type', sa.Enum('TREE', 'SHRUB', 'FLOWER', 'VEGETABLE', 'FRUIT', 'HERB', 'SUCCULENT', 'VINE', 'AQUATIC', 'FERN', name='planttype'), nullable=True),
        sa.Column('life_cycle', sa.Enum('ANNUAL', 'BIENNIAL', 'PERENNIAL', name='lifecycle'), nullable=True),
        
        # Популярность
        sa.Column('popularity_score', sa.Integer(), nullable=False, default=0),
        
        # Цветение
        sa.Column('flowering_period', sa.String(length=100), nullable=True),
        sa.Column('bloom_color', sa.String(length=50), nullable=True),
        
        # Зоны морозостойкости
        sa.Column('hardiness_zone_min', sa.Integer(), nullable=True),
        sa.Column('hardiness_zone_max', sa.Integer(), nullable=True),
        
        # Условия выращивания
        sa.Column('watering_frequency', sa.Enum('DAILY', 'TWICE_A_WEEK', 'WEEKLY', 'BI_WEEKLY', 'MONTHLY', 'RARELY', name='wateringfrequency'), nullable=True),
        sa.Column('light_level', sa.Enum('FULL_SUN', 'PARTIAL_SUN', 'SHADE', 'LOW_LIGHT', name='lightlevel'), nullable=True),
        sa.Column('temperature_min', sa.Float(), nullable=True),
        sa.Column('temperature_max', sa.Float(), nullable=True),
        sa.Column('humidity_level', sa.Enum('HIGH', 'MEDIUM', 'LOW', name='humiditylevel'), nullable=True),
        
        # Уход
        sa.Column('care_difficulty', sa.Enum('VERY_EASY', 'EASY', 'MODERATE', 'DIFFICULT', 'EXPERT', name='caredifficulty'), nullable=True),
        sa.Column('fertilizing_frequency', sa.Enum('WEEKLY', 'BI_WEEKLY', 'MONTHLY', 'QUARTERLY', 'ANNUALLY', 'NONE', name='fertilizingfrequency'), nullable=True),
        sa.Column('repotting_frequency', sa.Enum('ANNUALLY', 'BI_ANNUALLY', 'THREE_YEARS', 'RARELY', name='repottingfrequency'), nullable=True),
        
        # Безопасность
        sa.Column('is_toxic', sa.Boolean(), nullable=False, default=False),
        
        # Инструкции и советы
        sa.Column('care_instructions', sa.Text(), nullable=True),
        sa.Column('planting_instructions', sa.Text(), nullable=True),
        sa.Column('pruning_tips', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        
        # JSON поля
        sa.Column('care_tips', sa.Text(), nullable=True),
        sa.Column('common_problems', sa.Text(), nullable=True),
        sa.Column('propagation_methods', sa.Text(), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Индексы для таблицы plants
    op.create_index('ix_plants_name', 'plants', ['name'])
    op.create_index('ix_plants_popularity_score', 'plants', ['popularity_score'])
    op.create_index('ix_plants_plant_type', 'plants', ['plant_type'])
    op.create_index('idx_plant_type_popularity', 'plants', ['plant_type', 'popularity_score'])
    op.create_index('idx_plant_care_difficulty', 'plants', ['care_difficulty'])
    op.create_index('idx_plant_watering_light', 'plants', ['watering_frequency', 'light_level'])
    
    # 5. Создаем таблицу plant_images
    op.create_table('plant_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('plant_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=255), nullable=False),
        sa.Column('alt', sa.String(length=255), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=255), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 6. Создаем таблицы связей many-to-many
    
    # Таблица связи растений и категорий
    op.create_table('plant_category',
        sa.Column('plant_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id']),
        sa.ForeignKeyConstraint(['category_id'], ['plant_categories.id']),
        sa.PrimaryKeyConstraint('plant_id', 'category_id')
    )
    op.create_index('ix_plant_category_plant', 'plant_category', ['plant_id'])
    op.create_index('ix_plant_category_category', 'plant_category', ['category_id'])
    
    # Таблица связи растений и климатических зон
    op.create_table('plant_climate_zone',
        sa.Column('plant_id', sa.Integer(), nullable=False),
        sa.Column('climate_zone_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id']),
        sa.ForeignKeyConstraint(['climate_zone_id'], ['climate_zones.id']),
        sa.PrimaryKeyConstraint('plant_id', 'climate_zone_id')
    )
    op.create_index('ix_plant_climate_zone_plant', 'plant_climate_zone', ['plant_id'])
    op.create_index('ix_plant_climate_zone_climate', 'plant_climate_zone', ['climate_zone_id'])
    
    # Таблица связи растений и тегов
    op.create_table('plant_tag',
        sa.Column('plant_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id']),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id']),
        sa.PrimaryKeyConstraint('plant_id', 'tag_id')
    )
    op.create_index('ix_plant_tag_plant', 'plant_tag', ['plant_id'])
    op.create_index('ix_plant_tag_tag', 'plant_tag', ['tag_id'])


def downgrade():
    """Удаление всех таблиц для растений"""
    
    # Удаляем таблицы в обратном порядке (сначала зависимые, потом основные)
    op.drop_table('plant_tag')
    op.drop_table('plant_climate_zone')
    op.drop_table('plant_category')
    op.drop_table('plant_images')
    op.drop_table('plants')
    op.drop_table('tags')
    op.drop_table('climate_zones')
    op.drop_table('plant_categories')
    
    # Удаляем enum типы
    op.execute('DROP TYPE IF EXISTS growthrate')
    op.execute('DROP TYPE IF EXISTS planttype')
    op.execute('DROP TYPE IF EXISTS lifecycle')
    op.execute('DROP TYPE IF EXISTS wateringfrequency')
    op.execute('DROP TYPE IF EXISTS lightlevel')
    op.execute('DROP TYPE IF EXISTS humiditylevel')
    op.execute('DROP TYPE IF EXISTS caredifficulty')
    op.execute('DROP TYPE IF EXISTS fertilizingfrequency')
    op.execute('DROP TYPE IF EXISTS repottingfrequency')
