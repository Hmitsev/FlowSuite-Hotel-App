import base64

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from lastoria.database.db import get_connection

# =====================================
# НАСТРОЙКИ НА СТРАНИЦАТА
# =====================================

st.set_page_config(
    page_title="Сервитьор",
    page_icon="🤵",
    layout="wide"
)

# =====================================
# BACKGROUND
# =====================================

def set_waiter_background():
    with open(
        "lastoria/assets/Designer (11).png",
        "rb"
    ) as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>

        .stApp {{
            background:
                linear-gradient(
                    rgba(0,0,0,0.55),
                    rgba(0,0,0,0.80)
                ),
                url("data:image/png;base64,{encoded}");

            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

set_waiter_background()
st.markdown("""
<style>

/* Главно заглавие */
h1 {
    color: #D4AF37 !important;
    text-shadow: 0 0 12px rgba(212,175,55,0.4);
}

/* Подзаглавия */
h2, h3 {
    color: #D4AF37 !important;
}

/* Текст */
p, label, span {
    color: #F5E6A8 !important;
}

/* Info box */
[data-testid="stAlert"] {
    background: rgba(0,0,0,0.55) !important;
    border: 1px solid rgba(212,175,55,0.35) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    color: #D4AF37 !important;
    font-weight: 600;
}

/* Активен таб */
.stTabs [aria-selected="true"] {
    color: #FFD700 !important;
    border-bottom: 2px solid #D4AF37 !important;
}

/* Статистика и броячи */
[data-testid="stMetricValue"] {
    color: #D4AF37 !important;
}
/* =====================================
   ВИБРИРАЩА КАМБАНКА
===================================== */

@keyframes bellShake {
    0% {
        transform: rotate(0deg);
    }

    15% {
        transform: rotate(18deg);
    }

    30% {
        transform: rotate(-16deg);
    }

    45% {
        transform: rotate(12deg);
    }

    60% {
        transform: rotate(-10deg);
    }

    75% {
        transform: rotate(6deg);
    }

    100% {
        transform: rotate(0deg);
    }
}

.notification-bell-box {
    text-align: center;
    font-size: 50px;
    line-height: 1;
    padding: 8px;
    animation: bellShake 0.85s ease-in-out infinite;
    transform-origin: 50% 10%;
}

.notification-bell-count {
    color: #FF4D4D !important;
    font-size: 24px !important;
    font-weight: 900 !important;
    vertical-align: top;
}
</style>
""", unsafe_allow_html=True)
# =====================================
# ДОСТЪП ДО СЕРВИТЬОР
# =====================================

WAITER_PASSWORD = "waiter2026"

if "waiter_auth" not in st.session_state:
    st.session_state.waiter_auth = False

if not st.session_state.waiter_auth:

    password = st.text_input(
        "Парола",
        type="password"
    )

    if st.button("Вход"):

        if password == WAITER_PASSWORD:

            st.session_state.waiter_auth = True
            st.rerun()

    st.stop()

# =====================================
# ИСТОРИЯ НА ПРИКЛЮЧЕНИ ПОРЪЧКИ (24Ч)
# =====================================

def get_completed_orders():

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                o.id AS order_id,
                rt.table_number,
                o.created_at,
                o.order_status,
                o.total_amount,
                oi.id AS order_item_id,
                mi.item_name,
                oi.quantity,
                oi.notes,
                mi.department,
                oi.kitchen_status
            FROM orders o
            JOIN restaurant_tables rt
                ON rt.id = o.table_id
            JOIN order_items oi
                ON oi.order_id = o.id
            JOIN menu_items mi
                ON mi.id = oi.item_id
            WHERE o.order_status = 'COMPLETED'
              AND o.completed_at >= NOW() - INTERVAL '24 HOURS'
            ORDER BY
                o.completed_at DESC,
                o.id DESC,
                oi.id ASC
        """)

        return cur.fetchall()

    finally:
        cur.close()
        conn.close()

# =====================================
# ЗАРЕЖДАНЕ НА АКТИВНИ ПОРЪЧКИ
# =====================================

def get_waiter_orders():

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT
                o.id AS order_id,
                rt.table_number,
                o.created_at,
                o.order_status,
                o.total_amount,
                oi.id AS order_item_id,
                mi.item_name,
                oi.quantity,
                oi.notes,
                mi.department,
                oi.kitchen_status
            FROM orders o
            JOIN restaurant_tables rt
                ON rt.id = o.table_id
            JOIN order_items oi
                ON oi.order_id = o.id
            JOIN menu_items mi
                ON mi.id = oi.item_id
            WHERE o.order_status <> 'COMPLETED'
              AND oi.kitchen_status IN (
                  'NEW',
                  'PREPARING',
                  'READY',
                  'SERVED'
              )
            ORDER BY
                o.created_at ASC,
                o.id ASC,
                oi.id ASC
            """
        )

        return cur.fetchall()

    finally:
        cur.close()
        conn.close()
# =====================================
# БРОЙ НОВИ ПОРЪЧКИ ЗА СЕРВИТЬОРА
# =====================================

def get_new_waiter_order_count():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT COUNT(DISTINCT o.id)
            FROM orders o
            WHERE o.order_status = 'NEW'
            """
        )

        result = cur.fetchone()

        return int(
            result[0] or 0
        )

    finally:
        cur.close()
        conn.close()


# =====================================
# БРОЙ АКТИВНИ ПОРЪЧКИ
# =====================================

active_rows = get_waiter_orders()

active_count = len(
    set(row[0] for row in active_rows)
)


# =====================================
# АВТОМАТИЧНО ОБНОВЯВАНЕ
# =====================================

st_autorefresh(
    interval=15000,
    key="waiter_refresh"
)

view_mode = st.radio(
    "Изглед",
    [
        f"🤵 Активни поръчки ({active_count})",
        "📜 История (24ч)"
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="waiter_view_mode"
)

# =====================================
# CALLBACK ЗА ЧЕКБОКСА
# =====================================

def handle_served_checkbox(
    order_item_id,
    checkbox_key,
    department
):
    is_checked = bool(
        st.session_state.get(
            checkbox_key,
            False
        )
    )

    if not is_checked:
        return

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            UPDATE order_items
            SET kitchen_status = 'SERVED'
            WHERE id = %s
            """,
            (order_item_id,)
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()

# =====================================
# ФИНАЛИЗИРАНЕ НА ПОРЪЧКА
# =====================================

def complete_order(order_id):

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            UPDATE orders
            SET
                order_status = 'COMPLETED',
                updated_at = CURRENT_TIMESTAMP,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (order_id,)
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()

# =====================================
# ИЗВЕСТИЯ
# =====================================
def get_waiter_notifications():

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
                table_id,
                notification_type,
                message,
                created_at
            FROM notifications
            WHERE is_read = FALSE
             AND notification_type = 'CALL_WAITER'
            ORDER BY created_at DESC
            """
        )

        return cur.fetchall()

    finally:

        cur.close()
        conn.close()



def mark_notification_read(notification_id):

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            UPDATE notifications
            SET is_read = TRUE
            WHERE id = %s
            """,
            (notification_id,)
        )

        conn.commit()

    finally:

        cur.close()
        conn.close()

# =====================================
# ЗАРЕЖДАНЕ НА БРОЯЧИТЕ
# =====================================

try:
    new_waiter_order_count = (
        get_new_waiter_order_count()
    )

except Exception:
    new_waiter_order_count = 0


try:
    notifications = get_waiter_notifications()

except Exception:
    notifications = []


unread_waiter_notification_count = len(
    notifications
)

total_waiter_notifications = (
    new_waiter_order_count
    + unread_waiter_notification_count
)
# =====================================
# ЗАГЛАВИЕ И КАМБАНКА
# =====================================

waiter_title_col, waiter_bell_col = st.columns(
    [6, 1.3],
    vertical_alignment="center"
)

with waiter_title_col:
    st.title("🤵 Сервитьор")

with waiter_bell_col:
    if total_waiter_notifications > 0:
        st.markdown(
            f"""
            <div class="notification-bell-box">
                🔔
                <span class="notification-bell-count">
                    {total_waiter_notifications}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

# =====================================
# ЗАРЕЖДАНЕ И ГРУПИРАНЕ ПО ПОРЪЧКА
# =====================================

if view_mode.startswith("🤵 Активни поръчки"):

    rows = active_rows

else:

    rows = get_completed_orders()


orders = {}

for row in rows:
    order_id = row[0]

    if order_id not in orders:
        orders[order_id] = {
            "table_number": row[1],
            "created_at": row[2],
            "order_status": row[3],
            "total_amount": row[4],
            "items": []
        }

    orders[order_id]["items"].append(
        {
            "row_id": row[5],
            "name": row[6],
            "quantity": row[7],
            "notes": row[8],
            "department": row[9],
            "status": row[10]
        }
    )


# =====================================
# ПОКАЗВАНЕ НА ПОРЪЧКИТЕ
# =====================================

if not orders:
    st.success("Няма активни поръчки.")

else:

    for order_id, order_data in orders.items():

        table_number = order_data["table_number"]
        created_at = order_data["created_at"]
        total_amount = order_data["total_amount"]
        items = order_data["items"]

        with st.container(border=True):

            title_col, details_col, waiter_col = st.columns([4, 2, 2])

            with title_col:

                st.subheader(
                    f"🍽️ Поръчка №{order_id}"
                )

                st.markdown(
                    f"""
                    <div style="
                        color:#FF8C42;
                        font-size:34px;
                        font-weight:800;
                        margin-top:5px;
                        margin-bottom:10px;
                    ">
                       Маса № {table_number}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with details_col:

                if created_at:

                    from datetime import timedelta

                    local_time = created_at + timedelta(hours=3)
                    
                    st.caption(
                        "Получена: "
                        f"{local_time.strftime('%H:%M:%S')}"
                    )

                if total_amount is not None:

                    st.markdown(
                        f"**Общо: € {float(total_amount):.2f}**"
                    )

            with waiter_col:

                selected_waiter = st.selectbox(
                    "🤵 Сервитьор",
                    [
                        "Сервитьор 1",
                        "Сервитьор 2",
                        "Сервитьор 3",
                        "Сервитьор 4",
                        "Сервитьор 5"
                    ],
                    key=f"waiter_{order_id}"
                )
            # =====================================
            # ОБЩ СТАТУС
            # =====================================

            all_served_status = True
            all_ready_or_served = True
            
            for item in items:
            
                department = str(
                    item["department"] or ""
                ).lower()
            
                status = item["status"]
            
                # напитките винаги са готови
                if department == "bar":
                    continue
            
                if status != "SERVED":
                    all_served_status = False
            
                if status not in ("READY", "SERVED"):
                    all_ready_or_served = False

            any_preparing = any(
                item["status"] == "PREPARING"
                for item in items
            )

            if all_served_status:
                st.success(
                    "✅ ВСИЧКИ АРТИКУЛИ СА СЕРВИРАНИ"
                )
            elif all_ready_or_served:
                st.success(
                    "🟢 ПОРЪЧКАТА Е ГОТОВА"
                )
            elif any_preparing:
                st.warning(
                    "🟡 ПОРЪЧКАТА Е В ПОДГОТОВКА"
                )
            else:
                st.error(
                    "🔴 НОВА ПОРЪЧКА"
                )

            # =====================================
            # АРТИКУЛИ И ЧЕКБОКСИ
            # =====================================

            st.markdown("#### Артикули")

            for item in items:
                item_row_id = item["row_id"]
                item_name = item["name"]
                quantity = item["quantity"]
                notes = item["notes"]
                department = str(
                    item["department"] or ""
                ).lower()
                item_status = item["status"]

                item_col, status_col, served_col = st.columns(
                    [5, 2, 2],
                    vertical_alignment="center"
                )

                with item_col:
                    st.write(
                        f"**{item_name} x{quantity}**"
                    )

                    if notes:
                        st.caption(
                            f"📝 Коментар: {notes}"
                        )

                with status_col:
                    if item_status == "SERVED":
                        st.info("✅ Сервирано")
                    elif department == "bar":
                        st.info("🥛 Напитка")
                    elif item_status == "NEW":
                        st.error("🔴 Нова")
                    elif item_status == "PREPARING":
                        st.warning("🟡 Приготвя се")
                    elif item_status == "READY":
                        st.success("🟢 Готово")

                with served_col:
                    checkbox_key = (
                        f"waiter_served_{order_id}_{item_row_id}"
                    )

                    is_bar_item = department == "bar"

                    can_be_served = (
                        is_bar_item
                        or item_status in ("READY", "SERVED")
                    )

                    st.checkbox(
                        "Сервирано",
                        value=(
                            item_status == "SERVED"
                        ),
                        disabled=(
                            item_status == "SERVED"
                            or not can_be_served
                        ),
                        key=checkbox_key,
                        on_change=handle_served_checkbox,
                        args=(
                            item_row_id,
                            checkbox_key,
                            department
                        )
                    )

                    
                    st.divider()

            # =====================================
            # ОБОБЩЕНИЕ
            # =====================================

            ready_count = sum(
                1
                for item in items
                if item["status"] == "READY"
            )

            served_count = sum(
                1
                for item in items
                if item["status"] == "SERVED"
            )

            total_count = len(items)

            progress_col1, progress_col2 = st.columns(2)

            with progress_col1:
                st.write(
                    f"🟢 Готови за сервиране: {ready_count}"
                )

            with progress_col2:
                st.write(
                    f"✅ Сервирани: {served_count}/{total_count}"
                )

            if total_count > 0:
                st.progress(
                    served_count / total_count
                )

            

            # =====================================
            # ФИНАЛЕН БУТОН
            # =====================================

            if st.button(
                "✅ Финализирай поръчката",
                key=f"complete_{order_id}",
                type="primary",
                disabled=not all_ready_or_served,
                use_container_width=True
            ):
                try:
                    complete_order(order_id)

                    st.rerun()

                except Exception as error:
                    st.error(
                        f"Грешка при финализиране: {error}"
                    )

            if not all_ready_or_served:
                st.caption(
                    "Финализирането ще се активира, "
                    "когато всички артикули са отбелязани "
                    "като сервирани."
                )
