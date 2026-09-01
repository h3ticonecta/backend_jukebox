# Roadmap — Funcionalidades Planejadas

## Já implementado

| Funcionalidade | Contrato |
|---|---|
| Autenticação por Token | [03-auth-token.md](./contratos/03-auth-token.md) |
| Buckets S3/R2 (CRUD) | [04-buckets-crud.md](./contratos/04-buckets-crud.md) |
| Objetos do bucket (listar, upload, mover, excluir) | [05-bucket-objects.md](./contratos/05-bucket-objects.md) |
| Músicas (listar, CRUD, upload) | [06](./contratos/06-musicas-listar.md), [07](./contratos/07-musicas-crud.md), [08](./contratos/08-musicas-upload.md) |
| CORS | Configurado via `CORS_ALLOWED_ORIGINS` |

## Próximas entregas (backend)

| Prioridade | Funcionalidade | Descrição |
|---|---|---|
| Média | Fila de reprodução | Adicionar, remover, ordenar músicas na fila |
| Média | Votação / pedidos | Usuários solicitam músicas |
| Baixa | JWT / refresh token | Substituir ou complementar autenticação por token |

## Contratos futuros (a serem criados)

```
docs/contratos/
├── 09-fila-listar.md
├── 10-fila-adicionar.md
└── ...
```
