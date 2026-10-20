# Frontend API Docs: Katalog va buyurtma (`/api/v1/`)

Bu hujjat [snaber.uz](https://github.com/rasul-qutbiddinov/snaber.uz) frontendini statik ma'lumotdan (`lib/catalog/*.ts`) backend API ga o'tkazishni tushuntiradi.

## 1) Umumiy ma'lumot

- Base URL (local): `http://127.0.0.1:8000`
- API prefix: `/api/v1/`
- Auth: **kerak emas.** `Authorization` sarlavhasini yubormang: noto'g'ri token bilan katalog endpoint'lari `401` qaytaradi.
- Format: JSON, UTF-8. Hamma manzil `/` bilan tugaydi (`/api/v1/catalog/tree/`).
- Swagger: `/api/docs/`, ReDoc: `/api/redoc/`, sxema: `/api/schema/`.

Asosiy qoida: **filtr, tartib, facet'lar, variantlar va o'xshash mahsulotlar endi serverda hisoblanadi** va `lib/catalog/engine.ts` bilan aynan bir xil natija beradi (185 kategoriya va 199 mahsulot bo'yicha solishtirilgan). Frontendda faqat ko'rsatish qoladi: havolalar, chiplar, jadval ustunlarini yashirish, matnlar.

Narxlar — butun son, **so'm, bitta qadoq uchun** (`price`), qadoqdagi dona — `pack`. Mahsulot rasmlari hozircha yo'q: kartochkada kategoriya ikonkasi (`category.icon`) ko'rsatiladi, xuddi hozirgidek.

### `engine.ts` → API

| Hozir frontendda | API |
|---|---|
| `ROOT` (header, MegaMenu, footer, `CatalogHome`) | `GET catalog/tree/` |
| `ATTRIBUTES`, `ATTRIBUTE_LABEL` | `GET catalog/attributes/` |
| `locate(path)`, `breadcrumbs`, `isLeaf` | `GET catalog/categories/{path}/` |
| `productsIn(...)` | `GET catalog/products/` |
| `facets`, `cards`, `countIn`, leaf → mahsulotga redirect | `GET catalog/facets/` |
| `findProduct`, `variantsOf`, `ATTRIBUTES` bo'yicha specs | `GET catalog/products/{sku}/` |
| `related(product)` | `GET catalog/products/{sku}/related/` |
| `featured()` | `GET catalog/products/featured/` |
| Savatdagi «Оформить заказ» | `POST orders/` |

`hrefFor`, `chips`, `activeCount`, `parseQuery` frontendda qoladi: ular sayt manzili bilan ishlaydi. Faqat API ga so'rov yuborishda xususiyat parametrlari nomiga `attr_` qo'shiladi (3-bo'lim).

## 2) TypeScript turlari

```ts
export type Stock = 'in-stock' | 'low' | 'on-order';

export interface CategoryRef {
  slug: string;
  name: string;
  icon: IconKey; // lib/catalog/types.ts dagi bilan bir xil qiymatlar
}

export interface TableConfig {
  group_by: string | null; // xususiyat kaliti
  columns: string[];       // xususiyat kalitlari, ko'rsatish tartibida
}

export interface CategoryTreeNode extends CategoryRef {
  description: string;
  product_count: number; // shoxdagi barcha faol mahsulotlar
  table: TableConfig | null;
  children: CategoryTreeNode[];
}

export interface Attribute {
  key: string;
  label: string;
  requires: { key: string; value: string } | null;
}

export interface CategoryCard extends CategoryRef {
  description: string;
  product_count: number;
}

export interface CategoryDetail extends CategoryRef {
  description: string;
  path: string[];          // ["consumables", "fasteners", "bolts-screws"]
  trail: CategoryRef[];    // breadcrumb, yuqoridan pastga
  is_leaf: boolean;
  product_count: number;
  table: TableConfig | null;
  children: CategoryCard[];
  first_sku: string | null; // faqat oxirgi darajada
}

export interface Product {
  sku: string;
  name: string;
  path: string[];
  price: number;
  pack: number;
  stock: Stock;
  category: CategoryRef;   // oxirgi darajadagi kategoriya
  attrs: Record<string, string>;
}

export interface Page<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface FacetOption {
  value: string;
  count: number;
  selected: boolean;
}

export interface Facet {
  key: string;
  label: string;
  options: FacetOption[];
}

export interface Facets {
  total: number;
  facets: Facet[];
  children: (CategoryRef & { description: string; count: number })[];
  first_sku: string | null;
}

export interface VariantGroup {
  key: string;
  label: string;
  value: string; // ochiq mahsulotning qiymati
  options: { value: string; sku: string; selected: boolean }[];
}

export interface ProductDetail extends Product {
  trail: CategoryRef[];
  specs: { key: string; label: string; value: string }[];
  table: TableConfig | null;
  variants: VariantGroup[];
  variant_count: number;
}
```

`Product` frontenddagi hozirgi `Product` turi bilan mos: `sku, name, path, price, pack, stock, attrs` o'zgarmagan, faqat `category` qo'shilgan. `ProductCard`, `ProductTable`, `BuyBox`, savat shu turni o'zgarishsiz qabul qiladi.

## 3) Filtr parametrlari

`GET catalog/products/` va `GET catalog/facets/` bir xil parametrlarni oladi:

| Parametr | Misol | Izoh |
|---|---|---|
| `category` | `consumables/fasteners/bolts-screws` | Kategoriya yo'li (slug'lar `/` bilan). Bo'sh — butun katalog. Noto'g'ri yo'l — `404` |
| `q` | `винт m6` | Nomi yoki artikuli bo'yicha qidiruv. Har bir so'z bo'lishi kerak; katta-kichik harf farqi yo'q (kirill ham) |
| `attr_{key}` | `attr_thread=M6&attr_thread=M8` | Xususiyat filtri, takrorlash mumkin. Bitta xususiyat ichida **YOKI**, xususiyatlar orasida **VA**. Qiymat aynan mos kelishi kerak |

Saytdagi manzil `?thread=M6&q=...` ko'rinishida qolaveradi. API ga yuborishda kalitga `attr_` qo'shing — frontendda `category` kalitli xususiyat bor va u `category` parametri bilan to'qnashadi:

```ts
const toApiParams = (path: string[], { selection, q }: Query) => {
  const params = new URLSearchParams();
  if (path.length) params.set('category', path.join('/'));
  for (const [key, values] of Object.entries(selection)) {
    for (const value of values) params.append(`attr_${key}`, value);
  }
  if (q) params.set('q', q);
  return params;
};
```

Noma'lum `attr_` kalitlari e'tiborsiz qoldiriladi. `parseQuery` uchun kalitlar ro'yxatini `GET catalog/attributes/` dan oling.

## 4) Endpoint: Kategoriyalar daraxti

### GET `/api/v1/catalog/tree/`

Header, MegaMenu, footer va bosh sahifadagi «Каталог» uchun. Daraxt 3 darajali: bo'lim → guruh → oxirgi kategoriya.

### Success response: `200 OK`

```json
[
  {
    "slug": "consumables",
    "name": "Ходовые расходники и инструмент",
    "icon": "fasteners",
    "description": "",
    "product_count": 5253,
    "table": null,
    "children": [
      {
        "slug": "electrical",
        "name": "Электротехника и освещение",
        "icon": "electrical",
        "description": "",
        "product_count": 1000,
        "table": null,
        "children": [
          {
            "slug": "wire-cable",
            "name": "Провод и кабель",
            "icon": "cable",
            "description": "",
            "product_count": 158,
            "table": { "group_by": "section", "columns": ["cores", "insulation", "voltage", "spool"] },
            "children": []
          }
        ]
      }
    ]
  }
]
```

- Tartib admin paneldagi «Tartib» bo'yicha, frontenddagi bilan bir xil.
- Yuqori darajadagi `description` bo'sh: «12 разделов» matnini `children.length` dan hisoblang (hozir `data.ts` shunday qiladi).
- Javob ~32 KB va kamdan-kam o'zgaradi: Next.js da `revalidate: 300` bilan keshlang.

## 5) Endpoint: Xususiyatlar

### GET `/api/v1/catalog/attributes/`

Filtrlar va jadval ustunlari nomlari (`ATTRIBUTE_LABEL` o'rniga). Tartib — filtrlar panelidagi tartib.

```json
[
  { "key": "thread", "label": "Размер резьбы", "requires": null },
  { "key": "pitch", "label": "Шаг резьбы", "requires": { "key": "system", "value": "Метрическая" } }
]
```

`requires` — filtr faqat shu qiymat tanlanganda chiqadi. Buni o'zingiz tekshirishingiz shart emas: `facets/` shartni hisobga olib qaytaradi. Keshlash: `revalidate: 300`.

## 6) Endpoint: Kategoriya

### GET `/api/v1/catalog/categories/{path}/`

`{path}` — slug'lar `/` bilan: `/api/v1/catalog/categories/consumables/fasteners/bolts-screws/`.

### Success response: `200 OK`

```json
{
  "slug": "bolts-screws",
  "name": "Болты и винты",
  "icon": "screws",
  "description": "",
  "path": ["consumables", "fasteners", "bolts-screws"],
  "trail": [
    { "slug": "consumables", "name": "Ходовые расходники и инструмент", "icon": "fasteners" },
    { "slug": "fasteners", "name": "Крепёж", "icon": "screws" },
    { "slug": "bolts-screws", "name": "Болты и винты", "icon": "screws" }
  ],
  "is_leaf": true,
  "product_count": 1767,
  "table": {
    "group_by": "thread",
    "columns": ["head", "finish", "threading", "profile", "drive", "strength", "material"]
  },
  "children": [],
  "first_sku": "SHB-04002"
}
```

| Maydon | Izoh |
|---|---|
| `trail` | Breadcrumb: `/catalog/` + `trail[0..i].slug` |
| `is_leaf` | `true` — oxirgi daraja, mahsulotlar shu yerda |
| `children` | Ichki kategoriyalar, filtrsiz sonlari bilan. Filtrlangan kartochkalar uchun `facets/` dagi `children` ni ishlating |
| `first_sku` | Faqat oxirgi darajada: filtrsiz ochiladigan mahsulot (buyurtma asosida bo'lmagan birinchisi). Aks holda `null` |
| `table` | Oxirgi darajadagi jadval ko'rinishi; `ProductTable` ning `config` i |

`generateMetadata` uchun `name` ni shu yerdan oling.

### Error response: `404 Not Found`

```json
{ "detail": "Not found." }
```

Yo'l topilmadi → `notFound()`.

## 7) Endpoint: Mahsulotlar ro'yxati

### GET `/api/v1/catalog/products/`

Parametrlar — 3-bo'lim, qo'shimcha: `page` (1 dan), `page_size` (standart 100, ko'pi bilan 500).

Tartib:

- oxirgi darajadagi kategoriyada — jadval tartibi: `table.group_by` qiymati, keyin uzunlik, keyin nomi (`#4-40 < #10-24 < 1/4-20 < M3 < M10`) — `productsIn(path, query, groupBy)` bilan bir xil, guruh sarlavhalarini ketma-ket qatorlardan chizsangiz bo'ladi;
- boshqa hollarda (qidiruv natijasi) — katalog tartibi.

### Success response: `200 OK`

```json
{
  "count": 136,
  "next": "http://127.0.0.1:8000/api/v1/catalog/products/?attr_system=%D0%9C...&page=2&page_size=2",
  "previous": null,
  "results": [
    {
      "sku": "HHS-04295",
      "name": "Болт с шестигранной головкой M6 x 10 мм, нержавеющая сталь 18-8",
      "path": ["consumables", "fasteners", "bolts-screws"],
      "price": 58300,
      "pack": 50,
      "stock": "in-stock",
      "category": { "slug": "bolts-screws", "name": "Болты и винты", "icon": "screws" },
      "attrs": {
        "system": "Метрическая",
        "thread": "M6",
        "pitch": "1 мм",
        "length": "10 мм",
        "material": "Нержавеющая сталь 18-8",
        "finish": "Без покрытия",
        "strength": "A2-70",
        "head": "Шестигранная",
        "drive": "Наружный шестигранник",
        "threading": "Полная резьба"
      }
    }
  ]
}
```

- `ProductTable` hozir ko'pi bilan 300 qator ko'rsatadi: `page_size=300` so'rang, «Показаны первые 300 из N» uchun `count` ni oling.
- Qidiruv natijasida «Категория» ustuni uchun `category.name` (`leafName` o'rniga).
- `next`/`previous` — to'liq URL; ularni o'zgartirmasdan so'rash mumkin.

### Error response: `404 Not Found`

```json
{ "detail": "Kategoriya topilmadi" }
```

## 8) Endpoint: Filtrlar paneli va kartochkalar

### GET `/api/v1/catalog/facets/`

Parametrlar — 3-bo'lim. Katalog sahifasi uchun bitta so'rov: filtrlar, mahsulotlar soni, ichki kategoriya kartochkalari va oxirgi darajadagi redirect.

### Success response: `200 OK`

```json
{
  "total": 136,
  "facets": [
    {
      "key": "system",
      "label": "Система мер",
      "options": [{ "value": "Метрическая", "count": 136, "selected": true }]
    },
    {
      "key": "thread",
      "label": "Размер резьбы",
      "options": [
        { "value": "M3", "count": 80, "selected": false },
        { "value": "M4", "count": 96, "selected": false },
        { "value": "M5", "count": 129, "selected": false }
      ]
    }
  ],
  "children": [],
  "first_sku": "HHS-04295"
}
```

| Maydon | Izoh |
|---|---|
| `total` | Filtrlarga mos mahsulotlar soni («N товаров») |
| `facets` | Filtrlar paneli, chiqish tartibida. Xususiyat faqat mahsulotlarni hali ajratib tursa chiqadi; har bir xususiyatning sonlari **boshqa** filtrlardan o'tgan mahsulotlar bo'yicha. Tanlangan, lekin mahsuloti qolmagan qiymat `count: 0` bilan qoladi — uni olib tashlash mumkin bo'lsin |
| `facets[].options` | Qiymatlar tartiblangan (`#4-40 < #10-24 < 1/4-20`, keyin metrik). Havola = `hrefFor(segments, toggled(query, key, value))` |
| `children` | Filtrlarga mos ichki kategoriyalar, `count > 0` lari — `CategoryCards` uchun |
| `first_sku` | Faqat oxirgi darajada va `total > 0` da: filtrlarga mos ochiladigan mahsulot. Aks holda `null` |

Katalog sahifasi (`app/catalog/[[...path]]/page.tsx`) shunday bo'ladi:

```ts
const facets = await api<Facets>(`catalog/facets/?${toApiParams(path, query)}`);

if (category.is_leaf && facets.first_sku) redirect(productHref(facets.first_sku));

const asTable = category.is_leaf || query.q !== '';
const rows = asTable
  ? (await api<Page<Product>>(`catalog/products/?${toApiParams(path, query)}&page_size=300`)).results
  : [];
// kartochkalar: facets.children; filtrlar: facets.facets; soni: facets.total
```

Root sahifada (`path = []`) va filtrsiz `category` parametrini yubormang — `total` butun katalog bo'ladi.

## 9) Endpoint: Mahsulot sahifasi

### GET `/api/v1/catalog/products/{sku}/`

### Success response: `200 OK`

```json
{
  "sku": "SHA-03301",
  "name": "Винт с внутренним шестигранником #6-32 x 1\", нержавеющая сталь 18-8",
  "path": ["consumables", "fasteners", "bolts-screws"],
  "price": 61700,
  "pack": 50,
  "stock": "in-stock",
  "category": { "slug": "bolts-screws", "name": "Болты и винты", "icon": "screws" },
  "attrs": { "system": "Дюймовая", "thread": "#6-32", "length": "1\"", "drive": "Torx" },
  "trail": [
    { "slug": "consumables", "name": "Ходовые расходники и инструмент", "icon": "fasteners" },
    { "slug": "fasteners", "name": "Крепёж", "icon": "screws" },
    { "slug": "bolts-screws", "name": "Болты и винты", "icon": "screws" }
  ],
  "specs": [
    { "key": "system", "label": "Система мер", "value": "Дюймовая" },
    { "key": "thread", "label": "Размер резьбы", "value": "#6-32" },
    { "key": "length", "label": "Длина", "value": "1\"" }
  ],
  "table": { "group_by": "thread", "columns": ["head", "finish", "threading", "profile", "drive", "strength", "material"] },
  "variants": [
    {
      "key": "thread",
      "label": "Размер резьбы",
      "value": "#6-32",
      "options": [
        { "value": "#4-40", "sku": "SHA-03247", "selected": false },
        { "value": "#6-32", "sku": "SHA-03301", "selected": true },
        { "value": "#8-32", "sku": "SHA-03343", "selected": false }
      ]
    }
  ],
  "variant_count": 1767
}
```

(`attrs`, `specs`, `variants` qisqartirilgan.)

| Maydon | Izoh |
|---|---|
| `specs` | «Все характеристики» jadvali, xususiyatlar tartibida (`ATTRIBUTES.filter(...)` o'rniga) |
| `variants` | `VariantChips` uchun (`variantsOf` o'rniga). Chip havolasi — `productHref(option.sku)`. Bog'liq xususiyat (`pitch`) alohida qator bo'lmaydi, ko'pi bilan 10 qator |
| `variant_count` | Shu kategoriyadagi mahsulotlar soni: `> 1` bo'lsa «Все варианты (N)» |
| `table` | «Все варианты» jadvali ko'rinishi; qatorlarini `GET catalog/products/?category={path.join('/')}&page_size=300` dan oling |

Kalit xususiyatlar ro'yxati (`keySpecs`) — `specs` dan `variants` dagi kalitlarni chiqarib tashlang, xuddi hozirgidek.

### Error response: `404 Not Found`

Mahsulot yo'q yoki admin panelda nofaol qilingan → `notFound()`.

## 10) Endpoint: O'xshash mahsulotlar va «Хиты продаж»

### GET `/api/v1/catalog/products/{sku}/related/?limit=8`

Shu kategoriyadan, buyurtma asosida bo'lmaganlar; umumiy xususiyatlari ko'pi oldin, teng bo'lsa arzoni. `limit` — standart 8, ko'pi bilan 50. Javob — `Product[]` (sahifalanmagan). Mahsulot yo'q bo'lsa `404`.

### GET `/api/v1/catalog/products/featured/?limit=10`

Admin panelda «Ommabop» belgilangan faol mahsulotlar. `limit` — standart 10, ko'pi bilan 50. Javob — `Product[]`, bo'sh massiv ham bo'lishi mumkin.

## 11) Endpoint: Buyurtma

### POST `/api/v1/orders/`

`Content-Type: application/json`. Savatdagi «Оформить заказ» tugmasi uchun. To'lov yo'q: menejer qo'ng'iroq qilib tasdiqlaydi.

| Maydon | Tur | Majburiy | Izoh |
|---|---|---|---|
| `name` | string | ha | 2–100 belgi; ortiqcha bo'shliqlar olib tashlanadi |
| `phone` | string | ha | O'zbekiston raqami: `+998 90 123-45-67` yoki `90 123 45 67` (9 raqam) |
| `comment` | string | yo'q | 1000 belgigacha |
| `items` | array | ha | 1–100 qator |
| `items[].sku` | string | ha | Faol mahsulot artikuli |
| `items[].qty` | int | ha | Qadoqlar soni, 1–10000 (`CartItem.qty` bilan bir xil) |

```json
{
  "name": "Алишер Каримов",
  "phone": "90 123-45-67",
  "comment": "Позвоните после обеда",
  "items": [
    { "sku": "SHA-03301", "qty": 2 },
    { "sku": "CON-00001", "qty": 1 }
  ]
}
```

`price`, `name`, `pack` yuborish shart emas — yuborilsa ham e'tiborsiz qoldiriladi. Bir artikul ikki qatorda kelsa, bitta qatorga qo'shiladi.

### Success response: `201 Created`

```json
{
  "number": 2,
  "status": "new",
  "total": 241200,
  "created_at": "2026-10-20T10:18:13.661286+05:00",
  "items": [
    {
      "sku": "SHA-03301",
      "name": "Винт с внутренним шестигранником #6-32 x 1\", нержавеющая сталь 18-8",
      "price": 61700,
      "pack": 50,
      "qty": 2,
      "amount": 123400
    },
    {
      "sku": "CON-00001",
      "name": "Контактор 9 А, 24 В, 3",
      "price": 117800,
      "pack": 1,
      "qty": 1,
      "amount": 117800
    }
  ]
}
```

- **Narx har doim bazadan olinadi.** Savatdagi narx eskirgan bo'lishi mumkin: tasdiq sahifasida javobdagi `total` va `items[].price` ni ko'rsating, savatdagini emas.
- `number` — mijozga aytiladigan buyurtma raqami («Заказ № 2»).
- Muvaffaqiyatli javobdan keyin `clearCart()`.

### Error response: `400 Bad Request`

Xato maydon bo'yicha qaytadi. `items` dagi xatolar qatorlar tartibida: xatosiz qator — `{}`.

```json
{
  "name": ["Ismingizni yozing"],
  "phone": ["Telefon raqamini +998 90 123-45-67 ko'rinishida yozing"],
  "items": [
    { "qty": ["Ensure this value is greater than or equal to 1."] },
    {}
  ]
}
```

Mahsulot topilmasa yoki sotuvdan olingan bo'lsa (savatda eski mahsulot qolgan):

```json
{ "items": [{}, { "sku": ["Mahsulot topilmadi yoki sotuvda yo'q"] }] }
```

Bo'sh savat:

```json
{ "items": { "non_field_errors": ["This list may not be empty."] } }
```

- `items` ikki ko'rinishda keladi: massiv — qatorlar xatosi; obyekt (`non_field_errors`) — butun ro'yxat xatosi.
- `sku` xatolari faqat barcha qatorlarning `qty` lari to'g'ri bo'lgandan keyin tekshiriladi.
- Server matnlari o'zbekcha yoki inglizcha: sayt ruscha, shuning uchun foydalanuvchiga xatoni **maydon nomi bo'yicha o'z matningiz bilan** ko'rsating, server matnini emas.

### Error response: `429 Too Many Requests`

```json
{ "detail": "Request was throttled. Expected available in 3540 seconds." }
```

Bitta manzildan soatiga 10 tadan ko'p buyurtma qabul qilinmaydi (serverda `ORDERS_THROTTLE_RATE`). Xato to'ldirilgan forma sanalmaydi. `Retry-After` sarlavhasida kutish soniyalari bor. Matn: «Слишком много заказов, попробуйте позже или позвоните нам».

## 12) Next.js dan ulash

```ts
// lib/api.ts
import { notFound } from 'next/navigation';

const API_URL = process.env.API_URL ?? 'http://127.0.0.1:8000';

export async function api<T>(path: string, init?: RequestInit & { revalidate?: number }): Promise<T> {
  const response = await fetch(`${API_URL}/api/v1/${path}`, {
    ...init,
    next: { revalidate: init?.revalidate ?? 0 },
  });
  if (response.status === 404) notFound();
  if (!response.ok) throw new Error(`API ${response.status}: ${path}`);
  return response.json() as Promise<T>;
}
```

- Katalog va mahsulot sahifalari server komponentlarda so'raladi: CORS kerak emas, `API_URL` serverdagi ichki manzil bo'lishi mumkin (`http://127.0.0.1:8020`).
- Keshlash: `tree/` va `attributes/` — `revalidate: 300`; `products/`, `facets/`, mahsulot sahifasi — `revalidate: 0` yoki qisqa (narx va holat admin panelda o'zgaradi).
- Buyurtma brauzerdan yuborilsa, sayt manzili backend `.env` dagi `CORS_ALLOWED_ORIGINS` da bo'lishi kerak (local: `http://localhost:3000` allaqachon bor).
- Buyurtma Next.js route handler / server action orqali yuborilsa, mijoz manzilini `X-Forwarded-For` da uzating va backendda `NUM_PROXIES` ni shunga moslang — aks holda limit hamma mijozlarni bitta deb sanaydi.

`stock` qiymatlari o'zgarmagan: `STOCK` (`lib/catalog/format.ts`) — `in-stock` «В наличии», `low` «Мало», `on-order` «Под заказ».

## 13) Tez-tez beriladigan savollar

- **Kategoriya `slug` i yagonami?** Faqat bir darajada. Doim to'liq yo'l (`path`) bilan ishlang.
- **Filtr qiymatlarini qanday yozaman?** API qaytargandek, o'zgartirmasdan: `facets[].options[].value` ni URL ga qo'ying.
- **Yangi xususiyat qo'shilsa?** `attributes/` va `facets/` o'zi qaytaradi; frontendda kod o'zgarmaydi.
- **Ma'lumot qayerdan?** Hozircha frontenddagi statik katalogdan import qilingan, keyin admin panelda yuritiladi. `lib/catalog/data.ts` va `real.ts` ni API ga o'tgach o'chirsa bo'ladi.
