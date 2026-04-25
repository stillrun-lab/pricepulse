# Pricepulse

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
