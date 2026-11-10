
"""NHL pregame Pinnacle odds parser — safe mode."""

import json
from datetime import datetime, timezone
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name("config.json")

NHL_SPORT_ID = 15
NHL_TOURNAMENT_ID = 234
BOOKMAKER = "pinnacle"


def load_config():
    with CONFIG_PATH.open(encoding="utf-8") as file:
        config = json.load(file)

    if config.get("sport") != "NHL":
        raise ValueError("Only NHL monitoring is permitted")

    if config.get("pregame_only") is not True:
        raise ValueError("Live odds are not permitted")

    if set(config.get("player_props", [])) != {
        "goals", "points"
    }:
        raise ValueError(
            "Only goals and points player props are permitted"
        )

    if config.get("real_odds_enabled") is not False:
        raise ValueError(
            "Real odds polling is disabled until quota protection exists"
        )

    return config


def implied_probability(decimal_odds):
    """Return the raw implied probability, before removing vig."""
    try:
        odds = float(decimal_odds)
    except (TypeError, ValueError):
        return None

    if odds <= 1:
        return None

    return 1.0 / odds


def parse_pinnacle_odds(response):
    """Extract active Pinnacle outcomes from an OddsPapi response."""
    bookmaker_odds = response.get("bookmakerOdds", {})
    pinnacle = bookmaker_odds.get(BOOKMAKER, {})
    markets = pinnacle.get("markets", {})

    if not isinstance(markets, dict):
        return []

    parsed = []

    for market_id, market in markets.items():
        if not isinstance(market, dict):
            continue

        if market.get("marketActive") is False:
            continue

        outcomes = market.get("outcomes", {})

        if not isinstance(outcomes, dict):
            continue

        for outcome_id, outcome in outcomes.items():
            if not isinstance(outcome, dict):
                continue

            players = outcome.get("players", {})

            if not isinstance(players, dict):
                continue

            for player_id, selection in players.items():
                if not isinstance(selection, dict):
                    continue

                if selection.get("active") is not True:
                    continue

                price = selection.get("price")
                probability = implied_probability(price)

                if probability is None:
                    continue

                parsed.append({
                    "market_id": str(market_id),
                    "outcome_id": str(outcome_id),
                    "player_id": str(player_id),
                    "outcome": selection.get(
                        "bookmakerOutcomeId"
                    ),
                    "player_name": selection.get(
                        "playerName"
                    ),
                    "decimal_odds": float(price),
                    "raw_implied_probability": probability,
                    "main_line": selection.get(
                        "mainLine"
                    ),
                    "last_changed": selection.get(
                        "changedAt"
                    ),
                })

    return parsed


def main():
    config = load_config()

    print(
        datetime.now(timezone.utc).isoformat(),
        "NHL pregame monitor"
    )

    print("Sport ID:", NHL_SPORT_ID)
    print("NHL tournament ID:", NHL_TOURNAMENT_ID)
    print("Bookmaker:", BOOKMAKER)
    print("Lookahead hours:", config["lookahead_hours"])
    print("Minimum edge:", config["min_edge_percentage_points"])
    print("Allowed player props:", config["player_props"])

    print("SAFE MODE ACTIVE")
    print("Pinnacle odds parser loaded successfully")
    print("No API requests made")
    print("No Polymarket comparisons performed")
    print("No alerts sent")
    print("No bets placed")


if __name__ == "__main__":
    main()
