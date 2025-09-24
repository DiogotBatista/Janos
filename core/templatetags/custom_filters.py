from django import template
from django.utils.safestring import mark_safe
from datetime import datetime, date
import re
import locale

register = template.Library()

# --- Helpers internos ---------------------------------------------------------

def _to_decimal(value, default=0.0):
    """
    Converte strings com vírgula ou ponto para float.
    """
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if s == '':
        return default
    # Trata formatos "1.234,56" e "1234,56"
    s = s.replace('.', '').replace(',', '.')
    try:
        return float(s)
    except Exception:
        try:
            return float(value)
        except Exception:
            return default

def _only_digits(s):
    return re.sub(r'\D+', '', str(s or ''))

# --- Filtros de apresentação --------------------------------------------------

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Adiciona classe CSS em widgets de formulário no template.
    Ex.: {{ form.campo|add_class:"form-control is-invalid" }}
    """
    try:
        return field.as_widget(attrs={"class": css_class})
    except AttributeError:
        return field

@register.filter(name='add_placeholder')
def add_placeholder(field, text):
    """
    Define placeholder em widgets de formulário no template.
    """
    try:
        return field.as_widget(attrs={"placeholder": text})
    except AttributeError:
        return field

@register.filter(name='attr')
def attr(field, args):
    """
    Define um ou mais atributos em um widget.
    Ex.: {{ form.email|attr:"autocomplete=off, data-x=1" }}
    """
    try:
        pairs = [x.strip() for x in str(args).split(',') if x.strip()]
        attrs = {}
        for p in pairs:
            if '=' in p:
                k, v = p.split('=', 1)
                attrs[k.strip()] = v.strip()
        return field.as_widget(attrs=attrs)
    except AttributeError:
        return field

@register.filter(name="split")
def split(value, separator):
    return value.split(separator)


# --- Formatação numérica / monetária -----------------------------------------

@register.filter(name='br_number')
def br_number(value, digits=2):
    """
    Formata número no padrão brasileiro: 1.234,56
    """
    n = _to_decimal(value, 0.0)
    fmt = f"{{:,.{int(digits)}f}}".format(n)
    # troca separadores
    return fmt.replace(',', 'X').replace('.', ',').replace('X', '.')

@register.filter(name='br_currency')
def br_currency(value, prefix='R$'):
    """
    Formata moeda no padrão BR: R$ 1.234,56
    """
    n = _to_decimal(value, 0.0)
    fmt = f"{prefix} {{:,.2f}}".format(n)
    return fmt.replace(',', 'X').replace('.', ',').replace('X', '.')

# --- Datas --------------------------------------------------------------------

@register.filter(name='date_br')
def date_br(value):
    """
    Converte date/datetime/string -> dd/mm/aaaa
    """
    if isinstance(value, (datetime, date)):
        return value.strftime('%d/%m/%Y')
    s = str(value).strip()
    for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%d/%m/%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(s, fmt).strftime('%d/%m/%Y')
        except Exception:
            pass
    return s

@register.filter(name='datetime_br')
def datetime_br(value):
    """
    Converte date/datetime/string -> dd/mm/aaaa HH:MM
    """
    if isinstance(value, (datetime, date)):
        if isinstance(value, date) and not isinstance(value, datetime):
            value = datetime.combine(value, datetime.min.time())
        return value.strftime('%d/%m/%Y %H:%M')
    s = str(value).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%d/%m/%Y %H:%M'):
        try:
            return datetime.strptime(s, fmt).strftime('%d/%m/%Y %H:%M')
        except Exception:
            pass
    return s

# --- Operações simples --------------------------------------------------------

@register.filter(name='to_int')
def to_int(value, default=0):
    try:
        return int(float(value))
    except Exception:
        return int(default)

@register.filter(name='to_float')
def to_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)

@register.filter(name='mul')
def mul(a, b):
    return _to_decimal(a) * _to_decimal(b)

@register.filter(name='div')
def div(a, b):
    b = _to_decimal(b, 0.0)
    return (_to_decimal(a) / b) if b else 0.0

@register.filter(name='percent')
def percent(value, digits=0):
    """
    Converte 0.23 -> 23% ; 23 -> 23%
    """
    v = _to_decimal(value, 0.0)
    if v <= 1.0:
        v *= 100.0
    fmt = f"{{:.{int(digits)}f}}%".format(v)
    return fmt.replace('.', ',')

# --- Masks BR -----------------------------------------------------------------

@register.filter(name='mask_cnpj')
def mask_cnpj(value):
    d = _only_digits(value)
    if len(d) != 14:
        return value
    return f"{d[0:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:14]}"

@register.filter(name='mask_cpf')
def mask_cpf(value):
    d = _only_digits(value)
    if len(d) != 11:
        return value
    return f"{d[0:3]}.{d[3:6]}.{d[6:9]}-{d[9:11]}"

@register.filter(name='mask_phone_br')
def mask_phone_br(value):
    d = _only_digits(value)
    if len(d) == 11:  # celular
        return f"({d[0:2]}) {d[2:7]}-{d[7:11]}"
    if len(d) == 10:  # fixo
        return f"({d[0:2]}) {d[2:6]}-{d[6:10]}"
    return value

# --- Booleanos ----------------------------------------------------------------

@register.filter(name='yesno_br')
def yesno_br(value, mapping="Sim,Não"):
    """
    Ex.: {{ obj.ativo|yesno_br }}  -> "Sim" ou "Não"
    """
    parts = [p.strip() for p in mapping.split(',')]
    yes = parts[0] if len(parts) > 0 else 'Sim'
    no = parts[1] if len(parts) > 1 else 'Não'
    return yes if bool(value) else no
