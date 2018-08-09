import os

import django
import pytest


def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
    django.setup()


@pytest.fixture
def json_error():
    data = {'success': False, 'error': {'info': 'Invalid json'}}
    return data


@pytest.fixture
def json_success():
    data = {
        "summary_rates": [
            {
                "country_code": "US",
                "country": "United States",
                "region_code": "CA",
                "region": "California",
                "minimum_rate": {
                    "label": "State Tax",
                    "rate": 0.065
                },
                "average_rate": {
                    "label": "Tax",
                    "rate": 0.0827
                }
            },
            {
                "country_code": "CA",
                "country": "Canada",
                "region_code": "BC",
                "region": "British Columbia",
                "minimum_rate": {
                    "label": "GST",
                    "rate": 0.05
                },
                "average_rate": {
                    "label": "PST",
                    "rate": 0.12
                }
            },
            {
                "country_code": "UK",
                "country": "United Kingdom",
                "region_code": None,
                "region": None,
                "minimum_rate": {
                    "label": "VAT",
                    "rate": 0.2
                },
                "average_rate": {
                    "label": "VAT",
                    "rate": 0.2
                }
            }
        ]
    }
    return data


@pytest.fixture
def json_types_success():
    data = {
        "categories": [
            {
                "name": "Clothing",
                "product_tax_code": "20010",
                "description": " All human wearing apparel suitable for general use"
            },
            {
                "name": "Software as a Service",
                "product_tax_code": "30070",
                "description": "Pre-written software, delivered electronically, but access remotely."
            },
            {
                "name": "Digital Goods",
                "product_tax_code": "31000",
                "description": "Digital products transferred electronically, meaning obtained by the purchaser by means other than tangible storage media."
            },
            {
                "name": "Candy",
                "product_tax_code": "40010",
                "description": "Candy and similar items"
            },
            {
                "name": "Supplements",
                "product_tax_code": "40020",
                "description": "Non-food dietary supplements"
            },
            {
                "name": "Food & Groceries",
                "product_tax_code": "40030",
                "description": "Food for humans consumption, unprepared"
            },
            {
                "name": "Soft Drinks",
                "product_tax_code": "40050",
                "description": "Soft drinks, soda, and other similar beverages. Does not include fruit juices and water."
            },
            {
                "name": "Bottled Water",
                "product_tax_code": "40060",
                "description": "Bottled, drinkable water for human consumption."
            },
            {
                "name": "Prepared Foods",
                "product_tax_code": "41000",
                "description": "Foods intended for on-site consumption. Ex. Restaurant meals."
            },
            {
                "name": "Non-Prescription",
                "product_tax_code": "51010",
                "description": "Drugs for human use without a prescription"
            },
            {
                "name": "Prescription",
                "product_tax_code": "51020",
                "description": "Drugs for human use with a prescription"
            },
            {
                "name": "Books",
                "product_tax_code": "81100",
                "description": "Books, printed"
            },
            {
                "name": "Textbook",
                "product_tax_code": "81110",
                "description": "Textbooks, printed"
            },
            {
                "name": "Religious Books",
                "product_tax_code": "81120",
                "description": "Religious books and manuals, printed"
            },
            {
                "name": "Magazines & Subscriptions",
                "product_tax_code": "81300",
                "description": "Periodicals, printed, sold by subscription"
            },
            {
                "name": "Magazine",
                "product_tax_code": "81310",
                "description": "Periodicals, printed, sold individually"
            },
            {
                "name": "Other Exempt",
                "product_tax_code": "99999",
                "description": "Item is exempt"
            }
        ]
    }
    return data


@pytest.fixture
def json_success_for_address():
    data = {
        "rate": {
            "zip": "05495-2086",
            "country": "US",
            "country_rate": "0.0",
            "state": "VT",
            "state_rate": "0.06",
            "county": "CHITTENDEN",
            "county_rate": "0.0",
            "city": "WILLISTON",
            "city_rate": "0.0",
            "combined_district_rate": "0.01",
            "combined_rate": "0.07",
            "freight_taxable": True
        }
    }
    return data


@pytest.fixture
def json_success_for_order():
    data = {
        "tax": {
            "order_total_amount": 16.5,
            "shipping": 1.5,
            "taxable_amount": 15,
            "amount_to_collect": 1.35,
            "rate": 0.09,
            "has_nexus": True,
            "freight_taxable": False,
            "tax_source": "destination",
            "breakdown": {
                "taxable_amount": 15,
                "tax_collectable": 1.35,
                "combined_tax_rate": 0.09,
                "state_taxable_amount": 15,
                "state_tax_rate": 0.0625,
                "state_tax_collectable": 0.94,
                "county_taxable_amount": 15,
                "county_tax_rate": 0.0025,
                "county_tax_collectable": 0.04,
                "city_taxable_amount": 0,
                "city_tax_rate": 0,
                "city_tax_collectable": 0,
                "special_district_taxable_amount": 15,
                "special_tax_rate": 0.025,
                "special_district_tax_collectable": 0.38,
                "line_items": [
                    {
                        "id": "1",
                        "taxable_amount": 15,
                        "tax_collectable": 1.35,
                        "combined_tax_rate": 0.09,
                        "state_taxable_amount": 15,
                        "state_sales_tax_rate": 0.0625,
                        "state_amount": 0.94,
                        "county_taxable_amount": 15,
                        "county_tax_rate": 0.0025,
                        "county_amount": 0.04,
                        "city_taxable_amount": 0,
                        "city_tax_rate": 0,
                        "city_amount": 0,
                        "special_district_taxable_amount": 15,
                        "special_tax_rate": 0.025,
                        "special_district_amount": 0.38
                    }
                ]
            }
        }
    }
    return data
