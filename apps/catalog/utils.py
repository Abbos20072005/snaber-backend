import re

# Frontend `compareValues` bilan bir xil tartib: avval dyuymli, keyin metrik
# qiymatlar, ular ichida haqiqiy o'lcham bo'yicha (#10 < 1/4", M6 < M10).
_METRIC_RE = re.compile(r"мм|^M\d|\sм$")
_GAUGE_RE = re.compile(r"^#(\d+)")
_MIXED_FRACTION_RE = re.compile(r"^(\d+)-(\d+)/(\d+)")
_FRACTION_RE = re.compile(r"^(\d+)/(\d+)")
_NUMBER_RE = re.compile(r"^[A-Za-z]{0,2}(\d+(?:\.\d+)?)")


def value_rank(value):
    """Return `(is_metric, size)`; `size` is None when the value has no number."""
    is_metric = 1 if _METRIC_RE.search(value) else 0
    value = value.strip()

    if match := _GAUGE_RE.match(value):
        return is_metric, 0.06 + 0.013 * int(match[1])
    if match := _MIXED_FRACTION_RE.match(value):
        denominator = int(match[3])
        if denominator:
            return is_metric, int(match[1]) + int(match[2]) / denominator
    if match := _FRACTION_RE.match(value):
        denominator = int(match[2])
        if denominator:
            return is_metric, int(match[1]) / denominator
    if match := _NUMBER_RE.match(value):
        return is_metric, float(match[1])
    return is_metric, None


def normalize_search(text):
    """Lowercase in Python: SQLite LIKE ignores case only for ASCII letters."""
    return " ".join((text or "").lower().replace("ё", "е").split())


def normalize_value(value):
    # "M10 " va "M10" ikki xil filtr bo'lib qolmasin.
    return " ".join((value or "").split())
