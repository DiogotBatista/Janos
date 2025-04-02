from email.policy import default

from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UsuarioManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        # extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True')

        return self._create_user(email, password, **extra_fields)


class CustomUsuario(AbstractUser):
    email = models.EmailField('E-mail', unique=True)
    is_staff = models.BooleanField('Membro da equipe', default=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    objects = UsuarioManager()

class Projetista(models.Model):
    projetista = models.CharField('Nome', max_length=150)
    email = models.ForeignKey(CustomUsuario, on_delete=models.PROTECT, null=True, blank=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        ordering = ['projetista']
        verbose_name = 'Projetista'
        verbose_name_plural = 'Projetistas'

    def __str__(self):
        return self.projetista

class Polo(models.Model):
    polo = models.CharField('Polo', max_length=3, unique=True, db_index=True)

    class Meta:
        ordering = ['polo']
        verbose_name = 'Polo'
        verbose_name_plural = 'Polos'

    def __str__(self):
        return self.polo

class Chave(models.Model):


    chave = models.CharField('Número', max_length=6, unique=True)
    projetista = models.ForeignKey(Projetista, on_delete=models.PROTECT, null=True, blank=True)
    polo = models.ForeignKey(Polo, on_delete=models.PROTECT, null=True, blank=True)

    # Validador para garantir 10 dígitos no campo NS
    ns_validator = RegexValidator(regex=r'^\d{10}$', message="Favor confirmar a NS")
    ns = models.CharField('NS', max_length=10, validators=[ns_validator], null=True, blank=True)

    # Validador para o formato de coordenada UTM
    coordenada_validator = RegexValidator(
        regex=r'^\d{6}:\d{7}$',
        message="Coordenada incorreta"
    )
    coordenada = models.CharField(
        'Coordenada',
        max_length=14,
        validators=[coordenada_validator],
        null=True,
        blank=True
    )

    poste = models.CharField('Poste/Ponto', max_length=3, null=True, blank=True)
    municipio = models.CharField('Municipio', max_length=100, null=True, blank=True)
    chamado = models.CharField("Chamado", max_length=30, null=True, blank=True)
    data_chamado = models.DateField('Data do Chamado', null=True, blank=True)
    data_inclusao = models.DateTimeField(auto_now_add=True, editable=False)
    data_modificacao = models.DateTimeField(auto_now=True)
    observacao = models.TextField('Observação', null=True, blank=True)

    class Meta:
        verbose_name = 'Chave'
        verbose_name_plural = 'Chaves'

    def __str__(self):
        return self.chave

class Aviso(models.Model):
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    ordenacao = models.IntegerField('Ordenação')

    class Meta:
        ordering = ['ordenacao']
        verbose_name = 'Aviso'
        verbose_name_plural = 'Avisos'

    def __str__(self):
        return self.titulo


class EmailConfig(models.Model):
    nome = models.CharField(max_length=100, help_text="Nome do destinatário")
    email = models.EmailField(help_text="Endereço de email do destinatário")

    class Meta:
        ordering = ['nome']
        verbose_name = 'Destinatário'
        verbose_name_plural = 'Destinatários'

    def __str__(self):
        return f"{self.nome} <{self.email}>"