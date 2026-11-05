#!/usr/bin/env python3
"""
Dashboard & Multi-Page AI Admin Builder v4.0 (dashboard_builder.py)
Builds the 6-page AI Admin Control Plane for both:
  1. Live HTTP Server on port 8090 (~/.gemini/orchestrator/admin/static/*.html)
  2. Antigravity Artifact Directory (rsi_control_center.html + 6 sibling pages)
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from rsi_engine.cockpit_pages_tpl import COCKPIT_V4_HTML_TEMPLATE
    from rsi_engine.cockpit_script_tpl import COCKPIT_V4_SCRIPT_TEMPLATE
    from rsi_engine.core import DEFAULT_DB_PATH, RSIEngine
    from rsi_engine.skill_forge import evaluate_skill_dir
else:
    from .cockpit_pages_tpl import COCKPIT_V4_HTML_TEMPLATE
    from .cockpit_script_tpl import COCKPIT_V4_SCRIPT_TEMPLATE
    from .core import DEFAULT_DB_PATH, RSIEngine
    from .skill_forge import evaluate_skill_dir

ORCH_ROOT = Path.home() / ".gemini" / "orchestrator"
if str(ORCH_ROOT) not in sys.path:
    sys.path.insert(0, str(ORCH_ROOT))

NEW_RSI_SKILLS = {
    "aide-tree-explorer",
    "specbench-eval-guard",
    "rsi-skill-evolver",
    "causal-hypothesis-distiller",
    "evolution-bloat-pruner",
}

MULTI_PAGES: list[tuple[str, str, str]] = [
    ("index.html", "dashboard", "1. 🎛️ Пульт & ИИ-Симулятор"),
    ("rsi-studio.html", "rsi", "2. 🌳 Студия Дерева AIDE² & Кода"),
    ("debates.html", "debates", "3. 🗣️ Дебаты Совета & Мышление Агентов"),
    ("judges.html", "judges", "4. ⚖️ Коллегия из 3 Судей & Вердикты"),
    ("skills-editor.html", "skills", "5. 🧬 Редактор 30 Скилов SkillForge"),
    ("help-guide.html", "help", "6. 📖 Интерактивный Хелп «На пальцах»"),
]


def collect_payload(db_path: Path = DEFAULT_DB_PATH) -> dict[str, Any]:
    engine = RSIEngine(db_path=db_path)
    tree_status = engine.get_tree_status("weco_fraud_golf")
    next_step_info = engine.select_next_step("weco_fraud_golf")

    with engine._connect() as conn:
        full_nodes = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM nodes WHERE campaign_id = 'weco_fraud_golf' ORDER BY step_num ASC"
            ).fetchall()
        ]

    hyp_by_node = {h["node_id"]: h for h in tree_status["causal_hypotheses"]}
    pareto_ids = {n["node_id"] for n in tree_status["pareto_frontier"]}
    champ_id = tree_status["champion_node"]["node_id"] if tree_status["champion_node"] else None

    human_explanations = {
        "node_000_draft": {
            "short_title": "Черновик #0: Простой порог суммы",
            "plain_why": "Отправная точка дерева (Root DRAFT). Проверяет только условие amount > 600. На секретном тесте даёт лишь 56.25%.",
        },
        "node_001_improve": {
            "short_title": "Улучшение #1: Учёт зарубежных переводов",
            "plain_why": "Ветка от #0. Добавлено правило для зарубежных транзакций (foreign == 1 и amount > 300). Точность честно выросла с 56.25% до 75.00%.",
        },
        "node_002_improve": {
            "short_title": "Атака читерства #2: Зазубривание ответов",
            "plain_why": "Агент захардкодил точные суммы из открытого теста (980, 420, 720, 130, 90). На открытом тесте получил 100%, но на секретном провалился до 68.75% (Δ = 0.3125 > 0.18). Судья №1 SpecGuard наложил ВЕТО!",
        },
        "node_003_improve": {
            "short_title": "Плато #3: Бесполезная подкрутка числа",
            "plain_why": "Попытка сдвинуть порог с 600 до 580 не дала прироста (75.00% → 75.00%). Сработал детектор стагнации Plateau Signal: нужна новая идея!",
        },
        "node_004_fuse": {
            "short_title": "Слияние #4 (FUSE): Прорыв по подсказке Шефа",
            "plain_why": "Шеф вбросил идею многофакторной формулы риска. Точность пробила потолок до 100% на обоих тестах! Но в коде осталась мёртвая функция deprecated_amount_bucketer и лишние import math/json (14 LOC).",
        },
        "node_005_prune": {
            "short_title": "Очистка #5 (PRUNE): Парето-Чемпион",
            "plain_why": "Судья №3 (OMEGA + BloatPruner) вычистил мёртвую функцию и лишние импорты из узла #4. Код сжался с 14 до 8 строк при сохранении 100% точности!",
        },
    }

    enriched_nodes = []
    for n in full_nodes:
        nid = n["node_id"]
        h = hyp_by_node.get(nid, {})
        outcome = h.get("outcome", "INCREMENTAL")
        if n["verdict"] == "REWARD_HACK_BLOCKED":
            priority, priority_label = "P1", "P1 · Вето чита"
        elif nid == champ_id:
            priority, priority_label = "P1", "P1 · Чемпион"
        elif outcome in ("BREAKTHROUGH", "PRUNED_LEAN"):
            priority, priority_label = "P2", "P2 · Прорыв"
        elif outcome == "NO_GAIN":
            priority, priority_label = "P4", "P4 · Плато"
        else:
            priority, priority_label = "P3", "P3 · Штатный"

        exp = human_explanations.get(nid, {})
        enriched_nodes.append(
            {
                **n,
                "outcome": outcome,
                "score_delta": h.get("score_delta", 0.0),
                "lesson_learned": h.get("lesson_learned", ""),
                "is_pareto": nid in pareto_ids,
                "is_champion": nid == champ_id,
                "priority": priority,
                "priority_label": priority_label,
                "short_title": exp.get("short_title", nid),
                "plain_why": exp.get("plain_why", n["hypothesis"]),
            }
        )

    skills_root = Path.home() / ".gemini" / "skills"
    skills_list = []
    if skills_root.exists():
        for d in sorted(skills_root.iterdir()):
            if d.is_dir() and (d / "SKILL.md").exists():
                rep = evaluate_skill_dir(d)
                d_dict = rep.to_dict()
                d_dict["is_new_rsi"] = rep.skill_name in NEW_RSI_SKILLS
                if d_dict["is_new_rsi"]:
                    d_dict["priority"] = "P1 · RSI Core"
                elif len(d_dict["bundled_scripts"]) > 0:
                    d_dict["priority"] = "P2 · Scripted"
                else:
                    d_dict["priority"] = "P3 · Text Skill"
                skills_list.append(d_dict)

    return {
        "generated_at": tree_status["campaign"]["created_at"] if tree_status.get("campaign") else "2026-11-05T05:55:00Z",
        "campaign": tree_status["campaign"],
        "next_step": next_step_info,
        "nodes": enriched_nodes,
        "skills": skills_list,
        "summary": {
            "total_nodes": len(enriched_nodes),
            "accepted_nodes": sum(1 for x in enriched_nodes if x["verdict"] == "ACCEPTED"),
            "blocked_hacks": sum(1 for x in enriched_nodes if x["verdict"] == "REWARD_HACK_BLOCKED"),
            "champion_id": champ_id,
            "champion_score": tree_status["champion_node"]["private_score"] if tree_status["champion_node"] else 1.0,
            "champion_loc": tree_status["champion_node"]["code_loc"] if tree_status["champion_node"] else 8,
            "total_skills": len(skills_list),
            "scripted_skills": sum(1 for s in skills_list if len(s["bundled_scripts"]) > 0),
            "avg_skill_fitness": round(
                sum(s["composite_fitness"] for s in skills_list) / max(1, len(skills_list)), 2
            ),
        },
    }


def render_page_html(snapshot: dict[str, Any], initial_page: str, page_title: str) -> str:
    full_tpl = COCKPIT_V4_HTML_TEMPLATE + COCKPIT_V4_SCRIPT_TEMPLATE
    return (
        full_tpl.replace("__PAGE_TITLE__", page_title)
        .replace("__GENERATED_AT__", str(snapshot.get("generated_at", "2026-11-05T05:55:00Z")))
        .replace("__INITIAL_PAGE__", initial_page)
        .replace("__SNAPSHOT_JSON__", json.dumps(snapshot, ensure_ascii=False))
    )


def build_dashboard(output_html: Path, db_path: Path = DEFAULT_DB_PATH) -> dict[str, Any]:
    hive_db = ORCH_ROOT / "hive_mind.db"
    hive_conn = sqlite3.connect(str(hive_db))
    hive_conn.row_factory = sqlite3.Row
    try:
        from admin.rsi_council_api import build_collegium_verdicts, ensure_default_debates_and_collegium, load_debates_list

        ensure_default_debates_and_collegium(hive_conn)
        rsi_data = collect_payload(db_path=db_path)
        debates = load_debates_list()
        collegium = build_collegium_verdicts(hive_conn, rsi_data["nodes"])
        dir_rows = hive_conn.execute("SELECT * FROM directives ORDER BY code ASC").fetchall()
        directives = [dict(r) for r in dir_rows]
    finally:
        hive_conn.close()

    snapshot = {
        "status": "ok",
        "generated_at": rsi_data["generated_at"],
        "config": {
            "mode": "full",
            "max_hack_gap": 0.18,
            "plateau_window": 2,
            "golden_threshold": 85,
            "judge_domain_weight": 1.5,
            "auto_prune_enabled": True,
        },
        "rsi": rsi_data,
        "debates": debates,
        "collegium_verdicts": collegium,
        "directives": directives,
    }

    output_html.parent.mkdir(parents=True, exist_ok=True)
    static_dir = ORCH_ROOT / "admin" / "static"
    static_dir.mkdir(parents=True, exist_ok=True)

    pages_written = []
    for fname, page_key, title in MULTI_PAGES:
        html_str = render_page_html(snapshot, initial_page=page_key, page_title=title)
        (static_dir / fname).write_text(html_str, encoding="utf-8")
        (output_html.parent / fname).write_text(html_str, encoding="utf-8")
        pages_written.append(fname)

    # Also write main artifact file (e.g. rsi_control_center.html)
    main_html = render_page_html(snapshot, initial_page="dashboard", page_title="RSI COCKPIT v3.0 / AI ADMIN v4.0")
    output_html.write_text(main_html, encoding="utf-8")

    return {
        "output_html": str(output_html),
        "pages_written": pages_written,
        "size_bytes": len(main_html.encode("utf-8")),
        "nodes_embedded": len(rsi_data["nodes"]),
        "skills_embedded": len(rsi_data["skills"]),
        "debates_embedded": len(debates),
        "collegium_verdicts_embedded": len(collegium),
        "champion_id": rsi_data["summary"]["champion_id"],
    }


if __name__ == "__main__":
    default_out = Path(
        "/home/antigravity/.gemini/jetski/brain/v1/default/jetski_remote_agents_3p/9af70b28-36a4-4bbf-9eb7-f4a167627b3d/rsi_control_center.html"
    )
    parser = argparse.ArgumentParser(description="Build Multi-Page AI Admin v4.0")
    parser.add_argument("positional_out", nargs="?", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--kag", default="")
    args = parser.parse_args()

    out_file = Path(args.out or args.positional_out or default_out).resolve()
    info = build_dashboard(out_file, db_path=Path(args.db))
    print(json.dumps(info, ensure_ascii=False, indent=2))
