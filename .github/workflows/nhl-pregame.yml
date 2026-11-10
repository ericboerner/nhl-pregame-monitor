
name: NHL Pregame Monitor

on:
  schedule:
    - cron: '3,13,23,33,43,53 * * * *'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  monitor:
    runs-on: ubuntu-latest
    timeout-minutes: 3
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Run NHL monitor
        run: python3 monitor.py

      - name: Inspect NHL market details
        if: github.event_name == 'workflow_dispatch'
        env:
          ODDSPAPI_API_KEY: ${{ secrets.ODDSPAPI_API_KEY }}
        run: |
          python3 - <<'PY'
          import json
          import os
          import urllib.parse
          import urllib.request
          from datetime import datetime, timedelta, timezone

          key = os.environ["ODDSPAPI_API_KEY"]
          now = datetime.now(timezone.utc)
          end = now + timedelta(hours=12)

          def request(path, params):
              query = urllib.parse.urlencode({
                  **params,
                  "apiKey": key
              })
              url = "https://api.oddspapi.io" + path + "?" + query
              with urllib.request.urlopen(url, timeout=25) as response:
                  return json.load(response)

          fixtures = request("/v4/fixtures", {
              "tournamentId": 234,
              "from": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
              "to": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
              "statusId": 0,
              "hasOdds": "true",
              "bookmakers": "pinnacle"
          })

          print("Upcoming NHL fixtures:", len(fixtures))

          if not fixtures:
              print("No NHL fixtures in the next 12 hours.")
          else:
              fixture = fixtures[0]
              fixture_id = fixture["fixtureId"]
              print("Fixture:", fixture.get("participant1Name"),
                    "vs", fixture.get("participant2Name"))
              print("Start:", fixture.get("startTime"))

              odds = request("/v4/odds", {
                  "fixtureId": fixture_id,
                  "bookmakers": "pinnacle",
                  "oddsFormat": "decimal",
                  "language": "en",
                  "verbosity": 2
              })

              pinnacle = odds.get("bookmakerOdds", {}).get("pinnacle", {})
              markets = pinnacle.get("markets", {})

              print("Market count:", len(markets))

              for market_id, market in list(markets.items())[:40]:
                  print("\nMARKET ID:", market_id)
                  print("Data type:", type(market).__name__)

                  if isinstance(market, dict):
                      print("Fields:", list(market.keys()))

                      for field in (
                          "marketName", "name", "label",
                          "marketType", "description",
                          "outcomes", "selections", "bets"
                      ):
                          if field in market:
                              value = market[field]
                              if isinstance(value, (dict, list)):
                                  print(field + ":", json.dumps(value)[:700])
                              else:
                                  print(field + ":", value)
                  else:
                      print("Value preview:", str(market)[:200])

              print("\nMarket detail inspection complete")
          PY
