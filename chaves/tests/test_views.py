from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from chaves.models import CustomUsuario, Chave, Polo, Projetista
from django.contrib.auth.models import Group
import os
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.messages import get_messages
from chaves.forms import AtribuirProjetistaForm


class ImportarChavesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('view_importar_chaves')
        self.user_comum = CustomUsuario.objects.create_user('comum@test.com', 'password')
        self.user_supervisor = CustomUsuario.objects.create_user('supervisor@test.com', 'password')
        self.user_super = CustomUsuario.objects.create_superuser('super@test.com', 'password')
        self.group_supervisor = Group.objects.create(name='supervisor_projetos')
        self.user_supervisor.groups.add(self.group_supervisor)

    def test_acesso_usuario_comum(self):
        self.client.login(username='comum@test.com', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_acesso_usuario_supervisor(self):
        self.client.login(username='supervisor@test.com', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)  # OK

    def test_acesso_superuser(self):
        self.client.login(username='super@test.com', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)  # OK

    @override_settings(MEDIA_ROOT=os.path.join(os.path.dirname(__file__), 'test_media'))
    def test_upload_valido(self):
        self.client.login(username='supervisor@test.com', password='password')
        with open('chaves/test_media/2967784-EMLE-PablloTadeu.xlsx', 'rb') as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                                               content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response = self.client.post(self.url, {'planilha': uploaded_file})
            # Verifique o comportamento esperado após o upload válido

    def test_upload_invalido(self):
        self.client.login(username='supervisor@test.com', password='password')
        response = self.client.post(self.url, {'planilha': ''})
        self.assertFalse(response.context['form'].is_valid())


class CustomLoginTestCase(TestCase):
    def setUp(self):
        # Criar usuário de teste usando o modelo personalizado
        self.user = CustomUsuario.objects.create_user(email='testuser@example.com', password='12345')

    def test_login_success(self):
        # Dados de login
        login_data = {
            'username': 'testuser@example.com',
            'password': '12345'
        }
        response = self.client.post(reverse('login'), login_data)
        # Verificar se o redirecionamento ocorreu
        self.assertRedirects(response, reverse('janus_view'))

    def test_login_failure(self):
        # Dados de login incorretos
        login_data = {
            'username': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('login'), login_data)
        # Verificar se o login falhou
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Usuário ou senha inválidos' in response.content.decode())

class CustomLoginViewTest(TestCase):

    def test_get_login_form(self):
        """
        Testa se a página de login retorna um AuthenticationForm com os campos
        com as classes CSS do Bootstrap quando acessada via GET.
        """
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], AuthenticationForm)
        self.assertIn('class="form-control"', response.content.decode('utf-8'))

class GerenciarChavesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Criar usuários e grupos para o teste usando CustomUsuario
        self.superuser = CustomUsuario.objects.create_superuser(email='superuser@test.com', password='password')
        self.user = CustomUsuario.objects.create_user(email='user@test.com', password='password')
        self.tecnicos_group = Group.objects.create(name='tecnicos')
        self.supervisor_group = Group.objects.create(name='supervisor_projetos')
        self.user.groups.add(self.tecnicos_group)

        # Criar algumas chaves para testes
        Chave.objects.create(chave="CHV01", ns="1234567890")

    def test_access_superuser(self):
        self.client.login(email='superuser@test.com', password='password')
        response = self.client.get(reverse('gerenciar_chaves'))
        self.assertEqual(response.status_code, 200)

    def test_access_user_in_tecnicos_group(self):
        self.client.login(email='user@test.com', password='password')
        response = self.client.get(reverse('gerenciar_chaves'))
        self.assertEqual(response.status_code, 200)

    def test_access_unauthorized_user(self):
        unauthorized_user = CustomUsuario.objects.create_user(email='unauth_user@test.com', password='password')
        self.client.login(email='unauth_user@test.com', password='password')
        response = self.client.get(reverse('gerenciar_chaves'))
        self.assertEqual(response.status_code, 403)  # Espera-se erro 403 de permissão negada

class PesquisarChaveTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = CustomUsuario.objects.create_superuser(email='superuser@test.com', password='password')
        self.client.login(email='superuser@test.com', password='password')

        # Criação de instâncias de Chave para o teste
        Chave.objects.create(chave="CHV01", ns="1234567890")
        Chave.objects.create(chave="CHV02", ns="2345678901")
        Chave.objects.create(chave="CHV03")

    def test_search_by_ns(self):
        response = self.client.get(reverse('gerenciar_chaves'), {'ns_search': '1234'})
        self.assertContains(response, 'CHV01')
        self.assertNotContains(response, 'CHV02')
        self.assertNotContains(response, 'CHV03')

    def test_search_by_chave(self):
        response = self.client.get(reverse('gerenciar_chaves'), {'chave_search': 'CHV02'})
        self.assertNotContains(response, 'CHV01')
        self.assertContains(response, 'CHV02')
        self.assertNotContains(response, 'CHV03')

    def test_filter_sem_projeto(self):
        response = self.client.get(reverse('gerenciar_chaves'), {'sem_projeto': 'true'})
        self.assertNotContains(response, 'CHV01')
        self.assertNotContains(response, 'CHV02')
        self.assertContains(response, 'CHV03')

class EditarChaveViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = CustomUsuario.objects.create_superuser(email='superuser@test.com', password='password')
        self.tecnico_user = CustomUsuario.objects.create_user(email='tecnico@test.com', password='password')
        self.supervisor_user = CustomUsuario.objects.create_user(email='supervisor@test.com', password='password')
        self.unauthorized_user = CustomUsuario.objects.create_user(email='unauthorized@test.com', password='password')

        self.tecnico_group = Group.objects.create(name='tecnicos')
        self.supervisor_group = Group.objects.create(name='supervisor_projetos')
        self.tecnico_user.groups.add(self.tecnico_group)
        self.supervisor_user.groups.add(self.supervisor_group)

        self.chave = Chave.objects.create(chave='CHV01')

    def test_access_superuser(self):
        self.client.login(email='superuser@test.com', password='password')
        response = self.client.get(reverse('editar_chave', kwargs={'id': self.chave.id}))
        self.assertEqual(response.status_code, 200)

    def test_access_tecnico_user(self):
        self.client.login(email='tecnico@test.com', password='password')
        response = self.client.get(reverse('editar_chave', kwargs={'id': self.chave.id}))
        self.assertEqual(response.status_code, 200)

    def test_access_supervisor_user(self):
        self.client.login(email='supervisor@test.com', password='password')
        response = self.client.get(reverse('editar_chave', kwargs={'id': self.chave.id}))
        self.assertEqual(response.status_code, 200)

    def test_access_unauthorized_user(self):
        self.client.login(email='unauthorized@test.com', password='password')
        response = self.client.get(reverse('editar_chave', kwargs={'id': self.chave.id}))
        self.assertEqual(response.status_code, 403)

    def test_post_valid_form(self):
        self.client.login(email='superuser@test.com', password='password')

        # Crie um objeto Polo válido ou obtenha um existente do banco de dados
        polo_valido = Polo.objects.create(polo='GVS')

        form_data = {
            'chave': 'CHV02',
            'ns': '1234567890',
            'polo': polo_valido.id,  # Use o ID do objeto Polo válido
            'municipio': 'Cidade Exemplo',
            'coordenada': '123456:1234567',
            'poste': '001',
            # Inclua quaisquer outros campos obrigatórios aqui
        }

        response = self.client.post(reverse('editar_chave', kwargs={'id': self.chave.id}), form_data)
        form = response.context['form']
        if form.errors:
            print("Erros no formulário:", form.errors)

        self.chave.refresh_from_db()
        self.assertEqual(self.chave.chave, 'CHV02', "O valor da chave não foi atualizado corretamente")

    def test_post_invalid_form(self):
        self.client.login(email='superuser@test.com', password='password')
        response = self.client.post(reverse('editar_chave', kwargs={'id': self.chave.id}), {'chave': ''})
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(['Por favor, corrija os erros abaixo.' in str(m) for m in messages]))

    def test_chave_not_found(self):
        self.client.login(email='superuser@test.com', password='password')
        response = self.client.get(reverse('editar_chave', kwargs={'id': 999}))
        self.assertEqual(response.status_code, 404)

class AtribuirProjetistaViewTest(TestCase):

    def setUp(self):
        # Criação de usuários para os testes
        self.client = Client()
        self.superuser = CustomUsuario.objects.create_superuser(email='superuser@test.com', password='password')
        self.user = CustomUsuario.objects.create_user(email='user@test.com', password='password')
        self.projetista = Projetista.objects.create(projetista='Projetista 1')
        self.chave = Chave.objects.create(chave='CHV01')
        supervisor_group = Group.objects.create(name='supervisor_projetos')
        self.superuser.groups.add(supervisor_group)

    def test_acesso_usuario_nao_autorizado(self):
        self.client.login(email='user@test.com', password='password')
        response = self.client.get(reverse('atribuir_projetista'))
        self.assertEqual(response.status_code, 403)  # Acesso negado

    def test_acesso_usuario_autorizado(self):
        self.client.login(email='superuser@test.com', password='password')
        response = self.client.get(reverse('atribuir_projetista'))
        self.assertEqual(response.status_code, 200)  # Acesso concedido
        self.assertIsInstance(response.context['form'], AtribuirProjetistaForm)

    def test_submissao_formulario_valido(self):
        self.client.login(email='superuser@test.com', password='password')
        form_data = {
            'projetista': self.projetista.id,
            'chaves_ids': f"[{self.chave.id}]"
        }
        response = self.client.post(reverse('atribuir_projetista'), form_data)
        self.chave.refresh_from_db()
        self.assertEqual(self.chave.projetista, self.projetista)
        self.assertRedirects(response, reverse('admin:chaves_chave_changelist'))

    def test_render_formulario_invalido(self):
        self.client.login(email='superuser@test.com', password='password')
        form_data_invalido = {
            'projetista': '',  # valor inválido
            'chaves_ids': ''
        }
        response = self.client.post(reverse('atribuir_projetista'), form_data_invalido)
        self.assertEqual(response.status_code, 200)  # A página ainda é renderizada
        self.assertFalse(response.context['form'].is_valid())  # O formulário deve ser inválido

    def test_render_formulario_inicial_get(self):
        self.client.login(email='superuser@test.com', password='password')
        response = self.client.get(reverse('atribuir_projetistasdf'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], AtribuirProjetistaForm)
        self.assertFalse(response.context['form'].is_bound)  # Verifica se o formulário não está vinculado a dados POST