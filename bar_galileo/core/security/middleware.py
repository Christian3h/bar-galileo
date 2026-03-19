"""
Middleware de seguridad para prevenir ataques SSTI y XSS en Django.

Este middleware:
1. Escanea todos los datos POST/PUT/PATCH
2. Detecta y bloquea patrones de inyección
3. Loggea intentos de ataque para auditoría

⚠️ NOTA: Este middleware complementa (no reemplaza) la validación en forms.
         Es una capa adicional de seguridad.
"""

import re
import logging
from django.http import HttpResponseBadRequest
from django.conf import settings

logger = logging.getLogger('security')


# ============================================================================
# PATRONES DE ATAQUE - NO MODIFICAR
# ============================================================================

# Patrones que indicam posible intento de SSTI/XSS
ATTACK_PATTERNS = [
    # Django templates
    (r'\{\{', 'Django template injection ({{}})'),
    (r'\{%', 'Django template tag injection ({%)'),
    
    # XSS básico
    (r'<\s*script', 'XSS - Script tag'),
    (r'javascript:', 'XSS - JavaScript protocol'),
    (r'on\w+\s*=', 'XSS - Event handler'),
    
    # Command injection
    (r'`.*`', 'Command injection (backticks)'),
    (r'\$\(', 'Command injection ($())'),
    (r'\$\{', 'Template literal injection'),
    
    # Other template engines
    (r'<%', 'ERB/Ruby template injection'),
    (r'#\{', 'Ruby interpolation'),
    
    # Data URLs
    (r'data:', 'Data URL injection'),
    (r'vbscript:', 'VBScript injection'),
]

# Compilar patrones
COMPILED_PATTERNS = [(re.compile(pattern, re.IGNORECASE), msg) for pattern, msg in ATTACK_PATTERNS]


class SecurityValidationMiddleware:
    """
    Middleware que valida todos los inputs contra ataques de inyección.
    
    Configuración en settings.py:
    
        SECURITY_MIDDLEWARE_ENABLED = True
        SECURITY_MIDDLEWARE_LOG_ONLY = False  # True = solo log, no bloquear
    
    Rutas excluidas (no se validan):
        - /admin/ (Django admin ya tiene su propia seguridad)
        - /api/auth/ (autenticación)
        - /health/ (health checks)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'SECURITY_MIDDLEWARE_ENABLED', True)
        self.log_only = getattr(settings, 'SECURITY_MIDDLEWARE_LOG_ONLY', False)
        
        # Rutas a excluir de la validación
        self.exclude_paths = [
            '/admin/',
            '/api/',
            '/health/',
            '/accounts/',
            '/captcha/',
            '/users/',
            '/products/',
            '/reportes/',
            '/expenses/',
            '/nominas/',
            '/static/',
            '/media/',
            '/tables/',
            '/roles/',
            '/facturacion/',
            '/site_images/',
            '/google_chat/',
            '/rag_chat/',
            '/notifications/',
            '/backups/',
        ]
    
    def __call__(self, request):
        # Skip si está desactivado
        if not self.enabled:
            return self.get_response(request)
        
        # Skip para rutas excluidas
        if self._should_skip(request.path):
            return self.get_response(request)
        
        # Solo validar métodos con body
        if request.method in ['POST', 'PUT', 'PATCH']:
            attack_found = self._check_request(request)
            
            if attack_found:
                # Log del intento de ataque
                logger.warning(
                    f"[SECURITY] Posible ataque SSTI/XSS detectado | "
                    f"IP: {self._get_client_ip(request)} | "
                    f"Path: {request.path} | "
                    f"Pattern: {attack_found}"
                )
                
                if self.log_only:
                    # Solo loguear, no bloquear
                    pass
                else:
                    # Bloquear request
                    return HttpResponseBadRequest(
                        "Solicitud rechazada: Caracteres no permitidos detectados."
                    )
        
        response = self.get_response(request)
        return response
    
    def _should_skip(self, path):
        """Determina si la ruta debe ser excluida de la validación."""
        for exclude in self.exclude_paths:
            if path.startswith(exclude):
                return True
        return False
    
    def _get_client_ip(self, request):
        """Obtiene la IP real del cliente (considera proxies)."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
    
    def _check_request(self, request):
        """
        Escanea todos los datos del request en busca de patrones de ataque.
        
        Returns:
            Tupla (pattern_found, message) o None si no hay ataque
        """
        # Check POST data
        if hasattr(request, 'POST') and request.POST:
            for key, value in request.POST.items():
                if value:
                    attack = self._scan_value(str(value))
                    if attack:
                        return attack
        
        # Check PUT/PATCH data (JSON)
        if request.method in ['PUT', 'PATCH']:
            try:
                if hasattr(request, 'data') and request.data:
                    # Django REST Framework
                    attack = self._scan_dict(request.data)
                    if attack:
                        return attack
                elif hasattr(request, 'body') and request.body:
                    import json
                    data = json.loads(request.body)
                    attack = self._scan_dict(data)
                    if attack:
                        return attack
            except (json.JSONDecodeError, AttributeError):
                pass
        
        return None
    
    def _scan_dict(self, data, prefix=''):
        """Escanea un diccionario recursivamente."""
        if isinstance(data, dict):
            for key, value in data.items():
                key_str = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    result = self._scan_dict(value, key_str)
                    if result:
                        return result
                else:
                    attack = self._scan_value(str(value), key_str)
                    if attack:
                        return attack
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    result = self._scan_dict(item, f"{prefix}[{i}]")
                    if result:
                        return result
                else:
                    attack = self._scan_value(str(item), f"{prefix}[{i}]")
                    if attack:
                        return attack
        return None
    
    def _scan_value(self, value, field_name=''):
        """Escanea un valor individual."""
        if not value or len(value) < 2:
            return None
        
        for pattern, message in COMPILED_PATTERNS:
            if pattern.search(value):
                return f"{message} | Field: {field_name}" if field_name else message
        
        return None


class RateLimitMiddleware:
    """
    Middleware simple de rate limiting para prevenir brute force.
    
    Configuración en settings.py:
    
        RATE_LIMIT_ENABLED = True
        RATE_LIMIT_REQUESTS = 100  # Máximo requests por ventana
        RATE_LIMIT_WINDOW = 60     # Ventana en segundos
    """
    
    # Almacenamiento simple en memoria (en producción usar Redis)
    _requests = {}
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'RATE_LIMIT_ENABLED', True)
        self.max_requests = getattr(settings, 'RATE_LIMIT_REQUESTS', 100)
        self.window = getattr(settings, 'RATE_LIMIT_WINDOW', 60)
    
    def __call__(self, request):
        if not self.enabled:
            return self.get_response(request)
        
        # Skip para rutas de autenticación (manejado por Django)
        if request.path.startswith('/admin/') or request.path.startswith('/accounts/'):
            return self.get_response(request)
        
        client_ip = self._get_client_ip(request)
        
        if self._is_rate_limited(client_ip):
            logger.warning(
                f"[RATE LIMIT] IP bloqueada por exceder límite: {client_ip}"
            )
            return HttpResponseBadRequest(
                "Demasiadas solicitudes. Intenta de nuevo más tarde."
            )
        
        response = self.get_response(request)
        return response
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
    
    def _is_rate_limited(self, ip):
        import time
        
        now = time.time()
        window_start = now - self.window
        
        # Limpiar entradas antiguas
        self._requests = {k: v for k, v in self._requests.items() if v > window_start}
        
        # Contar requests en la ventana
        count = self._requests.get(ip, 0)
        
        if count >= self.max_requests:
            return True
        
        # Incrementar contador
        self._requests[ip] = count + 1
        return False
