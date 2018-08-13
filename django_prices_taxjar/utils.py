from decimal import Decimal

from typing import Iterable

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from prices import flat_tax, Money

from . import LineItem, tax_amount

from .models import Tax, TaxCategories, DEFAULT_TYPES_INSTANCE_ID

try:
    ACCESS_KEY = settings.TAXJAR_ACCESS_KEY
except AttributeError:
    raise ImproperlyConfigured('TAXJAR_ACCESS_KEY is required')

DEFAULT_URL = 'https://api.taxjar.com/v2/'

TAXJAR_API = getattr(settings, 'TAXJAR_API', DEFAULT_URL)

RATES_URL = 'summary_rates'
TYPES_URL = 'categories'
RATES_LOCATION_URL = 'rates/{postal_code}'
ORDER_TAXES_URL = 'taxes'

CACHE_KEY = getattr(
    settings, 'TAXJAR_CACHE_KEY', 'taxjar_summary_rates')
INDIVIDUAL_CACHE_KEY = getattr(
    settings, 'TAXJAR_INDIVIDUAL_CACHE_KEY', 'taxjar_rates')
CACHE_TIME = getattr(settings, 'TAXJAR_CACHE_TTL', 60 * 60)


def validate_data(json_data):
    if json_data.get('error', None):
        info = json_data['error']
        raise ImproperlyConfigured(info)


def fetch_from_api(url, method, additional_data=None):
    url = TAXJAR_API + url
    headers = {
        'Authorization': 'Token token="{}"'.format(ACCESS_KEY)
    }
    response = method(
        url, headers=headers, data=additional_data)
    return response.json()


def fetch_categories():
    return fetch_from_api(TYPES_URL, requests.get)


def fetch_tax_rates():
    return fetch_from_api(RATES_URL, requests.get)


def fetch_tax_for_address(postal_code, address_data):
    return fetch_from_api(
        RATES_LOCATION_URL.format(postal_code=postal_code),
        requests.get,
        additional_data=address_data)


def fetch_tax_for_order(order_data):
    return fetch_from_api(
        ORDER_TAXES_URL, requests.post, additional_data=order_data)


def save_tax_categories(json_data):
    validate_data(json_data)

    categories = json_data['categories']
    TaxCategories.objects.update_or_create(
        id=DEFAULT_TYPES_INSTANCE_ID, defaults={'types': categories})


def create_objects_from_json(json_data):
    validate_data(json_data)

    # Handle proper response
    rates = json_data['summary_rates']
    for rate in rates:
        country_code = rate['country_code']
        region_code = rate['region_code']

        # Convert to strings to avoid potential issues with rates being floats.
        try:
            rate['minimum_rate']['rate'] = str(rate['minimum_rate']['rate'])
        except (KeyError):
            pass
        try:
            rate['average_rate']['rate'] = str(rate['average_rate']['rate'])
        except (KeyError):
            pass

        Tax.objects.update_or_create(
            country_code=country_code, region_code=region_code,
            defaults={'data': rate})
        country_region_cache_key = CACHE_KEY + \
            country_code + (region_code or '')
        cache.set(country_region_cache_key, rate, CACHE_TIME)


def get_tax_rates_for_region(country_code: str, region_code: str=None,
                             force_refresh: bool=False):
    """
    Get the tax rates for a given region.

    country_code is required, but region_code is not.  If you do not have a
    region_code, either do not pass region_code, or pass None.

    In the US, region_code is the state/territory postal code.
    In Canada, region_code is the province/territory postal code.
    """

    country_region_cache_key = CACHE_KEY + country_code + (region_code or '')
    tax_rates = cache.get(country_region_cache_key)
    if not tax_rates or force_refresh:
        try:
            region_tax = Tax.objects.get(country_code=country_code,
                                         region_code=region_code)
            tax_rates = region_tax.data
            cache.set(country_region_cache_key, tax_rates, CACHE_TIME)
        except ObjectDoesNotExist:
            tax_rates = None
    return tax_rates


def get_tax_rate(tax_rates: dict, rate_name=None):
    """
    Get the tax rate for a set of tax rates and a given rate_name.

    WARNING: rate_name is currently not used.
    This is due to the nature of how TaxJar's API works.
    """

    if tax_rates is None:
        return None

    rate = tax_rates['average_rate']['rate']

    return rate


def get_tax_for_rate(tax_rates: dict, rate_name=None):
    """
    Get the tax for a set of tax rates and a given rate_name.

    WARNING: rate_name is currently not used.
    This is due to the nature of how TaxJar's API works.
    """

    rate = get_tax_rate(tax_rates, rate_name)
    if rate is None:
        return None

    final_tax_rate = Decimal(rate)

    def tax(base, keep_gross=False):
        return flat_tax(base, final_tax_rate, keep_gross=keep_gross)

    return tax


def get_tax_categories():
    """Get a list of the available tax categories offered."""

    categories = TaxCategories.objects.singleton()
    return categories.types if categories else []


def get_tax_for_address(postal_code: str, country_code: str=None,
                        region_code: str=None, city: str=None,
                        street: str=None, force_refresh: bool=False):
    """
    Get the tax rate for a given address.

    postal_code is required, but the more fields provided,
    the potentially more accurate the final result.
    """

    address_cache_key = INDIVIDUAL_CACHE_KEY + postal_code + \
        (country_code or '') + (region_code or '') + \
        (city or '') + (street or '')
    address_cache_key = address_cache_key.replace(' ', '_')

    rates = cache.get(address_cache_key)
    if not rates or force_refresh:
        additional_data = {}
        if country_code:
            additional_data['country'] = country_code
        if region_code:
            additional_data['state'] = region_code
        if city:
            additional_data['city'] = city
        if street:
            additional_data['street'] = street

        rates = fetch_tax_for_address(postal_code, additional_data)['rate']

        cache.set(address_cache_key, rates, CACHE_TIME)

    rate = rates['combined_rate']

    final_tax_rate = Decimal(rate)

    def tax(base, keep_gross=False):
        return flat_tax(base, final_tax_rate, keep_gross=keep_gross)

    return tax


def is_shipping_taxable_for_address(postal_code: str, country_code: str=None,
                                    region_code: str=None, city: str=None,
                                    street: str=None, force_refresh: bool=False):
    """
    Get the tax rate for a given address.

    postal_code is required, but the more fields provided,
    the potentially more accurate the final result.
    """

    address_cache_key = INDIVIDUAL_CACHE_KEY + postal_code + \
        (country_code or '') + (region_code or '') + \
        (city or '') + (street or '')
    address_cache_key = address_cache_key.replace(' ', '_')

    rates = cache.get(address_cache_key)
    if not rates or force_refresh:
        additional_data = {}
        if country_code:
            additional_data['country'] = country_code
        if region_code:
            additional_data['state'] = region_code
        if city:
            additional_data['city'] = city
        if street:
            additional_data['street'] = street

        rates = fetch_tax_for_address(postal_code, additional_data)['rate']

        cache.set(address_cache_key, rates, CACHE_TIME)

    return rates['freight_taxable']


def get_taxes_for_order(shipping_cost: Money, country_code: str,
                        postal_code: str=None, region_code: str=None,
                        city: str=None, street: str=None, amount: Money=None,
                        line_items: Iterable[LineItem]=None):
    """
    Get the tax for an individual order.

    amount or line_items is required.  line_items will take precedence if both
    are included.

    line_items is an iterable collection of django_prices_taxjar.LineItem.

    If country_code is 'US', then postal_code is required.
    If country_code is 'US' or 'CA', then region_code is required.

    WARNING: This explicitly does not cache the results, as this could change
    very quickly based off of the individual line items and any associated tax
    code.
    """
    if amount is None and line_items is None:
        raise TypeError('At least one of amount or line_items is required.')

    data = {
        "to_country": country_code,
        "shipping": shipping_cost.amount,
    }

    if postal_code:
        data['to_zip'] = postal_code
    if region_code:
        data['to_state'] = region_code
    if city:
        data['to_city'] = city
    if street:
        data['to_street'] = street
    if line_items:
        data['line_items'] = list(
            map(lambda item: item.dictionary, line_items))
    elif amount:
        data['amount'] = amount.amount

    response = fetch_tax_for_order(data)

    amount_to_collect = Decimal(str(response['tax']['amount_to_collect']))

    def tax(base, keep_gross=False):
        return tax_amount(base, amount_to_collect, keep_gross=keep_gross)

    return tax
