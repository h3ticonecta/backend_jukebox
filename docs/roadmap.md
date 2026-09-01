# Roadmap — Funcionalidades Planejadas

Itens **ainda não implementados**. O frontend deve aguardar os contratos correspondentes antes de integrar.

## Já implementado

| Funcionalidade | Contrato |
|---|---|
| Autenticação por Token | [03-auth-token.md](./contratos/03-auth-token.md) |
| Buckets S3/R2 (CRUD) | [04-buckets-crud.md](./contratos/04-buckets-crud.md) |
| Objetos do bucket (listar, upload, mover, excluir) | [05-bucket-objects.md](./contratos/05-bucket-objects.md) |
| CORS | Configurado via `CORS_ALLOWED_ORIGINS` |

## Próximas entregas (backend)

| Prioridade | Funcionalidade | Descrição |
|---|---|---|
| Alta | CRUD de músicas | Metadados de músicas vinculados ao bucket |
| Média | Fila de reprodução | Adicionar, remover, ordenar músicas na fila |
| Média | Votação / pedidos | Usuários solicitam músicas |
| Baixa | JWT / refresh token | Substituir ou complementar autenticação por token |

## Contratos futuros (a serem criados)

```
docs/contratos/
├── 06-musicas-listar.md
├── 07-musicas-criar.md
├── 08-fila-listar.md
├── 09-fila-adicionar.md
└── ...
```

## Dependências externas

| Serviço | Uso | Status |
|---|---|---|
| Cloudflare R2 / AWS S3 | Armazenar arquivos de áudio | Integrado via módulo buckets |
| PostgreSQL | Dados relacionais | Configurado no Railway |

## Como solicitar novos contratos

1. Descreva a funcionalidade necessária no frontend
2. Backend implementa o endpoint
3. Backend cria/atualiza o contrato em `docs/contratos/`
4. Frontend implementa com base no contrato
