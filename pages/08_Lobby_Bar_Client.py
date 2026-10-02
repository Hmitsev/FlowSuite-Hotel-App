import streamlit as st

from database.db import get_connection
from pathlib import Path
import base64


# =========================================================
# НАСТРОЙКИ НА СТРАНИЦАТА
# =========================================================
st.set_page_config(
    page_title="Lobby Bar",
    page_icon="🍸",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# =========================================================
# БАНЕР И ВИЗУАЛЕН СТИЛ
# =========================================================
BANNER_FILE = (
    Path("assets")
    / "Screenshot 2026-09-09 025734.png"
)


@st.cache_data
def get_base64_image(file_path):
    with open(
        file_path,
        "rb"
    ) as image_file:
        return base64.b64encode(
            image_file.read()
        ).decode()


background_css = """
    background:
        radial-gradient(
            circle at top,
            rgba(28, 23, 15, 0.97) 0%,
            rgba(7, 10, 15, 0.99) 48%,
            rgba(3, 5, 8, 1) 100%
        );
"""


if BANNER_FILE.exists():
    banner_base64 = get_base64_image(
        BANNER_FILE
    )

    background_css = f"""
        background-image:
            linear-gradient(
                rgba(3, 5, 8, 0.82),
                rgba(3, 5, 8, 0.94)
            ),
            url(
                "data:image/png;base64,{banner_base64}"
            );
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    """


page_style = f"""
<style>
.stApp {{
    {background_css}
    background-color: #080B12;
    color: #F5E6C8;
}}

[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSpinner"] {{
    display: none !important;
}}

footer {{
    visibility: hidden;
}}

.block-container {{
    max-width: 1050px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}}

h1,
h2,
h3,
h4,
p,
label,
span {{
    color: #F5E6C8;
}}

[data-testid="stVerticalBlockBorderWrapper"] {{
    background: rgba(8, 12, 18, 0.88);
    border: 1px solid rgba(212, 175, 55, 0.38);
    border-radius: 16px;
    box-shadow:
        0 14px 35px rgba(0, 0, 0, 0.28);
}}

[data-testid="stMetric"] {{
    background: rgba(8, 12, 18, 0.88);
    border: 1px solid rgba(212, 175, 55, 0.38);
    border-radius: 15px;
    padding: 16px;
}}

[data-testid="stAlert"] {{
    background: rgba(8, 12, 18, 0.90);
    border: 1px solid rgba(212, 175, 55, 0.32);
    border-radius: 14px;
}}

div[data-testid="stButton"] button,
div[data-testid="stFormSubmitButton"] button {{
    min-height: 43px !important;
    border-radius: 11px !important;
    font-weight: 800 !important;
}}

div[data-testid="stButton"] button[kind="primary"],
div[data-testid="stFormSubmitButton"] button[kind="primary"] {{
    background:
        linear-gradient(
            135deg,
            #B98528 0%,
            #D4AF37 48%,
            #F5D77B 100%
        ) !important;
    border: 1px solid #F5D77B !important;
    color: #101010 !important;
}}

div[data-testid="stButton"] button[kind="primary"] p,
div[data-testid="stFormSubmitButton"] button[kind="primary"] p {{
    color: #101010 !important;
}}

@media only screen and (max-width: 768px) {{
    .block-container {{
        padding-top: 0.5rem;
        padding-left: 0.7rem;
        padding-right: 0.7rem;
    }}

    div[data-testid="stButton"] button,
    div[data-testid="stFormSubmitButton"] button {{
        min-height: 40px !important;
        font-size: 12px !important;
    }}
}}
</style>
"""


st.markdown(
    page_style,
    unsafe_allow_html=True
)

# =========================================================
# ДЕМО МЕНЮ
# =========================================================
LOBBY_MENU = [
    {
        "name": "Минерална вода",
        "description": "330 мл",
        "price": 3.50,
        "category": "Безалкохолни"
    },
    {
        "name": "Coca-Cola",
        "description": "330 мл",
        "price": 4.50,
        "category": "Безалкохолни"
    },
    {
        "name": "Портокалов сок",
        "description": "250 мл",
        "price": 5.00,
        "category": "Безалкохолни"
    },
    {
        "name": "Еспресо",
        "description": "Класическо еспресо",
        "price": 3.50,
        "category": "Топли напитки"
    },
    {
        "name": "Капучино",
        "description": "Еспресо с млечна пяна",
        "price": 5.50,
        "category": "Топли напитки"
    },
    {
        "name": "Лате",
        "description": "Кафе с мляко",
        "price": 6.00,
        "category": "Топли напитки"
    },
    {
        "name": "Бира",
        "description": "330 мл",
        "price": 6.50,
        "category": "Алкохолни"
    },
    {
        "name": "Чаша бяло вино",
        "description": "150 мл",
        "price": 8.50,
        "category": "Алкохолни"
    },
    {
        "name": "Аперол Шприц",
        "description": "Класически коктейл",
        "price": 12.00,
        "category": "Коктейли"
    },
    {
        "name": "Мохито",
        "description": "Ром, лайм, мента и сода",
        "price": 13.00,
        "category": "Коктейли"
    },
    {
        "name": "Клуб сандвич",
        "description": "Сервира се с пържени картофи",
        "price": 14.50,
        "category": "Храна"
    },
    {
        "name": "Шоколадово суфле",
        "description": "Топъл шоколадов десерт",
        "price": 9.00,
        "category": "Храна"
    }
]


# =========================================================
# ЗОНА И НОМЕР НА МАСАТА ОТ QR ЛИНКА
# Пример: ?area=lobby&table=1
# =========================================================
raw_area = st.query_params.get(
    "area",
    "lobby"
)

service_area = str(
    raw_area or "lobby"
).strip().upper()


raw_table_number = st.query_params.get(
    "table"
)

if raw_table_number:
    try:
        parsed_table_number = int(
            raw_table_number
        )

        if 1 <= parsed_table_number <= 999:
            st.session_state.lobby_table_number = (
                parsed_table_number
            )

    except (TypeError, ValueError):
        pass


table_number = st.session_state.get(
    "lobby_table_number",
    1
)


# =========================================================
# SESSION STATE
# =========================================================
if "lobby_cart" not in st.session_state:
    st.session_state.lobby_cart = {}


if "lobby_order_success" not in st.session_state:
    st.session_state.lobby_order_success = None


if "lobby_order_error" not in st.session_state:
    st.session_state.lobby_order_error = None


# =========================================================
# ПОМОЩНИ ФУНКЦИИ
# =========================================================
def add_to_cart(
    item_name,
    unit_price
):
    if item_name not in st.session_state.lobby_cart:
        st.session_state.lobby_cart[item_name] = {
            "quantity": 0,
            "unit_price": float(unit_price)
        }

    st.session_state.lobby_cart[
        item_name
    ]["quantity"] += 1


def remove_from_cart(
    item_name
):
    if item_name not in st.session_state.lobby_cart:
        return

    current_quantity = (
        st.session_state.lobby_cart[
            item_name
        ]["quantity"]
    )

    if current_quantity <= 1:
        del st.session_state.lobby_cart[
            item_name
        ]

    else:
        st.session_state.lobby_cart[
            item_name
        ]["quantity"] -= 1


def get_cart_total():
    return sum(
        float(item_data["unit_price"])
        * int(item_data["quantity"])
        for item_data
        in st.session_state.lobby_cart.values()
    )


def create_lobby_order(
    selected_table_number,
    selected_service_area,
    guest_note
):
    if not st.session_state.lobby_cart:
        raise ValueError(
            "Поръчката е празна."
        )

    normalized_note = str(
        guest_note or ""
    ).strip()

    total_amount = get_cart_total()

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO lobby_bar_orders (
                service_area,
                table_number,
                order_status,
                total_amount,
                guest_note,
                created_at,
                updated_at
            )
            VALUES (
                %s,
                %s,
                'NEW',
                %s,
                %s,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            RETURNING id
            """,
            (
                selected_service_area,
                selected_table_number,
                total_amount,
                normalized_note
            )
        )

        result = cur.fetchone()

        if result is None:
            raise ValueError(
                "Не беше създадена поръчка."
            )

        order_id = result[0]

        for item_name, item_data in st.session_state.lobby_cart.items():

            cur.execute(
                """
                INSERT INTO lobby_bar_order_items (
                    order_id,
                    item_name,
                    quantity,
                    unit_price,
                    item_status,
                    created_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    'NEW',
                    CURRENT_TIMESTAMP
                )
                """,
                (
                    order_id,
                    item_name,
                    int(item_data["quantity"]),
                    float(item_data["unit_price"])
                )
            )

        conn.commit()

        return order_id

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()


# =========================================================
# СЪОБЩЕНИЯ СЛЕД ИЗПРАЩАНЕ
# =========================================================
if st.session_state.lobby_order_success:

    success_data = (
        st.session_state.lobby_order_success
    )

    st.success(
        "Поръчката е изпратена успешно."
    )

    st.info(
        "Номер на поръчката: "
        f"#{success_data['order_id']}"
    )

    st.info(
        "🍽️ Lobby Bar, "
        f"маса №{success_data['table_number']}"
    )

    st.session_state.lobby_order_success = None


if st.session_state.lobby_order_error:

    st.error(
        st.session_state.lobby_order_error
    )

    st.session_state.lobby_order_error = None


# =========================================================
# ЗАГЛАВИЕ
# =========================================================
st.markdown(
    """
    <div style="
        text-align:center;
        color:#D4AF37;
        font-size:36px;
        font-weight:900;
        letter-spacing:1px;
        margin-bottom:4px;
    ">
        🍸 LOBBY BAR
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div style="
        text-align:center;
        color:#F5E6C8;
        font-size:20px;
        font-weight:800;
        margin-bottom:20px;
    ">
        🍽️ Маса №{table_number}
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Изберете желаните артикули и изпратете поръчката."
)


# =========================================================
# ПРОВЕРКА НА QR ПАРАМЕТРИТЕ
# =========================================================
if service_area != "LOBBY":

    st.warning(
        "Тази страница е предназначена за Lobby Bar."
    )


# =========================================================
# КАТЕГОРИИ
# =========================================================
menu_categories = []

for menu_item in LOBBY_MENU:
    category = menu_item["category"]

    if category not in menu_categories:
        menu_categories.append(
            category
        )


selected_category = st.radio(
    "Категория",
    menu_categories,
    horizontal=True,
    label_visibility="collapsed",
    key="lobby_menu_category"
)

st.divider()


# =========================================================
# ФИЛТРИРАНО МЕНЮ
# =========================================================
filtered_menu = [
    menu_item
    for menu_item in LOBBY_MENU
    if menu_item["category"]
    == selected_category
]


for menu_item in filtered_menu:

    with st.container(
        border=True
    ):
        item_col, price_col, action_col = (
            st.columns(
                [5, 2, 2],
                vertical_alignment="center"
            )
        )

        with item_col:
            st.subheader(
                menu_item["name"]
            )

            st.caption(
                menu_item["description"]
            )

        with price_col:
            st.write(
                f"**€ {menu_item['price']:.2f}**"
            )

        with action_col:
            if st.button(
                "➕ Добави",
                key=(
                    "lobby_add_"
                    f"{menu_item['name']}"
                ),
                type="primary",
                use_container_width=True
            ):
                add_to_cart(
                    item_name=menu_item["name"],
                    unit_price=menu_item["price"]
                )

                st.rerun()


# =========================================================
# КОЛИЧКА
# =========================================================
st.divider()

st.subheader(
    "🧾 Вашата поръчка"
)

if not st.session_state.lobby_cart:

    st.info(
        "Все още няма избрани артикули."
    )

else:

    for item_name, item_data in st.session_state.lobby_cart.items():

        cart_col1, cart_col2, cart_col3 = st.columns(
            [5, 2, 2],
            vertical_alignment="center"
        )

        with cart_col1:
            st.write(
                f"**{item_name}**"
            )

            st.caption(
                f"Количество: {item_data['quantity']}"
            )

        with cart_col2:

            item_total = (
                float(item_data["unit_price"])
                * int(item_data["quantity"])
            )

            st.write(
                f"€ {item_total:.2f}"
            )

        with cart_col3:

            if st.button(
                "➖ Премахни",
                key=f"lobby_remove_{item_name}",
                use_container_width=True
            ):
                remove_from_cart(
                    item_name
                )

                st.rerun()

    st.divider()

    lobby_total = get_cart_total()

    st.metric(
        "Общо",
        f"€ {lobby_total:.2f}"
    )


    guest_note = st.text_area(
        "Коментар към поръчката",
        placeholder=(
            "Например: Без лед, "
            "допълнителен лимон..."
        ),
        key="lobby_guest_note"
    )

    order_col1, order_col2 = st.columns(
        2
    )

    with order_col1:
        if st.button(
            "🗑️ Изчисти поръчката",
            key="clear_lobby_cart",
            use_container_width=True
        ):
            st.session_state.lobby_cart = {}
            st.rerun()

    with order_col2:
        if st.button(
            "✅ Изпрати поръчката",
            key="send_lobby_order",
            type="primary",
            use_container_width=True
        ):
            try:
                new_order_id = create_lobby_order(
                    selected_table_number=table_number,
                    selected_service_area=service_area,
                    guest_note=guest_note
                )

                st.session_state.lobby_cart = {}

                st.session_state.lobby_order_success = {
                    "order_id": new_order_id,
                    "table_number": table_number
                }

                if "lobby_guest_note" in st.session_state:
                    st.session_state.lobby_guest_note = ""

                st.rerun()

            except Exception as error:
                st.session_state.lobby_order_error = (
                    "Поръчката не беше изпратена."
                    "\n\n"
                    f"Причина: {error}"
                )

                st.rerun()


# =========================================================
# БРАНДИРАНЕ
# =========================================================
st.divider()

st.caption(
    "Powered by HMITSEVAPPS"
)
