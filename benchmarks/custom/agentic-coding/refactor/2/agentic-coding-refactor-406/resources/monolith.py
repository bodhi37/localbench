"""Order pricing (monolith: refactor me into the required helpers)."""


def order_total(lines):
    """Return the discounted order total for a list of (qty, price) pairs."""
    subtotal = 0
    for qty, price in lines:
        if qty < 0 or price < 0:
            raise ValueError("qty and price must be non-negative")
        subtotal += qty * price
    if subtotal < 0:
        raise ValueError("subtotal must be non-negative")
    if subtotal >= 1000:
        rate = 0.15
    elif subtotal >= 500:
        rate = 0.10
    elif subtotal >= 100:
        rate = 0.05
    else:
        rate = 0.0
    return round(subtotal * (1 - rate), 2)
