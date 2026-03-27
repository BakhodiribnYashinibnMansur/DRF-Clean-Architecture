# ============================================
# Book Views (Presentation Layer)
# Full CRUD API for book management using ModelViewSet.
# Supports filtering, search, ordering, and per-action permissions.
# Uses BookService for business logic in write operations.
# ============================================

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from apps.books.application.services import BookService
from apps.books.infrastructure.models import Book
from apps.books.infrastructure.repositories import DjangoBookRepository

from .filters import BookFilter
from .permissions import IsOwnerOrAdmin
from .serializers import BookDetailSerializer, BookListSerializer


class BookViewSet(viewsets.ModelViewSet):
    """
    Full CRUD ViewSet for books.

    Endpoints (via router):
        GET    /api/books/           — List all books (paginated, filterable)
        POST   /api/books/           — Create a new book (authenticated)
        GET    /api/books/{id}/      — Retrieve a single book
        PUT    /api/books/{id}/      — Full update a book (owner or admin)
        PATCH  /api/books/{id}/      — Partial update a book (owner or admin)
        DELETE /api/books/{id}/      — Delete a book (owner or admin)

    Filtering:
        - ?title=python         — Filter by title (case-insensitive)
        - ?author=tolkien       — Filter by author name
        - ?genre=fiction        — Filter by genre
        - ?language=english     — Filter by language
        - ?published_after=2020-01-01
        - ?published_before=2023-12-31
        - ?min_pages=100
        - ?max_pages=500

    Search:
        - ?search=keyword       — Search in title, author, isbn

    Ordering:
        - ?ordering=title       — Order by title (ascending)
        - ?ordering=-created_at — Order by creation date (descending)
    """

    queryset = Book.objects.select_related("created_by").all()
    filterset_class = BookFilter
    search_fields = ["title", "author", "isbn"]
    ordering_fields = ["title", "author", "published_date", "page_count", "created_at"]
    ordering = ["-created_at"]  # Default ordering

    def get_serializer_class(self):
        """Use compact serializer for list, full serializer for detail/create/update."""
        if self.action == "list":
            return BookListSerializer
        return BookDetailSerializer

    def get_permissions(self):
        """
        Permission logic:
        - list, retrieve: any authenticated user (or read-only for anonymous)
        - create: authenticated users only
        - update, partial_update, destroy: owner of the book or admin
        """
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticatedOrReadOnly()]
        if self.action == "create":
            return [IsAuthenticated()]
        # update, partial_update, destroy
        return [IsAuthenticated(), IsOwnerOrAdmin()]

    def perform_create(self, serializer):
        """
        Create a book with business rule validation via the service layer.
        The service checks ISBN uniqueness before the serializer persists.
        """
        # Validate business rules through the service layer
        service = BookService(repository=DjangoBookRepository())
        isbn = serializer.validated_data.get("isbn", "")
        if service._repo.exists_by_isbn(isbn):
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"isbn": f"A book with ISBN '{isbn}' already exists."})

        # Persist through DRF serializer (sets created_by automatically)
        serializer.save(created_by=self.request.user)
