# MegaSena AI Coding Assistant Instructions

## Project Overview
MegaSena is a FastAPI-based backend service that generates lottery number game portfolios using statistical and clustering strategies. The system analyzes historical contest draws to identify anchor numbers and generates optimized game combinations grouped into three strategy clusters (Safe, Hybrid, Zebra).

## Architecture & Data Flow

### Core Components

**main.py** - FastAPI application with 4 endpoints
- `/health`: Liveness check returning model version
- `/anchors`: POST endpoint analyzing historical draws to score numbers (1-60) by frequency and recency
- `/generate`: POST endpoint creating 12-game portfolios with anchors and metrics
- `/config`: GET endpoint exposing strategy configuration

**models.py** - Pydantic data models defining request/response contracts
- `ContestDraw`: Validates 6 unique lottery numbers (1-60) with contest metadata
- `StrategyConfig`: Dataclass defining 3 clusters (S/H/Z) with sum ranges, block rules, and parity constraints
- `GameMetrics`: Computed game properties (sum, even/odd counts, consecutive pairs, etc.)

**anchors.py** - Anchor number scoring algorithm using rolling windows
- Computes frequency in R10/R20/R50 windows and recency (delay) for each number
- Combines metrics with fixed weights (0.40 freq, 0.35 delay, 0.25 cycle_bias)
- Returns top-ranked numbers for portfolio anchoring

### Missing Implementation

File metrics.py is imported but not present. Should contain:
- compute_metrics(): Calculate GameMetrics for a game given numbers and reference draw
- rolling_windows(): Extract last N draws for frequency window calculations

See METRICS_IMPLEMENTATION.md for detailed specifications, examples, and calculation logic for each metric property.

## Development Patterns & Conventions

### Validation & Constraints
- Use Pydantic conlist and conint for field-level validation (e.g., lottery numbers must be 1-60)
- Add @model_validator decorators for cross-field rules (e.g., unique numbers check)
- Raise HTTPException(status_code=400) for invalid request data

### Configuration as Code
- StrategyConfig dataclass holds all strategy parameters; avoid hardcoding elsewhere
- Clusters are named with single letters (S/H/Z) and include descriptive notes in Portuguese
- Constraints like min_terminal_distinct_per_game and max_overlap_default are centralized in config

### Anchor Scoring Algorithm
- Always operate on rolling windows, not full history (prevents recency bias)
- Use numpy for percentile-based normalization to 0-1 range
- Score formula: 0.40 * freq + 0.35 * delay + 0.25 * cycle_bias (weights are semantic, not arbitrary)
- Return sorted descending; use top 2 in portfolio generation

### API Response Structure
- Return Pydantic models directly; FastAPI auto-serializes to JSON
- Always include model_version in responses for tracking schema evolution
- Use descriptive Field() docstrings; they appear in OpenAPI schema

## Critical Files & Workflows

- Schema Changes: Edit models module to update FastAPI auto-generated OpenAPI docs
- Strategy Tuning: Modify cluster parameters or anchor weights in StrategyConfig class
- New Endpoints: Add routes to main module; leverage shared functions from anchors module
- Stub Implementation: metrics module and rolling_windows function incomplete; integration points for future ML pipeline

## Running & Testing

Setup and run the API server:

1. Install dependencies: `pip install -r requirements.txt`
2. Start API: uvicorn with app module and reload flag on port 8000
3. Visit interactive API docs at http://localhost:8000/docs

## Tech Stack
- FastAPI >=0.95.0: Modern async web framework with automatic OpenAPI docs
- Pydantic >=2.0.0: Data validation via type hints and decorators
- NumPy >=1.24.0: Statistical calculations (percentiles, normalization)
- Uvicorn >=0.22.0: ASGI server for development and production
