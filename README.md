# MegaSena Strategy Prototype

Protótipo inicial do backend para a Estratégia Mega-Sena v2.9 (cobertura avançada). O foco é expor endpoints básicos, consolidar as regras e permitir evolução iterativa.

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
