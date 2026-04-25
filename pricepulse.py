"""
Pricepulse — configurable price-alert bot.

Reads alerts.yaml, fetches current prices, and fires Telegram/Discord
notifications when thresholds cross. Deduplicates via state/fired.json.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml
import yfinance as yf

BASE = Path(__file__).parent
ALERTS_FILE = BASE / "alerts.yaml"
STATE_FILE = BASE / "state" / "fired.json"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")


def load_alerts() -> list[dict]:
    with ALERTS_FILE.open() as f:
        return yaml.safe_load(f).get("alerts", [])


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_stock_price(symbol: str) -> float | None:
    try:
        t = yf.Ticker(symbol)
        price = t.fast_info.get("last_price")
        if price is None:
            hist = t.history(period="1d")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
        return float(price) if price else None
    except Exception as e:
        print(f"  ! {symbol}: fetch failed ({e})", file=sys.stderr)
        return None


def get_crypto_price(symbol: str) -> float | None:
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": symbol, "vs_currencies": "usd"},
            timeout=10,
        )
        r.raise_for_status()
        return r.json().get(symbol, {}).get("usd")
    except Exception as e:
        print(f"  ! {symbol}: fetch failed ({e})", file=sys.stderr)
        return None


def check_alert(alert: dict, price: float) -> str | None:
    sym, rule, threshold = alert["symbol"], alert["rule"], alert["value"]
    if rule == "above" and price > threshold:
        return f"📈 {sym.upper()} crossed ABOVE {threshold} (now ${price:,.2f})"
    if rule == "below" and price < threshold:
        return f"📉 {sym.upper()} crossed BELOW {threshold} (now ${price:,.2f})"
    return None


def alert_key(alert: dict) -> str:
    return f"{alert['symbol']}:{alert['rule']}:{alert['value']}"


def send_telegram(msg: str) -> None:
    if not (TELEGRAM_TOKEN and TELEGRAM_CHAT):
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT, "text": msg},
            timeout=10,
        )
    except Exception as e:
        print(f"  ! telegram failed: {e}", file=sys.stderr)


def send_discord(msg: str) -> None:
    if not DISCORD_WEBHOOK:
        return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg}, timeout=10)
    except Exception as e:
        print(f"  ! discord failed: {e}", file=sys.stderr)


def notify(msg: str) -> None:
    print(f"  → {msg}")
    send_telegram(msg)
    send_discord(msg)


def main() -> int:
    alerts = load_alerts()
    state = load_state()
    now = datetime.now(timezone.utc).isoformat()
    print(f"[{now}] Pricepulse — checking {len(alerts)} alert(s)")

    for alert in alerts:
        sym = alert["symbol"]
        kind = alert.get("kind", "stock")
        price = get_crypto_price(sym) if kind == "crypto" else get_stock_price(sym)
        if price is None:
            continue

        key = alert_key(alert)
        if state.get(key, {}).get("fired"):
            print(f"  · {sym} ${price:,.2f} (already fired)")
            continue

        if (msg := check_alert(alert, price)):
            notify(msg)
            state[key] = {"fired": True, "at": now, "price": price}
        else:
            print(f"  · {sym} ${price:,.2f} (no trigger)")

    save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())