#!/usr/bin/env python3
"""
AIDE² Core: Steerable Code-Space Tree Search & Causal Hypothesis Engine
Inspired by:
- Zhengyao Jiang et al., Weco AI:
  * AIDE: AI-Driven Exploration in the Space of Code (arXiv:2502.13138)
  * AIDE²: The First Evidence of Recursive Self-Improvement (arXiv:2609.26457)
  * SpecBench: Measuring Reward Hacking in Long-Horizon Coding Agents (arXiv:2605.21384)
  * Aiden: Steerable Auto-Research & Branch Fusion
- Meta AI HyperAgents (arXiv:2603.19461):
  * Causal Hypothesis Log & Metacognitive Memory
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sqlite3
from pathlib import Path
import sys
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from rsi_engine.bloat_pruner import analyze_code_bloat
    from rsi_engine.knowledge_accumulator import CumulativeKnowledgeEngine
    from rsi_engine.specguard import evaluate_two_tier
else:
    from .bloat_pruner import analyze_code_bloat
    from .knowledge_accumulator import CumulativeKnowledgeEngine
    from .specguard import evaluate_two_tier

DEFAULT_DB_PATH = Path.home() / ".gemini" / "orchestrator" / "rsi_evolution.db"


SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    target_file TEXT NOT NULL,
    workdir TEXT NOT NULL,
    goal TEXT NOT NULL,
    direction TEXT NOT NULL DEFAULT 'maximize',
    public_eval_cmd TEXT NOT NULL,
    private_eval_cmd TEXT,
    max_hack_gap REAL NOT NULL DEFAULT 0.15,
    plateau_window INTEGER NOT NULL DEFAULT 4,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS nodes (
    node_id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL REFERENCES campaigns(campaign_id),
    parent_id TEXT,
    secondary_parent_id TEXT,
    step_num INTEGER NOT NULL,
    operator TEXT NOT NULL, -- 'DRAFT' | 'DEBUG' | 'IMPROVE' | 'FUSE' | 'PRUNE'
    hypothesis TEXT NOT NULL,
    code_content TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    public_score REAL,
    private_score REAL,
    reward_hack_gap REAL NOT NULL DEFAULT 0.0,
    is_reward_hacking INTEGER NOT NULL DEFAULT 0,
    verdict TEXT NOT NULL, -- 'ACCEPTED' | 'REWARD_HACK_BLOCKED' | 'CRASHED'
    verdict_reason TEXT NOT NULL DEFAULT '',
    exec_time_ms REAL NOT NULL DEFAULT 0.0,
    code_loc INTEGER NOT NULL DEFAULT 0,
    cyclomatic_complexity INTEGER NOT NULL DEFAULT 0,
    dead_func_count INTEGER NOT NULL DEFAULT 0,
    bloat_index REAL NOT NULL DEFAULT 0.0,
    guarded_output TEXT NOT NULL DEFAULT '',
    one_liner_summary TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS causal_hypotheses (
    hypothesis_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id TEXT NOT NULL REFERENCES campaigns(campaign_id),
    node_id TEXT NOT NULL REFERENCES nodes(node_id),
    operator TEXT NOT NULL,
    hypothesis TEXT NOT NULL,
    outcome TEXT NOT NULL, -- 'BREAKTHROUGH' | 'INCREMENTAL' | 'NO_GAIN' | 'REFUTED_CRASH' | 'REWARD_HACK_BLOCKED' | 'PRUNED_LEAN'
    score_delta REAL NOT NULL DEFAULT 0.0,
    lesson_learned TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS steer_ideas (
    idea_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id TEXT NOT NULL REFERENCES campaigns(campaign_id),
    idea_text TEXT NOT NULL,
    author TEXT NOT NULL DEFAULT 'human',
    target_node_id TEXT,
    consumed_by_node_id TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING', -- 'PENDING' | 'FUSED'
    created_at TEXT NOT NULL
);
"""


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RSIEngine:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA_SQL)

    def init_campaign(
        self,
        campaign_id: str,
        name: str,
        target_file: str,
        workdir: str,
        goal: str,
        public_eval_cmd: str,
        private_eval_cmd: str | None = None,
        direction: str = "maximize",
        max_hack_gap: float = 0.15,
        plateau_window: int = 4,
    ) -> dict[str, Any]:
        """Creates or resets an AIDE² code-space search campaign."""
        now = _utc_now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO campaigns (
                    campaign_id, name, target_file, workdir, goal, direction,
                    public_eval_cmd, private_eval_cmd, max_hack_gap, plateau_window,
                    status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
                """,
                (
                    campaign_id,
                    name,
                    str(Path(target_file).resolve()),
                    str(Path(workdir).resolve()),
                    goal,
                    direction,
                    public_eval_cmd,
                    private_eval_cmd,
                    max_hack_gap,
                    plateau_window,
                    now,
                ),
            )
        return self.get_campaign(campaign_id)

    def get_campaign(self, campaign_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM campaigns WHERE campaign_id = ?", (campaign_id,)
            ).fetchone()
            if not row:
                raise ValueError(f"Campaign '{campaign_id}' not found.")
            return dict(row)

    def inject_steer_idea(
        self,
        campaign_id: str,
        idea_text: str,
        author: str = "human",
        target_node_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Aiden Steerable Auto-Research pattern:
        Queues a human or external research idea to be fused with the tree's best branch.
        """
        now = _utc_now()
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO steer_ideas (campaign_id, idea_text, author, target_node_id, status, created_at)
                VALUES (?, ?, ?, ?, 'PENDING', ?)
                """,
                (campaign_id, idea_text, author, target_node_id, now),
            )
            idea_id = cur.lastrowid
        return {
            "idea_id": idea_id,
            "campaign_id": campaign_id,
            "idea_text": idea_text,
            "author": author,
            "status": "PENDING",
            "created_at": now,
        }

    def _is_better(self, score_a: float, score_b: float, direction: str) -> bool:
        return (score_a > score_b) if direction == "maximize" else (score_a < score_b)

    def select_next_step(self, campaign_id: str) -> dict[str, Any]:
        """
        AIDE² Meta-Search Policy & Context Compactor (16x prompt reduction):
        - Instead of feeding full transcripts of all previous attempts, builds the AIDE²
          compact memory window: Newest-12 one-liner summaries + 1 full best solution.
        - Calculates the 4-step Plateau Signal and Bug Rate (>15% threshold).
        - Chooses the optimal operator:
          1. `DRAFT` if tree is empty or <2 initial drafts exist.
          2. `FUSE` if a human steer idea is pending in `steer_ideas`.
          3. `DEBUG` if the most recent promising draft crashed and bug rate allows recovery.
          4. `PRUNE` if the best node has `bloat_index >= 0.25` or dead functions > 0.
          5. `DRAFT` (orthogonal exploration) if the Plateau Signal fires (no gain in last W steps).
          6. `IMPROVE` (focused hill-climbing on the best node) otherwise.
        """
        camp = self.get_campaign(campaign_id)
        direction = camp["direction"]
        window = int(camp["plateau_window"])

        with self._connect() as conn:
            nodes = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM nodes WHERE campaign_id = ? ORDER BY step_num ASC",
                    (campaign_id,),
                ).fetchall()
            ]
            pending_steers = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM steer_ideas WHERE campaign_id = ? AND status = 'PENDING' ORDER BY idea_id ASC",
                    (campaign_id,),
                ).fetchall()
            ]
            refuted = [
                dict(r)
                for r in conn.execute(
                    """
                    SELECT hypothesis, outcome, lesson_learned FROM causal_hypotheses
                    WHERE campaign_id = ? AND outcome IN ('REFUTED_CRASH', 'REWARD_HACK_BLOCKED', 'NO_GAIN')
                    ORDER BY hypothesis_id DESC LIMIT 8
                    """,
                    (campaign_id,),
                ).fetchall()
            ]

        total_steps = len(nodes)
        accepted_nodes = [
            n for n in nodes if n["verdict"] == "ACCEPTED" and n["public_score"] is not None
        ]

        if accepted_nodes:
            best_node = sorted(
                accepted_nodes,
                key=lambda n: (
                    n["public_score"] if direction == "maximize" else -n["public_score"],
                    -n["code_loc"],
                    -n["exec_time_ms"],
                ),
                reverse=True,
            )[0]
        else:
            best_node = None

        # Calculate recent bug/crash rate
        recent_slice = nodes[-min(len(nodes), 8) :] if nodes else []
        bug_rate = (
            round(
                sum(1 for n in recent_slice if n["verdict"] != "ACCEPTED") / len(recent_slice),
                3,
            )
            if recent_slice
            else 0.0
        )

        # Calculate AIDE² Plateau Signal over last `window` steps
        plateau_detected = False
        if len(nodes) >= window and best_node is not None:
            last_w_ids = {n["node_id"] for n in nodes[-window:]}
            # If the best node was found strictly before the last `window` steps, we are on a plateau
            if best_node["node_id"] not in last_w_ids:
                plateau_detected = True

        # AIDE² 16x Compact Context: newest 12 one-liners + 1 full best solution
        newest_12_one_liners = [
            n["one_liner_summary"] for n in nodes[-12:] if n.get("one_liner_summary")
        ]

        # Decide operator
        operator = "DRAFT"
        parent_id = best_node["node_id"] if best_node else None
        secondary_parent_id = None
        steer_to_consume = None
        rationale = ""

        if total_steps == 0 or not best_node:
            operator = "DRAFT"
            parent_id = None
            rationale = "Tree has no valid baseline node yet; initialize root DRAFT."
        elif pending_steers:
            operator = "FUSE"
            steer_to_consume = pending_steers[0]
            parent_id = steer_to_consume.get("target_node_id") or best_node["node_id"]
            # Pick second-best distinct accepted node as secondary parent if available
            other_accepted = [n for n in accepted_nodes if n["node_id"] != parent_id]
            if other_accepted:
                secondary_parent_id = other_accepted[-1]["node_id"]
            rationale = (
                f"Human/External Steer Idea #{steer_to_consume['idea_id']} queued: "
                f"FUSE idea '{steer_to_consume['idea_text']}' into best branch {parent_id}."
            )
        elif best_node["dead_func_count"] > 0 or best_node["bloat_index"] >= 0.25:
            operator = "PRUNE"
            parent_id = best_node["node_id"]
            rationale = (
                f"Best node {parent_id} accumulated bloat (bloat_index={best_node['bloat_index']}, "
                f"dead_funcs={best_node['dead_func_count']}). Schedule metric-preserving PRUNE."
            )
        elif plateau_detected:
            operator = "DRAFT"
            parent_id = best_node["node_id"]
            rationale = (
                f"AIDE² Plateau Signal fired (no improvement in last {window} steps). "
                "Switching from local hill-climbing to orthogonal structural DRAFT."
            )
        elif nodes[-1]["verdict"] == "CRASHED" and bug_rate > 0.15:
            operator = "DEBUG"
            parent_id = nodes[-1]["node_id"]
            rationale = (
                f"Recent bug rate is {bug_rate * 100:.1f}% (>15% AIDE² threshold) and last node "
                f"{parent_id} crashed. Invoking targeted DEBUG with raw tail traceback."
            )
        else:
            operator = "IMPROVE"
            parent_id = best_node["node_id"]
            rationale = f"Climbing promising branch from best node {parent_id} (public_score={best_node['public_score']})."

        cum_engine = CumulativeKnowledgeEngine(self.db_path)
        cum_ctx = cum_engine.get_cumulative_context_for_next_epoch(campaign_id, camp["target_file"])

        return {
            "campaign_id": campaign_id,
            "next_step_num": total_steps,
            "recommended_operator": operator,
            "parent_node_id": parent_id,
            "secondary_parent_id": secondary_parent_id,
            "rationale": rationale,
            "plateau_signal": plateau_detected,
            "recent_bug_rate": bug_rate,
            "include_debug_component": bug_rate > 0.15,
            "pending_steer_idea": steer_to_consume,
            "cumulative_knowledge_context": cum_ctx,
            "aide2_compact_memory": {
                "newest_12_one_liners": newest_12_one_liners,
                "best_node_id": best_node["node_id"] if best_node else None,
                "best_public_score": best_node["public_score"] if best_node else None,
                "best_code_loc": best_node["code_loc"] if best_node else None,
                "best_full_solution": best_node["code_content"] if best_node else None,
                "refuted_hypotheses_do_not_repeat": refuted,
            },
        }

    def submit_candidate(
        self,
        campaign_id: str,
        operator: str,
        hypothesis: str,
        code_content: str | None = None,
        parent_id: str | None = None,
        secondary_parent_id: str | None = None,
        steer_idea_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Writes candidate code to target_file (if provided), runs SpecGuard Two-Tier Evaluation,
        analyzes AST bloat, records the node in the AIDE² tree, and logs a Causal Hypothesis.
         Automatically restores the best working code to target_file if the candidate crashes
        or gets blocked for reward hacking!
        """
        camp = self.get_campaign(campaign_id)
        target_path = Path(camp["target_file"])
        workdir = Path(camp["workdir"])
        direction = camp["direction"]

        # Read or write candidate code
        if code_content is not None:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(code_content, encoding="utf-8")
        else:
            code_content = target_path.read_text(encoding="utf-8")

        code_hash = hashlib.sha256(code_content.encode("utf-8")).hexdigest()[:12]

        # Analyze current best before evaluating candidate
        with self._connect() as conn:
            step_row = conn.execute(
                "SELECT COALESCE(MAX(step_num) + 1, 0) AS next_step FROM nodes WHERE campaign_id = ?",
                (campaign_id,),
            ).fetchone()
            step_num = int(step_row["next_step"]) if step_row else 0

            accepted = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM nodes WHERE campaign_id = ? AND verdict = 'ACCEPTED' AND public_score IS NOT NULL",
                    (campaign_id,),
                ).fetchall()
            ]

        prev_best = None
        if accepted:
            prev_best = sorted(
                accepted,
                key=lambda n: (
                    n["public_score"] if direction == "maximize" else -n["public_score"],
                    -n["code_loc"],
                ),
                reverse=True,
            )[0]

        base_node_id = f"node_{step_num:03d}_{operator.lower()}"
        with self._connect() as conn:
            exists = conn.execute("SELECT 1 FROM nodes WHERE node_id = ?", (base_node_id,)).fetchone()
        node_id = f"{campaign_id}_{base_node_id}" if exists else base_node_id

        # 1. Run SpecGuard Two-Tier Verification
        verdict_obj = evaluate_two_tier(
            cwd=workdir,
            public_cmd=camp["public_eval_cmd"],
            private_cmd=camp.get("private_eval_cmd"),
            candidate_file=target_path,
            direction=direction,
            max_hack_gap=float(camp["max_hack_gap"]),
        )

        # 2. Run AST Bloat Pruner Analysis
        bloat_rep = analyze_code_bloat(code_content, file_path=str(target_path))

        pub_score = verdict_obj.public_result.score
        priv_score = verdict_obj.private_result.score if verdict_obj.private_result else pub_score
        exec_ms = verdict_obj.public_result.duration_ms + (
            verdict_obj.private_result.duration_ms if verdict_obj.private_result else 0.0
        )

        # 3. Determine Causal Hypothesis Outcome & Score Delta
        prev_best_score = prev_best["public_score"] if prev_best else None
        score_delta = 0.0
        if pub_score is not None and prev_best_score is not None:
            score_delta = round(
                (pub_score - prev_best_score)
                if direction == "maximize"
                else (prev_best_score - pub_score),
                4,
            )

        if verdict_obj.verdict == "REWARD_HACK_BLOCKED":
            outcome = "REWARD_HACK_BLOCKED"
            lesson = (
                f"BLOCKED FOR REWARD HACKING: '{hypothesis}' achieved public={pub_score} "
                f"but private={priv_score} (gap={verdict_obj.reward_hack_gap}). {verdict_obj.reason}"
            )
        elif verdict_obj.verdict == "CRASHED":
            outcome = "REFUTED_CRASH"
            lesson = f"CRASHED: '{hypothesis}' failed execution ({verdict_obj.reason})."
        elif operator.upper() == "PRUNE" and prev_best is not None and score_delta >= -1e-6:
            loc_saved = prev_best["code_loc"] - bloat_rep.code_loc
            outcome = "PRUNED_LEAN"
            lesson = (
                f"METRIC-PRESERVING PRUNE: Reduced code by {loc_saved} LOC "
                f"(bloat_index={bloat_rep.bloat_index}) while holding score={pub_score}."
            )
        elif prev_best_score is None or score_delta > 0.03:
            outcome = "BREAKTHROUGH"
            lesson = (
                f"BREAKTHROUGH (+{score_delta:.4f}): '{hypothesis}' lifted public score to "
                f"{pub_score} (private={priv_score}, LOC={bloat_rep.code_loc})."
            )
        elif score_delta > 0.0:
            outcome = "INCREMENTAL"
            lesson = (
                f"INCREMENTAL (+{score_delta:.4f}): '{hypothesis}' improved public score to "
                f"{pub_score} (private={priv_score})."
            )
        else:
            outcome = "NO_GAIN"
            lesson = (
                f"NO GAIN (delta={score_delta:.4f}): '{hypothesis}' scored {pub_score} "
                f"vs best {prev_best_score}."
            )

        one_liner = (
            f"[Step {step_num} | {operator.upper()} | {verdict_obj.verdict}] "
            f"pub={pub_score} priv={priv_score} gap={verdict_obj.reward_hack_gap} "
            f"LOC={bloat_rep.code_loc} CC={bloat_rep.total_cyclomatic_complexity} :: {hypothesis[:90]}"
        )

        now = _utc_now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO nodes (
                    node_id, campaign_id, parent_id, secondary_parent_id, step_num,
                    operator, hypothesis, code_content, code_hash, public_score,
                    private_score, reward_hack_gap, is_reward_hacking, verdict,
                    verdict_reason, exec_time_ms, code_loc, cyclomatic_complexity,
                    dead_func_count, bloat_index, guarded_output, one_liner_summary,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node_id,
                    campaign_id,
                    parent_id,
                    secondary_parent_id,
                    step_num,
                    operator.upper(),
                    hypothesis,
                    code_content,
                    code_hash,
                    pub_score,
                    priv_score,
                    verdict_obj.reward_hack_gap,
                    1 if verdict_obj.is_reward_hacking else 0,
                    verdict_obj.verdict,
                    verdict_obj.reason,
                    round(exec_ms, 2),
                    bloat_rep.code_loc,
                    bloat_rep.total_cyclomatic_complexity,
                    len(bloat_rep.dead_functions),
                    bloat_rep.bloat_index,
                    verdict_obj.public_result.guarded_output,
                    one_liner,
                    now,
                ),
            )
            conn.execute(
                """
                INSERT INTO causal_hypotheses (
                    campaign_id, node_id, operator, hypothesis, outcome,
                    score_delta, lesson_learned, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    campaign_id,
                    node_id,
                    operator.upper(),
                    hypothesis,
                    outcome,
                    score_delta,
                    lesson,
                    now,
                ),
            )
            if steer_idea_id is not None:
                conn.execute(
                    "UPDATE steer_ideas SET status = 'FUSED', consumed_by_node_id = ? WHERE idea_id = ?",
                    (node_id, steer_idea_id),
                )

        # Rollback target_file to best working node if candidate failed or did not beat prev_best
        restored_to_best = False
        if prev_best is not None:
            is_new_champ = (
                verdict_obj.verdict == "ACCEPTED"
                and pub_score is not None
                and (
                    score_delta > 0
                    or (score_delta >= -1e-6 and bloat_rep.code_loc < prev_best["code_loc"])
                )
            )
            if not is_new_champ:
                target_path.write_text(prev_best["code_content"], encoding="utf-8")
                restored_to_best = True

        cum_engine = CumulativeKnowledgeEngine(self.db_path)
        knowledge_snapshot = cum_engine.record_epoch_knowledge(
            campaign_id=campaign_id,
            epoch_num=step_num,
            node_id=node_id,
            target_file=target_path,
            hypothesis=hypothesis,
            outcome=outcome,
        )

        return {
            "node_id": node_id,
            "step_num": step_num,
            "operator": operator.upper(),
            "verdict": verdict_obj.verdict,
            "verdict_reason": verdict_obj.reason,
            "outcome": outcome,
            "public_score": pub_score,
            "private_score": priv_score,
            "reward_hack_gap": verdict_obj.reward_hack_gap,
            "score_delta_vs_best": score_delta,
            "bloat_metrics": {
                "code_loc": bloat_rep.code_loc,
                "cyclomatic_complexity": bloat_rep.total_cyclomatic_complexity,
                "dead_functions": bloat_rep.dead_functions,
                "bloat_index": bloat_rep.bloat_index,
            },
            "cumulative_knowledge": knowledge_snapshot,
            "lesson_learned": lesson,
            "one_liner_summary": one_liner,
            "restored_previous_champion": restored_to_best,
        }

    def get_tree_status(self, campaign_id: str) -> dict[str, Any]:
        """Returns complete tree structure, Pareto frontier, and Causal Hypothesis Log."""
        camp = self.get_campaign(campaign_id)
        direction = camp["direction"]
        with self._connect() as conn:
            nodes = [
                dict(r)
                for r in conn.execute(
                    """
                    SELECT node_id, parent_id, secondary_parent_id, step_num, operator,
                           hypothesis, public_score, private_score, reward_hack_gap,
                           is_reward_hacking, verdict, verdict_reason, exec_time_ms,
                           code_loc, cyclomatic_complexity, dead_func_count, bloat_index,
                           one_liner_summary, created_at
                    FROM nodes WHERE campaign_id = ? ORDER BY step_num ASC
                    """,
                    (campaign_id,),
                ).fetchall()
            ]
            hypotheses = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM causal_hypotheses WHERE campaign_id = ? ORDER BY hypothesis_id ASC",
                    (campaign_id,),
                ).fetchall()
            ]
            steers = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM steer_ideas WHERE campaign_id = ? ORDER BY idea_id ASC",
                    (campaign_id,),
                ).fetchall()
            ]

        accepted = [n for n in nodes if n["verdict"] == "ACCEPTED" and n["public_score"] is not None]

        # Compute Pareto frontier: maximize score while minimizing code_loc
        pareto_frontier: list[dict[str, Any]] = []
        for cand in accepted:
            dominated = False
            for other in accepted:
                if other["node_id"] == cand["node_id"]:
                    continue
                better_or_eq_score = (
                    other["public_score"] >= cand["public_score"]
                    if direction == "maximize"
                    else other["public_score"] <= cand["public_score"]
                )
                strictly_better_score = (
                    other["public_score"] > cand["public_score"]
                    if direction == "maximize"
                    else other["public_score"] < cand["public_score"]
                )
                better_or_eq_loc = other["code_loc"] <= cand["code_loc"]
                strictly_better_loc = other["code_loc"] < cand["code_loc"]

                if better_or_eq_score and better_or_eq_loc and (strictly_better_score or strictly_better_loc):
                    dominated = True
                    break
            if not dominated:
                pareto_frontier.append(cand)

        champion = None
        if accepted:
            champion = sorted(
                accepted,
                key=lambda n: (
                    n["public_score"] if direction == "maximize" else -n["public_score"],
                    -n["code_loc"],
                ),
                reverse=True,
            )[0]

        return {
            "campaign": camp,
            "total_nodes": len(nodes),
            "accepted_count": len(accepted),
            "reward_hack_blocked_count": sum(1 for n in nodes if n["verdict"] == "REWARD_HACK_BLOCKED"),
            "crashed_count": sum(1 for n in nodes if n["verdict"] == "CRASHED"),
            "champion_node": champion,
            "pareto_frontier": pareto_frontier,
            "nodes": nodes,
            "causal_hypotheses": hypotheses,
            "steer_ideas": steers,
        }

    def export_kag_markdown(self, campaign_id: str, output_path: Path | None = None) -> str:
        """
        Crystallizes the campaign's Causal Hypothesis Log (both breakthroughs and refuted dead-ends)
        into a structured Markdown knowledge document and semantic triplets for KAG / ReMe memory.
        """
        status = self.get_tree_status(campaign_id)
        camp = status["campaign"]
        champ = status["champion_node"]

        lines = [
            f"# 🧠 KAG Causal Experience Distillation: `{camp['name']}` (`{campaign_id}`)",
            f"> **Goal:** {camp['goal']} | **Direction:** `{camp['direction']}` | **Total Steps:** `{status['total_nodes']}`",
            "",
        ]
        if champ:
            lines.extend(
                [
                    "## 🏆 Champion Solution Node",
                    f"- **Node ID:** `{champ['node_id']}` (Operator: `{champ['operator']}`)",
                    f"- **Public Score:** `{champ['public_score']}` | **Held-Out Private Score:** `{champ['private_score']}` | **Reward Hack Gap:** `{champ['reward_hack_gap']}`",
                    f"- **Code Metrics:** `{champ['code_loc']} LOC`, Cyclomatic Complexity `{champ['cyclomatic_complexity']}`, Bloat Index `{champ['bloat_index']}`",
                    f"- **Winning Hypothesis:** {champ['hypothesis']}",
                    "",
                ]
            )

        lines.extend(
            [
                "## 🔬 Causal Hypothesis Log (HyperAgents + SAGE Memory)",
                "| Step / Node | Operator | Outcome | Score Delta | Causal Lesson Learned |",
                "|---|---|---|---:|---|",
            ]
        )
        for h in status["causal_hypotheses"]:
            lines.append(
                f"| `{h['node_id']}` | `{h['operator']}` | **{h['outcome']}** | `{h['score_delta']:+.4f}` | {h['lesson_learned']} |"
            )

        lines.extend(
            [
                "",
                "## 🔗 Semantic KAG Triplets (Subject -> Predicate -> Object)",
                "```json",
            ]
        )
        triplets = []
        for h in status["causal_hypotheses"]:
            triplets.append(
                {
                    "subject": f"{campaign_id}:{h['node_id']}",
                    "predicate": f"TESTED_HYPOTHESIS_{h['outcome']}",
                    "object": h["hypothesis"],
                    "score_delta": h["score_delta"],
                }
            )
        lines.append(json.dumps(triplets, ensure_ascii=False, indent=2))
        lines.append("```\n")

        md_text = "\n".join(lines)
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(md_text, encoding="utf-8")
        return md_text

    def get_domain_knowledge(self, domain_id: str | None = None) -> dict[str, Any]:
        """Returns the RSI-0 Domain Knowledge Matrix (or a specific domain pack) for Plan-First evolution."""
        from dataclasses import asdict
        if __package__ in (None, ""):
            from rsi_engine.knowledge_injector import KNOWLEDGE_MATRIX
        else:
            from .knowledge_injector import KNOWLEDGE_MATRIX
        if domain_id and domain_id in KNOWLEDGE_MATRIX:
            return asdict(KNOWLEDGE_MATRIX[domain_id])
        return {k: asdict(v) for k, v in KNOWLEDGE_MATRIX.items()}

    def audit_target_knowledge(self, file_path: Path | str) -> dict[str, Any]:
        """Audits a target file against RSI-0 playability, hitbox physics, and graphics invariants."""
        if __package__ in (None, ""):
            from rsi_engine.knowledge_injector import audit_file_against_knowledge
        else:
            from .knowledge_injector import audit_file_against_knowledge
        return audit_file_against_knowledge(file_path)

