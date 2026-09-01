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
| [Contratos de API](./contratos/README.md) | Endpoints implementados |
| [Roadmap](./roadmap.md) | Funcionalidades planejadas (ainda não implementadas) |

## Status atual

| Área | Status |
|---|---|
| API pública JSON (`/`, `/health/`) | Implementado |
| Django Admin (`/admin/`) | Implementado |
| PostgreSQL (produção) | Implementado |
| Deploy Railway | Implementado |
| API REST de músicas/fila | Planejado |
| Autenticação para frontend | Planejado |
| Cloudflare R2 (armazenamento) | Planejado |
| CORS | Planejado |

## Base URL (dev)

```
https://backendjukebox-dev.up.railway.app
```

## Contato

Dúvidas sobre contratos ou novos endpoints: alinhar com o time de backend antes de implementar no frontend.
