from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUsuario, Chave, Projetista
from django import forms

class ChaveForm(forms.ModelForm):
    class Meta:
        model = Chave
        fields = ['chave','ns', 'polo', 'municipio', 'coordenada', 'poste', 'municipio', 'observacao']


    def __init__(self, *args, **kwargs):
        super(ChaveForm, self).__init__(*args, **kwargs)

        # Aplicando classes do Bootstrap a todos os campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'observacao':
                field.widget.attrs['placeholder'] = 'Adicione qualquer observação aqui (opcional)'
                field.help_text = 'Você pode deixar este campo em branco se desejar.'
            if field_name != 'observacao':
                field.required = True

        # Tornando o campo 'chave' somente leitura
        if 'chave' in self.fields:
            self.fields['chave'].widget.attrs['readonly'] = True
            self.fields['chave'].disabled = True  # Opcional, caso queira que o valor seja enviado no formulário

class CustomUsuarioCreateForm(UserCreationForm):

    class Meta:
        model = CustomUsuario
        fields = ('email', 'first_name', 'last_name')
        labels = {'email': 'E-mail'}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        # Agora, como o campo 'email' já é parte do formulário,
        # não é necessário atribuir manualmente
        if commit:
            user.save()
        return user

class CustomUsuarioChangeForm(UserChangeForm):
    class Meta:
        model = CustomUsuario
        fields = ('first_name', 'last_name')

class PlanilhaUploadForm(forms.Form):
    planilha = forms.FileField(label='Selecione uma planilha')

class AtribuirProjetistaForm(forms.Form):
    projetista = forms.ModelChoiceField(
        queryset=Projetista.objects.filter(ativo=True),  # Filtra apenas os projetistas ativos
        required=True,
        label="Projetista"
    )
    chaves_ids = forms.CharField(widget=forms.HiddenInput())

class ConfirmacaoSolicitacaoForm(forms.Form):
    confirmacao = forms.BooleanField(label='Confirmar a solicitação de chaves', required=True)