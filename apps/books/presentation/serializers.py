# ============================================
# Book Serializers (Presentation Layer)
# Handles data validation and transformation for Book API endpoints.
# Separate serializers for list (compact) and detail (full) views.
# ============================================

from rest_framework import serializers

from apps.books.infrastructure.models import Book


class BookListSerializer(serializers.ModelSerializer):
    """
    Compact serializer for book list views.
    Omits the description field for faster list responses.
    Shows created_by as a nested object with id and email.
    """

    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "genre",
            "language",
            "published_date",
            "page_count",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]

    def get_created_by(self, obj):
        """Return compact user info or None if no creator."""
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "email": obj.created_by.email,
            }
        return None


class BookDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for book detail/create/update views.
    Includes all fields. created_by is set automatically in the view.
    """

    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "genre",
            "language",
            "published_date",
            "page_count",
            "description",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def get_created_by(self, obj):
        """Return compact user info or None if no creator."""
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "email": obj.created_by.email,
            }
        return None
