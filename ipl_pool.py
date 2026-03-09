#!/usr/bin/env python3
"""IPL prediction pool helper.

Creates and scores a grid-style CSV designed for spreadsheet use.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List


BASE_COLUMNS = [
    "MatchNo",
    "MatchLabel",
    "TeamA",
    "TeamB",
    "Winner",
    "ImpactWindowOpen",
]


@dataclass(frozen=True)
class PlayerColumns:
    name: str

    @property
    def pick(self) -> str:
        return f"{self.name}_Pick"

    @property
    def joker(self) -> str:
        return f"{self.name}_Joker"

    @property
    def impact(self) -> str:
        return f"{self.name}_Impact"

    @property
    def impact_pick(self) -> str:
        return f"{self.name}_ImpactPick"

    @property
    def final_pick(self) -> str:
        return f"{self.name}_FinalPick"

    @property
    def points(self) -> str:
        return f"{self.name}_Points"

    def all_columns(self) -> List[str]:
        return [
            self.pick,
            self.joker,
            self.impact,
            self.impact_pick,
            self.final_pick,
            self.points,
        ]


def normalize_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def player_names(count: int) -> List[str]:
    return [f"P{i:02d}" for i in range(1, count + 1)]


def headers_for_players(players: Iterable[str]) -> List[str]:
    headers = BASE_COLUMNS.copy()
    for name in players:
        headers.extend(PlayerColumns(name).all_columns())
    return headers


def init_sheet(output: Path, players: int, matches: int) -> None:
    names = player_names(players)
    headers = headers_for_players(names)

    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for i in range(1, matches + 1):
            row: Dict[str, str] = {h: "" for h in headers}
            row["MatchNo"] = str(i)
            row["MatchLabel"] = f"Match {i}"
            row["ImpactWindowOpen"] = "TRUE"
            writer.writerow(row)


def pick_final(row: Dict[str, str], cols: PlayerColumns) -> str:
    original = row.get(cols.pick, "").strip()
    impact_used = normalize_bool(row.get(cols.impact, ""))
    impact_allowed = normalize_bool(row.get("ImpactWindowOpen", ""))
    impact_pick = row.get(cols.impact_pick, "").strip()

    if impact_used and impact_allowed and impact_pick:
        return impact_pick
    return original


def score_row(row: Dict[str, str], players: Iterable[str]) -> None:
    winner = row.get("Winner", "").strip()

    for name in players:
        cols = PlayerColumns(name)
        final = pick_final(row, cols)
        row[cols.final_pick] = final

        joker = normalize_bool(row.get(cols.joker, ""))
        if not winner or not final:
            row[cols.points] = ""
            continue

        if final == winner:
            row[cols.points] = "2" if joker else "1"
        else:
            row[cols.points] = "-1" if joker else "0"


def score_sheet(path: Path, players: int) -> None:
    names = player_names(players)
    headers = headers_for_players(names)

    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    for row in rows:
        score_row(row, names)

    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def total_points(path: Path, players: int) -> List[tuple[str, int]]:
    names = player_names(players)
    totals = {name: 0 for name in names}

    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            for name in names:
                points_col = PlayerColumns(name).points
                value = row.get(points_col, "").strip()
                if value:
                    totals[name] += int(value)

    return sorted(totals.items(), key=lambda item: item[1], reverse=True)


def print_leaderboard(path: Path, players: int) -> None:
    board = total_points(path, players)
    print("Leaderboard")
    print("-----------")
    for rank, (name, pts) in enumerate(board, start=1):
        print(f"{rank:>2}. {name}: {pts}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="IPL prediction pool CSV helper")
    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init", help="Create a blank grid-style CSV")
    init_p.add_argument("--output", default="ipl_predictions.csv", type=Path)
    init_p.add_argument("--players", default=40, type=int)
    init_p.add_argument("--matches", default=74, type=int)

    score_p = sub.add_parser("score", help="Update final picks and points in CSV")
    score_p.add_argument("--file", default="ipl_predictions.csv", type=Path)
    score_p.add_argument("--players", default=40, type=int)

    board_p = sub.add_parser("leaderboard", help="Print player rankings")
    board_p.add_argument("--file", default="ipl_predictions.csv", type=Path)
    board_p.add_argument("--players", default=40, type=int)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        init_sheet(args.output, args.players, args.matches)
        print(f"Created {args.output}")
    elif args.command == "score":
        score_sheet(args.file, args.players)
        print(f"Scored {args.file}")
    elif args.command == "leaderboard":
        print_leaderboard(args.file, args.players)


if __name__ == "__main__":
    main()
