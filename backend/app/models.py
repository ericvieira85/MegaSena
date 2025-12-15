from dataclasses import dataclass
from typing import List, Sequence

from pydantic import BaseModel, Field, conlist


class ContestDraw(BaseModel):
    contest_id: int = Field(..., description="Unique contest identifier")
    date: str = Field(..., description="Contest date in YYYY-MM-DD format")
    numbers: conlist(int, min_length=6, max_length=6) = Field(
        ..., description="Six unique numbers between 1 and 60"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "contest_id": 1234,
                "date": "2024-01-03",
                "numbers": [3, 14, 21, 37, 45, 56],
            }
        }
    }


class GameMetrics(BaseModel):
    total_sum: int
    even: int
    odd: int
    blocks: int
    terminals_distinct: int
    consecutive_pairs: int
    repeats_last_draw: int


class GeneratedGame(BaseModel):
    cluster: str
    numbers: List[int]
    metrics: GameMetrics


class PortfolioResponse(BaseModel):
    model_version: str
    anchors: List[int] = Field(default_factory=list)
    games: List[GeneratedGame]


@dataclass
class ClusterConfig:
    name: str
    size: int
    sum_min: int
    sum_max: int
    blocks_allowed: Sequence[int]
    parity_allowed: Sequence[str]
    allow_high_50_range: bool = True
    notes: str | None = None


@dataclass
class StrategyConfig:
    model_version: str = "v2.9"
    total_games: int = 12
    clusters: Sequence[ClusterConfig] = (
        ClusterConfig(
            name="S",
            size=4,
            sum_min=165,
            sum_max=190,
            blocks_allowed=(5,),
            parity_allowed=("3-3", "4-2"),
            allow_high_50_range=False,
            notes="Seguro: alvo limpo com blocos completos.",
        ),
        ClusterConfig(
            name="H",
            size=4,
            sum_min=160,
            sum_max=200,
            blocks_allowed=(4, 5),
            parity_allowed=("2-4", "3-3", "4-2"),
            notes="Híbrido: mistura regras clássicas com abertura para variação.",
        ),
        ClusterConfig(
            name="Z",
            size=2,
            sum_min=150,
            sum_max=205,
            blocks_allowed=(4, 5),
            parity_allowed=("2-4", "3-3", "4-2", "5-1", "1-5"),
            notes="Zebra controlada: permite exceções configuráveis.",
        ),
        ClusterConfig(
            name="A",
            size=2,
            sum_min=160,
            sum_max=200,
            blocks_allowed=(4, 5),
            parity_allowed=("2-4", "3-3", "4-2"),
            notes=(
                "Anti-falha: precisa cobrir pelo menos 2 de 3 faixas (1-20, 21-40, 41-60)."
            ),
        ),
    )
    min_terminal_distinct_per_game: int = 4
    max_overlap_default: int = 2
    max_overlap_exceptions_allowed: int = 2
    max_exposure_general: int = 3
    max_exposure_anchor: int = 4
    anchors_per_game_range: tuple[int, int] = (3, 4)
    max_games_with_4_blocks: int = 3
    must_cover_terminals: bool = True
    allow_zebra_parity_extreme: bool = True


strategy_config = StrategyConfig()
