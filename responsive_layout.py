"""Responsive layout rules independent of Qt for deterministic testing."""

def dashboard_columns(width: int, *, count: int = 5) -> int:
    """Choose 1–3 columns based on available content width (not screen width)."""
    if isinstance(width, bool) or not isinstance(width, int) or width < 0:
        raise ValueError('width must be a nonnegative integer')
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError('count must be a nonnegative integer')
    if count == 0:
        return 0
    return min(count, 3 if width >= 810 else 2 if width >= 520 else 1)


def grid_positions(count: int, columns: int):
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError('count must be a nonnegative integer')
    if isinstance(columns, bool) or not isinstance(columns, int) or columns < 1:
        raise ValueError('columns must be a positive integer')
    return [(index // columns, index % columns) for index in range(count)]
