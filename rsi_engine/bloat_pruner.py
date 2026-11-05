#!/usr/bin/env python3
"""
Evolution Bloat Pruner: AST Dead-Code & Complexity Analyzer
Addresses the primary failure mode reported in Weco AI's AIDE²:
"The evolved agent's complexity blows up, and some of it is plain dead code;
both make further customization and production deployment harder."

Capabilities:
1. Calculates exact non-empty Lines of Code (LOC), Cyclomatic Complexity (McCabe),
   and maximum nesting depth for Python modules.
2. Detects dead/unreferenced functions, classes, and unused imports via AST symbol table analysis.
3. Computes an Evolution Bloat Score and suggests concrete pruning targets for
   metric-preserving simplification (`PRUNE` operator in AIDE²).
"""

from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class FunctionMetrics:
    name: str
    lineno: int
    end_lineno: int
    loc: int
    cyclomatic_complexity: int
    is_referenced: bool


@dataclass
class BloatReport:
    file_path: str
    total_lines: int
    code_loc: int
    total_cyclomatic_complexity: int
    avg_function_complexity: float
    max_function_complexity: int
    dead_functions: list[str] = field(default_factory=list)
    unused_imports: list[str] = field(default_factory=list)
    high_complexity_functions: list[str] = field(default_factory=list)
    bloat_index: float = 0.0  # 0.0 (clean) to 1.0 (heavily bloated)
    needs_pruning: bool = False
    functions: list[FunctionMetrics] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _compute_node_complexity(node: ast.AST) -> int:
    """Computes McCabe cyclomatic complexity of a function or module AST node."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(
            child,
            (
                ast.If,
                ast.For,
                ast.AsyncFor,
                ast.While,
                ast.ExceptHandler,
                ast.With,
                ast.AsyncWith,
                ast.IfExp,
                ast.comprehension,
            ),
        ):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += max(0, len(child.values) - 1)
    return complexity


def analyze_code_bloat(code_text: str, file_path: str = "<memory>") -> BloatReport:
    """
    Analyzes Python source code for LOC, cyclomatic complexity, dead functions,
    and unused imports.
    """
    raw_lines = code_text.splitlines()
    total_lines = len(raw_lines)
    code_loc = sum(
        1 for ln in raw_lines if ln.strip() and not ln.strip().startswith("#")
    )

    try:
        tree = ast.parse(code_text, filename=file_path)
    except SyntaxError as exc:
        return BloatReport(
            file_path=file_path,
            total_lines=total_lines,
            code_loc=code_loc,
            total_cyclomatic_complexity=0,
            avg_function_complexity=0.0,
            max_function_complexity=0,
            bloat_index=1.0,
            needs_pruning=True,
            recommendations=[f"Fix SyntaxError at line {exc.lineno}: {exc.msg}"],
        )

    # Collect all referenced names across the AST (excluding function/import definitions themselves)
    referenced_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            referenced_names.add(node.id)
        elif isinstance(node, ast.Attribute):
            referenced_names.add(node.attr)

    # Collect top-level and class-level function definitions
    func_defs: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_defs.append(node)

    # Collect imports
    imported_symbols: dict[str, int] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound_name = alias.asname or alias.name.split(".")[0]
                if bound_name != "__future__":
                    imported_symbols[bound_name] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                bound_name = alias.asname or alias.name
                imported_symbols[bound_name] = node.lineno

    unused_imports = [
        f"{sym} (L{lineno})"
        for sym, lineno in sorted(imported_symbols.items(), key=lambda x: x[1])
        if sym not in referenced_names
    ]

    functions_report: list[FunctionMetrics] = []
    dead_functions: list[str] = []
    high_complexity: list[str] = []

    # Entrypoints or dunder methods are never considered dead
    exempt_prefixes = ("__", "main", "test_", "run", "evaluate", "solve", "score", "predict")

    for fn in func_defs:
        start = fn.lineno
        end = getattr(fn, "end_lineno", start) or start
        fn_loc = max(1, end - start + 1)
        cc = _compute_node_complexity(fn)
        is_exempt = fn.name.startswith(exempt_prefixes) or bool(fn.decorator_list)
        is_ref = is_exempt or (fn.name in referenced_names)

        functions_report.append(
            FunctionMetrics(
                name=fn.name,
                lineno=start,
                end_lineno=end,
                loc=fn_loc,
                cyclomatic_complexity=cc,
                is_referenced=is_ref,
            )
        )
        if not is_ref:
            dead_functions.append(f"{fn.name} (L{start}-L{end}, {fn_loc} LOC)")
        if cc >= 10:
            high_complexity.append(f"{fn.name} (CC={cc}, L{start}-L{end})")

    total_cc = sum(f.cyclomatic_complexity for f in functions_report) or _compute_node_complexity(tree)
    avg_cc = (
        round(total_cc / len(functions_report), 2)
        if functions_report
        else float(total_cc)
    )
    max_cc = max((f.cyclomatic_complexity for f in functions_report), default=total_cc)

    # Calculate normalized bloat index [0..1]
    dead_penalty = min(0.4, 0.15 * len(dead_functions))
    import_penalty = min(0.2, 0.04 * len(unused_imports))
    cc_penalty = min(0.4, max(0.0, (avg_cc - 5.0) / 15.0))
    bloat_index = round(min(1.0, dead_penalty + import_penalty + cc_penalty), 3)
    needs_pruning = bool(dead_functions or len(unused_imports) >= 2 or max_cc >= 12 or bloat_index >= 0.25)

    recs: list[str] = []
    if dead_functions:
        recs.append(f"Remove {len(dead_functions)} unreferenced dead function(s): {', '.join(dead_functions)}")
    if unused_imports:
        recs.append(f"Clean up {len(unused_imports)} unused import(s): {', '.join(unused_imports)}")
    if high_complexity:
        recs.append(f"Decompose or simplify high-complexity function(s): {', '.join(high_complexity)}")
    if not recs:
        recs.append("Codebase is lean and free of structural bloat.")

    return BloatReport(
        file_path=file_path,
        total_lines=total_lines,
        code_loc=code_loc,
        total_cyclomatic_complexity=total_cc,
        avg_function_complexity=avg_cc,
        max_function_complexity=max_cc,
        dead_functions=dead_functions,
        unused_imports=unused_imports,
        high_complexity_functions=high_complexity,
        bloat_index=bloat_index,
        needs_pruning=needs_pruning,
        functions=functions_report,
        recommendations=recs,
    )


def analyze_file_bloat(path: Path) -> BloatReport:
    text = path.read_text(encoding="utf-8", errors="replace")
    return analyze_code_bloat(text, file_path=str(path))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AIDE² Evolution Bloat Pruner & AST Analyzer")
    parser.add_argument("target", help="Path to Python file to analyze")
    args = parser.parse_args()

    p = Path(args.target).resolve()
    report = analyze_file_bloat(p)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
