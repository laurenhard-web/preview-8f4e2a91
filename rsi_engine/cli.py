#!/usr/bin/env python3
"""
Unified CLI v9.0 for the RSI-0 Meta-Evolution Engine
(AIDE² + SpecBench + EvoSkill + HyperAgents + DomainSpheres + DonorVault + ConfigFlags + OpenAPI 3.1)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from rsi_engine.bloat_pruner import analyze_file_bloat
    from rsi_engine.config_flag_manager import ConfigAndFlagManager
    from rsi_engine.core import DEFAULT_DB_PATH, RSIEngine
    from rsi_engine.domain_library_router import DomainKnowledgeLibrary
    from rsi_engine.donor_harvester_vault import DonorHarvesterVault
    from rsi_engine.openapi_doc_generator import OpenAPISpecAndDocsGenerator
    from rsi_engine.self_evolution_teamwork import SelfEvolutionTeamworkOrchestrator
    from rsi_engine.skill_forge import compress_skill_markdown, evaluate_skill_dir
    from rsi_engine.specguard import evaluate_two_tier
else:
    from .bloat_pruner import analyze_file_bloat
    from .config_flag_manager import ConfigAndFlagManager
    from .core import DEFAULT_DB_PATH, RSIEngine
    from .domain_library_router import DomainKnowledgeLibrary
    from .donor_harvester_vault import DonorHarvesterVault
    from .openapi_doc_generator import OpenAPISpecAndDocsGenerator
    from .self_evolution_teamwork import SelfEvolutionTeamworkOrchestrator
    from .skill_forge import compress_skill_markdown, evaluate_skill_dir
    from .specguard import evaluate_two_tier


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RSI-0 v9 Meta-Evolution CLI (AIDE² + DomainSpheres + DonorVault + FeatureFlags + OpenAPI 3.1)"
    )
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="Path to unified SQLite database")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # 1. init-campaign
    p_init = sub.add_parser("init-campaign", help="Initialize an AIDE² tree search campaign")
    p_init.add_argument("--id", required=True)
    p_init.add_argument("--name", required=True)
    p_init.add_argument("--target", required=True)
    p_init.add_argument("--workdir", default=".")
    p_init.add_argument("--goal", required=True)
    p_init.add_argument("--public-cmd", required=True)
    p_init.add_argument("--private-cmd", default=None)
    p_init.add_argument("--direction", choices=["maximize", "minimize"], default="maximize")
    p_init.add_argument("--max-gap", type=float, default=0.15)
    p_init.add_argument("--plateau-window", type=int, default=4)

    # 2. next-step
    p_next = sub.add_parser("next-step", help="Get next AIDE² recommended operator & compact memory")
    p_next.add_argument("--id", required=True)

    # 3. submit
    p_sub = sub.add_parser("submit", help="Submit candidate code, run SpecGuard + AST bloat check")
    p_sub.add_argument("--id", required=True)
    p_sub.add_argument("--operator", required=True, choices=["DRAFT", "IMPROVE", "DEBUG", "FUSE", "PRUNE"])
    p_sub.add_argument("--hypothesis", required=True)
    p_sub.add_argument("--code-file", default=None)
    p_sub.add_argument("--parent-id", default=None)
    p_sub.add_argument("--secondary-parent-id", default=None)
    p_sub.add_argument("--steer-id", type=int, default=None)

    # 4. steer
    p_steer = sub.add_parser("steer", help="Inject a human/research idea for branch fusion")
    p_steer.add_argument("--id", required=True)
    p_steer.add_argument("--idea", required=True)
    p_steer.add_argument("--author", default="human")
    p_steer.add_argument("--target-node", default=None)

    # 5. status
    p_stat = sub.add_parser("status", help="Show AIDE² tree status, Pareto frontier, and champion")
    p_stat.add_argument("--id", required=True)

    # 6. distill-kag
    p_kag = sub.add_parser("distill-kag", help="Distill Causal Hypothesis Log to KAG Markdown & triplets")
    p_kag.add_argument("--id", required=True)
    p_kag.add_argument("--out", default=None)

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
    p_pr.add_argument("target")

    # 9. skill-audit
    p_sk = sub.add_parser("skill-audit", help="Evaluate or compress SKILL.md via SkillForge")
    p_sk.add_argument("target")
    p_sk.add_argument("--all", action="store_true")
    p_sk.add_argument("--compress", action="store_true")

    # 10. spheres (NEW v9)
    p_sph = sub.add_parser("spheres", help="List or route extensible Domain Knowledge Spheres")
    p_sph.add_argument("--query", default=None, help="Project prompt to route via Dual-Axis Selection Contour")
    p_sph.add_argument("--aesthetic", default="iconic_design_aesthetics_ferrari_pininfarina")

    # 11. delegate-sphere (NEW v9)
    p_del = sub.add_parser("delegate-sphere", help="Chief Architect: commission subagents to build a new sphere")
    p_del.add_argument("--sphere-id", required=True)
    p_del.add_argument("--title", required=True)
    p_del.add_argument("--rationale", required=True)

    # 12. donors (NEW v9)
    p_dnr = sub.add_parser("donors", help="Sync or list canonical Donor Blueprints in storage/donors_vault/")
    p_dnr.add_argument("--sphere-id", default=None)
    p_dnr.add_argument("--harvest-url", default=None)
    p_dnr.add_argument("--donor-id", default=None)
    p_dnr.add_argument("--title", default=None)

    # 13. flags (NEW v9)
    p_flg = sub.add_parser("flags", help="Inspect or toggle Feature Flags and Linear sync_op_log")
    p_flg.add_argument("--set", dest="set_flag", default=None, help="Flag key to toggle")
    p_flg.add_argument("--enable", action="store_true")
    p_flg.add_argument("--disable", action="store_true")
    p_flg.add_argument("--snapshot-epoch", type=int, default=None)

    # 14. openapi (NEW v9)
    sub.add_parser("openapi", help="Generate live OpenAPI 3.1.0 specification from SQLite & routes")

    # 15. self-evolve-20 (NEW v9)
    sub.add_parser("self-evolve-20", help="Run the 20-Epoch Multi-Department Teamwork Self-Evolution Campaign")

    args = parser.parse_args()
    db_path = Path(args.db)

    if args.cmd == "spheres":
        lib = DomainKnowledgeLibrary(db_path=db_path)
        lib.sync_seed_spheres()
        if args.query:
            print(json.dumps(lib.route_project_contour(args.query, args.aesthetic), ensure_ascii=False, indent=2))
        else:
            print(json.dumps(lib.list_spheres(), ensure_ascii=False, indent=2))
        return

    if args.cmd == "delegate-sphere":
        lib = DomainKnowledgeLibrary(db_path=db_path)
        res = lib.delegate_new_sphere_creation(
            sphere_id=args.sphere_id,
            title=args.title,
            category="custom_delegated_sphere",
            rationale=args.rationale,
            seed_queries=[args.title, args.rationale],
        )
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    if args.cmd == "donors":
        vault = DonorHarvesterVault(db_path=db_path)
        vault.sync_canonical_donors()
        if args.harvest_url and args.donor_id and args.title:
            res = vault.harvest_donor_from_url(
                donor_id=args.donor_id,
                sphere_id=args.sphere_id or "core_api_and_platform_architecture",
                title=args.title,
                url=args.harvest_url,
            )
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(vault.list_donors(args.sphere_id), ensure_ascii=False, indent=2))
        return

    if args.cmd == "flags":
        mgr = ConfigAndFlagManager(rsi_db_path=db_path)
        mgr.sync_flags_from_config()
        if args.set_flag:
            val = True if args.enable else (False if args.disable else True)
            print(json.dumps(mgr.set_flag(args.set_flag, val), ensure_ascii=False, indent=2))
        elif args.snapshot_epoch is not None:
            print(json.dumps(mgr.create_epoch_snapshot(args.snapshot_epoch), ensure_ascii=False, indent=2))
        else:
            print(json.dumps(mgr.get_full_diagnostics(), ensure_ascii=False, indent=2))
        return

    if args.cmd == "openapi":
        gen = OpenAPISpecAndDocsGenerator(rsi_db_path=db_path)
        print(json.dumps(gen.build_openapi_31_spec(), ensure_ascii=False, indent=2))
        return

    if args.cmd == "self-evolve-20":
        team = SelfEvolutionTeamworkOrchestrator(db_path=db_path)
        print(json.dumps(team.run_20_epochs_teamwork(), ensure_ascii=False, indent=2))
        return

    engine = RSIEngine(db_path=db_path)
    if args.cmd == "init-campaign":
        res = engine.init_campaign(
            campaign_id=args.id, name=args.name, target_file=args.target, workdir=args.workdir,
            goal=args.goal, public_eval_cmd=args.public_cmd, private_eval_cmd=args.private_cmd,
            direction=args.direction, max_hack_gap=args.max_gap, plateau_window=args.plateau_window,
        )
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.cmd == "next-step":
        print(json.dumps(engine.select_next_step(args.id), ensure_ascii=False, indent=2))
    elif args.cmd == "submit":
        code_text = Path(args.code_file).read_text(encoding="utf-8") if args.code_file else None
        res = engine.submit_candidate(
            campaign_id=args.id, operator=args.operator, hypothesis=args.hypothesis,
            code_content=code_text, parent_id=args.parent_id,
            secondary_parent_id=args.secondary_parent_id, steer_idea_id=args.steer_id,
        )
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.cmd == "steer":
        print(json.dumps(engine.inject_steer_idea(args.id, args.idea, args.author, args.target_node), ensure_ascii=False, indent=2))
    elif args.cmd == "status":
        print(json.dumps(engine.get_tree_status(args.id), ensure_ascii=False, indent=2))
    elif args.cmd == "distill-kag":
        out_path = Path(args.out).resolve() if args.out else None
        print(engine.export_kag_markdown(args.id, output_path=out_path))
    elif args.cmd == "specguard":
        verdict = evaluate_two_tier(
            cwd=Path(args.workdir).resolve(), public_cmd=args.public_cmd, private_cmd=args.private_cmd,
            candidate_file=Path(args.candidate).resolve() if args.candidate else None,
            direction=args.direction, max_hack_gap=args.max_gap,
        )
        print(json.dumps(verdict.to_dict(), ensure_ascii=False, indent=2))
    elif args.cmd == "prune-audit":
        print(json.dumps(analyze_file_bloat(Path(args.target).resolve()).to_dict(), ensure_ascii=False, indent=2))
    elif args.cmd == "skill-audit":
        target = Path(args.target).resolve()
        if args.all and target.is_dir():
            reports = [evaluate_skill_dir(d).to_dict() for d in sorted(target.iterdir()) if d.is_dir() and (d / "SKILL.md").exists()]
            reports.sort(key=lambda r: r["composite_fitness"], reverse=True)
            print(json.dumps({"skills_count": len(reports), "reports": reports}, ensure_ascii=False, indent=2))
        else:
            rep = evaluate_skill_dir(target).to_dict()
            if args.compress:
                md_file = target / "SKILL.md" if target.is_dir() else target
                rep["compression_result"] = compress_skill_markdown(md_file.read_text(encoding="utf-8"))
            print(json.dumps(rep, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
