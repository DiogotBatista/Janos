from django.contrib import admin
from .models import Projetista, Polo, Chave, CustomUsuario, Aviso, EmailConfig
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUsuarioCreateForm, CustomUsuarioChangeForm
from django.shortcuts import redirect
from django.http import HttpResponse
from openpyxl import Workbook

def atribuir_projetista(modeladmin, request, queryset):
    # Aqui você pode armazenar os IDs em sessão ou outra lógica
    request.session['chave_ids'] = list(queryset.values_list('id', flat=True))
    return redirect('atribuir_projetista')

class SemProjetistaFilter(admin.SimpleListFilter):
    title = ('Atribuição')
    parameter_name = 'projetista'

    def lookups(self, request, model_admin):
        return (
            ('nao_atribuido', ('Não Atribuído')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'nao_atribuido':
            return queryset.filter(projetista__isnull=True)

@admin.register(CustomUsuario)
class CustomUsuarioAdmin(UserAdmin):
    add_form = CustomUsuarioCreateForm
    form = CustomUsuarioChangeForm
    model = CustomUsuario
    list_display = ('first_name', 'last_name', 'email', 'is_staff','last_login', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(Projetista)
class ProjetistaAdmin(admin.ModelAdmin):
    list_display = ('projetista', 'email', 'ativo')

@admin.register(Polo)
class PoloAdmin(admin.ModelAdmin):
    list_display = ('polo',)

def exportar_para_excel(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="relatorio_chaves.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = "Chaves"

    # Adicionando os cabeçalhos
    colunas = ['Chave', 'Projetista', 'NS', 'Poste/Ponto', 'Coordenada', 'Polo', 'Município', 'Observação', 'Dt de Inclusão', 'Dt de Modificação']
    ws.append(colunas)

    # Adicionando os dados
    for obj in queryset:
        data = [
            obj.chave,
            obj.projetista.projetista if obj.projetista else '',  # Ajuste conforme o modelo de relacionamento
            obj.ns,
            obj.poste,
            obj.coordenada,
            obj.polo.polo if obj.polo else '',  # Ajuste conforme o modelo de relacionamento
            obj.municipio,
            obj.observacao,
            obj.data_inclusao.strftime("%Y-%m-%d %H:%M") if obj.data_inclusao else '',
            obj.data_modificacao.strftime("%Y-%m-%d %H:%M") if obj.data_modificacao else '',
        ]
        ws.append(data)

    wb.save(response)
    return response

exportar_para_excel.short_description = "Exportar Selecionados para Excel"


@admin.register(Chave)
class ChaveAdmin(admin.ModelAdmin):
    list_display = ('chave', 'projetista', 'polo', 'ns', 'coordenada', 'poste', 'municipio', 'chamado', 'data_chamado', 'observacao', 'data_inclusao', 'data_modificacao')
    search_fields = ['chave', 'ns', 'projetista__projetista', 'municipio', 'polo__polo', 'observacao']
    change_list_template = "custom_change_list.html"
    actions = [atribuir_projetista, exportar_para_excel]
    list_filter = (SemProjetistaFilter, 'projetista')  # Adicionando o filtro personalizado


@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_criacao', 'ordenacao')
    list_filter = ('data_criacao',)

@admin.register(EmailConfig)
class EmailConfig(admin.ModelAdmin):
    list_display = ('nome', 'email')
    list_filter = ('nome',)


admin.site.site_header = "JANOS - Administração do Banco de Dados"
admin.site.site_title = "JANOS - Administração"
admin.site.index_title = "JANOS - Página de administração"
admin.site.site_url = "/janus/menu/"