from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.forms.widgets import PasswordInput
from django.template.response import TemplateResponse
from django.urls import path

from maquinas.models import (
    Credito,
    Maquina,
    MusicaTocada,
    RoletaConfig,
    RoletaFaixaValor,
    RoletaPremioFaixa,
)
from maquinas.services import relatorio_faturamento, relatorio_mais_tocadas
from maquinas.teclas import TECLAS_PADRAO


def _build_maquina_admin_form():
    """Form com campos virtuais tecla_* — não passar por modelform_factory do admin."""

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

            teclas_map = {t['acao']: t['tecla'] for t in self.instance.get_teclas()}
            for padrao in TECLAS_PADRAO:
                field_name = f'tecla_{padrao["acao"]}'
                self.fields[field_name].initial = teclas_map.get(padrao['acao'], padrao['tecla'])

        def save(self, commit=True):
            instance = super().save(commit=False)
            raw_password = self.cleaned_data.get('senha')
            if raw_password:
                instance.set_password(raw_password)
                instance.rotate_token()

            teclas = []
            for padrao in TECLAS_PADRAO:
                acao = padrao['acao']
                tecla = (self.cleaned_data.get(f'tecla_{acao}') or '').strip()
                teclas.append({
                    'acao': acao,
                    'label': padrao['label'],
                    'tecla': tecla or padrao['tecla'],
                })
            instance.teclas = teclas

            if commit:
                instance.save()
            return instance

    for padrao in TECLAS_PADRAO:
        kwargs = {
            'label': padrao['label'],
            'max_length': 32,
            'required': False,
        }
        if padrao['acao'] == 'vol':
            kwargs['help_text'] = (
                'Um botão físico na máquina: clique aumenta o volume; '
                'cliques repetidos diminuem; segurar diminui em sequência (lógica no app).'
            )
        MaquinaAdminForm.base_fields[f'tecla_{padrao["acao"]}'] = forms.CharField(**kwargs)

    return MaquinaAdminForm


MaquinaAdminForm = _build_maquina_admin_form()


class RoletaConfigInline(admin.StackedInline):
    model = RoletaConfig
    can_delete = False
    max_num = 1
    verbose_name = 'Configuração da Roleta'
    verbose_name_plural = 'Configuração da Roleta'
    fieldsets = (
        (None, {
            'fields': ('ativada',),
        }),
        ('Probabilidades (pesos)', {
            'fields': (
                'peso_premio_mais_2_musicas',
                'peso_premio_mais_1_musica',
                'peso_bonus_recarga_50pct',
                'peso_tente_novamente',
                'peso_nao_foi_dessa_vez',
            ),
        }),
        ('Regras', {
            'fields': (
                'creditos_minimos_girar',
                'max_premio_mais_2_musicas_dia_percent',
            ),
        }),
    )


@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    form = MaquinaAdminForm
    inlines = [RoletaConfigInline]
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
        ('Teclas', {
            'fields': tuple(f'tecla_{t["acao"]}' for t in TECLAS_PADRAO),
            'description': 'Atalhos exibidos no app da jukebox. O front usa estas teclas; crédito pode ser inserido pela tecla ou pela API.',
        }),
        ('Vinculação', {
            'fields': ('api_token', 'last_login_at'),
            'description': 'O token é gerado automaticamente e devolvido no login da máquina.',
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def get_form(self, request, obj=None, change=False, **kwargs):
        """Evita modelform_factory, que não suporta campos virtuais tecla_*."""
        return self.form

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

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        from maquinas.roleta_services import get_or_create_roleta_config

        if form.instance.pk:
            get_or_create_roleta_config(form.instance)


class RoletaPremioFaixaInline(admin.TabularInline):
    model = RoletaPremioFaixa
    extra = 0
    fields = ('tipo', 'quantidade', 'peso', 'ordem')


class RoletaFaixaValorInline(admin.StackedInline):
    model = RoletaFaixaValor
    extra = 0
    fields = ('valor', 'giros_liberados', 'ordem')
    show_change_link = True


@admin.register(RoletaConfig)
class RoletaConfigAdmin(admin.ModelAdmin):
    list_display = ('maquina', 'ativada', 'creditos_minimos_girar', 'updated_at')
    list_filter = ('ativada',)
    search_fields = ('maquina__nome_jukebox', 'maquina__usuario')
    inlines = [RoletaFaixaValorInline]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('maquina', 'ativada'),
        }),
        ('Probabilidades (pesos)', {
            'fields': (
                'peso_premio_mais_2_musicas',
                'peso_premio_mais_1_musica',
                'peso_bonus_recarga_50pct',
                'peso_tente_novamente',
                'peso_nao_foi_dessa_vez',
            ),
        }),
        ('Regras', {
            'fields': (
                'creditos_minimos_girar',
                'max_premio_mais_2_musicas_dia_percent',
            ),
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(RoletaFaixaValor)
class RoletaFaixaValorAdmin(admin.ModelAdmin):
    list_display = ('config', 'valor', 'giros_liberados', 'ordem')
    list_filter = ('config__maquina',)
    search_fields = ('config__maquina__nome_jukebox',)
    inlines = [RoletaPremioFaixaInline]


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
