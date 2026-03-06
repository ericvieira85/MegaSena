from collections import Counter
from typing import Iterable, List, Sequence, Tuple

from .models import ContestDraw, GameMetrics


BLOCKS = (
    range(1, 11),
    range(11, 21),
    range(21, 31),
    range(31, 41),
    range(41, 51),
    range(51, 61),
)


def _block_index(number: int) -> int:
    for idx, block in enumerate(BLOCKS, start=1):
        if number in block:
            return idx
    raise ValueError(f"Number {number} out of range 1-60")


def parity(numbers: Sequence[int]) -> Tuple[int, int]:
    even = sum(1 for n in numbers if n % 2 == 0)
    odd = len(numbers) - even
    return even, odd


def blocks(numbers: Sequence[int]) -> int:
    present = {_block_index(n) for n in numbers}
    return len(present)


def terminals(numbers: Sequence[int]) -> Counter:
    return Counter(n % 10 for n in numbers)


def consecutive_pairs(numbers: Sequence[int]) -> int:
    sorted_numbers = sorted(numbers)
    return sum(1 for a, b in zip(sorted_numbers, sorted_numbers[1:]) if b - a == 1)


def count_repeats(numbers: Sequence[int], last_draw: ContestDraw) -> int:
    last_set = set(last_draw.numbers)
    return sum(1 for n in numbers if n in last_set)


def compute_metrics(numbers: Sequence[int], last_draw: ContestDraw) -> GameMetrics:
    even, odd = parity(numbers)
    terminals_count = terminals(numbers)
    return GameMetrics(
        total_sum=sum(numbers),
        even=even,
        odd=odd,
        blocks=blocks(numbers),
        terminals_distinct=len(terminals_count),
        consecutive_pairs=consecutive_pairs(numbers),
        repeats_last_draw=count_repeats(numbers, last_draw),
    )


def rolling_windows(draws: List[ContestDraw], window: int) -> List[ContestDraw]:
    if window <= 0:
        raise ValueError("Window must be positive")
    return draws[-window:]

