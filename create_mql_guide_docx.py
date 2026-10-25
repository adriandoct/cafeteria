import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def build_mql_guide():
    doc = docx.Document()

    # Configuración de márgenes estándar
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Paleta de colores corporativos URC y MongoDB
    COLOR_PRIMARY = RGBColor(15, 23, 42)       # Slate 900
    COLOR_MONGO_GREEN = RGBColor(19, 170, 82)  # MongoDB Forest Green
    COLOR_SECONDARY = RGBColor(14, 165, 233)   # Sky 500
    COLOR_AMBER = RGBColor(217, 119, 6)        # Amber 600
    COLOR_ROSE = RGBColor(225, 29, 72)         # Rose 600
    COLOR_TEXT = RGBColor(51, 65, 85)          # Slate 700
    COLOR_MUTED = RGBColor(100, 116, 139)      # Slate 500
    COLOR_CODE_DARK = RGBColor(30, 41, 59)     # Dark slate

    HEX_PRIMARY = "0F172A"
    HEX_MONGO_GREEN = "13AA52"
    HEX_SECONDARY = "0EA5E9"
    HEX_AMBER = "D97706"
    HEX_ROSE = "E11D48"
    HEX_BG_HEADER = "1E293B"
    HEX_BG_SUBHEADER = "0F766E"
    HEX_BG_MONGO = "023430"
    HEX_BG_ALT = "F8FAFC"
    HEX_BORDER = "CBD5E1"
    HEX_CALLOUT_BG = "F1F5F9"
    HEX_CODE_BG = "F8FAFC"

    # Helpers XML de estilizado
    def set_cell_background(cell, hex_color):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    def set_cell_margins(cell, top=130, bottom=130, left=170, right=170):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def set_cell_borders(cell, top=HEX_BORDER, bottom=HEX_BORDER, left=None, right=None, sz=4):
        tcPr = cell._tc.get_or_add_tcPr()
        borders_xml = f'<w:tcBorders {nsdecls("w")}>'
        borders_xml += f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{top}"/>' if top else '<w:top w:val="none"/>'
        borders_xml += f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{bottom}"/>' if bottom else '<w:bottom w:val="none"/>'
        borders_xml += f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{left}"/>' if left else '<w:left w:val="none"/>'
        borders_xml += f'<w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{right}"/>' if right else '<w:right w:val="none"/>'
        borders_xml += '</w:tcBorders>'
        tcPr.append(parse_xml(borders_xml))

    def add_header_h1(text, icon="🍃"):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(22)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        
        run_icon = p.add_run(f"{icon} ")
        run_icon.font.size = Pt(14)
        
        run = p.add_run(text)
        run.font.name = "Arial"
        run.font.size = Pt(14.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY

        p_line = doc.add_paragraph()
        p_line.paragraph_format.space_before = Pt(0)
        p_line.paragraph_format.space_after = Pt(8)
        run_line = p_line.add_run("―" * 65)
        run_line.font.size = Pt(8)
        run_line.font.color.rgb = RGBColor(203, 213, 225)

    def add_header_h2(text, badge=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        
        run = p.add_run(text)
        run.font.name = "Arial"
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = COLOR_MONGO_GREEN

        if badge:
            run_b = p.add_run(f"  [{badge}]")
            run_b.font.size = Pt(9)
            run_b.font.color.rgb = COLOR_MUTED
            run_b.font.italic = True

    def add_header_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        
        run = p.add_run(text)
        run.font.name = "Arial"
        run.font.size = Pt(10.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY

    def add_p(text, bold_prefix=None, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        
        if bold_prefix:
            run_b = p.add_run(bold_prefix)
            run_b.font.name = "Calibri"
            run_b.font.size = Pt(10)
            run_b.font.bold = True
            run_b.font.color.rgb = COLOR_PRIMARY
            
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR_TEXT
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            run_b = p.add_run(bold_prefix)
            run_b.font.name = "Calibri"
            run_b.font.size = Pt(10)
            run_b.font.bold = True
            run_b.font.color.rgb = COLOR_PRIMARY
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR_TEXT

    def add_callout(text, title="NOTA DE ARQUITECTURA", border_hex=HEX_MONGO_GREEN, icon="💡"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.9)
        set_cell_background(cell, HEX_CALLOUT_BG)
        set_cell_margins(cell, top=120, bottom=120, left=180, right=160)
        set_cell_borders(cell, top=None, bottom=None, left=border_hex, right=None, sz=18)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        r_title = p.add_run(f"{icon} {title}\n")
        r_title.font.name = "Arial"
        r_title.font.size = Pt(9.5)
        r_title.font.bold = True
        if border_hex == HEX_MONGO_GREEN:
            r_title.font.color.rgb = COLOR_MONGO_GREEN
        elif border_hex == HEX_AMBER:
            r_title.font.color.rgb = COLOR_AMBER
        elif border_hex == HEX_ROSE:
            r_title.font.color.rgb = COLOR_ROSE
        else:
            r_title.font.color.rgb = COLOR_PRIMARY

        r_body = p.add_run(text)
        r_body.font.name = "Calibri"
        r_body.font.size = Pt(9.5)
        r_body.font.color.rgb = COLOR_TEXT
        doc.add_paragraph().paragraph_format.space_after = Pt(3)

    def add_code_box(code_content, language="MQL / Python"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.9)
        set_cell_background(cell, "0F172A")  # Fondo oscuro elegante
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        set_cell_borders(cell, top=HEX_BORDER, bottom=HEX_BORDER, left=HEX_BORDER, right=HEX_BORDER, sz=4)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.1

        r_lang = p.add_run(f"// --- {language} ---\n")
        r_lang.font.name = "Consolas"
        r_lang.font.size = Pt(8.5)
        r_lang.font.color.rgb = RGBColor(148, 163, 184) # slate 400

        r_code = p.add_run(code_content)
        r_code.font.name = "Consolas"
        r_code.font.size = Pt(9)
        r_code.font.color.rgb = RGBColor(226, 232, 240) # light text

        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ==============================================================================
    # 1. PORTADA PROFESIONAL
    # ==============================================================================
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_before = Pt(20)
    p_meta.paragraph_format.space_after = Pt(4)
    r_inst = p_meta.add_run("UNIVERSIDAD ROSARIO CASTELLANOS\n")
    r_inst.font.name = "Arial"
    r_inst.font.size = Pt(13)
    r_inst.font.bold = True
    r_inst.font.color.rgb = COLOR_MONGO_GREEN

    r_dep = p_meta.add_run("DIRECCIÓN DE SISTEMAS Y TECNOLOGÍA • ARQUITECTURA DE SOFTWARE NoSQL\n")
    r_dep.font.name = "Arial"
    r_dep.font.size = Pt(10)
    r_dep.font.bold = True
    r_dep.font.color.rgb = COLOR_MUTED

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(22)
    p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("GUÍA MAESTRA DEL LENGUAJE MQL (MONGODB QUERY LANGUAGE)\nEN EL SISTEMA CAFÉ URC EXPRESS")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(4)
    p_sub.paragraph_format.space_after = Pt(20)
    r_sub = p_sub.add_run("Ubicación Exacta en el Código Fuente, Traducción de Django ORM a MQL Nativo, Guía Operativa de Actualización, Modificación, Eliminación (CRUD) y Manipulación de Subdocumentos Embebidos")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_MUTED

    # Ficha Técnica en Tabla
    table_meta = doc.add_table(rows=6, cols=2)
    table_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_rows = [
        ("Base de Datos NoSQL:", "MongoDB (Base de datos: 'cafeteria')"),
        ("Controlador / Driver:", "django-mongodb-backend 6.1.0 + PyMongo 4.18.2"),
        ("Framework Backend:", "Django 6.1 (Python 3.12+ / 3.14)"),
        ("Colecciones Activas:", "users, categories, products, inventory, orders, shifts"),
        ("Subdocumentos Embebidos:", "DetalleItem (Array), PagoMercadoPago (Objeto inmutable)"),
        ("Enfoque de la Guía:", "Localización de código, Actualizar ($set, $inc), Modificar, Borrar ($unset, deleteOne/Many) y MQL Nativo"),
    ]
    col_widths = [Inches(2.4), Inches(4.5)]
    for i, (k, v) in enumerate(meta_rows):
        row = table_meta.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width, c1.width = col_widths[0], col_widths[1]
        set_cell_background(c0, HEX_CALLOUT_BG)
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
        set_cell_borders(c0, top=HEX_BORDER, bottom=HEX_BORDER, left=HEX_BORDER, right=HEX_BORDER)
        set_cell_borders(c1, top=HEX_BORDER, bottom=HEX_BORDER, left=HEX_BORDER, right=HEX_BORDER)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.font.name = "Arial"
        r0.font.size = Pt(9)
        r0.font.bold = True
        r0.font.color.rgb = COLOR_PRIMARY

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.font.name = "Calibri"
        r1.font.size = Pt(9)
        r1.font.color.rgb = COLOR_TEXT

    doc.add_page_break()

    # ==============================================================================
    # SECCIÓN 1: ¿QUÉ ES MQL Y CÓMO FUNCIONA EN ESTE PROYECTO?
    # ==============================================================================
    add_header_h1("1. Fundamentos: ¿Qué es el Lenguaje MQL y su Rol en el Proyecto?", "🍃")
    
    add_p(
        "MQL (MongoDB Query Language) es el lenguaje nativo de consulta, manipulación y agregación de MongoDB. "
        "A diferencia del SQL tradicional que opera sobre tablas relacionales compuestas de filas y columnas rígidas "
        "mediante sentencias como SELECT, INSERT INTO, UPDATE o DELETE, MQL opera directamente sobre documentos BSON "
        "(Binary JSON) y colecciones estructuradas de manera flexible mediante sintaxis de objetos y operadores especializados ($set, $inc, $in, $push, etc.)."
    )

    add_p(
        "En el proyecto Café URC Express, el lenguaje MQL coexiste en tres niveles de interacción:",
        bold_prefix="Los 3 Niveles de MQL en este Proyecto: "
    )

    add_bullet(
        " Nivel donde tú escribes código en Python utilizando modelos de Django (Pedido, Producto, Inventario). "
        "El paquete oficial django-mongodb-backend (versión 6.1.0) intercepta cada llamada de Python y la compila transparentemente en comandos de MQL que son transmitidos a MongoDB a través de sockets TCP.",
        bold_prefix="1. Nivel ORM (Traductor Automático Python -> MQL):"
    )
    add_bullet(
        " El driver oficial de MongoDB en Python instalado en tu entorno virtual (pymongo 4.18.2). "
        "Permite enviar comandos MQL nativos directos (como db.orders.find_one(), update_one(), delete_many()) desde scripts de Python sin pasar por el ORM de Django.",
        bold_prefix="2. Nivel Driver Nativo (PyMongo):"
    )
    add_bullet(
        " La consola de comandos oficial (mongosh) o la interfaz gráfica MongoDB Compass. "
        "Aquí es donde se ejecuta MQL en su forma más pura y directa (ej. db.orders.updateOne({_id: ObjectId('...')}, {$set: {estado: 'DELIVERED'}})).",
        bold_prefix="3. Nivel Shell y GUI (mongosh & MongoDB Compass):"
    )

    add_callout(
        "La conexión principal a MongoDB se encuentra declarada en el archivo config/settings.py (líneas 77-88). "
        "Allí se define el motor 'django_mongodb_backend', el host 'mongodb://localhost:27017/' y el nombre de la base de datos 'cafeteria'. "
        "Todas las operaciones de la cafetería impactan directamente en esta base de datos.",
        title="DÓNDE SE CONFIGURA LA CONEXIÓN MONGODB",
        border_hex=HEX_MONGO_GREEN,
        icon="🔌"
    )

    # ==============================================================================
    # SECCIÓN 2: DÓNDE ESTÁ EL CÓDIGO MQL EN TU PROYECTO (MAPA DE ARCHIVOS)
    # ==============================================================================
    add_header_h1("2. Localización Exacta: ¿Dónde está el Código MQL en el Proyecto?", "📂")

    add_p(
        "Si buscas sentencias de texto plano tipo SQL (SELECT * FROM...) no las encontrarás, porque este proyecto es 100% NoSQL. "
        "A continuación se detalla exactamente en qué archivos y funciones se ejecutan las operaciones del lenguaje MQL:"
    )

    table_loc = doc.add_table(rows=7, cols=4)
    table_loc.alignment = WD_TABLE_ALIGNMENT.CENTER
    loc_headers = ["Archivo Fuente", "Líneas / Módulo", "Operación MQL Ejecutada", "Propósito en la Cafetería"]
    for j, h in enumerate(loc_headers):
        cell = table_loc.rows[0].cells[j]
        set_cell_background(cell, HEX_BG_HEADER)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    loc_data = [
        ("miapp/models.py", "Líneas 235-250\n(Inventario)", "updateOne ($set / $inc)", "Descuenta stock en venta y reabastece existencias físicas."),
        ("miapp/models.py", "Líneas 400-415\n(TurnoCorte)", "updateOne ($set)", "Cierre de turno de caja y cálculo de arqueo ciego."),
        ("miapp/views.py", "Líneas 169-202\n(menu_cliente)", "find / find_one", "Consulta catálogo activo, categorías y stock para la PWA."),
        ("miapp/views.py", "Líneas 490-503\n(api_crear_pedido)", "insertOne (con Array)", "Inserta un pedido nuevo con ítems embebidos y PIN seguro."),
        ("miapp/views.py", "Líneas 561-570\n(webhook MP)", "updateOne ($set)\nfind_one", "Actualiza estatus de pago a APPROVED y descuenta inventario."),
        ("miapp/views.py", "Líneas 747-748\n(api_estado_kds)", "updateOne ($set)", "Transición de comanda: PAID -> IN_PREP -> READY -> DELIVERED."),
    ]

    widths_loc = [Inches(1.5), Inches(1.3), Inches(1.7), Inches(2.4)]
    for i, row in enumerate(loc_data, 1):
        tr = table_loc.rows[i]
        bg = HEX_BG_ALT if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            c = tr.cells[j]
            c.width = widths_loc[j]
            set_cell_background(c, bg)
            set_cell_margins(c, top=60, bottom=60, left=80, right=80)
            set_cell_borders(c, top=HEX_BORDER, bottom=HEX_BORDER, left=HEX_BORDER, right=HEX_BORDER)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ==============================================================================
    # SECCIÓN 3: CÓMO SE INSERTA / CREA (CREATE / INSERT)
    # ==============================================================================
    add_header_h1("3. Inserción de Datos: Dónde y Cómo se Crea en MQL (Insert)", "➕")

    add_p(
        "En MongoDB, la creación de nuevos registros se realiza mediante los comandos MQL insertOne() (para un documento) "
        "o insertMany() (para inserciones en lote). En el código de Django, esto se detona mediante el método .objects.create() o instanciando el modelo y ejecutando .save()."
    )

    add_header_h2("3.1 Inserción de un Pedido con Subdocumentos Embebidos (PWA Cliente)")
    add_p(
        "Ubicación en el código: miapp/views.py -> función api_crear_pedido_cliente (líneas 490 a 503).",
        bold_prefix="📍 Dónde está: "
    )
    add_p(
        "Cuando el estudiante o docente realiza una compra desde su celular, la función recibe los productos, "
        "genera el número de turno (#URC-XXX), el código PIN de retiro seguro, los ítems embebidos inmutables (DetalleItem) "
        "y el subdocumento inicial de pago (PagoMercadoPago)."
    )

    add_header_h3("Código Python en tu Proyecto (miapp/views.py):")
    code_insert_py = (
        "# 1. Instanciar subdocumentos embebidos\n"
        "detalles_embebidos = [\n"
        "    DetalleItem(producto_id=str(prod.id), sku=prod.sku, nombre_prod=prod.nombre,\n"
        "                precio_unitario=prod.precio_venta, cantidad=2, subtotal=116.00,\n"
        "                area_despacho='Cocina', notas='Bien dorada, con rajas')\n"
        "]\n"
        "pago_mp = PagoMercadoPago(mp_payment_id='MP-20261022-99', metodo_pago='QR_MERCADOPAGO',\n"
        "                         estatus='PENDING', monto=116.00)\n\n"
        "# 2. Inserción del documento principal en la colección 'orders'\n"
        "pedido = Pedido.objects.create(\n"
        "    order_number='#URC-105',\n"
        "    cliente=cliente_perfil,\n"
        "    cliente_nombre='Valeria Gómez Sánchez',\n"
        "    codigo_pin='PIN-412',\n"
        "    estado='PENDING_PAYMENT',\n"
        "    tipo_despacho='Cocina Caliente',\n"
        "    items=detalles_embebidos,\n"
        "    subtotal=Decimal('116.00'),\n"
        "    total=Decimal('116.00'),\n"
        "    pago=pago_mp,\n"
        "    origen='PWA Móvil',\n"
        "    tiempo_espera_estimado=7\n"
        ")"
    )
    add_code_box(code_insert_py, "Python (Django ORM en miapp/views.py)")

    add_header_h3("Comando MQL Nativo que se Ejecuta en MongoDB:")
    code_insert_mql = (
        "use cafeteria;\n\n"
        "db.orders.insertOne({\n"
        "  order_number: \"#URC-105\",\n"
        "  cliente_nombre: \"Valeria Gómez Sánchez\",\n"
        "  codigo_pin: \"PIN-412\",\n"
        "  estado: \"PENDING_PAYMENT\",\n"
        "  tipo_despacho: \"Cocina Caliente\",\n"
        "  items: [\n"
        "    {\n"
        "      producto_id: \"6717a1b2c3d4e5f6a7b8c9d0\",\n"
        "      sku: \"URC-TRT-01\",\n"
        "      nombre_prod: \"Torta de Milanesa con Queso\",\n"
        "      precio_unitario: NumberDecimal(\"58.00\"),\n"
        "      cantidad: 2,\n"
        "      subtotal: NumberDecimal(\"116.00\"),\n"
        "      area_despacho: \"Cocina\",\n"
        "      notas: \"Bien dorada, con rajas\"\n"
        "    }\n"
        "  ],\n"
        "  pago: {\n"
        "    mp_payment_id: \"MP-20261022-99\",\n"
        "    metodo_pago: \"QR_MERCADOPAGO\",\n"
        "    estatus: \"PENDING\",\n"
        "    monto: NumberDecimal(\"116.00\"),\n"
        "    fecha_pago: null\n"
        "  },\n"
        "  subtotal: NumberDecimal(\"116.00\"),\n"
        "  total: NumberDecimal(\"116.00\"),\n"
        "  origen: \"PWA Móvil\",\n"
        "  tiempo_espera_estimado: 7,\n"
        "  creado_en: ISODate(\"2026-10-22T10:35:00Z\"),\n"
        "  actualizado_en: ISODate(\"2026-10-22T10:35:00Z\")\n"
        "});"
    )
    add_code_box(code_insert_mql, "MQL Nativo (db.orders.insertOne)")

    # ==============================================================================
    # SECCIÓN 4: CÓMO SE CONSULTA / BUSCA (READ / FIND)
    # ==============================================================================
    add_header_h1("4. Consultas y Filtros: Dónde y Cómo se Busca en MQL (Find)", "🔍")

    add_p(
        "Para leer datos, MQL utiliza db.coleccion.find(filtro, proyeccion) o db.coleccion.findOne(filtro). "
        "En Django, esto corresponde a .objects.filter(), .objects.get() y .objects.all()."
    )

    add_header_h2("4.1 Consulta de Pedidos Activos en Pantalla KDS (Cocina y Mostrador)")
    add_p(
        "Ubicación en el código: miapp/views.py -> función pantalla_kds (líneas 295 a 305).",
        bold_prefix="📍 Dónde está: "
    )
    add_p(
        "La pantalla de cocina necesita únicamente las órdenes que ya están pagadas (PAID) o en preparación (IN_PREPARATION), "
        "ordenadas cronológicamente para atender primero a quienes llegaron primero (FIFO)."
    )

    add_header_h3("Código Python en tu Proyecto:")
    code_find_py = (
        "# Consulta en Django ORM con operador __in y orden ascendente\n"
        "pedidos_activos = Pedido.objects.filter(\n"
        "    estado__in=['PAID', 'IN_PREPARATION']\n"
        ").order_by('creado_en')"
    )
    add_code_box(code_find_py, "Python (Django ORM)")

    add_header_h3("Comando MQL Nativo Equivalente:")
    code_find_mql = (
        "// MQL: Operador $in para múltiples estados y sort: 1 (ascendente)\n"
        "db.orders.find({\n"
        "  estado: { $in: [\"PAID\", \"IN_PREPARATION\"] }\n"
        "}).sort({ creado_en: 1 });"
    )
    add_code_box(code_find_mql, "MQL Nativo (db.orders.find con $in)")

    add_header_h2("4.2 Consulta con Notación de Punto (Dot Notation) para Subdocumentos")
    add_p(
        "MongoDB permite buscar dentro de objetos anidados sin necesidad de costosos 'JOIN'. "
        "Por ejemplo, para buscar todos los pedidos pagados mediante Mercado Pago con tarjeta de débito o QR:"
    )
    code_find_dot = (
        "// MQL: Búsqueda sobre el subdocumento 'pago'\n"
        "db.orders.find({\n"
        "  \"pago.estatus\": \"APPROVED\",\n"
        "  \"pago.metodo_pago\": \"QR_MERCADOPAGO\"\n"
        "});"
    )
    add_code_box(code_find_dot, "MQL Nativo (Dot Notation sobre Subdocumentos)")

    # ==============================================================================
    # SECCIÓN 5: CÓMO SE ACTUALIZA / CAMBIA (UPDATE / CHANGE)
    # ==============================================================================
    add_header_h1("5. Modificación y Actualización: Dónde y Cómo se Cambia en MQL (Update)", "✏️")

    add_p(
        "Esta es una de las partes más críticas del sistema. En MQL, NUNCA se sobreescribe un documento completo "
        "para cambiar solo un campo; se utilizan operadores de actualización atómicos como $set (para asignar valores), "
        "$inc (para sumar o restar cantidades numéricas como stock), $push (para agregar a un array) o $currentDate."
    )

    add_header_h2("5.1 Caso A: Cambio de Estado de Comanda en Pantalla KDS (Cocina)")
    add_p(
        "Ubicación en el código: miapp/views.py -> función api_actualizar_estado_kds (líneas 747 a 749).",
        bold_prefix="📍 Dónde está: "
    )
    add_p(
        "Cuando el cocinero hace clic en 'Listo para Retiro', el pedido cambia de 'IN_PREPARATION' a 'READY_FOR_PICKUP'. "
        "En Django se ejecuta pedido.estado = nuevo_estado y pedido.save()."
    )

    add_header_h3("Código Python en tu Proyecto:")
    code_upd_kds_py = (
        "pedido = Pedido.objects.filter(id=order_id).first()\n"
        "pedido.estado = 'READY_FOR_PICKUP'\n"
        "pedido.save()"
    )
    add_code_box(code_upd_kds_py, "Python (Django ORM)")

    add_header_h3("Comando MQL Nativo que se Ejecuta:")
    code_upd_kds_mql = (
        "// MQL: updateOne con operador atómico $set\n"
        "db.orders.updateOne(\n"
        "  { _id: ObjectId(\"6717a1b2c3d4e5f6a7b8c9d0\") },\n"
        "  {\n"
        "    $set: {\n"
        "      estado: \"READY_FOR_PICKUP\",\n"
        "      actualizado_en: new Date()\n"
        "    }\n"
        "  }\n"
        ");"
    )
    add_code_box(code_upd_kds_mql, "MQL Nativo (db.orders.updateOne con $set)")

    add_header_h2("5.2 Caso B: Descuento Atómico de Inventario al Vender (Blindaje contra Sobreventas)")
    add_p(
        "Ubicación en el código: miapp/models.py -> método descontar() de la clase Inventario (líneas 235 a 241).",
        bold_prefix="📍 Dónde está: "
    )
    add_p(
        "Al confirmarse una venta por mostrador o por Mercado Pago, el stock debe disminuir de forma segura."
    )

    add_header_h3("Código Python en tu Proyecto:")
    code_inv_py = (
        "# miapp/models.py (Línea 238)\n"
        "def descontar(self, cantidad):\n"
        "    if self.stock_actual >= cantidad:\n"
        "        self.stock_actual -= cantidad\n"
        "        self.save(update_fields=['stock_actual', 'actualizado_en'])\n"
        "        return True\n"
        "    return False"
    )
    add_code_box(code_inv_py, "Python (Método en Inventario)")

    add_header_h3("Comando MQL Nativo (Uso del Operador $inc):")
    code_inv_mql = (
        "// MQL: Decrementar el campo 'stock_actual' en 2 unidades de forma atómica\n"
        "db.inventory.updateOne(\n"
        "  { producto_id: ObjectId(\"6717a1b2c3d4e5f6a7b8c9d0\") },\n"
        "  {\n"
        "    $inc: { stock_actual: -2 },\n"
        "    $set: { actualizado_en: new Date() }\n"
        "  }\n"
        ");"
    )
    add_code_box(code_inv_mql, "MQL Nativo (Operador $inc en db.inventory)")

    add_header_h2("5.3 Caso C: Actualización Masiva de Turnos Previos (Cierre de Caja)")
    add_p(
        "Ubicación en el código: miapp/views.py -> función api_abrir_turno (línea 819).",
        bold_prefix="📍 Dónde está: "
    )
    add_p(
        "Al abrir un nuevo turno, el sistema cierra automáticamente cualquier turno anterior que haya quedado en estado 'ABIERTO'."
    )
    code_bulk_upd = (
        "# Python (Django ORM):\n"
        "TurnoCorte.objects.filter(cajero=perfil, estado='ABIERTO').update(estado='CERRADO', fecha_cierre=timezone.now())\n\n"
        "// MQL Nativo equivalente (updateMany):\n"
        "db.shifts.updateMany(\n"
        "  { cajero_id: ObjectId(\"...\"), estado: \"ABIERTO\" },\n"
        "  {\n"
        "    $set: {\n"
        "      estado: \"CERRADO\",\n"
        "      fecha_cierre: new Date()\n"
        "    }\n"
        "  }\n"
        ");"
    )
    add_code_box(code_bulk_upd, "Python vs MQL (updateMany)")

    # ==============================================================================
    # SECCIÓN 6: CÓMO SE BORRA / ELIMINA (DELETE / REMOVE)
    # ==============================================================================
    add_header_h1("6. Eliminación de Datos: Dónde y Cómo se Borra en MQL (Delete)", "🗑️")

    add_p(
        "En el lenguaje MQL de MongoDB, el borrado físico de documentos se lleva a cabo mediante los métodos "
        "db.coleccion.deleteOne(filtro) y db.coleccion.deleteMany(filtro). Si se desea eliminar una colección entera, "
        "se utiliza db.coleccion.drop()."
    )

    add_header_h2("6.1 Borrado Físico (Hard Delete) en Django Admin y Código")
    add_p(
        "Ubicación en el código: miapp/admin.py (líneas 72 a 75) y método nativo .delete() de Django.",
        bold_prefix="📍 Dónde está: "
    )
    add_p(
        "En el panel de administración (/admin), los administradores pueden seleccionar productos, categorías o turnos "
        "y eliminarlos. Cuando ejecutas obj.delete() en Python, Django envía a MongoDB un comando deleteOne()."
    )

    add_header_h3("Código Python en Django:")
    code_del_py = (
        "# Eliminar un producto específico por su SKU\n"
        "producto = Producto.objects.filter(sku='URC-TRT-01').first()\n"
        "if producto:\n"
        "    producto.delete()\n\n"
        "# Eliminar pedidos cancelados con más de 30 días de antigüedad\n"
        "Pedido.objects.filter(estado='CANCELLED').delete()"
    )
    add_code_box(code_del_py, "Python (Django ORM .delete())")

    add_header_h3("Comandos MQL Nativos Equivalentes:")
    code_del_mql = (
        "// 1. Borrar un solo documento por filtro exacto:\n"
        "db.products.deleteOne({ sku: \"URC-TRT-01\" });\n\n"
        "// 2. Borrar múltiples documentos que coincidan con un criterio:\n"
        "db.orders.deleteMany({ estado: \"CANCELLED\" });\n\n"
        "// 3. Borrar un documento por su clave primaria _id:\n"
        "db.orders.deleteOne({ _id: ObjectId(\"6717a1b2c3d4e5f6a7b8c9d0\") });"
    )
    add_code_box(code_del_mql, "MQL Nativo (deleteOne / deleteMany)")

    add_callout(
        "En un sistema transaccional de cafetería universitaria, los pedidos NUNCA deben borrarse físicamente con deleteOne() "
        "porque se perdería la auditoría de caja (Arqueo Ciego) y las estadísticas contables del corte Z. "
        "En su lugar, el sistema implementa BORRADO LÓGICO (Soft Delete): se ejecuta un updateOne() cambiando el campo estado a 'CANCELLED' "
        "o activo a false en productos (db.products.updateOne({sku: '...'}, {$set: {activo: false}})). "
        "De este modo, el ítem deja de verse en el menú pero permanece en el historial para auditorías.",
        title="REGLA DE ORO DE ARQUITECTURA NoSQL: BORRADO LÓGICO VS FÍSICO",
        border_hex=HEX_ROSE,
        icon="⚠️"
    )

    # ==============================================================================
    # SECCIÓN 7: SUBDOCUMENTOS EMBEBIDOS EN MQL
    # ==============================================================================
    add_header_h1("7. Manejo Avanzado de Subdocumentos y Arreglos en MQL", "🧩")

    add_p(
        "Uno de los mayores atractivos de MongoDB frente a SQL es su capacidad de almacenar estructuras jerárquicas "
        "dentro del mismo documento. En este proyecto tenemos dos campos embebidos fundamentales en la colección 'orders':"
    )

    add_bullet(
        " Subdocumento individual con los datos de pasarela (mp_payment_id, metodo_pago, estatus, monto, fecha_pago).",
        bold_prefix="1. Objeto Embebido 'pago' (PagoMercadoPago):"
    )
    add_bullet(
        " Arreglo de subdocumentos con la instantánea inmutable de los productos comprados (producto_id, sku, precio_unitario, cantidad, notas).",
        bold_prefix="2. Arreglo Embebido 'items' (DetalleItem):"
    )

    add_header_h2("Operaciones MQL sobre Arreglos y Subdocumentos:")

    add_header_h3("A. Buscar Pedidos que Contengan un Producto Específico dentro del Arreglo:")
    code_sub_find = (
        "// MQL: Operador $elemMatch para buscar dentro del arreglo 'items'\n"
        "db.orders.find({\n"
        "  items: {\n"
        "    $elemMatch: {\n"
        "      sku: \"URC-TRT-01\",\n"
        "      area_despacho: \"Cocina\"\n"
        "    }\n"
        "  }\n"
        "});"
    )
    add_code_box(code_sub_find, "MQL Nativo ($elemMatch sobre arreglo de ítems)")

    add_header_h3("B. Agregar un Nuevo Ítem al Arreglo Embebido sin Reescribir el Pedido ($push):")
    code_sub_push = (
        "// MQL: Operador $push para insertar un nuevo ítem a la lista de items\n"
        "db.orders.updateOne(\n"
        "  { order_number: \"#URC-105\" },\n"
        "  {\n"
        "    $push: {\n"
        "      items: {\n"
        "        producto_id: \"6717a1b2c3d4e5f6a7b8c9d1\",\n"
        "        sku: \"URC-BEB-01\",\n"
        "        nombre_prod: \"Agua Purificada 600ml\",\n"
        "        precio_unitario: NumberDecimal(\"15.00\"),\n"
        "        cantidad: 1,\n"
        "        subtotal: NumberDecimal(\"15.00\"),\n"
        "        area_despacho: \"Mostrador\",\n"
        "        notas: \"Fría\"\n"
        "      }\n"
        "    },\n"
        "    $inc: { total: NumberDecimal(\"15.00\") }\n"
        "  }\n"
        ");"
    )
    add_code_box(code_sub_push, "MQL Nativo ($push para agregar subdocumento)")

    # ==============================================================================
    # SECCIÓN 8: CÓMO EJECUTAR MQL DIRECTAMENTE (GUÍA PRÁCTICA)
    # ==============================================================================
    add_header_h1("8. Guía Práctica: ¿Cómo Ejecutar Comandos MQL en tu Computadora?", "💻")

    add_p(
        "Tienes 3 maneras directas de interactuar con el lenguaje MQL sobre la base de datos 'cafeteria' de este proyecto:"
    )

    add_header_h2("Método 1: Desde la Consola mongosh (MongoDB Shell)")
    add_p("Abre tu terminal de Windows (PowerShell o CMD) y escribe:")
    code_shell = (
        "# 1. Abrir mongosh\n"
        "mongosh\n\n"
        "# 2. Conectarse a la base de datos del proyecto\n"
        "use cafeteria;\n\n"
        "# 3. Ver todas las colecciones\n"
        "show collections;\n\n"
        "# 4. Contar pedidos existentes\n"
        "db.orders.countDocuments();\n\n"
        "# 5. Ver el último pedido registrado de forma legible\n"
        "db.orders.find().sort({ creado_en: -1 }).limit(1).pretty();"
    )
    add_code_box(code_shell, "Comandos mongosh en Terminal")

    add_header_h2("Método 2: Desde MongoDB Compass (Interfaz Gráfica)")
    add_p(
        "Abre MongoDB Compass y conéctate a mongodb://localhost:27017. "
        "Selecciona la base de datos 'cafeteria' y haz clic en la colección 'orders'. "
        "En la barra superior de filtro ('Filter'), puedes escribir MQL directo como:"
    )
    add_bullet("{ estado: 'READY_FOR_PICKUP' } -> Para ver los pedidos listos para entrega.")
    add_bullet("{ 'pago.metodo_pago': 'QR_MERCADOPAGO' } -> Para filtrar por ventas con código QR.")
    add_bullet("{ total: { $gte: 100 } } -> Para ver compras mayores o iguales a $100 MXN.")

    add_header_h2("Método 3: Ejecutar MQL Nativo desde Python en tu Proyecto (vía PyMongo)")
    add_p(
        "Si necesitas ejecutar una consulta MQL directa en un script o vista de Django sin restricciones del ORM, "
        "puedes usar el cliente directo de PyMongo que ya está configurado:"
    )
    code_pymongo = (
        "from pymongo import MongoClient\n\n"
        "# Conexión directa al servidor local\n"
        "client = MongoClient('mongodb://localhost:27017/')\n"
        "db = client['cafeteria']\n\n"
        "# 1. MQL nativo: Búsqueda\n"
        "pedido = db.orders.find_one({'order_number': '#URC-101'})\n"
        "print('Cliente:', pedido['cliente_nombre'])\n\n"
        "# 2. MQL nativo: Actualización con $set\n"
        "db.orders.update_one(\n"
        "    {'order_number': '#URC-101'},\n"
        "    {'$set': {'estado': 'DELIVERED'}}\n"
        ")\n\n"
        "# 3. MQL nativo: Borrado con delete_one\n"
        "db.orders.delete_one({'order_number': '#URC-999'})"
    )
    add_code_box(code_pymongo, "Python con PyMongo Directo")

    # ==============================================================================
    # SECCIÓN 9: TABLA DE EQUIVALENCIAS (CHEAT SHEET: DJANGO ORM <-> MQL)
    # ==============================================================================
    add_header_h1("9. Tabla de Equivalencias Rápidas: Django ORM <---> MQL Nativo", "⚡")

    table_eq = doc.add_table(rows=10, cols=3)
    table_eq.alignment = WD_TABLE_ALIGNMENT.CENTER
    eq_headers = ["Operación Deseada", "Sintaxis Django ORM (Python)", "Sintaxis MQL Nativa (MongoDB)"]
    for j, h in enumerate(eq_headers):
        cell = table_eq.rows[0].cells[j]
        set_cell_background(cell, HEX_BG_MONGO)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    eq_data = [
        ("Insertar un documento", "Pedido.objects.create(campo='val')", "db.orders.insertOne({ campo: 'val' })"),
        ("Buscar todos", "Producto.objects.all()", "db.products.find({})"),
        ("Buscar con filtro simple", "Producto.objects.filter(activo=True)", "db.products.find({ activo: true })"),
        ("Buscar por ID único", "Pedido.objects.get(id=mi_id)", "db.orders.findOne({ _id: ObjectId(mi_id) })"),
        ("Buscar con 'IN' (múltiples)", "Pedido.objects.filter(estado__in=['A','B'])", "db.orders.find({ estado: { $in: ['A','B'] } })"),
        ("Actualizar un solo objeto", "pedido.estado = 'X'\npedido.save()", "db.orders.updateOne({ _id: id }, { $set: { estado: 'X' } })"),
        ("Actualizar en lote (Bulk)", "Turno.objects.filter(e='A').update(e='C')", "db.shifts.updateMany({ e: 'A' }, { $set: { e: 'C' } })"),
        ("Incrementar / Decrementar", "inv.stock_actual -= 2\ninv.save()", "db.inventory.updateOne({}, { $inc: { stock_actual: -2 } })"),
        ("Borrar documento(s)", "pedido.delete()\nPedido.objects.filter(e='C').delete()", "db.orders.deleteOne({ _id: id })\ndb.orders.deleteMany({ e: 'C' })"),
    ]

    widths_eq = [Inches(1.8), Inches(2.5), Inches(2.6)]
    for i, row in enumerate(eq_data, 1):
        tr = table_eq.rows[i]
        bg = HEX_BG_ALT if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            c = tr.cells[j]
            c.width = widths_eq[j]
            set_cell_background(c, bg)
            set_cell_margins(c, top=60, bottom=60, left=80, right=80)
            set_cell_borders(c, top=HEX_BORDER, bottom=HEX_BORDER, left=HEX_BORDER, right=HEX_BORDER)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.name = "Consolas" if j > 0 else "Calibri"
            r.font.size = Pt(8 if j > 0 else 9)
            r.font.color.rgb = COLOR_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Conclusión
    add_p(
        "En resumen: MQL no es un archivo único en el proyecto, sino el lenguaje en el que 'habla' la base de datos MongoDB. "
        "Tu código en Python utiliza Django ORM como capa de abstracción para generar MQL de forma limpia y tipada, "
        "pero cada vez que ejecutas .create(), .filter(), .save(), .update() o .delete(), se ejecuta exactamente la operación MQL "
        "correspondiente descrita en esta guía.",
        bold_prefix="Conclusión de Arquitectura: "
    )

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Guia_MQL_MongoDB_Cafeteria_URC.docx")
    doc.save(output_path)
    print(f"Documento Word generado exitosamente: {output_path}")

if __name__ == "__main__":
    build_mql_guide()
