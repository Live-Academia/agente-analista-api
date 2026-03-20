# Como Contribuir — Deep Agent API

Obrigado por contribuir! Este guia define os padroes de trabalho para o time.

## Pre-requisitos

- Python 3.11+
- Git
- Acesso ao repositorio na org `Live-Academia`

## Setup Local

```bash
# Clone o repositorio
git clone https://github.com/Live-Academia/agente-analista-api.git
cd agente-analista-api

# Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instale as dependencias (incluindo dev)
pip install -e ".[dev]"

# Configure as variaveis de ambiente
cp .env.example .env
# Edite .env com suas chaves de API
```

## Estrategia de Branches

```
main         → producao (protegida — requer PR + 1 review)
develop      → integracao (branch base para features)
feature/xxx  → nova funcionalidade
fix/xxx      → correcao de bug
hotfix/xxx   → correcao urgente (abre PR direto para main)
release/x.x  → preparacao de release
```

**Fluxo padrao:**

```bash
# Crie sua branch a partir de develop
git checkout develop
git pull origin develop
git checkout -b feature/minha-feature

# Desenvolva, commite e abra PR para develop
git push origin feature/minha-feature
# → Abra PR no GitHub usando o template
```

## Padrão de Commits (Conventional Commits)

```
feat: add streaming SSE endpoint for chat
fix: add timeout to LLM factory
docs: update API endpoint documentation
test: add integration test for /api/analyze
chore: update fastapi dependency to 0.115
refactor: extract prompt formatting to helper
ci: add deploy workflow for Fly.io
```

**Tipos validos:** `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `ci`, `perf`

## Rodando os Testes

```bash
# Todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=src --cov=api --cov-report=term-missing

# Lint
ruff check src/ api/ tests/
```

## Abrindo um Pull Request

1. Certifique-se de que `pytest tests/ -v` e `ruff check` passam localmente
2. Abra o PR para a branch `develop` (nao `main`)
3. Preencha o template de PR completamente
4. Aguarde 1 review aprovado antes de fazer merge
5. Use **Squash and Merge** para manter o historico limpo

## Release para Producao

1. Abra PR de `develop` → `main` com titulo `release: vX.X.X`
2. Atualize `CHANGELOG.md` com as mudancas
3. Apos merge em `main`, o GitHub Actions faz deploy automatico no Fly.io

## Reportar Bugs

Use os [Issue Templates](.github/ISSUE_TEMPLATE/) do GitHub.
