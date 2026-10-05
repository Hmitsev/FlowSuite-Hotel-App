
from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path

import streamlit as st

from lastoria.database.db import get_connection
from lastoria.database.queries import (
    create_order,
    get_categories,
    get_items_by_category,
)


ASSET_DIR = Path(__file__).resolve().parent / "assets"


def asset(file_name: str) -> str:
    """Return an absolute path to a Lastoria asset."""
    return str(ASSET_DIR / file_name)


def show_lastoria_signature() -> None:
    st.markdown(
        """
        <div style="
            position: fixed;
            bottom: 12px;
            right: 18px;
            color: #D4AF37;
            font-family: Arial, sans-serif;
            text-align: right;
            opacity: 0.75;
            z-index: 999;
        ">
            <div style="font-size:18px;font-weight:800;line-height:1;">HA</div>
            <div style="font-size:11px;letter-spacing:2px;font-weight:600;">HMITSEV</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_lastoria_client() -> None:
    # =====================================
    # LANGUAGE
    # =====================================
    
    if "lastoria_lang" not in st.session_state:
        st.session_state.lastoria_lang = "bg"
    
    lang_col1, lang_col2 = st.columns([8, 1])
    
    with lang_col2:
    
        if st.button(
            "🇬🇧 EN",
            key="lastoria_lang_toggle",
            use_container_width=True
        ):
            st.info(
                "🇬🇧 English version is currently under development and will be available soon."
            )
    
    T = {
        "bg": {
            "menu": "📋 Меню",
            "cart": "🛒 Вашата поръчка",
            "order": "✅ Изпрати поръчка",
            "call_waiter": "🔔 Извикай сервитьор",
            "table": "🍽️ Маса №",
            "empty_cart": "Няма избрани артикули.",
            "add": "🛒 Добави",
            "comment": "Коментар"
        },
    
        "en": {
            "menu": "📋 Menu",
            "cart": "🛒 Your Order",
            "order": "✅ Send Order",
            "call_waiter": "🔔 Call Waiter",
            "table": "🍽️ Table No.",
            "empty_cart": "No items selected.",
            "add": "🛒 Add",
            "comment": "Comment"
        }
    }
    
    # Временно винаги използваме BG,
    # докато английските преводи не са готови.
    t = T["bg"]

    # =====================================
    # ВИЗИЯ
    # =====================================


    @st.cache_data
    def get_base64(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(
                f.read()
            ).decode()

    bg_image = get_base64(
        asset("Designer (4).png")
    )

    page_style = f"""
    <style>

    .stApp {{
        background-image:
            linear-gradient(
                rgba(0,0,0,0.72),
                rgba(0,0,0,0.72)
            ),
            url("data:image/png;base64,{bg_image}");

        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        background-repeat: no-repeat;
    }}

    /* =====================================
       ЛУКСОЗНИ КАТЕГОРИИ
    ===================================== */

    [data-testid="stSegmentedControl"] button {{

        background: rgba(
            15,
            23,
            42,
            0.90
        ) !important;

        border: 1px solid #D4AF37 !important;

        border-radius: 14px !important;

        color: #D4AF37 !important;

        font-weight: 700 !important;

        min-height: 48px !important;

        padding-left: 16px !important;
        padding-right: 16px !important;
    }}

    [data-testid="stSegmentedControl"] button:hover {{

        border: 1px solid #FFD54F !important;

        color: #FFD54F !important;
    }}

    [data-testid="stSegmentedControl"] button[aria-pressed="true"] {{

        background: linear-gradient(
            135deg,
            #D4AF37,
            #FFD54F
        ) !important;

        color: #FFD54F !important;

        border: none !important;

        font-weight: 800 !important;

        box-shadow:
            0 0 12px rgba(
                255,
                213,
                79,
                0.35
            ) !important;
    }}

    /* =====================================
       СКРИВА STREAMLIT STATUS
    ===================================== */

    [data-testid="stStatusWidget"] {{
        display: none !important;
    }}

    div[data-testid="stStatusWidget"] {{
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
    }}

    [data-testid="stSpinner"] {{
        display: none !important;
    }}

    .stSpinner {{
        display: none !important;
    }}

    /* =====================================
       ХЕДЪР
    ===================================== */

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    [data-testid="stToolbar"] {{
        right: 2rem;
    }}

    </style>
    """

    st.markdown(
        page_style,
        unsafe_allow_html=True
    )
    # =====================================
    # SESSION STATE
    # =====================================

    if "lastoria_cart" not in st.session_state:
        st.session_state.lastoria_cart = []
    if "lastoria_cart_notice" not in st.session_state:
        st.session_state.lastoria_cart_notice = None   

    if "lastoria_last_order_id" not in st.session_state:
        st.session_state.lastoria_last_order_id = None


    # =====================================
    # ПОМОЩНИ ФУНКЦИИ
    # =====================================

    def add_to_cart(item_id, item_name, price, note=""):

        st.session_state.lastoria_cart.append(
            {
                "id": int(item_id),
                "name": str(item_name),
                "price": float(price),
                "note": str(note).strip()
            }
        )


    def remove_one_from_cart(item_id, note):

        for index, cart_item in enumerate(st.session_state.lastoria_cart):

            same_item = cart_item["id"] == item_id

            same_note = (
                cart_item.get("note", "").strip()
                == note.strip()
            )

            if same_item and same_note:
                st.session_state.lastoria_cart.pop(index)
                break

    def call_waiter(table_number):

        conn = get_connection()
        cur = conn.cursor()

        try:

            cur.execute(
                """
                SELECT id
                FROM restaurant_tables
                WHERE table_number = %s
                LIMIT 1
                """,
                (table_number,)
            )

            result = cur.fetchone()

            if not result:
                return False

            table_id = result[0]

            cur.execute(
                """
                INSERT INTO notifications
                (
                    table_id,
                    notification_type,
                    message,
                    is_read
                )
                VALUES
                (
                    %s,
                    'CALL_WAITER',
                    %s,
                    FALSE
                )
                """,
                (
                    table_id,
                    f'Маса №{table_number} извика сервитьор'
                )
            )

            conn.commit()
            return True

        finally:

            cur.close()
            conn.close()
    # =====================================
    # ЗАГЛАВИЕ И БАНЕР
    # =====================================



    try:
        st.image(
            asset("Ластория.фон.jpeg"),
            use_container_width=True
        )
    except Exception:
        st.warning(
            "Банерът не беше намерен, но менюто може да се използва."
        )


        # =====================================
    # МАСА ОТ QR КОДА
    # =====================================

    raw_table_number = st.query_params.get(
        "table",
        "1"
    )

    try:
        table_number = int(
            raw_table_number
        )

    except (TypeError, ValueError):
        table_number = 1

    if table_number < 1 or table_number > 20:
        st.error(
            "Невалиден QR код. "
            "Номерът на масата трябва да бъде "
            "между 1 и 20."
        )
        st.stop()

    # =====================================
    # ЛЕНТА С МАСА И КОЛИЧКА
    # =====================================

    cart_count = len(
        st.session_state.lastoria_cart
    )

    table_col, cart_col = st.columns(
        [6, 2],
        vertical_alignment="center"
    )

    with table_col:
        st.success(
            f"{t['table']} {table_number}"
        )

    with cart_col:
        with st.popover(
            f"🛒 Количка ({cart_count})",
            use_container_width=True
        ):
            st.markdown(
                "### 🛒 Вашата поръчка"
            )

            st.caption(
                f"Добавени артикули: {cart_count}"
            )

            if not st.session_state.lastoria_cart:
                st.info(
                    t["empty_cart"]
                )

            else:
                grouped = {}

                for cart_item in (
                    st.session_state.lastoria_cart
                ):
                    group_key = (
                        cart_item["id"],
                        cart_item.get(
                            "note",
                            ""
                        ),
                        cart_item["name"]
                    )

                    if group_key not in grouped:
                        grouped[group_key] = {
                            "id": cart_item["id"],
                            "name": cart_item["name"],
                            "price": float(
                                cart_item["price"]
                            ),
                            "note": cart_item.get(
                                "note",
                                ""
                            ),
                            "qty": 0
                        }

                    grouped[group_key]["qty"] += 1

                cart_total = 0.0

                for group_index, data in enumerate(
                    grouped.values()
                ):
                    qty = data["qty"]

                    row_total = (
                        qty
                        * float(data["price"])
                    )

                    cart_total += row_total

                    st.write(
                        f"**{data['name']}**"
                    )

                    if data["note"]:
                        st.caption(
                            f"📝 {data['note']}"
                        )

                    minus_col, qty_col, plus_col = st.columns(
                        [1, 2, 1],
                        vertical_alignment="center"
                    )

                    with minus_col:
                        if st.button(
                            "➖",
                            key=(
                                "lastoria_cart_minus_"
                                f"{group_index}_"
                                f"{data['id']}"
                            ),
                            use_container_width=True
                        ):
                            remove_one_from_cart(
                                data["id"],
                                data["note"]
                            )

                            st.rerun()

                    with qty_col:
                        st.markdown(
                            (
                                "<div style='"
                                "text-align:center;"
                                "font-size:18px;"
                                "font-weight:800;"
                                "color:#FFD54F;"
                                "'>"
                                f"x{qty}"
                                "</div>"
                            ),
                            unsafe_allow_html=True
                        )

                    with plus_col:
                        if st.button(
                            "➕",
                            key=(
                                "lastoria_cart_plus_"
                                f"{group_index}_"
                                f"{data['id']}"
                            ),
                            use_container_width=True
                        ):
                            add_to_cart(
                                item_id=data["id"],
                                item_name=data["name"],
                                price=data["price"],
                                note=data["note"]
                            )

                            st.rerun()

                    st.caption(
                        f"€ {data['price']:.2f} × "
                        f"{qty} = € {row_total:.2f}"
                    )

                    st.divider()

                st.success(
                    f"Общо: € {cart_total:.2f}"
                )

                clear_col, send_col = st.columns(
                    2
                )

                with clear_col:
                    if st.button(
                        "🗑️ Изчисти",
                        key="lastoria_clear_cart_popover",
                        use_container_width=True
                    ):
                        st.session_state.lastoria_cart = []

                        st.rerun()

                with send_col:
                    if st.button(
                        t["order"],
                        key="lastoria_send_order_popover",
                        type="primary",
                        use_container_width=True
                    ):
                        try:
                            order_id = create_order(
                                table_number,
                                st.session_state.lastoria_cart
                            )

                            st.session_state.lastoria_cart = []

                            st.session_state.lastoria_last_order_id = (
                                order_id
                            )

                            st.rerun()

                        except Exception as error:
                            st.error(
                                "Поръчката не беше изпратена: "
                                f"{error}"
                            )

    # =====================================
    # СЪОБЩЕНИЕ ЗА ИЗПРАТЕНА ПОРЪЧКА
    # =====================================

    if (
        st.session_state.lastoria_last_order_id
        is not None
    ):
        sent_order_id = (
            st.session_state.lastoria_last_order_id
        )

        st.success(
            f"✅ Поръчка №{sent_order_id} "
            "е изпратена успешно! "
            "Кухнята и сервитьорът вече я виждат."
        )

        st.session_state.lastoria_last_order_id = None

    # =====================================
    # УКАЗАНИЕ ЗА ТЕЛЕФОН
    # =====================================

    st.caption(
        "📱 ↔️ За по-добра видимост може "
        "да завъртите телефона хоризонтално"
    )

    # =====================================
    # ПОВИКВАНЕ НА СЕРВИТЬОР
    # =====================================

    if st.button(
        t["call_waiter"],
        key="lastoria_call_waiter",
        use_container_width=True
    ):
        if call_waiter(
            table_number
        ):
            st.success(
                "Сервитьорът е уведомен."
            )

        else:
            st.error(
                "Масата не е намерена "
                "в базата данни."
            )

    # =====================================
    # МЕНЮ
    # =====================================

    st.markdown(
        """
        <div style="
            border:2px solid #D4AF37;
            border-radius:16px;
            padding:14px 20px 50px 20px;
            margin-bottom:35px;
            background:linear-gradient(
                135deg,
                rgba(15,23,42,0.95),
                rgba(10,18,30,0.95)
            );
            box-shadow:
                0 0 12px rgba(212,175,55,0.25);
        ">
            <span style="
                color:#F5E6C8;
                font-size:32px;
                font-weight:800;
                letter-spacing:1px;
            ">
                📋 Меню
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    categories = get_categories()

    now = datetime.now().time()

    daily_end = datetime.strptime("16:00", "%H:%M").time()

    # След 16:00 скрива Дневно меню
    if now > daily_end:
        categories = [
            category
            for category in categories
            if category[0] != "Дневно меню"
        ]


    category_display = {
        "Дневно меню": "📅 🔥 ДНЕВНО МЕНЮ",
        "Салати": "⚜ Салати",
        "Разядки и студени предястия": "⚜ Предястия",
        "Топли предложения за споделяне": "⚜ За споделяне",
        "Риба и морски дарове": "⚜ Морски дарове",
        "Паста и ризото": "⚜ Паста и ризото",
        "Приготвено на плоча": "⚜ На плоча",
        "Основни ястия": "⚜ Основни ястия",
        "От краче до уше": "⚜ От краче до уше",
        "Бургери": "⚜ Бургери",
        "Десерти": "⚜ Десерти",
        "Напитки": "🥂 Напитки"
    }
    category_grams = {
        "Салати": "400 гр.",
        "Разядки и студени предястия": "300 гр.",
        "Топли предложения за споделяне": "350 гр.",
        "Риба и морски дарове": "450 гр.",
        "Паста и ризото": "400 гр.",
        "Приготвено на плоча": "450 гр.",
        "Основни ястия": "450 гр.",
        "От краче до уше": "400 гр.",
        "Бургери": "450 гр.",
        "Десерти": "1 бр."
    }
    category_banners = {
        "📅 🔥 ДНЕВНО МЕНЮ": asset("01_dnevno_menu.png"),
        "⚜ Салати": asset("02_salati.png"),
        "⚜ Предястия": asset("03_predyastiya.png"),
        "⚜ За споделяне": asset("04_za_spodelyane.png"),
        "⚜ Морски дарове": asset("05_morski_darove.png"),
        "⚜ Паста и ризото": asset("06_pasta_i_rizoto.png"),
        "⚜ На плоча": asset("07_na_plocha.png"),
        "⚜ Основни ястия": asset("08_osnovni_yastiya.png"),
        "⚜ От краче до уше": asset("09_ot_krache_do_ushe.png"),
        "⚜ Бургери": asset("10_burgeri.png"),
        "⚜ Десерти": asset("11_deserti.png")
    }
    reverse_display = {
        value: key
        for key, value in category_display.items()
    }

    category_names = [
        category_display.get(
            category[0],
            category[0]
        )
        for category in categories
    ]

    if not category_names:
        st.warning("В момента няма активни категории в менюто.")
        show_lastoria_signature()
        return

    selected_display = st.segmented_control(
        "",
        category_names,
        default=category_names[0],
        key="lastoria_main_category_selector"
    )

    selected_category = reverse_display.get(
        selected_display,
        selected_display
    )
    main_section_grams = category_grams.get(
        selected_category,
        ""
    )

    if main_section_grams:

        st.markdown(
            f"""
            <div style="
                color:#CFCFCF;
                font-size:16px;
                font-weight:600;
                margin-top:4px;
                margin-bottom:10px;
            ">
                ⚖️ {main_section_grams}
            </div>
            """,
            unsafe_allow_html=True
        )
    items = get_items_by_category(
        selected_category
    )
    main_banner = category_banners.get(selected_display)

    if main_banner:
        st.image(
            main_banner,
            use_container_width=True
        )

    # =====================================
    # ПОДКАТЕГОРИИ НА ДНЕВНОТО МЕНЮ
    # =====================================

    if selected_category == "Дневно меню":

        selected_daily_group = st.segmented_control(
            "",
            [
                "🍲 Супи",
                "🍽️ Готови ястия",
                "🍰 Десерт"
            ],
            default="🍲 Супи",
            key="lastoria_daily_group_selector"
        )

        items = [
            item
            for item in items
            if len(item) > 7
            and item[7] == selected_daily_group
        ]

        st.markdown(
            f"""
            <div style="
                color:#FFD54F;
                font-size:22px;
                font-weight:700;
                margin-top:12px;
                margin-bottom:10px;
            ">
                {selected_daily_group}
            </div>
            """,
            unsafe_allow_html=True
        )
    section_title = ""

    # =====================================
    # ПОДКАТЕГОРИИ НА НАПИТКИТЕ
    # =====================================

    if selected_category == "Напитки":

        selected_drink_group = st.segmented_control(
            "",
            [
                "☕ Топли напитки",
                "🥤 Безалкохолни",
                "🍺 Бира и сайдер",
                "🍷 Вина",
                "🥃 Алкохол"
            ],
            default="☕ Топли напитки",
            key="lastoria_drink_group_selector"
        )

        drink_banners = {
            "☕ Топли напитки": asset("12_topli_napitki.png"),
            "🥤 Безалкохолни": asset("13_gazirani_napitki.png"),
            "🍺 Бира и сайдер": asset("фон бира.png"),
            "🍷 Вина": asset("фон вина.jpeg"),
            "🥃 Алкохол": asset("фон алкохол.jpeg")
        }

        banner_path = drink_banners.get(selected_drink_group)

        if banner_path:
            st.image(
                banner_path,
                width=700
            )

            st.markdown("<br>", unsafe_allow_html=True)

        items = [
            item
            for item in items
            if len(item) > 4
            and item[4] == selected_drink_group
        ]

        section_title = selected_drink_group

        # =====================================
        # ПОДКАТЕГОРИИ НА ВИНАТА
        # =====================================

        if selected_drink_group == "🍷 Вина":

            selected_wine_type = st.segmented_control(
                "",
                [
                    "🤍 Бели вина",
                    "🍷 Червени вина",
                    "🌹 Розе",
                    "🥂 Просеко"
                ],
                default="🤍 Бели вина",
                key="lastoria_wine_type_selector"
            )

            items = [
                item
                for item in items
                if len(item) > 5
                and item[5] == selected_wine_type
            ]

            section_title = selected_wine_type

        # =====================================
        # ПОДКАТЕГОРИИ НА АЛКОХОЛА
        # =====================================

        elif selected_drink_group == "🥃 Алкохол":

            selected_alcohol_type = st.segmented_control(
                "",
                [
                    "🥃 Уиски",
                    "🍸 Водка",
                    "🥃 Ракия",
                    "🥃 Джин",
                    "🌿 Анасонови",
                    "🥃 Ром / Коняк",
                    "🍷 Дижестив"
                ],
                default="🥃 Уиски",
                key="lastoria_alcohol_type_selector"
            )

            items = [
                item
                for item in items
                if len(item) > 6
                and item[6] == selected_alcohol_type
            ]

            section_title = selected_alcohol_type

        st.markdown(
            f"""
            <div style="
                color:#FFD54F;
                font-size:22px;
                font-weight:700;
                margin-top:12px;
                margin-bottom:10px;
            ">
                {section_title}
            </div>
            """,
            unsafe_allow_html=True
        )

    # =====================================
    # СНИМКИ НА БУРГЕРИТЕ
    # =====================================

    burger_images = {
        "Американски хот-дог": asset("shared image (15).jpeg"),
        "Свински бургер": asset("shared image (16).jpeg"),
        "Телешки бургер": asset("shared image (4).jpeg"),
        "Пилешки бургер": asset("shared image (6).jpeg"),
        "Пържени картофи с пилешко": asset("shared image (9).jpeg"),
        "Пържени картофи със сьомга": asset("shared image (12).jpeg"),
        "Пържени картофи с бекон": asset("shared image (13).jpeg"),
        "Пържени картофи с телешко": asset("01d65c96-56f8-4703-99ed-a1ac6d9b5065.jpg")
    }

    # =====================================
    # ПОКАЗВАНЕ НА АРТИКУЛИТЕ
    # =====================================

    if not items:

        st.info(
            "В тази секция все още няма налични артикули."
        )

    else:

        for item_index, item in enumerate(items):

            item_id = item[0]
            item_name = item[1]
            price = float(item[2])
            description = item[3] if len(item) > 3 else ""
            item_drink_group = item[4] if len(item) > 4 else ""
            item_wine_type = item[5] if len(item) > 5 else ""
            item_alcohol_type = item[6] if len(item) > 6 else ""

            col1, col2, col3, col4 = st.columns(
                [6, 0.7, 1.3, 1.7]
            )

            # =====================================
            # ИМЕ НА АРТИКУЛА
            # =====================================

            with col1:

                st.markdown(
                    f"""
                    <div style="
                        background-color:#0F172A;
                        border:1px solid #24324A;
                        border-radius:12px;
                        padding:12px 14px;
                        color:#F5E6C8;
                        font-weight:700;
                        font-size:18px;
                        min-height:52px;
                        display:flex;
                        align-items:center;
                    ">
                        {item_name}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                drink_variants = {

                    "Кока-Кола 250ml": [
                        "Coca-Cola",
                        "Coca-Cola Zero"
                    ],

                    "Фанта 250ml": [
                        "Портокал",
                        "Лимон",
                        "Екзотик"
                    ],

                    "Натурален сок Cappy": [
                        "Праскова",
                        "Портокал",
                        "Ябълка",
                        "Мултивитамин"
                    ],

                    "Студен чай Fuzetea": [
                        "Праскова",
                        "Лимон",
                        "Зелен чай"
                    ],

                    "Schweppes Сода": [
                        "Сода",
                        "Тоник",
                        "Bitter Lemon"
                    ]
                }

                selected_variant = ""

                if item_name in drink_variants:
                
                    variant_col, _ = st.columns([2, 8])

                    with variant_col:
                
                        selected_variant = st.selectbox(
                            "",
                            drink_variants[item_name],
                            key=f"lastoria_variant_{item_id}_{item_index}"
                        )

            # =====================================
            # ИНФОРМАЦИЯ И КОМЕНТАР
            # =====================================
        
            with col2:
        
                with st.popover("ℹ️"):
        
                    st.markdown(
                        f"""
                        <div style="
                            color:#F5E6C8;
                            font-size:28px;
                            font-weight:800;
                            text-align:center;
                            margin-bottom:10px;
                        ">
                            {item_name}
                        </div>
                        """,
                        unsafe_allow_html=True
                )
    
                    drink_images = {
                        "Кока-Кола 250ml": asset("kola.png"),
                        "Спрайт 250ml": asset("sprite.png"),
                        "Фанта 250ml": asset("fanta port.png"),
                        "Минерална вода Банкя 330ml": asset("bankq.png"),
                
                        "Натурален сок Cappy": asset("kapu praskova.png"),
                        "Студен чай Fuzetea": asset("stud.chai.png"),
                        "Red Bull": asset("red bul.png"),
                        "Фреш 200ml": asset("фреш.png"),
                
                        "Капучино": asset("kapochino.png"),
                        "Бяло фрапе": asset("фон топла напитка.png"),
                        "Бяло фрапе с вкус": asset("фон топла напитка.png"),
                        "Черно фрапе": asset("фон топла напитка.png"),
                
                        "Beluga": asset("beluga.png"),
                        "Руски стандарт": asset("ruski stand.png"),
                        "Бургас 63": asset("burgas 63.png"),
                
                        "Bushmills": asset("bushmils.png"),
                        "Bushmills Black": asset("bushmils black.png"),
                        "Jack Daniels": asset("jack.png"),
                        "Jameson": asset("jameson.png"),
                        "Jameson Black Barrel": asset("jameson.png")
                    }
    
                    image_path = burger_images.get(item_name)
    
                    if not image_path:
                        image_path = drink_images.get(item_name)

                    if image_path:
        
                        try:
                            st.image(
                                image_path,
                                use_container_width=True
                            )
        
                        except Exception:
                            st.caption(
                                "Снимката временно не е налична."
                            )
        
                    if item_drink_group == "🥃 Алкохол":
        
                        st.markdown(
                            """
                            <div style="
                                background:#1F2937;
                                color:#FFD54F;
                                border:1px solid #D4AF37;
                                border-radius:10px;
                                padding:10px;
                                text-align:center;
                                font-weight:700;
                                margin-bottom:10px;
                            ">
                                🥃 Посочената цена е за 50 мл.
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
        
                    if description:
        
                        st.write(
                            description
                        )
        
                    else:
        
                        st.info(
                            "Няма описание."
                        )
        
                    comment_label = "Коментар"
        
                    if selected_category not in (
                        "Напитки",
                    ):
                        comment_label = "Коментар към кухнята"
        
                    comment = st.text_area(
                        comment_label,
                        placeholder=" коментар",
                        key=f"lastoria_comment_{item_id}_{item_index}",
                        height=80
                    )
        
                    if st.button(
                        "Запази коментар",
                        key=f"lastoria_save_{item_id}_{item_index}"
                    ):
        
                        st.session_state[
                            f"lastoria_saved_note_{item_id}_{item_index}"
                        ] = comment
        
                        st.success(
                            "Коментарът е запазен."
                        )
            # =====================================
            # ЦЕНА
            # =====================================

            with col3:

                st.markdown(
                    f"""
                    <div style="
                        color:#FFD54F;
                        font-weight:700;
                        font-size:18px;
                        padding-left:15px;
                    ">
                        € {price:.2f}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # =====================================
            # ДОБАВЯНЕ В КОЛИЧКАТА
            # =====================================

            with col4:

                item_is_in_cart = any(
                    cart_item["id"] == item_id
                    for cart_item in st.session_state.lastoria_cart
                )

                if item_is_in_cart:
                    st.markdown(
                        """
                        <div style="
                            background:#198754;
                            color:white;
                            border-radius:8px;
                            padding:4px 8px;
                            text-align:center;
                            font-size:12px;
                            font-weight:700;
                            margin-bottom:4px;
                        ">
                            ✅ Добавено
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                if st.button(
                    "🛒 Добави",
                    key=f"lastoria_add_{item_id}_{item_index}",
                    use_container_width=True
                ):

                    saved_comment = st.session_state.get(
                        f"lastoria_saved_note_{item_id}_{item_index}",
                        ""
                    )

                    final_name = item_name

                    if (
                        item_name in drink_variants
                        and selected_variant
                    ):
                        final_name = (
                            f"{item_name} - {selected_variant}"
                        )

                    add_to_cart(
                        item_id=item_id,
                        item_name=final_name,
                        price=price,
                        note=saved_comment
                    )

                    st.session_state.lastoria_cart_notice = (
                        f"✅ Добавено: {final_name}"
                    )

                    st.rerun()

    # =====================================
    # ПОТВЪРЖДЕНИЕ ЗА ДОБАВЕН АРТИКУЛ
    # =====================================

    if st.session_state.lastoria_cart_notice:
        st.toast(
            st.session_state.lastoria_cart_notice
        )

        st.session_state.lastoria_cart_notice = None

    show_lastoria_signature()      
    # =====================================
    # КОЛИЧКА
    # =====================================

    st.divider()

    st.subheader(t["cart"])

    if st.session_state.lastoria_last_order_id is not None:

        st.success(
            f"✅ Поръчката е изпратена успешно!\n\n"
            f"🧾 Номер на поръчката: {st.session_state.lastoria_last_order_id}\n\n"
            "👨‍🍳 Кухнята и сервитьорът вече виждат вашата поръчка.\n\n"
            "🔔 Ако имате нужда от нещо допълнително, "
            "използвайте бутона „Извикай сервитьор“ "
            "или просто махнете с 👋."
        )

        st.session_state.lastoria_last_order_id = None

    elif not st.session_state.lastoria_cart:

        st.info(t["empty_cart"])

    else:

        grouped = {}

        for item in st.session_state.lastoria_cart:

            key = (
                item["id"],
                item.get("note", "")
            )

            if key not in grouped:

                grouped[key] = {
                    "id": item["id"],
                    "name": item["name"],
                    "price": item["price"],
                    "note": item.get("note", ""),
                    "qty": 0
                }

            grouped[key]["qty"] += 1

        total = 0

        for data in grouped.values():

            qty = data["qty"]

            row_total = qty * data["price"]

            c1, c2, c3, c4, c5 = st.columns(
                [5, 1, 1, 1, 1]
            )

            with c1:

                st.write(data["name"])

                if data["note"]:

                    st.caption(
                        f"📝 {data['note']}"
                    )

            with c2:

                if st.button(
                    "➖",
                    key=f"lastoria_minus_{data['id']}_{data['note']}"
                ):

                    remove_one_from_cart(
                        data["id"],
                        data["note"]
                    )

                    st.rerun()

            with c3:

                st.write(
                    f"x{qty}"
                )

            with c4:

                if st.button(
                    "➕",
                    key=f"lastoria_plus_{data['id']}_{data['note']}"
                ):

                    add_to_cart(
                        item_id=data["id"],
                        item_name=data["name"],
                        price=data["price"],
                        note=data["note"]
                    )

                    st.rerun()

            with c5:

                st.write(
                    f"€ {row_total:.2f}"
                )

            total += row_total

        st.success(
            f"Общо: € {total:.2f}"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "🗑️ Изчисти количката",
                key="lastoria_clear_cart"
            ):

                st.session_state.lastoria_cart = []

                st.rerun()

        with col2:

            if st.button(
                t["order"],
                key="lastoria_send_order"
            ):

                order_id = create_order(
                    table_number,
                    st.session_state.lastoria_cart
                )

                st.session_state.lastoria_cart = []
                st.session_state.lastoria_last_order_id = order_id

                st.rerun()

    show_lastoria_signature()
