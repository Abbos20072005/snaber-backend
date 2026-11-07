import csv
import io
import math
import os
import re

from openpyxl import load_workbook

from apps.core.exceptions import ValidationError

MAX_LINES = 200
MAX_FILE_SIZE = 2 * 1024 * 1024

# "Cement M400 - 20", "Cement M400 x 20 bags", "Cement M400 20"
LINE_PATTERN = re.compile(
    r"^(?P<name>.+?)[\s,;:|\-–—x×*]+(?P<quantity>\d+(?:[.,]\d+)?)\s*[^\W\d_]{0,12}\.?$",
    re.IGNORECASE,
)


def to_quantity(value):
    try:
        return max(1, math.ceil(float(str(value).replace(",", "."))))
    except ValueError:
        return None


def parse_text(text):
    lines = []
    for row in text.splitlines():
        row = row.strip()
        if not row:
            continue
        match = LINE_PATTERN.match(row)
        if match:
            lines.append(
                {
                    "name": match["name"].strip(),
                    "quantity": to_quantity(match["quantity"]),
                }
            )
        else:
            lines.append({"name": row, "quantity": 1})
    return lines


def read_rows(file):
    extension = os.path.splitext(file.name)[1].lower()
    if extension == ".xlsx":
        sheet = load_workbook(file, read_only=True, data_only=True).active
        return list(sheet.iter_rows(values_only=True))
    if extension == ".csv":
        content = file.read()
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = content.decode("cp1251")
        try:
            dialect = csv.Sniffer().sniff(text[:2048], delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        return list(csv.reader(io.StringIO(text), dialect))
    raise ValidationError(
        message="Upload an .xlsx or .csv file", message_key="unsupported_file"
    )


def parse_file(file):
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(message="File is too large", message_key="file_too_large")
    lines = []
    for index, row in enumerate(read_rows(file)):
        name = str(row[0]).strip() if row and row[0] is not None else ""
        cell = row[1] if len(row) > 1 and row[1] is not None else 1
        quantity = to_quantity(cell)
        # The first row is a header when its quantity column is not a number.
        if index == 0 and quantity is None:
            continue
        if name:
            lines.append({"name": name, "quantity": quantity or 1})
    return lines


def parse_lines(text, file):
    lines = parse_text(text) if text else parse_file(file)
    if len(lines) > MAX_LINES:
        raise ValidationError(
            message=f"The list can have at most {MAX_LINES} lines",
            message_key="too_many_lines",
        )
    return lines
