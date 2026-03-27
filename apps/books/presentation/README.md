# Presentation Layer (books)

**API qatlami** — DRF-specific kod. Tashqi dunyo bilan aloqa.

## Vazifasi

Presentation layer "API qanday ishlaydi?" savoliga javob beradi.
HTTP request qabul qiladi, validate qiladi, response qaytaradi.

## Fayllar

### `views.py` — ViewSet (API Controller)
```python
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("created_by").all()
    filterset_class = BookFilter
    search_fields = ["title", "author", "isbn"]
    ordering_fields = ["title", "author", "published_date", ...]

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer   # Compact (description yo'q)
        return BookDetailSerializer     # Full

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticatedOrReadOnly()]
        if self.action == "create":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOwnerOrAdmin()]  # update/delete

    def perform_create(self, serializer):
        # Service layer orqali ISBN uniqueness tekshiruvi
        service = BookService(repository=DjangoBookRepository())
        ...
        serializer.save(created_by=self.request.user)
```

### `serializers.py` — Data Validation & Transformation
```python
class BookListSerializer(ModelSerializer):    # List uchun (description yo'q)
class BookDetailSerializer(ModelSerializer):  # Detail uchun (barcha fieldlar)
```

Ikki serializer — **performance uchun**. List API da description yuklanmaydi.

### `permissions.py` — Access Control
```python
class IsAdminOrReadOnly:     # Admin yozadi, boshqalar faqat o'qiydi
class IsOwnerOrAdmin:        # Faqat kitob egasi yoki admin o'zgartira oladi
```

### `filters.py` — Query Filtering
```python
class BookFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    author = CharFilter(lookup_expr="icontains")
    genre = ChoiceFilter(choices=Book.Genre.choices)
    published_after = DateFilter(field_name="published_date", lookup_expr="gte")
    min_pages = NumberFilter(field_name="page_count", lookup_expr="gte")
    ...
```

8 ta filter: title, author, genre, language, published_after/before, min/max_pages.

### `urls.py` — URL Routing
```python
router = DefaultRouter()
router.register("", BookViewSet, basename="book")
# Auto-generated: GET /, POST /, GET /{id}/, PUT /{id}/, PATCH /{id}/, DELETE /{id}/
```

## Import qoidasi

```
presentation/ → barcha layerlardan import qilishi mumkin:
                domain/        (entity, exception)
                application/   (service)
                infrastructure/ (model, repository)
                DRF, Django    (serializers, viewsets, permissions, filters)
```

## Nima uchun kerak?

1. **API layer ajratilgan** — framework o'zgarsa (DRF → FastAPI), faqat shu layer o'zgaradi
2. **Validation** — serializer faqat API data validation qiladi, biznes logic service da
3. **Per-action permissions** — har bir action uchun alohida permission
4. **Optimized queries** — `select_related`, alohida list/detail serializer
