def to_int(value: object) -> int | None:
    if not isinstance(value, str):
        return None
    cleaned = value.lstrip("#").strip()
    return int(cleaned) if cleaned.isdigit() else None


def clean_str(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    return value.replace("​", "").strip() or None


def to_list(value: object, drop: tuple[str, ...] = ()) -> list[str]:
    if not isinstance(value, list):
        return []
    return [x for x in value if isinstance(x, str) and x not in drop]
