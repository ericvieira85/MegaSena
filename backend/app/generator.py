import random
from collections import Counter
from typing import List, Sequence, Tuple

from .anchors import compute_anchor_scores
from .metrics import blocks, compute_metrics, consecutive_pairs, parity, terminals
from .models import ContestDraw, GeneratedGame, PortfolioResponse, StrategyConfig, strategy_config


def _parity_label(numbers: Sequence[int]) -> str:
    even, odd = parity(numbers)
    return f"{even}-{odd}"


def _has_required_ranges(numbers: Sequence[int]) -> int:
    low = sum(1 for n in numbers if 1 <= n <= 20)
    mid = sum(1 for n in numbers if 21 <= n <= 40)
    high = sum(1 for n in numbers if 41 <= n <= 60)
    checks = [high >= 2, mid >= 2, low >= 1]
    return sum(checks)


def _valid_base_constraints(
    numbers: Sequence[int],
    cluster: str,
    last_draw: ContestDraw,
    cfg: StrategyConfig,
) -> bool:
    if len(set(numbers)) != 6:
        return False
    if any(n < 1 or n > 60 for n in numbers):
        return False

    total_sum = sum(numbers)
    if total_sum < 145 or total_sum > 215:
        return False

    if cluster == "Z":
        if not (150 <= total_sum <= 205):
            return False
    else:
        if not (160 <= total_sum <= 195):
            return False

    terminal_distinct = len(terminals(numbers))
    if terminal_distinct < cfg.min_terminal_distinct_per_game:
        return False

    if consecutive_pairs(numbers) > 1:
        return False

    repeats_last = sum(1 for n in numbers if n in last_draw.numbers)
    if repeats_last > cfg.max_repeat_last_draw_per_game:
        return False

    return True


def _valid_cluster_constraints(numbers: Sequence[int], cluster_cfg, last_draw: ContestDraw, cfg: StrategyConfig) -> bool:
    metrics = compute_metrics(numbers, last_draw)

    if metrics.blocks not in cluster_cfg.blocks_allowed:
        return False

    parity_label = _parity_label(numbers)
    if parity_label not in cluster_cfg.parity_allowed:
        if not (
            cluster_cfg.name == "Z"
            and cfg.allow_zebra_parity_extreme
            and parity_label in {"5-1", "1-5"}
        ):
            return False

    if metrics.total_sum < cluster_cfg.sum_min or metrics.total_sum > cluster_cfg.sum_max:
        return False

    if cluster_cfg.name == "A":
        if _has_required_ranges(numbers) < 2:
            return False

    return True


def _overlap(a: Sequence[int], b: Sequence[int]) -> int:
    return len(set(a).intersection(b))


def _fits_global_constraints(
    candidate: Sequence[int],
    cluster_blocks: int,
    current_games: List[GeneratedGame],
    exposures: Counter,
    anchor_numbers: set[int],
    overlap_exceptions_left: int,
    cfg: StrategyConfig,
    last_draw: ContestDraw,
    last_draw_counts: Counter,
    games_with_4_blocks: int,
) -> Tuple[bool, int, int]:
    # exposure caps
    for n in candidate:
        cap = cfg.max_exposure_anchor if n in anchor_numbers else cfg.max_exposure_general
        if exposures[n] + 1 > cap:
            return False, overlap_exceptions_left, games_with_4_blocks
        if n in last_draw.numbers and last_draw_counts[n] + 1 > cfg.max_repeat_last_draw_per_number_portfolio:
            return False, overlap_exceptions_left, games_with_4_blocks

    # overlap checks
    for game in current_games:
        inter = _overlap(candidate, game.numbers)
        if inter > cfg.max_overlap_default:
            if inter == 3 and overlap_exceptions_left > 0:
                overlap_exceptions_left -= 1
            else:
                return False, overlap_exceptions_left, games_with_4_blocks

    if cluster_blocks == 4 and games_with_4_blocks + 1 > cfg.max_games_with_4_blocks:
        return False, overlap_exceptions_left, games_with_4_blocks

    return True, overlap_exceptions_left, games_with_4_blocks + (1 if cluster_blocks == 4 else 0)


def _generate_candidate(cluster_cfg, anchors: List[int]) -> List[int]:
    candidate: set[int] = set()

    # Mild encouragement to include anchors
    for anchor in anchors:
        if len(candidate) < 3 and random.random() < 0.7:
            candidate.add(anchor)

    while len(candidate) < 6:
        candidate.add(random.randint(1, 60))

    return sorted(candidate)


def _repair_terminal_coverage(
    games: List[GeneratedGame],
    missing_terminals: List[int],
    cluster_map: dict,
    last_draw: ContestDraw,
    cfg: StrategyConfig,
    anchors: List[int],
) -> List[GeneratedGame]:
    replacements: List[GeneratedGame] = games.copy()
    terminals_by_game = [terminals(g.numbers) for g in replacements]

    for terminal in missing_terminals:
        replaced = False
        for idx, game in enumerate(replacements):
            if terminals_by_game[idx].get(terminal, 0) == 0:
                cluster_cfg = cluster_map[game.cluster]
                for _ in range(cfg.repair_attempts):
                    candidate = _generate_candidate(cluster_cfg, anchors)
                    if candidate and candidate != game.numbers:
                        metrics = compute_metrics(candidate, last_draw)
                        if _valid_base_constraints(candidate, cluster_cfg.name, last_draw, cfg) and _valid_cluster_constraints(candidate, cluster_cfg, last_draw, cfg):
                            if (terminal in [n % 10 for n in candidate]):
                                replacements[idx] = GeneratedGame(cluster=game.cluster, numbers=candidate, metrics=metrics)
                                replaced = True
                                break
                if replaced:
                    break
    return replacements


def build_portfolio(draws: List[ContestDraw], cfg: StrategyConfig = strategy_config) -> PortfolioResponse:
    if not draws:
        raise ValueError("At least one contest draw is required")

    last_draw = draws[-1]
    anchor_scores = compute_anchor_scores(draws)
    anchors = [score.number for score in anchor_scores[:2]]
    anchor_set = set(anchors)

    games: List[GeneratedGame] = []
    exposures: Counter = Counter()
    last_draw_counts: Counter = Counter()
    overlap_exceptions_left = cfg.max_overlap_exceptions_allowed
    games_with_4_blocks = 0

    cluster_map = {cluster.name: cluster for cluster in cfg.clusters}

    for cluster_cfg in cfg.clusters:
        attempts = 0
        needed = cluster_cfg.size
        while needed > 0 and attempts < cfg.candidate_pool_size:
            attempts += 1
            candidate = _generate_candidate(cluster_cfg, anchors)

            if not _valid_base_constraints(candidate, cluster_cfg.name, last_draw, cfg):
                continue
            if not _valid_cluster_constraints(candidate, cluster_cfg, last_draw, cfg):
                continue

            cluster_blocks = blocks(candidate)
            fits, overlap_exceptions_left, games_with_4_blocks = _fits_global_constraints(
                candidate,
                cluster_blocks,
                games,
                exposures,
                anchor_set,
                overlap_exceptions_left,
                cfg,
                last_draw,
                last_draw_counts,
                games_with_4_blocks,
            )
            if not fits:
                continue

            metrics = compute_metrics(candidate, last_draw)
            games.append(
                GeneratedGame(
                    cluster=cluster_cfg.name,
                    numbers=sorted(candidate),
                    metrics=metrics,
                )
            )

            exposures.update(candidate)
            last_draw_counts.update([n for n in candidate if n in last_draw.numbers])
            needed -= 1

    if len(games) != cfg.total_games:
        raise RuntimeError("Unable to generate full portfolio within constraints")

    if cfg.must_cover_terminals:
        covered = set()
        for game in games:
            covered.update(n % 10 for n in game.numbers)
        missing = [t for t in range(10) if t not in covered]
        if missing:
            games = _repair_terminal_coverage(games, missing, cluster_map, last_draw, cfg, anchors)

    return PortfolioResponse(model_version=cfg.model_version, anchors=anchors, games=games)

