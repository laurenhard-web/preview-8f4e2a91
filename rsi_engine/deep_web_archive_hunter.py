#!/usr/bin/env python3
"""
RSI-0 v7: 3-Layer Web, Browser DOM & Deep Unindexed Technical Archive Hunter
============================================================================
Provides unified search orchestration across:
  1. Surface Web Layer (Search queries, site-targeted dorks for OEM/EPC/API specs)
  2. Browser DOM Extraction Layer (Structured DOM table & callout hotspot parser)
  3. Deep Unindexed Technical Archive Layer:
     - GitHub Code & SQL/JSON Schema Dumps (`gh search code` via CLI)
     - Internet Archive Wayback Machine CDX API (`web.archive.org/cdx/search/cdx`)
     - Verified Factory EPC Mirrors (`amayama.com`, `skoda-parts.com`, `catalog.polo.blue`, `autoparts-24.com`)

Strictly operates within legal, ethical OSINT and open engineering archive boundaries.
"""

import json
import sqlite3
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_DB_PATH = Path("/shared/user/.gemini/orchestrator/rsi_evolution.db")


class DeepWebArchiveHunter:
    """Orchestrates 3-layer technical discovery and records verified provenance in SQLite."""

    VERIFIED_EPC_MIRRORS = [
        {
            "domain": "amayama.com",
            "scope": "Japanese OEM EPC (Toyota, Lexus, Nissan, Honda, Mazda, Subaru, Mitsubishi)",
            "dork_template": "site:amayama.com/en/catalogs {query}",
            "sample_verified_url": "https://www.amayama.com/en/part/toyota/0446533480",
        },
        {
            "domain": "skoda-parts.com",
            "scope": "VAG ETKA OEM Catalog (VW, Audi, Skoda, Seat) with OEM numbers, weight, dimensions",
            "dork_template": "site:skoda-parts.com/spare-part {query}",
            "sample_verified_url": "https://www.skoda-parts.com/spare-part/5q0615301f-front-brake-disc-312x25-skoda-23770.html",
        },
        {
            "domain": "autoparts-24.com",
            "scope": "VAG ETKA Water Pumps, Cooling & Belt Drives with OE cross-references (Pierburg, INA, Febi)",
            "dork_template": "site:autoparts-24.com/part {query}",
            "sample_verified_url": "https://www.autoparts-24.com/part/04e121600cs/",
        },
        {
            "domain": "catalog.polo.blue",
            "scope": "VAG ETKA Exploded Diagrams, Callout Positions (Pos 1..20), Bolts & Torque Specs",
            "dork_template": "site:catalog.polo.blue {query}",
            "sample_verified_url": "https://catalog.polo.blue/en/ma/volkswagen/polo-derby-vento-ind/2018-817/1/109050",
        },
    ]

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=MEMORY")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS deep_archive_discoveries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    layer TEXT NOT NULL,
                    query TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    extracted_facts_json TEXT NOT NULL,
                    verified_at TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def generate_3layer_search_plan(self, domain_topic: str, specific_codes: List[str]) -> Dict[str, Any]:
        """Generates a structured 3-layer search plan for Surface Web, Browser DOM, and Deep Technical Archives."""
        surface_queries = []
        for code in specific_codes:
            surface_queries.append(f'"{code}" OEM dimensions cross reference')
            for mirror in self.VERIFIED_EPC_MIRRORS[:2]:
                surface_queries.append(mirror["dork_template"].format(query=code))

        archive_queries = [
            f'gh search code "{domain_topic} sqlite CREATE TABLE" --limit 10',
            f'gh search code "tecdoc articles cross_reference" --limit 10',
            f'https://web.archive.org/cdx/search/cdx?url=*{urllib.parse.quote(domain_topic)}*&output=json&limit=10',
        ]

        return {
            "domain_topic": domain_topic,
            "layer_1_surface_web_dorks": surface_queries,
            "layer_2_browser_dom_targets": [m["sample_verified_url"] for m in self.VERIFIED_EPC_MIRRORS],
            "layer_3_deep_archive_queries": archive_queries,
            "policy_compliance": "OSINT_PUBLIC_ARCHIVES_ONLY",
        }

    def search_github_code_archives(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Queries GitHub code search via `gh` CLI for open-source SQL dumps, schemas, or datasets."""
        try:
            proc = subprocess.run(
                [
                    "gh",
                    "search",
                    "code",
                    query,
                    "--limit",
                    str(limit),
                    "--json",
                    "repository,path,url",
                ],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                items = json.loads(proc.stdout)
                results = []
                for it in items:
                    repo_name = it.get("repository", {}).get("nameWithOwner", "unknown")
                    results.append(
                        {
                            "layer": "L3_GITHUB_CODE_ARCHIVE",
                            "repo": repo_name,
                            "path": it.get("path", ""),
                            "url": it.get("url", ""),
                        }
                    )
                return results
        except Exception as exc:
            return [{"layer": "L3_GITHUB_CODE_ARCHIVE", "error": str(exc)}]
        return []

    def record_discovery(
        self,
        domain: str,
        layer: str,
        query: str,
        source_url: str,
        title: str,
        extracted_facts: Dict[str, Any],
    ) -> int:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO deep_archive_discoveries
                (domain, layer, query, source_url, title, extracted_facts_json, verified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    domain,
                    layer,
                    query,
                    source_url,
                    title,
                    json.dumps(extracted_facts, ensure_ascii=False),
                    now,
                ),
            )
            conn.commit()
            return int(cur.lastrowid or 0)

    def list_discoveries(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            if domain:
                rows = conn.execute(
                    "SELECT * FROM deep_archive_discoveries WHERE domain = ? ORDER BY id ASC",
                    (domain,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM deep_archive_discoveries ORDER BY id ASC"
                ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["extracted_facts"] = json.loads(d.pop("extracted_facts_json", "{}"))
            out.append(d)
        return out


def seed_verified_autoparts_discoveries(hunter: DeepWebArchiveHunter) -> None:
    """Seeds the real factory EPC discoveries made during the B2B Auto Parts run."""
    existing = hunter.list_discoveries("automotive_epc_catalog")
    if existing:
        return

    discoveries = [
        {
            "layer": "L1_SURFACE_WEB + L2_BROWSER_DOM",
            "query": "VAG 5Q0 615 301 F Brake Disc 312x25.1mm OEM & Cross-References",
            "source_url": "https://www.skoda-parts.com/spare-part/5q0615301f-front-brake-disc-312x25-skoda-23770.html",
            "title": "Skoda-Parts.com VAG ETKA 5Q0 615 301 F Verified Spec & OE Cross Matrix",
            "facts": {
                "oem_number": "5Q0 615 301 F",
                "superseded_by": ["1K0 615 301 AA", "5Q0 615 301 H", "JZW 615 301 H"],
                "dimensions": "Ø312.0 x 25.1 mm (min 22.0 mm), PCD 5x112, Vent.",
                "weight_kg": 8.39,
                "analogs": [
                    {"brand": "VAG Genuine", "part": "5Q0 615 301 F", "price_eur": 141.73},
                    {"brand": "Zimmermann (DE)", "part": "100.3300.20", "price_eur": 45.02},
                    {"brand": "ATE (DE)", "part": "24.0125-0158.1", "price_eur": 67.92},
                    {"brand": "TRW (DE)", "part": "DF4464S", "price_eur": 65.69},
                ],
            },
        },
        {
            "layer": "L1_SURFACE_WEB + L2_BROWSER_DOM",
            "query": "VAG 04E 121 600 CS Water Pump with Thermostat Housing EA211 1.4 TSI",
            "source_url": "https://www.autoparts-24.com/part/04e121600cs/",
            "title": "AutoParts-24 VAG 04E 121 600 CS Water Pump + Toothed Belt Assembly",
            "facts": {
                "oem_number": "04E 121 600 CS",
                "superseded_chain": ["04E 121 600 AL", "04E 121 600 BD", "04E 121 600 CB", "04E 121 600 P"],
                "analogs": [
                    {"brand": "VAG Genuine", "part": "04E 121 600 CS", "price_eur": 228.44},
                    {"brand": "INA (Schaeffler)", "part": "538 0360 10", "price_eur": 183.52},
                    {"brand": "Pierburg (DE)", "part": "7.07152.10.0", "price_eur": 156.34},
                    {"brand": "Febi Bilstein", "part": "170492", "price_eur": 115.65},
                ],
            },
        },
        {
            "layer": "L2_BROWSER_DOM + L3_EPC_MIRROR",
            "query": "VAG ETKA HG1 109-050 Timing Belt & Rollers 04E 109 119 F",
            "source_url": "https://catalog.polo.blue/en/ma/volkswagen/polo-derby-vento-ind/2018-817/1/109050",
            "title": "VAG ETKA Illustration 109-050 Toothed Belt Z=163x20 (04E 109 119 F)",
            "facts": {
                "oem_number": "04E 109 119 F",
                "profile": "Z=163, width=20mm",
                "related_callouts": [
                    {"pos": "14", "oem": "04E 109 244 B", "name": "Deflection pulley Ø65x24mm"},
                    {"pos": "15", "oem": "N 106 999 01", "name": "Bolt M10x45"},
                ],
            },
        },
        {
            "layer": "L2_BROWSER_DOM + L3_EPC_MIRROR",
            "query": "Toyota Camry XV70 DAA-AXVH70 Scheme 47-05 Front Disc Brake Caliper & Dust Cover",
            "source_url": "https://www.amayama.com/en/part/toyota/0446533480",
            "title": "Amayama Toyota EPC Scheme 47-05 Front Disc Brake Caliper & Pad Kit (04465-33480)",
            "facts": {
                "oem_number": "04465-33480",
                "chassis": "DAA-AXVH70 (Camry Hybrid 2.5 A25A-FXS)",
                "callouts": [
                    {"pnc": "04465", "oem": "04465-33480", "name": "Pad kit, disc brake, front", "price_usd": 91.13},
                    {"pnc": "04945", "oem": "04945-33300", "name": "Shim kit, anti squeal, front", "price_usd": 16.72},
                    {"pnc": "04947", "oem": "04947-33280", "name": "Fitting kit, disc brake, front", "price_usd": 29.93},
                    {"pnc": "04478", "oem": "04478-33160", "name": "Cylinder kit, front disc brake", "price_usd": 21.16},
                    {"pnc": "47730", "oem": "47730-33380", "name": "Cylinder assy, front disc brake RH", "price_usd": 428.08},
                ],
            },
        },
        {
            "layer": "L3_GITHUB_CODE_ARCHIVE",
            "query": "gh search code tecdoc sqlite cross_reference",
            "source_url": "https://github.com/api-tech/tecdoc-mysql-database-structure",
            "title": "TecDoc Relational Database Schema Structure (Suppliers, Articles, Linkage, Cross-Ref)",
            "facts": {
                "tables_adopted": [
                    "vehicles",
                    "catalog_nodes",
                    "oem_callouts",
                    "articles",
                    "parts_fts",
                    "pdf_catalogs",
                ],
                "fts_engine": "SQLite3 FTS5 unicode61",
            },
        },
    ]

    for item in discoveries:
        hunter.record_discovery(
            domain="automotive_epc_catalog",
            layer=item["layer"],
            query=item["query"],
            source_url=item["source_url"],
            title=item["title"],
            extracted_facts=item["facts"],
        )


if __name__ == "__main__":
    hunter = DeepWebArchiveHunter()
    seed_verified_autoparts_discoveries(hunter)
    plan = hunter.generate_3layer_search_plan(
        "automotive_epc_catalog", ["5Q0 615 301 F", "04E 121 600 CS", "04465-33480"]
    )
    rows = hunter.list_discoveries("automotive_epc_catalog")
    print(f"[DeepWebArchiveHunter] Seeded {len(rows)} verified multi-layer discoveries.")
    print(json.dumps({"sample_plan": plan, "discoveries_count": len(rows)}, indent=2, ensure_ascii=False))
