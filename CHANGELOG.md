# Changelog

Todos os cambios relevantes deste projeto sao documentados aqui.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semantico](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2026-03-20

### Adicionado
- API REST com FastAPI: endpoints `/api/analyze`, `/api/chat`, `/api/chat/stream`, `/api/report`
- Suporte a streaming de respostas LLM via SSE (`/api/chat/stream`)
- 4 fontes de dados: arquivo (CSV/Excel), Google Sheets, Supabase, BigQuery
- Multi-LLM: Claude (Anthropic) e GPT-4o (OpenAI) via factory pattern
- LangGraph workflow: ingest → analyze → insights → report / qa
- Analise estatistica avancada: correlacoes, outliers, perfil numerico, temporal, segmentos, metricas de negocio
- Deploy no Fly.io (regiao: gru) com healthcheck
- CI/CD via GitHub Actions: lint + testes em PRs, deploy automatico em `main`
- Governanca: CONTRIBUTING.md, PR template, issue templates, CHANGELOG

### Corrigido
- Timeout de 60s em chamadas LLM para evitar travamentos
- LIMIT 10.000 linhas em fontes externas (BigQuery, Supabase)
- Try/except ao salvar relatorio em filesystem read-only (Fly.io)
- Remocao de `operator.add` em `insights` para evitar acumulacao incorreta
