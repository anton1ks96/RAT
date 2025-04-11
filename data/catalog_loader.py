import json

def load_catalog(catalog_path='catalog.json'):
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    return catalog

def format_catalog(catalog):
    catalog_lines = []
    for product in catalog:
        line = f"{product['name']} · {product['volume']} · {product['price']}"
        if 'description' in product and product['description']:
            line += f"\n\nОписание: {product['description']}"
        catalog_lines.append(line)
    return "\n\n".join(catalog_lines)