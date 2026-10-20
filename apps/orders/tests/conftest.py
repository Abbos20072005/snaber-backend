import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.catalog.importer import CatalogImporter
from apps.catalog.tests.fixtures import CATALOG


@pytest.fixture
def catalog(db):
    CatalogImporter(CATALOG).run()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def clear_throttle_history():
    # Throttle tarixi keshda: testlar bir-biriga ta'sir qilmasin.
    cache.clear()
    yield
    cache.clear()
