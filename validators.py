import re
import html
from decimal import Decimal, InvalidOperation

# Expresiones regulares oficiales SAT CFDI 4.0
RFC_MORAL_REGEX = re.compile(r"^[A-ZÑ&]{3}\d{6}[A-Z0-9]{3}$")
RFC_FISICA_REGEX = re.compile(r"^[A-ZÑ&]{4}\d{6}[A-Z0-9]{3}$")
CP_REGEX = re.compile(r"^\d{5}$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
CLAVE_SAT_REGEX = re.compile(r"^\d{8}$")
REGIMEN_FISCAL_REGEX = re.compile(r"^\d{3}$")
SKU_REGEX = re.compile(r"^[A-Z0-9._-]{2,50}$", re.IGNORECASE)


def sanitize_string(value, max_length=255):
    """Limpia cadenas, elimina espacios redundantes y caracteres de control."""
    if value is None:
        return ""
    val = str(value).strip()
    # Eliminar caracteres nulos o no imprimibles
    val = "".join(ch for ch in val if ch.isprintable())
    return val[:max_length]


def escape_output(value):
    """Escapa caracteres peligrosos para prevenir XSS."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def validate_rfc(rfc):
    """
    Valida estructura oficial SAT de RFC (12 moral o 13 física).
    Rechaza inyecciones y formatos inválidos.
    """
    if not rfc or not isinstance(rfc, str):
        return False, "El RFC es obligatorio y debe ser una cadena de texto."
    
    clean = rfc.strip().upper()
    if len(clean) == 12:
        if not RFC_MORAL_REGEX.match(clean):
            return False, "El RFC de persona moral debe tener 3 letras, 6 dígitos (fecha AAMMDD) y 3 caracteres de homoclave SAT."
    elif len(clean) == 13:
        if not RFC_FISICA_REGEX.match(clean):
            return False, "El RFC de persona física debe tener 4 letras, 6 dígitos (fecha AAMMDD) y 3 caracteres de homoclave SAT."
    else:
        return False, f"El RFC '{clean}' tiene longitud inválida ({len(clean)} caracteres). Debe ser de 12 (moral) o 13 (física)."
    
    return True, clean


def validate_codigo_postal(cp):
    """Valida código postal oficial de 5 dígitos numéricos."""
    if not cp:
        return False, "El código postal es obligatorio."
    clean = str(cp).strip()
    if not CP_REGEX.match(clean):
        return False, f"El código postal '{clean}' es inválido. Debe constar de exactamente 5 dígitos numéricos."
    return True, clean


def validate_regimen_fiscal(regimen):
    """Valida clave de régimen fiscal SAT (3 dígitos)."""
    if not regimen:
        return True, "601"  # Valor por defecto SAT: General de Ley Personas Morales
    clean = str(regimen).strip()
    if not REGIMEN_FISCAL_REGEX.match(clean):
        return False, f"El régimen fiscal '{clean}' no es válido. Debe ser una clave SAT de 3 dígitos (ej. 601, 612, 626)."
    return True, clean


def validate_correo(correo):
    """Valida formato seguro de correo electrónico."""
    if not correo:
        return True, ""  # Opcional
    clean = str(correo).strip().lower()
    if len(clean) > 255 or not EMAIL_REGEX.match(clean):
        return False, f"El correo electrónico '{clean}' tiene un formato inválido."
    return True, clean


def validate_tipo_persona(tipo):
    """Valida rol fiscal estricto."""
    clean = str(tipo or "").strip().upper()
    if clean not in ("EMISOR", "RECEPTOR"):
        return False, f"El tipo fiscal '{clean}' es inválido. Debe ser 'EMISOR' o 'RECEPTOR'."
    return True, clean


def validate_sku(sku):
    """Valida formato seguro de SKU (2 a 50 caracteres alfanuméricos, guiones o puntos)."""
    if not sku:
        return False, "El SKU del servicio es obligatorio."
    clean = str(sku).strip().upper()
    if not SKU_REGEX.match(clean):
        return False, f"El SKU '{clean}' contiene caracteres inválidos. Solo se permiten letras, números, puntos, guiones y guión bajo (2 a 50 caracteres)."
    return True, clean


def validate_clave_sat(clave):
    """Valida clave de producto/servicio SAT de 8 dígitos."""
    if not clave:
        return True, "80101500"  # Clave SAT genérica de servicios profesionales
    clean = str(clave).strip()
    if not CLAVE_SAT_REGEX.match(clean):
        return False, f"La clave de catálogo SAT '{clean}' debe ser numérica de 8 dígitos (ej. 80101500, 81111508)."
    return True, clean


def validate_precio(precio):
    """Valida que el precio sea un número positivo > 0 y no manipulado."""
    if precio is None or precio == "":
        return False, "El precio base es obligatorio."
    try:
        p_dec = Decimal(str(precio).strip())
        if p_dec <= Decimal("0"):
            return False, "El precio base debe ser un valor positivo estrictamente mayor a 0.00."
        if p_dec > Decimal("99999999.99"):
            return False, "El precio base excede el valor monetario máximo permitido."
        return True, float(p_dec.quantize(Decimal("0.01")))
    except (InvalidOperation, ValueError, TypeError):
        return False, f"El precio '{precio}' no es un número decimal válido."


def validate_partidas(partidas):
    """
    Valida partidas de factura:
    - Debe ser una lista no vacía.
    - Cada partida debe tener servicio_id válido y cantidad entera > 0.
    - Rechaza cantidades negativas, cero, flotantes o irracionales (anti DevTools tampering).
    """
    if not partidas or not isinstance(partidas, list):
        return False, "La factura debe incluir al menos una partida de servicio.", []

    sanitized = []
    for idx, p in enumerate(partidas, 1):
        if not isinstance(p, dict):
            return False, f"La partida #{idx} tiene una estructura de datos inválida.", []

        s_id = str(p.get("servicio_id", "")).strip()
        if not s_id:
            return False, f"La partida #{idx} no especifica un servicio válido.", []

        try:
            qty_raw = p.get("cantidad")
            if qty_raw is None:
                return False, f"La cantidad en la partida #{idx} es obligatoria.", []
            
            # Verificar que sea un número entero
            qty_float = float(qty_raw)
            if not qty_float.is_integer():
                return False, f"La cantidad en la partida #{idx} ({qty_raw}) debe ser un número entero sin decimales.", []

            qty = int(qty_float)
            if qty <= 0:
                return False, f"Manipulación detectada: la cantidad en la partida #{idx} ({qty}) debe ser mayor a 0.", []
            if qty > 9999:
                return False, f"La cantidad en la partida #{idx} ({qty}) excede el límite permitido (9,999 unidades).", []
        except (ValueError, TypeError):
            return False, f"La cantidad en la partida #{idx} no es un número entero válido.", []

        sanitized.append({
            "servicio_id": s_id,
            "cantidad": qty
        })

    return True, "OK", sanitized

