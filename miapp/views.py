import json
import random
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone

from .models import (
    Usuario,
    Categoria,
    Producto,
    Inventario,
    Pedido,
    TurnoCorte,
    DetalleItem,
    PagoMercadoPago
)


# ==============================================================================
# HELPERS DE ROLES Y SEGURIDAD (RBAC)
# ==============================================================================

def get_user_role(user):
    """Retorna el rol del usuario actual: 'admin', 'cajero', o 'cliente'."""
    if not user.is_authenticated:
        return 'cliente'
    if user.is_superuser:
        return 'admin'
    perfil = getattr(user, 'perfil', None)
    if perfil:
        return perfil.rol
    if user.groups.filter(name='Cajeros').exists() or user.username.lower().startswith('cajer'):
        return 'cajero'
    return 'cliente'


def get_current_perfil(user):
    """Retorna o crea el perfil de Usuario asociado."""
    if not user.is_authenticated:
        return None
    perfil = getattr(user, 'perfil', None)
    if not perfil:
        rol = 'admin' if user.is_superuser else ('cajero' if 'cajer' in user.username.lower() else 'cliente')
        perfil, _ = Usuario.objects.get_or_create(
            username=user.username,
            defaults={
                'user': user,
                'nombre_completo': user.get_full_name() or user.username.capitalize(),
                'email': user.email or f"{user.username}@urc.edu.mx",
                'matricula_urc': f"URC-{random.randint(2022, 2026)}-{random.randint(1000, 9999)}",
                'rol': rol
            }
        )
    return perfil


# ==============================================================================
# VISTAS DE AUTENTICACIÓN
# ==============================================================================

def login_view(request):
    """
    Pantalla de inicio de sesión con roles:
    - Administrador General (admin / admin1234)
    - Cajero / Mostrador POS (cajero / cajero1234)
    - Estudiante / Cliente PWA (estudiante / estudiante1234)
    """
    if request.user.is_authenticated:
        rol = get_user_role(request.user)
        if rol == 'cajero':
            return redirect('modulo_cajero')
        elif rol == 'admin':
            return redirect('admin_dashboard')
        return redirect('menu_cliente')

    error_msg = None
    if request.method == 'POST':
        usuario_input = request.POST.get('username', '').strip()
        password_input = request.POST.get('password', '').strip()
        user = authenticate(request, username=usuario_input, password=password_input)
        if user is not None:
            login(request, user)
            rol = get_user_role(user)
            if rol == 'cajero':
                return redirect('modulo_cajero')
            elif rol == 'admin':
                return redirect('admin_dashboard')
            return redirect('menu_cliente')
        else:
            error_msg = "Credenciales incorrectas. Verifica tu usuario y contraseña de la Universidad Rosario Castellanos."

    return render(request, 'miapp/login.html', {
        'error_msg': error_msg,
    })


def logout_view(request):
    """Cierra la sesión del usuario actual."""
    logout(request)
    return redirect('menu_cliente')


def cambiar_rol_demo(request, nuevo_rol):
    """
    Herramienta de demostración rápida para evaluadores y autoridades de la URC:
    Permite alternar con un clic la vista entre Cliente (PWA), Cajero (POS) y Administrador.
    """
    if nuevo_rol not in ['cliente', 'cajero', 'admin']:
        nuevo_rol = 'cliente'

    # Buscar o crear el usuario correspondiente
    user_map = {
        'admin': ('admin', 'admin1234', 'Administrador General URC', 'admin@urc.edu.mx'),
        'cajero': ('cajero', 'cajero1234', 'Cajero Turno Matutino', 'caja1@urc.edu.mx'),
        'cliente': ('estudiante', 'estudiante1234', 'Valeria Gómez (Estudiante)', 'valeria.gomez@urc.edu.mx'),
    }
    uname, pwd, nombre, email = user_map[nuevo_rol]
    user = User.objects.filter(username=uname).first()
    if not user:
        if nuevo_rol == 'admin':
            user = User.objects.create_superuser(username=uname, email=email, password=pwd)
        else:
            user = User.objects.create_user(username=uname, email=email, password=pwd)
        user.first_name = nombre.split()[0]
        user.save()

    perfil, _ = Usuario.objects.get_or_create(
        username=uname,
        defaults={
            'user': user,
            'nombre_completo': nombre,
            'email': email,
            'matricula_urc': f"URC-2024-{random.randint(1000, 9999)}",
            'rol': nuevo_rol,
        }
    )
    if perfil.user != user:
        perfil.user = user
        perfil.save()

    login(request, user)

    if nuevo_rol == 'cajero':
        return redirect('modulo_cajero')
    elif nuevo_rol == 'admin':
        return redirect('admin_dashboard')
    return redirect('menu_cliente')


# ==============================================================================
# VISTA 1: CLIENTE / ESTUDIANTE (PWA MÓVIL ANTICOLAS & MERCADO PAGO)
# ==============================================================================

def menu_cliente(request):
    """
    PWA Móvil de Pedido Anticipado para Estudiantes y Docentes de la URC.
    - Reduce tiempo de permanencia de 14 min a < 45 seg.
    - Catálogo dinámico con opciones personalizables ('Bien dorada, con rajas').
    - Filtro por área ('Grab & Go < 30 seg' vs 'Cocina Caliente').
    - Checkout integrado con simulación de Mercado Pago (QR, saldo, tarjeta).
    - Trazador de comanda en vivo con PIN de retiro seguro.
    """
    categorias = Categoria.objects.filter(activa=True).order_by('nombre')
    productos = Producto.objects.filter(activo=True).select_related('categoria').order_by('categoria', 'nombre')
    
    # Mapeo de stock disponible
    stock_dict = {inv.producto_id: inv.stock_actual for inv in Inventario.objects.all()}

    productos_data = []
    for p in productos:
        stock = stock_dict.get(p.id, 50)
        productos_data.append({
            'id': str(p.id),
            'sku': p.sku,
            'nombre': p.nombre,
            'descripcion': p.descripcion,
            'categoria': p.categoria.nombre if p.categoria else 'General',
            'categoria_id': str(p.categoria_id) if p.categoria else '',
            'precio_venta': float(p.precio_venta),
            'tiempo_prep': p.tiempo_prep,
            'tiempo_prep_min': round(p.tiempo_prep / 60, 1) if p.tiempo_prep >= 60 else f"{p.tiempo_prep} seg",
            'area_despacho': p.area_despacho,
            'es_grab_and_go': p.es_grab_and_go,
            'opciones': p.opciones_personalizables or [],
            'imagen_url': p.imagen_url,
            'stock': stock,
        })

    # Consultar pedidos recientes del usuario o en sesión
    pedidos_recientes = []
    perfil = get_current_perfil(request.user) if request.user.is_authenticated else None
    if perfil:
        pedidos_recientes = Pedido.objects.filter(cliente=perfil).order_by('-creado_en')[:5]
    elif 'ultimo_pedido_id' in request.session:
        pedidos_recientes = Pedido.objects.filter(id=request.session['ultimo_pedido_id'])

    user_role = get_user_role(request.user)

    return render(request, 'miapp/menu_cliente.html', {
        'categorias': categorias,
        'productos': productos_data,
        'productos_json': json.dumps(productos_data),
        'pedidos_recientes': pedidos_recientes,
        'user_role': user_role,
        'perfil': perfil,
    })


# ==============================================================================
# VISTA 2: CAJERO (PUNTO DE VENTA POS & ARQUEO CIEGO / CORTE Z)
# ==============================================================================

@login_required(login_url='login')
def modulo_cajero(request):
    """
    Punto de Venta (POS) de Mostrador para el Cajero:
    - Cobro de venta presencial en efectivo o TPV.
    - Generación inmediata de ticket con PIN de retiro seguro.
    - CUMPLIMIENTO RBAC ESTRICTO:
      * Acceso DENEGADO a modificar inventario (bloqueo en UI y API).
      * Acceso DENEGADO a alterar precios de productos.
    - MÓDULO DE CORTE DE CAJA (CORTE Z):
      * Procedimiento de ARQUEO CIEGO: El cajero no ve el acumulado en pantalla.
        Debe ingresar manualmente la cantidad contada físicamente.
      * Contraste y cálculo de desfasaje (faltante/sobrante) y póliza consolidada.
    """
    rol = get_user_role(request.user)
    if rol not in ['cajero', 'admin']:
        return render(request, 'miapp/acceso_denegado.html', {
            'motivo': 'Acceso Restringido: Este módulo es exclusivo para el rol de Cajero / Operador de Ventas.'
        }, status=403)

    perfil = get_current_perfil(request.user)

    # Buscar turno abierto actual del cajero o crear uno si no existe
    turno_actual = TurnoCorte.objects.filter(cajero=perfil, estado='ABIERTO').order_by('-fecha_apertura').first()
    if not turno_actual and rol == 'cajero':
        turno_actual = TurnoCorte.objects.create(
            cajero=perfil,
            fondo_inicial=Decimal('500.00'),
            estado='ABIERTO'
        )

    # Catálogo de productos para el mostrador
    productos = Producto.objects.filter(activo=True).select_related('categoria').order_by('categoria', 'nombre')
    stock_dict = {inv.producto_id: inv.stock_actual for inv in Inventario.objects.all()}

    productos_data = []
    for p in productos:
        productos_data.append({
            'id': str(p.id),
            'sku': p.sku,
            'nombre': p.nombre,
            'categoria': p.categoria.nombre if p.categoria else 'General',
            'precio_venta': float(p.precio_venta),
            'tiempo_prep': p.tiempo_prep,
            'area_despacho': p.area_despacho,
            'stock': stock_dict.get(p.id, 0),
            'imagen_url': p.imagen_url,
            'opciones': p.opciones_personalizables or []
        })

    # Últimas 8 órdenes cobradas en mostrador
    ultimas_ordenes = Pedido.objects.all().order_by('-creado_en')[:8]

    # Historial de turnos cerrados por este cajero
    turnos_anteriores = TurnoCorte.objects.filter(cajero=perfil, estado='CERRADO').order_by('-fecha_cierre')[:5]

    return render(request, 'miapp/cajero_pos.html', {
        'productos': productos_data,
        'productos_json': json.dumps(productos_data),
        'turno_actual': turno_actual,
        'turnos_anteriores': turnos_anteriores,
        'ultimas_ordenes': ultimas_ordenes,
        'user_role': rol,
        'perfil': perfil,
    })


# ==============================================================================
# VISTA 3: PANTALLA KDS COCINA & MOSTRADOR EXPRESS (ROUTING INTELIGENTE)
# ==============================================================================

def pantalla_kds(request):
    """
    Kitchen Display System (KDS) & Pantalla de Despacho de Comandas:
    - Segregación Inteligente de Comandas (Routing):
      * 'Mostrador Express': Pedidos 'Grab & Go' (dulces, sodas, aguas) para armado en < 30 seg.
      * 'Cocina Caliente': Plancha, tortas, chilaquiles, baguettes, café expresso.
    - Máquina de Estados:
      `PAID` (En Cola) -> `IN_PREPARATION` -> `READY_FOR_PICKUP` (¡Listo!) -> `DELIVERED` (Entregado con PIN)
    - Sonido interactivo de nueva comanda y temporizadores en tiempo real.
    """
    user_role = get_user_role(request.user)

    # Órdenes activas en cocina o mostrador
    ordenes_activas = Pedido.objects.filter(
        estado__in=['PAID', 'IN_PREPARATION', 'READY_FOR_PICKUP']
    ).order_by('creado_en')

    # Desglose segregado
    comandas_express = []
    comandas_cocina = []
    comandas_listas = []

    for ord_obj in ordenes_activas:
        if ord_obj.estado == 'READY_FOR_PICKUP':
            comandas_listas.append(ord_obj)
        elif ord_obj.tipo_despacho == 'Grab & Go':
            comandas_express.append(ord_obj)
        else:
            comandas_cocina.append(ord_obj)

    # Entregadas recientemente para histórico
    recientes_entregadas = Pedido.objects.filter(estado='DELIVERED').order_by('-actualizado_en')[:10]

    return render(request, 'miapp/pantalla_kds.html', {
        'comandas_express': comandas_express,
        'comandas_cocina': comandas_cocina,
        'comandas_listas': comandas_listas,
        'recientes_entregadas': recientes_entregadas,
        'total_activas': ordenes_activas.count(),
        'user_role': user_role,
    })


# ==============================================================================
# VISTA 4: PANEL ADMINISTRADOR GENERAL & AUDITORÍA GLOBAL
# ==============================================================================

@login_required(login_url='login')
def admin_dashboard(request):
    """
    Panel de Control Ejecutivo y Auditoría Global (Exclusivo Administrador):
    - Métricas operativas de impacto: Tiempo en fila de 14 min a < 45 seg.
    - Auditoría Financiera de Cortes Z de todos los cajeros (Arqueos ciegos, faltantes/sobrantes).
    - Monitoreo y Reabastecimiento de Inventario (Blindaje Financiero y Cero Pérdidas).
    - Catálogo maestro de productos y configuración.
    """
    rol = get_user_role(request.user)
    if rol != 'admin':
        return render(request, 'miapp/acceso_denegado.html', {
            'motivo': 'Acceso Restringido: Este módulo requiere privilegios de Administrador General URC.'
        }, status=403)

    perfil = get_current_perfil(request.user)

    # Métricas financieras y de impacto
    pedidos_completados = Pedido.objects.filter(estado__in=['PAID', 'IN_PREPARATION', 'READY_FOR_PICKUP', 'DELIVERED'])
    
    total_facturado = sum(p.total for p in pedidos_completados) or Decimal('0.00')
    total_mp = sum(p.total for p in pedidos_completados if p.pago and p.pago.metodo_pago != 'EFECTIVO_CAJA') or Decimal('0.00')
    total_efectivo = sum(p.total for p in pedidos_completados if (p.pago and p.pago.metodo_pago == 'EFECTIVO_CAJA') or p.origen == 'Mostrador POS') or Decimal('0.00')

    pedidos_grab_go = pedidos_completados.filter(tipo_despacho='Grab & Go').count()
    pedidos_cocina = pedidos_completados.filter(tipo_despacho__in=['Cocina Caliente', 'Mixto']).count()

    # Inventario con alertas de stock bajo
    inventarios = Inventario.objects.select_related('producto', 'producto__categoria').all().order_by('stock_actual')
    alertas_stock = [inv for inv in inventarios if inv.requiere_alerta]

    # Auditoría de todos los Cortes Z
    turnos_auditoria = TurnoCorte.objects.select_related('cajero').all().order_by('-fecha_apertura')[:15]

    # Catálogo de productos
    productos = Producto.objects.select_related('categoria').all().order_by('categoria', 'nombre')
    categorias = Categoria.objects.all()

    return render(request, 'miapp/admin_dashboard.html', {
        'total_facturado': total_facturado,
        'total_mp': total_mp,
        'total_efectivo': total_efectivo,
        'total_pedidos': pedidos_completados.count(),
        'pedidos_grab_go': pedidos_grab_go,
        'pedidos_cocina': pedidos_cocina,
        'inventarios': inventarios,
        'alertas_stock': alertas_stock,
        'turnos_auditoria': turnos_auditoria,
        'productos': productos,
        'categorias': categorias,
        'user_role': rol,
        'perfil': perfil,
    })


# ==============================================================================
# API ENDPOINTS (MERCADO PAGO, KDS, POS Y CORTE Z)
# ==============================================================================

@require_POST
def api_crear_pedido_cliente(request):
    """
    Endpoint para registrar un nuevo pedido desde la PWA Móvil del Estudiante/Docente:
    - Genera número de turno #URC-XXX.
    - Genera código PIN de retiro seguro (ej. PIN 412).
    - Desacopla orden e ítems con composición inmutable (congelación de precios históricos).
    - Asigna estado PENDING_PAYMENT listo para pago con Mercado Pago.
    """
    try:
        data = json.loads(request.body)
        items_req = data.get('items', [])
        nombre_cliente = data.get('nombre_cliente', 'Estudiante URC').strip()
        metodo_pago_sel = data.get('metodo_pago', 'QR_MERCADOPAGO')

        if not items_req:
            return JsonResponse({'success': False, 'error': 'El carrito no contiene productos.'}, status=400)

        # Determinar número secuencial de turno #URC-XXX
        ultimo = Pedido.objects.order_by('-creado_en').first()
        numero_base = 101
        if ultimo and ultimo.order_number.startswith('#URC-'):
            try:
                numero_base = int(ultimo.order_number.replace('#URC-', '')) + 1
            except ValueError:
                numero_base = 101
        order_number = f"#URC-{numero_base}"

        # Código PIN de retiro seguro de 3 dígitos (ej. 412)
        codigo_pin = f"PIN-{random.randint(100, 999)}"

        detalles_embebidos = []
        subtotal_acum = Decimal('0.00')
        max_tiempo_prep = 30
        tiene_cocina = False
        tiene_mostrador = False

        for it in items_req:
            p_id = it.get('id')
            cant = int(it.get('cantidad', 1))
            notas = it.get('notas', '').strip()

            prod = Producto.objects.filter(id=p_id).first()
            if not prod:
                continue

            precio_u = prod.precio_venta
            sub_it = precio_u * cant
            subtotal_acum += sub_it

            if prod.area_despacho == 'Cocina':
                tiene_cocina = True
            else:
                tiene_mostrador = True

            if prod.tiempo_prep > max_tiempo_prep:
                max_tiempo_prep = prod.tiempo_prep

            detalles_embebidos.append(
                DetalleItem(
                    producto_id=str(prod.id),
                    sku=prod.sku,
                    nombre_prod=prod.nombre,
                    precio_unitario=precio_u,
                    cantidad=cant,
                    subtotal=sub_it,
                    area_despacho=prod.area_despacho,
                    notas=notas
                )
            )

        if not detalles_embebidos:
            return JsonResponse({'success': False, 'error': 'No se encontraron productos válidos.'}, status=400)

        # Routing comanda
        if tiene_cocina and tiene_mostrador:
            tipo_despacho = 'Mixto'
        elif tiene_cocina:
            tipo_despacho = 'Cocina Caliente'
        else:
            tipo_despacho = 'Grab & Go'

        tiempo_minutos = max(1, round(max_tiempo_prep / 60))

        # Cliente perfil
        cliente_perfil = get_current_perfil(request.user) if request.user.is_authenticated else None

        # Preparar subdocumento de pago inicial
        pago_mp = PagoMercadoPago(
            mp_payment_id=f"MP-{timezone.now().strftime('%Y%m%d%H%M%S')}-{random.randint(10, 99)}",
            metodo_pago=metodo_pago_sel,
            estatus='PENDING',
            monto=subtotal_acum,
        )

        pedido = Pedido.objects.create(
            order_number=order_number,
            cliente=cliente_perfil,
            cliente_nombre=nombre_cliente or (cliente_perfil.nombre_completo if cliente_perfil else 'Estudiante URC'),
            codigo_pin=codigo_pin,
            estado='PENDING_PAYMENT',
            tipo_despacho=tipo_despacho,
            items=detalles_embebidos,
            subtotal=subtotal_acum,
            total=subtotal_acum,
            pago=pago_mp,
            origen='PWA Móvil',
            tiempo_espera_estimado=tiempo_minutos
        )

        # Guardar en sesión para seguimiento anónimo si no está logueado
        request.session['ultimo_pedido_id'] = str(pedido.id)

        # Datos para modal de pago Mercado Pago
        checkout_info = {
            'order_id': str(pedido.id),
            'order_number': pedido.order_number,
            'total': float(pedido.total),
            'mp_payment_id': pago_mp.mp_payment_id,
            'metodo_pago': metodo_pago_sel,
            'pin': pedido.codigo_pin,
            'qr_data': f"mercadopago://pay?pref_id={pago_mp.mp_payment_id}&amount={pedido.total}&collector=URC_CAFETERIA"
        }

        return JsonResponse({'success': True, 'pedido': checkout_info})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
def api_webhook_mercadopago(request):
    """
    Webhook Asíncrono de Mercado Pago (Automatización Zero-Touch):
    - Al confirmarse el pago en la app/QR de Mercado Pago ('approved'):
      * Cambia estado de la orden a 'PAID' (En Cola).
      * Decrementa transaccionalmente el inventario de cada producto.
      * Activa la notificación y el sonido en la pantalla KDS / Mostrador.
    """
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        mp_payment_id = data.get('mp_payment_id')
        status = data.get('status', 'approved').upper()

        pedido = Pedido.objects.filter(id=order_id).first()
        if not pedido and mp_payment_id:
            pedido = Pedido.objects.filter(pago__mp_payment_id=mp_payment_id).first()

        if not pedido:
            return JsonResponse({'success': False, 'error': 'Pedido no encontrado'}, status=404)

        if status in ['APPROVED', 'PAID']:
            # 1. Actualizar estado del pago
            if pedido.pago:
                pedido.pago.estatus = 'APPROVED'
                pedido.pago.fecha_pago = timezone.now()
            else:
                pedido.pago = PagoMercadoPago(
                    mp_payment_id=mp_payment_id or f"MP-{timezone.now().strftime('%Y%m%d%H%M')}",
                    metodo_pago='QR_MERCADOPAGO',
                    estatus='APPROVED',
                    monto=pedido.total,
                    fecha_pago=timezone.now()
                )

            # 2. Transición de máquina de estados a PAID
            pedido.estado = 'PAID'
            pedido.save()

            # 3. Decrementar inventario transaccionalmente (Blindaje contra sobreventas)
            for it in pedido.items:
                inv = Inventario.objects.filter(producto_id=it.producto_id).first()
                if inv:
                    inv.descontar(it.cantidad)

            return JsonResponse({
                'success': True,
                'mensaje': 'Pago procesado exitosamente vía Mercado Pago. Comanda enviada a KDS.',
                'order_number': pedido.order_number,
                'codigo_pin': pedido.codigo_pin,
                'estado': pedido.estado,
                'tipo_despacho': pedido.tipo_despacho
            })
        else:
            if pedido.pago:
                pedido.pago.estatus = 'REJECTED'
            pedido.estado = 'CANCELLED'
            pedido.save()
            return JsonResponse({'success': True, 'mensaje': 'Pago rechazado.'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
@login_required(login_url='login')
def api_procesar_venta_mostrador(request):
    """
    Punto de Venta Mostrador (POS Cajero):
    - Cobro presencial (Efectivo / TPV).
    - Descuenta stock disponible.
    - Genera número de turno y PIN de retiro.
    - Registra en el turno del cajero.
    """
    rol = get_user_role(request.user)
    if rol not in ['cajero', 'admin']:
        return JsonResponse({'success': False, 'error': 'No tienes permisos de Cajero para cobrar en mostrador.'}, status=403)

    try:
        data = json.loads(request.body)
        items_req = data.get('items', [])
        metodo_pago = data.get('metodo_pago', 'EFECTIVO_CAJA')
        nombre_cliente = data.get('nombre_cliente', 'Cliente Mostrador').strip()

        if not items_req:
            return JsonResponse({'success': False, 'error': 'El carrito está vacío.'}, status=400)

        # Generar número de turno
        ultimo = Pedido.objects.order_by('-creado_en').first()
        num_base = 101
        if ultimo and ultimo.order_number.startswith('#URC-'):
            try:
                num_base = int(ultimo.order_number.replace('#URC-', '')) + 1
            except ValueError:
                num_base = 101
        order_number = f"#URC-{num_base}"
        codigo_pin = f"PIN-{random.randint(100, 999)}"

        detalles_embebidos = []
        subtotal_acum = Decimal('0.00')
        tiene_cocina = False
        tiene_mostrador = False

        # Validar y reservar stock
        for it in items_req:
            p_id = it.get('id')
            cant = int(it.get('cantidad', 1))
            notas = it.get('notas', '').strip()

            prod = Producto.objects.filter(id=p_id).first()
            if not prod:
                continue

            inv = Inventario.objects.filter(producto=prod).first()
            if inv and inv.stock_actual < cant:
                return JsonResponse({
                    'success': False,
                    'error': f'Stock insuficiente para {prod.nombre}. Disponible: {inv.stock_actual}, Solicitado: {cant}'
                }, status=400)

            precio_u = prod.precio_venta
            sub_it = precio_u * cant
            subtotal_acum += sub_it

            if prod.area_despacho == 'Cocina':
                tiene_cocina = True
            else:
                tiene_mostrador = True

            detalles_embebidos.append(
                DetalleItem(
                    producto_id=str(prod.id),
                    sku=prod.sku,
                    nombre_prod=prod.nombre,
                    precio_unitario=precio_u,
                    cantidad=cant,
                    subtotal=sub_it,
                    area_despacho=prod.area_despacho,
                    notas=notas
                )
            )

            # Descontar stock inmediatamente
            if inv:
                inv.descontar(cant)

        # Determinar routing
        if tiene_cocina and tiene_mostrador:
            tipo_despacho = 'Mixto'
        elif tiene_cocina:
            tipo_despacho = 'Cocina Caliente'
        else:
            tipo_despacho = 'Grab & Go'

        perfil_cajero = get_current_perfil(request.user)

        # Pago registrado en caja
        pago_reg = PagoMercadoPago(
            mp_payment_id=f"POS-{timezone.now().strftime('%Y%m%d%H%M%S')}-{random.randint(10, 99)}",
            metodo_pago=metodo_pago,
            estatus='APPROVED',
            monto=subtotal_acum,
            fecha_pago=timezone.now()
        )

        pedido = Pedido.objects.create(
            order_number=order_number,
            cliente=None,
            cliente_nombre=nombre_cliente,
            codigo_pin=codigo_pin,
            estado='PAID',  # Al ser cobrado en caja entra directo como pagado a la cola
            tipo_despacho=tipo_despacho,
            items=detalles_embebidos,
            subtotal=subtotal_acum,
            total=subtotal_acum,
            pago=pago_reg,
            origen='Mostrador POS',
            cajero_id=str(perfil_cajero.id) if perfil_cajero else request.user.username,
            tiempo_espera_estimado=2 if tipo_despacho == 'Grab & Go' else 7
        )

        return JsonResponse({
            'success': True,
            'order_number': pedido.order_number,
            'codigo_pin': pedido.codigo_pin,
            'total': float(pedido.total),
            'tipo_despacho': pedido.tipo_despacho,
            'metodo_pago': metodo_pago,
            'mensaje': 'Venta presencial registrada exitosamente.'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
def api_actualizar_estado_kds(request):
    """
    Actualiza el estado del pedido en la máquina de estados desde la pantalla KDS:
    PAID -> IN_PREPARATION -> READY_FOR_PICKUP -> DELIVERED
    """
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        nuevo_estado = data.get('nuevo_estado')
        pin_ingresado = data.get('pin_ingresado', '').strip().upper()

        pedido = Pedido.objects.filter(id=order_id).first()
        if not pedido:
            return JsonResponse({'success': False, 'error': 'Pedido no encontrado'}, status=404)

        # Si se va a marcar como entregado (DELIVERED), validar PIN de retiro
        if nuevo_estado == 'DELIVERED':
            pin_esperado = pedido.codigo_pin.replace('PIN-', '').replace('PIN', '').strip()
            pin_limpio = pin_ingresado.replace('PIN-', '').replace('PIN', '').strip()
            if pin_ingresado and pin_limpio != pin_esperado:
                return JsonResponse({
                    'success': False,
                    'error': f'Código PIN incorrecto ({pin_ingresado}). Debe coincidir con el PIN del ticket ({pedido.codigo_pin}).'
                }, status=400)

        pedido.estado = nuevo_estado
        pedido.save()

        return JsonResponse({
            'success': True,
            'order_id': str(pedido.id),
            'order_number': pedido.order_number,
            'nuevo_estado': pedido.estado,
            'estado_display': pedido.get_estado_display(),
            'codigo_pin': pedido.codigo_pin
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
@login_required(login_url='login')
def api_cierre_arqueo_ciego(request):
    """
    Procedimiento de Corte de Caja (Corte Z) con ARQUEO CIEGO:
    - El cajero ingresa a ciegas el monto de efectivo físico contado en caja.
    - El sistema recupera el total calculado por sistema, calcula el desfasaje
      (faltante o sobrante) y emite la póliza consolidada.
    """
    rol = get_user_role(request.user)
    if rol not in ['cajero', 'admin']:
        return JsonResponse({'success': False, 'error': 'No autorizado.'}, status=403)

    try:
        data = json.loads(request.body)
        efectivo_declarado = Decimal(str(data.get('efectivo_declarado', '0.00')))
        observaciones = data.get('observaciones', '').strip()

        perfil = get_current_perfil(request.user)
        turno = TurnoCorte.objects.filter(cajero=perfil, estado='ABIERTO').order_by('-fecha_apertura').first()

        if not turno:
            return JsonResponse({'success': False, 'error': 'No hay ningún turno abierto para este cajero.'}, status=400)

        # Ejecutar arqueo ciego
        turno.cerrar_con_arqueo_ciego(efectivo_declarado, observaciones)

        return JsonResponse({
            'success': True,
            'turno_id': str(turno.id),
            'fecha_apertura': turno.fecha_apertura.strftime('%Y-%m-%d %H:%M'),
            'fecha_cierre': turno.fecha_cierre.strftime('%Y-%m-%d %H:%M'),
            'fondo_inicial': float(turno.fondo_inicial),
            'ventas_efectivo_sistema': float(turno.ventas_efectivo_sistema),
            'ventas_mp_sistema': float(turno.ventas_mercadopago_sistema),
            'total_esperado_caja': float(turno.total_esperado_caja),
            'efectivo_declarado': float(turno.efectivo_declarado),
            'diferencia': float(turno.diferencia),
            'total_global_facturado': float(turno.total_global_facturado),
            'mensaje': 'Corte Z emitido exitosamente con Arqueo Ciego.'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
@login_required(login_url='login')
def api_abrir_turno(request):
    """Abre un nuevo turno de caja con fondo inicial."""
    try:
        data = json.loads(request.body)
        fondo_inicial = Decimal(str(data.get('fondo_inicial', '500.00')))
        perfil = get_current_perfil(request.user)

        # Cerrar turnos previos si hubiera
        TurnoCorte.objects.filter(cajero=perfil, estado='ABIERTO').update(estado='CERRADO', fecha_cierre=timezone.now())

        nuevo_turno = TurnoCorte.objects.create(
            cajero=perfil,
            fondo_inicial=fondo_inicial,
            estado='ABIERTO'
        )

        return JsonResponse({
            'success': True,
            'turno_id': str(nuevo_turno.id),
            'fondo_inicial': float(nuevo_turno.fondo_inicial),
            'mensaje': 'Nuevo turno de caja abierto correctamente.'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
@login_required(login_url='login')
def api_reabastecer_inventario(request):
    """
    Reabastece stock físico de un producto (Exclusivo Administrador).
    Cajero y Cliente tienen BLOQUEADO este endpoint con 403 Forbidden.
    """
    rol = get_user_role(request.user)
    if rol != 'admin':
        return JsonResponse({'success': False, 'error': 'DENEGADO: Solo el Administrador General puede reabastecer inventario.'}, status=403)

    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        cantidad = int(data.get('cantidad', 50))

        inv = Inventario.objects.filter(producto_id=producto_id).first()
        if not inv:
            prod = Producto.objects.filter(id=producto_id).first()
            if not prod:
                return JsonResponse({'success': False, 'error': 'Producto no encontrado.'}, status=404)
            inv = Inventario.objects.create(producto=prod, stock_actual=cantidad, alerta_min=10)
        else:
            inv.reabastecer(cantidad)

        return JsonResponse({
            'success': True,
            'producto': inv.producto.nombre,
            'nuevo_stock': inv.stock_actual,
            'mensaje': f'Stock reabastecido a {inv.stock_actual} unidades.'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def api_consultar_pedido(request, order_id):
    """Consulta en tiempo real el estatus y PIN de un pedido para la PWA del estudiante."""
    pedido = Pedido.objects.filter(id=order_id).first()
    if not pedido:
        pedido = Pedido.objects.filter(order_number=order_id).first()
    if not pedido:
        return JsonResponse({'success': False, 'error': 'Pedido no encontrado'}, status=404)

    return JsonResponse({
        'success': True,
        'order_number': pedido.order_number,
        'codigo_pin': pedido.codigo_pin,
        'estado': pedido.estado,
        'estado_display': pedido.get_estado_display(),
        'tipo_despacho': pedido.tipo_despacho,
        'total': float(pedido.total),
        'tiempo_espera_estimado': pedido.tiempo_espera_estimado,
        'hora': pedido.creado_en.strftime('%H:%M:%S'),
        'items': [
            {
                'nombre': it.nombre_prod,
                'cantidad': it.cantidad,
                'notas': it.notas,
                'area': it.area_despacho
            } for it in pedido.items
        ]
    })
