from jsonfield import JSONField

from django.db import models
from django.utils.translation import pgettext_lazy

DEFAULT_TYPES_INSTANCE_ID = 1


class Tax(models.Model):
    country_code = models.CharField(
        pgettext_lazy('Tax field', 'country code'), max_length=2,
        db_index=True)
    region_code = models.CharField(
        pgettext_lazy('Tax field', 'region code'), max_length=2, db_index=True,
        blank=True, null=True)
    data = JSONField(pgettext_lazy('Tax field', 'data'))

    def __str__(self):
        return self.country_code


class TaxCategoriesQuerySet(models.QuerySet):
    def singleton(self):
        return self.filter(id=DEFAULT_TYPES_INSTANCE_ID).first()


class TaxCategories(models.Model):
    types = JSONField(pgettext_lazy('Tax field', 'types'))
    objects = TaxCategoriesQuerySet.as_manager()
