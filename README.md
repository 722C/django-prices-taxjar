# django-prices-taxjar: [TaxJar API](https://taxjar.com/) support for `prices`

[![Build Status](https://secure.travis-ci.org/722C/django-prices-taxjar.png)](https://travis-ci.org/722C/django-prices-taxjar) [![codecov.io](https://img.shields.io/codecov/c/github/722C/django-prices-taxjar/master.svg)](http://codecov.io/github/722C/django-prices-taxjar?branch=master)

# Note

While this can work with VAT, it is more optimized towards the US. For a fully VAT compatible system, look at [django-prices-vatlayer](https://github.com/mirumee/django-prices-vatlayer), which this is forked from. Notably, lower taxes for some products are not currently taken into account.

This does **not** have a compatible API with [django-prices-vatlayer](https://github.com/mirumee/django-prices-vatlayer), but it does have similarities.

# Example

```python
from prices import Money
from django_prices_taxjar.utils import (
    get_tax_for_rate, get_tax_rates_for_country)

de_tax_rates = get_tax_rates_for_country('DE')
books_tax = get_tax_for_rate(de_tax_rates, 'books')

price_with_tax = books_tax(Money(10, 'EUR'))
print(price_with_tax)
# TaxedMoney(net=Money('10', 'EUR'), gross=Money('11', 'EUR'))

price_with_tax = books_tax(
    TaxedMoney(net=Money(10, 'EUR'), gross=Money(10, 'EUR')))
print(price_with_tax)
# TaxedMoney(net=Money('10', 'EUR'), gross=Money('11', 'EUR'))
```

# Installation

The package can easily be installed via pip:

```
pip install django-prices-taxjar
```

After installation, you'll also need to setup your site to use it. To do that, open your `settings.py` and do the following:

1.  Add `'django_prices_taxjar',` to your `INSTALLED_APPS`
2.  Add `TAXJAR_ACCESS_KEY = 'YOUR_API_KEY_HERE'` line
3.  Replace `YOUR_API_KEY_HERE` with the API key that you have obtained from taxjar API

Lastly, run `manage.py migrate` to create new tables in your database and `manage.py get_tax_rates` to populate them with initial data.

# Updating Tax rates

To get current tax rates from the API run the `get_tax_rates` management command.

You may also set cron job for running this task daily to always be up to date with current tax rates.
