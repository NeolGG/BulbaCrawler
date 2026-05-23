from typing import Any, TypeGuard

from bs4 import Tag


def _is_tag(ctx: object) -> TypeGuard[Tag]:
    return isinstance(ctx, Tag)


def op_find(ctx: Any, tag: str, attrs: dict[str, Any] | None = None) -> Tag | None:
    if not _is_tag(ctx):
        return None
    result = ctx.find(tag, attrs or {})
    return result if _is_tag(result) else None


def op_find_all(ctx: Any, tag: str, attrs: dict[str, Any] | None = None) -> list[Tag]:
    if not _is_tag(ctx):
        return []
    return ctx.find_all(tag, attrs or {})


def op_find_where_attr_contains(
    ctx: Any, tag: str, attr: str, value: str
) -> Tag | None:
    if not _is_tag(ctx):
        return None
    result = ctx.find(tag, {attr: lambda v: isinstance(v, str) and value in v})
    return result if _is_tag(result) else None


def op_select(ctx: Any, css: str) -> list[Tag]:
    if not _is_tag(ctx):
        return []
    return [el for el in ctx.select(css) if _is_tag(el)]


def op_attr(ctx: Any, name: str) -> str | None:
    if not _is_tag(ctx):
        return None
    raw = ctx.get(name)
    return raw if isinstance(raw, str) else None


def op_text(ctx: Any) -> str | None:
    if not _is_tag(ctx):
        return None
    return ctx.get_text(strip=True)


def op_text_all(ctx: Any) -> list[str]:
    if not isinstance(ctx, list):
        return []
    return [el.get_text(strip=True) for el in ctx if _is_tag(el)]
