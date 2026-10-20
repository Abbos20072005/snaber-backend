/**
 * Frontend dagi statik katalogni (lib/catalog) JSON ga chiqaradi;
 * backend uni `manage.py import_catalog` bilan bazaga yuklaydi.
 *
 *   npx --yes tsx@4.19.2 tools/export_catalog.mts <frontend papkasi> <natija.json>
 */
import { writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

interface AttributeDef {
  key: string;
  label: string;
  requires?: { key: string; value: string };
}

interface CategoryNode {
  slug: string;
  name: string;
  icon: string;
  description?: string;
  children?: CategoryNode[];
  table?: { groupBy?: string; columns: string[] };
}

interface Product {
  sku: string;
  name: string;
  path: string[];
  price: number;
  pack: number;
  stock: string;
  attrs: Record<string, string>;
}

const [frontendDir, outFile] = process.argv.slice(2);
if (!frontendDir || !outFile) {
  console.error('Foydalanish: tsx tools/export_catalog.mts <frontend papkasi> <natija.json>');
  process.exit(1);
}

const load = (file: string) => import(pathToFileURL(resolve(frontendDir, file)).href);

const data = await load('lib/catalog/data.ts');
const engine = await load('lib/catalog/engine.ts');

const ATTRIBUTES: AttributeDef[] = data.ATTRIBUTES;
const ROOT: CategoryNode = data.ROOT;
const PRODUCTS: Product[] = data.PRODUCTS;

const categories: object[] = [];
const walk = (node: CategoryNode, path: string[]) => {
  (node.children ?? []).forEach((child, order) => {
    const childPath = [...path, child.slug];
    categories.push({
      path: childPath,
      name: child.name,
      icon: child.icon,
      // Yuqori darajadagi tavsif ("12 разделов") frontendda hisoblanadi, saqlanmaydi.
      description: path.length === 0 ? '' : (child.description ?? ''),
      order,
      table: child.table ? { group_by: child.table.groupBy ?? null, columns: child.table.columns } : null
    });
    walk(child, childPath);
  });
};
walk(ROOT, []);

const result = {
  attributes: ATTRIBUTES.map((attribute, order) => ({
    key: attribute.key,
    label: attribute.label,
    order,
    requires: attribute.requires ?? null
  })),
  categories,
  products: PRODUCTS.map((product) => ({
    sku: product.sku,
    name: product.name,
    path: product.path,
    price: product.price,
    pack: product.pack,
    stock: product.stock,
    attrs: product.attrs
  })),
  featured: (engine.featured(10) as Product[]).map((product) => product.sku)
};

writeFileSync(outFile, JSON.stringify(result, null, 1));
console.log(
  `${result.attributes.length} xususiyat, ${categories.length} kategoriya, ` +
    `${result.products.length} mahsulot, ${result.featured.length} ommabop -> ${outFile}`
);
