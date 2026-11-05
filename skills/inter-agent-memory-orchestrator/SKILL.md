---
name: inter-agent-memory-orchestrator
description: Оркестратор сквозной передачи памяти и верифицированных артефактов между агентами (Researcher -> DB & Storage Architect -> CAD Frontend Engineer -> Strict Judge) через таблицу inter_agent_memory_bus в SQLite WAL и граф KAG.
---
# Inter-Agent Memory Bus & Multi-Stage Handoff Orchestrator

## Назначение
Обеспечивает 100% сохранность знаний между этапами и эпохами RSI:
1. Каждый агент перед стартом читает входящие пакеты из `inter_agent_memory_bus` (`fetch_agent_inbox`) и графа памяти `KAG` (`orch.py recall`).
2. После завершения своего этапа агент публикует `publish_handoff_packet` со списком реально созданных на диске файлов (`SQLite DB`, `.pdf`, `.jpg/.png/.svg`) и проверенных URL-источников.
3. Судья (`@strict_judge`) проверяет физическое наличие БД, таблиц, PDF-каталогов, изображений и соответствие OEM-артикулов заводским спецификациям.