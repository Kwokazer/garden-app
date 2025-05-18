import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def seed_database():
    # Создание подключения
    db_url = f'postgresql+asyncpg://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOST")}:{os.environ.get("POSTGRES_PORT")}/{os.environ.get("POSTGRES_DB")}'
    engine = create_async_engine(db_url)
    
    async with engine.begin() as conn:
        # 1. Сначала заполняем таблицу ролей (roles) - это исправляет ошибку внешнего ключа
        roles = [
            (1, 'user', 'Обычный зарегистрированный пользователь'),
            (2, 'expert', 'Специалист по растениям'),
            (3, 'moderator', 'Модерация контента'),
            (4, 'admin', 'Полные права на платформе')
        ]
        
        for role in roles:
            await conn.execute(text(
                "INSERT INTO roles (id, name, description) "
                "VALUES (:id, :name, :description) ON CONFLICT (id) DO NOTHING"
            ), {"id": role[0], "name": role[1], "description": role[2]})
        
        # 2. Заполняем таблицу разрешений (permissions)
        permissions = [
            (1, 'create_post', 'Создание постов'),
            (2, 'edit_post', 'Редактирование постов'),
            (3, 'delete_post', 'Удаление постов'),
            (4, 'moderate_comments', 'Модерация комментариев'),
            (5, 'admin_access', 'Административный доступ')
        ]
        
        for perm in permissions:
            await conn.execute(text(
                "INSERT INTO permissions (id, name, description) "
                "VALUES (:id, :name, :description) ON CONFLICT (id) DO NOTHING"
            ), {"id": perm[0], "name": perm[1], "description": perm[2]})
        
        # 3. Связываем роли и разрешения
        role_permissions = [
            # user - базовые права
            (1, 1),  # user может создавать посты
            # expert - права эксперта
            (2, 1), (2, 2),  # эксперт может создавать и редактировать посты
            # moderator - права модератора
            (3, 1), (3, 2), (3, 3), (3, 4),  # модератор может создавать, редактировать, удалять и модерировать
            # admin - все права
            (4, 1), (4, 2), (4, 3), (4, 4), (4, 5)  # админ имеет все права
        ]
        
        for rp in role_permissions:
            await conn.execute(text(
                "INSERT INTO role_permission (role_id, permission_id) "
                "VALUES (:role_id, :permission_id) ON CONFLICT DO NOTHING"
            ), {"role_id": rp[0], "permission_id": rp[1]})
        
        # 4. Создаем пользователей
        users = [
            (1, 'user@example.com', 'user123', 'Иван', 'Петров', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', True, True, 'LIMITED'),
            (2, 'expert@example.com', 'expert123', 'Ольга', 'Экспертова', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', True, True, 'PUBLIC'),
            (3, 'moderator@example.com', 'moderator123', 'Сергей', 'Модераторов', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', True, True, 'PUBLIC'),
            (4, 'admin@example.com', 'admin123', 'Администратор', 'Системы', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', True, True, 'PRIVATE')
        ]
        
        for user in users:
            await conn.execute(text(
                "INSERT INTO users (id, email, username, first_name, last_name, hashed_password, is_active, is_verified, privacy_level) "
                "VALUES (:id, :email, :username, :first_name, :last_name, :hashed_password, :is_active, :is_verified, :privacy_level) "
                "ON CONFLICT (id) DO NOTHING"
            ), {
                "id": user[0], 
                "email": user[1], 
                "username": user[2], 
                "first_name": user[3], 
                "last_name": user[4], 
                "hashed_password": user[5], 
                "is_active": user[6], 
                "is_verified": user[7], 
                "privacy_level": user[8]
            })
        
        # 5. Связываем пользователей с ролями
        user_roles = [
            (1, 1),  # user - роль user
            (2, 2),  # expert - роль expert
            (3, 3),  # moderator - роль moderator
            (4, 4)   # admin - роль admin
        ]
        
        for ur in user_roles:
            await conn.execute(text(
                "INSERT INTO user_role (user_id, role_id) "
                "VALUES (:user_id, :role_id) ON CONFLICT DO NOTHING"
            ), {"user_id": ur[0], "role_id": ur[1]})
        
        # Дальнейший код для других таблиц (climate_zones, plant_categories, plants и т.д.)
        # ...

        print("База данных успешно заполнена!")

if __name__ == "__main__":
    asyncio.run(seed_database())
