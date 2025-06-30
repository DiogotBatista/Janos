from django.contrib import admin
from .models import ErroSistema

@admin.register(ErroSistema)
class ErroSistemaAdmin(admin.ModelAdmin):
    list_display = ('data', 'view', 'usuario', 'mensagem_curta', 'corrigido', 'icone_suporte')
    search_fields = ('view', 'usuario', 'mensagem', 'stack_trace', 'acao_corretiva')
    list_filter = ('usuario', 'view', 'data', 'corrigido')
    list_editable = ('corrigido',)
    readonly_fields = ('data', 'view', 'usuario', 'mensagem', 'stack_trace')
    fieldsets = (
        (None, {
            'fields': ('data', 'view', 'usuario', 'mensagem', 'stack_trace')
        }),
        ('Tratamento do erro', {
            'fields': ('corrigido', 'acao_corretiva'),
            'classes': ('collapse',),
        }),
    )

    def mensagem_curta(self, obj):
        return (obj.mensagem[:60] + '...') if len(obj.mensagem) > 60 else obj.mensagem
    mensagem_curta.short_description = "Mensagem"

    def icone_suporte(self, obj):
        return "✅" if obj.corrigido else "🚨"
    icone_suporte.short_description = "Status"
