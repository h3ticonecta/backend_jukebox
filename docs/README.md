# Documentação Backend Jukebox

Contratos e especificações para integração com o frontend.

## Visão geral

Este repositório contém o **backend** do projeto Jukebox, construído com **Django 5.2**. A documentação descreve o que já está implementado e disponível para consumo, em formato de contrato de API.

## Índice

| Documento | Descrição |
|---|---|
| [Arquitetura](./arquitetura.md) | Stack, serviços e responsabilidades |
| [Ambientes](./ambientes.md) | URLs base, variáveis e deploy |
| [Convenções](./convencoes.md) | Padrões de request/response, erros e versionamento |
| [Integração Frontend](./integracao-frontend.md) | Orientações para o time de frontend |
| [Contratos de API](./contratos/README.md) | Endpoints implementados (fonte única para o frontend) |
| [Roadmap](./roadmap.md) | Funcionalidades planejadas (ainda não implementadas) |

## Status atual

| Área | Status |
|---|---|
| API pública JSON (`/`, `/health/`) | Implementado |
| Django Admin (`/admin/`) | Implementado |
| Módulo Buckets S3/R2 (`/api/v1/buckets/`) | Implementado |
| Módulo Músicas (`/api/v1/musicas/`) | Implementado |
| Módulo Máquinas (`/api/v1/maquinas/`) | Implementado |
| Configuração da Roleta (por máquina) | Implementado — [contrato 12](./contratos/12-roleta.md) |
| PIX QR Code (Mercado Pago) | Implementado — [contrato 13](./contratos/13-pix-mercadopago.md) |
| Autenticação por Token (`/api/v1/auth/token/`) | Implementado |
| PostgreSQL (produção) | Implementado |
| Deploy Railway | Implementado |
| CORS | Implementado (via `CORS_ALLOWED_ORIGINS`) |
| API REST de músicas/fila | Músicas implementado / Fila planejado |
| Cloudflare R2 (armazenamento) | Implementado (via módulo buckets) |

## Base URL (dev)

```
https://backendjukebox-dev.up.railway.app
```

Esse hostname está em `ALLOWED_HOSTS` no Django (`config/settings.py`). Testes com `curl` ou Admin nessa URL não devem retornar `DisallowedHost`. Produção do painel costuma usar `paineljukebox.h3ti.com.br` — configure `EXTRA_ALLOWED_HOSTS` no Railway para esse domínio.

## Contato

Dúvidas sobre contratos ou novos endpoints: alinhar com o time de backend antes de implementar no frontend.
