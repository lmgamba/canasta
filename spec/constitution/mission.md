# Misión

## What we build

Canasta is a local-first grocery intelligence app that scans supermarket receipts and reveals your real consumption patterns over time.

1. **Receipt Scanner** — uploads a receipt photo and uses Google Gemini 2.5 Flash (Vision) to extract every item, price, quantity, and category automatically.
2. **Consumption Dashboard** — shows how much of each product you buy per week/month, which categories dominate your spending, and which items you buy most frequently.
3. **Receipt History** — a chronological log of all scanned receipts with totals and item breakdowns.

## Who it's for

- Anyone who wants to understand their grocery habits beyond just the total amount spent.
- People tracking nutrition or health goals who want to see their actual purchasing patterns.

## Principles

- **Local-first** — all data lives on the user's machine. No accounts, no cloud, no tracking.
- **Zero friction** — one photo, one click, done. The app does the work.
- **Honest data** — what you see reflects exactly what was on your receipt, nothing inferred beyond category assignment.
- **Simple to run** — anyone with Python installed can run Canasta in under two minutes.

## What it is NOT

- Not a general expense tracker — supermarket receipts only.
- Not a diet or calorie tracking app (v1).
- Not a cloud app — there is no hosted version, no login, no shared data.
- Not a mobile app — runs locally in the browser via localhost.