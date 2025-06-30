import traceback
from django.utils.deprecation import MiddlewareMixin
from logs.models import ErroSistema

class LogErroMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        ErroSistema.objects.create(
            view=request.path,
            usuario=request.user.username if hasattr(request, 'user') and request.user.is_authenticated else "Anônimo",
            mensagem=str(exception),
            stack_trace=traceback.format_exc()
        )
        return None  # mantém o comportamento padrão do Django (tela de erro)
