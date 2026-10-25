import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

def draw_uml():
    fig, ax = plt.subplots(figsize=(26, 20), dpi=300)
    fig.patch.set_facecolor('#0B1120')
    ax.set_facecolor('#0B1120')
    ax.set_xlim(0, 26)
    ax.set_ylim(0, 20)
    ax.axis('off')

    # Paleta de colores Premium URC
    COLOR_BASE_HDR = '#F59E0B'      # Amber
    COLOR_CLIENTE_HDR = '#0EA5E9'   # Cyan
    COLOR_CAJERO_HDR = '#10B981'    # Emerald
    COLOR_ADMIN_HDR = '#8B5CF6'     # Purple
    COLOR_EMBED_HDR = '#0284C7'     # Sky Blue
    COLOR_SHIFT_HDR = '#EF4444'     # Rose Red
    COLOR_INV_HDR = '#D97706'       # Deep Amber

    BOX_BG = '#1E293B'
    BORDER_COLOR = 'rgba(255,255,255,0.15)'

    # Título Principal
    ax.text(13, 19.3, "CAFÉ URC EXPRESS: DIAGRAMA ESTRUCTURAL UML Y RELACIONES", 
            fontsize=20, weight='bold', ha='center', va='center', color='#F8FAFC', fontname='DejaVu Sans')
    ax.text(13, 18.7, "Universidad Rosario Castellanos • Arquitectura NoSQL MongoDB (Base: 'cafeteria') | RBAC & Mercado Pago", 
            fontsize=12, ha='center', va='center', color='#94A3B8', fontname='DejaVu Sans')

    def draw_box(x, y, w, h, title, stereotype, attrs, methods, hdr_color):
        # Card Body
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                             facecolor=BOX_BG, edgecolor='#475569', linewidth=1.5, zorder=2)
        ax.add_patch(box)

        # Card Header
        hdr_h = 1.1
        hdr = FancyBboxPatch((x, y + h - hdr_h), w, hdr_h, boxstyle="round,pad=0.02,rounding_size=0.15",
                             facecolor=hdr_color, edgecolor='#475569', linewidth=1.2, zorder=3)
        ax.add_patch(hdr)

        # Header Text
        ax.text(x + w/2, y + h - 0.35, stereotype, fontsize=8, weight='bold', ha='center', va='center', color='#0F172A', zorder=4)
        ax.text(x + w/2, y + h - 0.75, title, fontsize=12, weight='bold', ha='center', va='center', color='#0F172A', zorder=4)

        # Atributos
        curr_y = y + h - 1.45
        for a in attrs:
            ax.text(x + 0.3, curr_y, a, fontsize=8.5, color='#F8FAFC', fontname='DejaVu Sans', zorder=4)
            curr_y -= 0.32

        if methods:
            curr_y -= 0.15
            # Línea divisoria
            ax.plot([x + 0.2, x + w - 0.2], [curr_y + 0.15, curr_y + 0.15], color='#475569', lw=1, zorder=4)
            for m in methods:
                ax.text(x + 0.3, curr_y, m, fontsize=8.5, color='#38BDF8', fontname='DejaVu Sans', weight='bold', zorder=4)
                curr_y -= 0.32

    # 1. Clase Base: Usuario
    draw_box(9.5, 14.8, 7.0, 3.2, "Usuario", "<<Clase Base / users>>",
             ["- _id: ObjectId", "- nombre_completo: String", "- email: String", "- rol: String (cliente|cajero|admin)"],
             ["+ login()", "+ logout()"], COLOR_BASE_HDR)

    # 2. Subclases: Cliente, Cajero, Administrador
    draw_box(1.5, 10.2, 6.5, 3.4, "Cliente", "<<Herencia: Rol>>",
             ["- matriculaURC: String", "- telefono: String", "- pedidosActivos: Array"],
             ["+ crearPedido()", "+ pagarMercadoPago()", "+ consultarEstatus()"], COLOR_CLIENTE_HDR)

    draw_box(9.5, 10.2, 7.0, 3.4, "Cajero", "<<Herencia: Rol POS>>",
             ["- turnoActualId: ObjectId", "- totalEfectivoContado: Dbl"],
             ["+ registrarVentaPres()", "+ actualizarKDS()", "+ generarCorteZ_ArqueoCiego()"], COLOR_CAJERO_HDR)

    draw_box(17.8, 10.2, 6.7, 3.4, "Administrador", "<<Herencia: Rol Admin>>",
             ["- nivelSeguridad: Int (5)", "- privilegiosAuditoria: Bool"],
             ["+ reabastecerInventario()", "+ modificarPrecios()", "+ auditarCortesGlobales()"], COLOR_ADMIN_HDR)

    # Flechas de Herencia hacia Usuario
    ax.annotate('', xy=(12.0, 14.7), xytext=(4.75, 13.7),
                arrowprops=dict(facecolor='#94A3B8', edgecolor='#94A3B8', width=1.5, headwidth=8, headlength=8))
    ax.annotate('', xy=(13.0, 14.7), xytext=(13.0, 13.7),
                arrowprops=dict(facecolor='#94A3B8', edgecolor='#94A3B8', width=1.5, headwidth=8, headlength=8))
    ax.annotate('', xy=(14.0, 14.7), xytext=(21.15, 13.7),
                arrowprops=dict(facecolor='#94A3B8', edgecolor='#94A3B8', width=1.5, headwidth=8, headlength=8))

    # 3. Pedido (Colección orders)
    draw_box(1.5, 4.2, 6.8, 4.6, "Pedido", "<<Colección: orders>>",
             ["- orderNumber: String (#URC-XXX)", "- estado: String (PENDING..DELIVERED)", 
              "- codigoPIN: String (ej. PIN 412)", "- tipoDespacho: Grab&Go | Cocina",
              "- subtotal, total: Decimal", "- tiempoEsperaEstimado: Int", "- origen: PWA | Mostrador"],
             ["+ determinarRouting()", "+ validarPIN()"], COLOR_BASE_HDR)

    # 4. TurnoCorte (Colección shifts)
    draw_box(9.5, 4.2, 7.0, 4.6, "TurnoCorte", "<<Colección: shifts (Corte Z)>>",
             ["- cajero_id: ObjectId", "- fechaApertura, fechaCierre: Date",
              "- fondoInicial: Decimal ($500.00)", "- ventasEfectivoSistema: Decimal",
              "- ventasMPSistema: Decimal", "- totalEsperadoCaja: Decimal",
              "- efectivoDeclarado: Decimal (Arqueo)", "- diferencia: Decimal (Desfasaje)"],
             ["+ calcularMetricas()", "+ cerrarTurnoArqueoCiego()"], COLOR_SHIFT_HDR)

    # 5. Inventario & Producto
    draw_box(17.8, 5.8, 6.7, 3.0, "Inventario", "<<Colección: inventory>>",
             ["- producto_id: ObjectId", "- stockActual: Int", "- alertaMin: Int (10)", "- fechaReabastecimiento: Date"],
             ["+ descontar(cant)", "+ reabastecer(cant) [ADMIN]"], COLOR_INV_HDR)

    draw_box(17.8, 1.2, 6.7, 3.8, "Producto", "<<Colección: products>>",
             ["- sku: String (URC-TRT-01)", "- nombre: String", "- precioVenta: Decimal",
              "- tiempoPrep: Int (Segundos)", "- areaDespacho: Mostrador|Cocina", "- opciones: JSON (bien dorada..)"],
             ["+ esGrabAndGo(): Bool"], '#22C55E')

    # Subdocumentos Embebidos de Pedido
    draw_box(1.5, 0.4, 6.8, 2.8, "DetalleItem", "<<Subdocumento Embebido>>",
             ["- nombreProd: String", "- precioUnitario: Decimal (Snapshot)",
              "- cantidad: Int", "- subtotal: Decimal", "- notas: String ('Bien dorada, rajas')", "- areaDespacho: String"],
             None, COLOR_EMBED_HDR)

    draw_box(9.5, 0.4, 7.0, 2.8, "PagoMercadoPago", "<<Subdocumento Embebido>>",
             ["- mpPaymentId: String", "- metodoPago: QR|Saldo|Tarjeta|SPEI",
              "- estatus: APPROVED|PENDING", "- monto: Decimal", "- fechaPago: DateTime"],
             None, COLOR_EMBED_HDR)

    # Conectores y Cardinalidades
    # Cliente -> Pedido (1 a Muchos)
    ax.plot([4.75, 4.75], [10.2, 8.8], color='#38BDF8', lw=2)
    ax.text(5.0, 9.3, "1 emite 0..*", fontsize=8.5, color='#38BDF8', weight='bold')

    # Cajero -> TurnoCorte (1 a Muchos)
    ax.plot([13.0, 13.0], [10.2, 8.8], color='#10B981', lw=2)
    ax.text(13.2, 9.3, "1 opera 0..*", fontsize=8.5, color='#10B981', weight='bold')

    # Admin -> Inventario (1 audita y reabastece 1..*)
    ax.plot([21.15, 21.15], [10.2, 8.8], color='#8B5CF6', lw=2)
    ax.text(21.3, 9.3, "1 audita 1..*", fontsize=8.5, color='#8B5CF6', weight='bold')

    # Inventario -> Producto (1 a 1)
    ax.plot([21.15, 21.15], [5.8, 5.0], color='#D97706', lw=2)
    ax.text(21.3, 5.3, "1 a 1", fontsize=8.5, color='#D97706', weight='bold')

    # Pedido -> DetalleItem (Composición Embebida)
    ax.plot([4.9, 4.9], [4.2, 3.2], color='#0284C7', lw=2, linestyle='--')
    ax.text(5.1, 3.6, "Embebe 1..*", fontsize=8, color='#0284C7', weight='bold')

    # Pedido -> PagoMercadoPago (1 a 1 Embebido)
    ax.plot([8.3, 9.5], [6.5, 1.8], color='#0284C7', lw=2, linestyle=':')
    ax.text(8.5, 4.0, "1 a 1 Webhook", fontsize=8, color='#0284C7', weight='bold')

    plt.tight_layout()
    plt.savefig('uml_colecciones_mongodb.png', dpi=300, facecolor='#0B1120', edgecolor='none')
    print("Diagrama UML generado con éxito en 'uml_colecciones_mongodb.png'.")

if __name__ == '__main__':
    draw_uml()
