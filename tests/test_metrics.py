from backend.app.metrics import compute_metrics
from backend.app.models import ContestDraw

def test_compute_metrics_basic():
    last = ContestDraw(contest_id=1, date="2025-01-01", numbers=[7, 8, 9, 10, 11, 12])
    numbers = [1, 2, 3, 4, 5, 6]
    m = compute_metrics(numbers, last)
    assert m.total_sum == sum(numbers)
    assert m.even == 3
    assert m.odd == 3
    assert m.blocks == 1
    assert m.terminals_distinct == 6
    assert m.consecutive_pairs == 5
    assert m.repeats_last_draw == 0
