---
name: deep-web-and-archive-researcher
description: "Трехуровневый исследовательский скилл (Surface Web + Browser DOM Scraper + Deep Technical Archives / Unindexed Dumps — GitHub Code Dumps, Internet Archive Wayback, заводские EPC каталоги Amayama, ETKA, Skoda-Parts, Polo.blue). Запрещает выдумывать фейковые артикулы или моки без реальных источников."
---

# Deep Web, Browser DOM & Unindexed Technical Archive Researcher

## Назначение
Ликвидирует генерацию «фейковых реплик из головы» при разработке отраслевых систем (каталогов автозапчастей, ERP, медицинских/промышленных справочников). Перед написанием кода агент обязан пройти 3 контура разведки:

1. **Контур 1: Веб-поиск (`google_search`)** — проверка подлинности заводских OEM-номеров, ревизий, технических параметров (диаметр, толщина, сверловка, PR-коды, моменты затяжки).
2. **Контур 2: Браузерный парсинг таблиц и DOM (`google:browse` + Headless Chromium)** — прямое извлечение полных ведомостей деталей из реальных онлайн-каталогов (`amayama.com`, `skoda-parts.com`, `catalog.polo.blue`, `autoparts-24.com`).
3. **Контур 3: Глубокий поиск по неиндексируемым архивам и дампам (`Deep Technical Archives / OSINT Code & SQL Dumps`)**:
   - Поиск открытых SQL/JSON/CSV дампов (`gh search code`, `gh search repos`, `archive.org` Wayback CDX) по схемам `TecDoc`, `ACES/PIES`, `ETKA`, `EPC`;
   - Скачивание реальных фотографий узлов и деталей в локальное хранилище `storage/images/`.
   - Передача пакета верифицированных данных в `inter_agent_memory_bus`.