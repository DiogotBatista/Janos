from django.db import models

class ErroSistema(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    view = models.CharField(max_length=255, blank=True)
    usuario = models.CharField(max_length=255, blank=True)
    mensagem = models.TextField()
    stack_trace = models.TextField(blank=True)

    # Novos campos
    corrigido = models.BooleanField("Corrigido?", default=False)
    acao_corretiva = models.TextField("Ação corretiva", blank=True)

    def __str__(self):
        return f"[{self.data.strftime('%d/%m/%Y %H:%M:%S')}] {self.view or 'view desconhecida'}"
