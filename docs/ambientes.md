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

| Ambiente | Engine |
|---|---|
| Local (sem `DATABASE_URL`) | SQLite (`db.sqlite3`) |
| Railway (com `DATABASE_URL`) | PostgreSQL |

O frontend **não acessa o banco diretamente**. Toda comunicação é via HTTP com o backend.

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
