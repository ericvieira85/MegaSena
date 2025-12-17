from backend.app.anchors import compute_anchor_scores, AnchorScore
from backend. app.models import ContestDraw

def test_compute_anchor_scores_size_and_order():
    draws = [
        ContestDraw(contest_id=1, date="2025-01-01", numbers=[1, 2, 3, 4, 5, 6]),
        ContestDraw(contest_id=2, date="2025-01-08", numbers=[4, 5, 6, 7, 8, 9]),
    ]
    scores = compute_anchor_scores(draws)
    assert isinstance(scores, list)
    assert len(scores) == 60
    assert all(isinstance(s, AnchorScore) for s in scores)
    assert all(scores[i].score >= scores[i+1].score for i in range(len(scores)-1))
