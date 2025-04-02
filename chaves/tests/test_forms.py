from django.test import TestCase
from chaves.forms import ChaveForm, CustomUsuarioCreateForm
from chaves.models import Chave, Polo, Projetista, CustomUsuario

class ChaveFormTestCase(TestCase):
    def setUp(self):
        # Criando instâncias de Projetista e Polo para uso no teste
        self.projetista = Projetista.objects.create(projetista="Projetista Teste")
        self.polo = Polo.objects.create(polo="001")

    def test_form_valid_data(self):
        # Testando o formulário com dados válidos
        form_data = {
            'chave': '123456',
            'ns': '1234567890',
            'polo': self.polo.id,
            'municipio': 'Teste',
            'coordenada': '123456:1234567',
            'poste': '001',
            'observacao': 'Teste observação'
        }
        form = ChaveForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        # Testando o formulário com dados inválidos
        form_data = {
            'chave': '123',
            'ns': '12345',
        }
        form = ChaveForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_bootstrap_classes(self):
        # Verificando se as classes do Bootstrap são aplicadas
        form = ChaveForm()
        for field_name, field in form.fields.items():
            self.assertIn('form-control', field.widget.attrs['class'])

    def test_form_observacao_optional(self):
        # Verificando se o campo observacao é opcional
        form = ChaveForm()
        self.assertFalse(form.fields['observacao'].required)


from django.test import TestCase
from chaves.forms import CustomUsuarioCreateForm

class CustomUsuarioCreateFormTestCase(TestCase):

    def test_save_user(self):
        # Inclua os dados necessários, incluindo 'email'
        form_data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'strong_password',
            'password2': 'strong_password',
        }
        form = CustomUsuarioCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Teste adicional para verificar se o usuário foi salvo corretamente
        user = form.save()
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        # Verificar se a senha foi definida corretamente
        self.assertTrue(user.check_password('strong_password'))
