"""Safe-mode NHL pregame scheduled check. No live odds API or Telegram calls."""
import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    config = json.loads(Path(__file__).with_name("config.json").read_text())
    assert config["sport"] == "NHL" and config["pregame_only"]
    assert set(config["player_props"]) == {"goals", "points"}
    assert config["min_edge_percentage_points"] == 3
    print(f"{datetime.now(timezone.utc).isoformat()} NHL pregame monitor scheduled check")
    print("SAFE MODE: no odds requests, no comparisons, no alerts, no bets.")
    if config["real_odds_enabled"]:
        raise RuntimeError("Live odds mode is not implemented; keep real_odds_enabled=false")


if __name__ == "__main__":
    main()
