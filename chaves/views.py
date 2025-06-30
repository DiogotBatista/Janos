from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from scripts.importar_chaves import cadastrar_chaves_from_planilha
from .forms import AtribuirProjetistaForm, ConfirmacaoSolicitacaoForm
from .forms import ChaveForm, PlanilhaUploadForm
from .models import Chave, Projetista, Aviso


def view_index(request):
    return render(request, 'index.html')

@login_required(login_url='/janus/login')  # Substitua '/caminho_para_login/' pela URL da sua página de login
def view_importar_chaves(request):
    is_superuser = request.user.is_superuser
    usuario_no_grupo_supervisor = request.user.groups.filter(name='supervisor_projetos').exists()

    # Verifica se o usuário é superusuário ou pertence ao grupo 'topografia'
    if not (is_superuser or usuario_no_grupo_supervisor):
        raise PermissionDenied

    if request.method == 'POST':
        form = PlanilhaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            planilha = request.FILES['planilha']
            cadastrar_chaves_from_planilha(request, planilha)
            # return HttpResponse("Chaves importadas com sucesso!")
    else:
        form = PlanilhaUploadForm()
    return render(request, 'upload_planilha.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('janus_view')  # Altere 'index.html' para 'index' se estiver usando o nome da URL
        else:
            form = AuthenticationForm()
            form.fields['username'].widget.attrs.update({'class': 'form-control'})
            form.fields['password'].widget.attrs.update({'class': 'form-control'})
            messages.error(request, 'Usuário ou senha inválidos')
    else:
        form = AuthenticationForm()
        form.fields['username'].widget.attrs.update({'class': 'form-control'})
        form.fields['password'].widget.attrs.update({'class': 'form-control'})
    return render(request, 'login.html', {'form': form})

@login_required(login_url='/janus/login')  # Substitua '/caminho_para_login/' pela URL da sua página de login
def gerenciar_chaves(request):
    usuario_logado = request.user
    is_superuser = request.user.is_superuser
    usuario_no_grupo_tecnicos = request.user.groups.filter(name='tecnicos').exists()
    usuario_no_grupo_supervisor = request.user.groups.filter(name='supervisor_projetos').exists()

    # Verifica se o usuário é superusuário ou pertence ao grupo 'topografia'
    if not (is_superuser or usuario_no_grupo_tecnicos or usuario_no_grupo_supervisor):
        raise PermissionDenied

    # Verifica se o usuário é superusuário ou está no grupo 'supervisor_projetos'
    if usuario_logado.is_superuser or usuario_logado.groups.filter(name='supervisor_projetos').exists():
        chaves = Chave.objects.all()
    else:
        # Ajuste a consulta para buscar o Projetista relacionado ao CustomUsuario
        chaves = Chave.objects.filter(projetista__email__email=usuario_logado.email)

    # Lógica de pesquisa
    ns_search = request.GET.get('ns_search', '')
    chave_search = request.GET.get('chave_search', '')
    projetista_search = request.GET.get('projetista_search', '')

    if ns_search:
        chaves = chaves.filter(ns__icontains=ns_search)
    if chave_search:
        chaves = chaves.filter(chave__icontains=chave_search)
    if projetista_search:
        chaves = chaves.filter(projetista__projetista__icontains=projetista_search)

    if 'sem_projeto' in request.GET:
        chaves = chaves.filter(ns__isnull=True)

    # Adicionando paginação
    paginator = Paginator(chaves, 20)
    page_number = request.GET.get('page')
    chaves_page = paginator.get_page(page_number)

    # Passando as verificações para o template
    context = {
        'chaves': chaves_page,
        'is_superuser': is_superuser,
        'usuario_no_grupo_supervisor': usuario_no_grupo_supervisor,
    }

    return render(request, 'gerenciar_chaves.html', context)

@login_required(login_url='/janus/login')
def janus_view(request):
    usuario_no_grupo_topografia = request.user.groups.filter(name='topografia').exists()
    is_superuser = request.user.is_superuser
    usuario_no_grupo_supervisor = request.user.groups.filter(name='supervisor_projetos').exists()
    usuario_no_grupo_tecnicos = request.user.groups.filter(name='tecnicos').exists()
    avisos = Aviso.objects.all()
    context = {
        'first_name': request.user.first_name if request.user.is_authenticated else 'Visitante',
        'usuario_no_grupo_topografia': usuario_no_grupo_topografia,
        'is_superuser': is_superuser,
        'usuario_no_grupo_supervisor': usuario_no_grupo_supervisor,
        'usuario_no_grupo_tecnicos': usuario_no_grupo_tecnicos,
        'avisos': avisos,
    }
    return render(request, 'menu.html', context)

@login_required(login_url='/janus/login')  # Substitua '/caminho_para_login/' pela URL da sua página de login
def editar_chave(request, id):
    chave = get_object_or_404(Chave, id=id)
    is_superuser = request.user.is_superuser
    email_logado = request.user.email

    # Verifica se o usuário logado é o projetista associado à chave ou tem permissões especiais
    if not (
            is_superuser or
            (chave.projetista and chave.projetista.email.email == email_logado) or
            request.user.groups.filter(name__in=['supervisor_projetos']).exists()
    ):
        raise PermissionDenied

    if request.method == 'POST':
        form = ChaveForm(request.POST, instance=chave)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chave atualizada com sucesso!')
            # return redirect('gerenciar_chaves')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ChaveForm(instance=chave)

    return render(request, 'editar_chave.html', {'form': form})

@login_required(login_url='/janus/login/')
def view_atribuir_projetista(request):
    is_superuser = request.user.is_superuser
    usuario_no_grupo_supervisor = request.user.groups.filter(name='supervisor_projetos').exists()

    # Verifica se o usuário é superusuário ou pertence ao grupo 'topografia'
    if not (is_superuser or usuario_no_grupo_supervisor):
        raise PermissionDenied

    if request.method == 'POST':
        form = AtribuirProjetistaForm(request.POST)
        if form.is_valid():
            projetista = form.cleaned_data['projetista']
            chaves_ids_str = form.cleaned_data['chaves_ids']  # Uma string de IDs
            chaves_ids = [int(id.strip()) for id in chaves_ids_str.strip('[]').split(',') if id.strip().isdigit()]
            Chave.objects.filter(id__in=chaves_ids).update(projetista=projetista)
            return redirect('admin:chaves_chave_changelist')
        else:
            return render(request, 'atribuir_projetista.html', {'form': form})
    else:
        # Inicializa o formulário com os IDs das chaves da sessão
        chaves_ids_inicial = request.session.get('chave_ids', [])
        form = AtribuirProjetistaForm(initial={'chaves_ids': chaves_ids_inicial})

        # Ordena os projetistas alfabeticamente antes de passar para o formulário
        projetistas_ativos = Projetista.objects.filter(ativo=True).order_by('projetista')
        form.fields['projetista'].queryset = projetistas_ativos

        return render(request, 'atribuir_projetista.html', {'form': form})

@login_required(login_url='/janus/login/')
def buscar_chave(request):
    chave_pesquisada = None
    if 'query' in request.GET:
        query = request.GET['query'].strip()
        try:
            chave_pesquisada = Chave.objects.get(chave=query)
        except Chave.DoesNotExist:
            chave_pesquisada = None  # Para exibir uma mensagem de erro no template

    return render(request, 'buscar_chave.html', {'chave': chave_pesquisada})

from .models import EmailConfig
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime

def solicitacao_chave_view(request):
    modal_show = False
    chaves_sem_ns_msg = ''
    form = ConfirmacaoSolicitacaoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        try:
            projetista = Projetista.objects.get(email=request.user)
            usuario_nome = projetista.projetista
            chaves_sem_ns = Chave.objects.filter(projetista=projetista, ns__isnull=True).count()

            if chaves_sem_ns > 2:
                modal_show = True
                chaves_sem_ns_msg = f'Solicitação Negada! Você ainda tem {chaves_sem_ns} Chaves para serem designadas.'
            else:
                # Buscar emails dinamicamente do banco de dados
                destinatarios = EmailConfig.objects.all().values_list('email', flat=True)

                context = {'usuario_nome': usuario_nome, 'data_solicitacao': datetime.now()}
                html_content = render_to_string('email_solicitacao_chave.html', context)
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    'Solicitação de Chaves',
                    text_content,
                    'noreply@dbsistemas.com.br',
                    destinatarios  # Usar a lista de emails obtida do banco de dados
                )
                email.attach_alternative(html_content, "text/html")
                # print(f"Enviando e-mail para: {list(destinatarios)}")
                # print("Destinatários:", list(destinatarios))
                email.send()

                return redirect('pagina_de_sucesso')
        except Projetista.DoesNotExist:
            usuario_nome = request.user.get_full_name() or request.user.username

    return render(request, 'solicitacao_chaves.html',
                  {'form': form, 'modal_show': modal_show, 'chaves_sem_ns_msg': chaves_sem_ns_msg})

def pagina_de_sucesso_view(request):
    return render(request, 'pagina_de_sucesso.html')


from django.http import HttpResponse

def view_com_erro(request):
    x = 1 / 0  # isso vai causar ZeroDivisionError
    return HttpResponse("Isso nunca será exibido.")