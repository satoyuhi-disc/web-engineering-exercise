---
name: django-expert
description: Use when writing or reviewing Django code (models, views, forms, URLs, admin, settings) — Django-specific conventions and pitfalls to check before finishing any Django task.
---

# Django Expert

## Models
- Prefer `related_name` on FKs when a model has multiple relations to the same target.
- Always implement `__str__()`.
- Use `Meta.ordering` instead of ordering in every view/query.
- Add `db_index=True` / `models.Index` for fields used in frequent filters (dates, FKs, slugs).
- Never put business logic that mutates other models inside `save()` without a clear reason — prefer explicit service functions or model methods.

## Views
- Keep function/class-based views thin: fetch, validate, delegate, render/redirect.
- Use `get_object_or_404` instead of manual try/except `DoesNotExist`.
- Any view that mutates data must check the HTTP method (`require_http_methods`, or CBV `http_method_names`) — never mutate on GET.
- Use `@login_required` / `LoginRequiredMixin` for anything that creates/edits data owned by a user.
- Always use `select_related`/`prefetch_related` when a template will access FK/M2M fields in a loop (avoid N+1).

## Forms
- Validate everything server-side even if there's client-side JS validation.
- Put cross-field validation in `clean()`, single-field validation in `clean_<field>()`.
- Never trust `request.POST` values for fields that determine ownership (e.g. `author`) — set them from `request.user` in the view, not from the form.

## URLs & Security
- Namespace app URLs (`app_name = "..."`) and always reverse with the namespace.
- CSRF protection must stay on for any state-changing POST — never add `@csrf_exempt` without a documented reason.
- Never expose `DEBUG=True` or a hardcoded `SECRET_KEY` outside local dev settings.

## Before finishing any Django task
1. Run `python manage.py check`.
2. Run `python manage.py makemigrations --check --dry-run` — no model change should be uncommitted as a migration.
3. Run the test suite — a new view or model method with no test is not done.
