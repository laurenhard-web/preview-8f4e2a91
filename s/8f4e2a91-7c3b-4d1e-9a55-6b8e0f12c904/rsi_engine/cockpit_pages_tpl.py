#!/usr/bin/env python3
"""
Multi-Page AI Admin Control Plane v4.0 — HTML Template & Client Engine (cockpit_pages_tpl.py)
Follows Boss Directive [DIR-006] (Comp AI CRM Design System: #006B4F, untinted neutrals #0f0f0f/#171717/#2a2a2a,
5px/8px radii, Rule of Two Fills, AppIconRail, DetailSheetStats, SourcedValue, Suggestion, ToolStep)
and [DIR-004] (ISO-8601 timestamps & P1-P5 priority legend).

Generates 6 physical multi-page HTML files:
  1. index.html         (Page 1: 🎛️ Пульт Управления & ИИ-Симулятор «Что к чему приведёт»)
  2. rsi-studio.html    (Page 2: 🌳 Студия Дерева AIDE² & Живой Редактор Кода с ИИ-Мутатором)
  3. debates.html       (Page 3: 🗣️ Дебаты Совета Раунды 1–3 & Логи Рассуждений 8 Агентов)
  4. judges.html        (Page 4: ⚖️ Коллегия из 3 Судей & Журнал Вердиктов с Пультом Шефа)
  5. skills-editor.html (Page 5: 🧬 ИИ-Студия и Редактор 30 Скилов SkillForge)
  6. help-guide.html    (Page 6: 📖 Интерактивный Хелп «На пальцах» & Карта «Что где менять»)
"""

from __future__ import annotations

COCKPIT_V4_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>__PAGE_TITLE__ — Hive Mind &amp; RSI AI Admin v4.0</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    /* Comp AI Authentic Untinted Neutrals & #006B4F Accent [DIR-006] */
    .comp-surface { background-color: var(--card, #171717); border: 1px solid var(--border, #2a2a2a); border-radius: 8px; }
    .comp-bg { background-color: var(--background, #0f0f0f); color: var(--foreground, #f5f5f5); }
    .comp-btn-primary { background-color: #006B4F; color: #ffffff; border: 1px solid #008562; border-radius: 5px; }
    .comp-btn-primary:hover { background-color: #00805e; }
    .comp-btn-danger { background-color: #AE2E24; color: #ffffff; border: 1px solid #c93b30; border-radius: 5px; }
    .comp-btn-outline { background-color: var(--secondary, #1f1f1f); color: var(--foreground, #f5f5f5); border: 1px solid var(--border, #2a2a2a); border-radius: 5px; }
    .comp-btn-outline:hover { border-color: #40be96; }
    .comp-pill-active { background-color: #006B4F; color: #ffffff; border-color: #40be96; font-weight: 700; }
    .sourced-dotted { text-decoration: underline; text-decoration-style: dotted; text-underline-offset: 4px; cursor: help; }
    @keyframes pulseBorder {
      0% { box-shadow: 0 0 0 0 rgba(64, 190, 150, 0.7); }
      70% { box-shadow: 0 0 0 8px rgba(64, 190, 150, 0); }
      100% { box-shadow: 0 0 0 0 rgba(64, 190, 150, 0); }
    }
    .cockpit-flash { animation: pulseBorder 0.65s ease-out; }
  </style>
</head>
<body class="comp-bg antialiased min-h-screen flex flex-col">

  <!-- ===================================================================== -->
  <!-- TOP TELEMETRY & PRIORITY LEGEND BAR ([DIR-004] + [DIR-006])           -->
  <!-- ===================================================================== -->
  <header class="border-b border-[var(--border,#2a2a2a)] bg-[var(--card,#171717)] px-4 py-2.5 flex flex-wrap items-center justify-between gap-2 text-xs">
    <div class="flex items-center gap-2.5 flex-wrap">
      <span class="px-2.5 py-1 font-bold tracking-wide comp-btn-primary">
        🎛️ HIVE MIND &amp; RSI AI ADMIN v4.0
      </span>
      <span class="font-mono text-[var(--muted-foreground,#a0a0a0)]" id="hdr-iso-time">
        ISO-8601: __GENERATED_AT__
      </span>
      <span class="font-mono px-2 py-0.5 rounded bg-[var(--secondary,#1f1f1f)] border border-[var(--border,#2a2a2a)]">
        RECALL_ID: REC-20261105055329-EDCFCA
      </span>
      <span id="hdr-api-status" class="font-mono px-2 py-0.5 rounded border border-[var(--border,#2a2a2a)] text-emerald-400">
        ● Сервер :8090 + Живая Память Активны
      </span>
    </div>

    <!-- Priority Legend P1-P5 [DIR-004] + AI Copilot Trigger -->
    <div class="flex items-center gap-1.5 flex-wrap">
      <span class="text-[var(--muted-foreground,#a0a0a0)] mr-1">Приоритеты [DIR-004]:</span>
      <span class="px-1.5 py-0.5 rounded font-mono border border-[#e5735b]/50 text-[#e5735b]">P1 Критич</span>
      <span class="px-1.5 py-0.5 rounded font-mono border border-[#c07e22]/50 text-[#c07e22]">P2 Высок</span>
      <span class="px-1.5 py-0.5 rounded font-mono border border-[#40be96]/50 text-[#40be96]">P3 Штатн</span>
      <span class="px-1.5 py-0.5 rounded font-mono border border-[#4b87f0]/50 text-[#4b87f0]">P4 Низк</span>
      <span class="px-1.5 py-0.5 rounded font-mono border border-[#a0a0a0]/50 text-[#a0a0a0]">P5 Архив</span>
      <button onclick="toggleAiDrawer()" class="ml-2 px-3 py-1 font-bold comp-btn-primary">
        🤖 ИИ-Штурман («Что менять и к чему приведёт?»)
      </button>
    </div>
  </header>

  <!-- ===================================================================== -->
  <!-- MAIN 3-COLUMN LAYOUT: APP ICON RAIL + MULTI-PAGE SIDEBAR + WORKSPACE  -->
  <!-- ===================================================================== -->
  <div class="flex-1 flex flex-col lg:flex-row">

    <!-- 1. LEFT MULTI-PAGE NAVIGATION SIDEBAR (6 SEPARATE PAGES) -->
    <aside class="w-full lg:w-72 shrink-0 border-b lg:border-b-0 lg:border-r border-[var(--border,#2a2a2a)] bg-[var(--card,#171717)] p-3 space-y-3">
      <div class="text-xs font-bold uppercase tracking-wider text-[var(--muted-foreground,#a0a0a0)] px-2">
        🗂️ Многостраничная Навигация (6 страниц)
      </div>

      <nav class="space-y-1.5 text-xs" id="multipage-nav">
        <a href="index.html" onclick="return switchPage('dashboard', event)" id="nav-dashboard" class="block p-2.5 rounded-lg border transition">
          <div class="font-bold">1. 🎛️ Пульт &amp; ИИ-Симулятор</div>
          <div class="text-[var(--muted-foreground,#a0a0a0)] mt-0.5">Настройки порогов + ИИ-прогноз «Что к чему приведёт»</div>
        </a>

        <a href="rsi-studio.html" onclick="return switchPage('rsi', event)" id="nav-rsi" class="block p-2.5 rounded-lg border transition">
          <div class="font-bold">2. 🌳 Студия Дерева &amp; Кода</div>
          <div class="text-[var(--muted-foreground,#a0a0a0)] mt-0.5">Живой редактор Python-кода, ИИ-мутатор FUSE/PRUNE и Diff</div>
        </a>

        <a href="debates.html" onclick="return switchPage('debates', event)" id="nav-debates" class="block p-2.5 rounded-lg border transition">
          <div class="font-bold">3. 🗣️ Дебаты &amp; Мышление Агентов</div>
          <div class="text-[var(--muted-foreground,#a0a0a0)] mt-0.5">Как спорили отделы (Раунды 1–3) + логи мыслей 8 агентов</div>
        </a>

        <a href="judges.html" onclick="return switchPage('judges', event)" id="nav-judges" class="block p-2.5 rounded-lg border transition">
          <div class="font-bold">4. ⚖️ Коллегия из 3 Судей</div>
          <div class="text-[var(--muted-foreground,#a0a0a0)] mt-0.5">Тройной трибунал (SpecGuard + IOTA + OMEGA) и пульт 👍/⚠️/👎</div>
        </a>

        <a href="skills-editor.html" onclick="return switchPage('skills', event)" id="nav-skills" class="block p-2.5 rounded-lg border transition">
          <div class="font-bold">5. 🧬 Редактор 30 Скилов</div>
          <div class="text-[var(--muted-foreground,#a0a0a0)] mt-0.5">Правка SKILL.md, ИИ-сжатие «воды» AIDE² и аудит скриптов</div>
        </a>

        <a href="help-guide.html" onclick="return switchPage('help', event)" id="nav-help" class="block p-2.5 rounded-lg border transition">
          <div class="font-bold">6. 📖 Интерактивный Хелп</div>
          <div class="text-[var(--muted-foreground,#a0a0a0)] mt-0.5">Карта причинно-следственных связей «На пальцах»</div>
        </a>
      </nav>

      <!-- Quick Contextual Help Box in Sidebar -->
      <div class="p-3 rounded-lg bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] text-xs space-y-1.5">
        <div class="font-bold text-[#40be96]">💡 Подсказка по текущей странице:</div>
        <div id="sidebar-page-help" class="text-[var(--muted-foreground,#a0a0a0)] leading-relaxed">
          На этой странице вы можете двигать ползунки настроек и сразу видеть ИИ-прогноз последствий до сохранения в БД.
        </div>
      </div>

      <!-- Direct Directives Checklist -->
      <div class="p-3 rounded-lg bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] text-xs space-y-1">
        <div class="font-bold">👑 Активные Директивы Шефа:</div>
        <div class="text-[var(--muted-foreground,#a0a0a0)] space-y-1 font-mono" id="sidebar-directives-list"></div>
      </div>
    </aside>

    <!-- 2. MAIN WORKSPACE AREA -->
    <main class="flex-1 p-4 md:p-5 space-y-4 overflow-y-auto">

      <!-- DetailSheetStats 4-Cell Docked Telemetry Strip [DIR-006] -->
      <div class="grid grid-cols-2 lg:grid-cols-4 border border-[var(--border,#2a2a2a)] rounded-lg overflow-hidden bg-[var(--card,#171717)] text-xs">
        <div class="p-3 border-b lg:border-b-0 border-r border-[var(--border,#2a2a2a)]">
          <div class="text-[var(--muted-foreground,#a0a0a0)]">Текущая страница (Multi-Page)</div>
          <div class="text-sm font-bold mt-0.5 text-[#40be96]" id="stat-current-page">1. 🎛️ Пульт &amp; ИИ-Симулятор</div>
          <div class="font-mono text-[var(--muted-foreground,#a0a0a0)] mt-0.5" id="stat-page-url">URL: /index.html</div>
        </div>
        <div class="p-3 border-b lg:border-b-0 lg:border-r border-[var(--border,#2a2a2a)]">
          <div class="text-[var(--muted-foreground,#a0a0a0)]">Парето-Чемпион дерева AIDE²</div>
          <div class="text-sm font-bold font-mono mt-0.5" id="stat-champion">node_005_prune (100% · 8 LOC)</div>
          <div class="text-[var(--muted-foreground,#a0a0a0)] mt-0.5">Поймано читов вето: <b class="text-[#e5735b]" id="stat-blocked-cnt">1</b></div>
        </div>
        <div class="p-3 border-r border-[var(--border,#2a2a2a)]">
          <div class="text-[var(--muted-foreground,#a0a0a0)]">Судебный орган приёмки</div>
          <div class="text-sm font-bold mt-0.5">⚖️ Коллегия из 3 Судей</div>
          <div class="text-[var(--muted-foreground,#a0a0a0)] mt-0.5">SpecGuard (1.5x) · IOTA (1.5x) · OMEGA (1.0x)</div>
        </div>
        <div class="p-3">
          <div class="text-[var(--muted-foreground,#a0a0a0)]">Сессии Дебатов и Агенты</div>
          <div class="text-sm font-bold mt-0.5" id="stat-debates-cnt">2 сессии Совета · 8 агентов</div>
          <div class="text-[var(--muted-foreground,#a0a0a0)] mt-0.5">Каталог скилов: <b id="stat-skills-cnt">30 скилов</b></div>
        </div>
      </div>

      <!-- Live Action Feedback Toast Banner -->
      <div id="live-action-banner" class="comp-surface px-4 py-2.5 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div class="flex items-center gap-2">
          <span class="px-2 py-0.5 font-bold comp-btn-primary" id="banner-pill">ЖИВОЕ УПРАВЛЕНИЕ</span>
          <span id="banner-msg" class="font-medium">
            Вы находитесь в многостраничной ИИ-Админке v4.0. Любую настройку, код узла или скил можно изменить с мгновенным ИИ-прогнозом «Что к чему приведёт».
          </span>
        </div>
        <span class="font-mono text-[var(--muted-foreground,#a0a0a0)]" id="banner-sub">Порт :8090 / SQLite WAL</span>
      </div>

      <!-- ================================================================= -->
      <!-- PAGE 1: 🎛️ ПУЛЬТ УПРАВЛЕНИЯ & ИИ-СИМУЛЯТОР «ЧТО К ЧЕМУ ПРИВЕДЁТ»  -->
      <!-- ================================================================= -->
      <section id="page-dashboard" class="space-y-4">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">

          <!-- Left 6 cols: Interactive Controls & Sliders (EDITABLE!) -->
          <div class="lg:col-span-6 comp-surface p-4 space-y-4">
            <div class="border-b border-[var(--border,#2a2a2a)] pb-3 flex items-start justify-between gap-2">
              <div>
                <h2 class="text-base font-bold">🎚️ Пульт Настроек Системы и Коллегии Судей (Живое редактирование)</h2>
                <p class="text-xs text-[var(--muted-foreground,#a0a0a0)] mt-0.5">
                  Двигайте любой ползунок ниже — в правом окне <b>ИИ-Симулятор последствий</b> сразу покажет, к чему это приведёт и какие решения изменят свой статус!
                </p>
              </div>
              <button onclick="applyAiOptimalConfig()" class="px-2.5 py-1.5 text-xs font-bold comp-btn-outline shrink-0">
                🤖 ИИ-Эталон
              </button>
            </div>

            <div class="space-y-4 text-xs">
              <!-- Control 1: Max Hack Gap -->
              <div class="p-3 rounded-lg bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] space-y-1.5">
                <div class="flex justify-between items-center">
                  <label for="cfg-gap" class="font-bold sourced-dotted" title="Максимально допустимая разница между открытым и секретным тестом">
                    1. Порог анти-чита Судьи №1 SpecGuard (Макс. разрыв Δ = Public − Private):
                  </label>
                  <span class="font-mono font-bold text-sm text-[#40be96]" id="cfg-gap-val">0.18</span>
                </div>
                <input id="cfg-gap" type="range" min="0.05" max="0.40" step="0.01" value="0.18" oninput="updateWhatIfPreview()" class="w-full accent-[#006B4F]" />
                <div class="text-[var(--muted-foreground,#a0a0a0)]">
                  <b>Что меняет:</b> Если агент на открытом тесте получил 100%, а на секретном 68.75% (разрыв <code>0.31</code> выше порога), Судья №1 блокирует решение вето <code>REWARD_HACK_BLOCKED</code>.
                </div>
              </div>

              <!-- Control 2: Plateau Window -->
              <div class="p-3 rounded-lg bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] space-y-1.5">
                <div class="flex justify-between items-center">
                  <label for="cfg-plateau" class="font-bold sourced-dotted">
                    2. Окно детекции плато AIDE² (Через сколько шагов без роста звать на помощь FUSE):
                  </label>
                  <span class="font-mono font-bold text-sm text-[#40be96]" id="cfg-plateau-val">2 шага</span>
                </div>
                <input id="cfg-plateau" type="range" min="1" max="5" step="1" value="2" oninput="updateWhatIfPreview()" class="w-full accent-[#006B4F]" />
                <div class="text-[var(--muted-foreground,#a0a0a0)]">
                  <b>Что меняет:</b> Когда <code>N</code> шагов подряд точность не растёт, система прекращает мелкие правки <code>IMPROVE</code> и включает оператор слияния с идеей человека <code>FUSE</code>.
                </div>
              </div>

              <!-- Control 3: Collegium Golden Threshold -->
              <div class="p-3 rounded-lg bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] space-y-1.5">
                <div class="flex justify-between items-center">
                  <label for="cfg-golden" class="font-bold sourced-dotted">
                    3. Проходной балл Коллегии 3 Судей в Золотой Фонд (01_GOLDEN_SOLUTIONS):
                  </label>
                  <span class="font-mono font-bold text-sm text-[#40be96]" id="cfg-golden-val">85 / 100</span>
                </div>
                <input id="cfg-golden" type="range" min="65" max="98" step="1" value="85" oninput="updateWhatIfPreview()" class="w-full accent-[#006B4F]" />
                <div class="text-[var(--muted-foreground,#a0a0a0)]">
                  <b>Что меняет:</b> Решения со средневзвешенным баллом 3 судей выше этого порога автоматически кристаллизуются в базу эталонов <code>01_GOLDEN_SOLUTIONS/</code>.
                </div>
              </div>

              <!-- Control 4: Auto-Prune Toggle & Mode -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="p-3 rounded-lg bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] space-y-1.5">
                  <label class="flex items-center justify-between font-bold cursor-pointer">
                    <span>4. Авто-санитар кода PRUNE:</span>
                    <input id="cfg-autoprune" type="checkbox" checked onchange="updateWhatIfPreview()" class="w-4 h-4 accent-[#006B4F]" />
                  </label>
                  <div class="text-[var(--muted-foreground,#a0a0a0)]">
                    Автоматически удалять мёртвые функции и лишние <code>import</code> после <code>FUSE</code>.
                  </div>
                </div>

                <div class="p-3 rounded-lg bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] space-y-1.5">
                  <div class="font-bold">5. Режим Роя Оркестратора:</div>
                  <select id="cfg-mode" onchange="updateWhatIfPreview()" class="w-full px-2.5 py-1.5 rounded bg-[var(--card,#171717)] border border-[var(--border,#2a2a2a)]">
                    <option value="full">FULL (Все 8 субагентов + Коллегия 3 Судей)</option>
                    <option value="lite">LITE (Экономия квоты)</option>
                  </select>
                </div>
              </div>

              <div class="flex flex-wrap gap-2 pt-1">
                <button onclick="saveConfigToBackend()" class="px-4 py-2 font-bold comp-btn-primary">
                  💾 Применить и сохранить настройки в SQLite БД
                </button>
                <button onclick="switchPage('rsi')" class="px-3 py-2 font-medium comp-btn-outline">
                  🌳 Перейти к редактированию кода узлов →
                </button>
              </div>
            </div>
          </div>

          <!-- Right 6 cols: AI What-If Impact Simulator ("Что к чему приведёт") -->
          <div id="what-if-card" class="lg:col-span-6 comp-surface p-4 space-y-3">
            <div class="border-b border-[var(--border,#2a2a2a)] pb-3 flex items-center justify-between gap-2">
              <div>
                <h2 class="text-base font-bold text-[#40be96]">🤖 ИИ-Симулятор Последствий («Что к чему приведёт»)</h2>
                <p class="text-xs text-[var(--muted-foreground,#a0a0a0)] mt-0.5">
                  Живой расчёт влияния ваших настроек на дерево решений AIDE² и вердикты Коллегии 3 Судей до записи в БД:
                </p>
              </div>
              <span id="whatif-risk-badge" class="px-2.5 py-1 rounded text-xs font-mono font-bold border border-[#40be96] text-[#40be96]">
                P3 · Сбалансированно
              </span>
            </div>

            <div id="whatif-impacts-list" class="space-y-2.5 text-xs"></div>

            <!-- Quick Navigation Cards to Other Pages -->
            <div class="pt-2 border-t border-[var(--border,#2a2a2a)] space-y-2 text-xs">
              <div class="font-bold">🧭 Куда перейти дальше (быстрые переходы по страницам):</div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <button onclick="switchPage('debates')" class="p-2.5 text-left comp-btn-outline">
                  <b>🗣️ Страница 3: Логи Дебатов и Мыслей</b>
                  <div class="text-[var(--muted-foreground,#a0a0a0)] mt-0.5">Посмотреть, как спорили 8 агентов и запустить новый Совет</div>
                </button>
                <button onclick="switchPage('judges')" class="p-2.5 text-left comp-btn-outline">
                  <b>⚖️ Страница 4: Коллегия из 3 Судей</b>
                  <div class="text-[var(--muted-foreground,#a0a0a0)] mt-0.5">Протоколы голосования 3 судей, вето и кнопки 👍/⚠️/👎</div>
                </button>
              </div>
            </div>
          </div>

        </div>
      </section>

      <!-- ================================================================= -->
      <!-- PAGE 2: 🌳 СТУДИЯ ДЕРЕВА AIDE² & ЖИВОЙ РЕДАКТОР КОДА УЗЛОВ        -->
      <!-- ================================================================= -->
      <section id="page-rsi" class="hidden space-y-4">
        <!-- Quick Scenario Bar inside RSI Studio -->
        <div class="comp-surface p-3 flex flex-wrap items-center gap-2 text-xs">
          <span class="font-bold text-[var(--muted-foreground,#a0a0a0)]">⚡ Фокус дерева (1 клик):</span>
          <button onclick="focusRsiNode('node_000_draft')" class="px-2.5 py-1 comp-btn-outline">1. Старт #0 (56.25%, 2 LOC)</button>
          <button onclick="focusRsiNode('node_002_improve')" class="px-2.5 py-1 comp-btn-outline">2. 🛡️ Пойманный Чит #2 (Δ=0.31 BLOCKED)</button>
          <button onclick="focusRsiNode('node_004_fuse')" class="px-2.5 py-1 comp-btn-outline">3. 🚀 Прорыв идеей Шефа #4 FUSE (14 LOC)</button>
          <button onclick="focusRsiNode('node_005_prune')" class="px-2.5 py-1 comp-btn-primary font-bold">4. ✂️ Пример PRUNE #5 (Чемпион 8 LOC)</button>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <!-- Left 5 cols: 2D Branching Tree & Filters -->
          <div class="lg:col-span-5 comp-surface p-4 space-y-3">
            <h2 class="text-base font-bold">🌳 2D-Схема Ветвления Дерева Кода (`weco_fraud_golf`)</h2>
            <p class="text-xs text-[var(--muted-foreground,#a0a0a0)]">
              Кликните на любой узел, чтобы открыть его код, построчный Diff с родителем и запустить живую ИИ-мутацию:
            </p>
            <div id="rsi-tree-diagram" class="p-3 rounded-lg bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] font-mono text-xs space-y-1.5"></div>
            <div id="rsi-nodes-cards" class="space-y-2 max-h-[360px] overflow-y-auto pr-1 text-xs"></div>
          </div>

          <!-- Right 7 cols: Live Node Inspector, Line Diff & Code Mutator -->
          <div id="rsi-inspector-box" class="lg:col-span-7 comp-surface p-4 space-y-4">
            <div class="border-b border-[var(--border,#2a2a2a)] pb-3 flex flex-wrap items-start justify-between gap-2">
              <div>
                <div class="flex items-center gap-2 text-xs font-mono">
                  <span id="nd-prio" class="px-2 py-0.5 rounded border border-[#40be96] text-[#40be96]">P1 · Чемпион</span>
                  <span id="nd-op" class="px-2 py-0.5 rounded bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)]">PRUNE</span>
                  <span id="nd-iso" class="text-[var(--muted-foreground,#a0a0a0)]"></span>
                </div>
                <h3 class="text-lg font-bold mt-1" id="nd-title">Очистка #5 (PRUNE): Парето-Чемпион</h3>
                <div class="text-xs text-[var(--muted-foreground,#a0a0a0)] mt-0.5" id="nd-parent-line"></div>
              </div>
              <span id="nd-verdict-badge" class="px-3 py-1 rounded text-xs font-mono font-bold comp-btn-primary">🏆 ПАРЕТО-ЧЕМПИОН</span>
            </div>

            <!-- Plain Russian Explanation -->
            <div class="p-3 rounded-lg bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] text-xs space-y-1">
              <div class="font-bold text-[#40be96]">🔍 Что было сделано в этом узле и почему:</div>
              <p id="nd-plain-why" class="leading-relaxed"></p>
            </div>

            <!-- Colored Line-by-Line Diff vs Parent -->
            <div class="space-y-1.5 text-xs">
              <div class="font-bold">🔀 Построчное сравнение кода (Diff с родителем: красным <code>-</code> удалено, зелёным <code>+</code> добавлено):</div>
              <div id="nd-diff-view" class="p-3 rounded-lg bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] font-mono overflow-x-auto space-y-0.5 max-h-[210px]"></div>
            </div>

            <!-- LIVE CODE EDITOR & AI MUTATOR (REAL ACTION!) -->
            <div class="p-3.5 rounded-lg bg-[var(--background,#0f0f0f)] border border-[#006B4F] space-y-3 text-xs">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="font-bold text-[#40be96]">✏️ Живой Редактор и ИИ-Мутатор Кода (Создать новый узел дерева в БД)</div>
                <div class="flex flex-wrap gap-1.5">
                  <button onclick="fillAiMutationPreset('prune_clean')" class="px-2 py-1 comp-btn-outline">✂️ ИИ: Сжать код (PRUNE)</button>
                  <button onclick="fillAiMutationPreset('fuse_boost')" class="px-2 py-1 comp-btn-outline">🚀 ИИ: Усилить формулу (FUSE)</button>
                  <button onclick="fillAiMutationPreset('cheat_test')" class="px-2 py-1 comp-btn-outline">🛡️ ИИ: Тест чита (Δ=0.31)</button>
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div>
                  <label class="block text-[var(--muted-foreground,#a0a0a0)] mb-1">Оператор мутации AIDE²:</label>
                  <select id="mut-operator" class="w-full px-2.5 py-1.5 rounded bg-[var(--card,#171717)] border border-[var(--border,#2a2a2a)] font-mono">
                    <option value="IMPROVE">IMPROVE (Улучшить ветку)</option>
                    <option value="FUSE">FUSE (Скрестить с идеей Шефа)</option>
                    <option value="PRUNE">PRUNE (Вычистить мёртвый код)</option>
                    <option value="DEBUG">DEBUG (Исправить баг)</option>
                  </select>
                </div>
                <div>
                  <label class="block text-[var(--muted-foreground,#a0a0a0)] mb-1">Гипотеза / Идея Шефа (запишется в KAG):</label>
                  <input id="mut-hypothesis" type="text" value="Оптимизация весов риска из Веб-Админки v4.0" class="w-full px-2.5 py-1.5 rounded bg-[var(--card,#171717)] border border-[var(--border,#2a2a2a)]" />
                </div>
              </div>

              <textarea id="mut-code-editor" rows="7" oninput="previewCodeMutationImpact()" class="w-full p-2.5 rounded bg-[var(--card,#171717)] border border-[var(--border,#2a2a2a)] font-mono text-xs"></textarea>

              <!-- Live Pre-Flight AI Impact Preview for edited code -->
              <div id="mut-impact-preview" class="p-2.5 rounded bg-[var(--card,#171717)] border border-[var(--border,#2a2a2a)] text-[var(--muted-foreground,#a0a0a0)]"></div>

              <button onclick="submitLiveNodeMutation()" class="w-full py-2 font-bold comp-btn-primary">
                ▶️ Прогнать код через Коллегию 3 Судей (Public + Held-Out) и сохранить новый узел в БД
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- ================================================================= -->
      <!-- PAGE 3: 🗣️ ДЕБАТЫ СОВЕТА (РАУНДЫ 1-3) & ЛОГИ РАССУЖДЕНИЙ АГЕНТОВ  -->
      <!-- ================================================================= -->
      <section id="page-debates" class="hidden space-y-4">
        <!-- Top AI Debate Launcher (Interactive!) -->
        <div class="comp-surface p-4 space-y-3 text-xs">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h2 class="text-base font-bold">🗣️ Созвать Новый Изолированный Совет Отделов (`True Isolated Council v2.1`)</h2>
              <p class="text-[var(--muted-foreground,#a0a0a0)]">
                Впишите любую архитектурную задачу и свой проверочный вопрос — отделы проведут слепой Раунд 1, перекрёстную атаку `Member A..E` в Раунде 2 и голосование `2/3`!
              </p>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-12 gap-2">
            <input id="deb-new-topic" type="text" placeholder="Тема дебатов (например: Как ускорить фильтрацию скилов без потери точности?)" value="Автоматическая генерация Python-скриптов верификации для текстовых скилов" class="md:col-span-5 px-3 py-2 rounded bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)]" />
            <input id="deb-new-question" type="text" placeholder="Острый вопрос Шефа для атаки предпосылок..." value="Как гарантировать, что сгенерированный скрипт не содержит бесконечных циклов и уязвимостей?" class="md:col-span-5 px-3 py-2 rounded bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)]" />
            <button onclick="launchNewCouncilDebate()" class="md:col-span-2 px-3 py-2 font-bold comp-btn-primary">
              🗣️ Запустить Совет
            </button>
          </div>
        </div>

        <!-- Debate Session Selector + Filter by Agent -->
        <div class="comp-surface p-4 space-y-4 text-xs">
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border,#2a2a2a)] pb-3">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="font-bold">📜 Выберите протокол дебатов:</span>
              <select id="deb-session-select" onchange="renderDebatesPage()" class="px-3 py-1.5 rounded bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] font-mono"></select>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
              <span>Фильтр по агенту:</span>
              <select id="deb-agent-filter" onchange="renderDebatesPage()" class="px-3 py-1.5 rounded bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] font-mono">
                <option value="ALL">Все 8 агентов роя</option>
                <option value="autopilot_planner">autopilot_planner (ALPHA_ARCHITECT)</option>
                <option value="strict_judge">strict_judge (BETA_SKEPTIC / IOTA)</option>
                <option value="backend_specialist">backend_specialist (DELTA / TORVALDS)</option>
                <option value="worker">worker (ETA_BACKEND_DEV)</option>
                <option value="research_analyst">research_analyst (PHYSICIST)</option>
                <option value="frontend_designer">frontend_designer (GAMMA_UX)</option>
                <option value="devops_sre">devops_sre (THETA_DEVOPS)</option>
                <option value="memory_auditor">memory_auditor (OMEGA_SYNTHESIZER)</option>
              </select>
            </div>
          </div>

          <!-- Stage 0 Epistemic Gateway + OMEGA Synthesis Summary -->
          <div id="deb-summary-header" class="p-3.5 rounded-lg bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] space-y-2"></div>

          <!-- Round 1: Individual Agent Reasoning Logs (Chain-of-Thought) -->
          <div class="space-y-2">
            <h3 class="text-sm font-bold text-[#40be96]">🧠 Раунд 1 (Blind-First): Логи Рассуждений Каждого Агента (Цепочки мыслей `[FACT]`, `[INFERENCE]`, `[ASSUMPTION]`)</h3>
            <div id="deb-reasoning-grid" class="grid grid-cols-1 md:grid-cols-2 gap-3"></div>
          </div>

          <!-- Round 2: Anonymized Cross-Examination (How they argued!) -->
          <div class="space-y-2 pt-2 border-t border-[var(--border,#2a2a2a)]">
            <h3 class="text-sm font-bold text-[#c07e22]">⚔️ Раунд 2 (Anonymized Cross-Examination): Лог Споров — Как Участники `Member A..E` Атаковали Друг Друга</h3>
            <div id="deb-cross-list" class="space-y-2.5"></div>
          </div>

          <!-- Round 3: Fractal Drilling L1-L5 & Confidence-Weighted 2/3 Vote Tally -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 pt-2 border-t border-[var(--border,#2a2a2a)]">
            <div class="space-y-2">
              <h3 class="text-sm font-bold">🌀 Фрактальное Бурение Горизонтов (`L1–L5`)</h3>
              <div id="deb-horizons-list" class="space-y-1.5"></div>
            </div>
            <div class="space-y-2">
              <h3 class="text-sm font-bold">🗳️ Раунд 3: Взвешенное Голосование (`2/3 Tally`, вес `1.5×` у профильного отдела)</h3>
              <div id="deb-votes-list" class="space-y-1.5"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- ================================================================= -->
      <!-- PAGE 4: ⚖️ КОЛЛЕГИЯ ИЗ 3 СУДЕЙ & ЖУРНАЛ ВЕРДИКТОВ                 -->
      <!-- ================================================================= -->
      <section id="page-judges" class="hidden space-y-4">
        <!-- Architecture Explanation: Single Judge vs Collegium of 3 Judges -->
        <div class="comp-surface p-4 space-y-3 text-xs">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <h2 class="text-base font-bold">⚖️ Как устроен Суд в системе: Коллегия из 3 Специализированных Судей + Детерминированный Hard Gate</h2>
            <span class="px-2.5 py-1 rounded font-mono bg-[var(--background,#0f0f0f)] border border-[#40be96] text-[#40be96]">
              Порог принятия: 2/3 взвешенных голосов без ВЕТО
            </span>
          </div>
          <p class="text-[var(--muted-foreground,#a0a0a0)]">
            Чтобы исключить ошибку или галлюцинацию одной модели, вместо одного судьи каждое решение проверяет <b>Коллегия из 3 независимых судей</b>:
          </p>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div class="p-3 rounded-lg bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] space-y-1">
              <div class="font-bold text-[#e5735b]">🛡️ Судья №1: SpecGuard Tribunal (Вес 1.5× · ПРАВО ВЕТО)</div>
              <div class="text-[var(--muted-foreground,#a0a0a0)]">
                Детерминированный технический судья: прогоняет код на открытом (Public) и секретном (Held-Out Private) контурах. Если разрыв <code>Δ &gt; 0.18</code> или найден эксплойт <code>sys.exit(0)</code> — накладывает <b>абсолютное вето (DEALBREAKER)</b>.
              </div>
            </div>
            <div class="p-3 rounded-lg bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] space-y-1">
              <div class="font-bold text-[#40be96]">📜 Судья №2: IOTA Strict Judge (Вес 1.5× · ПРАВО ВЕТО)</div>
              <div class="text-[var(--muted-foreground,#a0a0a0)]">
                Конституционный судья (агент <code>strict_judge</code>): проверяет наличие замка памяти <code>RECALL_ID</code> (без него — <b>0 баллов и вето</b>), соблюдение всех 6 директив Шефа <code>00_BOSS_FEEDBACK.md</code> и безопасность <code>skill_scan.py</code>.
              </div>
            </div>
            <div class="p-3 rounded-lg bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] space-y-1">
              <div class="font-bold text-[#4b87f0]">✂️ Судья №3: OMEGA Pareto Arbiter (Вес 1.0× · Чистота и КПД)</div>
              <div class="text-[var(--muted-foreground,#a0a0a0)]">
                Судья Парето-эффективности (<code>memory_auditor</code> + <code>bloat_pruner</code>): проверяет отсутствие мёртвых функций, лишних <code>import</code> и цикломатическую сложность. Требует очистки <code>PRUNE</code> при раздувании кода.
              </div>
            </div>
          </div>
        </div>

        <!-- Boss Action Bar: Issue Praise / Remark (New Directive) / Scold directly to hive_mind.db -->
        <div class="comp-surface p-4 space-y-3 text-xs">
          <h3 class="text-sm font-bold">👑 Прямой Вердикт Шефа (Наградить агента или создать новую Директиву в `00_BOSS_FEEDBACK.md`)</h3>
          <div class="grid grid-cols-1 md:grid-cols-12 gap-2">
            <select id="boss-fb-agent" class="md:col-span-3 px-2.5 py-2 rounded bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)] font-mono">
              <option value="frontend_designer">frontend_designer (Дизайн)</option>
              <option value="backend_specialist">backend_specialist (Бэкенд)</option>
              <option value="worker">worker (Инженер)</option>
              <option value="autopilot_planner">autopilot_planner (Архитектор)</option>
              <option value="strict_judge">strict_judge (Судья IOTA)</option>
              <option value="research_analyst">research_analyst (Аналитик)</option>
              <option value="devops_sre">devops_sre (DevOps)</option>
              <option value="memory_auditor">memory_auditor (Судья OMEGA)</option>
            </select>
            <select id="boss-fb-type" class="md:col-span-3 px-2.5 py-2 rounded bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)]">
              <option value="praise">👍 Похвала (+15 к рейтингу агента)</option>
              <option value="remark">⚠️ Замечание (0 баллов + новая директива DIR)</option>
              <option value="scold">👎 Разнос (-25 баллов + жёсткая директива DIR)</option>
            </select>
            <input id="boss-fb-comment" type="text" placeholder="Текст приказа или оценки Шефа (запишется в БД и 00_BOSS_FEEDBACK.md)..." class="md:col-span-4 px-3 py-2 rounded bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)]" />
            <button onclick="submitBossFeedback()" class="md:col-span-2 px-3 py-2 font-bold comp-btn-primary">
              ⚡ Вынести приказ
            </button>
          </div>
        </div>

        <!-- Collegium Verdicts Log Filter & Cards -->
        <div class="comp-surface p-4 space-y-3 text-xs">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <h3 class="text-sm font-bold">📋 Полный Журнал Решений Коллегии 3 Судей (Узлы RSI + Задачи Hive Mind)</h3>
            <select id="judges-filter" onchange="renderJudgesPage()" class="px-3 py-1.5 rounded bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)]">
              <option value="ALL">Все вердикты Коллегии</option>
              <option value="VETO">🚨 Только заблокированные ВЕТО (DEALBREAKER)</option>
              <option value="RSI_NODE">🌳 Только узлы дерева AIDE²</option>
              <option value="HIVE_TASK">🐝 Только задачи агентов Hive Mind</option>
            </select>
          </div>
          <div id="collegium-verdicts-list" class="space-y-3"></div>
        </div>
      </section>

      <!-- ================================================================= -->
      <!-- PAGE 5: 🧬 СТУДИЯ И ИИ-РЕДАКТОР 30 СКИЛОВ (SKILLFORGE)            -->
      <!-- ================================================================= -->
      <section id="page-skills" class="hidden grid grid-cols-1 lg:grid-cols-12 gap-4">
        <div class="lg:col-span-7 comp-surface p-4 space-y-3 text-xs">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <h2 class="text-base font-bold">🧬 Каталог 30 Скилов Системы (Кликните для редактирования и ИИ-прокачки)</h2>
            <span id="sk-count-badge" class="font-mono px-2 py-0.5 rounded bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)]">30 скилов</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <input id="sk-search" type="text" oninput="renderSkillsPage()" placeholder="Поиск скила..." class="px-2.5 py-1.5 rounded bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)]" />
            <select id="sk-cat" onchange="renderSkillsPage()" class="px-2.5 py-1.5 rounded bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)]">
              <option value="ALL">Все 30 скилов</option>
              <option value="NEW_RSI">🔥 5 новых RSI-скилов</option>
              <option value="WITH_SCRIPTS">⚙️ Со скриптами в scripts/</option>
              <option value="TEXT_ONLY">📝 Без скриптов (Кандидаты на прокачку)</option>
            </select>
            <select id="sk-sort" onchange="renderSkillsPage()" class="px-2.5 py-1.5 rounded bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)]">
              <option value="fitness_desc">Сортировка: Fitness ↓</option>
              <option value="tokens_desc">Самые раздутые по токенам ↓</option>
              <option value="pareto_desc">КПД на 1k токенов ↓</option>
            </select>
          </div>
          <div class="overflow-x-auto max-h-[460px] border border-[var(--border,#2a2a2a)] rounded-lg">
            <table class="w-full text-left border-collapse">
              <thead class="sticky top-0 bg-[var(--card,#171717)] border-b border-[var(--border,#2a2a2a)] text-[var(--muted-foreground,#a0a0a0)]">
                <tr>
                  <th class="py-2 px-2.5">Скил</th>
                  <th class="py-2 px-2">Пр-т</th>
                  <th class="py-2 px-2">Скрипты</th>
                  <th class="py-2 px-2">Токены</th>
                  <th class="py-2 px-2">Fitness</th>
                </tr>
              </thead>
              <tbody id="sk-tbody" class="divide-y divide-[var(--border,#2a2a2a)]"></tbody>
            </table>
          </div>
        </div>

        <!-- Right 5 cols: Interactive Skill Optimizer & What-If Simulator -->
        <div id="sk-editor-card" class="lg:col-span-5 comp-surface p-4 space-y-3 text-xs">
          <div class="border-b border-[var(--border,#2a2a2a)] pb-2.5 flex items-center justify-between">
            <div>
              <div class="text-[var(--muted-foreground,#a0a0a0)]">ИИ-Оптимизатор Скила (`SkillForge`)</div>
              <h3 class="text-base font-bold font-mono mt-0.5" id="sk-ed-name">aide-tree-explorer</h3>
            </div>
            <span id="sk-ed-score" class="px-2.5 py-1 font-bold comp-btn-primary">89.3 / 100</span>
          </div>

          <div id="sk-ed-bars" class="space-y-2"></div>

          <div class="p-3 rounded-lg bg-[var(--background,#0f0f0f)] border border-[#006B4F] space-y-2">
            <div class="font-bold text-[#40be96]">🤖 ИИ-Действия над выбранным скилом (Что изменится):</div>
            <div id="sk-ed-whatif" class="text-[var(--muted-foreground,#a0a0a0)]"></div>
            <div class="flex flex-wrap gap-2 pt-1">
              <button onclick="simulateSkillUpgrade('compress')" class="px-3 py-1.5 font-bold comp-btn-primary">
                ✂️ ИИ-Сжатие промпта AIDE² (-18% токенов)
              </button>
              <button onclick="simulateSkillUpgrade('add_script')" class="px-3 py-1.5 font-medium comp-btn-outline">
                ⚙️ Добавить Python-скрипт проверки (+25 Детерминизм)
              </button>
            </div>
          </div>

          <div class="space-y-1">
            <div class="font-bold">💡 Рекомендации аудитора `SkillForge`:</div>
            <ul id="sk-ed-suggestions" class="list-disc pl-4 space-y-1 text-[var(--muted-foreground,#a0a0a0)]"></ul>
          </div>
        </div>
      </section>

      <!-- ================================================================= -->
      <!-- PAGE 6: 📖 ИНТЕРАКТИВНЫЙ ХЕЛП & КАРТА «ЧТО ГДЕ МЕНЯТЬ»            -->
      <!-- ================================================================= -->
      <section id="page-help" class="hidden space-y-4 text-xs">
        <div class="comp-surface p-5 space-y-4">
          <h2 class="text-lg font-bold text-[#40be96]">📖 Полный Путеводитель по Многостраничной ИИ-Админке v4.0 («На пальцах»)</h2>
          <p class="text-[var(--muted-foreground,#a0a0a0)]">
            Эта таблица отвечает на главный вопрос: <b>«Что именно я могу здесь менять, на какой странице это находится и к чему приведёт каждое действие?»</b>
          </p>

          <div class="overflow-x-auto border border-[var(--border,#2a2a2a)] rounded-lg">
            <table class="w-full text-left border-collapse">
              <thead class="bg-[var(--background,#0f0f0f)] border-b border-[var(--border,#2a2a2a)]">
                <tr>
                  <th class="p-3">Ваша цель (Что вы хотите сделать)</th>
                  <th class="p-3">На какую страницу перейти</th>
                  <th class="p-3">Какую ручку / кнопку нажать</th>
                  <th class="p-3">К чему это приведёт в системе</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[var(--border,#2a2a2a)]">
                <tr>
                  <td class="p-3 font-bold">Защитить проект от читерства ИИ (подгонки под тесты)</td>
                  <td class="p-3"><button onclick="switchPage('dashboard')" class="underline text-[#40be96]">1. 🎛️ Пульт &amp; ИИ-Симулятор</button></td>
                  <td class="p-3">Ползунок <code>Порог анти-чита Δ</code> (поставить <code>0.15 – 0.18</code>)</td>
                  <td class="p-3">Судья №1 (`SpecGuard`) заблокирует любое решение, где секретный тест просел сильнее чем на 18% от открытого.</td>
                </tr>
                <tr>
                  <td class="p-3 font-bold">Отредактировать код узла или сжать мусор в коде</td>
                  <td class="p-3"><button onclick="switchPage('rsi')" class="underline text-[#40be96]">2. 🌳 Студия Дерева &amp; Кода</button></td>
                  <td class="p-3">Кнопка <code>✂️ ИИ: Сжать код (PRUNE)</code> → <code>▶️ Прогнать через Коллегию 3 Судей</code></td>
                  <td class="p-3">Код проверится на 24 тестах, очистится от мёртвых функций и запишется как новый узел в `rsi_evolution.db`.</td>
                </tr>
                <tr>
                  <td class="p-3 font-bold">Посмотреть, как агенты спорили и как мыслил каждый</td>
                  <td class="p-3"><button onclick="switchPage('debates')" class="underline text-[#40be96]">3. 🗣️ Дебаты &amp; Мышление</button></td>
                  <td class="p-3">Выбрать сессию `DEB-...` или нажать <code>🗣️ Запустить Совет</code></td>
                  <td class="p-3">Откроются цепочки рассуждений (`[FACT]`, `[INFERENCE]`) каждого из 8 агентов и диалоги перекрёстных атак Раунда 2.</td>
                </tr>
                <tr>
                  <td class="p-3 font-bold">Проверить лог Коллегии 3 Судей и наказать/похвалить агента</td>
                  <td class="p-3"><button onclick="switchPage('judges')" class="underline text-[#40be96]">4. ⚖️ Коллегия из 3 Судей</button></td>
                  <td class="p-3">Форма <code>👑 Прямой Вердикт Шефа</code> (`👍 Похвала` / `⚠️ Замечание` / `👎 Разнос`)</td>
                  <td class="p-3">Рейтинг агента изменится (`+15` / `-25`), а замечание/разнос автоматически станет новой директивой в `00_BOSS_FEEDBACK.md`.</td>
                </tr>
                <tr>
                  <td class="p-3 font-bold">Прокачать или сжать промпт любого из 30 скилов</td>
                  <td class="p-3"><button onclick="switchPage('skills')" class="underline text-[#40be96]">5. 🧬 Редактор 30 Скилов</button></td>
                  <td class="p-3">Кнопка <code>✂️ ИИ-Сжатие промпта AIDE²</code></td>
                  <td class="p-3">Удаляются вводные штампы без потери кода, снижается расход токенов и растёт `Fitness` скила.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

    </main>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE-OVER AI COPILOT DRAWER ("СПРОСИ ИИ-ШТУРМАНА")                   -->
  <!-- ===================================================================== -->
  <div id="ai-copilot-drawer" class="hidden fixed inset-y-0 right-0 z-50 w-full max-w-md bg-[var(--card,#171717)] border-l border-[var(--border,#2a2a2a)] shadow-2xl p-4 flex flex-col justify-between text-xs">
    <div class="space-y-3 overflow-y-auto pr-1">
      <div class="flex items-center justify-between border-b border-[var(--border,#2a2a2a)] pb-3">
        <div>
          <h3 class="text-sm font-bold text-[#40be96]">🤖 ИИ-Штурман Админки («На пальцах»)</h3>
          <div class="text-[var(--muted-foreground,#a0a0a0)]">Объясняет, что где менять и к чему это приведёт</div>
        </div>
        <button onclick="toggleAiDrawer()" class="px-2.5 py-1 comp-btn-outline">Закрыть ✕</button>
      </div>

      <div class="space-y-1.5">
        <div class="font-bold">Быстрые вопросы к ИИ-Штурману:</div>
        <button onclick="askAiCopilot('У нас одна судья или коллегия судей? Где смотреть их решения?')" class="w-full text-left p-2 comp-btn-outline">
          ⚖️ У нас одна судья или коллегия судей? Где смотреть их решения?
        </button>
        <button onclick="askAiCopilot('Где смотреть логи дебатов и рассуждений каждого агента?')" class="w-full text-left p-2 comp-btn-outline">
          🗣️ Где смотреть логи дебатов и рассуждений каждого агента?
        </button>
        <button onclick="askAiCopilot('Что именно я могу менять в админке и к чему это приведёт?')" class="w-full text-left p-2 comp-btn-outline">
          🎛️ Что именно я могу менять в админке и к чему это приведёт?
        </button>
      </div>

      <div id="ai-copilot-response" class="p-3.5 rounded-lg bg-[var(--background,#0f0f0f)] border border-[#006B4F] whitespace-pre-line leading-relaxed">
        Выберите вопрос выше или напишите свой ниже — ИИ-Штурман подробно разложит ответ по полочкам и даст прямую кнопку перехода на нужную страницу.
      </div>
    </div>

    <div class="pt-3 border-t border-[var(--border,#2a2a2a)] flex gap-2">
      <input id="ai-copilot-input" type="text" placeholder="Задайте любой вопрос по работе системы..." class="flex-1 px-3 py-2 rounded bg-[var(--background,#0f0f0f)] border border-[var(--border,#2a2a2a)]" />
      <button onclick="askAiCopilot(document.getElementById('ai-copilot-input').value)" class="px-3 py-2 font-bold comp-btn-primary">
        Спросить
      </button>
    </div>
  </div>
"""
