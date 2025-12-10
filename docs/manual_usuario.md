# Manual de Usuario - Sistema Bar Galileo
##  Índice
1. [Introducción](#introducción)
2. [Acceso al Sistema](#acceso-al-sistema)
3. [Módulos del Sistema](#módulos-del-sistema)
4. [Gestión de Productos](#gestión-de-productos)
5. [Gestión de Mesas y Pedidos](#gestión-de-mesas-y-pedidos)
6. [Gestión de Gastos](#gestión-de-gastos)
7. [Gestión de Nóminas](#gestión-de-nóminas)
8. [Sistema de Facturación](#sistema-de-facturación)
9. [Sistema de Reportes](#sistema-de-reportes)
10. [Sistema de Backups](#sistema-de-backups)
11. [Roles y Permisos](#roles-y-permisos)
12. [Sistema de Ayuda](#sistema-de-ayuda)
13. [Mensajes de Error Frecuentes](#mensajes-de-error-frecuentes)
14. [Preguntas Frecuentes](#preguntas-frecuentes)
---
## 1. Introducción
### ¿Qué es Bar Galileo?
**Bar Galileo** es un sistema integral de gestión para establecimientos de hostelería (bares, restaurantes, cafeterías). Desarrollado con Django y Python, permite administrar de forma eficiente todos los aspectos operativos del negocio.
### ¿A quién va dirigido?
- **Administradores**: Control total del sistema, gestión de usuarios, reportes y configuraciones
- **Meseros**: Gestión de mesas, pedidos y facturación
- **Cajeros**: Manejo de caja, facturación y cobros
- **Personal de Cocina**: Consulta de pedidos activos
- **Gerentes**: Acceso a reportes, análisis de ventas y gastos
### Características Principales
-  Gestión completa de productos, inventario y categorías
-  Sistema de mesas y pedidos en tiempo real
-  Facturación automatizada
-  Control de gastos con comprobantes
-  Gestión de nóminas de empleados
-  Generación de reportes avanzados (PDF, Excel, CSV)
-  Sistema de backups automáticos y manuales
-  Control de roles y permisos personalizados
-  Notificaciones en tiempo real con WebSockets
-  Chatbot de ayuda con IA (RAG)
-  Integración con Google Sign-In
---
## 2. Acceso al Sistema
### 2.1 URL de Acceso
El sistema está disponible en:
```
http://localhost:8000/
```
O en la URL configurada por su administrador de sistemas.
### 2.2 Inicio de Sesión
#### Opción 1: Login con Usuario y Contraseña
1. Acceda a la página de inicio
2. Haga clic en **"Iniciar Sesión"**
3. Ingrese su **nombre de usuario** o **correo electrónico**
4. Ingrese su **contraseña**
5. Complete el **captcha** de seguridad
6. Haga clic en **"Entrar"**
#### Opción 2: Login con Google
1. En la página de inicio, haga clic en **"Iniciar sesión con Google"**
2. Seleccione su cuenta de Google
3. Autorice el acceso
4. Será redirigido automáticamente al sistema
### 2.3 Recuperación de Contraseña
1. En la página de login, haga clic en **"¿Olvidaste tu contraseña?"**
2. Ingrese su correo electrónico registrado
3. Revise su bandeja de entrada y siga las instrucciones del correo
4. Establezca una nueva contraseña
### 2.4 Registro de Nuevo Usuario
*Nota: Solo los administradores pueden crear nuevos usuarios desde el panel de administración.*
1. El administrador accede a **Dashboard > Usuarios**
2. Clic en **"Crear Usuario"**
3. Completa el formulario con:
   - Nombre de usuario
   - Correo electrónico
   - Contraseña
   - Rol asignado
4. Guarda los cambios
### 2.5 Primera Vez en el Sistema
Al iniciar sesión por primera vez:
1. Complete su perfil en **"Mi Perfil"**
2. Cambie su contraseña temporal (si aplica)
3. Familiarícese con el menú lateral y las opciones disponibles según su rol
---
## 3. Módulos del Sistema
### 3.1 Dashboard Principal
Al ingresar, verá un panel con:
- **Resumen de ventas del día**
- **Pedidos activos**
- **Estado de mesas**
- **Alertas de stock bajo**
- **Accesos rápidos** a funciones principales
### 3.2 Menú de Navegación
El menú lateral incluye:
| Módulo | Descripción | Ícono |
|--------|-------------|-------|
| **Inicio** | Página principal con productos disponibles |  |
| **Productos** | Gestión de productos, categorías, marcas |  |
| **Mesas** | Control de mesas y pedidos |  |
| **Gastos** | Registro y control de gastos |  |
| **Nóminas** | Gestión de empleados y pagos |  |
| **Facturación** | Consulta y gestión de facturas |  |
| **Reportes** | Generación de reportes analíticos |  |
| **Backups** | Respaldos de base de datos |  |
| **Roles** | Gestión de roles y permisos |  |
| **Ayuda** | Chatbot asistente con IA |  |
---
## 4. Gestión de Productos
### 4.1 Ver Catálogo de Productos
1. Navegue a **Inicio** o **Productos**
2. Verá tarjetas con:
   - Imagen del producto
   - Nombre
   - Precio de venta
   - Stock disponible
3. Use la barra de búsqueda para filtrar por nombre
4. Haga clic en un producto para ver detalles completos
### 4.2 Agregar Nuevo Producto
**Permisos requeridos**: Administrador, Gerente
1. Vaya a **Productos > Agregar Producto**
2. Complete el formulario:
   - **Nombre**: Nombre único del producto
   - **Descripción**: Detalles del producto
   - **Categoría**: Seleccione de la lista (Bebidas, Comidas, etc.)
   - **Marca**: Seleccione la marca correspondiente
   - **Proveedor**: Seleccione el proveedor
   - **Precio de Compra**: Costo de adquisición
   - **Precio de Venta**: Precio al público (debe ser mayor al de compra)
   - **Stock Inicial**: Cantidad disponible
   - **Activo**: Marque si estará disponible para venta
3. **Subir Imágenes**:
   - Haga clic en **"Seleccionar imágenes"**
   - Formatos soportados: PNG, JPG, JPEG, WEBP
   - Se pueden subir múltiples imágenes
4. Haga clic en **"Guardar"**
### 4.3 Editar Producto
1. Busque el producto en el listado
2. Haga clic en **"Editar"** (ícono de lápiz)
3. Modifique los campos necesarios
4. Para cambiar imágenes:
   - Elimine las imágenes antiguas (ícono de basurero)
   - Suba nuevas imágenes
5. Haga clic en **"Actualizar"**
### 4.4 Gestionar Stock
El stock se actualiza automáticamente:
- **Al crear/editar** un producto
- **Al facturar** un pedido (descuenta del stock)
- **Al registrar entrada** de mercancía
Para ver el historial de movimientos:
1. Entre al detalle del producto
2. Vea la sección **"Movimientos de Stock"**
3. Se muestra fecha, cantidad y tipo de movimiento
### 4.5 Desactivar Producto
Para productos que ya no se venden pero se quiere mantener el historial:
1. Edite el producto
2. Desmarque la opción **"Activo"**
3. Guarde los cambios
4. El producto desaparecerá del catálogo público pero permanecerá en reportes históricos
### 4.6 Gestión de Categorías
1. Vaya a **Productos > Categorías**
2. **Crear Categoría**:
   - Nombre (ej: Bebidas Calientes, Cervezas, Entradas)
   - Descripción opcional
3. **Editar/Eliminar**: Use los botones correspondientes
### 4.7 Gestión de Marcas y Proveedores
Similar a categorías, gestione:
- **Marcas**: Coca-Cola, Heineken, etc.
- **Proveedores**: Datos de contacto, teléfono, dirección
---
## 5. Gestión de Mesas y Pedidos
### 5.1 Ver Estado de Mesas
1. Navegue a **Mesas**
2. Verá un tablero visual con todas las mesas
3. Estados posibles:
   -  **Disponible**: Mesa libre
   -  **Ocupada**: Mesa con pedido activo
   -  **Reservada**: Mesa reservada
   -  **Fuera de servicio**: Mesa no disponible
### 5.2 Crear Nuevo Pedido
1. Seleccione una mesa **Disponible**
2. Haga clic en **"Nuevo Pedido"**
3. Se abrirá el formulario de pedido:
   - **Buscar productos**: Use la barra de búsqueda
   - **Agregar al pedido**: Haga clic en el producto
   - **Ajustar cantidad**: Use los botones +/-
   - **Ver total**: Se calcula automáticamente
4. Haga clic en **"Guardar Pedido"**
5. La mesa cambia a estado **Ocupada**
### 5.3 Editar Pedido Activo
1. Haga clic en la mesa ocupada
2. Seleccione **"Ver Pedido"**
3. Puede:
   - Agregar más productos
   - Eliminar productos (ícono X)
   - Cambiar cantidades
4. Haga clic en **"Actualizar Pedido"**
### 5.4 Asociar Usuarios a Pedido
Para dividir la cuenta:
1. En el pedido activo, clic en **"Asociar Usuarios"**
2. Seleccione los usuarios que compartirán la cuenta
3. Al facturar, podrá dividir el total entre ellos
### 5.5 Cancelar Pedido
1. Abra el pedido
2. Haga clic en **"Cancelar Pedido"**
3. Confirme la acción
4. El pedido se marca como **Cancelado**
5. La mesa vuelve a estado **Disponible**
### 5.6 Facturar Pedido
Ver sección de **Facturación** más adelante.
---
## 6. Gestión de Gastos
### 6.1 Registrar Nuevo Gasto
**Permisos requeridos**: Administrador, Gerente, Cajero
1. Vaya a **Gastos > Registrar Gasto**
2. Complete el formulario:
   - **Fecha**: Fecha del gasto
   - **Monto**: Cantidad gastada
   - **Categoría**: Seleccione (Servicios, Compras, Salarios, etc.)
   - **Descripción**: Detalle del gasto
   - **Comprobante**: Suba una imagen o PDF del recibo
3. Haga clic en **"Guardar"**
### 6.2 Ver Listado de Gastos
1. Vaya a **Gastos**
2. Use los filtros:
   - Por fecha (rango)
   - Por categoría
   - Por monto
3. Haga clic en un gasto para ver detalles completos
### 6.3 Editar/Eliminar Gasto
1. En el listado, haga clic en **"Editar"** (lápiz)
2. Modifique los campos necesarios
3. Para eliminar, use el botón **"Eliminar"** (requiere confirmación)
### 6.4 Descargar Comprobante
1. Entre al detalle del gasto
2. Haga clic en **"Ver Comprobante"**
3. Se abrirá el archivo adjunto
### 6.5 Gestión de Categorías de Gastos
1. Vaya a **Gastos > Categorías**
2. Cree, edite o elimine categorías según necesidad
3. Categorías comunes:
   - Servicios (luz, agua, internet)
   - Compras (inventario)
   - Salarios
   - Mantenimiento
   - Marketing
---
## 7. Gestión de Nóminas
### 7.1 Registro de Empleados
#### 7.1.1 Agregar Nuevo Empleado
1. Vaya a **Nóminas > Empleados > Agregar**
2. Complete el formulario:
   - **Nombre Completo**
   - **Cargo**: Se puede vincular con un rol del sistema
   - **Salario Base**: Monto mensual
   - **Fecha de Contratación**
   - **Estado**: Activo, Inactivo, Vacaciones, etc.
   - **Tipo de Contrato**: Tiempo completo, medio tiempo, temporal
   - **Email y Teléfono**: Datos de contacto
   - **Dirección**
3. *Opcional*: **Vincular con Usuario del Sistema**
   - Seleccione un usuario existente
   - Permite que el empleado acceda al sistema
4. Haga clic en **"Guardar"**
#### 7.1.2 Ver Listado de Empleados
1. Vaya a **Nóminas > Empleados**
2. Verá una tabla con:
   - Nombre
   - Cargo
   - Salario
   - Estado
   - Antigüedad
3. Use filtros por estado o búsqueda por nombre
### 7.2 Gestión de Pagos
#### 7.2.1 Registrar Pago
1. Vaya a **Nóminas > Pagos > Registrar**
2. Seleccione el **Empleado**
3. Complete:
   - **Fecha de Pago**
   - **Monto**
   - **Tipo de Pago**:
     - Salario
     - Bonificación
     - Pago de Vacaciones
     - Liquidación
     - Otro
   - **Descripción**: Detalle del pago
   - **Comprobante**: Suba el recibo de pago
4. Haga clic en **"Guardar"**
#### 7.2.2 Ver Historial de Pagos
1. Entre al detalle de un empleado
2. Verá la sección **"Historial de Pagos"**
3. Se muestra:
   - Fecha
   - Monto
   - Tipo
   - Comprobante descargable
### 7.3 Bonificaciones
1. Vaya a **Nóminas > Bonificaciones**
2. Cree bonificaciones asociadas a empleados
3. Se suman automáticamente al salario total
### 7.4 Reportes de Nómina
1. Vaya a **Reportes > Nóminas**
2. Seleccione período
3. Genere reporte en PDF o Excel
4. Incluye:
   - Total pagado por empleado
   - Desglose por tipo de pago
   - Total general del período
---
## 8. Sistema de Facturación
### 8.1 Generar Factura desde Pedido
1. Abra un pedido activo desde **Mesas**
2. Haga clic en **"Facturar"**
3. El sistema:
   - Genera un número de factura único
   - Calcula el total automáticamente
   - Descuenta los productos del stock
   - Marca el pedido como **Facturado**
   - Libera la mesa
4. Se muestra la factura para imprimir o descargar
### 8.2 Ver Listado de Facturas
1. Vaya a **Facturación**
2. Verá un listado con:
   - Número de factura
   - Fecha
   - Mesa
   - Total
3. Use filtros:
   - Por rango de fechas
   - Por número de factura
   - Por mesa
### 8.3 Ver Detalle de Factura
1. Haga clic en una factura del listado
2. Verá:
   - Número de factura
   - Fecha y hora
   - Mesa asociada
   - Productos facturados (cantidad, precio, subtotal)
   - Total general
3. Opciones:
   - **Imprimir**: Genera versión para impresora térmica
   - **Descargar PDF**: Para enviar por correo o guardar
### 8.4 Reimprimir Factura
1. Busque la factura en el listado
2. Haga clic en **"Reimprimir"**
3. Se genera nuevamente el documento
### 8.5 Anular Factura
*Esta función puede estar restringida por permisos*
1. Abra la factura
2. Haga clic en **"Anular"**
3. Ingrese el motivo de anulación
4. Confirme
5. El sistema:
   - Marca la factura como anulada
   - Restablece el stock de los productos
   - Registra el evento en el log
---
## 9. Sistema de Reportes
### 9.1 Tipos de Reportes Disponibles
#### 9.1.1 Reporte de Ventas
- Total de ventas por período
- Ventas por producto
- Ventas por categoría
- Tendencias de ventas
#### 9.1.2 Reporte de Inventario
- Stock actual de todos los productos
- Alertas de stock bajo
- Movimientos de inventario
- Productos más vendidos
#### 9.1.3 Reporte de Gastos
- Total de gastos por período
- Gastos por categoría
- Comparativa de gastos mensual
#### 9.1.4 Reporte de Nóminas
- Total pagado por empleado
- Desglose por tipo de pago
- Historial de pagos
#### 9.1.5 Reporte de Productos
- Productos más vendidos
- Productos menos vendidos
- Rentabilidad por producto
#### 9.1.6 Reporte General
- Resumen de ventas, gastos, utilidades
- Estado general del negocio
### 9.2 Generar Reporte
#### 9.2.1 Crear Nuevo Reporte
1. Vaya a **Reportes > Generar Reporte**
2. Seleccione:
   - **Tipo de Reporte**: Ventas, Inventario, Gastos, etc.
   - **Período**: Diario, Semanal, Mensual, Trimestral, Anual, Personalizado
   - **Rango de Fechas**: Si eligió "Personalizado"
   - **Formato de Exportación**: PDF, Excel, CSV
3. Haga clic en **"Generar Reporte"**
4. El sistema procesará la información
5. Una vez generado:
   - Se muestra una vista previa
   - Puede descargar el archivo
#### 9.2.2 Reportes Programados
1. Vaya a **Reportes > Programar Reporte**
2. Configure:
   - Tipo de reporte
   - Frecuencia (diaria, semanal, mensual)
   - Correos destinatarios
3. El sistema generará y enviará el reporte automáticamente
### 9.3 Ver Historial de Reportes
1. Vaya a **Reportes > Historial**
2. Verá todos los reportes generados
3. Puede:
   - Descargar reportes anteriores
   - Regenerar con los mismos parámetros
   - Eliminar reportes antiguos
### 9.4 Visualización de Datos
Los reportes incluyen:
- **Tablas** con datos detallados
- **Gráficos**:
  - Gráficos de barras
  - Gráficos de líneas (tendencias)
  - Gráficos circulares (proporciones)
- **KPIs** (indicadores clave):
  - Total de ventas
  - Producto más vendido
  - Ticket promedio
  - Margen de utilidad
---
## 10. Sistema de Backups
### 10.1 Importancia de los Backups
Los backups son copias de seguridad de toda la base de datos. Permiten:
- Recuperar información en caso de fallo
- Restaurar el sistema a un punto anterior
- Migrar datos a otro servidor
### 10.2 Crear Backup Manual
1. Vaya a **Backups > Crear Backup**
2. Haga clic en **"Crear Backup Ahora"**
3. El sistema:
   - Genera una copia de la base de datos
   - La almacena en `backups/backup_files/`
   - Muestra confirmación con fecha y tamaño
4. Tiempo estimado: 10-30 segundos
### 10.3 Backups Automáticos
El sistema está configurado para crear backups automáticos:
- **Frecuencia**: Diaria a las 2:00 AM
- **Ubicación**: `bar_galileo/backups/backup_files/`
- **Retención**: Se guardan los últimos 30 backups
### 10.4 Ver Listado de Backups
1. Vaya a **Backups**
2. Verá una lista con:
   - Fecha y hora de creación
   - Tamaño del archivo
   - Tipo (manual/automático)
3. Use filtros por fecha
### 10.5 Descargar Backup
1. En el listado, haga clic en **"Descargar"**
2. El archivo se descargará en su computador
3. Guárdelo en un lugar seguro (USB, nube, etc.)
### 10.6 Restaurar Backup
**️ IMPORTANTE**: Esta operación sobrescribe toda la base de datos actual.
1. Vaya a **Backups > Restaurar**
2. Seleccione el backup que desea restaurar
3. Haga clic en **"Restaurar"**
4. Confirme la acción (se pedirá confirmación múltiple)
5. El sistema:
   - Detiene todas las conexiones
   - Restaura la base de datos
   - Reinicia el sistema
6. Todos los usuarios serán desconectados
### 10.7 Eliminar Backups Antiguos
1. En el listado de backups
2. Seleccione los que desea eliminar
3. Haga clic en **"Eliminar"**
4. Confirme (no se puede deshacer)
---
## 11. Roles y Permisos
### 11.1 Roles Predefinidos del Sistema
#### Administrador
- **Descripción**: Control total del sistema
- **Permisos**:
  - Crear, editar, eliminar usuarios
  - Gestionar roles y permisos
  - Acceso a todos los módulos
  - Ver todos los reportes
  - Configurar backups
  - Acceso al panel de Django Admin
#### Gerente
- **Descripción**: Gestión operativa y reportes
- **Permisos**:
  - Ver y generar reportes
  - Gestión de productos
  - Gestión de gastos
  - Gestión de nóminas
  - Ver facturación
#### Mesero
- **Descripción**: Atención de mesas y pedidos
- **Permisos**:
  - Ver productos
  - Gestionar mesas
  - Crear y editar pedidos
  - Facturar pedidos
#### Cajero
- **Descripción**: Manejo de caja y facturación
- **Permisos**:
  - Facturar pedidos
  - Ver facturas
  - Registrar gastos
  - Ver reportes de ventas
#### Cocina
- **Descripción**: Personal de cocina
- **Permisos**:
  - Ver pedidos activos
  - Marcar pedidos como preparados
  - Ver productos
### 11.2 Gestión de Roles
#### 11.2.1 Crear Nuevo Rol
1. Vaya a **Roles > Crear Rol**
2. Ingrese:
   - **Nombre**: Nombre del rol (ej: "Supervisor")
   - **Descripción**: Descripción detallada
3. **Asignar Permisos**:
   - Seleccione los módulos a los que tendrá acceso
   - Para cada módulo, seleccione las acciones:
     - **Ver**: Puede consultar información
     - **Crear**: Puede agregar nuevos registros
     - **Editar**: Puede modificar registros existentes
     - **Eliminar**: Puede eliminar registros
4. Haga clic en **"Guardar"**
#### 11.2.2 Editar Rol Existente
1. Vaya a **Roles**
2. Haga clic en el rol que desea editar
3. Modifique nombre, descripción o permisos
4. Guarde los cambios
5. *Nota*: Los cambios se aplican inmediatamente a todos los usuarios con ese rol
#### 11.2.3 Eliminar Rol
1. Solo si no hay usuarios asignados a ese rol
2. Haga clic en **"Eliminar"**
3. Confirme la acción
### 11.3 Asignar Rol a Usuario
1. Vaya a **Dashboard > Usuarios**
2. Seleccione un usuario
3. Haga clic en **"Editar"**
4. En el campo **"Rol"**, seleccione el rol apropiado
5. Guarde los cambios
6. El usuario debe cerrar sesión y volver a entrar para que los cambios surtan efecto
### 11.4 Matriz de Permisos
| Módulo | Admin | Gerente | Mesero | Cajero | Cocina |
|--------|-------|---------|--------|--------|--------|
| Productos (Ver) |  |  |  |  |  |
| Productos (Crear/Editar) |  |  |  |  |  |
| Mesas (Ver) |  |  |  |  |  |
| Mesas (Gestionar) |  |  |  |  |  |
| Pedidos (Ver) |  |  |  |  |  |
| Pedidos (Crear/Editar) |  |  |  |  |  |
| Facturación |  |  |  |  |  |
| Gastos |  |  |  |  |  |
| Nóminas |  |  |  |  |  |
| Reportes |  |  |  | Parcial |  |
| Backups |  |  |  |  |  |
| Roles |  |  |  |  |  |
---
## 12. Sistema de Ayuda
### 12.1 ¿Qué es el Sistema de Ayuda?
El sistema incluye una herramienta de ayuda inteligente que le permite consultar información sobre cómo usar el sistema. Puede hacer preguntas en lenguaje natural y recibir respuestas claras basadas en este manual.
### 12.2 Acceder a la Ayuda
1. Haga clic en **"Ayuda"** en el menú lateral del dashboard
2. Se abrirá una ventana de chat donde puede escribir sus preguntas
### 12.3 Hacer una Consulta
1. Escriba su pregunta de forma clara y sencilla
2. Ejemplos de preguntas:
   - "¿Cómo creo un producto?"
   - "¿Cómo facturo un pedido?"
   - "¿Cómo genero un reporte?"
3. Presione Enter o haga clic en "Enviar"
4. El sistema le mostrará la información relevante del manual
5. Si la respuesta no es clara, intente reformular su pregunta
### 12.4 Descargar el Manual
Puede descargar este manual completo en formato PDF:
1. Vaya al menú **"Ayuda"**
2. Haga clic en **"Descargar Manual PDF"**
3. El archivo se descargará automáticamente
### 12.5 Consejos de Uso
- Sea específico en sus preguntas
- Use palabras clave relacionadas con lo que busca
- Si no encuentra lo que necesita, consulte el manual completo
- Para asistencia adicional, contacte a su administrador
---
## 13. Mensajes de Error Frecuentes
### 13.1 Errores de Autenticación
#### "Usuario o contraseña incorrectos"
- **Causa**: Credenciales inválidas
- **Solución**: 
  - Verifique que el usuario y contraseña sean correctos
  - Verifique que no tenga Bloq Mayús activado
  - Use la opción "¿Olvidaste tu contraseña?"
#### "Sesión expirada"
- **Causa**: La sesión ha caducado por inactividad
- **Solución**: Vuelva a iniciar sesión
#### "No tienes permiso para acceder a esta página"
- **Causa**: Su rol no tiene permisos para ese módulo
- **Solución**: Contacte a su administrador para solicitar los permisos necesarios
### 13.2 Errores de Productos
#### "El precio de venta debe ser mayor que el de compra"
- **Causa**: Validación de modelo
- **Solución**: Asegúrese de que el precio de venta sea superior al precio de compra
#### "El nombre del producto ya existe"
- **Causa**: Los nombres de productos deben ser únicos
- **Solución**: Use un nombre diferente o agregue un distintivo (ej: "Coca Cola 350ml", "Coca Cola 500ml")
#### "Stock no puede ser negativo"
- **Causa**: Intentó guardar un producto con stock negativo
- **Solución**: Ingrese un valor de stock 0 o mayor
#### "Error al subir imagen: Solo se permiten archivos PNG, JPG, JPEG o WEBP"
- **Causa**: Formato de archivo no soportado
- **Solución**: Convierta la imagen a uno de los formatos permitidos
### 13.3 Errores de Pedidos y Facturación
#### "No se puede editar un pedido facturado"
- **Causa**: El pedido ya fue convertido en factura
- **Solución**: Si necesita modificar, debe anular la factura primero (requiere permisos de administrador)
#### "No hay suficiente stock para este producto"
- **Causa**: La cantidad solicitada excede el stock disponible
- **Solución**: 
  - Reduzca la cantidad en el pedido
  - Actualice el stock del producto primero
#### "La mesa ya tiene un pedido activo"
- **Causa**: Intentó crear un nuevo pedido en una mesa ocupada
- **Solución**: 
  - Edite el pedido existente
  - O facture el pedido actual antes de crear uno nuevo
### 13.4 Errores de Reportes
#### "No hay datos para el período seleccionado"
- **Causa**: No hay información en el rango de fechas elegido
- **Solución**: Amplíe el rango de fechas o verifique que haya actividad registrada
#### "Error al generar reporte: Timeout"
- **Causa**: El reporte tiene demasiados datos
- **Solución**: 
  - Reduzca el rango de fechas
  - Genere reportes parciales
### 13.5 Errores de Backups
#### "No se puede restaurar: Archivo corrupto"
- **Causa**: El archivo de backup está dañado
- **Solución**: Use un backup anterior
#### "Error de permisos al crear backup"
- **Causa**: El servidor no tiene permisos de escritura en la carpeta de backups
- **Solución**: Contacte al administrador de sistemas
### 13.6 Errores de Chatbot
#### "GOOGLE_API_KEY no configurada"
- **Causa**: Falta la clave de API de Google
- **Solución**: El administrador debe configurar la variable de entorno en el archivo `.env`
#### "No se encontraron documentos indexados"
- **Causa**: No hay documentos procesados en el sistema RAG
- **Solución**: Suba el manual de usuario desde el panel de administración
#### "Error al procesar documento: Formato no soportado"
- **Causa**: El archivo no es PDF, TXT o MD
- **Solución**: Convierta el documento a un formato soportado
---
## 14. Preguntas Frecuentes
### 14.1 General
**¿Puedo usar el sistema desde mi celular?**
Sí, el sistema es responsive y se adapta a dispositivos móviles. Sin embargo, algunas funciones administrativas se visualizan mejor en pantallas grandes.
**¿El sistema funciona sin internet?**
El sistema funciona en la red local sin internet, excepto:
- Login con Google (requiere internet)
- Chatbot RAG (usa Google API)
**¿Cómo puedo cambiar mi contraseña?**
Vaya a **Mi Perfil > Cambiar Contraseña**, ingrese su contraseña actual y la nueva contraseña dos veces.
**¿Puedo personalizar el logo o colores del sistema?**
Sí, el administrador puede modificar los archivos de estilo en `static/css/` y el logo en `static/img/`.
### 14.2 Productos e Inventario
**¿El sistema descuenta automáticamente el stock al facturar?**
Sí, cuando se factura un pedido, el stock de cada producto se descuenta automáticamente.
**¿Cómo puedo ver qué productos se están agotando?**
En el Dashboard principal hay una sección de "Alertas de Stock Bajo" que muestra productos con menos de 10 unidades.
**¿Puedo importar productos desde un Excel?**
Actualmente no, pero puede contactar al administrador para solicitar esta funcionalidad.
### 14.3 Mesas y Pedidos
**¿Puedo tener múltiples pedidos en la misma mesa?**
No, cada mesa solo puede tener un pedido activo a la vez. Facture el pedido actual antes de crear uno nuevo.
**¿Qué pasa si un cliente se va sin pagar?**
Debe cancelar el pedido desde el panel de mesas. Esto liberará la mesa y no generará factura.
**¿Puedo transferir un pedido de una mesa a otra?**
Sí, abra el pedido y use la opción "Cambiar Mesa".
### 14.4 Reportes
**¿Cuánto tiempo se guardan los reportes?**
Los reportes se guardan indefinidamente, pero puede eliminarlos manualmente del historial.
**¿Puedo programar el envío automático de reportes por correo?**
Sí, use la función "Reportes Programados" y configure los correos destinatarios.
**¿Los reportes incluyen datos de pedidos cancelados?**
No, solo se incluyen pedidos facturados.
### 14.5 Seguridad y Backups
**¿Con qué frecuencia debo hacer backups?**
Los backups automáticos son diarios. Para mayor seguridad, haga backups manuales antes de:
- Actualizaciones del sistema
- Cambios masivos de datos
- Fin de mes
**¿Dónde debo guardar los backups descargados?**
En un lugar seguro, preferiblemente:
- Disco duro externo
- Servicio de nube (Google Drive, Dropbox)
- Servidor de respaldos de la empresa
**¿Qué pasa si olvido mi contraseña de administrador?**
Contacte al administrador de sistemas. Puede restablecerse desde el servidor usando comandos de Django.
### 14.6 Chatbot
**¿El chatbot guarda mis conversaciones?**
Sí, todas las consultas se guardan en el historial para mejorar el servicio y la experiencia del usuario.
**¿Puedo usar el chatbot para tareas operativas?**
No, el chatbot es solo informativo. No puede crear pedidos, facturar, etc. Solo proporciona información y guía.
**¿El chatbot funciona en otros idiomas?**
Está optimizado para español, pero puede entender preguntas en inglés y responderá en el idioma de la pregunta.
---
## 15. Soporte y Contacto
### 15.1 Soporte Técnico
Para problemas técnicos:
- **Chatbot de Ayuda**: Disponible 24/7 en el sistema
- **Administrador del Sistema**: Contacte a su administrador local
- **Documentación**: Consulte este manual
### 15.2 Actualizaciones del Sistema
El sistema se actualiza periódicamente. Las actualizaciones incluyen:
- Corrección de errores
- Nuevas funcionalidades
- Mejoras de seguridad
- Optimizaciones de rendimiento
**Notificaciones de actualización**: Aparecerán en el Dashboard cuando haya una nueva versión disponible.
### 15.3 Capacitación
Se recomienda capacitación para:
- Nuevos usuarios
- Nuevas funcionalidades
- Cambios importantes en procesos
Contacte a su administrador para programar sesiones de capacitación.
---
## 16. Glosario de Términos
| Término | Definición |
|---------|------------|
| **RAG** | Retrieval-Augmented Generation - Tecnología de IA que combina búsqueda de información con generación de texto |
| **Embedding** | Representación vectorial de texto que permite búsquedas semánticas |
| **Stock** | Cantidad disponible de un producto en inventario |
| **Factura** | Documento que formaliza la venta de productos/servicios |
| **Pedido** | Conjunto de productos solicitados por un cliente, aún no facturado |
| **Rol** | Conjunto de permisos asignados a un tipo de usuario |
| **Backup** | Copia de seguridad de la base de datos |
| **Dashboard** | Panel de control con información resumida del sistema |
| **KPI** | Key Performance Indicator - Indicador clave de rendimiento |
| **Middleware** | Componente que procesa peticiones antes de llegar a las vistas |
| **WebSocket** | Tecnología para comunicación en tiempo real |
---
## 17. Notas de Versión
### Versión Actual: 2.0
**Fecha**: Diciembre 2025
**Nuevas Funcionalidades**:
-  Chatbot RAG con inteligencia artificial
-  Sistema de notificaciones en tiempo real
-  Integración con Google Sign-In
-  Reportes avanzados con gráficos
-  Sistema de backups automáticos
-  Gestión completa de nóminas
-  Facturación mejorada
**Mejoras**:
- Interfaz más intuitiva y moderna
- Mejor rendimiento en consultas de reportes
- Optimización de imágenes (formato WebP)
- Validaciones mejoradas en formularios
---
## 18. Conclusión
Este manual cubre todas las funcionalidades principales del sistema **Bar Galileo**. Para dudas específicas no cubiertas en este documento, utilice el **Chatbot de Ayuda** o contacte a su administrador.
**Recuerde**:
- Realice backups regularmente
- Mantenga sus credenciales seguras
- Cierre sesión al terminar su turno
- Reporte cualquier comportamiento inusual del sistema
¡Gracias por usar Bar Galileo! 
---
**Documento creado**: Diciembre 2025  
**Última actualización**: Diciembre 2025  
**Versión del manual**: 1.0  
**Autor**: Sistema Bar Galileo  
**Contacto**: Chatbot de Ayuda interno