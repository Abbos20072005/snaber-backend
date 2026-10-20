from django.core.management.base import BaseCommand
from django.db import transaction

from apps.product.models import Category, Product

# parent code -> [(code suffix, (en, ru, uz), product name keywords)]
# Products of the parent are moved into the first child whose keyword matches the product
# name (the first child is the fallback), so the products stay reachable once the parent
# stops being a leaf.
THIRD_LEVEL = {
    "sec-01-1": [
        ("1", ("Power cable", "Силовой кабель", "Quvvat kabeli"), ["cable vvg"]),
        ("2", ("Installation wire", "Монтажный провод", "Montaj simi"), ["wire"]),
        ("3", ("Flexible cord", "Шнур гибкий", "Egiluvchan shnur"), ["cord"]),
        ("4", ("Network cable", "Сетевой кабель", "Tarmoq kabeli"), ["utp", "network"]),
    ],
    "sec-01-4": [
        ("1", ("Sockets", "Розетки", "Rozetkalar"), ["socket"]),
        ("2", ("Switches", "Выключатели", "O'chirgichlar"), ["switch"]),
        ("3", ("Plugs", "Вилки", "Vilkalar"), ["plug"]),
        ("4", ("Extension cords", "Удлинители", "Uzaytirgichlar"), ["extension cord"]),
    ],
    "sec-06-1": [
        ("1", ("Self-tapping screws", "Саморезы", "O'ziburama vintlar"), ["screw"]),
        ("2", ("Bolts", "Болты", "Boltlar"), ["bolt"]),
        ("3", ("Nuts and washers", "Гайки и шайбы", "Gayka va shaybalar"), ["nut", "washer"]),
    ],
    "sec-06-3": [
        ("1", ("Wedge anchors", "Анкеры клиновые", "Ponali ankerlar"), ["wedge"]),
        ("2", ("Plastic dowels", "Дюбели пластиковые", "Plastik dyubellar"), ["dowel"]),
        ("3", ("Chemical anchors", "Химические анкеры", "Kimyoviy ankerlar"), ["chemical"]),
    ],
    "sec-07-1": [
        ("1", ("Rutile electrodes", "Электроды рутиловые", "Rutil elektrodlar"), ["mp-3"]),
        ("2", ("Basic electrodes", "Электроды основные", "Asosiy elektrodlar"), ["uoni"]),
        ("3", ("Stainless steel electrodes", "Электроды для нержавейки", "Zanglamas po'lat elektrodlari"), ["stainless"]),
    ],
    "sec-07-5": [
        ("1", ("Welding inverters", "Сварочные инверторы", "Payvandlash invertorlari"), ["inverter"]),
        ("2", ("Semi-automatic welders", "Сварочные полуавтоматы", "Payvandlash yarim avtomatlari"), ["semi"]),
        ("3", ("Welding accessories", "Сварочные аксессуары", "Payvandlash aksessuarlari"), ["mask", "holder"]),
    ],
    "sec-08-1": [
        ("1", ("Metal cutting discs", "Диски по металлу", "Metall kesish disklari"), ["metal"]),
        ("2", ("Stone cutting discs", "Диски по камню", "Tosh kesish disklari"), ["stone"]),
        ("3", ("Diamond discs", "Алмазные диски", "Olmos disklari"), ["diamond"]),
    ],
    "sec-10-1": [
        ("1", ("Polypropylene pipes", "Полипропиленовые трубы", "Polipropilen quvurlar"), ["pp pipe"]),
        ("2", ("Metal-plastic pipes", "Металлопластиковые трубы", "Metall-plastik quvurlar"), ["metal-plastic"]),
        ("3", ("Fittings", "Фитинги", "Fitinglar"), ["fitting"]),
    ],
    "sec-12-5": [
        ("1", ("Bitumen mastics", "Битумные мастики", "Bitum mastikalari"), ["bitumen"]),
        ("2", ("Silicone sealants", "Силиконовые герметики", "Silikon germetiklar"), ["silicone"]),
        ("3", ("Polyurethane foam", "Монтажная пена", "Montaj ko'pigi"), ["foam"]),
    ],
    "sec-17-1": [
        ("1", ("Radiators", "Радиаторы", "Radiatorlar"), ["radiator"]),
        ("2", ("Heating cables and mats", "Греющие кабели и маты", "Isitish kabellari va matlari"), ["heating"]),
        ("3", ("Electric heaters", "Электрообогреватели", "Elektr isitgichlar"), ["electric"]),
    ],
    "sec-26-1": [
        ("1", ("Basin faucets", "Смесители для раковины", "Rakovina uchun aralashtirgichlar"), ["basin"]),
        ("2", ("Shower faucets", "Смесители для душа", "Dush uchun aralashtirgichlar"), ["shower"]),
        ("3", ("Kitchen faucets", "Смесители для кухни", "Oshxona aralashtirgichlari"), ["kitchen"]),
    ],
    "sec-27-1": [
        ("1", ("Interior paints", "Краски для внутренних работ", "Ichki bo'yoqlar"), ["paint"]),
        ("2", ("Primers", "Грунтовки", "Gruntovkalar"), ["primer"]),
        ("3", ("Enamels", "Эмали", "Emallar"), ["enamel"]),
    ],
    "sec-27-2": [
        ("1", ("Step ladders", "Стремянки", "Zinapoyalar"), ["step ladder"]),
        ("2", ("Extension ladders", "Лестницы раздвижные", "Surma zinapoyalar"), ["extension"]),
        ("3", ("Scaffolding", "Строительные леса", "Qurilish iskalalari"), ["scaffold"]),
    ],
    "sec-19-4": [
        ("1", ("Mineral wool", "Минеральная вата", "Mineral paxta"), ["mineral wool"]),
        ("2", ("XPS boards", "Плиты XPS", "XPS plitalari"), ["xps"]),
        ("3", ("Foam boards", "Пенопласт", "Penoplast"), ["foam"]),
    ],
    "sec-19-1": [
        ("1", ("Cement and concrete", "Цемент и бетон", "Sement va beton"), ["cement", "concrete"]),
        ("2", ("Bricks and blocks", "Кирпич и блоки", "G'isht va bloklar"), ["brick", "block"]),
        ("3", ("Rebar and profile pipes", "Арматура и профильные трубы", "Armatura va profil quvurlar"), ["rebar", "profile pipe"]),
        ("4", ("Timber and plywood", "Пиломатериалы и фанера", "Yog'och va faner"), ["board", "plywood"]),
        ("5", ("Gypsum and dry mixes", "Гипсокартон и сухие смеси", "Gipsokarton va quruq aralashmalar"), ["gypsum", "adhesive"]),
        ("6", ("Roofing", "Кровля", "Tom yopish materiallari"), ["metal tile", "corrugated"]),
        ("7", ("Floor tiles and laminate", "Плитка и ламинат", "Plitka va laminat"), ["tile 6", "porcelain", "laminate"]),
        ("8", ("Power tools", "Электроинструмент", "Elektr asboblar"), ["hammer", "grinder"]),
        ("9", ("Doors and windows", "Двери и окна", "Eshik va derazalar"), ["door", "window"]),
        ("10", ("Waterproofing membranes", "Гидроизоляционные мембраны", "Gidroizolyatsiya membranalari"), ["membrane"]),
    ],
}


class Command(BaseCommand):
    help = "Add third-level categories under existing subcategories and move their products."

    @transaction.atomic
    def handle(self, *args, **options):
        created = moved = 0

        for parent_code, children in THIRD_LEVEL.items():
            parent = Category.objects.filter(code=parent_code).first()
            if not parent:
                self.stdout.write(self.style.WARNING(f"Skip {parent_code}: not found"))
                continue

            nodes = []
            for suffix, (en, ru, uz), keywords in children:
                node, was_created = Category.objects.get_or_create(
                    code=f"{parent_code}-{suffix}",
                    defaults={
                        "name": en,
                        "name_en": en,
                        "name_ru": ru,
                        "name_uz": uz,
                        "parent": parent,
                        "level": parent.level + 1,
                        "is_active": True,
                    },
                )
                created += was_created
                nodes.append((node, keywords))

            for product in Product.objects.filter(category=parent):
                name = product.name_en.lower()
                target = next(
                    (
                        node
                        for node, keywords in nodes
                        if any(keyword in name for keyword in keywords)
                    ),
                    nodes[0][0],
                )
                Product.objects.filter(pk=product.pk).update(category=target)
                moved += 1

        self.stdout.write(
            self.style.SUCCESS(f"Created {created} categories, moved {moved} products")
        )
