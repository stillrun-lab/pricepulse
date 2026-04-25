# Pricepulse

<<<<<<< HEAD
Configurable price-alert bot. Watches stocks and crypto, fires notifications
to Telegram and Discord when price thresholds are crossed. Deploys on GitHub
Actions cron — no server, no recurring infrastructure.

## What it does

Reads a list of price-watch rules from `alerts.yaml`, polls live prices
on a schedule, and pushes a notification when a threshold is crossed.
Each alert fires once and is deduplicated via a state file committed back
to the repo, so you don't get spammed.

```yaml
# Example alerts.yaml
alerts:
  - symbol: AAPL
    kind: stock
    rule: above
    value: 250.00

  - symbol: bitcoin
    kind: crypto
    rule: below
    value: 90000
    Architecture
┌──────────────────────┐
│ GitHub Actions cron  │  every 15 min
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐    ┌─────────────────┐
│ pricepulse.py        │───►│ Yahoo Finance   │
│  • load alerts.yaml  │    │ CoinGecko       │
│  • fetch prices      │    └─────────────────┘
│  • diff vs state     │
│  • send notifications│
└──────────┬───────────┘
           │
   ┌───────┴────────┐
   ▼                ▼
Telegram        Discord
Features
Stocks via Yahoo Finance (no API key)
Crypto via CoinGecko free API (no API key)
Telegram + Discord webhook notifications (either/both)
State tracking prevents duplicate alerts
One YAML file controls all watched symbols and thresholds
Zero-ops deployment via GitHub Actions
=======
Configurable price-alert bot. Watches stocks and crypto, fires notifications
to Telegram and Discord when price thresholds are crossed. Deploys on GitHub
Actions cron — no server, no recurring infrastructure.

## What it does

Reads a list of price-watch rules from `alerts.yaml`, polls live prices
on a schedule, and pushes a notification when a threshold is crossed.
Each alert fires once and is deduplicated via a state file committed back
to the repo, so you don't get spammed.

```yaml
# Example alerts.yaml
alerts:
  - symbol: AAPL
    kind: stock
    rule: above
    value: 250.00

  - symbol: bitcoin
    kind: crypto
    rule: below
    value: 90000

>>>>>>> 2d76f23cafd117ac4b941218697785c98c7eacab