from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.forms.widgets import PasswordInput
from django.template.response import TemplateResponse
from django.urls import path

from maquinas.models import Credito, Maquina, MusicaTocada
from maquinas.services import relatorio_faturamento, relatorio_mais_tocadas


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
    change_list_template = 'admin/maquinas/change_list.html'

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

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'relatorios/',
                self.admin_site.admin_view(self.relatorios_view),
                name='maquinas_maquina_relatorios',
            ),
        ]
        return custom + urls

    def relatorios_view(self, request):
        if not request.user.is_active or not request.user.is_staff:
            raise PermissionDenied

        maquina_id = request.GET.get('maquina_id') or None
        inicio = request.GET.get('inicio') or None
        fim = request.GET.get('fim') or None
        faturamento = relatorio_faturamento(maquina_id=maquina_id, inicio=inicio, fim=fim)
        mais_tocadas = relatorio_mais_tocadas(
            maquina_id=maquina_id,
            inicio=inicio,
            fim=fim,
            limit=30,
        )
        context = {
            **self.admin_site.each_context(request),
            'title': 'Relatórios das máquinas',
            'opts': self.model._meta,
            'maquinas': Maquina.objects.filter(is_active=True),
            'maquina_id': maquina_id or '',
            'inicio': inicio or '',
            'fim': fim or '',
            'faturamento': faturamento,
            'mais_tocadas': mais_tocadas,
        }
        return TemplateResponse(request, 'admin/maquinas/relatorios.html', context)


@admin.register(Credito)
class CreditoAdmin(admin.ModelAdmin):
    list_display = ('maquina', 'valor', 'origem', 'created_at')
    list_filter = ('origem', 'maquina', 'created_at')
    search_fields = ('maquina__nome_jukebox', 'observacao')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(MusicaTocada)
class MusicaTocadaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'musica_nome', 'maquina', 'pasta', 'created_at')
    list_filter = ('maquina', 'media_type', 'created_at')
    search_fields = ('titulo', 'musica_nome', 'musica_key', 'maquina__nome_jukebox')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
