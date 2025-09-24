# core/messages.py
from django.contrib import messages
from django.utils.text import capfirst

# ========== Helpers internos ==================================================

def _model_verbose_name(obj_or_model):
    """
    Retorna o verbose_name do model, capitalizado.
    Aceita a classe do model OU uma instância.
    """
    model = obj_or_model if hasattr(obj_or_model, "_meta") else obj_or_model.__class__
    return capfirst(model._meta.verbose_name)

def _obj_display(obj):
    """
    Texto padrão para exibir o objeto. Usa __str__ se existir.
    """
    try:
        return str(obj)
    except Exception:
        return f"ID {getattr(obj, 'pk', '—')}"

# ========== Mensagens prontas ================================================

def add_created_message(request, obj, extra_text: str | None = None):
    model_name = _model_verbose_name(obj)
    text = f"{model_name} “{_obj_display(obj)}” criado(a) com sucesso."
    if extra_text:
        text = f"{text} {extra_text}"
    messages.success(request, text)

def add_updated_message(request, obj, extra_text: str | None = None):
    model_name = _model_verbose_name(obj)
    text = f"{model_name} “{_obj_display(obj)}” atualizado(a) com sucesso."
    if extra_text:
        text = f"{text} {extra_text}"
    messages.success(request, text)

def add_deleted_message(request, model_or_obj, extra_text: str | None = None):
    model_name = _model_verbose_name(model_or_obj)
    text = f"{model_name} excluído(a) com sucesso."
    if extra_text:
        text = f"{text} {extra_text}"
    messages.success(request, text)

def add_info_message(request, text: str):
    messages.info(request, text)

def add_warning_message(request, text: str):
    messages.warning(request, text)

def add_error_message(request, text: str = "Erro ao processar a ação."):
    messages.error(request, text)

# ========== Atalhos para FBVs =================================================

def message_created_ok(request, obj, extra_text: str | None = None):
    add_created_message(request, obj, extra_text)

def message_updated_ok(request, obj, extra_text: str | None = None):
    add_updated_message(request, obj, extra_text)

def message_deleted_ok(request, model_or_obj, extra_text: str | None = None):
    add_deleted_message(request, model_or_obj, extra_text)

def message_error(request, text: str = "Erro ao processar a ação."):
    add_error_message(request, text)


'''
COMO UTILIZAR NAS VIEWS

from core.messages import message_created_ok, message_updated_ok, message_deleted_ok, message_error

# Depois de salvar:
message_created_ok(request, obj)

# Depois de atualizar:
message_updated_ok(request, obj, extra_text="(verifique o status)")

# Depois de excluir:
message_deleted_ok(request, ModelClass)

# Em erro:
message_error(request, "Falha na importação da planilha.")

'''