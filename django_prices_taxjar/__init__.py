from typing import Union

from django.conf import settings

from prices import Money, TaxedMoney

try:
    DEFAULT_TAXJAR_PRODUCT_TAX_CODE = settings.DEFAULT_TAXJAR_PRODUCT_TAX_CODE
except AttributeError:
    DEFAULT_TAXJAR_PRODUCT_TAX_CODE = '99999'


class LineItem(object):
    """Helper object for unifying input for order based taxes."""

    def __init__(self, id: str, quantity: int, unit_price: Money,
                 product_tax_code=None: str, discount=None: Money):
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
            'unit_price': self.unit_price.value
            'product_tax_code': (self.product_tax_code or
                                 DEFAULT_TAXJAR_PRODUCT_TAX_CODE),
            'discount': self.discount.value if self.discount else 0
        }


def tax_amount(base: Union[Money, TaxedMoney], amount: Decimal, *,
               keep_gross=False):
    """
    Apply a tax of an amount by increasing gross or decreasing net amount.

    This only works on Money or TaxedMony and not MoneyRanges
    """
    if keep_gross:
        net = base - Money(amount, base.currency).quantize()
        return TaxedMoney(net=net, gross=base)
    else:
        gross = base + Money(amount, base.currency).quantize()
        return TaxedMoney(net=base, gross=gross)
