import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def build_urc_document():
    doc = docx.Document()

    # Configuración de márgenes estándar
    for section in doc.sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)

    # Paleta de colores corporativos URC
    COLOR_PRIMARY = RGBColor(15, 23, 42)       # Slate 900
    COLOR_SECONDARY = RGBColor(14, 165, 233)   # Sky 500
    COLOR_AMBER = RGBColor(217, 119, 6)        # Amber 600
    COLOR_EMERALD = RGBColor(16, 185, 129)     # Emerald 500
    COLOR_ROSE = RGBColor(225, 29, 72)         # Rose 600
    COLOR_TEXT = RGBColor(51, 65, 85)          # Slate 700
    COLOR_MUTED = RGBColor(100, 116, 139)      # Slate 500

    HEX_PRIMARY = "0F172A"
    HEX_SECONDARY = "0EA5E9"
    HEX_AMBER = "D97706"
    HEX_EMERALD = "10B981"
    HEX_BG_HEADER = "1E293B"
    HEX_BG_SUBHEADER = "0F766E"
    HEX_BG_ALT = "F8FAFC"
    HEX_BORDER = "CBD5E1"
    HEX_CALLOUT_BG = "F1F5F9"

    # Helpers XML de estilizado
    def set_cell_background(cell, hex_color):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
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

    def add_header_h1(text, icon="📌"):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(20)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        
        run_icon = p.add_run(f"{icon} ")
        run_icon.font.size = Pt(14)
        
        run = p.add_run(text)
        run.font.name = "Arial"
        run.font.size = Pt(15)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY

        # Línea divisoria elegante
        p_line = doc.add_paragraph()
        p_line.paragraph_format.space_before = Pt(0)
        p_line.paragraph_format.space_after = Pt(8)
        run_line = p_line.add_run("―" * 60)
        run_line.font.size = Pt(8)
        run_line.font.color.rgb = RGBColor(203, 213, 225)

    def add_header_h2(text, badge=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        
        run = p.add_run(text)
        run.font.name = "Arial"
        run.font.size = Pt(12.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_AMBER

        if badge:
            run_b = p.add_run(f"  [{badge}]")
            run_b.font.size = Pt(9.5)
            run_b.font.color.rgb = COLOR_MUTED
            run_b.font.italic = True

    def add_p(text, bold_prefix=None, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        
        if bold_prefix:
            run_b = p.add_run(bold_prefix)
            run_b.font.name = "Calibri"
            run_b.font.size = Pt(10.5)
            run_b.font.bold = True
            run_b.font.color.rgb = COLOR_PRIMARY
            
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(10.5)
        run.font.color.rgb = COLOR_TEXT
        return p

    def add_callout(text, title="NOTA DE ARQUITECTURA", border_hex=HEX_AMBER):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.8)
        set_cell_background(cell, HEX_CALLOUT_BG)
        set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
        set_cell_borders(cell, top=None, bottom=None, left=border_hex, right=None, sz=18)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        r_title = p.add_run(f"💡 {title}\n")
        r_title.font.name = "Arial"
        r_title.font.size = Pt(9.5)
        r_title.font.bold = True
        r_title.font.color.rgb = COLOR_AMBER

        r_body = p.add_run(text)
        r_body.font.name = "Calibri"
        r_body.font.size = Pt(9.5)
        r_body.font.color.rgb = COLOR_TEXT
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ==============================================================================
    # 1. PORTADA PROFESIONAL URC
    # ==============================================================================
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_before = Pt(20)
    p_meta.paragraph_format.space_after = Pt(4)
    r_inst = p_meta.add_run("UNIVERSIDAD ROSARIO CASTELLANOS\n")
    r_inst.font.name = "Arial"
    r_inst.font.size = Pt(13)
    r_inst.font.bold = True
    r_inst.font.color.rgb = COLOR_AMBER

    r_dep = p_meta.add_run("DIRECCIÓN DE SISTEMAS Y TECNOLOGÍA • INGENIERÍA DE SOFTWARE\n")
    r_dep.font.name = "Arial"
    r_dep.font.size = Pt(10)
    r_dep.font.bold = True
    r_dep.font.color.rgb = COLOR_MUTED

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(24)
    p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("CAFÉ URC EXPRESS:\nSISTEMA AUTOMATIZADO DE ATENCIÓN Y PUNTO DE VENTA (POS/KDS)")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(4)
    p_sub.paragraph_format.space_after = Pt(24)
    r_sub = p_sub.add_run("Documento de Análisis Integral de Arquitectura, Modelado NoSQL en MongoDB, Diagrama Estructural UML, Matriz de Roles RBAC y Pasarela Mercado Pago con Arqueo Ciego")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_MUTED

    # Tabla de especificaciones de portada
    tbl_portada = doc.add_table(rows=5, cols=2)
    tbl_portada.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_rows = [
        ("Base de Datos NoSQL:", "MongoDB (Nombre de BD: 'cafeteria' en mongodb://localhost:27017/)"),
        ("Framework & Backend:", "Django 6.1.1 + django-mongodb-backend (Motor Oficial MongoDB)"),
        ("Módulos Principales:", "PWA Móvil Alumnos, POS Cajero con Arqueo Ciego, Pantalla KDS y Dashboard Admin"),
        ("Seguridad & Roles:", "RBAC Estricto (Cliente Estudiante/Docente, Cajero POS, Administrador General)"),
        ("Pasarela & Flujo:", "Mercado Pago (Checkout QR / Saldo / Tarjeta) + Automatización Zero-Touch vía Webhook"),
    ]
    for idx, (label, val) in enumerate(meta_rows):
        c_lbl = tbl_portada.cell(idx, 0)
        c_val = tbl_portada.cell(idx, 1)
        c_lbl.width = Inches(2.2)
        c_val.width = Inches(4.6)
        set_cell_background(c_lbl, "F1F5F9")
        set_cell_background(c_val, "FFFFFF")
        set_cell_margins(c_lbl, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c_val, top=80, bottom=80, left=120, right=120)
        set_cell_borders(c_lbl, sz=2)
        set_cell_borders(c_val, sz=2)
        
        p0 = c_lbl.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.font.bold = True
        r0.font.size = Pt(9)
        r0.font.color.rgb = COLOR_PRIMARY
        
        p1 = c_val.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.size = Pt(9)
        r1.font.color.rgb = COLOR_TEXT

    doc.add_page_break()

    # ==============================================================================
    # 2. RESUMEN EJECUTIVO Y DIAGNÓSTICO OPERATIVO
    # ==============================================================================
    add_header_h1("Resumen Ejecutivo y Diagnóstico Operativo", icon="📊")

    add_p("La cafetería universitaria de la Universidad Rosario Castellanos enfrenta una problemática recurrente en sus horarios pico de mayor demanda: los cambios de bloque de clase y los recesos académicos de 20 minutos. Durante estos lapsos, cientos de alumnos y docentes convergen en una única fila física para ordenar, pagar en efectivo y esperar la entrega de sus productos.")

    add_p("El diagnóstico de ingeniería de procesos revela que en la cafetería colisionan dos naturalezas de consumo totalmente dispares:", bold_prefix="Colisión de Dinámicas Operativas: ")
    add_p("1. Productos de despacho inmediato ('Grab & Go'): Refrescos embotellados, aguas purificadas, jugos, papas, galletas y chocolates, cuya preparación requiere menos de 15 a 30 segundos.")
    add_p("2. Alimentos de cocina caliente con tiempo de elaboración: Tortas a la plancha, chilaquiles con pollo o huevo, baguettes al grill y café de especialidad expresso/capuchino, demandando entre 5 y 8 minutos de cocción.")

    add_p("Al canalizar ambas demandas por una sola caja tradicional con cobro en efectivo suelto, los alumnos que únicamente desean adquirir un agua o dulce quedan atrapados tras órdenes complejas de alimentos calientes. Esto deriva en esperas que promedian 14 a 15 minutos, obligando a los estudiantes a perder minutos clave de clase o abstenerse de consumir en la cafetería.")

    add_callout(
        "OBJETIVO OPERATIVO CENTRAL:\n"
        "Reducir el tiempo promedio de permanencia en fila de 14 minutos a MENOS DE 45 SEGUNDOS para el retiro en barra física, desacoplando el pedido y cobro digital previo (vía PWA y Mercado Pago) de la entrega de comandas.",
        title="META DE IMPACTO CUANTIFICABLE",
        border_hex=HEX_EMERALD
    )

    # ==============================================================================
    # 3. ARQUITECTURA DE FLUJO Y LOGÍSTICA ANTI-COLAS
    # ==============================================================================
    add_header_h1("Arquitectura de Flujo y Logística Anti-Colas", icon="⚡")

    add_p("El sistema opera bajo una arquitectura de flujo desacoplado y despacho segregado por tipo de producto, dividiendo el ciclo del servicio en cuatro etapas sincronizadas en tiempo real:")

    add_header_h2("1. Pedido y Cobro Digital Anticipado (PWA Móvil)")
    add_p("El estudiante o docente explora el menú institucional desde su teléfono móvil antes de terminar su clase. Configura especificaciones detalladas para su orden (ej. 'Torta de milanesa, bien dorada, con rajas, sin cebolla') y procesa el pago de forma instantánea mediante la integración con Mercado Pago (escaneo de código QR, saldo en cuenta o tarjeta bancaria).")

    add_header_h2("2. Segregación Inteligente de Comandas (Routing Algorithm)")
    add_p("En el momento en que se confirma el pago, el backend en Django analiza atómicamente la lista de ítems contenidos en la comanda para determinar su ruta de despacho:")
    add_p("• Si el pedido contiene únicamente productos 'Grab & Go' (bebidas embotelladas, dulces, galletas), viaja a la columna Mostrador Express para su armado inmediato en menos de 30 segundos.")
    add_p("• Si incluye productos calientes (plancha, chilaquiles, café gourmet), se rutea a la columna Cocina Caliente del monitor KDS (Kitchen Display System).")
    add_p("• Si contiene ambos, se etiqueta como despacho 'Mixto', permitiendo que mostrador arme el snack mientras cocina termina la plancha.")

    add_header_h2("3. Máquina de Estados del Pedido")
    add_p("Cada transacción transita de forma determinista a través de la siguiente máquina de estados:")
    add_p("PENDING_PAYMENT  ➔  PAID  ➔  IN_PREPARATION  ➔  READY_FOR_PICKUP  ➔  DELIVERED", bold_prefix="Estados: ")

    add_header_h2("4. Notificación y Retiro Seguro con Código PIN")
    add_p("Cuando el personal de cocina o barra pulsa el botón '¡Listo!' en el KDS, la comanda pasa a estado READY_FOR_PICKUP. El alumno visualiza en su pantalla su número de turno (ej. #URC-142) acompañado de un CÓDIGO PIN DE RETIRO SEGURO (ej. PIN 412). Al presentarse en barra, el personal valida el PIN antes de liberar la charola, erradicando confusiones y suplantaciones de entrega.")

    # ==============================================================================
    # 4. DIAGRAMA ESTRUCTURAL UML Y RELACIONES DE CLASES
    # ==============================================================================
    add_header_h1("Diagrama Estructural UML y Relaciones de Clases", icon="📐")

    add_p("El modelado del sistema implementa una jerarquía orientada a objetos donde los tres actores principales (Cliente, Cajero y Administrador) heredan de la clase base Usuario, desacoplando sus responsabilidades mediante el patrón Role-Based Access Control (RBAC):")

    # Inserción de imagen UML
    img_path = os.path.join(os.path.dirname(__file__), 'uml_colecciones_mongodb.png')
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(6.8))
        
        p_caption = doc.add_paragraph()
        p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_caption.paragraph_format.space_after = Pt(12)
        r_cap = p_caption.add_run("Figura 1: Diagrama Estructural UML de Clases, Herencia y Modelos Embebidos en MongoDB (Base 'cafeteria').")
        r_cap.font.size = Pt(8.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_MUTED

    add_header_h2("Justificación de Cardinalidades y Arquitectura NoSQL")
    add_p("• Cliente a Pedido (1 a Muchos por Referencia): Un estudiante registra decenas de pedidos durante el semestre. Utilizar referencia normalizada (cliente_id) evita que el documento del usuario crezca indefinidamente y desborde el límite de 16MB de MongoDB.")
    add_p("• Pedido a DetalleItem (1 a Muchos - Subdocumento Embebido): Composición inmutable. Cuando el cliente compra una torta a $58.00 con la nota 'bien dorada, con rajas', esos valores quedan congelados dentro del pedido. Posteriores modificaciones de precios del catálogo no adulteran las auditorías históricas pasadas.")
    add_p("• Pedido a PagoMercadoPago (1 a 1 Embebido): Cada orden digital se vincula con un único ID de transacción de pasarela (mp_payment_id) al recibir el webhook 'approved'.")
    add_p("• Cajero a TurnoCorte (1 a Muchos): Cada turno de trabajo genera un arqueo independiente, permitiendo identificar desfasajes por operador sin mezclar fondos.")
    add_p("• Inventario a Producto (1 a 1 Desacoplado): Separar el inventario de la colección maestra de productos evita bloqueos concurrentes de escritura en el catálogo cuando decenas de usuarios compran en el mismo receso.")

    # ==============================================================================
    # 5. MODELO DE DATOS NOSQL MONGODB (COLECCIONES Y SUBDOCUMENTOS)
    # ==============================================================================
    add_header_h1("Modelo de Datos NoSQL (Base de Datos: 'cafeteria')", icon="🗄️")

    add_p("El sistema se diseñó para la base de datos 'cafeteria' en MongoDB, estructurado en 6 colecciones principales y 2 subdocumentos embebidos optimizados para alta concurrencia de lectura y transaccionalidad atómica a nivel de documento:")

    # TABLA DE COLECCIONES
    tbl_cols = doc.add_table(rows=7, cols=4)
    tbl_cols.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_cols = ["Colección / Subdoc", "Propósito en el Negocio", "Tipo Estructural", "Nivel Acceso RBAC"]
    for j, h in enumerate(headers_cols):
        cell = tbl_cols.cell(0, j)
        set_cell_background(cell, HEX_BG_HEADER)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        set_cell_borders(cell, sz=4)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    data_cols = [
        ("users", "Almacena credenciales, matrícula URC, teléfono, correo y rol asignado.", "Colección Raíz", "Autenticación Propia"),
        ("categories", "Agrupa productos y define la segregación de despacho (Cocina vs Mostrador).", "Colección Raíz", "Lectura: Todos | Escritura: Admin"),
        ("products", "Catálogo maestro: SKU, nombre, precio, tiempos estimados y opciones JSON.", "Colección Raíz", "Lectura: Todos | Escritura: Admin"),
        ("inventory", "Existencias físicas, stock mínimo de alerta y fechas de reabastecimiento.", "Colección Raíz", "Solo Administrador (Restringido Cajeros)"),
        ("orders", "Transacción comercial con ítems y pago embebidos, estatus y código PIN.", "Colección Raíz", "Lectura: Propietario | Estado: Cajero/Admin"),
        ("shifts (Cortes Z)", "Registro de turnos de caja, fondo inicial, ventas MP y arqueo ciego.", "Colección Raíz", "Cajero: Opera | Admin: Auditoría Total"),
    ]

    for i, row in enumerate(data_cols, start=1):
        bg = HEX_BG_ALT if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            cell = tbl_cols.cell(i, j)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            set_cell_borders(cell, sz=2)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8)
            r.font.color.rgb = COLOR_TEXT
            if j == 0:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # DETALLE DE CAMPOS POR COLECCIÓN
    add_header_h2("Detalle Exhaustivo de Atributos por Colección")

    add_p("1. Colección 'users' (Modelo: Usuario)", bold_prefix="Colección: ")
    add_p("• _id (ObjectId): Identificador nativo BSON de MongoDB.\n"
          "• user_id (ForeignKey): Vínculo 1 a 1 con auth_user de Django para autenticación y contraseñas hasheadas (PBKDF2/SHA256).\n"
          "• username (String): Identificador único o matrícula institucional.\n"
          "• nombre_completo (String): Nombre oficial del alumno, docente o cajero.\n"
          "• matricula_urc (String): Matrícula institucional única (ej. 'URC-2024-0412').\n"
          "• telefono (String): Teléfono para alertas push y confirmaciones SMS.\n"
          "• rol (String): 'cliente' | 'cajero' | 'admin'.\n"
          "• turno_actual_id (String/ObjectId): ID del turno de caja activo (solo si rol=cajero).\n"
          "• nivel_seguridad (Integer): Nivel de privilegios jerárquicos (1=Estudiante, 2=Cajero, 5=Superadmin).")

    add_p("2. Colección 'categories' (Modelo: Categoria)", bold_prefix="Colección: ")
    add_p("• _id (ObjectId): Clave primaria NoSQL.\n"
          "• nombre (String): Nombre visible (Tortas & Plancha, Bebidas Grab & Go, Chilaquiles, Cafetería).\n"
          "• slug (String): Slug URL único.\n"
          "• area_despacho (String): 'Cocina' (Plancha KDS) o 'Mostrador' (Grab & Go < 30 seg).\n"
          "• icono (String): Identificador de ícono para la interfaz visual.\n"
          "• activa (Boolean): Visibilidad en menú.")

    add_p("3. Colección 'products' (Modelo: Producto)", bold_prefix="Colección: ")
    add_p("• _id (ObjectId): Clave primaria NoSQL.\n"
          "• sku (String): Código único de inventario (ej. 'URC-TRT-01', 'URC-BEB-01').\n"
          "• nombre (String): Nombre comercial del platillo o bebida.\n"
          "• categoria_id (ForeignKey): Referencia BSON a la categoría.\n"
          "• precio_venta (Decimal): Precio unitario en pesos mexicanos ($ MXN).\n"
          "• tiempo_prep (Integer): Tiempo estimado de elaboración en segundos (ej. 15s para agua, 420s para torta).\n"
          "• area_despacho (String): 'Mostrador' vs 'Cocina'.\n"
          "• opciones_personalizables (JSON Array): Lista de especificaciones seleccionables por el alumno (['Bien dorada', 'Con rajas', 'Sin cebolla', 'Queso extra']).\n"
          "• imagen_url (String): Emoji o URL fotográfica del producto.\n"
          "• activo (Boolean): Bandera de disponibilidad para la venta.")

    add_p("4. Colección 'inventory' (Modelo: Inventario)", bold_prefix="Colección: ")
    add_p("• _id (ObjectId): Clave primaria.\n"
          "• producto_id (OneToOneField): Referencia al producto en catálogo.\n"
          "• stock_actual (Integer): Existencias físicas contadas en almacén.\n"
          "• alerta_min (Integer): Umbral de reorden (por defecto 10 unidades). Cuando stock_actual <= alerta_min, el sistema dispara alerta visual en el panel del administrador.\n"
          "• fecha_reabastecimiento (DateTime): Timestamp del último ingreso de mercancía.\n"
          "• actualizado_en (DateTime): Timestamp de última transacción de descuento.")

    add_p("5. Colección 'orders' (Modelo: Pedido)", bold_prefix="Colección: ")
    add_p("• _id (ObjectId): Identificador BSON de comanda.\n"
          "• order_number (String): Turno secuencial visual (ej. '#URC-142').\n"
          "• cliente_id (ForeignKey): Referencia al documento del estudiante o docente.\n"
          "• cliente_nombre (String): Nombre del titular de la orden.\n"
          "• codigo_pin (String): Código PIN de retiro de 3 dígitos (ej. 'PIN-412').\n"
          "• estado (String): 'PENDING_PAYMENT' | 'PAID' | 'IN_PREPARATION' | 'READY_FOR_PICKUP' | 'DELIVERED' | 'CANCELLED'.\n"
          "• tipo_despacho (String): Segregación calculada ('Grab & Go' | 'Cocina Caliente' | 'Mixto').\n"
          "• items (EmbeddedModelArrayField): Arreglo de subdocumentos DetalleItem.\n"
          "• pago (EmbeddedModelField): Subdocumento PagoMercadoPago.\n"
          "• subtotal, total (Decimal): Montos consolidados calculados atómicamente.\n"
          "• origen (String): 'PWA Móvil' o 'Mostrador POS'.\n"
          "• cajero_id (String): Cajero operador (si se cobró presencialmente en caja).\n"
          "• tiempo_espera_estimado (Integer): Minutos estimados calculados según el ítem más lento.")

    add_p("6. Subdocumento Embebido: DetalleItem", bold_prefix="Subdocumento: ")
    add_p("• producto_id, sku, nombre_prod (String): Instantánea fija del artículo.\n"
          "• precio_unitario (Decimal): Precio de venta sellado en el momento exacto de la orden.\n"
          "• cantidad (Integer): Unidades solicitadas.\n"
          "• subtotal (Decimal): precio_unitario * cantidad.\n"
          "• area_despacho (String): 'Cocina' vs 'Mostrador'.\n"
          "• notas (String): Especificaciones del alumno (ej. 'Bien dorada, con rajas').")

    add_p("7. Subdocumento Embebido: PagoMercadoPago", bold_prefix="Subdocumento: ")
    add_p("• mp_payment_id (String): Identificador de transacción en la pasarela.\n"
          "• metodo_pago (String): 'QR_MERCADOPAGO' | 'SALDO_CUENTA' | 'TARJETA_DEBITO_CREDITO' | 'TRANSFERENCIA_SPEI' | 'EFECTIVO_CAJA'.\n"
          "• estatus (String): 'PENDING' | 'APPROVED' | 'REJECTED'.\n"
          "• monto (Decimal): Monto cobrado.\n"
          "• fecha_pago (DateTime): Fecha y hora de confirmación del webhook.")

    add_p("8. Colección 'shifts' (Modelo: TurnoCorte - Cortes Z)", bold_prefix="Colección: ")
    add_p("• _id (ObjectId): Clave primaria del turno.\n"
          "• cajero_id (ForeignKey): Cajero responsable del turno de caja.\n"
          "• fecha_apertura, fecha_cierre (DateTime): Registro de jornada.\n"
          "• fondo_inicial (Decimal): Fondo de cambio en efectivo otorgado al inicio (ej. $500.00 MXN).\n"
          "• ventas_efectivo_sistema (Decimal): Suma calculada por sistema de pedidos pagados en mostrador.\n"
          "• ventas_mercadopago_sistema (Decimal): Suma digital registrada por la pasarela.\n"
          "• total_esperado_caja (Decimal): fondo_inicial + ventas_efectivo_sistema.\n"
          "• total_global_facturado (Decimal): ventas_efectivo_sistema + ventas_mercadopago_sistema.\n"
          "• efectivo_declarado (Decimal): Efectivo físico contado e ingresado a ciegas por el cajero.\n"
          "• diferencia (Decimal): efectivo_declarado - total_esperado_caja (Desfasaje: 0.00 exacto, positivo=sobrante, negativo=faltante).\n"
          "• estado (String): 'ABIERTO' o 'CERRADO'.\n"
          "• notas_arqueo (String): Observaciones selladas.")

    # ==============================================================================
    # 6. MATRIZ DE ROLES Y SEGURIDAD RBAC
    # ==============================================================================
    add_header_h1("Matriz de Roles y Seguridad del Punto de Venta (RBAC)", icon="🛡️")

    add_p("Para blindar la integridad financiera del campus y erradicar pérdidas o mermas no autorizadas, el sistema implementa una matriz estricta de Roles y Privilegios (Role-Based Access Control - RBAC).")

    tbl_rbac = doc.add_table(rows=9, cols=4)
    tbl_rbac.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_rbac = ["Módulo / Función del Sistema", "Cliente (Estudiante/Docente)", "Cajero (Punto de Venta)", "Administrador General"]
    for j, h in enumerate(headers_rbac):
        cell = tbl_rbac.cell(0, j)
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        set_cell_borders(cell, sz=4)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    matrix_rows = [
        ("Explorar Catálogo y Precios", "Permitido", "Permitido", "Permitido"),
        ("Ordenar y Pagar vía Mercado Pago", "Permitido", "N/A", "Permitido"),
        ("Cobro Presencial en Caja (Efectivo/TPV)", "Denegado", "Permitido", "Permitido"),
        ("Cambiar Estado de Pedido (KDS Cocina)", "Denegado", "Permitido", "Permitido"),
        ("Visualizar Stock y Reabastecer Inventario", "Denegado", "DENEGADO (Bloqueo UI/API)", "Permitido"),
        ("Modificar Precios y Costos de Catálogo", "Denegado", "DENEGADO (Bloqueo UI/API)", "Permitido"),
        ("Generar Corte de Turno Personal (Corte Z)", "Denegado", "Permitido (Arqueo Ciego)", "Permitido"),
        ("Auditar Cortes Globales y Métrica Financiera", "Denegado", "Denegado", "Permitido"),
    ]

    for i, row in enumerate(matrix_rows, start=1):
        bg = HEX_BG_ALT if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            cell = tbl_rbac.cell(i, j)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            set_cell_borders(cell, sz=2)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8)
            if "DENEGADO" in val:
                r.font.bold = True
                r.font.color.rgb = COLOR_ROSE
            elif "Permitido" in val:
                r.font.color.rgb = COLOR_EMERALD
            else:
                r.font.color.rgb = COLOR_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ==============================================================================
    # 7. PASARELA DE PAGO: MERCADO PAGO Y AUTOMATIZACIÓN ZERO-TOUCH
    # ==============================================================================
    add_header_h1("Pasarela de Pago: Integración Mercado Pago vía Webhooks", icon="💳")

    add_p("Se seleccionó Mercado Pago como pasarela principal por su masiva penetración entre los jóvenes universitarios en México, permitiendo liquidar cuentas mediante:", bold_prefix="Justificación Técnica: ")
    add_p("• Saldo en cuenta Mercado Pago (débito instantáneo en un clic).")
    add_p("• Transferencias interbancarias SPEI sin costo ni comisión.")
    add_p("• Tarjetas de débito y crédito bancarias.")
    add_p("• Escaneo directo de Códigos QR colocados en las mesas y barras de la cafetería.")

    add_callout(
        "AUTOMATIZACIÓN ZERO-TOUCH:\n"
        "Al confirmarse el pago en la app de Mercado Pago, un webhook asíncrono impacta el endpoint `/api/mercadopago/webhook/` en el backend en Django. De manera totalmente desasistida, la transacción cambia el estado de la comanda a 'PAID', decrementa atómicamente el stock físico en MongoDB y dispara el sonido de campana de comanda en el KDS de cocina.",
        title="FLUJO ASÍNCRONO COMPLETAMENTE DESASISTIDO",
        border_hex=HEX_SECONDARY
    )

    # ==============================================================================
    # 8. PROCEDIMIENTO DE CORTE DE CAJA (CORTE Z) Y ARQUEO CIEGO
    # ==============================================================================
    add_header_h1("Procedimiento del Corte de Caja (Corte Z) y Arqueo Ciego", icon="🔒")

    add_p("Para transparentar cada peso recaudado y prevenir que los operadores de caja ajusten su declaración según lo esperado por el sistema, el software incorpora un módulo de ARQUEO CIEGO.")

    add_p("Al concluir su turno, la pantalla del cajero bloquea deliberadamente los totales calculados por el sistema. El operador únicamente dispone de un formulario donde debe contar físicamente los billetes y monedas de su cajón de dinero e ingresar el importe neto contable.")

    add_p("Al enviar la declaración ciega, el backend ejecuta la función `cerrar_con_arqueo_ciego()`, contrastando la declaración física contra las transacciones reales registradas en MongoDB, emitiendo la Póliza Consolidada de Corte Z:")

    # TABLA EJEMPLO DE CORTE Z
    tbl_corte = doc.add_table(rows=6, cols=2)
    tbl_corte.alignment = WD_TABLE_ALIGNMENT.CENTER
    corte_data = [
        ("Fondo de Cambio Inicial en Efectivo:", "$500.00 MXN"),
        ("Ventas Cobradas en Efectivo (Mostrador POS):", "$2,950.00 MXN"),
        ("Total Efectivo en Caja Esperado (Fondo + Ventas):", "$3,450.00 MXN"),
        ("Ventas Procesadas vía Mercado Pago (App / QR):", "$12,890.00 MXN (84 operaciones)"),
        ("TOTAL GLOBAL FACTURADO EN TURNO:", "$16,340.00 MXN"),
    ]
    for idx, (label, val) in enumerate(corte_data):
        c0 = tbl_corte.cell(idx, 0)
        c1 = tbl_corte.cell(idx, 1)
        c0.width = Inches(3.8)
        c1.width = Inches(3.0)
        set_cell_background(c0, "F8FAFC" if idx % 2 == 0 else "FFFFFF")
        set_cell_background(c1, "F8FAFC" if idx % 2 == 0 else "FFFFFF")
        set_cell_margins(c0, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c1, top=80, bottom=80, left=120, right=120)
        set_cell_borders(c0, sz=2)
        set_cell_borders(c1, sz=2)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.font.size = Pt(8.5)
        if "TOTAL GLOBAL" in label:
            r0.font.bold = True
            r0.font.color.rgb = COLOR_PRIMARY
        else:
            r0.font.color.rgb = COLOR_TEXT

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.size = Pt(8.5)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_AMBER if "TOTAL GLOBAL" in label else COLOR_PRIMARY

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ==============================================================================
    # 9. GUÍA PARA EXPOSICIÓN Y DEFENSA ANTE EL COMITÉ EVALUADOR
    # ==============================================================================
    add_header_h1("Guía de Exposición y Defensa ante el Comité Evaluador", icon="🎓")

    add_p("Para defender este proyecto ante el comité evaluador o las autoridades del campus de la Universidad Rosario Castellanos, se recomienda enfatizar los siguientes tres pilares estratégicos:")

    add_header_h2("Pilar 1: Impacto Directo en la Experiencia Estudiantil")
    add_p("Se erradican las filas de 14 a 15 minutos en recesos que solo duran 20 minutos. Los estudiantes no tienen que sacrificar su alimentación ni llegar tarde a sus materias. El pedido se lanza antes de concluir la sesión académica y se retira en barra en menos de 45 segundos con su código PIN.")

    add_header_h2("Pilar 2: Blindaje Financiero y Cero Pérdidas")
    add_p("Los cajeros no pueden alterar existencias ni modificar precios unitarios para encubrir mermas o faltantes. El arqueo ciego exige ingresar la cifra contada sin pistas en pantalla, lo que garantiza auditorías inalterables y conciliación transparente con la pasarela bancaria.")

    add_header_h2("Pilar 3: Escalabilidad Multi-Campus NoSQL")
    add_p("Gracias a la arquitectura en colecciones MongoDB y la flexibilidad de Django, el sistema está listo para replicarse de forma inmediata en las demás sedes de la Universidad Rosario Castellanos (Coyoacán, Azcapotzalco, Gustavo A. Madero) compartiendo el mismo núcleo tecnológico y base de datos distribuida en MongoDB Atlas.")

    # Guardar documento Word
    output_filename = "Documentacion_Analisis_Cafe_URC_Express.docx"
    doc.save(output_filename)
    print(f"Documento Word generado exitosamente: '{output_filename}' ({os.path.getsize(output_filename)} bytes)")

if __name__ == '__main__':
    build_urc_document()
