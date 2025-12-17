from typing import List

from fastapi import FastAPI

from .anchors import AnchorScore, compute_anchor_scores
from .generator import build_portfolio
from .models import ContestDraw, PortfolioResponse, strategy_config

app = FastAPI(title="MegaSena Strategy API", version=strategy_config.model_version)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok", "model_version": strategy_config.model_version}


@app.post("/anchors", response_model=List[AnchorScore])
def anchor_candidates(draws: List[ContestDraw]) -> List[AnchorScore]:
    return compute_anchor_scores(draws)


@app.post("/generate", response_model=PortfolioResponse)
def generate_portfolio(draws: List[ContestDraw]) -> PortfolioResponse:
    return build_portfolio(draws)


@app.get("/config")
def get_config() -> dict:
    return {
        "model_version": strategy_config.model_version,
        "clusters": [cluster.__dict__ for cluster in strategy_config.clusters],
        "constraints": {
            "min_terminal_distinct_per_game": strategy_config.min_terminal_distinct_per_game,
            "max_overlap_default": strategy_config.max_overlap_default,
            "max_overlap_exceptions_allowed": strategy_config.max_overlap_exceptions_allowed,
            "max_exposure_general": strategy_config.max_exposure_general,
            "max_exposure_anchor": strategy_config.max_exposure_anchor,
            "anchors_per_game_range": strategy_config.anchors_per_game_range,
            "max_games_with_4_blocks": strategy_config.max_games_with_4_blocks,
            "must_cover_terminals": strategy_config.must_cover_terminals,
            "allow_zebra_parity_extreme": strategy_config.allow_zebra_parity_extreme,
            "max_repeat_last_draw_per_game": strategy_config.max_repeat_last_draw_per_game,
            "max_repeat_last_draw_per_number_portfolio": strategy_config.max_repeat_last_draw_per_number_portfolio,
            "candidate_pool_size": strategy_config.candidate_pool_size,
            "repair_attempts": strategy_config.repair_attempts,
        },
    }

