#!/usr/bin/env python3
"""
RSI Evolution MCP Server (Model Context Protocol JSON-RPC 2.0 over stdio)
Exposes AIDE² Tree Search, SpecGuard Two-Tier Verifier, Evolution Bloat Pruner,
SkillForge, and KAG Causal Hypothesis Distillation as standard MCP tools.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

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

TOOLS_SPEC: list[dict[str, Any]] = [
    {
        "name": "rsi_init_campaign",
        "description": "Initialize an AIDE² code-space tree search campaign with SpecBench public & held-out private evaluation commands.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string"},
                "name": {"type": "string"},
                "target_file": {"type": "string"},
                "workdir": {"type": "string"},
                "goal": {"type": "string"},
                "public_eval_cmd": {"type": "string"},
                "private_eval_cmd": {"type": "string"},
                "direction": {"type": "string", "enum": ["maximize", "minimize"]},
                "max_hack_gap": {"type": "number"},
                "plateau_window": {"type": "integer"},
            },
            "required": ["campaign_id", "name", "target_file", "workdir", "goal", "public_eval_cmd"],
        },
    },
    {
        "name": "rsi_next_step",
        "description": "Get the next recommended AIDE² operator (DRAFT, IMPROVE, DEBUG, FUSE, PRUNE), plateau signal, and 16x compressed memory context.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string"},
            },
            "required": ["campaign_id"],
        },
    },
    {
        "name": "rsi_submit_candidate",
        "description": "Submit a candidate code modification to the AIDE² tree, run SpecGuard two-tier verification & AST bloat check, and log the causal hypothesis.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string"},
                "operator": {"type": "string", "enum": ["DRAFT", "IMPROVE", "DEBUG", "FUSE", "PRUNE"]},
                "hypothesis": {"type": "string"},
                "code_content": {"type": "string"},
                "parent_id": {"type": "string"},
                "secondary_parent_id": {"type": "string"},
                "steer_idea_id": {"type": "integer"},
            },
            "required": ["campaign_id", "operator", "hypothesis"],
        },
    },
    {
        "name": "rsi_inject_steer",
        "description": "Inject a human or external research idea into the AIDE² tree search for branch fusion (Aiden steerable auto-research pattern).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string"},
                "idea_text": {"type": "string"},
                "author": {"type": "string"},
                "target_node_id": {"type": "string"},
            },
            "required": ["campaign_id", "idea_text"],
        },
    },
    {
        "name": "rsi_tree_status",
        "description": "Retrieve full AIDE² tree status, champion node, Pareto frontier, and Causal Hypothesis Log.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string"},
            },
            "required": ["campaign_id"],
        },
    },
    {
        "name": "specguard_verify",
        "description": "Run SpecBench two-tier (Public vs Held-Out Private) verification and static AST anti-cheat scan on any project target.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workdir": {"type": "string"},
                "public_cmd": {"type": "string"},
                "private_cmd": {"type": "string"},
                "candidate_file": {"type": "string"},
                "direction": {"type": "string", "enum": ["maximize", "minimize"]},
                "max_hack_gap": {"type": "number"},
            },
            "required": ["workdir", "public_cmd"],
        },
    },
    {
        "name": "pruner_analyze_bloat",
        "description": "Run AIDE² Evolution Bloat Pruner AST analysis to detect dead functions, unused imports, and high cyclomatic complexity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "skillforge_evaluate",
        "description": "Evaluate an agent skill directory (SKILL.md + scripts/) on AIDE² compression density, determinism, and OpenSkill virtual verifier anchors.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "skill_path": {"type": "string"},
                "compress": {"type": "boolean"},
            },
            "required": ["skill_path"],
        },
    },
    {
        "name": "kag_distill_hypotheses",
        "description": "Export a campaign's Causal Hypothesis Log and semantic KAG triplets to Markdown.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string"},
                "output_path": {"type": "string"},
            },
            "required": ["campaign_id"],
        },
    },
]


class RSIMCPServer:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.engine = RSIEngine(db_path=db_path)

    def handle_tool_call(self, name: str, arguments: dict[str, Any]) -> Any:
        if name == "rsi_init_campaign":
            return self.engine.init_campaign(
                campaign_id=arguments["campaign_id"],
                name=arguments["name"],
                target_file=arguments["target_file"],
                workdir=arguments["workdir"],
                goal=arguments["goal"],
                public_eval_cmd=arguments["public_eval_cmd"],
                private_eval_cmd=arguments.get("private_eval_cmd"),
                direction=arguments.get("direction", "maximize"),
                max_hack_gap=float(arguments.get("max_hack_gap", 0.15)),
                plateau_window=int(arguments.get("plateau_window", 4)),
            )
        elif name == "rsi_next_step":
            return self.engine.select_next_step(arguments["campaign_id"])
        elif name == "rsi_submit_candidate":
            return self.engine.submit_candidate(
                campaign_id=arguments["campaign_id"],
                operator=arguments["operator"],
                hypothesis=arguments["hypothesis"],
                code_content=arguments.get("code_content"),
                parent_id=arguments.get("parent_id"),
                secondary_parent_id=arguments.get("secondary_parent_id"),
                steer_idea_id=arguments.get("steer_idea_id"),
            )
        elif name == "rsi_inject_steer":
            return self.engine.inject_steer_idea(
                campaign_id=arguments["campaign_id"],
                idea_text=arguments["idea_text"],
                author=arguments.get("author", "human"),
                target_node_id=arguments.get("target_node_id"),
            )
        elif name == "rsi_tree_status":
            return self.engine.get_tree_status(arguments["campaign_id"])
        elif name == "specguard_verify":
            cand = arguments.get("candidate_file")
            res = evaluate_two_tier(
                cwd=Path(arguments["workdir"]).resolve(),
                public_cmd=arguments["public_cmd"],
                private_cmd=arguments.get("private_cmd"),
                candidate_file=Path(cand).resolve() if cand else None,
                direction=arguments.get("direction", "maximize"),
                max_hack_gap=float(arguments.get("max_hack_gap", 0.15)),
            )
            return res.to_dict()
        elif name == "pruner_analyze_bloat":
            rep = analyze_file_bloat(Path(arguments["file_path"]).resolve())
            return rep.to_dict()
        elif name == "skillforge_evaluate":
            sp = Path(arguments["skill_path"]).resolve()
            eval_rep = evaluate_skill_dir(sp).to_dict()
            if arguments.get("compress"):
                md_file = sp / "SKILL.md" if sp.is_dir() else sp
                comp = compress_skill_markdown(md_file.read_text(encoding="utf-8"))
                eval_rep["compression_preview"] = {
                    "original_bytes": comp["original_bytes"],
                    "compressed_bytes": comp["compressed_bytes"],
                    "compression_ratio": comp["compression_ratio"],
                }
            return eval_rep
        elif name == "kag_distill_hypotheses":
            out = arguments.get("output_path")
            md = self.engine.export_kag_markdown(
                arguments["campaign_id"],
                output_path=Path(out).resolve() if out else None,
            )
            return {"campaign_id": arguments["campaign_id"], "markdown": md}
        else:
            raise ValueError(f"Unknown MCP tool: {name}")

    def handle_jsonrpc(self, request: dict[str, Any]) -> dict[str, Any] | None:
        method = request.get("method", "")
        req_id = request.get("id")
        params = request.get("params") or {}

        if method == "notifications/initialized":
            return None

        try:
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "weco-aide2-rsi-mcp",
                        "version": "2.1.0",
                    },
                }
            elif method == "tools/list":
                result = {"tools": TOOLS_SPEC}
            elif method == "tools/call":
                tool_name = params.get("name", "")
                tool_args = params.get("arguments") or {}
                payload = self.handle_tool_call(tool_name, tool_args)
                result = {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(payload, ensure_ascii=False, indent=2),
                        }
                    ],
                    "isError": False,
                }
            elif method == "ping":
                result = {}
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }

            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(exc)},
            }

    def serve_stdio(self) -> None:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except json.JSONDecodeError:
                continue
            resp = self.handle_jsonrpc(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    server = RSIMCPServer()
    server.serve_stdio()
