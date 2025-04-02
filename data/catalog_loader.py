import json

def load_catalog(catalog_path='catalog.json'):
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    return catalog

def format_catalog(catalog):
    catalog_lines = []
    for product in catalog:
        catalog_lines.append(f"Название: {product['name']}, Цена: {product['price']}, Объем: {product['volume']}")
    return "\n".join(catalog_lines)
