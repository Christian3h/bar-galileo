# Informe de Optimizacion - Bar Galileo
**Fecha:** 4 de marzo de 2026  
**Servidor:** Azure VM - AMD EPYC 7763, 4 vCPUs, 7.8 GB RAM  
**Dominio:** https://www.dominiopruebaprigma.xyz

---

## Resumen ejecutivo

Se realizo una optimizacion completa del servidor de produccion, reemplazando componentes que limitaban el rendimiento y corrigiendo bugs criticos que causaban cierres de sesion aleatorios. El resultado es una aplicacion que aprovecha los 4 nucleos del servidor, con cache distribuido, archivos estaticos servidos eficientemente y sesiones estables entre todos los procesos.

---

## Estado actual del servidor

| Componente | Estado | Uso de memoria |
|---|---|---|
| Web (Gunicorn + 9 workers) | Activo y saludable | 765 MB |
| Base de datos (MySQL 8.0) | Activo y saludable | 403 MB |
| Cache (Redis 7) | Activo y saludable | 1.3 MB |
| Nginx (sistema, con SSL) | Activo | - |

---

## Cambios realizados

### 1. Daphne reemplazado por Gunicorn + Uvicorn Workers

**Antes:** El servidor usaba Daphne como servidor ASGI. Daphne corre en un unico proceso, lo que significa que todas las peticiones HTTP y WebSocket se procesaban de forma secuencial. Con 4 CPUs disponibles en el servidor, se estaban desperdiciando 3 nucleos completos.

**Despues:** Se reemplazo por Gunicorn con workers de tipo UvicornWorker. Gunicorn actua como gestor de procesos y levanta 9 workers (formula estandar: 2 x CPUs + 1), cada uno es un proceso independiente capaz de manejar requests en paralelo. Uvicorn es el worker elegido porque soporta ASGI completo, manteniendo compatibilidad total con Django Channels y WebSockets.

**Por que se cambio Daphne:** Daphne es adecuado para desarrollo o servidores de un solo nucleo. En produccion con multiples CPUs no escala horizontalmente. Gunicorn es el estandar de la industria para Django en produccion por su capacidad de gestionar multiples procesos de forma estable.



---

### 2. Redis - Cache distribuido y Channel Layers

**Antes:** Django usaba  para los WebSockets (notificaciones en tiempo real, estado de mesas). El propio codigo lo marcaba con el comentario . Ademas no habia ningun sistema de cache configurado.

**Problemas que esto causaba:**
- Con multiples workers, cada proceso tiene su propia memoria independiente. Un mensaje WebSocket enviado al worker 3 nunca llegaba a un cliente conectado al worker 7.
- Sin cache, cada peticion repetida consultaba la base de datos desde cero.

**Despues:** Se agrego un contenedor Redis 7 (Alpine). Redis actua como memoria compartida entre todos los workers:

- **Channel Layers:** Los mensajes WebSocket ahora pasan por Redis, garantizando que lleguen al cliente sin importar a que worker este conectado.
- **Cache:** Las consultas repetidas a la base de datos se almacenan en Redis con un TTL de 300 segundos, reduciendo la carga sobre MySQL.

**Por que Redis:** Es el backend recomendado oficialmente por Django Channels para produccion. Ademas sirve tanto para cache como para mensajeria, evitando agregar un servicio extra. Consume solo 1.3 MB de RAM en este momento.



---

### 3. Nginx - Archivos estaticos sin pasar por Python

**Antes:** Nginx ya existia en el servidor con SSL (Let's Encrypt), pero los archivos estaticos (CSS, JavaScript, imagenes) pasaban a traves del proxy hacia Gunicorn, consumiendo workers de Python para servir archivos que no requieren ninguna logica de negocio.

**Despues:** Nginx sirve los archivos estaticos y media directamente desde los volumenes de Docker, sin que Python intervenga.



Los headers  con  hacen que el navegador guarde los archivos estaticos por 30 dias, eliminando peticiones repetidas al servidor en visitas posteriores.

**Por que no se agrego Nginx en Docker:** El servidor ya tenia Nginx instalado con certificados SSL de Let's Encrypt activos. Agregar otro Nginx en Docker hubiera creado conflicto de puertos (80/443 ya ocupados). Se opto por actualizar el Nginx existente.

---

## Bugs criticos corregidos

### Bug 1 - Cierre de sesion aleatorio entre paginas (el mas grave)

**Sintoma:** Al navegar entre paginas la sesion se cerraba sola. El panel requeria dos clicks para entrar.

**Causa raiz:** El archivo  buscaba la clave secreta con  en minusculas, pero el  la define como  en mayusculas. En Linux las variables de entorno son case-sensitive, entonces  retornaba  y Django generaba una clave aleatoria diferente en cada worker al arrancar.

Con Daphne (1 solo proceso) esto no se notaba porque todos los requests usaban la misma clave en memoria. Con 9 workers, las cookies firmadas por un worker eran rechazadas por otro, cerrando la sesion.



### Bug 2 - Error 500 en el login

**Causa:** Se habia eliminado desde el panel de administracion de Django el registro  de la tabla  (tenia id=1). La configuracion  apuntaba a ese registro inexistente.  llama a  al renderizar el login, lanzando  y produciendo el error 500.

**Solucion:** Se inserto un nuevo registro con  apuntando al dominio real .

---

## Archivos de respaldo para reversion

Si se necesita revertir a la configuracion anterior:

| Archivo de respaldo | Reemplaza a |
|---|---|
|  |  |
|  |  |
|  |  |
|  | Config Nginx del sistema |

Para revertir via git al estado anterior a la optimizacion:


---

## Configuracion de Google OAuth

Se reconfiguraron las credenciales de Google OAuth para que funcionen con el dominio de produccion. Las credenciales estan almacenadas en la base de datos (tabla ) asociadas al site . La app fue publicada en Google Cloud Console (estado: Produccion), permitiendo que cualquier cuenta de Google pueda iniciar sesion.

**URIs de callback configuradas en Google Cloud Console:**


---

## Metricas del servidor al momento del informe


