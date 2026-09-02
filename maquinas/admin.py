from django import forms
from django.contrib import admin
from django.forms.widgets import PasswordInput

from maquinas.models import Maquina


class MaquinaAdminForm(forms.ModelForm):
    senha = forms.CharField(
        label='senha',
        widget=PasswordInput(render_value=False),
        required=False,
        help_text='Preencha para definir ou alterar a senha. Deixe em branco para manter a atual.',
    )

    class Meta:
        model = Maquina
        fields = ('nome_jukebox', 'usuario', 'senha', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['senha'].required = True
            self.fields['senha'].help_text = 'Senha de acesso desta jukebox.'

    def save(self, commit=True):
        instance = super().save(commit=False)
        raw_password = self.cleaned_data.get('senha')
        if raw_password:
            instance.set_password(raw_password)
            instance.rotate_token()
        if commit:
            instance.save()
        return instance


@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    form = MaquinaAdminForm
    list_display = (
        'nome_jukebox',
        'usuario',
        'is_active',
        'last_login_at',
        'updated_at',
    )
    list_filter = ('is_active',)
    search_fields = ('nome_jukebox', 'usuario')
    readonly_fields = ('api_token', 'last_login_at', 'created_at', 'updated_at')

    fieldsets = (
        ('Jukebox', {
            'fields': ('nome_jukebox', 'usuario', 'senha', 'is_active'),
            'description': 'Cadastre cada máquina física. Usuário e senha são usados na vinculação do app.',
        }),
        ('Vinculação', {
            'fields': ('api_token', 'last_login_at'),
            'description': 'O token é gerado automaticamente e devolvido no login da máquina.',
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
