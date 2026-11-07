from decimal import Decimal


def calculate_amount_target(amount_source: Decimal, rate: Decimal) -> Decimal:
    return amount_source * rate
