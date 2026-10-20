# Snaber backend

[snaber.uz](https://github.com/rasul-qutbiddinov/snaber.uz) frontendi uchun Django 5.2 + DRF backend: sanoat mollari katalogi (McMaster uslubidagi filtrlar), mahsulot sahifasi va savatdan buyurtma.

- `apps/catalog` — xususiyatlar, kategoriyalar daraxti, mahsulotlar, katalog API va import.
- `apps/orders` — buyurtmalar va ularning holatlari.
- Admin panel: `/admin/`, API hujjati: `/api/docs/` (Swagger), `/api/redoc/`.

Filtrlash, tartib, facet'lar va variantlar frontenddagi `lib/catalog/engine.ts` bilan aynan bir xil ishlaydi: 185 kategoriya va 199 mahsulot bo'yicha natijalar solishtirib tekshirilgan.

## Ishga tushirish

Python 3.10+ kerak. Ma'lumotni frontenddan qayta eksport qilish uchun Node.js 20+.

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
cp .env.example .env            # SECRET_KEY ni to'ldiring
.venv/Scripts/python manage.py migrate
.venv/Scripts/python manage.py import_catalog
.venv/Scripts/python manage.py createsuperuser
.venv/Scripts/python manage.py runserver 8000
```

Linux/macOS da `.venv/Scripts/` o'rniga `.venv/bin/`.

Standart baza — `db.sqlite3`. SQLite kirill harflarida `LIKE` ni katta-kichik harfga sezgir qiladi; shuning uchun qidiruv uchun nom va artikul kichik harflarda alohida saqlanadi (`Product.search_text`), u ikkala bazada bir xil ishlaydi.

## Katalog ma'lumoti

Hozirgi katalog frontenddagi statik ma'lumotdan olingan: 80 xususiyat, 185 kategoriya, 7939 mahsulot. U `apps/catalog/fixtures/catalog.json` da saqlanadi.

Frontendda ma'lumot o'zgarsa:

```bash
npx --yes tsx@4.19.2 tools/export_catalog.mts <frontend papkasi> apps/catalog/fixtures/catalog.json
.venv/Scripts/python manage.py import_catalog
```

`import_catalog`:

- avval butun faylni tekshiradi: noma'lum xususiyat, oxirgi darajada bo'lmagan kategoriyadagi mahsulot, noma'lum ikonka yoki takroriy artikul bo'lsa, hech narsa yozilmaydi va xatolar ko'rsatiladi;
- yozuvlarni xususiyat kaliti, kategoriya yo'li va artikul bo'yicha topadi, faqat o'zgarganini yozadi (o'zgarishsiz qayta import ~13 soniya);
- mahsulot nomi, narxi, qadog'i, holati va «Ommabop» belgisini fayldagi qiymat bilan almashtiradi — admin panelda qilingan shu o'zgarishlar ustidan yoziladi;
- `--dry-run` — faqat tekshiradi va sanaydi; `--deactivate-missing` — faylda yo'q mahsulotlarni nofaol qiladi.

## Admin panel

- **Xususiyatlar**: kalit (API da `attr_{kalit}`), nomi, filtrlar panelidagi tartibi. Shart qo'yilsa (masalan «Шаг резьбы» faqat «Метрическая» tanlanganda), filtr shundagina chiqadi va mahsulot kartochkasida alohida chip qatori bo'lmaydi.
- **Kategoriyalar** daraxt ko'rinishida, har qatorda shoxdagi mahsulotlar soni va «+ ichki kategoriya». Slug bir darajada takrorlanmaydi (sayt manzili `/catalog/a/b/c`). Oxirgi darajadagi kategoriyada jadvalni guruhlash xususiyati va ustunlar tartibi beriladi. Mahsuloti bor kategoriyaga ichki kategoriya qo'shib bo'lmaydi.
- **Mahsulotlar**: artikul (sayt manzili `/product/{artikul}`), narx (bitta qadoq, so'm), qadoqdagi dona, holati (`in-stock`, `low`, `on-order`), xususiyat qiymatlari pastda. Faqat oxirgi darajadagi kategoriyaga biriktiriladi. Bir xil qiymat bir xil yozilishi kerak: `M10` va `М10` (kirill M) ikki xil filtr bo'ladi.
- **Buyurtmalar** faqat saytdan keladi. Holat: Yangi → Tasdiqlangan → Bajarilgan, yoki Bekor qilingan; boshqa o'tishlarga ruxsat yo'q. Qidiruv raqam, ism yoki telefonning bir qismi bo'yicha («90 123 45»).

## API

Hammasi `/api/v1/` ostida, autentifikatsiyasiz.

| Manzil | Vazifasi |
| --- | --- |
| `GET catalog/tree/` | Kategoriyalar daraxti: ikonka, tavsif, jadval ko'rinishi, mahsulotlar soni |
| `GET catalog/attributes/` | Xususiyatlar nomi va filtr chiqish sharti (`requires`) |
| `GET catalog/categories/{yo'l}/` | Kategoriya: `trail`, ichki kategoriyalar, `table`; oxirgi darajada `first_sku` — ochiladigan mahsulot |
| `GET catalog/products/` | Filtrlangan ro'yxat, sahifalab (`page`, `page_size` ≤ 500) |
| `GET catalog/facets/` | Filtrlar paneli, `total`, ichki kategoriya kartochkalari (`children`), filtrlarga mos `first_sku` |
| `GET catalog/products/{artikul}/` | Mahsulot: `specs`, variant chiplari (`variants`), kategoriya jadvali |
| `GET catalog/products/{artikul}/related/` | O'xshash mahsulotlar (`limit` ≤ 50) |
| `GET catalog/products/featured/` | «Хиты продаж» — admin panelda «Ommabop» belgilanganlar |
| `POST orders/` | Buyurtma |

`products/` va `facets/` parametrlari:

- `category=consumables/fasteners/bolts-screws` — kategoriya yo'li, bo'sh bo'lsa butun katalog;
- `q=винт m6` — nomi va artikuli bo'yicha, har bir so'z bo'lishi kerak;
- `attr_{kalit}=qiymat` — takrorlash mumkin: bitta xususiyat ichida YOKI, xususiyatlar orasida VA. Prefiks kerak, chunki frontendda `category` kalitli xususiyat bor.

Mahsulot ro'yxati frontenddagi `Product` turi bilan bir xil: `sku, name, path, price, pack, stock, attrs` + `category` (`slug, name, icon`). Oxirgi darajadagi kategoriyada tartib jadvaldagidek: guruhlash xususiyati, uzunlik, nomi (`#4-40 < #10-24 < 1/4-20 < M3 < M10`).

Buyurtma:

```json
POST /api/v1/orders/
{"name": "Алишер", "phone": "90 123-45-67", "comment": "", "items": [{"sku": "SHA-03301", "qty": 2}]}
```

- `qty` — qadoqlar soni. Narx har doim bazadan olinadi; javobdagi `total` va `items` (`sku, name, price, pack, qty, amount`) — buyurtma haqiqatda qabul qilingan narxlar, saytda shuni ko'rsating.
- Nomi, artikuli, narxi, qadog'i qatorga ko'chiriladi: keyin katalog o'zgarsa ham buyurtma o'zgarmaydi.
- Telefon `+998901234567` ko'rinishiga keltiriladi; 9 raqam ham qabul qilinadi.
- Noma'lum yoki nofaol mahsulot xatosi o'sha qatorga beriladi: `{"items": [{}, {"sku": ["..."]}]}`.
- Bitta manzildan `ORDERS_THROTTLE_RATE` tadan ko'p buyurtma qabul qilinmaydi (429). Xato to'ldirilgan forma sanalmaydi.

## Testlar

```bash
.venv/Scripts/python -m pytest
.venv/Scripts/python manage.py check
```

Testlar `apps/*/tests/` da; umumiy kichik katalog — `apps/catalog/tests/fixtures/`.

## Serverga qo'yish

`.env` da:

| O'zgaruvchi | Qiymati |
| --- | --- |
| `DEBUG` | `False` |
| `SECRET_KEY` | uzun tasodifiy qator: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `ALLOWED_HOSTS` | `snaber.uz,www.snaber.uz` (`*` qoldirmang) |
| `CSRF_TRUSTED_ORIGINS` | `https://snaber.uz,https://www.snaber.uz` — busiz admin panelga kirib bo'lmaydi |
| `DB_ENGINE`, `DB_*` | `postgresql` va PostgreSQL ulanishi |
| `CORS_ALLOWED_ORIGINS` | brauzerdan API ga murojaat qiladigan sayt manzili |
| `NUM_PROXIES` | backend oldidagi proksilar soni. Brauzer nginx orqali to'g'ridan-to'g'ri murojaat qilsa — `1`; buyurtmani Next.js serveri uzatsa va `X-Forwarded-For` ga mijoz manzilini qo'shsa — `2`. Bo'sh qolsa `X-Forwarded-For` ni soxtalashtirib buyurtma limitini chetlab o'tish mumkin |
| `CACHE_BACKEND` | `db` — buyurtma limiti gunicorn workerlari orasida umumiy bo'ladi (`locmem` da har worker alohida sanaydi) |
| `SECURE_HSTS_SECONDS` | HTTPS barqaror ishlagach `31536000` |
| `SENTRY_DSN` | ixtiyoriy |

Docker bilan:

```bash
docker compose up -d --build
docker compose exec web python manage.py import_catalog
docker compose exec web python manage.py createsuperuser
```

Konteyner ishga tushganda `migrate`, `createcachetable`, `collectstatic` bajariladi va gunicorn `127.0.0.1:8020` da tinglaydi. Dockerda SQLite ishlatmang: konteyner qayta qurilganda `db.sqlite3` yo'qoladi.

nginx (TLS shu yerda; HTTP→HTTPS redirect ham nginx da, `SECURE_SSL_REDIRECT=False` qoladi — aks holda Next.js ning ichki `http://127.0.0.1:8020` so'rovlari ham redirect bo'ladi):

```nginx
location /static/ { alias /srv/snaber/backend/static/; }
location /media/  { alias /srv/snaber/backend/media/; }
location ~ ^/(api|admin)/ {
    proxy_pass http://127.0.0.1:8020;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## Hali yo'q

- Frontend hali statik ma'lumotda ishlaydi: `lib/catalog/engine.ts` ni shu API ga almashtirish kerak.
- Kirish, sevimlilar, solishtirish, sharhlar — frontendda hozircha faqat tugma.
- Mahsulot rasmlari: frontend kategoriya ikonkasini ko'rsatadi.
- Yangi buyurtma haqida menejerga xabar (masalan Telegram) yo'q: buyurtmalar admin panelda ko'rinadi.
