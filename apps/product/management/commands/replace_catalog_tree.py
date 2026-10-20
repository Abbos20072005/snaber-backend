"""Replace the catalog tree with the 5-group / 28-section industrial tree.

- Creates groups (level 0) -> sections (level 1, photos in media/seed/sec-NN.jpg)
  -> subcategories (level 2, leafs).
- Moves every product to its mapped subcategory (parks homeless building
  products under raw-materials) and migrates variant attributes/stocks.
- Deletes the old categories + orphaned attributes afterwards.

Usage:
    python manage.py replace_catalog_tree --confirm
"""

import os

from django.core.management.base import BaseCommand
from django.db import transaction

MEDIA_SEED_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "media", "seed"
)

# Groups: code, (en, ru, uz), sections: [{num, code, (en,ru,uz), subs: [(en,ru,uz), ...]}]
GROUPS = [
    {
        "code": "group-1",
        "n": (
            "Frequently bought consumables and tools",
            "Часто покупаемые расходники и инструменты",
            "Ko'p xarid qilinadigan sarf materiallari va asboblar",
        ),
        "sections": [
            {
                "num": "01", "code": "sec-01",
                "n": ("Electrical and lighting", "Электротехника и освещение", "Elektrotexnika va yoritish"),
                "subs": [
                    ("Wire and cable", "Провод и кабель", "Sim va kabel"),
                    ("Circuit breakers", "Автоматические выключатели", "Avtomatik o'chirgichlar"),
                    ("Starters and contactors", "Пускатели и контакторы", "Puskatel va kontaktorlar"),
                    ("Plugs and sockets", "Вилки и розетки", "Vilka va rozetkalar"),
                    ("Lamps and luminaires", "Лампы и светильники", "Lampa va yoritgichlar"),
                    ("Cable lugs and insulating tape", "Кабельные наконечники и изолента", "Kabel uchliklari va izolenta"),
                ],
            },
            {
                "num": "02", "code": "sec-02",
                "n": ("Bearings", "Подшипники", "Podshipniklar"),
                "subs": [
                    ("Ball bearings", "Шариковые подшипники", "Sharikli podshipniklar"),
                    ("Roller bearings", "Роликовые подшипники", "Rolikli podshipniklar"),
                    ("Mounted bearing units", "Корпусные подшипниковые узлы", "Korpusli podshipnik uzellari"),
                    ("Conveyor roller bearings", "Для конвейерных роликов", "Konveyer roliklari uchun"),
                    ("Bushings and liners", "Втулки и вкладыши", "Vtulka va vkladishlar"),
                ],
            },
            {
                "num": "03", "code": "sec-03",
                "n": ("Work safety and protection", "Охрана труда и защита", "Mehnat muhofazasi va himoya vositalari"),
                "subs": [
                    ("Workwear", "Спецодежда", "Maxsus kiyim"),
                    ("Safety footwear", "Спецобувь", "Maxsus poyabzal"),
                    ("Gloves and mittens", "Перчатки и рукавицы", "Qo'lqop va rukavitsalar"),
                    ("Helmets, goggles and masks", "Каски, очки и маски", "Kaska, ko'zoynak va niqoblar"),
                    ("Respirators and ear protection", "Респираторы и беруши", "Respirator va quloqchinlar"),
                    ("First aid kits", "Аптечки и первая помощь", "Aptechka va birinchi yordam"),
                    ("Fire safety", "Пожарная безопасность", "Yong'in xavfsizligi"),
                ],
            },
            {
                "num": "04", "code": "sec-04",
                "n": ("Cutting tools", "Режущий инструмент", "Kesuvchi asboblar"),
                "subs": [
                    ("Drill bits", "Свёрла", "Parmalar"),
                    ("Taps and dies", "Метчики и плашки", "Metchik va plashkalar"),
                    ("Milling cutters", "Фрезы", "Frezalar"),
                    ("Turning tools", "Токарные резцы", "Tokarlik keskichlari"),
                    ("Saws and saw blades", "Пилы и дисковые пилы", "Arra va arra disklari"),
                    ("Hole saws", "Коронки", "Koronkalar"),
                ],
            },
            {
                "num": "05", "code": "sec-05",
                "n": ("Hand tools", "Ручной инструмент", "Qo'l asboblari"),
                "subs": [
                    ("Wrenches", "Гаечные ключи", "Gayka kalitlari"),
                    ("Screwdrivers", "Отвёртки", "Otvyortkalar"),
                    ("Sockets", "Торцевые головки", "Torets kallaklari"),
                    ("Pliers and clamps", "Плоскогубцы и зажимы", "Ombir va qisqichlar"),
                    ("Knives, scissors and bolt cutters", "Ножи, ножницы и болторезы", "Pichoq, qaychi va bolt kesgichlar"),
                    ("Tool sets", "Наборы инструментов", "Asboblar to'plamlari"),
                ],
            },
            {
                "num": "06", "code": "sec-06",
                "n": ("Fasteners", "Крепёж", "Mahkamlagichlar"),
                "subs": [
                    ("Bolts and screws", "Болты и винты", "Bolt va vintlar"),
                    ("Nuts and washers", "Гайки и шайбы", "Gayka va shaybalar"),
                    ("Anchors and dowels", "Анкеры и дюбели", "Anker va dyubellar"),
                    ("Studs", "Шпильки", "Shpilkalar"),
                    ("Rivets", "Заклёпки", "Parchinlar"),
                    ("Adhesives and tapes", "Клей и ленты", "Yelim va lentalar"),
                ],
            },
            {
                "num": "07", "code": "sec-07",
                "n": ("Welding and cutting", "Сварка и резка", "Payvandlash va kesish"),
                "subs": [
                    ("Electrodes", "Электроды", "Elektrodlar"),
                    ("Welding wire", "Сварочная проволока", "Payvandlash simi"),
                    ("Regulators and cutters", "Редукторы и резаки", "Reduktor va kesgichlar"),
                    ("Gas welding hoses", "Шланги для газосварки", "Gaz payvandlash shlanglari"),
                    ("Welding machines", "Сварочные аппараты", "Payvandlash apparatlari"),
                    ("Soldering", "Пайка", "Kavsharlash"),
                ],
            },
            {
                "num": "08", "code": "sec-08",
                "n": ("Abrasives", "Абразивы", "Abrazivlar va jilvirlash"),
                "subs": [
                    ("Cutting discs", "Отрезные диски", "Kesish disklari"),
                    ("Grinding and cleaning discs", "Шлифовальные и зачистные диски", "Jilvirlash va tozalash disklari"),
                    ("Grinders", "Шлифовальные машины", "Jilvirlash mashinalari"),
                    ("Sandpaper", "Шлифовальная бумага", "Jilvir qog'ozlari"),
                    ("Files", "Напильники", "Egovlar"),
                    ("Sandblasters", "Пескоструйные аппараты", "Qum purkagich apparatlar"),
                ],
            },
            {
                "num": "09", "code": "sec-09",
                "n": ("Measuring tools", "Измерительный инструмент", "O'lchov asboblari"),
                "subs": [
                    ("Tapes and rulers", "Рулетки и линейки", "Ruletka va chizg'ichlar"),
                    ("Calipers", "Штангенциркули", "Shtangensirkullar"),
                    ("Micrometers", "Микрометры", "Mikrometrlar"),
                    ("Levels", "Уровни", "Sath o'lchagichlar (uroven)"),
                    ("Multimeters", "Мультиметры", "Multimetrlar"),
                ],
            },
        ],
    },
    {
        "code": "group-2",
        "n": (
            "Engineering systems maintenance",
            "Обслуживание инженерных систем и оборудования",
            "Muhandislik tizimlari va uskunalarga xizmat ko'rsatish",
        ),
        "sections": [
            {
                "num": "10", "code": "sec-10",
                "n": ("Pipes, hoses and fittings", "Трубы, рукава и фитинги", "Quvurlar, yenglar va fitinglar"),
                "subs": [
                    ("Pipes and fittings", "Трубы и фитинги", "Quvur va fitinglar"),
                    ("High-pressure hoses", "Рукава высокого давления (РВД)", "Yuqori bosimli yenglar (RVD)"),
                    ("Pressure hoses", "Напорные рукава и шланги", "Bosimli yeng va shlanglar"),
                    ("Hose clamps", "Хомуты", "Shlang xomutlari"),
                    ("Tubes", "Трубки", "Naychalar"),
                    ("Pipe cutters", "Труборезы", "Quvur kesgichlar"),
                ],
            },
            {
                "num": "11", "code": "sec-11",
                "n": ("Pumps, valves and level", "Насосы, клапаны и уровень", "Nasoslar, klapanlar va sath"),
                "subs": [
                    ("Pumps", "Насосы", "Nasoslar"),
                    ("Valves and taps", "Клапаны и краны", "Klapan va jumraklar"),
                    ("Gate valves", "Задвижки и вентили", "Zadvijka va ventillar"),
                    ("Flow meters", "Расходомеры", "Sarf o'lchagichlar"),
                    ("Level gauges", "Уровнемеры", "Suyuqlik sathi o'lchagichlari"),
                ],
            },
            {
                "num": "12", "code": "sec-12",
                "n": ("Seals and sealants", "Уплотнения и герметики", "Zichlagichlar va germetiklar"),
                "subs": [
                    ("Cuffs and rings", "Манжеты и кольца", "Manjet va halqalar"),
                    ("Gaskets", "Паронит и прокладки", "Paronit va prokladkalar"),
                    ("Gland packing", "Сальниковая набивка", "Salnik to'ldirgichi"),
                    ("Mechanical seals", "Торцевые уплотнения", "Torets zichlagichlari"),
                    ("Sealants", "Герметики", "Germetiklar"),
                ],
            },
            {
                "num": "13", "code": "sec-13",
                "n": ("Lubricants and coolants", "Смазочные материалы и СОЖ", "Moylash materiallari va sovutuvchi suyuqliklar"),
                "subs": [
                    ("Greases", "Густые смазки", "Quyuq moylar"),
                    ("Industrial oils", "Индустриальные масла", "Sanoat moylari"),
                    ("Grease guns", "Маслошприцы", "Moy shpritslari"),
                    ("Grease nipples", "Пресс-маслёнки", "Press-moydonlar"),
                    ("Coolants", "СОЖ", "Sovutuvchi-moylovchi suyuqliklar"),
                ],
            },
            {
                "num": "14", "code": "sec-14",
                "n": ("Drives, pneumatics and hydraulics", "Приводы, пневматика и гидравлика", "Yuritmalar, pnevmatika va gidravlika"),
                "subs": [
                    ("V-belts and drive belts", "Клиновые и приводные ремни", "Ponasimon va yuritma tasmalari"),
                    ("Chains and sprockets", "Цепи и звёздочки", "Zanjir va yulduzchalar"),
                    ("Gearboxes", "Редукторы", "Reduktorlar"),
                    ("Couplings", "Муфты", "Muftalar"),
                    ("Pneumatics", "Пневматика", "Pnevmatika"),
                    ("Hydraulics", "Гидравлика", "Gidravlika"),
                ],
            },
            {
                "num": "15", "code": "sec-15",
                "n": ("Filtration", "Фильтрация", "Filtrlash"),
                "subs": [
                    ("Oil and fuel filters", "Масляные и топливные фильтры", "Moy va yoqilg'i filtrlari"),
                    ("Air filters", "Воздушные фильтры", "Havo filtrlari"),
                    ("Hydraulic filters", "Гидравлические фильтры", "Gidravlik filtrlar"),
                    ("Cartridges and housings", "Картриджи и корпуса", "Filtr kartrijlari va korpuslari"),
                    ("Mesh and sieves", "Сетки и сита", "To'r va elaklar"),
                ],
            },
            {
                "num": "16", "code": "sec-16",
                "n": ("Pressure and temperature", "Давление и температура", "Bosim va harorat"),
                "subs": [
                    ("Pressure gauges", "Манометры", "Manometrlar"),
                    ("Pressure switches", "Реле давления", "Bosim relelari"),
                    ("Thermometers", "Термометры", "Termometrlar"),
                    ("Thermocouples", "Термопары и термосопротивления", "Termojuft va termoqarshiliklar"),
                    ("Heat exchangers", "Теплообменники", "Issiqlik almashtirgichlar"),
                ],
            },
            {
                "num": "17", "code": "sec-17",
                "n": ("Heating, ventilation and AC", "Отопление, вентиляция и кондиционирование", "Isitish, ventilyatsiya va konditsionerlash"),
                "subs": [
                    ("Heaters", "Обогреватели", "Isitgichlar"),
                    ("Fans", "Вентиляторы", "Ventilyatorlar"),
                    ("Dust collectors", "Пылеуловители", "Chang tutgichlar"),
                    ("Air conditioners", "Кондиционеры", "Konditsionerlar"),
                    ("Air ducts", "Воздуховоды", "Havo quvurlari"),
                ],
            },
        ],
    },
    {
        "code": "group-3",
        "n": (
            "Production and materials",
            "Производство и материалы",
            "Ishlab chiqarish va materiallar",
        ),
        "sections": [
            {
                "num": "18", "code": "sec-18",
                "n": ("Machine tooling", "Станочная оснастка", "Dastgoh moslamalari"),
                "subs": [
                    ("Vises and clamps", "Тиски и зажимы", "Iskanja va qisqichlar"),
                    ("Lathe chucks", "Токарные патроны", "Tokarlik patronlari"),
                    ("Jaws and mandrels", "Кулачки и оправки", "Sanga va opravkalar"),
                    ("Live centers", "Вращающиеся центры", "Aylanuvchi markazlar"),
                    ("Magnetic bases", "Магнитные основания", "Magnitli asoslar"),
                ],
            },
            {
                "num": "19", "code": "sec-19",
                "n": ("Raw materials", "Сырьё и материалы", "Xomashyo va materiallar"),
                "subs": [
                    ("Rolled metal", "Металлопрокат", "Metall prokat"),
                    ("Textolite and PTFE", "Текстолит и фторопласт", "Tekstolit va ftoroplast"),
                    ("Technical rubber", "Техническая резина", "Texnik rezina"),
                    ("Insulation materials", "Изоляционные материалы", "Izolyatsiya materiallari"),
                    ("Technical fabrics", "Технические ткани", "Texnik matolar"),
                ],
            },
        ],
    },
    {
        "code": "group-4",
        "n": (
            "Warehouse, lifting and logistics",
            "Склад, подъём и логистика",
            "Ombor, yuk ko'tarish va logistika",
        ),
        "sections": [
            {
                "num": "20", "code": "sec-20",
                "n": ("Warehouse equipment and conveyors", "Складская техника и конвейеры", "Ombor texnikasi va konveyerlar"),
                "subs": [
                    ("Trolleys", "Тележки", "Aravachalar"),
                    ("Pallet jacks", "Гидравлические тележки (рохля)", "Gidravlik aravachalar (roxlya)"),
                    ("Caster wheels", "Колёсные опоры", "G'ildirak tayanchlari"),
                    ("Ladders and step ladders", "Лестницы и стремянки", "Narvon va stremyankalar"),
                    ("Conveyors and rollers", "Конвейеры и ролики", "Konveyer va roliklar"),
                    ("Belt repair", "Ремонт конвейерных лент", "Konveyer lentalarini ta'mirlash"),
                ],
            },
            {
                "num": "21", "code": "sec-21",
                "n": ("Lifting equipment and rigging", "Грузоподъём и такелаж", "Yuk ko'tarish uskunalari va takelaj"),
                "subs": [
                    ("Hoists", "Тали", "Tallar"),
                    ("Winches", "Лебёдки", "Chig'irlar"),
                    ("Slings", "Стропы", "Stroplar"),
                    ("Steel ropes", "Стальные канаты", "Po'lat arqonlar"),
                    ("Load chains", "Грузовые цепи", "Yuk zanjirlari"),
                    ("Jacks", "Домкраты", "Domkratlar"),
                ],
            },
            {
                "num": "22", "code": "sec-22",
                "n": ("Mounting profiles and hangers", "Монтажные профили и подвесы", "Montaj profillari va osmalar"),
                "subs": [
                    ("Mounting profiles", "Монтажный профиль", "Montaj profili"),
                    ("Pipe hangers", "Подвесы для труб", "Quvur osmalari"),
                    ("Beam clamps", "Балочные зажимы", "To'sin qisqichlari"),
                    ("Turnbuckles", "Талрепы", "Talreplar"),
                    ("U-bolts", "U-образные болты", "U-shaklidagi boltlar"),
                ],
            },
            {
                "num": "23", "code": "sec-23",
                "n": ("Furniture, storage and containers", "Мебель, хранение и тара", "Mebel, saqlash va idishlar"),
                "subs": [
                    ("Workbenches", "Верстаки", "Verstaklar"),
                    ("Racks", "Стеллажи", "Stellajlar"),
                    ("Cabinets", "Шкафы", "Shkaflar"),
                    ("Tool boxes", "Ящики для инструментов", "Asbob qutilari"),
                    ("Drums and canisters", "Бочки и канистры", "Bochka va kanistrlar"),
                ],
            },
            {
                "num": "24", "code": "sec-24",
                "n": ("Packing and shipping", "Упаковка и отправка", "Qadoqlash va jo'natish"),
                "subs": [
                    ("Cardboard boxes", "Картонные коробки", "Karton qutilar"),
                    ("Stretch film", "Стрейч-плёнка", "Streych-plyonka"),
                    ("Packing tape", "Скотч", "Skotch"),
                    ("Strapping", "Стреппинг-лента", "Strepping lenta"),
                    ("Seals", "Пломбы", "Plombalar"),
                ],
            },
        ],
    },
    {
        "code": "group-5",
        "n": (
            "Building and office",
            "Здание и офис",
            "Bino va ofis",
        ),
        "sections": [
            {
                "num": "25", "code": "sec-25",
                "n": ("Hardware, locks and doors", "Фурнитура, замки и двери", "Furnitura, qulflar va eshiklar"),
                "subs": [
                    ("Hinges", "Петли", "Petlyalar"),
                    ("Handles", "Ручки", "Tutqichlar"),
                    ("Locks", "Замки", "Qulflar"),
                    ("Door closers", "Доводчики", "Eshik yopgichlar"),
                    ("Drawer slides", "Направляющие для ящиков", "Tortma yo'naltirgichlari"),
                ],
            },
            {
                "num": "26", "code": "sec-26",
                "n": ("Plumbing and cleaning", "Сантехника и уборка", "Santexnika va tozalash"),
                "subs": [
                    ("Faucets and showers", "Смесители и души", "Aralashtirgichlar va dushlar"),
                    ("Detergents", "Моющие средства", "Yuvish vositalari"),
                    ("Brooms and mops", "Веники и швабры", "Supurgi va shvabralar"),
                    ("Paper towels", "Бумажные полотенца", "Qog'oz sochiqlar"),
                    ("Sorbents", "Сорбенты", "Sorbentlar"),
                ],
            },
            {
                "num": "27", "code": "sec-27",
                "n": ("Building maintenance", "Обслуживание зданий", "Bino va hududga xizmat ko'rsatish"),
                "subs": [
                    ("Paints and enamels", "Краски и эмали", "Bo'yoq va emallar"),
                    ("Ladders", "Лестницы", "Narvonlar"),
                    ("Awnings", "Тенты", "Tentlar"),
                    ("Mats", "Коврики", "Gilamcha va to'shamalar"),
                    ("Garden tools", "Садовый инвентарь", "Bog' jihozlari"),
                ],
            },
            {
                "num": "28", "code": "sec-28",
                "n": ("Office and marking", "Офис и маркировка", "Ofis, lavhalar va markirovka"),
                "subs": [
                    ("Stationery", "Канцелярия", "Kanselyariya tovarlari"),
                    ("Signs", "Таблички", "Lavhalar"),
                    ("Labels", "Этикетки", "Yorliqlar"),
                    ("Stencils", "Трафареты", "Trafaretlar"),
                    ("Label printers", "Принтеры этикеток", "Yorliq printerlari"),
                ],
            },
        ],
    },
]

PARK_SUB = "sec-19-1"  # Metall prokat — parking for homeless building products.

# Old leaf code -> new subcategory code.
PRODUCT_MAP = {
    "cables": "sec-01-1",
    "sockets-switches": "sec-01-4",
    "electrodes": "sec-07-1",
    "inverters": "sec-07-5",
    "cutting-discs": "sec-08-1",
    "anchors": "sec-06-3",
    "screws": "sec-06-1",
    "pp-pipes": "sec-10-1",
    "faucets": "sec-26-1",
    "interior-paint": "sec-27-1",
    "primer": "sec-27-1",
    "radiators": "sec-17-1",
    "heated-floors": "sec-17-1",
    "step-ladders": "sec-27-2",
    "extension-ladders": "sec-27-2",
    "mineral-wool": "sec-19-4",
    "xps-boards": "sec-19-4",
    "rebar": "sec-19-1",
    "profile-pipe": "sec-19-1",
    "bitumen-mastic": "sec-12-5",
}


class Command(BaseCommand):
    help = "Replace catalog tree with the 5-group industrial tree, migrate products."

    def add_arguments(self, parser):
        parser.add_argument("--confirm", action="store_true")

    def handle(self, *args, **options):
        if not options["confirm"]:
            self.stdout.write(self.style.WARNING("Run with --confirm"))
            return

        from apps.product.models import (
            Attribute,
            AttributeValue,
            Category,
            Product,
            ProductAttributeValue,
        )

        with transaction.atomic():
            # 1. Build the new tree (groups -> sections -> subcategories).
            sub_by_code = {}
            for group in GROUPS:
                g_en, g_ru, g_uz = group["n"]
                group_cat, _ = Category.objects.get_or_create(
                    code=group["code"],
                    defaults={
                        "name": g_en, "name_en": g_en, "name_ru": g_ru, "name_uz": g_uz,
                        "parent": None, "level": 0, "is_leaf": False, "is_active": True,
                    },
                )
                for section in group["sections"]:
                    s_en, s_ru, s_uz = section["n"]
                    photo = f"seed/{section['code']}.jpg"
                    section_cat, _ = Category.objects.get_or_create(
                        code=section["code"],
                        defaults={
                            "name": s_en, "name_en": s_en, "name_ru": s_ru, "name_uz": s_uz,
                            "parent": group_cat, "level": 1, "is_leaf": False,
                            "is_active": True,
                            "image": photo if os.path.exists(os.path.join(str(MEDIA_SEED_DIR), f"{section['code']}.jpg")) else None,
                        },
                    )
                    for i, (sub_en, sub_ru, sub_uz) in enumerate(section["subs"], start=1):
                        sub_code = f"{section['code']}-{i}"
                        sub_cat, _ = Category.objects.get_or_create(
                            code=sub_code,
                            defaults={
                                "name": sub_en, "name_en": sub_en, "name_ru": sub_ru, "name_uz": sub_uz,
                                "parent": section_cat, "level": 2, "is_leaf": True,
                                "is_active": True,
                            },
                        )
                        sub_by_code[sub_code] = sub_cat

            # 2. Migrate products (+ their attributes).
            stats = {"moved": 0, "parked": 0, "attrs": 0, "values": 0}
            old_leaf_ids = set(
                Category.objects.filter(is_leaf=True)
                .exclude(code__in=set(sub_by_code))
                .values_list("id", flat=True)
            )
            for product in Product.objects.select_related("category").all():
                old_code = product.category.code if product.category else None
                if old_code in PRODUCT_MAP:
                    new_sub = sub_by_code[PRODUCT_MAP[old_code]]
                    stats["moved"] += 1
                else:
                    new_sub = sub_by_code[PARK_SUB]
                    stats["parked"] += 1

                # Recreate product attributes under the new leaf from old ones.
                key_to_new_value = {}
                for pav in ProductAttributeValue.objects.filter(
                    product=product
                ).select_related("attribute", "attribute_value"):
                    old_attr = pav.attribute
                    attr_en = old_attr.name_en or old_attr.name
                    attr, created = Attribute.objects.get_or_create(
                        category=new_sub, name_en=attr_en,
                        defaults={
                            "name": old_attr.name, "name_ru": old_attr.name_ru,
                            "name_uz": old_attr.name_uz,
                            "attribute_type": old_attr.attribute_type,
                            "is_filterable": old_attr.is_filterable,
                        },
                    )
                    if created:
                        stats["attrs"] += 1
                    old_val = pav.attribute_value
                    val_en = old_val.value_en or old_val.value
                    new_val, val_created = AttributeValue.objects.get_or_create(
                        attribute=attr, value_en=val_en,
                        defaults={
                            "value": old_val.value, "value_ru": old_val.value_ru,
                            "value_uz": old_val.value_uz,
                        },
                    )
                    if val_created:
                        stats["values"] += 1
                    ProductAttributeValue.objects.get_or_create(
                        product=pav.product, attribute=attr, attribute_value=new_val,
                    )
                    key_to_new_value[(attr_en, val_en)] = new_val
                    pav.delete()

                product.category = new_sub
                product.save(update_fields=["category"])

            # 3. Delete old categories (products already moved away) + leftovers.
            old_roots = list(
                Category.objects.filter(parent__isnull=True).exclude(
                    code__in=[g["code"] for g in GROUPS]
                ).values_list("id", flat=True)
            )
            Category.objects.filter(id__in=list(old_leaf_ids) + old_roots).delete()
            # Orphaned old attributes (their PAVs are gone or moved).
            Attribute.objects.filter(productattributevalue__isnull=True).delete()

            self.stdout.write(self.style.SUCCESS(
                f"Tree: {Category.objects.filter(level=0).count()} groups, "
                f"{Category.objects.filter(level=1).count()} sections, "
                f"{Category.objects.filter(level=2).count()} subcategories. "
                f"Products moved: {stats['moved']}, parked: {stats['parked']}, "
                f"attrs recreated: {stats['attrs']}, values: {stats['values']}."
            ))
