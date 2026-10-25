import os
import django
from decimal import Decimal
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from miapp.models import (
    Usuario, Categoria, Producto, Inventario, Pedido, TurnoCorte, DetalleItem, PagoMercadoPago
)

def poblar():
    print("Iniciando carga de datos maestros para Café URC Express...")

    # 1. Crear o actualizar Usuarios y Cuentas de Auth
    usuarios_data = [
        ('admin', 'admin1234', 'admin@urc.edu.mx', 'Lic. Fernando Rivas (Administrador General)', 'URC-ADM-001', 'admin', 5),
        ('cajero', 'cajero1234', 'caja1@urc.edu.mx', 'Juan Carlos Pérez (Cajero Mostrador)', 'URC-CAJ-104', 'cajero', 2),
        ('estudiante', 'estudiante1234', 'valeria.gomez@urc.edu.mx', 'Valeria Gómez Sánchez (Estudiante)', 'URC-2024-0412', 'cliente', 1),
        ('docente', 'docente1234', 'roberto.morales@urc.edu.mx', 'Dr. Roberto Morales (Docente)', 'URC-DOC-0821', 'cliente', 1),
    ]

    usuarios_obj = {}
    for username, pwd, email, nombre, mat, rol, seg in usuarios_data:
        u = User.objects.filter(username=username).first()
        if not u:
            if rol == 'admin':
                u = User.objects.create_superuser(username=username, email=email, password=pwd)
            else:
                u = User.objects.create_user(username=username, email=email, password=pwd)
            u.first_name = nombre.split()[0]
            u.save()
        else:
            u.set_password(pwd)
            u.save()

        perfil, _ = Usuario.objects.get_or_create(
            username=username,
            defaults={
                'user': u,
                'nombre_completo': nombre,
                'email': email,
                'matricula_urc': mat,
                'rol': rol,
                'nivel_seguridad': seg,
                'telefono': '5512345678'
            }
        )
        if perfil.user != u:
            perfil.user = u
            perfil.save()
        usuarios_obj[username] = perfil
        print(f" -> Usuario listo: {username} ({rol})")

    # 2. Categorías del Menú
    cat_data = [
        ('Tortas & Plancha', 'tortas-plancha', 'Cocina', 'bi-egg-fried', 'Tortas calientes preparadas en plancha al momento con ingredientes frescos.'),
        ('Chilaquiles & Desayunos', 'chilaquiles-desayunos', 'Cocina', 'bi-fire', 'Chilaquiles verdes y rojos con totopos dorados y acompañamientos.'),
        ('Cafetería de Especialidad', 'cafeteria', 'Cocina', 'bi-cup-hot', 'Expresso, capuchinos y café de grano con leche entera o deslactosada.'),
        ('Bebidas Embotelladas Grab & Go', 'bebidas-grab-go', 'Mostrador', 'bi-droplet-half', 'Aguas purificadas, refrescos y jugos fríos de retiro inmediato (< 30s).'),
        ('Dulces & Snacks Grab & Go', 'dulces-snacks', 'Mostrador', 'bi-basket2', 'Chocolates, papas y galletas listos en mostrador para armado rápido.'),
        ('Baguettes & Cuernitos', 'baguettes', 'Cocina', 'bi-badge-ad', 'Baguettes de jamón serrano, pavo y queso manchego al grill.'),
    ]

    cats_obj = {}
    for nombre, slug, area, icono, desc in cat_data:
        c, _ = Categoria.objects.update_or_create(
            slug=slug,
            defaults={
                'nombre': nombre,
                'area_despacho': area,
                'icono': icono,
                'descripcion': desc,
                'activa': True
            }
        )
        cats_obj[slug] = c
        print(f" -> Categoría lista: {nombre} [{area}]")

    # 3. Productos del Menú
    prod_data = [
        # Tortas
        ('URC-TRT-01', 'Torta de Milanesa con Queso', 'tortas-plancha', Decimal('58.00'), 420, 'Cocina',
         ["Bien dorada", "Con rajas en escabeche", "Con chipotle dulce", "Sin cebolla", "Queso Oaxaca extra +$10"],
         "🥪"),
        ('URC-TRT-02', 'Torta Cubana Gigante URC', 'tortas-plancha', Decimal('75.00'), 480, 'Cocina',
         ["Bien dorada", "Con rajas", "Con frijoles refritos", "Sin mayonesa"],
         "🥪"),
        ('URC-TRT-03', 'Torta de Jamón con Queso Manchego', 'tortas-plancha', Decimal('48.00'), 300, 'Cocina',
         ["Plancha bien caliente", "Con rajas", "Sin aguacate"],
         "🥪"),
        # Chilaquiles
        ('URC-CHL-01', 'Chilaquiles Verdes con Pollo Deshebrado', 'chilaquiles-desayunos', Decimal('65.00'), 450, 'Cocina',
         ["Salsa verde picante", "Con crema y queso fresco", "Sin cebolla morada", "Huevo estrellado extra +$12"],
         "🍳"),
        ('URC-CHL-02', 'Chilaquiles Rojos con Huevo al Gusto', 'chilaquiles-desayunos', Decimal('58.00'), 390, 'Cocina',
         ["Huevo estrellado tierno", "Huevo bien cocido", "Con frijoles refritos a un lado"],
         "🍳"),
        # Grab & Go - Bebidas (< 30s)
        ('URC-BEB-01', 'Agua Purificada Ciel 600ml', 'bebidas-grab-go', Decimal('18.00'), 15, 'Mostrador',
         ["Fría de refrigerador", "Al tiempo"],
         "💧"),
        ('URC-BEB-02', 'Coca-Cola Original 600ml', 'bebidas-grab-go', Decimal('24.00'), 15, 'Mostrador',
         ["Bien fría", "Con popote ecológico"],
         "🥤"),
        ('URC-BEB-03', 'Jugo Boing Mango Vidrio 500ml', 'bebidas-grab-go', Decimal('22.00'), 15, 'Mostrador',
         ["Frío"],
         "🧃"),
        # Grab & Go - Snacks (< 30s)
        ('URC-SNK-01', "Chocolate Hershey's con Almendras 40g", 'dulces-snacks', Decimal('26.00'), 10, 'Mostrador',
         [],
         "🍫"),
        ('URC-SNK-02', 'Galletas Chokis con Chispas de Chocolate', 'dulces-snacks', Decimal('20.00'), 10, 'Mostrador',
         [],
         "🍪"),
        ('URC-SNK-03', 'Papas Sabritas Original con Sal 45g', 'dulces-snacks', Decimal('25.00'), 10, 'Mostrador',
         ["Con salsa Botanera y limón", "Sin salsa"],
         "🥔"),
        # Cafetería
        ('URC-CAF-01', 'Café Americano Gourmet 12oz', 'cafeteria', Decimal('30.00'), 90, 'Cocina',
         ["Sin azúcar", "Con Splenda", "Con leche entera", "Con leche deslactosada"],
         "☕"),
        ('URC-CAF-02', 'Capuchino Italiano Vainilla 12oz', 'cafeteria', Decimal('42.00'), 150, 'Cocina',
         ["Canela espolvoreada", "Leche de almendras", "Doble shot expresso +$10"],
         "☕"),
        ('URC-CAF-03', 'Café Expresso Doble Intenso', 'cafeteria', Decimal('35.00'), 60, 'Cocina',
         ["Solo", "Cortado con espuma"],
         "☕"),
        # Baguettes
        ('URC-BAG-01', 'Baguette Pechuga de Pavo y Panela', 'baguettes', Decimal('62.00'), 360, 'Cocina',
         ["Pan crujiente al grill", "Con aderezo mostaza miel", "Sin jitomate"],
         "🥖"),
    ]

    for sku, nombre, cat_slug, precio, t_prep, area, opts, img in prod_data:
        p, _ = Producto.objects.update_or_create(
            sku=sku,
            defaults={
                'nombre': nombre,
                'categoria': cats_obj[cat_slug],
                'precio_venta': precio,
                'tiempo_prep': t_prep,
                'area_despacho': area,
                'opciones_personalizables': opts,
                'imagen_url': img,
                'activo': True,
                'descripcion': f"{nombre}. Preparado bajo estándares de higiene URC."
            }
        )

        # 4. Asignar inventario
        stock_init = 60
        if sku == 'URC-SNK-01':
            stock_init = 7  # Stock bajo intencional para probar alertas
        elif sku == 'URC-BEB-01':
            stock_init = 120

        Inventario.objects.update_or_create(
            producto=p,
            defaults={
                'stock_actual': stock_init,
                'alerta_min': 10,
                'fecha_reabastecimiento': timezone.now()
            }
        )
        print(f" -> Producto e Inventario listos: {sku} - {nombre} (Stock: {stock_init})")

    # 5. Turno de Caja Abierto
    cajero_user = usuarios_obj['cajero']
    turno, created = TurnoCorte.objects.get_or_create(
        cajero=cajero_user,
        estado='ABIERTO',
        defaults={
            'fondo_inicial': Decimal('500.00'),
            'total_esperado_caja': Decimal('500.00')
        }
    )
    print(f" -> Turno de Caja ID #{turno.id} activo para {cajero_user.nombre_completo}")

    # 6. Comandas iniciales de muestra
    prod_torta = Producto.objects.get(sku='URC-TRT-01')
    prod_agua = Producto.objects.get(sku='URC-BEB-01')
    prod_chokis = Producto.objects.get(sku='URC-SNK-02')
    prod_chilaquiles = Producto.objects.get(sku='URC-CHL-01')

    # Comanda 1: Grab & Go pagada con Mercado Pago en Mostrador Express
    if not Pedido.objects.filter(order_number='#URC-101').exists():
        p1 = Pedido.objects.create(
            order_number='#URC-101',
            cliente=usuarios_obj['estudiante'],
            cliente_nombre='Valeria Gómez (Estudiante)',
            codigo_pin='PIN-412',
            estado='READY_FOR_PICKUP',
            tipo_despacho='Grab & Go',
            subtotal=Decimal('38.00'),
            total=Decimal('38.00'),
            origen='PWA Móvil',
            tiempo_espera_estimado=1,
            items=[
                DetalleItem(
                    producto_id=str(prod_agua.id),
                    sku=prod_agua.sku,
                    nombre_prod=prod_agua.nombre,
                    precio_unitario=prod_agua.precio_venta,
                    cantidad=1,
                    subtotal=prod_agua.precio_venta,
                    area_despacho='Mostrador',
                    notas='Fría'
                ),
                DetalleItem(
                    producto_id=str(prod_chokis.id),
                    sku=prod_chokis.sku,
                    nombre_prod=prod_chokis.nombre,
                    precio_unitario=prod_chokis.precio_venta,
                    cantidad=1,
                    subtotal=prod_chokis.precio_venta,
                    area_despacho='Mostrador',
                    notas=''
                )
            ],
            pago=PagoMercadoPago(
                mp_payment_id='MP-20261021-99812',
                metodo_pago='QR_MERCADOPAGO',
                estatus='APPROVED',
                monto=Decimal('38.00'),
                fecha_pago=timezone.now()
            )
        )
        print(" -> Pedido muestra creado: #URC-101 (Listo para Retiro, PIN 412)")

    # Comanda 2: Cocina Caliente en preparación
    if not Pedido.objects.filter(order_number='#URC-102').exists():
        p2 = Pedido.objects.create(
            order_number='#URC-102',
            cliente=usuarios_obj['docente'],
            cliente_nombre='Dr. Roberto Morales (Docente)',
            codigo_pin='PIN-834',
            estado='IN_PREPARATION',
            tipo_despacho='Cocina Caliente',
            subtotal=Decimal('88.00'),
            total=Decimal('88.00'),
            origen='PWA Móvil',
            tiempo_espera_estimado=7,
            items=[
                DetalleItem(
                    producto_id=str(prod_torta.id),
                    sku=prod_torta.sku,
                    nombre_prod=prod_torta.nombre,
                    precio_unitario=prod_torta.precio_venta,
                    cantidad=1,
                    subtotal=prod_torta.precio_venta,
                    area_despacho='Cocina',
                    notas='Torta de milanesa, bien dorada, con rajas'
                ),
                DetalleItem(
                    producto_id=str(prod_agua.id),
                    sku=prod_agua.sku,
                    nombre_prod=prod_agua.nombre,
                    precio_unitario=prod_agua.precio_venta,
                    cantidad=1,
                    subtotal=prod_agua.precio_venta,
                    area_despacho='Mostrador',
                    notas='Al tiempo'
                )
            ],
            pago=PagoMercadoPago(
                mp_payment_id='MP-20261021-99855',
                metodo_pago='SALDO_CUENTA',
                estatus='APPROVED',
                monto=Decimal('88.00'),
                fecha_pago=timezone.now()
            )
        )
        print(" -> Pedido muestra creado: #URC-102 (Cocina Caliente, PIN 834)")

    # Comanda 3: Cobro en mostrador caja
    if not Pedido.objects.filter(order_number='#URC-103').exists():
        p3 = Pedido.objects.create(
            order_number='#URC-103',
            cliente=None,
            cliente_nombre='Alumno Mostrador',
            codigo_pin='PIN-195',
            estado='PAID',
            tipo_despacho='Cocina Caliente',
            subtotal=Decimal('65.00'),
            total=Decimal('65.00'),
            origen='Mostrador POS',
            cajero_id=str(cajero_user.id),
            tiempo_espera_estimado=6,
            items=[
                DetalleItem(
                    producto_id=str(prod_chilaquiles.id),
                    sku=prod_chilaquiles.sku,
                    nombre_prod=prod_chilaquiles.nombre,
                    precio_unitario=prod_chilaquiles.precio_venta,
                    cantidad=1,
                    subtotal=prod_chilaquiles.precio_venta,
                    area_despacho='Cocina',
                    notas='Con crema y salsa verde bien picosa'
                )
            ],
            pago=PagoMercadoPago(
                mp_payment_id='POS-20261021-1003',
                metodo_pago='EFECTIVO_CAJA',
                estatus='APPROVED',
                monto=Decimal('65.00'),
                fecha_pago=timezone.now()
            )
        )
        print(" -> Pedido muestra creado: #URC-103 (Cobro en Caja)")

    print("\n¡Base de datos 'cafeteria' en MongoDB poblada exitosamente!")

if __name__ == '__main__':
    poblar()
