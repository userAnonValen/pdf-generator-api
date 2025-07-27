import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from itertools import groupby
from operator import itemgetter
from pathlib import Path

def validar_imagenes(productos):
    imagenes_dir = Path("imagenes")
    if not imagenes_dir.exists():
        imagenes_dir.mkdir(parents=True, exist_ok=True)

    productos_con_imagen = 0
    productos_sin_imagen = 0

    for producto in productos:
        if 'imagen' in producto and producto['imagen']:
            imagen_path = producto['imagen'].replace('file://', '') if producto['imagen'].startswith('file://') else producto['imagen']
            if os.path.exists(imagen_path):
                productos_con_imagen += 1
            else:
                productos_sin_imagen += 1
        else:
            productos_sin_imagen += 1

    return productos_con_imagen, productos_sin_imagen

def generar_estadisticas(productos):
    if not productos:
        return {
            'total_productos': 0,
            'productos_destacados': 0,
            'categorias': {},
            'precio_min': 0,
            'precio_max': 0,
            'precio_promedio': 0
        }

    total_productos = len(productos)
    productos_destacados = len([p for p in productos if p.get('destacado', False)])

    categorias = {}
    for producto in productos:
        categoria = producto.get('categoria', 'Sin categoría')
        categorias[categoria] = categorias.get(categoria, 0) + 1

    precios = [p['precio'] for p in productos if 'precio' in p and isinstance(p['precio'], (int, float))]

    if precios:
        precio_min = min(precios)
        precio_max = max(precios)
        precio_promedio = sum(precios) / len(precios)
    else:
        precio_min = precio_max = precio_promedio = 0

    return {
        'total_productos': total_productos,
        'productos_destacados': productos_destacados,
        'categorias': categorias,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'precio_promedio': precio_promedio
    }

def groupby_filter(seq, attribute):
    orden_categorias = {
        'iPhone': 1,
        'iPad': 2, 
        'Apple Watch': 3,
        'AirPods': 4,
        'Samsung': 5
    }

    def sort_key(item):
        categoria = item.get(attribute, 'Sin categoría')
        return (orden_categorias.get(categoria, 999), categoria)

    sorted_seq = sorted(seq, key=sort_key)
    return groupby(sorted_seq, key=itemgetter(attribute))

def generar_pdf(productos, output_path="catalogo_generado.pdf"):
    productos_con_imagen, productos_sin_imagen = validar_imagenes(productos)
    stats = generar_estadisticas(productos)

    env = Environment(loader=FileSystemLoader("."), autoescape=True)
    env.filters['groupby'] = groupby_filter

    for p in productos:
        if 'imagen' in p and p['imagen'] and not p['imagen'].startswith(('http://', 'https://', 'file://')):
            imagen_path = Path(p['imagen'])
            if imagen_path.exists():
                p['imagen'] = imagen_path.resolve().as_uri()

    template = env.get_template("plantilla.html")
    html_rendered = template.render(productos=productos, stats=stats)

    css_optimizado = CSS(string='''
        @page { size: A4; margin: 1cm; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 0;
            line-height: 1.4;
            color: #1d1d1f;
            font-size: 12px;
        }
        img { max-width: 100%; height: auto; }
        .page-break { page-break-before: always; }
    ''')

    base_path = Path(__file__).parent.resolve()

    HTML(string=html_rendered, base_url=base_path).write_pdf(
    output_path,
    stylesheets=[css_optimizado],
    optimize_size=('fonts', 'images'),
    presentational_hints=True
)

