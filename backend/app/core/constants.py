"""
Константы проекта
"""

# Общие константы
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Константы для кэширования
DEFAULT_CACHE_TTL = 3600  # 1 час в секундах
LONG_CACHE_TTL = 86400    # 24 часа в секундах
SHORT_CACHE_TTL = 300     # 5 минут в секундах

# Константы для токенов
ACCESS_TOKEN_PREFIX = "Bearer "
BLACKLIST_TOKEN_PREFIX = "blacklist:"
SESSION_PREFIX = "session:"

# Константы для рейтинга
MIN_RATING = 1
MAX_RATING = 5

# Константы для лимитов запросов
RATE_LIMIT_DEFAULT_WINDOW = 60  # 60 секунд
RATE_LIMIT_DEFAULT_MAX_REQUESTS = 100  # 100 запросов в окно

# Константы для файлов
ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp"]
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 МБ

# Константы для ролей и разрешений
ROLE_ADMIN = "admin"
ROLE_MODERATOR = "moderator"
ROLE_USER = "user"

PERMISSION_MANAGE_USERS = "manage_users"
PERMISSION_MANAGE_CONTENT = "manage_content"
PERMISSION_MANAGE_PLANTS = "manage_plants"
PERMISSION_MANAGE_CATEGORIES = "manage_categories"
PERMISSION_MANAGE_CLIMATE_ZONES = "manage_climate_zones"
PERMISSION_MANAGE_QUESTIONS = "manage_questions"
PERMISSION_MANAGE_ANSWERS = "manage_answers"
PERMISSION_MANAGE_TAGS = "manage_tags"

# Константы для путей
API_PREFIX = "/api"
API_V1_PREFIX = "/api/v1"

# Константы для статусов
STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"
STATUS_PENDING = "pending"
STATUS_REJECTED = "rejected"
STATUS_APPROVED = "approved"

# Константы HTTP-статусов
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_INTERNAL_SERVER_ERROR = 500
