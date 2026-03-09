# IPL Prediction Tool (Grid-based)

This repository provides a lightweight, spreadsheet-first IPL prediction pool helper for **40 participants**.

## What it does

- Creates a **grid-style CSV** where each row is a match and each player has dedicated columns.
- Supports:
  - `Pick` (team prediction)
  - `Joker` (double points if correct, negative if wrong)
  - `Impact` + `ImpactPick` (change pick before cutoff)
- Calculates:
  - `FinalPick` (after considering impact rules)
  - `Points` per match
  - Leaderboard totals

## Scoring rules

- Normal pick:
  - Correct = `1`
  - Wrong = `0`
- Joker pick:
  - Correct = `2`
  - Wrong = `-1`
- Impact card:
  - If `ImpactWindowOpen` is true and `Impact` is true and `ImpactPick` is filled, `ImpactPick` becomes `FinalPick`.
  - Otherwise `Pick` is used as `FinalPick`.

## Usage

### 1) Create a blank sheet

```bash
python3 ipl_pool.py init --output ipl_predictions.csv --players 40 --matches 74
```

### 2) Fill predictions in your spreadsheet

Open `ipl_predictions.csv` in Google Sheets / Excel.

Populate `TeamA`, `TeamB`, each participant's picks, and eventually `Winner` when matches finish.

### 3) Score all matches

```bash
python3 ipl_pool.py score --file ipl_predictions.csv --players 40
```

### 4) Print leaderboard

```bash
python3 ipl_pool.py leaderboard --file ipl_predictions.csv --players 40
```

## Column layout (per player)

For each player (e.g., `P01`) the sheet includes:

- `P01_Pick`
- `P01_Joker`
- `P01_Impact`
- `P01_ImpactPick`
- `P01_FinalPick` (auto-filled by scoring command)
- `P01_Points` (auto-filled by scoring command)

This keeps all predictions in one place while still making scoring and ranking quick for organizers.
