def require_non_empty(value, field_name):
    """Validate that value is a non-blank string; return it stripped.

    Raises ValueError with a clear message when missing or blank.
    Shared by every model's property setter.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} cannot be empty.")
    return value.strip()