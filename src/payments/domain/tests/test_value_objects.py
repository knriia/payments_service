from decimal import Decimal

import pytest

from payments.domain.exceptions import InvalidPaymentAmount
from payments.domain.value_objects import Currency, Money


def test_create_money_with_positive_amount() -> None:
    money = Money(amount=Decimal("100"), currency=Currency.EUR)
    assert money.amount == Decimal("100")
    assert money.currency == Currency.EUR


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-1")])
def test_create_money_raises_error_when_amount_is_not_positive(amount: Decimal) -> None:
    with pytest.raises(InvalidPaymentAmount):
        Money(amount=amount, currency=Currency.EUR)
