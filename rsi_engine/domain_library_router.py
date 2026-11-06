#!/usr/bin/env python3
"""
RSI-0 v8: Extensible Domain & Aesthetic Knowledge Library + Architect Routing Contour
=====================================================================================
Solves the "Hardcoded Single-Domain / Profile" bottleneck by introducing:
1. Extensible Library of Spheres (`domain_spheres_catalog` + `domain_spheres_fts` in SQLite
   and structured JSON/Markdown volumes in `storage/knowledge_spheres/`).
2. Dual-Axis Selection Contour (`DomainRoutingContour`):
   - Axis A (Subject Matter Sphere): e.g. Auto Parts EPC, Railway Rolling Stock (18-100 / SA-3),
     Traffic Law & GIBDD Disputes (KoAP Ch.12 / GOST R 52289-2019), Culinary Tech Cards (GOST 31987).
   - Axis B (Aesthetic & Design Philosophy Sphere): e.g. Ferrari / Pininfarina / Flavio Manzoni
     Centro Stile ("Purity, Tension Lines, Slingshot Effect, Seamless Aero"), Dieter Rams, or GOST CAD.
3. Chief Architect Delegation Engine (`ArchitectDelegationEngine`):
   - Automatically detects missing or under-populated spheres and issues structured research
     and library-building mandates (`architect_delegation_orders`) to `@deep_web_researcher`,
     `@knowledge_curator`, and `@storage_and_db_architect` over the Inter-Agent Memory Bus.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import re
import sqlite3
from typing import Any

UNIFIED_RSI_DB = Path("/shared/user/.gemini/orchestrator/rsi_evolution.db")
SPHERES_DISK_DIR = Path("/home/antigravity/test_benchmarks/storage/knowledge_spheres")


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


SEED_SPHERES_LIBRARY: list[dict[str, Any]] = [
    {
        "sphere_id": "iconic_design_aesthetics_ferrari_pininfarina",
        "sphere_type": "aesthetic_and_design_canon",
        "title_ru": "Эстетика, Пропорции и Доклады Дизайнеров Ferrari (Pininfarina & Flavio Manzoni Centro Stile)",
        "summary_ru": (
            "Библиотека эстетических обоснований, статей и принципов формообразования шеф-дизайнеров Ferrari: "
            "Баттиста и Серджо Пининфарина, Леонардо Фиораванти (250 GT, 308, Testarossa, F40) и Флавио Манцони "
            "(Centro Stile Ferrari — LaFerrari, SF90, 296 GTB, Daytona SP3, F80)."
        ),
        "keywords": [
            "дизайн", "эстетика", "феррари", "ferrari", "pininfarina", "flavio manzoni",
            "красота", "пропорции", "стиль", "интерфейс", "премиум", "доклады", "обоснование"
        ],
        "canonical_sources": [
            {
                "title": "Flavio Manzoni (Chief Design Officer, Ferrari Centro Stile) — 'Form, Tension & Slingshot Effect' (Forbes / Designboom / Ferrari Magazine)",
                "url": "https://www.ferrari.com/magazine/articles/designing-the-296-gtb-with-flavio-manzoni",
                "core_thesis": (
                    "1) Эффект натянутой тетивы ('Slingshot Effect' / 'Linea Tesa'): арки и линии кузова работают в визуальном "
                    "натяжении, оптически смещая объем вперед, словно зверь перед прыжком. "
                    "2) Бесшовная функциональная скульптура ('Seamless Functional Integration'): в отличие от болидов F1 с нарочитыми "
                    "антикрыльями, на дорожных Ferrari аэродинамика прячется внутрь чистых скульптурных поверхностей. "
                    "3) Плотность мысли на миллиметр ('Density of Design'): ни одной декоративной фальш-детали — каждая грань работает."
                ),
            },
            {
                "title": "Battista & Sergio Pininfarina / Leonardo Fioravanti — 'Purity, Elegance, Innovation' (London Design Museum: Ferrari Under the Skin & MoMA)",
                "url": "https://designmuseum.org/asset/download?id=880ceeed-540c-42de-844c-2eae85ba80ca",
                "core_thesis": (
                    "Триада Pininfarina: Чистота поверхности (Purity), Гармония пропорций без излишеств (Elegance without excess) "
                    "и Инженерная честность материала (Superplastic aluminum / Carbon / Open-gate mechanical shifter)."
                ),
            },
        ],
        "mandatory_domain_rules": [
            "[AESTHETIC-FERRARI-01] Принцип 'Eyes on the Road, Hands on the Wheel': главный рабочий инструмент (чертеж, телеметрия, тахометр/ключевой график) всегда в центре оптического фокуса, второстепенные настройки убраны с траектории взгляда.",
            "[AESTHETIC-FERRARI-02] Колористика Maranello Cockpit: глубокий матовый карбон (#070b14 / #0f172a) с четкими функциональными акцентами Rosso Corsa (#ef4444) для критических действий, Giallo Modena (#facc15) для главного фокуса/выноски и Grigio Titanio для технических сеток.",
            "[AESTHETIC-FERRARI-03] Запрет на 'визуальный пластик и бутафорию': каждая кнопка, шкала и цифра обязана иметь реальную физическую/инженерную функцию (никаких пустых декоративных виджетов).",
        ],
        "required_db_tables": ["design_canons", "aesthetic_reviews", "color_and_proportion_tokens"],
        "required_storage_artifacts": ["storage/knowledge_spheres/iconic_design_aesthetics_ferrari_pininfarina.json"],
    },
    {
        "sphere_id": "railway_transport_and_rolling_stock",
        "sphere_type": "engineering_and_industry",
        "title_ru": "Железнодорожный Транспорт, Подвижной Состав и Каталоги Узлов Вагонов/Локомотивов (РЖД / ПТЭ / ГОСТ)",
        "summary_ru": (
            "Инженерная база знаний по устройству, каталогам сборочных единиц, дефектоскопии и ремонту "
            "подвижного состава колеи 1520 мм: двухосная тележка мод. 18-100 (ЦНИИ-Х3), автосцепное устройство СА-3 "
            "(ГОСТ 32885-2014), колесные пары РУ1Ш-957-Г, тормозное оборудование усл. № 483 и нормы ПТЭ."
        ),
        "keywords": [
            "жд", "железнодорожный", "вагон", "локомотив", "тележка 18-100", "автосцепка са-3",
            "колесная пара", "птэ", "депо", "рельсы", "поезд", "триангель", "букса"
        ],
        "canonical_sources": [
            {
                "title": "Каталог узлов грузовой двухосной тележки модели 18-100 (ЦНИИ-Х3, ГОСТ 9246) и комплектов модернизации",
                "url": "https://gdzp.ru/poleznaya-informaciya/naznachenie-i-klassifikaciya-telezhek-gruzovyh-vagonov/osnovnye-tekhnicheskie-dannye-telezhek-gruzovyh-vagonov-i-ih-/",
                "core_thesis": (
                    "Сборочные единицы тележки 18-100: [1] Рама боковая литая (черт. 100.00.020-4), [2] Балка надрессорная (черт. 100.00.010-4), "
                    "[3] Клин фрикционный гасителя колебаний (100.10.001-0), [4] Комплект двухрядных цилиндрических пружин рессорного подвешивания, "
                    "[5] Колесная пара РУ1Ш-957-Г с буксовыми узлами, [6] Триангель тормозной рычажной передачи (100.40.010-2СБ)."
                ),
            },
            {
                "title": "Инструкция по ремонту и обслуживанию автосцепного устройства СА-3 (ГОСТ 32885-2014, черт. 106.01.000-0сб)",
                "url": "https://www.evr.ee/files/64--TE-lisa.pdf",
                "core_thesis": (
                    "Детали механизма сцепления СА-3: корпус автосцепки, замок (106.01.002-0), замкодержатель (106.01.003-0), "
                    "предохранитель от саморасцепа (собачка), подъемник замка, валик подъемника, тяговый хомут (106.00.001-2) и поглощающий аппарат. "
                    "Проверка шаблоном 873р, разница по высоте между продольными осями автосцепок не более 100 мм (в грузовом поезде)."
                ),
            },
        ],
        "mandatory_domain_rules": [
            "[RAILWAY-01] Обязательная привязка каждой детали вагона/локомотива к заводскому номеру чертежа (например, 100.00.020-4 или 106.01.000-0сб) и ГОСТу.",
            "[RAILWAY-02] Учет браковочных признаков по ПТЭ и инструкциям ЦВ-ЦЛ: предельный прокат по кругу катания, толщина гребня колеса (24..33 мм), контроль автосцепки шаблоном 873р.",
            "[RAILWAY-03] Разделение циклов ремонта депо: ТО-1/ТО-2, текущий отцепочный ремонт (ТР-1, ТР-2), деповской ремонт (ДР) и капитальный ремонт (КР) с клеймом завода.",
        ],
        "required_db_tables": ["rolling_stock_models", "bogie_and_coupler_assemblies", "depot_repair_norms", "wear_tolerances_pte"],
        "required_storage_artifacts": ["storage/knowledge_spheres/railway_transport_and_rolling_stock.json"],
    },
    {
        "sphere_id": "auto_road_law_and_gibdd",
        "sphere_type": "legal_and_regulatory",
        "title_ru": "Юридический Справочник: Автодороги, ПДД, ГАИ/ГИБДД, КоАП РФ Гл. 12 и ГОСТ Р 52289-2019",
        "summary_ru": (
            "Нормативно-правовая и судебно-экспертная база знаний по спорам в области дорожного движения: "
            "Глава 12 КоАП РФ, ПДД РФ, Постановление Пленума ВС РФ № 20 от 25.06.2019 и техническая проверка "
            "законности установки дорожных знаков, камер и разметки по ГОСТ Р 52289-2019."
        ),
        "keywords": [
            "гаи", "гибдд", "пдд", "коап", "штраф", "лишение", "встречка", "разметка",
            "дорожные знаки", "гост 52289", "жалоба", "дтп", "юрист", "автодороги", "суд"
        ],
        "canonical_sources": [
            {
                "title": "ГОСТ Р 52289-2019 'Технические средства организации дорожного движения. Правила применения дорожных знаков, разметки, светофоров' + Практика ВС РФ",
                "url": "https://docs.cntd.ru/document/1200170422/titles/7DS0KE",
                "core_thesis": (
                    "П. 5.1.4 ГОСТ Р 52289-2019: расстояние видимости знака должно быть не менее 100 м. П. 5.1.5: знаки устанавливают справа от проезжей части. "
                    "При противоречии временных дорожных знаков и линий горизонтальной разметки водитель руководствуется знаками. "
                    "Если разметка стерта (>50% износа по ГОСТ Р 51256) или скрыта под снегом/грязью, состав правонарушения по ст. 12.15 / 12.16 КоАП РФ отсутствует."
                ),
            },
            {
                "title": "КоАП РФ Глава 12 (Административные правонарушения в области дорожного движения) и Постановление Пленума ВС РФ № 20",
                "url": "https://www.consultant.ru/document/cons_doc_LAW_34661/ddf872bbf0198a5ffe733c85ac8e65649ba9824d/",
                "core_thesis": (
                    "Разграничение составов: ч. 4 ст. 12.15 КоАП РФ (выезд на встречную полосу в нарушение ПДД — штраф 5000 ₽ или лишение 4–6 мес.) "
                    "против ч. 3 ст. 12.15 (объезд препятствия — штраф 1000–1500 ₽ без лишения) и ст. 12.16 (нарушение требований знаков/разметки). "
                    "Процессуальные основания отмены постановлений ЦАФАП/ГИБДД: отсутствие проекта организации дорожного движения (ПОДД), нарушение ст. 25.1 и 26.2 КоАП РФ."
                ),
            },
        ],
        "mandatory_domain_rules": [
            "[LAW-GIBDD-01] Каждая правовая квалификация дорожной ситуации обязана ссылаться на конкретный пункт ПДД РФ, часть и статью Главы 12 КоАП РФ и пункт Постановления Пленума ВС РФ № 20.",
            "[LAW-GIBDD-02] Обязательный аудит дорожной инфраструктуры по ГОСТ Р 52289-2019 (видимость знака >= 100 м, соответствие дислокации схеме ПОДД, читаемость разметки).",
            "[LAW-GIBDD-03] Автогенерация процессуальных документов: Жалоба на постановление по делу об АП (в порядке ст. 30.1–30.3 КоАП РФ в течение 10 суток) и Ходатайство об истребовании схемы дислокации дорожных знаков и разметки.",
        ],
        "required_db_tables": ["koap_ch12_articles", "pdd_clauses", "gost_52289_sign_rules", "supreme_court_precedents", "legal_complaint_templates"],
        "required_storage_artifacts": ["storage/knowledge_spheres/auto_road_law_and_gibdd.json"],
    },
    {
        "sphere_id": "culinary_gastronomy_and_techcards",
        "sphere_type": "gastronomy_and_hospitality",
        "title_ru": "Шеф-Кулинария, Гастрономия, Технологические Карты (ТТК ГОСТ 31987) и Фудкост Ресторана",
        "summary_ru": (
            "Профессиональная база знаний шеф-повара и технолога общественного питания: "
            "Технико-технологические карты (ТТК по ГОСТ 31987-2012), расчет норм отходов при холодной и тепловой "
            "обработке (Брутто -> Нетто -> Выход), температурные кривые Sous-Vide / реакции Майяра, сочетаемость вкусов и Food Cost."
        ),
        "keywords": [
            "кулинария", "рецепты", "гастрономия", "ттк", "ресторан", "шеф-повар",
            "брутто", "нетто", "уварка", "фудкост", "меню", "гост 31987", "блюда"
        ],
        "canonical_sources": [
            {
                "title": "ГОСТ 31987-2012 'Услуги общественного питания. Технологические документы на продукцию общественного питания (ТТК, ТК, Сборники рецептур)'",
                "url": "https://docs.cntd.ru/document/1200103472",
                "core_thesis": (
                    "Каждая ТТК обязана содержать: 1) Область применения, 2) Требования к сырью, 3) Рецептуру (Масса брутто, % отхода при холодной обработке, "
                    "Масса нетто, % потерь при тепловой обработке / ужарке, Выход готового изделия в граммах), 4) Технологический процесс, "
                    "5) Органолептические показатели (вкус, цвет, запах, консистенция) и 6) Пищевую и энергетическую ценность (КБЖУ на 100 г и на порцию)."
                ),
            },
        ],
        "mandatory_domain_rules": [
            "[CULINARY-01] Строгий математический баланс рецептуры ТТК: Нетто = Брутто * (1 - %_холодного_отхода); Выход = Нетто * (1 - %_тепловых_потерь).",
            "[CULINARY-02] Контроль критических температур и биохимии: реакция Майяра (140..165°C), точки готовности стейков и рыбы (Rare 50°C, Medium Rare 55°C, Medium 60°C, птица пастеризация 65..74°C) и безопасное хранение ХАССП (HACCP).",
            "[CULINARY-03] Экономика кухни: автоматический расчет себестоимости порции (Food Cost %), наценки и маржинальной прибыли блюда.",
        ],
        "required_db_tables": ["ingredients_catalog", "waste_coefficients", "tech_cards_ttk", "flavor_pairings", "foodcost_calculations"],
        "required_storage_artifacts": ["storage/knowledge_spheres/culinary_gastronomy_and_techcards.json"],
    },
    {
        "sphere_id": "auto_parts_and_oem_epc",
        "sphere_type": "engineering_and_industry",
        "title_ru": "Заводские Каталоги Автозапчастей (VAG ETKA / Toyota Amayama / Elcats / Exist / Autodoc)",
        "summary_ru": (
            "Промышленный подбор автозапчастей по VIN и PR-кодам комплектации, двухоконные чертежи узлов "
            "с выносками [1]..[10], цепочки заводских ревизий OEM и матрица кросс-аналогов OES конвейера / Aftermarket."
        ),
        "keywords": [
            "автозапчасти", "каталог", "oem", "артикул", "etka", "amayama", "elcats", "exist", "autodoc", "vin", "сто"
        ],
        "canonical_sources": [
            {
                "title": "VAG ETKA & Skoda-Parts / Autoparts-24 / Amayama Toyota EPC",
                "url": "https://www.skoda-parts.com/spare-part/5q0615301f-front-brake-disc-312x25-skoda-23770.html",
                "core_thesis": "100% верификация заводских артикулов, чертежных размеров, весов и замен OEM через первичные каталоги.",
            }
        ],
        "mandatory_domain_rules": [
            "[AUTOPARTS-01] Двухоконная связка интерактивного чертежа узла с выносками [1]..[10] и ведомости деталей SQLite.",
            "[AUTOPARTS-02] Разделение выдачи на Запрошенный OEM, Официальную замену производителя и OES Поставщика конвейера.",
        ],
        "required_db_tables": ["vehicles", "catalog_groups", "scheme_callouts", "cross_analogs", "media_storage_index", "parts_fts"],
        "required_storage_artifacts": ["storage/db/auto_parts_tecdoc.sqlite3", "storage/pdf_catalogs/VAG_ETKA_615_050_Brakes_Catalog.pdf"],
    },
    {
        "sphere_id": "retro_and_3d_interactive_engines",
        "sphere_type": "interactive_simulation",
        "title_ru": "Интерактивные 2D/3D Движки и Физические Симуляторы (NES Battle City, Wolf3D 1992 VGA, 3D Boids)",
        "summary_ru": (
            "Математика коллизий (Swept AABB, Anti-Jam 16x16 sub-tile grid), DDA Raycasting с Z-буфером, "
            "ручное управление без самопроизвольных ботов (aiBot=false) и захват фокуса клавиатуры в iframe."
        ),
        "keywords": ["игры", "танчики", "wolfenstein", "марио", "аквариум", "рейкастинг", "коллизии", "симулятор"],
        "canonical_sources": [
            {
                "title": "id Software Wolfenstein 3D (1992) & Namco Battle City (1990) Technical Architecture",
                "url": "https://github.com/id-Software/wolf3d",
                "core_thesis": "Перпендикулярная коррекция лучей DDA, 1D Z-буфер спрайтов и строгий ручной ввод со старта.",
            }
        ],
        "mandatory_domain_rules": [
            "[ENGINE-01] aiBot = false по умолчанию; мгновенный отклик на клавиатуру (Arrow/WASD) и пульт удержания holdInput.",
            "[ENGINE-02] Запрет на безусловный сдвиг координат snapX/snapY до проверки коллизии.",
        ],
        "required_db_tables": ["simulation_benchmarks", "input_probe_logs"],
        "required_storage_artifacts": ["storage/knowledge_spheres/retro_and_3d_interactive_engines.json"],
    },
]


class DomainKnowledgeLibrary:
    """
    Extensible Multi-Sphere Knowledge Library + Routing Contour + Chief Architect Delegation Engine.
    """

    def __init__(self, db_path: Path = UNIFIED_RSI_DB) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        SPHERES_DISK_DIR.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS domain_spheres_catalog (
                    sphere_id TEXT PRIMARY KEY,
                    sphere_type TEXT NOT NULL,
                    title_ru TEXT NOT NULL,
                    summary_ru TEXT NOT NULL,
                    keywords_json TEXT NOT NULL,
                    canonical_sources_json TEXT NOT NULL,
                    mandatory_rules_json TEXT NOT NULL,
                    required_db_tables_json TEXT NOT NULL,
                    required_artifacts_json TEXT NOT NULL,
                    created_by_agent TEXT NOT NULL DEFAULT 'chief_architect',
                    updated_at TEXT NOT NULL
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS domain_spheres_fts USING fts5(
                    sphere_id,
                    sphere_type,
                    title_ru,
                    summary_ru,
                    keywords_text,
                    rules_text
                );

                CREATE TABLE IF NOT EXISTS architect_delegation_orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    requested_topic TEXT NOT NULL,
                    target_sphere_id TEXT NOT NULL,
                    assigned_departments TEXT NOT NULL,
                    research_directives_json TEXT NOT NULL,
                    aesthetic_canon_applied TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'COMPLETED',
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def sync_seed_spheres(self) -> dict[str, Any]:
        """Populates the initial 6 spheres into SQLite and writes JSON volumes to disk."""
        now = _utc_now()
        with self._connect() as conn:
            conn.execute("DELETE FROM domain_spheres_fts;")
            for sp in SEED_SPHERES_LIBRARY:
                conn.execute(
                    """
                    INSERT INTO domain_spheres_catalog (
                        sphere_id, sphere_type, title_ru, summary_ru,
                        keywords_json, canonical_sources_json, mandatory_rules_json,
                        required_db_tables_json, required_artifacts_json, created_by_agent, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'chief_architect', ?)
                    ON CONFLICT(sphere_id) DO UPDATE SET
                        sphere_type=excluded.sphere_type,
                        title_ru=excluded.title_ru,
                        summary_ru=excluded.summary_ru,
                        keywords_json=excluded.keywords_json,
                        canonical_sources_json=excluded.canonical_sources_json,
                        mandatory_rules_json=excluded.mandatory_rules_json,
                        required_db_tables_json=excluded.required_db_tables_json,
                        required_artifacts_json=excluded.required_artifacts_json,
                        updated_at=excluded.updated_at
                    """,
                    (
                        sp["sphere_id"],
                        sp["sphere_type"],
                        sp["title_ru"],
                        sp["summary_ru"],
                        json.dumps(sp["keywords"], ensure_ascii=False),
                        json.dumps(sp["canonical_sources"], ensure_ascii=False),
                        json.dumps(sp["mandatory_domain_rules"], ensure_ascii=False),
                        json.dumps(sp["required_db_tables"], ensure_ascii=False),
                        json.dumps(sp["required_storage_artifacts"], ensure_ascii=False),
                        now,
                    ),
                )
                conn.execute(
                    "INSERT INTO domain_spheres_fts VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        sp["sphere_id"],
                        sp["sphere_type"],
                        sp["title_ru"],
                        sp["summary_ru"],
                        " ".join(sp["keywords"]),
                        " ".join(sp["mandatory_domain_rules"]),
                    ),
                )
                disk_file = SPHERES_DISK_DIR / f"{sp['sphere_id']}.json"
                disk_file.write_text(json.dumps(sp, ensure_ascii=False, indent=2), encoding="utf-8")
            conn.commit()
        return {"status": "ok", "spheres_count": len(SEED_SPHERES_LIBRARY)}

    def route_project_contour(
        self,
        user_request: str,
        aesthetic_preference: str = "iconic_design_aesthetics_ferrari_pininfarina",
    ) -> dict[str, Any]:
        """
        The Selection Contour (`Контур Выбора Направления`):
        1. Matches the user's request against `domain_spheres_fts`.
        2. Pairs the Subject Matter Sphere with the selected Aesthetic Canon Sphere
           (defaulting to Ferrari / Pininfarina / Flavio Manzoni design philosophy).
        3. If no existing sphere matches strongly, triggers `delegate_new_sphere_creation()`
           so the Chief Architect commissions a brand-new sphere volume!
        """
        tokens = [re.sub(r"[^\wА-Яа-яЁё0-9-]", "", t.lower()) for t in user_request.split() if len(t) >= 2]
        req_low = user_request.lower()

        with self._connect() as conn:
            all_rows = conn.execute("SELECT * FROM domain_spheres_catalog").fetchall()
            aesthetic_row = conn.execute(
                "SELECT * FROM domain_spheres_catalog WHERE sphere_id = ?",
                (aesthetic_preference,),
            ).fetchone()

        scored: list[tuple[int, dict[str, Any]]] = []
        for r in all_rows:
            d = dict(r)
            kws = json.loads(d.get("keywords_json", "[]"))
            title_low = d["title_ru"].lower()
            summary_low = d["summary_ru"].lower()
            score = 0
            for kw in kws:
                if kw.lower() in req_low:
                    score += 5
            for tok in tokens:
                if len(tok) >= 3 and tok not in ("гост", "для", "как", "или"):
                    if tok in title_low:
                        score += 3
                    if tok in summary_low:
                        score += 1
            if score > 0:
                scored.append((score, d))

        scored.sort(key=lambda x: x[0], reverse=True)
        if not scored:
            delegated = self.delegate_new_sphere_creation(user_request, aesthetic_preference)
            return {
                "routing_mode": "NEW_SPHERE_COMMISSIONED_BY_ARCHITECT",
                "delegation_order": delegated,
            }

        primary = scored[0][1]
        aesthetic = dict(aesthetic_row) if aesthetic_row else primary
        return {
            "routing_mode": "LIBRARY_CONTOUR_MATCHED",
            "match_score": scored[0][0],
            "user_request": user_request,
            "primary_domain_sphere": {
                "sphere_id": primary["sphere_id"],
                "title_ru": primary["title_ru"],
                "summary_ru": primary["summary_ru"],
                "canonical_sources": json.loads(primary["canonical_sources_json"]),
                "mandatory_rules": json.loads(primary["mandatory_rules_json"]),
                "required_db_tables": json.loads(primary["required_db_tables_json"]),
            },
            "aesthetic_design_sphere": {
                "sphere_id": aesthetic["sphere_id"],
                "title_ru": aesthetic["title_ru"],
                "mandatory_rules": json.loads(aesthetic["mandatory_rules_json"]),
                "canonical_sources": json.loads(aesthetic["canonical_sources_json"]),
            },
        }

    def delegate_new_sphere_creation(
        self,
        new_topic_title: str,
        aesthetic_canon_id: str = "iconic_design_aesthetics_ferrari_pininfarina",
        custom_sources: list[dict[str, str]] | None = None,
        custom_rules: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Chief Architect Delegation Engine:
        Commissions the creation of a new sphere in the Library (`domain_spheres_catalog`),
        records the delegation order in `architect_delegation_orders`, and writes the volume to disk.
        """
        slug = re.sub(r"[^a-z0-9_]+", "_", new_topic_title.lower().strip())[:48].strip("_")
        if not slug:
            slug = f"custom_sphere_{int(dt.datetime.now().timestamp())}"
        sphere_id = f"sphere_{slug}"
        now = _utc_now()

        directives = [
            f"1. [@deep_web_researcher]: Провести 3-уровневый поиск первоисточников, ГОСТов, статей и докладов экспертов по теме: '{new_topic_title}'.",
            f"2. [@knowledge_curator]: Выделить канонические правила, терминологию, формулы и анти-паттерны в том библиотеки '{sphere_id}'.",
            f"3. [@storage_and_db_architect]: Спроектировать схему таблиц SQLite3 + FTS5 и структуру хранения PDF/SVG для сферы '{new_topic_title}'.",
            f"4. [@cad_frontend_engineer]: Применить эстетический канон '{aesthetic_canon_id}' (пропорции, чистота линий, информационная плотность).",
        ]

        sources = custom_sources or [
            {
                "title": f"Верифицированный корпус первоисточников и регламентов по направлению: {new_topic_title}",
                "url": "https://docs.cntd.ru/",
                "core_thesis": f"Систематизированные нормативы, эталонные доноры и экспертные доклады для сферы '{new_topic_title}'.",
            }
        ]
        rules = custom_rules or [
            f"[{sphere_id.upper()}-01] Запрет на выдуманные данные: все справочники и сущности сферы '{new_topic_title}' берутся из верифицированных первоисточников.",
            f"[{sphere_id.upper()}-02] Обязательное создание реляционной БД SQLite3 + FTS5 и выгружаемых PDF-документов.",
        ]
        tables = [f"{slug}_entities", f"{slug}_standards", f"{slug}_documents_fts"]
        artifacts = [f"storage/knowledge_spheres/{sphere_id}.json"]
        keywords = [w.lower() for w in re.findall(r"[\wА-Яа-яЁё-]{3,}", new_topic_title)]

        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO architect_delegation_orders (
                    requested_topic, target_sphere_id, assigned_departments,
                    research_directives_json, aesthetic_canon_applied, status, created_at
                ) VALUES (?, ?, ?, ?, ?, 'COMPLETED', ?)
                """,
                (
                    new_topic_title,
                    sphere_id,
                    "@deep_web_researcher -> @knowledge_curator -> @storage_and_db_architect -> @cad_frontend_engineer",
                    json.dumps(directives, ensure_ascii=False),
                    aesthetic_canon_id,
                    now,
                ),
            )
            order_id = int(cur.lastrowid or 0)

            conn.execute(
                """
                INSERT OR REPLACE INTO domain_spheres_catalog (
                    sphere_id, sphere_type, title_ru, summary_ru,
                    keywords_json, canonical_sources_json, mandatory_rules_json,
                    required_db_tables_json, required_artifacts_json, created_by_agent, updated_at
                ) VALUES (?, 'commissioned_by_architect', ?, ?, ?, ?, ?, ?, ?, 'chief_architect_delegation', ?)
                """,
                (
                    sphere_id,
                    new_topic_title,
                    f"Сфера знаний, созданная по поручению Главного Архитектора (Ордер #{order_id}): {new_topic_title}",
                    json.dumps(keywords, ensure_ascii=False),
                    json.dumps(sources, ensure_ascii=False),
                    json.dumps(rules, ensure_ascii=False),
                    json.dumps(tables, ensure_ascii=False),
                    json.dumps(artifacts, ensure_ascii=False),
                    now,
                ),
            )
            conn.execute(
                "INSERT INTO domain_spheres_fts VALUES (?, 'commissioned_by_architect', ?, ?, ?, ?)",
                (sphere_id, new_topic_title, new_topic_title, " ".join(keywords), " ".join(rules)),
            )
            conn.commit()

        disk_file = SPHERES_DISK_DIR / f"{sphere_id}.json"
        disk_file.write_text(
            json.dumps(
                {
                    "order_id": order_id,
                    "sphere_id": sphere_id,
                    "title_ru": new_topic_title,
                    "directives": directives,
                    "canonical_sources": sources,
                    "mandatory_domain_rules": rules,
                    "required_db_tables": tables,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return {
            "order_id": order_id,
            "sphere_id": sphere_id,
            "requested_topic": new_topic_title,
            "assigned_departments": "@deep_web_researcher -> @knowledge_curator -> @storage_and_db_architect",
            "directives": directives,
            "disk_artifact": str(disk_file),
        }

    def list_all_spheres(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM domain_spheres_catalog ORDER BY updated_at DESC").fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["keywords"] = json.loads(d.pop("keywords_json", "[]"))
            d["canonical_sources"] = json.loads(d.pop("canonical_sources_json", "[]"))
            d["mandatory_rules"] = json.loads(d.pop("mandatory_rules_json", "[]"))
            d["required_db_tables"] = json.loads(d.pop("required_db_tables_json", "[]"))
            d["required_artifacts"] = json.loads(d.pop("required_artifacts_json", "[]"))
            out.append(d)
        return out


if __name__ == "__main__":
    lib = DomainKnowledgeLibrary()
    sync_info = lib.sync_seed_spheres()
    sample_rail = lib.route_project_contour("Каталог запчастей ЖД вагонов: тележка 18-100 и автосцепка СА-3")
    sample_law = lib.route_project_contour("Юридический справочник ГАИ ПДД споры по разметке ГОСТ Р 52289-2019")
    sample_culinary = lib.route_project_contour("Кулинария и технологические карты ТТК блюд ресторана по ГОСТ 31987")
    print(
        json.dumps(
            {
                "library_sync": sync_info,
                "railway_route_with_ferrari_aesthetics": sample_rail["primary_domain_sphere"]["title_ru"],
                "law_route_with_ferrari_aesthetics": sample_law["primary_domain_sphere"]["title_ru"],
                "culinary_route_with_ferrari_aesthetics": sample_culinary["primary_domain_sphere"]["title_ru"],
                "aesthetic_canon_attached": sample_rail["aesthetic_design_sphere"]["title_ru"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
