#!/usr/bin/env python3
"""
Unified CLI for the RSI Evolution Engine (AIDE² + SpecBench + EvoSkill + HyperAgents)
Can be invoked directly from terminal, subagents, or bundled skill scripts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from rsi_engine.bloat_pruner import analyze_file_bloat
    from rsi_engine.core import DEFAULT_DB_PATH, RSIEngine
    from rsi_engine.skill_forge import compress_skill_markdown, evaluate_skill_dir
    from rsi_engine.specguard import evaluate_two_tier
else:
    from .bloat_pruner import analyze_file_bloat
    from .core import DEFAULT_DB_PATH, RSIEngine
    from .skill_forge import compress_skill_markdown, evaluate_skill_dir
    from .specguard import evaluate_two_tier


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RSI Evolution Engine CLI (AIDE² Tree Search + SpecGuard + SkillForge + BloatPruner)"
    )
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="Path to SQLite database")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # 1. init-campaign
    p_init = sub.add_parser("init-campaign", help="Initialize an AIDE² tree search campaign")
    p_init.add_argument("--id", required=True, help="Campaign ID")
    p_init.add_argument("--name", required=True, help="Human-readable campaign name")
    p_init.add_argument("--target", required=True, help="Path to mutable target code file")
    p_init.add_argument("--workdir", default=".", help="Execution working directory")
    p_init.add_argument("--goal", required=True, help="Optimization objective description")
    p_init.add_argument("--public-cmd", required=True, help="Public validation command")
    p_init.add_argument("--private-cmd", default=None, help="Held-out private evaluation command")
    p_init.add_argument("--direction", choices=["maximize", "minimize"], default="maximize")
    p_init.add_argument("--max-gap", type=float, default=0.15)
    p_init.add_argument("--plateau-window", type=int, default=4)

    # 2. next-step
    p_next = sub.add_parser("next-step", help="Get next AIDE² recommended operator & compact memory")
    p_next.add_argument("--id", required=True, help="Campaign ID")

    # 3. submit
    p_sub = sub.add_parser("submit", help="Submit candidate code, run SpecGuard + AST bloat check")
    p_sub.add_argument("--id", required=True, help="Campaign ID")
    p_sub.add_argument("--operator", required=True, choices=["DRAFT", "IMPROVE", "DEBUG", "FUSE", "PRUNE"])
    p_sub.add_argument("--hypothesis", required=True, help="Causal hypothesis being tested")
    p_sub.add_argument("--code-file", default=None, help="Optional file containing new candidate code")
    p_sub.add_argument("--parent-id", default=None)
    p_sub.add_argument("--secondary-parent-id", default=None)
    p_sub.add_argument("--steer-id", type=int, default=None)

    # 4. steer
    p_steer = sub.add_parser("steer", help="Inject a human/research idea for branch fusion")
    p_steer.add_argument("--id", required=True, help="Campaign ID")
    p_steer.add_argument("--idea", required=True, help="Steer idea description")
    p_steer.add_argument("--author", default="human")
    p_steer.add_argument("--target-node", default=None)

    # 5. status
    p_stat = sub.add_parser("status", help="Show AIDE² tree status, Pareto frontier, and champion")
    p_stat.add_argument("--id", required=True, help="Campaign ID")

    # 6. distill-kag
    p_kag = sub.add_parser("distill-kag", help="Distill Causal Hypothesis Log to KAG Markdown & triplets")
    p_kag.add_argument("--id", required=True, help="Campaign ID")
    p_kag.add_argument("--out", default=None, help="Optional Markdown file output path")

    # 7. specguard
    p_sg = sub.add_parser("specguard", help="Run standalone SpecBench two-tier evaluation & anti-cheat")
    p_sg.add_argument("--workdir", default=".")
    p_sg.add_argument("--public-cmd", required=True)
    p_sg.add_argument("--private-cmd", default=None)
    p_sg.add_argument("--candidate", default=None)
    p_sg.add_argument("--direction", choices=["maximize", "minimize"], default="maximize")
    p_sg.add_argument("--max-gap", type=float, default=0.15)

    # 8. prune-audit
    p_pr = sub.add_parser("prune-audit", help="Run AST dead-code and cyclomatic complexity audit")
    p_pr.add_argument("target", help="Python file to audit")

    # 9. skill-audit
    p_sk = sub.add_parser("skill-audit", help="Evaluate or compress SKILL.md via SkillForge")
    p_sk.add_argument("target", help="Skill directory or SKILL.md path")
    p_sk.add_argument("--all", action="store_true", help="Audit all skills in directory")
    p_sk.add_argument("--compress", action="store_true", help="Run AIDE² non-destructive prompt compression")

    args = parser.parse_args()
    engine = RSIEngine(db_path=Path(args.db))

    if args.cmd == "init-campaign":
        res = engine.init_campaign(
            campaign_id=args.id,
            name=args.name,
            target_file=args.target,
            workdir=args.workdir,
            goal=args.goal,
            public_eval_cmd=args.public_cmd,
            private_eval_cmd=args.private_cmd,
            direction=args.direction,
            max_hack_gap=args.max_gap,
            plateau_window=args.plateau_window,
        )
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif args.cmd == "next-step":
        res = engine.select_next_step(args.id)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif args.cmd == "submit":
        code_text = None
        if args.code_file:
            code_text = Path(args.code_file).read_text(encoding="utf-8")
        res = engine.submit_candidate(
            campaign_id=args.id,
            operator=args.operator,
            hypothesis=args.hypothesis,
            code_content=code_text,
            parent_id=args.parent_id,
            secondary_parent_id=args.secondary_parent_id,
            steer_idea_id=args.steer_id,
        )
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif args.cmd == "steer":
        res = engine.inject_steer_idea(
            campaign_id=args.id,
            idea_text=args.idea,
            author=args.author,
            target_node_id=args.target_node,
        )
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif args.cmd == "status":
        res = engine.get_tree_status(args.id)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif args.cmd == "distill-kag":
        out_path = Path(args.out).resolve() if args.out else None
        md = engine.export_kag_markdown(args.id, output_path=out_path)
        print(md)

    elif args.cmd == "specguard":
        verdict = evaluate_two_tier(
            cwd=Path(args.workdir).resolve(),
            public_cmd=args.public_cmd,
            private_cmd=args.private_cmd,
            candidate_file=Path(args.candidate).resolve() if args.candidate else None,
            direction=args.direction,
            max_hack_gap=args.max_gap,
        )
        print(json.dumps(verdict.to_dict(), ensure_ascii=False, indent=2))

    elif args.cmd == "prune-audit":
        rep = analyze_file_bloat(Path(args.target).resolve())
        print(json.dumps(rep.to_dict(), ensure_ascii=False, indent=2))

    elif args.cmd == "skill-audit":
        target = Path(args.target).resolve()
        if args.all and target.is_dir():
            reports = [
                evaluate_skill_dir(d).to_dict()
                for d in sorted(target.iterdir())
                if d.is_dir() and (d / "SKILL.md").exists()
            ]
            reports.sort(key=lambda r: r["composite_fitness"], reverse=True)
            print(json.dumps({"skills_count": len(reports), "reports": reports}, ensure_ascii=False, indent=2))
        else:
            rep = evaluate_skill_dir(target).to_dict()
            if args.compress:
                md_file = target / "SKILL.md" if target.is_dir() else target
                comp = compress_skill_markdown(md_file.read_text(encoding="utf-8"))
                rep["compression_result"] = comp
            print(json.dumps(rep, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
