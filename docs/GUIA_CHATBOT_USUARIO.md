# 💬 Cómo Usar el Chatbot de Ayuda - Guía Rápida

## 🎯 ¿Qué es el Chatbot?

Es tu **asistente virtual personal** que conoce todo el Manual de Usuario del sistema. Puedes hacerle preguntas en lenguaje natural y te responderá con información precisa del manual.

---

## 🚀 Cómo Acceder

### Opción 1: Desde el Menú
1. Busca el menú lateral (izquierda)
2. Haz clic en **"Ayuda"** o **"Chatbot"**
3. Se abrirá la ventana del chat

### Opción 2: URL Directa
Escribe en tu navegador:
```
http://localhost:8000/rag-chat/
```

### Opción 3: Botón Flotante (próximamente)
- Aparecerá un ícono flotante en la esquina inferior derecha
- Haz clic para abrir el chat

---

## 📝 Cómo Hacer Preguntas

### ✅ Preguntas que Funcionan Bien

#### Procedimientos
```
✓ "¿Cómo creo un nuevo producto?"
✓ "¿Cómo facturo un pedido?"
✓ "¿Cómo agrego una imagen a un producto?"
✓ "¿Cómo genero un reporte de ventas?"
✓ "¿Cómo hago un backup de la base de datos?"
```

#### Información
```
✓ "¿Qué es el módulo de facturación?"
✓ "¿Para qué sirve el sistema de reportes?"
✓ "¿Qué tipos de reportes puedo generar?"
✓ "¿Cómo funciona el sistema de mesas?"
```

#### Permisos y Roles
```
✓ "¿Qué puede hacer un mesero?"
✓ "¿Quién puede crear usuarios?"
✓ "¿Qué permisos tiene el rol de cajero?"
✓ "¿Cómo asigno un rol a un usuario?"
```

#### Solución de Problemas
```
✓ "¿Qué significa el error 'stock no puede ser negativo'?"
✓ "¿Cómo soluciono el error de sesión expirada?"
✓ "¿Por qué no puedo editar un pedido facturado?"
✓ "¿Qué hago si olvidé mi contraseña?"
```

#### Preguntas Generales
```
✓ "¿Cómo inicio sesión?"
✓ "¿El sistema funciona sin internet?"
✓ "¿Puedo usar el sistema desde mi celular?"
✓ "¿Dónde veo las alertas de stock bajo?"
```

---

### ❌ Preguntas que No Funcionan

```
✗ "Crea un producto para mí"
   → El chatbot NO puede ejecutar acciones, solo informar

✗ "¿Qué hora es?"
   → El chatbot solo responde sobre el sistema Bar Galileo

✗ "¿Cuánto vendí hoy?"
   → Debes usar el módulo de Reportes para ver datos específicos

✗ "Hazme un café"
   → El chatbot es virtual, no puede hacer acciones físicas 😊
```

---

## 💡 Tips para Mejores Respuestas

### 1. Sé Específico
- ❌ "¿Cómo uso productos?"
- ✅ "¿Cómo creo un nuevo producto con imagen?"

### 2. Usa Términos del Sistema
- ❌ "¿Cómo anoto una venta?"
- ✅ "¿Cómo facturo un pedido?"

### 3. Una Pregunta a la Vez
- ❌ "¿Cómo creo productos, mesas y usuarios?"
- ✅ "¿Cómo creo un producto?" (luego haz otra pregunta)

### 4. Reformula si No Entiendes
- Si la respuesta no es clara, intenta con otras palabras
- Ejemplo:
  - Primera: "¿Cómo uso el inventario?"
  - Mejor: "¿Cómo actualizo el stock de un producto?"

### 5. Revisa las Fuentes
- El chatbot te muestra de qué parte del manual sacó la información
- Haz clic en las fuentes para ver más detalles

---

## 🎨 Interfaz del Chatbot

### Elementos de la Pantalla

```
┌─────────────────────────────────────────┐
│  Chat con Documentos            [Upload]│  ← Encabezado
├─────────────────────────────────────────┤
│  [Selector de Manual ▼]                 │  ← Dropdown
├─────────────────────────────────────────┤
│                                         │
│  💬 Bienvenida y mensaje inicial        │
│                                         │
│  👤 Tu pregunta aquí                    │
│                                         │
│  🤖 Respuesta del chatbot               │
│     📚 Fuentes: [Manual p.15]           │
│                                         │
├─────────────────────────────────────────┤
│  Escribe tu pregunta...         [Enviar]│  ← Input
└─────────────────────────────────────────┘
```

### Iconos
- 👤 **Usuario**: Tus preguntas
- 🤖 **Chatbot**: Respuestas del asistente
- 📚 **Fuentes**: Referencias al manual
- ✅ **Éxito**: Operación exitosa
- ⚠️ **Advertencia**: Información importante
- ❌ **Error**: Algo salió mal

---

## 📋 Ejemplos de Conversaciones

### Ejemplo 1: Crear Producto

**👤 Usuario**: ¿Cómo creo un nuevo producto?

**🤖 Chatbot**: Para crear un nuevo producto en Bar Galileo:

1. Ve a **Productos > Agregar Producto**
2. Completa el formulario:
   - **Nombre**: Nombre único del producto
   - **Descripción**: Detalles del producto
   - **Categoría**: Selecciona de la lista
   - **Precio de Compra**: Costo de adquisición
   - **Precio de Venta**: Precio al público (debe ser mayor)
   - **Stock Inicial**: Cantidad disponible
3. Opcionalmente sube imágenes (PNG, JPG, WEBP)
4. Haz clic en **"Guardar"**

**📚 Fuentes**: Manual de Usuario - Sección 4.2 (páginas 12-13)

---

### Ejemplo 2: Solucionar Error

**👤 Usuario**: ¿Qué significa "el precio de venta debe ser mayor que el de compra"?

**🤖 Chatbot**: Este error aparece cuando intentas guardar un producto con un precio de venta igual o menor al precio de compra.

**Solución**:
- Asegúrate de que el precio de venta sea superior al precio de compra
- Ejemplo: Si compras a $1,000, vende a $2,000 o más
- El sistema valida esto para evitar pérdidas

**📚 Fuentes**: Manual de Usuario - Sección 13.2 (página 42)

---

### Ejemplo 3: Permisos

**👤 Usuario**: ¿Qué puede hacer un mesero?

**🤖 Chatbot**: Un mesero en el sistema Bar Galileo tiene los siguientes permisos:

✅ **Puede hacer**:
- Ver productos
- Gestionar mesas (cambiar estados)
- Crear y editar pedidos
- Facturar pedidos

❌ **No puede hacer**:
- Crear o editar productos
- Ver reportes completos
- Gestionar gastos
- Gestionar nóminas
- Administrar usuarios o roles

**📚 Fuentes**: Manual de Usuario - Sección 11.4 (página 38)

---

## 🔄 Si el Chatbot No Responde Bien

### 1. Verifica que el Manual Esté Cargado
En el dropdown superior debe aparecer:
```
📖 Manual de Usuario - Sistema Bar Galileo (X páginas)
```

### 2. Si No Está Cargado
- Contacta al administrador
- El admin debe ejecutar: `python manage.py init_manual`

### 3. Si La Respuesta No Es Clara
- Reformula la pregunta con otras palabras
- Sé más específico
- Divide preguntas complejas en varias simples

### 4. Si El Chatbot Dice "No Encontré Información"
- La información puede no estar en el manual
- Pregunta de otra forma
- Contacta al administrador para actualizar el manual

---

## 🎓 Buenas Prácticas

### ✅ Hacer
- **Explora**: Haz diferentes tipos de preguntas
- **Aprende**: Lee las respuestas completas
- **Consulta fuentes**: Revisa las referencias del manual
- **Practica**: Mientras más uses el chatbot, mejor aprenderás

### ❌ Evitar
- No esperes que ejecute acciones (solo informa)
- No hagas preguntas fuera del contexto del sistema
- No pongas información sensible (contraseñas, datos personales)

---

## 📞 Ayuda Adicional

### Si Necesitas Más Ayuda

1. **Manual Completo**:
   - Pide al administrador el archivo `docs/manual_usuario.md`
   - Es el documento completo con toda la información

2. **Capacitación**:
   - Solicita una sesión de capacitación con tu supervisor

3. **Soporte Técnico**:
   - Contacta al administrador del sistema
   - Reporta errores o problemas técnicos

4. **Sugerencias**:
   - Si una pregunta frecuente no tiene buena respuesta
   - Pide al administrador actualizar el manual

---

## 🌟 Ventajas del Chatbot

✅ **Disponible 24/7**: Responde en cualquier momento  
✅ **Respuestas Instantáneas**: En 2-5 segundos  
✅ **Siempre Actualizado**: Usa el manual más reciente  
✅ **Múltiples Consultas**: Sin límite de preguntas  
✅ **Historial**: Guarda tus consultas anteriores  
✅ **Fuentes Confiables**: Todo del manual oficial  

---

## 🎯 Casos de Uso Comunes

### Nuevo en el Sistema
```
"¿Cómo inicio sesión?"
"¿Dónde veo el menú principal?"
"¿Qué es cada módulo?"
```

### Tareas Diarias
```
"¿Cómo creo un pedido?"
"¿Cómo facturo?"
"¿Cómo registro un gasto?"
```

### Problemas
```
"¿Por qué no puedo facturar?"
"¿Qué significa este error?"
"¿Cómo recupero mi contraseña?"
```

### Aprendizaje
```
"¿Cómo genero reportes?"
"¿Cómo funciona el sistema de backups?"
"¿Qué permisos necesito para X?"
```

---

## 📈 Mejora Continua

El chatbot mejora constantemente:
- Tu feedback ayuda a mejorar el manual
- Preguntas frecuentes se agregan al manual
- El administrador actualiza según las necesidades

**¿Encontraste algo que no está claro?**
→ Pide al administrador agregar esa información al manual

---

**¡Explora, pregunta y aprende!** 🚀

El chatbot es tu mejor herramienta para dominar el sistema Bar Galileo.

---

**Última actualización**: Diciembre 2025  
**Versión**: 1.0
