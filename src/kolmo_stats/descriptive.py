def mean(values):
    """
    Calculate the arithmetic mean.

    Example:
        mean([1, 2, 3]) -> 2.0
    """
    values = list(values)

    if len(values) == 0:
        raise ValueError("mean() requires at least one value")

    return sum(values) / len(values)