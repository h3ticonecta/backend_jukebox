# Roadmap — Funcionalidades Planejadas

Itens discutidos na arquitetura mas **ainda não implementados**. O frontend deve aguardar os contratos correspondentes antes de integrar.

## Próximas entregas (backend)

| Prioridade | Funcionalidade | Descrição |
|---|---|---|
| Alta | CORS | Permitir requisições do domínio do frontend |
| Alta | Autenticação API | Login/logout para usuários do app (JWT ou similar) |
| Alta | CRUD de músicas | Upload, listagem, detalhe, remoção |
| Média | Cloudflare R2 | Armazenamento de arquivos de áudio |
| Média | Fila de reprodução | Adicionar, remover, ordenar músicas na fila |
| Média | Votação / pedidos | Usuários solicitam músicas |
| Baixa | Versionamento `/api/v1/` | Prefixo de versão nos endpoints |

## Contratos futuros (a serem criados)

Quando implementados, novos arquivos serão adicionados em `docs/contratos/`:

```
docs/contratos/
├── 03-auth-login.md
├── 04-auth-logout.md
├── 05-musicas-listar.md
├── 06-musicas-upload.md
├── 07-fila-listar.md
├── 08-fila-adicionar.md
└── ...
```

## Dependências externas pendentes

| Serviço | Uso | Status |
|---|---|---|
| Cloudflare R2 | Armazenar arquivos `.mp3`, `.wav`, etc. | Não configurado |
| PostgreSQL | Dados relacionais | Configurado no Railway |

## Como solicitar novos contratos

1. Descreva a funcionalidade necessária no frontend
2. Backend implementa o endpoint
3. Backend cria/atualiza o contrato em `docs/contratos/`
4. Frontend implementa com base no contrato
