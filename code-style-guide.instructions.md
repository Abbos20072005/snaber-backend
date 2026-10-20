---
trigger: always_on
---

# Thinkland Backend Code Style Guide

## 1. Purpose
This guide standardizes coding style for Django + DRF code inside `src/apps`. The rules align with existing project patterns:
- `BaseModel` (`created_at`, `modified_at`, `created_by`, `modified_by`)
- `BaseModelSerializer`
- `pytest` tests

## 2. Folder and Module Structure
- Each domain app lives in: `apps/<domain>/`
- Keep the API layer in this structure:
  - `api/v1/serializers/`
  - `api/v1/views/`
  - `api/v1/urls.py`
  - `api/v1/filters.py` (if needed)
- Model files: `models/<entity>.py`
- Centralize exports via `models/__init__.py`.

## 3. Naming Conventions
- Class names: `PascalCase` (`OrganizationListAPIView`, `HrEmployeeCreateSerializer`).
- Functions/methods/fields: `snake_case`.
- Constants: `UPPER_CASE`.
- URL names: kebab-case (`hr-employee-list`).


## 4. Import Order
Write imports in 3 blocks with one blank line between them:
1. Python standard library
2. Third-party packages (`django`, `rest_framework`, etc.)
3. Local `apps.*` imports

Group related imports in the same file. Do not use wildcard imports.

## 5. Model Standards
- All business models should inherit from `BaseModel`.

- Use `null=True` and `blank=True` together only when truly required.
- Define choices with `TextChoices`/`IntegerChoices`.
- `__str__` should return a meaningful identifier.


## 6. Serializer Standards
- Create/Update serializers should inherit from `BaseModelSerializer`.
- List/Get serializers should use `serializers.ModelSerializer`.
- Use `__all__` only when truly necessary; prefer explicit `fields = (...)`.
- Use dedicated `RelationSerializer` for relation fields.
- Never use `source` in serializers. Always use a dedicated `RelationSerializer` for relation mapping.

Recommended naming:
- `<Entity>CreateSerializer`
- `<Entity>UpdateSerializer`
- `<Entity>ListSerializer`
- `<Entity>RetrieveSerializer`
- `<Entity>RelationSerializer`

## 7. View Standards

- Every view should explicitly define:
  - `queryset`
  - `serializer_class`
  - `permission_classes`

- Use `get_serializer_class()` when switching serializers for `PUT/PATCH`.
- Prevent N+1 queries with `select_related`/`prefetch_related`.
- For list endpoints, define `filterset_class`, `ordering_fields`, and `ordering`.

## 8. URL Standards
- Use `path` by default; use `re_path` only when regex is required.
- Do not mix trailing-slash styles within the same app.
- Group URL patterns by entity (`organization`, `hr-employee`, etc.).
- Keep `urlpatterns` readable and explicit.

## 9. Validation and Business Logic

- Return `ValidationError` mapped to a specific field whenever possible.

## 10. Comments and Docstrings
- Use comments only where needed: explain "why", not "what".
- Keep docstrings short and clear.
- Do not keep broken-encoding comments (`Ð...`); clean to UTF-8.

## 11. Test Standards (`pytest`)
- Use `@pytest.mark.django_db` on required test classes/functions.
- Test names should express behavior:
  - `test_create_organization_success`
  - `test_update_returns_400_for_invalid_data`
- Keep tests in "Arrange, Act, Assert" order.
- Store fixtures in `tests/fixtures` or near the app in `tests/<app>/fixtures`.

## 12. Migration and Data Safety
- Add comments for manually edited migrations.
- Do not rewrite migration history in active environments.
- Never commit hardcoded secrets (token, password, private key).

## 13. Recommended Quality Gate (CI/local)
Minimum checks:
1. `python manage.py check`
2. `pytest`
3. At least one positive and one negative test for each new endpoint

Optional (recommended):
1. `ruff` or `flake8`
2. `black`
3. `isort`

## 14. Pull Request Checklist
- New code follows this guide.
- Serializer/view naming matches project patterns.
- Queryset optimization is verified (`select_related`/`prefetch_related`).
- Tests are added or updated.
- Unnecessary comments and debug prints are removed.
