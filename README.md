# MegaSena Strategy Prototype

Protótipo inicial do backend para a Estratégia Mega-Sena v2.9 (cobertura avançada). O foco é expor endpoints básicos, consolidar as regras e permitir evolução iterativa.

## Estado atual (não está pronto para produção)

> **A aplicação está pronta?** Parcialmente. Ainda não há ingestão automática de resultados nem persistência/autenticação, mas o endpoint `/generate` agora monta um portfólio de 12 jogos (S/H/Z/A) respeitando guard-rails básicos, limites globais de overlap/exposição e cobertura de terminais.
- Endpoints disponíveis: `/health`, `/config`, `/anchors` (cálculo inicial de score), `/generate` (geração heurística).
- Regras codificadas: modelos de cluster, restrições gerais e cálculo básico de métricas/âncoras.
- Itens faltantes para considerar um MVP jogável:
  - Refinar o pipeline de geração (ranking/score, seleção ótima por cluster, seleção automática das 3 apostas preferenciais) — hoje é heurístico e pode falhar se as restrições forem muito estritas.
  - Ingestão de histórico (upload XLSX) e backtests reais; hoje os endpoints dependem de dados enviados manualmente.
  - Autenticação, persistência (SQLite) e governança de versões/aprovações.
  - Ajuste de anchor score para incluir viés de ciclo (R10/R20) e parâmetros configuráveis.
  - Testes automatizados, scripts de lint/CI e tratamento de erros nos endpoints.

## Estrutura
- `backend/app`: código FastAPI com modelos, métricas e cálculo preliminar de âncoras.
- `docs/strategy_v2.9.md`: resumo da estratégia completo para consulta.
- `requirements.txt`: dependências Python do backend.

## Executando localmente
1. Crie um ambiente virtual e instale dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Rode a API:
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```
3. Teste endpoints:
   - `GET /health` — status e versão do modelo.
   - `GET /config` — clusters e restrições configuradas.
   - `POST /anchors` — calcula scores de âncoras a partir de histórico enviado.
  - `POST /generate` — gera um portfólio heurístico (12 jogos S/H/Z/A) respeitando guard-rails básicos.

## Próximos passos
- Implementar pipeline completo de geração conforme `docs/strategy_v2.9.md` (candidatos, filtros, ranking, repair).
- Adicionar ingestão de histórico via upload XLSX e backtests.
- Criar autenticação, persistência e painel de calibração/aprovação de mudanças.
