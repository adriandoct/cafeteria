from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Usuario,
    Categoria,
    Producto,
    Inventario,
    Pedido,
    TurnoCorte
)


def es_cajero(user):
    """Verifica si el usuario autenticado tiene el rol de cajero."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return False
    perfil = getattr(user, 'perfil', None)
    if perfil and perfil.rol == 'cajero':
        return True
    if user.groups.filter(name='Cajeros').exists() or user.username.lower().startswith('cajer'):
        return True
    return False


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'nombre_completo', 'matricula_urc', 'email', 'rol', 'activo', 'creado_en')
    search_fields = ('username', 'nombre_completo', 'matricula_urc', 'email', 'telefono')
    list_filter = ('rol', 'activo', 'creado_en')
    ordering = ('-creado_en',)

    def has_module_permission(self, request):
        # El cajero no tiene acceso a gestionar cuentas ni roles de usuarios
        if es_cajero(request.user):
            return False
        return super().has_module_permission(request)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'area_despacho', 'icono', 'activa')
    search_fields = ('nombre', 'slug', 'descripcion')
    list_filter = ('area_despacho', 'activa')
    prepopulated_fields = {'slug': ('nombre',)}

    def has_module_permission(self, request):
        if es_cajero(request.user):
            return False
        return super().has_module_permission(request)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'categoria', 'precio_venta', 'tiempo_prep', 'area_despacho', 'activo')
    search_fields = ('sku', 'nombre', 'descripcion')
    list_filter = ('categoria', 'area_despacho', 'activo')
    ordering = ('categoria', 'nombre')

    # Cumplimiento RBAC estricto: El cajero puede ver el catálogo pero NO alterar precios ni productos
    def has_change_permission(self, request, obj=None):
        if es_cajero(request.user):
            return False
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        if es_cajero(request.user):
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if es_cajero(request.user):
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    """
    Control de Inventario y Almacén:
    Por regla estricta de negocio del documento (RBAC),
    el rol CAJERO TIENE TOTALMENTE DENEGADO el acceso a inventario.
    """
    list_display = ('producto', 'stock_actual', 'alerta_min', 'estado_stock', 'fecha_reabastecimiento', 'actualizado_en')
    search_fields = ('producto__sku', 'producto__nombre')
    list_filter = ('alerta_min',)
    readonly_fields = ('actualizado_en',)

    def estado_stock(self, obj):
        if obj.requiere_alerta:
            return format_html('<span style="color:red; font-weight:bold;">⚠️ ¡STOCK BAJO!</span>')
        return format_html('<span style="color:green; font-weight:bold;">✅ Óptimo</span>')
    estado_stock.short_description = "Estado Alerta"

    def has_module_permission(self, request):
        # Bloqueo total al módulo para cajeros
        if es_cajero(request.user):
            return False
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        if es_cajero(request.user):
            return False
        return super().has_view_permission(request, obj)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'cliente_nombre', 'codigo_pin', 'tipo_despacho', 'total', 'estado_badge', 'origen', 'creado_en')
    search_fields = ('order_number', 'cliente_nombre', 'codigo_pin')
    list_filter = ('estado', 'tipo_despacho', 'origen', 'creado_en')
    ordering = ('-creado_en',)

    def estado_badge(self, obj):
        colores = {
            'PENDING_PAYMENT': '#F59E0B',
            'PAID': '#3B82F6',
            'IN_PREPARATION': '#8B5CF6',
            'READY_FOR_PICKUP': '#10B981',
            'DELIVERED': '#6B7280',
            'CANCELLED': '#EF4444'
        }
        color = colores.get(obj.estado, '#000')
        return format_html(
            f'<span style="background:{color}; color:#fff; padding:3px 8px; border-radius:6px; font-weight:bold;">{obj.get_estado_display()}</span>'
        )
    estado_badge.short_description = "Estado de Comanda"


@admin.register(TurnoCorte)
class TurnoCorteAdmin(admin.ModelAdmin):
    list_display = ('id', 'cajero', 'fecha_apertura', 'fecha_cierre', 'total_global_facturado', 'efectivo_declarado', 'diferencia_badge', 'estado')
    search_fields = ('cajero__nombre_completo', 'cajero__username')
    list_filter = ('estado', 'fecha_apertura')
    ordering = ('-fecha_apertura',)

    def diferencia_badge(self, obj):
        if obj.estado == 'ABIERTO':
            return format_html('<i>En Curso (Arqueo Ciego)</i>')
        if obj.diferencia == 0:
            return format_html('<span style="color:green; font-weight:bold;">$0.00 (Cuadre Exacto)</span>')
        elif obj.diferencia > 0:
            return format_html(f'<span style="color:blue; font-weight:bold;">+${obj.diferencia} (Sobrante)</span>')
        else:
            return format_html(f'<span style="color:red; font-weight:bold;">-${abs(obj.diferencia)} (Faltante)</span>')
    diferencia_badge.short_description = "Desfasaje Arqueo Ciego"

    def has_module_permission(self, request):
        # Cajeros operan su corte desde la UI dedicada; solo Admin audita globalmente
        if es_cajero(request.user):
            return False
        return super().has_module_permission(request)
