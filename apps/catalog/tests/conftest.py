import pytest
from rest_framework.test import APIClient

from apps.catalog.importer import CatalogImporter
from apps.catalog.tests.fixtures import CATALOG


@pytest.fixture
def catalog(db):
    CatalogImporter(CATALOG).run()


@pytest.fixture
def api_client():
    return APIClient()
