---
name: django-patterns
description: Use when deciding how to structure a new Django feature — recommended patterns for querysets, templates, forms, and app layout in this project.
---

# Django Patterns

## Fat models / thin views
- Put reusable query logic in a custom `Manager`/`QuerySet` method (e.g. `Post.objects.published()`), not repeated inline filters across views.
- Put reusable presentation logic in template tags/filters, not in the view.

## Querysets
- Chain filters lazily; only call `.all()` / list() at the point you actually need to evaluate.
- Use `Paginator` for any list view that could grow beyond ~20 items.
- Avoid `.filter(...).count()` followed by `.filter(...)` again for the same condition — reuse the queryset variable.

## Templates
- One `base.html` with `{% block %}` regions; app templates extend it, never duplicate `<html>`/`<head>`.
- Extract repeated fragments (e.g. a single post card, a pagination widget) into `{% include %}` partials — this also makes HTMX partial-swap targets easy to reuse.
- Keep logic out of templates beyond simple conditionals/loops; anything more complex belongs in the view or a template tag.

## Forms
- One `ModelForm` per model unless the create/edit flows genuinely diverge.
- Server-rendered forms first; add HTMX/JS enhancement on top without breaking the no-JS path.

## App layout
- One Django app per bounded concern (e.g. `blog`, `accounts`) — don't let a single app accumulate unrelated models.
- Keep `urls.py` per app, included from the project root `urls.py` with a namespace.
