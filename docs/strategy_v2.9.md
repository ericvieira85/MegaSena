# Estratégia v2.9 — Cobertura Avançada

Este arquivo resume as regras fornecidas para geração do portfólio Mega-Sena v2.9. Use-o como fonte de verdade para evolução do backend.

## Objetivo e estrutura do portfólio
- Gerar 12 jogos (6 dezenas) divididos em clusters: S(4), H(4), Z(2), A(2).
- Controlar correlação via limites de overlap (<=2 por padrão; até 2 pares com overlap=3) e caps de exposição por dezena (geral 3x; até 2 âncoras em 4x).
- Cobertura global: terminais 0–9 precisam aparecer; 9/12 jogos com 5 blocos e no máximo 3 com 4 blocos.

## Entradas e janelas
- `historical_draws` com `contest_id`, `date`, `numbers` (6 dezenas). `last_draw` é o mais recente.
- Rolling windows: R10, R20, R50 (ou máximo disponível se menor).

## Métricas básicas por jogo
- Soma, paridade (3-3, 4-2, 2-4 aceitas), blocos (1–10 ... 51–60), terminais distintos >=4, consecutivos (0 ou 1 par), repetição do último concurso (<=1 por jogo; <=3 por dezena no portfólio).

## Classificação por dezena
- Freq. e atraso para AllTime/R50/R20/R10.
- Hot = top 20 freq R50; Cold = bottom 20 freq R50; Overdue = top 10 delay; Recent = delay <=2.

## Âncoras
- Calcular `anchor_score` com pesos: 0.40 morno forte (freq R50 em percentil 40–80), 0.35 atraso moderado (delay percentil 40–80), 0.25 compatibilidade de ciclo (R10/R20, faixa alta/baixa).
- Selecionar 2 âncoras (A preferir 31–60, B preferir 1–30). Cada âncora aparece em 3–4 jogos; juntas em no máximo 2 jogos.

## Guard-rails por cluster
- **Base**: soma normal 160–195 (Z pode 150–205), nunca <145 ou >215; paridade 3-3/4-2/2-4; blocos alvo 5 (aceita 4); terminais>=4; consecutivos <=1 par.
- **S (Seguro)**: soma 165–190; blocos 5; paridade 3-3 ou 4-2; <=1 consecutivo; preferir 0–1 dezena >=50.
- **H (Híbrido)**: soma 160–200; blocos 4–5; paridade 2-4/3-3/4-2; 0–2 dezenas >=50.
- **Z (Zebra controlada)**: soma 150–205; blocos 4–5; opcional 1 jogo com 5-1/1-5; guarda exceções configuráveis.
- **A (Anti-falha)**: blocos 4–5; precisa atender pelo menos 2 de: (>=2 em 41–60, >=2 em 21–40, >=1 em 1–20).

## Pipeline
1. Gerar candidatos (aleatório, por blocos, terminais, injeção de âncoras).
2. Filtrar por guard-rails do cluster.
3. Ranqueamento: estrutura, âncoras, diversidade (overlap/caps), recência.
4. Seleção ordenada S1..S4, H1..H4, Z1..Z2, A1..A2 mantendo estado global.
5. Repair step: cobrir terminais faltantes, limitar blocos 4x, corrigir cap de exposição; se falhar, relaxar um parâmetro e registrar.

## Pós-sorteio e governança
- Avaliar hits por jogo/cluster, cobertura global, diagnóstico de falha (soma, blocos, terminais, faixas 1-20/21-40/41-60, overlap).
- Gerar sugestões de calibração (ajuste de somas, blocos, terminais, caps, seleção de âncoras) com justificativa, impacto e plano de teste.
- Mudanças só aplicam após aprovação explícita (`PENDING` -> `APPROVED/REJECTED`).

## MVP adicional
- Upload de histórico XLSX para ingestão (sem scraping inicial).
- Painéis: rolling 10/20/50 (soma, paridade, blocos, >=50), mapa de exposição, cobertura de terminais.
- Função “Selecionar 3 para apostar”: preferir 1 S + 1 H + 1 A/Z com overlap <=1 (ideal) ou <=2.
