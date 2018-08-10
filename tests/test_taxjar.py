import pytest
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django_prices_taxjar import utils
from django_prices_taxjar.models import Tax, TaxCategories
from prices import Money, TaxedMoney


from django_prices_taxjar import LineItem


@pytest.fixture
def tax_country(db, json_success):
    data = json_success['summary_rates'][0]
    # Convert to strings to avoid potential issues with rates being floats.
    try:
        data['minimum_rate']['rate'] = str(data['minimum_rate']['rate'])
    except (KeyError):
        pass
    try:
        data['average_rate']['rate'] = str(data['average_rate']['rate'])
    except (KeyError):
        pass
    return Tax.objects.create(country_code=data['country_code'], region_code=data['region_code'], data=data)


@pytest.fixture
def rate_type(db, json_types_success):
    return TaxCategories.objects.create(
        types=json_types_success['categories'])


@pytest.fixture
def fetch_tax_rates_success(monkeypatch, json_success):
    monkeypatch.setattr(utils, 'fetch_tax_rates', lambda: json_success)


@pytest.fixture
def fetch_tax_rates_error(monkeypatch, json_error):
    monkeypatch.setattr(utils, 'fetch_tax_rates', lambda: json_error)


@pytest.fixture
def fetch_categories_success(monkeypatch, json_types_success):
    monkeypatch.setattr(utils, 'fetch_categories', lambda: json_types_success)


@pytest.fixture
def fetch_categories_error(monkeypatch, json_error):
    monkeypatch.setattr(utils, 'fetch_categories', lambda: json_error)


@pytest.fixture
def fetch_tax_rate_for_address_success(monkeypatch, json_success_for_address):
    monkeypatch.setattr(utils, 'fetch_tax_for_address',
                        lambda *args, **kwargs: json_success_for_address)


@pytest.fixture
def fetch_tax_rate_for_order_success(monkeypatch, json_success_for_order):
    monkeypatch.setattr(utils, 'fetch_tax_for_order',
                        lambda *args, **kwargs: json_success_for_order)


def test_validate_data_invalid(json_error):
    with pytest.raises(ImproperlyConfigured):
        utils.validate_data(json_error)


def test_validate_data_valid(json_success):
    assert utils.validate_data(json_success) is None


@pytest.mark.django_db
def test_create_objects_from_json_error(json_error, json_success):
    tax_counts = Tax.objects.count()

    with pytest.raises(ImproperlyConfigured):
        utils.create_objects_from_json(json_error)

    utils.create_objects_from_json(json_success)
    assert tax_counts + 3 == Tax.objects.count()


@pytest.mark.django_db
def test_create_objects_from_json_success(json_success):
    for json_dict in [json_success]:
        utils.create_objects_from_json(json_dict)
    assert Tax.objects.count() == 3


@pytest.mark.django_db
def test_save_tax_categories(json_types_success):
    utils.save_tax_categories(json_types_success)
    assert 1 == TaxCategories.objects.count()

    utils.save_tax_categories(json_types_success)
    assert 1 == TaxCategories.objects.count()


@pytest.mark.django_db
def test_get_tax_categories(rate_type):
    categories = utils.get_tax_categories()
    assert categories == rate_type.types


@pytest.mark.django_db
def test_get_tax_categories_no_categories():
    categories = utils.get_tax_categories()
    assert categories == []


def test_get_tax_rates_for_country_region(tax_country):
    country_code = tax_country.country_code
    region_code = tax_country.region_code
    tax_rates = utils.get_tax_rates_for_region(country_code, region_code)
    assert tax_rates['country'] == 'United States'
    assert tax_rates['region'] == 'California'
    assert tax_rates['minimum_rate']['rate'] == '0.065'
    assert tax_rates['average_rate']['rate'] == '0.0827'


@pytest.mark.django_db
def test_get_tax_rates_for_country_invalid_code():
    tax_rates = utils.get_tax_rates_for_region('XX')
    assert tax_rates is None


def test_get_tax_rate_standard_rate(tax_country):
    tax_rates = tax_country.data
    standard_rate = utils.get_tax_rate(tax_rates)
    assert standard_rate == tax_rates['average_rate']['rate']


def test_get_tax_rate_fallback_to_standard_rate(tax_country):
    tax_rates = tax_country.data
    hotels_rate = utils.get_tax_rate(tax_rates, 'hotels')
    assert hotels_rate == tax_rates['average_rate']['rate']


def test_get_tax_for_rate_standard_rate(tax_country):
    tax_rates = tax_country.data
    standard_tax = utils.get_tax_for_rate(tax_rates)

    assert standard_tax(Money(100, 'USD')) == TaxedMoney(
        net=Money(100, 'USD'), gross=Money('108.27', 'USD'))
    assert standard_tax(Money(100, 'USD'), keep_gross=True) == TaxedMoney(
        net=Money('92.36', 'USD'), gross=Money(100, 'USD'))

    taxed_money = TaxedMoney(net=Money(100, 'USD'), gross=Money(100, 'USD'))
    assert standard_tax(taxed_money) == TaxedMoney(
        net=Money(100, 'USD'), gross=Money('108.27', 'USD'))
    assert standard_tax(taxed_money, keep_gross=True) == TaxedMoney(
        net=Money('92.36', 'USD'), gross=Money(100, 'USD'))


def test_get_tax_for_rate_fallback_to_standard_rate(tax_country):
    tax_rates = tax_country.data
    hotels_tax = utils.get_tax_for_rate(tax_rates, 'hotels')

    assert hotels_tax(Money(100, 'USD')) == TaxedMoney(
        net=Money(100, 'USD'), gross=Money('108.27', 'USD'))
    assert hotels_tax(Money(100, 'USD'), keep_gross=True) == TaxedMoney(
        net=Money('92.36', 'USD'), gross=Money(100, 'USD'))

    taxed_money = TaxedMoney(net=Money(100, 'USD'), gross=Money(100, 'USD'))
    assert hotels_tax(taxed_money) == TaxedMoney(
        net=Money(100, 'USD'), gross=Money('108.27', 'USD'))
    assert hotels_tax(taxed_money, keep_gross=True) == TaxedMoney(
        net=Money('92.36', 'USD'), gross=Money(100, 'USD'))


def test_get_tax_for_rate_reduced_rate(tax_country):
    tax_rates = tax_country.data
    books_tax = utils.get_tax_for_rate(tax_rates, 'books')

    assert books_tax(Money(100, 'USD')) == TaxedMoney(
        net=Money(100, 'USD'), gross=Money('108.27', 'USD'))
    assert books_tax(Money(100, 'USD'), keep_gross=True) == TaxedMoney(
        net=Money('92.36', 'USD'), gross=Money(100, 'USD'))

    taxed_money = TaxedMoney(net=Money(100, 'USD'), gross=Money(100, 'USD'))
    assert books_tax(taxed_money) == TaxedMoney(
        net=Money(100, 'USD'), gross=Money('108.27', 'USD'))
    assert books_tax(taxed_money, keep_gross=True) == TaxedMoney(
        net=Money('92.36', 'USD'), gross=Money(100, 'USD'))


def test_get_tax_for_address(fetch_tax_rate_for_address_success):
    tax_for_address = utils.get_tax_for_address(
        '05495-2086', 'US', 'VT', 'Williston', '312 Hurricane Lane')

    assert tax_for_address(Money(100, 'USD')) == TaxedMoney(
        net=Money(100, 'USD'), gross=Money('107.00', 'USD'))
    assert tax_for_address(Money(100, 'USD'), keep_gross=True) == TaxedMoney(
        net=Money('93.46', 'USD'), gross=Money(100, 'USD'))

    taxed_money = TaxedMoney(net=Money(100, 'USD'), gross=Money(100, 'USD'))
    assert tax_for_address(taxed_money) == TaxedMoney(
        net=Money(100, 'USD'), gross=Money('107.00', 'USD'))
    assert tax_for_address(taxed_money, keep_gross=True) == TaxedMoney(
        net=Money('93.46', 'USD'), gross=Money(100, 'USD'))


def test_get_shipping_taxable_for_address(fetch_tax_rate_for_address_success):
    shipping_taxable_for_address = utils.is_shipping_taxable_for_address(
        '05495-2086', 'US', 'VT', 'Williston', '312 Hurricane Lane')
    assert shipping_taxable_for_address == True


def test_get_taxes_for_order(fetch_tax_rate_for_order_success):
    tax_for_order = utils.get_taxes_for_order(
        Money('1.5', 'USD'), 'US', '90002', 'CA', 'Los Angeles',
        '1335 E 103rd St', None,
        [
            LineItem('1', 1, Money(15, 'USD'), '20010')
        ]
    )
    assert tax_for_order(Money(15, 'USD')) == TaxedMoney(
        net=Money(15, 'USD'), gross=Money('16.35', 'USD'))
    assert tax_for_order(Money(15, 'USD'), keep_gross=True) == TaxedMoney(
        net=Money('13.65', 'USD'), gross=Money(15, 'USD'))

    taxed_money = TaxedMoney(net=Money(15, 'USD'), gross=Money(15, 'USD'))
    assert tax_for_order(taxed_money) == TaxedMoney(
        net=Money(15, 'USD'), gross=Money('16.35', 'USD'))
    assert tax_for_order(taxed_money, keep_gross=True) == TaxedMoney(
        net=Money('13.65', 'USD'), gross=Money(15, 'USD'))
