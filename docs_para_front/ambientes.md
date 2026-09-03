# Ambientes

## URLs

| Ambiente | Base URL | Branch |
|---|---|---|
| Desenvolvimento (Railway) | `https://backendjukebox-dev.up.railway.app` | `dev` |
| Local | `http://127.0.0.1:8000` | — |

## Variáveis de ambiente (backend)

Variáveis configuradas no Railway ou no arquivo `.env` local.

| Variável | Obrigatória | Descrição |
|---|---|---|
| `SECRET_KEY` | Sim (produção) | Chave secreta do Django |
| `DEBUG` | Sim | `True` (local) / `False` (produção) |
| `ALLOWED_HOSTS` | Não | Hosts permitidos, separados por vírgula |
| `DATABASE_URL` | Sim (produção) | Injetada automaticamente ao vincular PostgreSQL no Railway |
| `RAILWAY_PUBLIC_DOMAIN` | Não | Injetada pelo Railway; usada para `ALLOWED_HOSTS` e CSRF |
| `CSRF_TRUSTED_ORIGINS` | Não | Origens confiáveis para CSRF, separadas por vírgula |
| `DJANGO_SUPERUSER_USERNAME` | Sim (produção) | Usuário do admin criado no deploy |
| `DJANGO_SUPERUSER_EMAIL` | Não | E-mail do superusuário |
| `DJANGO_SUPERUSER_PASSWORD` | Sim (produção) | Senha do superusuário (sincronizada a cada deploy) |

## Variáveis para o frontend

O frontend deve configurar apenas a **base URL** da API:

```env
# Exemplo (.env do frontend)
VITE_API_BASE_URL=https://backendjukebox-dev.up.railway.app
# ou
NEXT_PUBLIC_API_BASE_URL=https://backendjukebox-dev.up.railway.app
```

> Nome da variável depende do framework (Vite, Next.js, etc.).

## Banco de dados

| Ambiente | Engine | Persistência |
|---|---|---|
| Local (sem `DATABASE_URL`) | SQLite (`db.sqlite3`) | Arquivo local |
| Railway (com `DATABASE_URL`) | PostgreSQL | **Persistente** |

> **Importante:** sem `DATABASE_URL` no Railway, o Django usa SQLite no disco do container — **os dados somem a cada redeploy** (buckets, músicas, etc.).

### Como vincular PostgreSQL no Railway

1. Abra o serviço **Backend** → **Variables**
2. Clique em **Add Reference** (ou **New Variable** → referência)
3. Selecione o serviço **PostgreSQL** → `DATABASE_URL`
4. Faça **redeploy**

### Verificar se está usando PostgreSQL

```bash
curl https://backendjukebox-dev.up.railway.app/health/
```

Resposta esperada:

```json
{
  "status": "ok",
  "database": "postgresql",
  "persistent": true
}
```

Se `"database": "sqlite"` em produção, o PostgreSQL **não está vinculado**.

## Configurar bucket pelo painel Admin (recomendado)

Com o PostgreSQL vinculado, cadastre o bucket uma vez no painel — os dados **persistem no banco** entre deploys.

1. Acesse `https://backendjukebox-dev.up.railway.app/admin/`
2. Vá em **Configurações de bucket** → **Adicionar**
3. Preencha os campos:

| Campo no Admin | O que preencher |
|---|---|
| **Nome** | `jukebox-prod` (identificador interno) |
| **Provedor** | `Cloudflare R2` |
| **URL do endpoint** | `https://9f7ffe....r2.cloudflarestorage.com` |
| **Nome do bucket** | `jukebox` |
| **URL pública** | `https://pub-b48c490....r2.dev` |
| **Pasta raiz das músicas** | `jukebox/Musicas/` |
| **Região** | `auto` |
| **Access key** | sua access key do R2 |
| **Secret key** | sua secret key do R2 |
| **Ativo** | marcado |

Também é possível cadastrar via API: `POST /api/v1/buckets/` (com token de autenticação).

> Não é necessário configurar variáveis `BUCKET_*` no Railway quando usar o Admin.

## Admin (uso interno)

| Campo | Valor |
|---|---|
| URL | `https://backendjukebox-dev.up.railway.app/admin/` |
| Autenticação | Sessão Django (formulário HTML) |
| Usuário | Configurado via `DJANGO_SUPERUSER_USERNAME` |

O login do admin **não é um endpoint de API** para o frontend consumir.

## Como rodar localmente (backend)

```powershell
cd d:\Projetos\backend_jukebox
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Base URL local: `http://127.0.0.1:8000`
