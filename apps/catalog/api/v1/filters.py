from rest_framework.exceptions import NotFound

from apps.catalog.browse import CatalogQuery
from apps.catalog.utils import normalize_search, normalize_value

ATTRIBUTE_PARAM_PREFIX = "attr_"
MAX_SEARCH_TERMS = 10
MAX_SEARCH_LENGTH = 200


def parse_category(params, tree):
    """`category=consumables/fasteners/bolts-screws` → Category; empty → whole catalog."""
    raw = (params.get("category") or "").strip("/ ")
    if not raw:
        return None
    category = tree.find(raw.split("/"))
    if category is None:
        raise NotFound("Kategoriya topilmadi")
    return category


def parse_catalog_query(params, tree, attributes_by_key):
    """Read `category`, `q` and `attr_<key>` (repeatable) query parameters.

    Atribut filtrlari prefiks bilan: frontenddagi `category` kalitli xususiyat
    `category` parametri bilan to'qnashmasin. Noma'lum kalitlar e'tiborsiz.
    """
    selection = {}
    for name in params:
        if not name.startswith(ATTRIBUTE_PARAM_PREFIX):
            continue
        key = name[len(ATTRIBUTE_PARAM_PREFIX) :]
        if key not in attributes_by_key:
            continue
        values = list(dict.fromkeys(filter(None, map(normalize_value, params.getlist(name)))))
        if values:
            selection[key] = values

    query = normalize_search((params.get("q") or "")[:MAX_SEARCH_LENGTH])
    return CatalogQuery(
        category=parse_category(params, tree),
        selection=selection,
        terms=query.split()[:MAX_SEARCH_TERMS],
    )
