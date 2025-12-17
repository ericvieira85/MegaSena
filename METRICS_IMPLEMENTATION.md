# Implementação Faltante: metrics.py

## Visão Geral
O arquivo `metrics.py` é importado em dois lugares mas não existe:
1. [main.py](../backend/app/main.py#L6): `from .metrics import compute_metrics`
2. [anchors.py](../backend/app/anchors.py#L9): `from .metrics import rolling_windows`

Este documento detalha o que deve ser implementado.

---

## Função 1: `rolling_windows(draws, window_size)`

### Propósito
Extrai os últimos N sorteios (janela móvel) de um histórico de sorteios. Usado para evitar viés de recência calculando frequências apenas em períodos recentes.

### Assinatura
```python
def rolling_windows(draws: List[ContestDraw], window_size: int) -> List[ContestDraw]:
    """
    Extract the last `window_size` draws from a list of contest draws.
    
    Args:
        draws: Complete list of historical contest draws
        window_size: Number of recent draws to extract
        
    Returns:
        List of the most recent `window_size` draws (or fewer if fewer draws exist)
    """
```

### Comportamento
- Se `len(draws) <= window_size`: retorna todos os sorteios
- Se `len(draws) > window_size`: retorna apenas os últimos `window_size` sorteios
- Mantém a ordem cronológica (primeiro = mais antigo, último = mais recente)

### Exemplo
```python
draws = [
    ContestDraw(contest_id=1, date="2024-01-01", numbers=[1,2,3,4,5,6]),
    ContestDraw(contest_id=2, date="2024-01-02", numbers=[7,8,9,10,11,12]),
    ContestDraw(contest_id=3, date="2024-01-03", numbers=[13,14,15,16,17,18]),
    ContestDraw(contest_id=4, date="2024-01-04", numbers=[19,20,21,22,23,24]),
]

rolling_windows(draws, 10)  # Retorna todos os 4 (window_size > len)
# [draw1, draw2, draw3, draw4]

rolling_windows(draws, 2)   # Retorna últimos 2
# [draw3, draw4]
```

### Uso em [anchors.py](../backend/app/anchors.py)
```python
for window_name, size in WINDOWS.items():
    subset = rolling_windows(draws, min(size, len(draws)))  # R10, R20, R50
    # subset é usado para calcular frequência em janelas de tempo específicas
```

---

## Função 2: `compute_metrics(numbers, reference_draw)`

### Propósito
Calcula propriedades de um jogo (6 números) com base em regras de loteria e comparação com o último sorteio.

### Assinatura
```python
def compute_metrics(numbers: List[int], reference_draw: ContestDraw) -> GameMetrics:
    """
    Compute metrics for a lottery game given 6 numbers and a reference draw.
    
    Args:
        numbers: List of 6 unique lottery numbers (1-60)
        reference_draw: The most recent contest draw for comparisons
        
    Returns:
        GameMetrics object with all calculated properties
    """
```

### Propriedades a Calcular

#### 1. **total_sum**: `int`
Soma de todos os 6 números.
```python
total_sum = sum(numbers)  # Ex: [3,14,21,37,45,56] → 176
```

#### 2. **even**: `int`
Quantidade de números pares no jogo.
```python
even = sum(1 for n in numbers if n % 2 == 0)  # Ex: [3,14,21,37,45,56] → 3 pares
```

#### 3. **odd**: `int`
Quantidade de números ímpares no jogo.
```python
odd = sum(1 for n in numbers if n % 2 != 0)  # Ex: [3,14,21,37,45,56] → 3 ímpares
# Invariante: even + odd deve sempre ser 6
```

#### 4. **blocks**: `int`
Número de "blocos" de 10 números distintos que contêm os 6 números.
Blocos: 1-10, 11-20, 21-30, 31-40, 41-50, 51-60
```python
# Ex: [3,14,21,37,45,56]
# Bloco 1 (1-10): 3 ✓
# Bloco 2 (11-20): 14 ✓
# Bloco 3 (21-30): 21 ✓
# Bloco 4 (31-40): 37 ✓
# Bloco 5 (41-50): 45 ✓
# Bloco 6 (51-60): 56 ✓
# blocks = 6 (todos os blocos cobertos)
```

**Cálculo**:
```python
blocks_covered = set()
for n in numbers:
    block = (n - 1) // 10  # 0-5 para blocos 1-6
    blocks_covered.add(block)
blocks = len(blocks_covered)
```

#### 5. **terminals_distinct**: `int`
Quantidade de terminações (último dígito) diferentes. Números 1-60 têm terminações 0-9.
```python
# Ex: [3,14,21,37,45,56]
# Terminações: 3, 4, 1, 7, 5, 6 → 6 distintas
terminals_distinct = len(set(n % 10 for n in numbers))
```

#### 6. **consecutive_pairs**: `int`
Quantidade de pares de números consecutivos ou que diferem por 10 (mesmo bloco).
```python
# Ex: [1,2,5,15,20,50]
# Pares: (1,2)✓, (1,11)?✗, (5,15)?✗, (15,20)?✗, (20,30)?✗
# Ou usar: (20,30) seria +10 no mesmo bloco
# Consecutivos: (1,2) = 1 par

# Método: considerar diferenças de 1 ou 10
pairs = 0
sorted_nums = sorted(numbers)
for i in range(len(sorted_nums) - 1):
    if sorted_nums[i+1] - sorted_nums[i] in [1, 10]:
        pairs += 1
consecutive_pairs = pairs
```

#### 7. **repeats_last_draw**: `int`
Quantidade de números que aparecem tanto no jogo quanto no último sorteio de referência.
```python
# Ex: game=[3,14,21,37,45,56], reference_draw.numbers=[3,7,21,40,45,60]
# Repetições: 3✓, 21✓, 45✓ → 3 repetições
repeats_last_draw = len(set(numbers) & set(reference_draw.numbers))
```

### Retorno
```python
return GameMetrics(
    total_sum=total_sum,
    even=even,
    odd=odd,
    blocks=blocks,
    terminals_distinct=terminals_distinct,
    consecutive_pairs=consecutive_pairs,
    repeats_last_draw=repeats_last_draw,
)
```

### Exemplo Completo
```python
draw = ContestDraw(
    contest_id=1234,
    date="2024-01-03",
    numbers=[3, 14, 21, 37, 45, 56]
)

reference = ContestDraw(
    contest_id=1235,
    date="2024-01-04",
    numbers=[3, 7, 21, 40, 45, 60]
)

metrics = compute_metrics(draw.numbers, reference)
# GameMetrics(
#     total_sum=176,
#     even=3,
#     odd=3,
#     blocks=6,
#     terminals_distinct=6,
#     consecutive_pairs=0,
#     repeats_last_draw=3,
# )
```

### Uso em [main.py](../backend/app/main.py)
```python
last_draw = draws[-1]  # Último sorteio histórico
dummy_numbers = [1, 2, 3, 4, 5, 6]  # Placeholder até geração completa
metrics = compute_metrics(dummy_numbers, last_draw)

# metrics é incluído em cada GeneratedGame
games.append(GeneratedGame(cluster=..., numbers=..., metrics=metrics))
```

---

## Template de Implementação

```python
from typing import List
from .models import ContestDraw, GameMetrics


def rolling_windows(draws: List[ContestDraw], window_size: int) -> List[ContestDraw]:
    """Extract the last window_size draws."""
    if not draws:
        return []
    return draws[-window_size:] if len(draws) > window_size else draws


def compute_metrics(numbers: List[int], reference_draw: ContestDraw) -> GameMetrics:
    """Compute game metrics."""
    # TODO: Implement the 7 calculations above
    return GameMetrics(
        total_sum=...,
        even=...,
        odd=...,
        blocks=...,
        terminals_distinct=...,
        consecutive_pairs=...,
        repeats_last_draw=...,
    )
```

---

## Notas Importantes

1. **Validação**: Não validar `numbers` ou `reference_draw`—assuma que já foram validados por Pydantic
2. **Performance**: Usar construções Python idiomáticas (list comprehensions, set operations)
3. **NumPy**: Não é necessário; operações são simples e NumPy não está importado em anchors.py
4. **Testes**: Verificar casos limites como blocos parciais, mesmo bloco ou números consecutivos
5. **Contrato**: O retorno deve ser sempre um `GameMetrics` válido, nunca None ou exceções não tratadas
