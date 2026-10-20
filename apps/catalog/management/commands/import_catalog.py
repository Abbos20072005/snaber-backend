import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.catalog.importer import CatalogImporter, CatalogImportError

DEFAULT_FILE = Path(__file__).resolve().parents[2] / "fixtures" / "catalog.json"


class Command(BaseCommand):
    help = "Frontend katalog eksportini (tools/export_catalog.mts) bazaga yuklaydi."

    def add_arguments(self, parser):
        parser.add_argument(
            "file", nargs="?", default=str(DEFAULT_FILE), help="JSON fayl (standart: fixtures/catalog.json)"
        )
        parser.add_argument(
            "--dry-run", action="store_true", help="Tekshiradi va hisoblaydi, bazaga yozmaydi"
        )
        parser.add_argument(
            "--deactivate-missing",
            action="store_true",
            help="Faylda yo'q mahsulotlarni nofaol qiladi",
        )

    def handle(self, *args, **options):
        path = Path(options["file"])
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise CommandError(f"Fayl topilmadi: {path}")
        except json.JSONDecodeError as error:
            raise CommandError(f"JSON noto'g'ri: {error}")

        importer = CatalogImporter(data, deactivate_missing=options["deactivate_missing"])
        try:
            stats = importer.run(dry_run=options["dry_run"])
        except CatalogImportError as error:
            raise CommandError("Import to'xtatildi:\n" + "\n".join(error.errors))

        lines = [f"{key}: {value}" for key, value in sorted(stats.items())]
        prefix = "Sinov (bazaga yozilmadi)" if options["dry_run"] else "Import tugadi"
        self.stdout.write(self.style.SUCCESS(f"{prefix}\n" + "\n".join(lines)))
