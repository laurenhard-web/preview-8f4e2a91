#!/usr/bin/env python3
"""
RSI-0 v7 Inter-Agent Memory Bus & Multi-Stage Handoff Orchestrator (agent_memory_bus.py)

Provides persistent, loss-free memory transfer between specialized agents in a campaign:
  1. @deep_web_researcher (Surface Web + Browser DOM + Deep Technical Archives / Unindexed Dumps)
  2. @storage_and_db_architect (SQLite3 + FTS5 DB + File Storage + Image Storage + Real PDF Catalogs)
  3. @cad_frontend_engineer (High-Precision Interactive SVG Blueprints + Live DB/Storage/PDF Explorer)
  4. @strict_judge (Verifies DB row counts, disk files, PDF headers, OEM authenticity, and Chromium Vision Gate)
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import sqlite3
from typing import Any

RSI_DB = Path("/shared/user/.gemini/orchestrator/rsi_evolution.db")


class InterAgentMemoryBus:
    """
    SQLite WAL Blackboard & Handoff Bus for multi-agent memory transfer across RSI epochs.
    """

    def __init__(self, db_path: Path = RSI_DB) -> None:
        self.db_path = db_path
        self._init_schema()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=MEMORY;")
        return conn

    def _init_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS inter_agent_memory_bus (
                    packet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT NOT NULL,
                    epoch_num INTEGER NOT NULL,
                    sender_agent TEXT NOT NULL,
                    receiver_agent TEXT NOT NULL,
                    stage_name TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    artifacts_on_disk_json TEXT NOT NULL DEFAULT '[]',
                    verified_sources_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_iamb_camp_ep
                    ON inter_agent_memory_bus(campaign_id, epoch_num);
                """
            )

    def publish_handoff_packet(
        self,
        campaign_id: str,
        epoch_num: int,
        sender_agent: str,
        receiver_agent: str,
        stage_name: str,
        summary: str,
        payload: dict[str, Any],
        artifacts_on_disk: list[str],
        verified_sources: list[str],
    ) -> int:
        now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO inter_agent_memory_bus (
                    campaign_id, epoch_num, sender_agent, receiver_agent,
                    stage_name, summary, payload_json,
                    artifacts_on_disk_json, verified_sources_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    campaign_id,
                    epoch_num,
                    sender_agent,
                    receiver_agent,
                    stage_name,
                    summary,
                    json.dumps(payload, ensure_ascii=False),
                    json.dumps(artifacts_on_disk, ensure_ascii=False),
                    json.dumps(verified_sources, ensure_ascii=False),
                    now,
                ),
            )
            return int(cur.lastrowid or 0)

    def fetch_agent_inbox(self, campaign_id: str, receiver_agent: str | None = None) -> list[dict[str, Any]]:
        with self._conn() as conn:
            if receiver_agent:
                rows = conn.execute(
                    """
                    SELECT * FROM inter_agent_memory_bus
                    WHERE campaign_id = ? AND receiver_agent = ?
                    ORDER BY packet_id ASC
                    """,
                    (campaign_id, receiver_agent),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM inter_agent_memory_bus
                    WHERE campaign_id = ?
                    ORDER BY packet_id ASC
                    """,
                    (campaign_id,),
                ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["payload"] = json.loads(d.pop("payload_json", "{}"))
            d["artifacts_on_disk"] = json.loads(d.pop("artifacts_on_disk_json", "[]"))
            d["verified_sources"] = json.loads(d.pop("verified_sources_json", "[]"))
            out.append(d)
        return out
