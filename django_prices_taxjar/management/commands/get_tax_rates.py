from django.core.management.base import BaseCommand

from ... import utils


class Command(BaseCommand):
    help = 'Get current tax rates in regions and saves to database'

    def handle(self, *args, **options):
        json_response_rates = utils.fetch_tax_rates()
        utils.create_objects_from_json(json_response_rates)

        json_response_types = utils.fetch_categories()
        utils.save_tax_categories(json_response_types)
