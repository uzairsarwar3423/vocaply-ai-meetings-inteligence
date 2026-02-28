# Import the Base class for SQLAlchemy models
from app.models.base import Base

# Note: Model imports are handled in app/models/__init__.py to avoid circular imports
# Alembic will discover models through the app.models module
