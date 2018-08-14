from decimal import Decimal
from typing import Union

from django.conf import settings

from prices import Money, TaxedMoney

try:
    DEFAULT_TAXJAR_PRODUCT_TAX_CODE = settings.DEFAULT_TAXJAR_PRODUCT_TAX_CODE
except AttributeError:
    # Use blank, as it will default to a nonspecific value.
    DEFAULT_TAXJAR_PRODUCT_TAX_CODE = ''


class LineItem(object):
    """Helper object for unifying input for order based taxes."""

    def __init__(self, id: str, quantity: int, unit_price: Money,
                 product_tax_code: str=None, discount: Money=None):
        self.id = id
        self.quantity = quantity
        self.unit_price = unit_price
        self.product_tax_code = product_tax_code
        self.discount = discount

    @property
    def dictionary(self):
        return {
            'id': self.id,
            'quantity': self.quantity,
            'unit_price': str(self.unit_price.amount),
            'product_tax_code': (self.product_tax_code or
                                 DEFAULT_TAXJAR_PRODUCT_TAX_CODE),
            'discount': str(self.discount.amount) if self.discount else 0
        }


def tax_amount(base: Union[Money, TaxedMoney], amount: Decimal, *,
               keep_gross=False):
    """
    Apply a tax of an amount by increasing gross or decreasing net amount.

    This only works on Money or TaxedMoney and not MoneyRanges
    """
    if isinstance(base, TaxedMoney):
        if keep_gross:
            net = base.net - Money(amount, base.currency).quantize()
            return TaxedMoney(net=net, gross=base.gross)
        else:
            gross = base.gross + Money(amount, base.currency).quantize()
            return TaxedMoney(net=base.net, gross=gross)
    elif isinstance(base, Money):
        if keep_gross:
            net = base - Money(amount, base.currency).quantize()
            return TaxedMoney(net=net, gross=base)
        else:
            gross = base + Money(amount, base.currency).quantize()
            return TaxedMoney(net=base, gross=gross)
