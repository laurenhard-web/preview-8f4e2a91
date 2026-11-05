#!/usr/bin/env python3
"""
RSI-0 Domain Knowledge Injector & Multi-Epoch Plan Expander (knowledge_injector.py)
Solves the "недостаточно знаний в системе RSI-0" root cause by equipping RSI-0 / AIDE²
with structured domain invariants, mathematical formulas, collision contracts, and
4x Crop Vision Gate checks across 6 interactive/3D/game-engine domains.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
from typing import Any


@dataclass
class DomainKnowledgePack:
    domain_id: str
    title: str
    mandatory_invariants: list[str]
    math_and_physics_contracts: list[str]
    visual_and_era_standards: list[str]
    forbidden_anti_patterns: list[str]
    verification_anchors: list[str]


KNOWLEDGE_MATRIX: dict[str, DomainKnowledgePack] = {
    "3D_RENDERING_AND_BOIDS": DomainKnowledgePack(
        domain_id="3D_RENDERING_AND_BOIDS",
        title="3D Perspective Frustum, Boids Flocking & Anatomical Procedural Shading",
        mandatory_invariants=[
            "3D perspective projection must sort all faces/entities back-to-front by camera-space Z (Painter's Algorithm).",
            "Strict 3D bounding-box clamping inside [-X_max + margin, +X_max - margin] with inward normal velocity reflection.",
            "Interactive orbit camera via mouse drag + W/A/S/D/Arrows + interactive particle/food spawning.",
        ],
        math_and_physics_contracts=[
            "Craig Reynolds Boids: F_total = w_sep * F_separation + w_align * F_alignment + w_coh * F_cohesion + w_seek * F_target + w_wall * F_boundary",
            "Fish pitch angle = clamp(atan2(vy, hypot(vx, vz)), -0.38, 0.38); tail wag phase = sin(tick * freq + phase)",
        ],
        visual_and_era_standards=[
            "5 distinct tropical fish species with multi-stop cylindrical scale gradients, gill operculum arc, translucent rayed pectoral/dorsal/caudal fins, and 1.5px dark iris.",
            "Water aeration bubbles must use radial translucent gradient + top-left crescent highlight arc (ZERO center dots!).",
            "Multi-tower medieval castle with conical roofs, arched gate, oxygen pump filter, and waving volumetric kelp.",
        ],
        forbidden_anti_patterns=[
            "FORBIDDEN: White circular sclera (`ctx.arc` + `#ffffff`) with black center pupil on fish (creates 'floating eyeball' horror artifact).",
            "FORBIDDEN: Gray rings with white/black center dots for water bubbles.",
        ],
        verification_anchors=[
            "outOfBoundsCount === 0 across 500 frames",
            "4x Crop Vision check on fish head and bubble column confirms zero cartoon white eyeballs",
        ],
    ),
    "RAYCASTER_FPS_1992_VGA": DomainKnowledgePack(
        domain_id="RAYCASTER_FPS_1992_VGA",
        title="1992 id Software VGA Wolfenstein 3D Raycaster, Z-Buffered Props & Classic HUD",
        mandatory_invariants=[
            "aiBot = false by default (100% manual control on launch; never walk or shoot without user input).",
            "Perpendicular wall distance correction: perpDist = rawDist * cos(rayAngle - playerAngle) to eliminate fisheye distortion.",
            "1D Z-Buffer array (zBuffer[numRays]) for per-column occlusion of enemy guards and 3D corridor props.",
        ],
        math_and_physics_contracts=[
            "Sliding doors (tile === 4): doorOpen[y][x] interpolates 0.0 -> 1.0 when distance < 1.95; DDA ray passes through when wallX < doorOpen[y][x].",
            "Circle-vs-Tile collision with sliding radius = 0.24 along X and Y independently.",
        ],
        visual_and_era_standards=[
            "128x128 procedural wall textures: Red Castle Brick, Blue Prison Stone with glowing wall torches, Golden Eagle Tapestry, Cyan Steel Doors.",
            "96x128 anatomical guard sprites: M40 Stahlhelm steel helmet, shaded face, uniform tunic with Sam Browne belt, jackboots, MP-40 submachine gun.",
            "3D Corridor Props in Z-Buffer: Overhead green/gold glowing ceiling lamps, fluted marble pillars, wooden barrels with iron bands, gold treasure chalices (+1000 PTS), medkits (+25% HP).",
            "Classic 1992 Royal-Blue (#172554) bottom HUD with FLOOR, SCORE, LIVES, animated B.J. Blazkowicz Mugshot Face in center, HEALTH %, AMMO, WEAPON.",
        ],
        forbidden_anti_patterns=[
            "FORBIDDEN: Low-res 24x32 blocky pink-square guard heads.",
            "FORBIDDEN: Uncontrolled demo bot walking and shooting automatically when the user opens the tab.",
        ],
        verification_anchors=[
            "aiBot === false on startup",
            "HUD includes animated B.J. Blazkowicz mugshot and 7 classic status boxes",
        ],
    ),
    "TILE_GRID_ARCADE_TANKS": DomainKnowledgePack(
        domain_id="TILE_GRID_ARCADE_TANKS",
        title="1990 NES/Dendy Battle City 26x26 Sub-Tile Grid, Anti-Jam Hitbox & Brick HP %",
        mandatory_invariants=[
            "aiBot = false by default so the golden player tank waits at spawn for human arrow/WASD keys.",
            "Inner collision hitbox must be 16x16 (margin = 5px inside 26x26 visual tank) to leave 12px clearance inside 28px corridors.",
            "Conditional corner lane-sliding: only slide toward 14px grid alignment if primary movement is blocked AND canTankMove(slideX, ny) is true.",
            "Pre-movement anti-jam guard `ensureTankUnstuck(tank)` ejects any tank overlapping a tile edge by 1..6px.",
        ],
        math_and_physics_contracts=[
            "Per-subtile destructible health matrix `subHP[26][26]` (100% intact -> 50% cracked -> 0% destroyed).",
            "Real-time aggregate HUD metrics: `bunkerBricksPct` (% HP of Eagle fortress wall) and `mapBricksPct` (% HP of castle/map brick walls).",
        ],
        visual_and_era_standards=[
            "5 distinct playable stages (Stage 01 Citadel, Stage 02 Steel Bridge, Stage 03 Forest Ambush, Stage 04 Castle Siege, Stage 05 Twin Rivers).",
            "Classic grey Famicom right sidebar with enemy tank counter icons, 1P lives, stage flag, plus left telemetry sidebar showing last pressed key.",
        ],
        forbidden_anti_patterns=[
            "FORBIDDEN: Unconditional `nx += (snapX - nx) * 0.45` before collision check (jams tank permanently into brick corners).",
            "FORBIDDEN: 24x24 full-sprite collision box inside 28px corridors.",
        ],
        verification_anchors=[
            "Player tank moves smoothly in all 4 directions (`ArrowUp/Down/Left/Right`, `WASD`, `ЦФЫВ`) with zero wall sticking",
            "Bunker Brick HP % and Map Brick HP % bars update dynamically on every shell impact",
        ],
    ),
    "PLATFORMER_SWEPT_AABB": DomainKnowledgePack(
        domain_id="PLATFORMER_SWEPT_AABB",
        title="Super Mario Bros World 1-1 Swept AABB Physics, Power-Up FSM & Safe Spawn Zones",
        mandatory_invariants=[
            "aiBot = false by default with immediate single-tap impulse + continuous hold support (`ArrowLeft/Right/Up`, `WASD`, `Space`, `F`).",
            "Enemies near spawn must patrol within `[minX, maxX]` bounds so an idle human player is never killed before touching the keyboard.",
        ],
        math_and_physics_contracts=[
            "Separate X-axis and Y-axis Swept AABB collision resolution against blocks, warp pipes, staircases, and moving platforms.",
            "Variable jump gravity (`grav = 0.40` while rising with jump held, `0.60` when falling).",
        ],
        visual_and_era_standards=[
            "3-state power-up FSM: Small Mario -> Super Mario (Mushroom) -> Fire Mario (white/red overalls shooting bouncing fireballs).",
            "Emerging Piranha Plants in green warp pipes + kickable spinning Koopa shells that bowl through Goombas.",
        ],
        forbidden_anti_patterns=[
            "FORBIDDEN: Enemies walking straight into x=55 spawn and killing idle player on frame 150.",
        ],
        verification_anchors=[
            "Keyboard `ArrowLeft/Right/Up` + `Space` + `F` and on-screen hold buttons move/jump/fire immediately",
        ],
    ),
    "IFRAME_KEYBOARD_AND_DEPLOY": DomainKnowledgePack(
        domain_id="IFRAME_KEYBOARD_AND_DEPLOY",
        title="Iframe Keyboard Focus, Artifact Live-Reload & Private GitHub / Secret VPS Deployment",
        mandatory_invariants=[
            "Every `<canvas>` must have `tabindex=\"0\"` and focus on click/hover (`el.focus({ preventScroll: true })`).",
            "Window `keydown`/`keyup` listeners must use `{ capture: true }` and decode `e.code`, `e.key` (including Cyrillic `ц/ф/ы/в`), and `e.keyCode` (`37..40, 32, 70`).",
            "Every game must provide a press-and-hold on-screen D-Pad (`onpointerdown=\"Sim.holdInput(dir, true)\"`, `onpointerup=\"Sim.holdInput(dir, false)\"`).",
            "Final artifact HTML must be touched via the native `write_to_file` or `replace_file_content` tool so the UI reloads the preview iframe.",
        ],
        math_and_physics_contracts=[
            "Secret preview bundle path `/s/<uuid4>/index.html` with `robots.txt` (`Disallow: /`) and `X-Robots-Tag: noindex, nofollow`.",
        ],
        visual_and_era_standards=[
            "Live keyboard telemetry indicator in top header and game HUD showing the exact key pressed by the user.",
        ],
        forbidden_anti_patterns=[
            "FORBIDDEN: Overwriting artifact HTML only via bash subprocess without triggering UI tool refresh.",
        ],
        verification_anchors=[
            "All 5 games respond to Arrow keys, WASD, Cyrillic ЦФЫВ, Space, and on-screen holdable D-Pad buttons",
        ],
    ),
}


def audit_file_against_knowledge(file_path: Path | str) -> dict[str, Any]:
    """Runs deterministic RSI-0 domain knowledge checks against a JS/HTML/Python file."""
    p = Path(file_path)
    if not p.exists():
        return {"file": str(p), "passed": False, "defects": ["FILE_NOT_FOUND"]}

    text = p.read_text(encoding="utf-8", errors="replace")
    defects: list[str] = []

    if re.search(r"\blet\s+(aiBot|aiDriver)\s*=\s*true\b", text):
        defects.append("[RSI-PLAY-01] Default autopilot (`aiBot = true`) is enabled; must be `false`.")
    if re.search(r"\bn[xy]\s*\+=\s*\(\s*snap[XY]\s*-\s*n[xy]\s*\)", text):
        defects.append("[RSI-PHYS-02] Unconditional `snapX/snapY` coordinate mutation causes wall jamming.")
    if p.suffix == ".html":
        if 'tabindex="0"' not in text:
            defects.append("[RSI-PLAY-02] HTML `<canvas>` is missing `tabindex=\"0\"` for iframe keyboard focus.")
        if "holdInput(" not in text:
            defects.append("[RSI-PLAY-03] HTML is missing press-and-hold `holdInput()` D-Pad controls.")
        if re.search(r"(RECALL_ID:\s*REC-|\[DIR-0\d\d\])", text):
            defects.append("[DIR-010] Internal factory metadata leaked into client HTML.")

    return {
        "file": str(p),
        "passed": len(defects) == 0,
        "defect_count": len(defects),
        "defects": defects,
        "domains_loaded": list(KNOWLEDGE_MATRIX.keys()),
    }


def export_knowledge_json(out_path: Path | str) -> dict[str, Any]:
    payload = {k: asdict(v) for k, v in KNOWLEDGE_MATRIX.items()}
    Path(out_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    import sys

    targets = sys.argv[1:] or [
        "/home/antigravity/test_benchmarks/test_benchmarks_showcase.html",
        "/home/antigravity/test_benchmarks/05_battle_city_tanks_90s/engine_battle_city.js",
        "/home/antigravity/test_benchmarks/04_wolfenstein3d_fps/engine_wolf3d.js",
        "/home/antigravity/test_benchmarks/02_super_mario_platformer/engine_mario.js",
        "/home/antigravity/test_benchmarks/01_blender_aquarium_3d/engine_aquarium.js",
        "/home/antigravity/test_benchmarks/03_zombie_car_derby/engine_zombie_car.js",
    ]
    results = [audit_file_against_knowledge(t) for t in targets]
    print(json.dumps({"all_passed": all(r["passed"] for r in results), "results": results}, ensure_ascii=False, indent=2))
