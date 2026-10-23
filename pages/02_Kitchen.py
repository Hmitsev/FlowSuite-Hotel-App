import base64
from pathlib import Path

import streamlit as st

from database.db import get_connection


# =====================================
# НАСТРОЙКИ НА СТРАНИЦАТА
# =====================================
st.set_page_config(
    page_title="Room Service Kitchen",
    page_icon="👨‍🍳",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =====================================
# BACKGROUND
# =====================================
BACKGROUND_CANDIDATES = [
    "Designer (10).png",
    "kitchen_background.png",
    "kitchen_banner.png",
    "Screenshot 2026-09-09 025744.png",
]


def find_asset(file_names):
    for file_name in file_names:
        file_path = Path("assets") / file_name
        if file_path.exists():
            return file_path
    return None


@st.cache_data
def get_base64_image(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


background_path = find_asset(BACKGROUND_CANDIDATES)
background_css = ""

if background_path:
    background_base64 = get_base64_image(background_path)
    background_css = f"""
        background-image:
            linear-gradient(
                rgba(3, 5, 8, 0.76),
                rgba(3, 5, 8, 0.92)
            ),
            url("data:image/png;base64,{background_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    """


# =====================================
# CSS
# =====================================
st.markdown(
    f"""
    <style>
    .stApp {{
        {background_css}
        background-color: #080B12;
        color: #F5E6C8;
    }}

    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stStatusWidget"],
    [data-testid="stSpinner"],
    .stSpinner {{ display: none !important; }}
    footer {{ visibility: hidden; }}

    .block-container {{
        max-width: 1500px;
        padding-top: 1.2rem;
        padding-bottom: 4rem;
    }}

    h1, h2, h3, h4 {{ color: #F5E6C8 !important; }}
    p, label, span {{ color: #F5E6C8; }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(7, 11, 18, 0.90);
        border: 1px solid rgba(212, 175, 55, 0.34);
        border-radius: 18px;
        box-shadow: 0 14px 35px rgba(0, 0, 0, 0.30);
    }}

    [data-testid="stMetric"] {{
        background: rgba(7, 11, 18, 0.78);
        border: 1px solid rgba(212, 175, 55, 0.28);
        border-radius: 16px;
        padding: 16px;
    }}

    [data-testid="stAlert"] {{
        background: rgba(7, 11, 18, 0.90);
        border: 1px solid rgba(212, 175, 55, 0.30);
        border-radius: 14px;
    }}

    div[data-testid="stButton"] button {{
        border-radius: 12px;
        font-weight: 700;
        min-height: 44px;
    }}

    div[data-testid="stButton"] button[kind="primary"] {{
        background: linear-gradient(135deg, #B98528, #D4AF37, #F5D77B) !important;
        border: 1px solid #F5D77B !important;
        color: #111111 !important;
        font-weight: 800 !important;
    }}

    div[data-testid="stButton"] button[kind="primary"] p {{
        color: #111111 !important;
        font-weight: 800 !important;
    }}

    @media only screen and (max-width: 768px) {{
        .block-container {{
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }}
        h1 {{ font-size: 30px !important; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================
# SESSION STATE
# =====================================
if "kitchen_auth" not in st.session_state:
    st.session_state.kitchen_auth = False
if "kitchen_message" not in st.session_state:
    st.session_state.kitchen_message = None
if "kitchen_error" not in st.session_state:
    st.session_state.kitchen_error = None


# =====================================
# ДОСТЪП ДО КУХНЯТА
# =====================================
KITCHEN_PASSWORD = "kitchen2026"

if not st.session_state.kitchen_auth:
    st.title("👨‍🍳 Room Service Kitchen")
    st.caption("Достъп до активните хотелски поръчки")

    password = st.text_input(
        "Парола",
        type="password",
        key="kitchen_password",
    )

    if st.button(
        "Вход",
        key="kitchen_login",
        type="primary",
        use_container_width=True,
    ):
        if password == KITCHEN_PASSWORD:
            st.session_state.kitchen_auth = True
            st.rerun()
        else:
            st.error("Невалидна парола.")
    st.stop()


# =====================================
# ГОРНА ЛЕНТА
# =====================================
title_col, logout_col = st.columns([6, 1])

with title_col:
    st.markdown(
        """
        <div style="
            text-align:center;
            color:#D4AF37;
            font-size:34px;
            font-weight:900;
            letter-spacing:1px;
            padding-top:4px;
        ">
            👨‍🍳 ROOM SERVICE KITCHEN
        </div>
        """,
        unsafe_allow_html=True,
    )

with logout_col:
    if st.button(
        "🚪 Изход",
        key="kitchen_logout",
        use_container_width=True,
    ):
        st.session_state.kitchen_auth = False
        st.rerun()


# =====================================
# ROOM SERVICE: ЗАРЕЖДАНЕ
# =====================================
def get_kitchen_orders():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT
                rso.id AS order_id,
                hr.room_number,
                rso.created_at,
                rso.order_status,
                rso.total_amount,
                rsoi.id AS order_item_id,
                rsoi.item_id,
                rsoi.item_name,
                rsoi.quantity,
                rsoi.unit_price,
                rsoi.notes,
                rsoi.item_status
            FROM room_service_orders rso
            JOIN hotel_rooms hr
                ON hr.id = rso.room_id
            JOIN room_service_order_items rsoi
                ON rsoi.order_id = rso.id
            WHERE rso.order_status IN ('NEW', 'PREPARING')
              AND LOWER(rsoi.item_name) NOT LIKE '%water%'
              AND LOWER(rsoi.item_name) NOT LIKE '%cola%'
              AND LOWER(rsoi.item_name) NOT LIKE '%coca%'
              AND LOWER(rsoi.item_name) NOT LIKE '%sprite%'
              AND LOWER(rsoi.item_name) NOT LIKE '%fanta%'
              AND LOWER(rsoi.item_name) NOT LIKE '%juice%'
              AND LOWER(rsoi.item_name) NOT LIKE '%tea%'
              AND LOWER(rsoi.item_name) NOT LIKE '%coffee%'
              AND LOWER(rsoi.item_name) NOT LIKE '%espresso%'
              AND LOWER(rsoi.item_name) NOT LIKE '%cappuccino%'
              AND LOWER(rsoi.item_name) NOT LIKE '%whiskey%'
              AND LOWER(rsoi.item_name) NOT LIKE '%vodka%'
              AND LOWER(rsoi.item_name) NOT LIKE '%wine%'
              AND LOWER(rsoi.item_name) NOT LIKE '%beer%'
            ORDER BY rso.created_at ASC, rso.id ASC, rsoi.id ASC
            """
        )
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


# =====================================
# LOBBY BAR: ЗАРЕЖДАНЕ НА КУХНЕНСКИ АРТИКУЛИ
# =====================================
def get_lobby_kitchen_orders():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT
                lbo.id AS order_id,
                lbo.table_number,
                lbo.created_at,
                lbo.order_status,
                lbo.total_amount,
                lbi.id AS order_item_id,
                lbi.item_name,
                lbi.quantity,
                lbi.unit_price,
                lbi.item_status
            FROM lobby_bar_orders lbo
            JOIN lobby_bar_order_items lbi
                ON lbi.order_id = lbo.id
            WHERE UPPER(COALESCE(lbi.department, 'BAR')) = 'KITCHEN'
              AND COALESCE(lbo.order_status, 'NEW') NOT IN ('COMPLETED', 'CANCELLED')
              AND COALESCE(lbi.item_status, 'NEW') NOT IN ('READY', 'COMPLETED', 'CANCELLED')
            ORDER BY lbo.created_at ASC, lbo.id ASC, lbi.id ASC
            """
        )
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


# =====================================
# ROOM SERVICE: СТАТУСИ
# =====================================
def start_order(order_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE room_service_orders
            SET order_status = 'PREPARING', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND order_status IN ('NEW', 'PREPARING')
            """,
            (order_id,),
        )
        cur.execute(
            """
            UPDATE room_service_order_items
            SET item_status = 'PREPARING'
            WHERE order_id = %s
              AND COALESCE(item_status, 'NEW') IN ('NEW', 'PREPARING')
            """,
            (order_id,),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def finish_order(order_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE room_service_orders
            SET order_status = 'READY', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND order_status IN ('NEW', 'PREPARING')
            """,
            (order_id,),
        )
        cur.execute(
            """
            UPDATE room_service_order_items
            SET item_status = 'READY'
            WHERE order_id = %s
              AND COALESCE(item_status, 'NEW') IN ('NEW', 'PREPARING')
            """,
            (order_id,),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# =====================================
# LOBBY BAR: СТАТУСИ НА КУХНЕНСКИТЕ АРТИКУЛИ
# =====================================
def start_lobby_kitchen_order(order_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE lobby_bar_order_items
            SET item_status = 'PREPARING'
            WHERE order_id = %s
              AND UPPER(COALESCE(department, 'BAR')) = 'KITCHEN'
              AND COALESCE(item_status, 'NEW') IN ('NEW', 'PREPARING')
            """,
            (order_id,),
        )
        cur.execute(
            """
            UPDATE lobby_bar_orders
            SET order_status = 'PREPARING'
            WHERE id = %s
              AND COALESCE(order_status, 'NEW') NOT IN ('COMPLETED', 'CANCELLED')
            """,
            (order_id,),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def finish_lobby_kitchen_order(order_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE lobby_bar_order_items
            SET item_status = 'READY'
            WHERE order_id = %s
              AND UPPER(COALESCE(department, 'BAR')) = 'KITCHEN'
              AND COALESCE(item_status, 'NEW') IN ('NEW', 'PREPARING')
            """,
            (order_id,),
        )

        # Родителската поръчка става READY само ако всички нейни артикули са готови.
        cur.execute(
            """
            UPDATE lobby_bar_orders
            SET order_status = CASE
                WHEN NOT EXISTS (
                    SELECT 1
                    FROM lobby_bar_order_items
                    WHERE order_id = %s
                      AND COALESCE(item_status, 'NEW') NOT IN ('READY', 'COMPLETED', 'CANCELLED')
                ) THEN 'READY'
                ELSE 'PREPARING'
            END
            WHERE id = %s
              AND COALESCE(order_status, 'NEW') NOT IN ('COMPLETED', 'CANCELLED')
            """,
            (order_id, order_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# =====================================
# ПОМОЩНИ ФУНКЦИИ
# =====================================
def group_room_service_orders(rows):
    orders = {}
    for row in rows:
        order_id = row[0]
        if order_id not in orders:
            orders[order_id] = {
                "room_number": row[1],
                "created_at": row[2],
                "order_status": row[3],
                "total_amount": row[4],
                "items": [],
            }
        orders[order_id]["items"].append(
            {
                "order_item_id": row[5],
                "item_id": row[6],
                "item_name": row[7],
                "quantity": row[8],
                "unit_price": row[9],
                "notes": row[10],
                "item_status": row[11] or "NEW",
            }
        )
    return orders


def group_lobby_orders(rows):
    orders = {}
    for row in rows:
        order_id = row[0]
        if order_id not in orders:
            orders[order_id] = {
                "table_number": row[1],
                "created_at": row[2],
                "order_status": row[3] or "NEW",
                "total_amount": row[4],
                "items": [],
            }
        orders[order_id]["items"].append(
            {
                "order_item_id": row[5],
                "item_name": row[6],
                "quantity": row[7],
                "unit_price": row[8],
                "item_status": row[9] or "NEW",
            }
        )
    return orders


def show_item_status(status):
    normalized = (status or "NEW").upper()
    if normalized == "NEW":
        st.error("🔴 Ново")
    elif normalized == "PREPARING":
        st.warning("🟡 Приготвя се")
    elif normalized in ("READY", "COMPLETED"):
        st.success("🟢 Готово")
    else:
        st.info(f"Статус: {normalized}")


# =====================================
# АВТОМАТИЧНО ОБНОВЯВАНЕ
# =====================================
@st.fragment(run_every="15s")
def kitchen_live_dashboard():
    if st.session_state.kitchen_message:
        st.success(st.session_state.kitchen_message)
        st.session_state.kitchen_message = None

    if st.session_state.kitchen_error:
        st.error(st.session_state.kitchen_error)
        st.session_state.kitchen_error = None

    try:
        room_rows = get_kitchen_orders()
        lobby_rows = get_lobby_kitchen_orders()
    except Exception as error:
        st.error(
            "Поръчките не могат да бъдат заредени.\n\n"
            f"Причина: {error}"
        )
        return

    room_orders = group_room_service_orders(room_rows)
    lobby_orders = group_lobby_orders(lobby_rows)

    all_orders = list(room_orders.values()) + list(lobby_orders.values())
    new_orders = sum(
        1 for order in all_orders
        if (order["order_status"] or "NEW").upper() == "NEW"
    )
    preparing_orders = sum(
        1 for order in all_orders
        if (order["order_status"] or "NEW").upper() == "PREPARING"
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        st.metric("Всички активни", len(room_orders) + len(lobby_orders))
    with metric_col2:
        st.metric("Room Service", len(room_orders))
    with metric_col3:
        st.metric("Lobby Bar → Kitchen", len(lobby_orders))
    with metric_col4:
        st.metric("Нови / В подготовка", f"{new_orders} / {preparing_orders}")

    st.divider()

    # =====================================
    # ROOM SERVICE
    # =====================================
    st.markdown("## 🛎️ Room Service поръчки")

    if not room_orders:
        st.success("Няма активни Room Service поръчки.")
    else:
        for order_id, order_data in room_orders.items():
            order_status = (order_data["order_status"] or "NEW").upper()
            created_at = order_data["created_at"]
            total_amount = float(order_data["total_amount"] or 0)

            with st.container(border=True):
                title_col, time_col, total_col = st.columns([4, 2, 2])

                with title_col:
                    st.subheader(f"🍽️ Room Service Order #{order_id}")
                    st.markdown(f"### 🛎️ Стая №{order_data['room_number']}")

                with time_col:
                    if created_at:
                        st.caption(
                            "Получена: "
                            f"{created_at.strftime('%d.%m.%Y %H:%M')}"
                        )
                    if order_status == "NEW":
                        st.error("🔴 НОВА ПОРЪЧКА")
                    elif order_status == "PREPARING":
                        st.warning("🟡 В ПОДГОТОВКА")

                with total_col:
                    st.metric("Общо", f"€ {total_amount:.2f}")

                st.markdown("#### Артикули")
                for item in order_data["items"]:
                    item_col, status_col = st.columns(
                        [5, 2],
                        vertical_alignment="center",
                    )
                    with item_col:
                        st.write(f"**{item['item_name']} x{item['quantity']}**")
                        if item["notes"]:
                            st.caption(f"📝 Коментар: {item['notes']}")
                    with status_col:
                        show_item_status(item["item_status"])
                    st.divider()

                preparing_col, ready_col = st.columns(2)
                with preparing_col:
                    if st.button(
                        "🟡 Започни подготовката",
                        key=f"room_start_{order_id}",
                        use_container_width=True,
                        disabled=(order_status == "PREPARING"),
                    ):
                        try:
                            start_order(order_id)
                            st.session_state.kitchen_message = (
                                f"Room Service поръчка №{order_id} е в подготовка."
                            )
                        except Exception as error:
                            st.session_state.kitchen_error = (
                                "Статусът не беше обновен. "
                                f"Причина: {error}"
                            )
                        st.rerun(scope="fragment")

                with ready_col:
                    if st.button(
                        "✅ Цялата поръчка е готова",
                        key=f"room_finish_{order_id}",
                        type="primary",
                        use_container_width=True,
                    ):
                        try:
                            finish_order(order_id)
                            st.session_state.kitchen_message = (
                                f"Room Service поръчка №{order_id} е готова за доставка."
                            )
                        except Exception as error:
                            st.session_state.kitchen_error = (
                                "Поръчката не беше отбелязана като готова. "
                                f"Причина: {error}"
                            )
                        st.rerun(scope="fragment")

    st.divider()

    # =====================================
    # LOBBY BAR → KITCHEN
    # =====================================
    st.markdown("## 🍴 Поръчки от Lobby Bar за кухнята")

    if not lobby_orders:
        st.success("Няма активни кухненски артикули от Lobby Bar.")
    else:
        for order_id, order_data in lobby_orders.items():
            order_status = (order_data["order_status"] or "NEW").upper()
            created_at = order_data["created_at"]
            kitchen_total = sum(
                float(item["unit_price"] or 0) * float(item["quantity"] or 0)
                for item in order_data["items"]
            )

            with st.container(border=True):
                title_col, time_col, total_col = st.columns([4, 2, 2])

                with title_col:
                    st.subheader(f"🍴 Lobby Bar Order #{order_id}")
                    table_number = order_data["table_number"]
                    st.markdown(f"### 🪑 Маса №{table_number}")

                with time_col:
                    if created_at:
                        st.caption(
                            "Получена: "
                            f"{created_at.strftime('%d.%m.%Y %H:%M')}"
                        )
                    if order_status == "NEW":
                        st.error("🔴 НОВА ПОРЪЧКА")
                    else:
                        st.warning("🟡 В ПОДГОТОВКА")

                with total_col:
                    st.metric("Кухня", f"€ {kitchen_total:.2f}")

                st.markdown("#### Артикули за кухнята")
                for item in order_data["items"]:
                    item_col, status_col = st.columns(
                        [5, 2],
                        vertical_alignment="center",
                    )
                    with item_col:
                        st.write(f"**{item['item_name']} x{item['quantity']}**")
                    with status_col:
                        show_item_status(item["item_status"])
                    st.divider()

                preparing_col, ready_col = st.columns(2)
                kitchen_is_preparing = all(
                    (item["item_status"] or "NEW").upper() == "PREPARING"
                    for item in order_data["items"]
                )

                with preparing_col:
                    if st.button(
                        "🟡 Започни подготовката",
                        key=f"lobby_start_{order_id}",
                        use_container_width=True,
                        disabled=kitchen_is_preparing,
                    ):
                        try:
                            start_lobby_kitchen_order(order_id)
                            st.session_state.kitchen_message = (
                                f"Кухненските артикули от Lobby Bar поръчка №{order_id} "
                                "са в подготовка."
                            )
                        except Exception as error:
                            st.session_state.kitchen_error = (
                                "Статусът на Lobby Bar поръчката не беше обновен. "
                                f"Причина: {error}"
                            )
                        st.rerun(scope="fragment")

                with ready_col:
                    if st.button(
                        "✅ Кухненските артикули са готови",
                        key=f"lobby_finish_{order_id}",
                        type="primary",
                        use_container_width=True,
                    ):
                        try:
                            finish_lobby_kitchen_order(order_id)
                            st.session_state.kitchen_message = (
                                f"Кухненските артикули от Lobby Bar поръчка №{order_id} "
                                "са готови."
                            )
                        except Exception as error:
                            st.session_state.kitchen_error = (
                                "Артикулите не бяха отбелязани като готови. "
                                f"Причина: {error}"
                            )
                        st.rerun(scope="fragment")


# =====================================
# СТАРТИРАНЕ НА LIVE DASHBOARD
# =====================================
kitchen_live_dashboard()


# =====================================
# БРАНДИРАНЕ
# =====================================
st.caption("Powered by HMITSEVAPPS")
