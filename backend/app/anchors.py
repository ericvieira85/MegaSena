from dataclasses import dataclass
from typing import Dict, List

import numpy as np

from .metrics import rolling_windows
from .models import ContestDraw


@dataclass
class AnchorScore:
    number: int
    score: float
    window_freq: Dict[str, float]
    delay: int


WINDOWS = {"R10": 10, "R20": 20, "R50": 50}


def _frequency(draws: List[ContestDraw], number: int) -> int:
    return sum(1 for draw in draws if number in draw.numbers)


def _delay(draws: List[ContestDraw], number: int) -> int:
    for idx, draw in enumerate(reversed(draws)):
        if number in draw.numbers:
            return idx
    return len(draws)


def compute_anchor_scores(draws: List[ContestDraw]) -> List[AnchorScore]:
    if not draws:
        return []

    scores: List[AnchorScore] = []
    all_numbers = range(1, 61)

    freq_windows: Dict[str, Dict[int, float]] = {}
    for window_name, size in WINDOWS.items():
        subset = rolling_windows(draws, min(size, len(draws)))
        freq_windows[window_name] = {
            n: _frequency(subset, n) / len(subset) for n in all_numbers
        }

    delays = {n: _delay(draws, n) for n in all_numbers}

    freq_r50 = np.array([freq_windows["R50"].get(n, 0.0) for n in all_numbers])
    delay_values = np.array([delays[n] for n in all_numbers])

    freq_percentiles = np.percentile(freq_r50, [40, 80])
    delay_percentiles = np.percentile(delay_values, [40, 80])

    def _normalize(value: float, lo: float, hi: float) -> float:
        if hi == lo:
            return 0.0
        clipped = min(max(value, lo), hi)
        return (clipped - lo) / (hi - lo)

    for idx, number in enumerate(all_numbers):
        freq_component = _normalize(freq_r50[idx], freq_percentiles[0], freq_percentiles[1])
        delay_component = _normalize(
            delay_values[idx], delay_percentiles[0], delay_percentiles[1]
        )
        cycle_bias = 0.0
        score = 0.40 * freq_component + 0.35 * delay_component + 0.25 * cycle_bias

        scores.append(
            AnchorScore(
                number=number,
                score=float(score),
                window_freq={k: v[number] for k, v in freq_windows.items()},
                delay=delays[number],
            )
        )

    scores.sort(key=lambda x: x.score, reverse=True)
    return scores

