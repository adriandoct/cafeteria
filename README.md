# Café URC Express: Sistema Automatizado de Atención y Punto de Venta (POS/KDS)
**Universidad Rosario Castellanos • Sistemas y Tecnología**

Solución integral orientada a erradicar las colas de espera en los recesos y cambios de clase en la cafetería universitaria. Desacopla la toma de orden y el cobro digital mediante **Mercado Pago** de la preparación física y entrega en barra, integrando segregación inteligente de comandas (**KDS**), control de acceso basado en roles (**RBAC**), control de mermas e inventario, y procedimiento de **Arqueo Ciego (Corte Z)** sobre una base de datos NoSQL en **MongoDB** (`cafeteria`).

---

## 📌 Objetivo de Impacto Operativo
- **Reducción de fila:** De **14 minutos** promedio en fila tradicional a menos de **45 segundos** para retiro en barra (-95% de tiempo de espera).
- **Cero manejo de efectivo suelto:** Pagos integrados con Mercado Pago (código QR, saldo en cuenta, tarjetas bancarias y transferencias SPEI).
- **Retiro Seguro:** Entrega en barra validada con **Turno `#URC-XXX`** y **Código PIN de retiro** (ej. `PIN 412`).

---

## 🚀 Inicio Rápido del Servidor

1. **Activar el entorno virtual:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Verificar conexión a MongoDB:**
   - Base de datos configurada: `cafeteria` en `mongodb://localhost:27017/`.

3. **Iniciar el servidor de desarrollo:**
   ```powershell
   python manage.py runserver
   ```

4. **Acceder a los módulos del sistema en el navegador:**
   - 📱 **PWA Móvil Alumnos / Menú Anticolas:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - 💼 **Punto de Venta Mostrador (POS Cajero & Arqueo Ciego):** [http://127.0.0.1:8000/caja/](http://127.0.0.1:8000/caja/)
   - 🍳 **Pantalla KDS Cocina & Routing Inteligente:** [http://127.0.0.1:8000/kds/](http://127.0.0.1:8000/kds/)
   - 👑 **Panel Ejecutivo de Administración y Auditoría:** [http://127.0.0.1:8000/admin-panel/](http://127.0.0.1:8000/admin-panel/)
   - ⚙️ **Django Admin (MongoAdmin):** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🔑 Credenciales y Matriz de Roles (RBAC)

| Rol / Actor | Usuario | Contraseña | Perfil / Matrícula URC | Módulos y Privilegios Clave |
| :--- | :--- | :--- | :--- | :--- |
| 👑 **Administrador General** | `admin` | `admin1234` | Lic. Fernando Rivas (`URC-ADM-001`) | **Acceso Total:** Reabastecimiento de inventario, edición de precios de catálogo, auditoría global de Cortes Z y métricas ejecutivas. |
| 💼 **Cajero (Punto de Venta POS)** | `cajero` | `cajero1234` | Juan Carlos Pérez (`URC-CAJ-104`) | **Venta y Despacho:** Cobro en mostrador (efectivo/TPV), ticket con PIN y cierre de turno con **Arqueo Ciego**. *Bloqueado:* Sin acceso a inventario ni a modificar precios. |
| 👨‍🎓 **Estudiante (PWA Móvil)** | `estudiante` | `estudiante1234` | Valeria Gómez (`URC-2024-0412`) | **Pedido Anticipado:** Menú segregado, personalizaciones ('bien dorada, con rajas'), pago digital Mercado Pago y trazador de turno con PIN. |
| 👨‍🏫 **Docente (PWA Móvil)** | `docente` | `docente1234` | Dr. Roberto Morales (`URC-DOC-0821`) | Pedido anticipado y seguimiento de comanda en vivo. |

---

## 🗄️ Modelo de Datos NoSQL MongoDB (Base de Datos: `cafeteria`)

1. **`users` (`Usuario`):**
   - Credenciales, matrícula URC, teléfono, correo institucional y rol asignado (`cliente`, `cajero`, `admin`).
2. **`categories` (`Categoria`):**
   - Agrupa productos y define la segregación de despacho: `area_despacho` (`Cocina` vs `Mostrador`).
3. **`products` (`Producto`):**
   - Catálogo maestro: SKU, nombre, descripción, precio de venta, tiempo estimado de preparación (`tiempo_prep`), opciones personalizables y área de despacho.
4. **`inventory` (`Inventario`):**
   - Existencias físicas, stock mínimo de alerta (`alerta_min`) y fechas de reabastecimiento. *Restringido estrictamente a Administrador.*
5. **`orders` (`Pedido`):**
   - Transacción comercial inmutable con instantánea de ítems embebidos (`DetalleItem`), código PIN de entrega, subdocumento de pago (`PagoMercadoPago`), routing (`Grab & Go`, `Cocina Caliente`, `Mixto`) y máquina de estados:
     $$\text{PENDING\_PAYMENT} \rightarrow \text{PAID} \rightarrow \text{IN\_PREPARATION} \rightarrow \text{READY\_FOR\_PICKUP} \rightarrow \text{DELIVERED}$$
6. **`shifts` (`TurnoCorte` - Cortes Z):**
   - Registro de turnos de caja, fondo inicial ($500.00 MXN), ventas en efectivo y Mercado Pago del sistema, y procedimiento de **Arqueo Ciego** donde el cajero declara su conteo físico a ciegas, calculando el desfasaje (faltante o sobrante) y emitiendo la póliza consolidada.

---

## ⚡ Automatización Zero-Touch de Mercado Pago
1. El estudiante realiza el checkout en la PWA (QR en mesa, Saldo en cuenta o Tarjeta).
2. El webhook asíncrono (`/api/mercadopago/webhook/`) recibe la confirmación `approved`:
   - Cambia el estado del pedido a `PAID` (En Cola).
   - Decrementa el inventario de MongoDB transaccionalmente.
   - Activa el routing inteligente y la alerta de comanda en el KDS de cocina / mostrador express.

---

## 🏛️ Defensa del Proyecto (Pilares Estratégicos)
- **Impacto Estudiantil Directo:** Eliminación de filas en recesos de 20 minutos; comida lista al sonar el timbre.
- **Blindaje Financiero y Cero Pérdidas:** Bloqueo total al cajero de modificar inventario y precios; arqueo ciego contrastado automáticamente.
- **Escalabilidad Multi-Campus:** Núcleo NoSQL listo para replicarse en las sedes Coyoacán, Azcapotzalco y Gustavo A. Madero de la URC.
