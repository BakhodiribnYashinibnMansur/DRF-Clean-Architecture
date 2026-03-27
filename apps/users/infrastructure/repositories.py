# ============================================
# User Repository (Infrastructure Layer)
# Concrete implementation of AbstractUserRepository using Django ORM.
# Maps between UserEntity (domain) and CustomUser (ORM model).
# ============================================

from typing import Optional

from apps.users.application.interfaces import AbstractUserRepository
from apps.users.domain.entities import UserEntity
from apps.users.infrastructure.models import CustomUser


class DjangoUserRepository(AbstractUserRepository):
    """
    Django ORM implementation of the user repository.
    Handles all database operations and maps between
    domain entities and ORM model instances.
    """

    @staticmethod
    def _to_entity(model: CustomUser) -> UserEntity:
        """Convert a Django ORM CustomUser instance to a domain UserEntity."""
        return UserEntity(
            id=model.id,
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            bio=model.bio,
            date_of_birth=model.date_of_birth,
            is_active=model.is_active,
            is_staff=model.is_staff,
            is_superuser=model.is_superuser,
            date_joined=model.date_joined,
            last_login=model.last_login,
        )

    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        """Retrieve a user by primary key. Returns None if not found."""
        try:
            model = CustomUser.objects.get(id=user_id)
            return self._to_entity(model)
        except CustomUser.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Retrieve a user by email. Returns None if not found."""
        try:
            model = CustomUser.objects.get(email=email)
            return self._to_entity(model)
        except CustomUser.DoesNotExist:
            return None

    def get_all(self) -> list[UserEntity]:
        """Retrieve all users ordered by date joined (newest first)."""
        return [self._to_entity(model) for model in CustomUser.objects.all()]

    def create_user(self, email: str, password: str, **kwargs) -> UserEntity:
        """Create a new user with hashed password."""
        model = CustomUser.objects.create_user(
            email=email, password=password, **kwargs
        )
        return self._to_entity(model)

    def update(self, user_id: int, **kwargs) -> UserEntity:
        """Update user fields and return the updated entity."""
        CustomUser.objects.filter(id=user_id).update(**kwargs)
        model = CustomUser.objects.get(id=user_id)
        return self._to_entity(model)

    def delete(self, user_id: int) -> None:
        """Delete a user by primary key."""
        CustomUser.objects.filter(id=user_id).delete()

    def exists_by_email(self, email: str) -> bool:
        """Check if a user with the given email exists."""
        return CustomUser.objects.filter(email=email).exists()

    def check_password(self, user_id: int, password: str) -> bool:
        """Verify that the password matches the user's stored hash."""
        try:
            model = CustomUser.objects.get(id=user_id)
            return model.check_password(password)
        except CustomUser.DoesNotExist:
            return False

    def set_password(self, user_id: int, new_password: str) -> None:
        """Set a new password for the user (hashed before storing)."""
        model = CustomUser.objects.get(id=user_id)
        model.set_password(new_password)
        model.save(update_fields=["password"])
