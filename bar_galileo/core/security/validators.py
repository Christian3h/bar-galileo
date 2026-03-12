"""
Validadores de seguridad para prevenir SSTI (Server-Side Template Injection)
y otros ataques de inyección en Django.

用法:
    from core.security.validators import EmailSSTIValidator, NameSSTIValidator
    
    class MiForm(forms.Form):
        email = forms.CharField(validators=[EmailSSTIValidator()])
        nombre = forms.CharField(validators=[NameSSTIValidator()])
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# ============================================================================
# PATRONES PELIGROSOS - NO MODIFICAR
# ============================================================================

# Caracteres y patrones que indican posible SSTI/XSS
SSTI_PATTERNS = [
    r'\{\{',           # Django template variables
    r'\}\}',           # Django template variables  
    r'\{%',            # Django template tags
    r'%\}',            # Django template tags
    r'<\s*script',     # Script tags
    r'<\s*iframe',     # Iframe injection
    r'<\s*object',    # Object injection
    r'<\s*embed',      # Embed injection
    r'javascript:',    # JavaScript protocol
    r'on\w+\s*=',      # Event handlers (onclick, onerror, etc.)
    r'data:',          # Data URLs
    r'vbscript:',      # VBScript protocol
    r'<\s*img',        # Image tag with potential events
    r'<\s*svg',        # SVG with embedded scripts
    r'\$\{',           # Template literals JS
    r'\$\(',           # Command substitution
    r'`',              # Backticks (command substitution)
    r'<%',             # ERB templates
    r'%>',             # ERB templates
    r'#\{',            # Ruby interpolation
]

# Compilar regex para mejor rendimiento
COMPILED_SSTI_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in SSTI_PATTERNS]


def validar_ssti(valor, nombre_campo="Campo"):
    """
    Validador genérico que detecta patrones SSTI/XSS.
    
    Args:
        valor: El valor a validar
        nombre_campo: Nombre del campo para el mensaje de error
    
    Raises:
        ValidationError: Si se detecta algún patrón peligroso
    """
    if not valor:
        return
    
    valor_str = str(valor)
    
    for pattern in COMPILED_SSTI_PATTERNS:
        if pattern.search(valor_str):
            raise ValidationError(
                _(f"{nombre_campo} contiene caracteres no permitidos."),
                code='invalid_characters'
            )


# ============================================================================
# VALIDADORES ESPECÍFICOS POR TIPO DE CAMPO
# ============================================================================

class BaseSSTIValidator:
    """
    Validador base que bloquea patrones SSTI/XSS genéricos.
    """
    
    def __call__(self, value):
        validar_ssti(value, self.nombre_campo)
    
    @property
    def nombre_campo(self):
        return self.__class__.__name__.replace('SSTIValidator', '')


class EmailSSTIValidator(BaseSSTIValidator):
    """
    Validador para emails:
    - Regex estricto de formato email
    - Bloquea patrones SSTI/XSS
    - Solo permite caracteres válidos en emails
    
    Ejemplo:
        class MiForm(forms.Form):
            email = forms.CharField(validators=[EmailSSTIValidator()])
    """
    
    # Regex estricta para email - bloquea {{ }} {% %} automáticamente
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
    
    def __call__(self, value):
        if not value:
            return
        
        value_str = str(value).strip()
        
        # 1. Primero verificar que sea un email válido
        if not self.EMAIL_REGEX.match(value_str):
            raise ValidationError(
                _('Ingresa un correo electrónico válido.'),
                code='invalid_email'
            )
        
        # 2. Verificar patrones SSTI
        super().__call__(value)


class NameSSTIValidator(BaseSSTIValidator):
    """
    Validador para nombres (personas, productos, etc.):
    - Solo letras, espacios, guiones, apóstrofos
    - Longitud controlada
    - Bloquea patrones SSTI
    
    Ejemplo:
        class MiForm(forms.Form):
            nombre = forms.CharField(validators=[NameSSTIValidator()])
    """
    
    # Solo letras (incluyendo español), espacios, guiones, apóstrofos
    NAME_REGEX = re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$')
    
    def __call__(self, value):
        if not value:
            return
        
        value_str = str(value).strip()
        
        # 1. Verificar formato de nombre
        if not self.NAME_REGEX.match(value_str):
            raise ValidationError(
                _('El nombre solo puede contener letras, espacios, guiones y apóstrofos.'),
                code='invalid_name'
            )
        
        # 2. Longitud máxima
        if len(value_str) > 100:
            raise ValidationError(
                _('El nombre no puede exceder 100 caracteres.'),
                code='name_too_long'
            )
        
        # 3. Verificar SSTI
        super().__call__(value)


class ProductSSTIValidator(BaseSSTIValidator):
    """
    Validador para nombres de productos:
    - Alfanumérico + símbolos seguros
    - Bloquea patrones SSTI
    
    Símbolos permitidos: - _ . , ( ) espacios
    """
    
    PRODUCT_REGEX = re.compile(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-_.,()]+$')
    
    def __call__(self, value):
        if not value:
            return
        
        value_str = str(value).strip()
        
        if not self.PRODUCT_REGEX.match(value_str):
            raise ValidationError(
                _('El nombre del producto contiene caracteres no permitidos.'),
                code='invalid_product_name'
            )
        
        if len(value_str) > 200:
            raise ValidationError(
                _('El nombre del producto no puede exceder 200 caracteres.'),
                code='product_name_too_long'
            )
        
        super().__call__(value)


class DescriptionSSTIValidator(BaseSSTIValidator):
    """
    Validador para descripciones (más permisivo):
    - Permite más símbolos
    - Pero sigue bloqueando lo peligroso
    
    Excluye: { } < > % ` $ ; | &
    """
    
    DESC_REGEX = re.compile(r'^[^{}<>%`$;|&]+$')
    
    def __call__(self, value):
        if not value:
            return
        
        value_str = str(value).strip()
        
        if not self.DESC_REGEX.match(value_str):
            raise ValidationError(
                _('La descripción contiene caracteres no permitidos: { } < > % ` $ ; | &'),
                code='invalid_description'
            )
        
        super().__call__(value)


class PasswordSSTIValidator:
    """
    Validador para contraseñas:
    - NO bloquea caracteres especiales (los usuarios deben poder usar cualquier carácter)
    - Solo valida longitud (mínimo 8, máximo 128)
    - Esto permite mayor seguridad real (más caracteres = más entropy)
    
    NOTA: No hereda de BaseSSTIValidator porque las contraseñas
    DEBEN poder tener {{ }} etc. para mayor seguridad.
    """
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    def __call__(self, value):
        if not value:
            raise ValidationError(
                _('La contraseña no puede estar vacía.'),
                code='password_empty'
            )
        
        value_str = str(value)
        
        if len(value_str) < self.MIN_LENGTH:
            raise ValidationError(
                _(f'La contraseña debe tener al menos {self.MIN_LENGTH} caracteres.'),
                code='password_too_short'
            )
        
        if len(value_str) > self.MAX_LENGTH:
            raise ValidationError(
                _(f'La contraseña no puede exceder {self.MAX_LENGTH} caracteres.'),
                code='password_too_long'
            )


class PhoneSSTIValidator(BaseSSTIValidator):
    """
    Validador para teléfonos:
    - Solo números, espacios, guiones, paréntesis, +
    """
    
    PHONE_REGEX = re.compile(r'^[0-9\s\-\(\)\+]+$')
    
    def __call__(self, value):
        if not value:
            return
        
        value_str = str(value).strip()
        
        if not self.PHONE_REGEX.match(value_str):
            raise ValidationError(
                _('El teléfono contiene caracteres no válidos.'),
                code='invalid_phone'
            )
        
        if len(value_str) > 20:
            raise ValidationError(
                _('El teléfono no puede exceder 20 caracteres.'),
                code='phone_too_long'
            )
        
        super().__call__(value)


class GenericSSTIValidator(BaseSSTIValidator):
    """
    Validador genérico para cualquier campo de texto:
    - Bloquea cualquier patrón SSTI/XSS conocido
    - Recomendado para campos de texto libre
    
    Excluye: { } < > % ` $ ; | &
    """
    
    GENERIC_REGEX = re.compile(r'^[^{}<>%`$;|&]+$')
    
    def __call__(self, value):
        if not value:
            return
        
        value_str = str(value).strip()
        
        if not self.GENERIC_REGEX.match(value_str):
            raise ValidationError(
                _('Este campo contiene caracteres no permitidos.'),
                code='invalid_characters'
            )
        
        super().__call__(value)
    
    @property
    def nombre_campo(self):
        return "Campo"
