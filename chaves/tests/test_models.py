from django.test import TestCase
from django.core.exceptions import ValidationError
from chaves.models import CustomUsuario, Projetista, Polo, Chave

class UsuarioManagerTest(TestCase):

    def test_criacao_de_usuario(self):
        """ Testa a criação de um usuário comum """
        user = CustomUsuario.objects.create_user(email='user@test.com', password='123')
        self.assertEqual(user.email, 'user@test.com')
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_criarcao_de_usuario_sem_email(self):
        """ Testa a criação de um usuário sem fornecer um e-mail """
        with self.assertRaises(ValueError):
            CustomUsuario.objects.create_user(email='', password='123')

    def test_criacao_de_usuario_superusuario(self):
        """ Testa a criação de um superusuário """
        superuser = CustomUsuario.objects.create_superuser(email='admin@test.com', password='123')
        self.assertEqual(superuser.email, 'admin@test.com')
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_criar_superusuario_sem_ser_superusuario(self):
        """ Testa a criação de um superusuário sem a flag is_superuser """
        with self.assertRaises(ValueError):
            CustomUsuario.objects.create_superuser(email='admin@test.com', password='123', is_superuser=False)

    def test_criar_superusuario_sem_estar_no_staff(self):
        """ Testa a criação de um superusuário sem a flag is_staff """
        with self.assertRaises(ValueError):
            CustomUsuario.objects.create_superuser(email='admin@test.com', password='123', is_staff=False)

class CustomUsuarioTestCase(TestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.first_name = "Test"
        self.last_name = "User"
        self.password = "testpassword123"
        CustomUsuario.objects.create_user(
            email=self.email,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name
        )

    def test_criacao_de_uruario(self):
        """ Testa a criação de um usuario """
        user = CustomUsuario.objects.get(email=self.email)
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.first_name, self.first_name)
        self.assertEqual(user.last_name, self.last_name)
        self.assertTrue(user.check_password(self.password))
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_user_string_representation(self):
        # Verificar a representação de string do Usuário
        user = CustomUsuario.objects.get(email=self.email)
        self.assertEqual(str(user), self.email)

class ProjetistaTestCase(TestCase):
    def setUp(self):
        # Primeiro, criar um usuário que será associado ao Projetista
        self.user = CustomUsuario.objects.create_user(
            email="user@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe"
        )

        # Agora, criar uma instância de Projetista
        self.projetista_name = "Projetista Teste"
        self.projetista = Projetista.objects.create(
            projetista=self.projetista_name,
            email=self.user
        )

    def test_projetista_creation(self):
        # Verificar se o Projetista foi criado corretamente
        self.assertEqual(self.projetista.projetista, self.projetista_name)
        self.assertEqual(self.projetista.email, self.user)

    def test_projetista_string_representation(self):
        # Verificar a representação de string do Projetista
        self.assertEqual(str(self.projetista), self.projetista_name)


class PoloTestCase(TestCase):
    def setUp(self):
        # Criando uma instância de Polo
        self.polo_name = "ABC"
        self.polo = Polo.objects.create(polo=self.polo_name)

    def test_polo_creation(self):
        # Verificando se o Polo foi criado corretamente
        self.assertEqual(self.polo.polo, self.polo_name)

    def test_polo_string_representation(self):
        # Verificando a representação de string do Polo
        self.assertEqual(str(self.polo), self.polo_name)

class ChaveTestCase(TestCase):
    def setUp(self):
        # Criando instâncias de Projetista e Polo para uso no teste
        self.projetista = Projetista.objects.create(projetista="Projetista Teste")
        self.polo = Polo.objects.create(polo="001")

        # Criando uma instância de Chave
        self.chave = Chave.objects.create(
            chave="123456",
            projetista=self.projetista,
            polo=self.polo,
            ns="1234567890",
            coordenada="123456:1234567"
        )

    def test_chave_creation(self):
        # Verificando se a Chave foi criada corretamente
        self.assertEqual(self.chave.chave, "123456")
        self.assertEqual(self.chave.projetista, self.projetista)
        self.assertEqual(self.chave.polo, self.polo)
        self.assertEqual(self.chave.ns, "1234567890")
        self.assertEqual(self.chave.coordenada, "123456:1234567")

    def test_chave_string_representation(self):
        # Verificando a representação de string da Chave
        self.assertEqual(str(self.chave), "123456")

    def test_invalid_ns(self):
        # Testando validação para NS inválido
        chave = Chave(ns="123")
        with self.assertRaises(ValidationError):
            chave.full_clean()

    def test_invalid_coordenada(self):
        # Testando validação para coordenada inválida
        chave = Chave(coordenada="123456:123")
        with self.assertRaises(ValidationError):
            chave.full_clean()
