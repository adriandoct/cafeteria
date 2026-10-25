from decimal import Decimal
from django.db import models
from django.utils import timezone
from django_mongodb_backend.models import EmbeddedModel
from django_mongodb_backend.fields import EmbeddedModelField, EmbeddedModelArrayField


# ==============================================================================
# SUBDOCUMENTOS EMBEBIDOS (MongoDB NoSQL)
# ==============================================================================

class DetalleItem(EmbeddedModel):
    """
    Subdocumento embebido: Composición inmutable dentro del documento Pedido.
    Cuando el cliente compra una torta a $55.00 con notas específicas, ese precio
    y sus notas de cocina quedan congelados dentro del pedido.
    Futuros incrementos de precio no adulteran auditorías pasadas.
    """
    producto_id = models.CharField(max_length=100, verbose_name="ID Producto")
    sku = models.CharField(max_length=50, verbose_name="SKU")
    nombre_prod = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario ($)")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal ($)")
    area_despacho = models.CharField(
        max_length=30,
        default='Mostrador',
        verbose_name="Área de Despacho (Cocina / Mostrador)"
    )
    notas = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Notas / Especificaciones (ej. 'Bien dorada, con rajas')"
    )

    class Meta:
        app_label = 'miapp'
        verbose_name = "Detalle de Ítem Embebido"
        verbose_name_plural = "Detalles de Ítems"

    def __str__(self):
        nota_str = f" [{self.notas}]" if self.notas else ""
        return f"{self.cantidad}x {self.nombre_prod} (${self.precio_unitario}){nota_str}"


class PagoMercadoPago(EmbeddedModel):
    """
    Subdocumento embebido: Registro transaccional de Mercado Pago.
    Permite cobro mediante Saldo Mercado Pago, SPEI, QR y Tarjetas bancarias.
    Automatización Zero-Touch: Al confirmarse el webhook, se marca como APPROVED.
    """
    METODOS_PAGO = [
        ('QR_MERCADOPAGO', 'Código QR Mercado Pago'),
        ('SALDO_CUENTA', 'Saldo en Cuenta Mercado Pago'),
        ('TARJETA_DEBITO_CREDITO', 'Tarjeta de Débito / Crédito'),
        ('TRANSFERENCIA_SPEI', 'Transferencia SPEI Directa'),
        ('EFECTIVO_CAJA', 'Efectivo en Mostrador (Caja)'),
    ]

    ESTADOS_PAGO = [
        ('PENDING', 'Pendiente de Validación'),
        ('APPROVED', 'Aprobado / Conciliado'),
        ('REJECTED', 'Rechazado'),
    ]

    mp_payment_id = models.CharField(max_length=100, verbose_name="ID Transacción Mercado Pago")
    metodo_pago = models.CharField(max_length=50, choices=METODOS_PAGO, default='QR_MERCADOPAGO', verbose_name="Método de Pago")
    estatus = models.CharField(max_length=30, choices=ESTADOS_PAGO, default='PENDING', verbose_name="Estatus Pasarela")
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Monto Cobrado ($)")
    fecha_pago = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Autorización")

    class Meta:
        app_label = 'miapp'
        verbose_name = "Pago Mercado Pago"
        verbose_name_plural = "Pagos Mercado Pago"

    def __str__(self):
        return f"{self.mp_payment_id} ({self.metodo_pago}) - ${self.monto} [{self.estatus}]"


# ==============================================================================
# COLECCIONES PRINCIPALES (MongoDB - Base de Datos 'cafeteria')
# ==============================================================================

class Usuario(models.Model):
    """
    Colección: 'users'
    Almacena credenciales, matrícula URC, teléfono, correo institucional y rol asignado.
    Soporta herencia lógica de actores: Cliente, Cajero y Administrador.
    """
    ROLES = [
        ('cliente', 'Cliente (Estudiante / Docente)'),
        ('cajero', 'Cajero (Punto de Venta / POS)'),
        ('admin', 'Administrador General'),
    ]

    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='perfil',
        verbose_name="Usuario Django Auth"
    )
    username = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Usuario")
    nombre_completo = models.CharField(max_length=200, verbose_name="Nombre Completo")
    email = models.EmailField(unique=True, verbose_name="Correo Institucional URC")
    matricula_urc = models.CharField(max_length=50, blank=True, verbose_name="Matrícula URC")
    telefono = models.CharField(max_length=30, blank=True, verbose_name="Teléfono Celular (SMS / WhatsApp)")
    rol = models.CharField(max_length=30, choices=ROLES, default='cliente', verbose_name="Rol Asignado")
    
    # Atributos específicos según herencia de rol (UML)
    turno_actual_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID Turno Actual (Cajero)")
    nivel_seguridad = models.PositiveIntegerField(default=1, verbose_name="Nivel de Seguridad (Admin)")
    
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        db_table = 'users'
        verbose_name = "Usuario (URC Express)"
        verbose_name_plural = "users (Usuarios URC)"

    @property
    def es_admin(self):
        return self.rol == 'admin' or (self.user and self.user.is_superuser)

    @property
    def es_cajero(self):
        return self.rol == 'cajero'

    @property
    def es_cliente(self):
        return self.rol == 'cliente'

    def __str__(self):
        matricula_str = f" [{self.matricula_urc}]" if self.matricula_urc else ""
        return f"{self.nombre_completo}{matricula_str} - {self.get_rol_display()}"


class Categoria(models.Model):
    """
    Colección: 'categories'
    Agrupa productos (Tortas, Bebidas, Dulces, Café) y define el área de despacho:
    - 'Cocina': Plancha, chilaquiles, café expresso caliente (KDS).
    - 'Mostrador': Grab & Go de despacho inmediato en menos de 30 segundos.
    """
    AREAS = [
        ('Mostrador', 'Mostrador Express (Grab & Go < 30 seg)'),
        ('Cocina', 'Cocina Caliente (Plancha / Cafetera KDS)'),
    ]

    nombre = models.CharField(max_length=150, verbose_name="Nombre de Categoría")
    slug = models.SlugField(max_length=150, unique=True, verbose_name="Slug")
    area_despacho = models.CharField(max_length=30, choices=AREAS, default='Mostrador', verbose_name="Área de Despacho")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    icono = models.CharField(max_length=50, default='bi-tag', verbose_name="Ícono Bootstrap / CSS")
    activa = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        db_table = 'categories'
        verbose_name = "Categoría"
        verbose_name_plural = "categories (Categorías del Menú)"

    def __str__(self):
        return f"{self.nombre} ({self.get_area_despacho_display()})"


class Producto(models.Model):
    """
    Colección: 'products'
    Catálogo maestro: SKU, nombre, descripción, precio de venta, tiempos estimados
    y opciones personalizables.
    """
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU / Código")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos', verbose_name="Categoría")
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de Venta ($ MXN)")
    tiempo_prep = models.PositiveIntegerField(
        default=30,
        verbose_name="Tiempo Estimado de Preparación (Segundos)"
    )
    area_despacho = models.CharField(
        max_length=30,
        choices=Categoria.AREAS,
        default='Mostrador',
        verbose_name="Área de Despacho"
    )
    opciones_personalizables = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Opciones Personalizables (JSON: ['Bien dorada', 'Con rajas', ...])"
    )
    imagen_url = models.CharField(max_length=300, blank=True, verbose_name="URL de Imagen o Emoji")
    activo = models.BooleanField(default=True, verbose_name="Activo para Venta")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        db_table = 'products'
        verbose_name = "Producto"
        verbose_name_plural = "products (Catálogo de Cafetería)"

    @property
    def es_grab_and_go(self):
        return self.area_despacho == 'Mostrador' or self.tiempo_prep <= 45

    def __str__(self):
        return f"{self.sku} - {self.nombre} (${self.precio_venta} MXN)"


class Inventario(models.Model):
    """
    Colección: 'inventory'
    Existencias físicas, stock mínimo de alerta y fechas de reabastecimiento.
    REGLA DE SEGURIDAD RBAC: Solo el Administrador General puede visualizar y reabastecer.
    Bloqueado deliberadamente a cajeros y clientes en UI y API para evitar alteraciones.
    """
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='inventario', verbose_name="Producto Asociado")
    stock_actual = models.PositiveIntegerField(default=50, verbose_name="Stock Físico Actual")
    alerta_min = models.PositiveIntegerField(default=10, verbose_name="Alerta Mínima de Stock")
    fecha_reabastecimiento = models.DateTimeField(null=True, blank=True, verbose_name="Última Fecha de Reabastecimiento")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        db_table = 'inventory'
        verbose_name = "Inventario de Cafetería"
        verbose_name_plural = "inventory (Control de Stock y Mermas)"

    @property
    def requiere_alerta(self):
        return self.stock_actual <= self.alerta_min

    def descontar(self, cantidad):
        """Descuenta de stock físico al confirmarse una venta o pedido pagado."""
        if self.stock_actual >= cantidad:
            self.stock_actual -= cantidad
            self.save(update_fields=['stock_actual', 'actualizado_en'])
            return True
        return False

    def reabastecer(self, cantidad):
        """Reabastece stock físico (Acción exclusiva de Administrador)."""
        self.stock_actual += cantidad
        self.fecha_reabastecimiento = timezone.now()
        self.save(update_fields=['stock_actual', 'fecha_reabastecimiento', 'actualizado_en'])

    def __str__(self):
        return f"Stock de {self.producto.nombre}: {self.stock_actual} uds (Mínimo: {self.alerta_min})"


class Pedido(models.Model):
    """
    Colección: 'orders'
    Transacción comercial con ítems y subtotales embebidos, estatus de preparación,
    código PIN de entrega y trazabilidad en la máquina de estados.
    Máquina de estados:
    PENDING_PAYMENT -> PAID -> IN_PREPARATION -> READY_FOR_PICKUP -> DELIVERED (o CANCELLED).
    """
    ESTADOS = [
        ('PENDING_PAYMENT', 'Pendiente de Pago'),
        ('PAID', 'Pagado / En Cola'),
        ('IN_PREPARATION', 'En Preparación'),
        ('READY_FOR_PICKUP', '¡Listo para Retiro!'),
        ('DELIVERED', 'Entregado en Mostrador'),
        ('CANCELLED', 'Cancelado'),
    ]

    TIPOS_DESPACHO = [
        ('Grab & Go', 'Grab & Go (Mostrador Express < 30 seg)'),
        ('Cocina Caliente', 'Cocina Caliente (Plancha / Cafetera KDS)'),
        ('Mixto', 'Mixto (Cocina + Grab & Go)'),
    ]

    order_number = models.CharField(max_length=30, unique=True, verbose_name="Número de Turno (ej. #URC-142)")
    cliente = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos', verbose_name="Cliente")
    cliente_nombre = models.CharField(max_length=150, blank=True, verbose_name="Nombre Cliente (Estudiante/Docente)")
    codigo_pin = models.CharField(max_length=10, verbose_name="Código PIN de Retiro Seguro (ej. PIN 412)")
    estado = models.CharField(max_length=30, choices=ESTADOS, default='PENDING_PAYMENT', verbose_name="Estado del Pedido")
    tipo_despacho = models.CharField(max_length=30, choices=TIPOS_DESPACHO, default='Grab & Go', verbose_name="Segregación de Comanda (Routing)")
    
    # Subdocumentos embebidos (Composición inmutable de venta)
    items = EmbeddedModelArrayField(DetalleItem, verbose_name="Ítems del Pedido (Instantánea Embebida)")
    pago = EmbeddedModelField(PagoMercadoPago, null=True, blank=True, verbose_name="Detalle de Pago Mercado Pago")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Subtotal ($)")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total ($)")
    origen = models.CharField(max_length=50, default='PWA Móvil', verbose_name="Canal de Origen (PWA Móvil / Mostrador POS)")
    cajero_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cajero Responsable (Si es Mostrador)")
    tiempo_espera_estimado = models.PositiveIntegerField(default=1, verbose_name="Tiempo Estimado de Espera (Minutos)")
    
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Hora de Registro")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        db_table = 'orders'
        verbose_name = "Pedido de Cafetería"
        verbose_name_plural = "orders (Pedidos y Comandas)"

    def determinar_tipo_despacho(self):
        """Analiza los ítems para la Segregación Inteligente de Comandas (Routing)."""
        tiene_cocina = False
        tiene_mostrador = False
        for it in self.items:
            if it.area_despacho == 'Cocina':
                tiene_cocina = True
            else:
                tiene_mostrador = True
        
        if tiene_cocina and tiene_mostrador:
            return 'Mixto'
        elif tiene_cocina:
            return 'Cocina Caliente'
        else:
            return 'Grab & Go'

    def __str__(self):
        return f"{self.order_number} - {self.cliente_nombre or 'Estudiante'} (${self.total} MXN) [{self.get_estado_display()}] PIN: {self.codigo_pin}"


class TurnoCorte(models.Model):
    """
    Colección: 'shifts' (Cortes Z)
    Registro de turnos de caja, fondo inicial en efectivo, acumulado digital Mercado Pago
    y procedimiento de ARQUEO CIEGO.
    El cajero no ve el acumulado en pantalla al momento de cerrar; ingresa manualmente
    la cantidad física contada. El sistema contrasta la declaración contra las ventas,
    calcula desfasajes (faltante o sobrante) y emite la póliza consolidada.
    """
    ESTADOS = [
        ('ABIERTO', 'Turno Abierto'),
        ('CERRADO', 'Turno Cerrado (Corte Z Emitido)'),
    ]

    cajero = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='turnos', verbose_name="Cajero Responsable")
    fecha_apertura = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora de Apertura")
    fecha_cierre = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y Hora de Cierre (Corte Z)")
    
    fondo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=500.00, verbose_name="Fondo de Cambio Inicial ($ MXN)")
    ventas_efectivo_sistema = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Ventas en Efectivo Mostrador ($)")
    ventas_mercadopago_sistema = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Ventas Procesadas Mercado Pago ($)")
    total_esperado_caja = models.DecimalField(max_digits=10, decimal_places=2, default=500.00, verbose_name="Total Efectivo en Caja Esperado ($)")
    total_global_facturado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Global Facturado en Turno ($)")
    
    # Arqueo Ciego
    efectivo_declarado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Efectivo Declarado por el Cajero (Arqueo Ciego)"
    )
    diferencia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Diferencia de Arqueo (Desfasaje: Faltante / Sobrante)"
    )
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ABIERTO', verbose_name="Estado del Turno")
    notas_arqueo = models.TextField(blank=True, verbose_name="Observaciones de Cierre / Arqueo")

    class Meta:
        db_table = 'shifts'
        verbose_name = "Turno de Caja (Corte Z)"
        verbose_name_plural = "shifts (Cortes Z y Arqueos)"

    def calcular_metricas_actuales(self):
        """Calcula ventas del turno actual desde la colección 'orders'."""
        pedidos_turno = Pedido.objects.filter(
            creado_en__gte=self.fecha_apertura,
            estado__in=['PAID', 'IN_PREPARATION', 'READY_FOR_PICKUP', 'DELIVERED']
        )
        if self.fecha_cierre:
            pedidos_turno = pedidos_turno.filter(creado_en__lte=self.fecha_cierre)

        efectivo = Decimal('0.00')
        mercadopago = Decimal('0.00')

        for p in pedidos_turno:
            if p.pago:
                if p.pago.metodo_pago == 'EFECTIVO_CAJA':
                    efectivo += p.total
                else:
                    mercadopago += p.total
            else:
                # Si no tiene desglose de pago, asume origen mostrador efectivo
                if p.origen == 'Mostrador POS':
                    efectivo += p.total
                else:
                    mercadopago += p.total

        self.ventas_efectivo_sistema = efectivo
        self.ventas_mercadopago_sistema = mercadopago
        self.total_esperado_caja = self.fondo_inicial + efectivo
        self.total_global_facturado = efectivo + mercadopago
        return self

    def cerrar_con_arqueo_ciego(self, monto_declarado, notas=""):
        """
        Ejecuta el Arqueo Ciego:
        El cajero declara 'monto_declarado' sin ver el monto del sistema.
        Se calcula la diferencia y se sella la póliza consolidada.
        """
        self.calcular_metricas_actuales()
        self.efectivo_declarado = Decimal(str(monto_declarado))
        self.diferencia = self.efectivo_declarado - self.total_esperado_caja
        self.fecha_cierre = timezone.now()
        self.estado = 'CERRADO'
        self.notas_arqueo = notas
        self.save()
        return self

    def __str__(self):
        cajero_nombre = self.cajero.nombre_completo if self.cajero else "Operador"
        return f"Turno #{self.id} - {cajero_nombre} [{self.estado}] - Facturado: ${self.total_global_facturado} MXN"
