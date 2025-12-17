# MegaSena Strategy Prototype

Protótipo inicial do backend para a Estratégia Mega-Sena v2.9 (cobertura avançada). O foco é expor endpoints básicos, consolidar as regras e permitir evolução iterativa.

## Estado atual (não está pronto para produção)

> **A aplicação está pronta?** Ainda não. Ela é apenas um esqueleto de API; não gera apostas reais e não faz ingestão de resultados automaticamente. Use apenas para experimentar o modelo e evoluir o código.
- Endpoints disponíveis: `/health`, `/config`, `/anchors` (cálculo inicial de score), `/generate` (placeholder com números fixos).
- Regras codificadas: modelos de cluster, restrições gerais e cálculo básico de métricas/âncoras.
- Itens faltantes para considerar um MVP jogável:
  - Implementar o pipeline completo de geração (candidatos, filtros por cluster, ranking, overlap/caps globais, repair step, seleção de 3 apostas).
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
   - `POST /generate` — cria um portfólio placeholder usando métricas e âncoras (substituir pelo pipeline completo nas próximas iterações).

## Próximos passos
- Implementar pipeline completo de geração conforme `docs/strategy_v2.9.md` (candidatos, filtros, ranking, repair).
- Adicionar ingestão de histórico via upload XLSX e backtests.
- Criar autenticação, persistência e painel de calibração/aprovação de mudanças.
