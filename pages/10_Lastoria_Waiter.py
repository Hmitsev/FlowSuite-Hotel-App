import base64
import uuid
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from lastoria.database.db import get_connection


# =====================================
# НАСТРОЙКИ НА СТРАНИЦАТА
# =====================================

st.set_page_config(
    page_title="Сервитьор",
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.markdown("""
<style>

[data-testid="stSidebar"] {
    display:none !important;
}

section[data-testid="stSidebar"] {
    display:none !important;
}

</style>
""", unsafe_allow_html=True)
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
# ПРИКЛЮЧЕНИ СМЕТКИ ЗА ПОСЛЕДНИТЕ 24 ЧАСА
# =====================================

def get_completed_orders():

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT
                o.id AS order_id,
                rt.table_number,
                o.created_at,
                o.completed_at,
                o.order_status,
                o.total_amount,
                o.checkout_group_id,
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
                o.id ASC,
                oi.id ASC
            """
        )

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
                  'READY'
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
# ТЕКУЩИ НЕПРИКЛЮЧЕНИ СМЕТКИ ПО МАСИ
# =====================================

def get_open_table_bills():

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT
                o.id AS order_id,
                o.table_id,
                rt.table_number,
                o.created_at,
                o.order_status,
                COALESCE(o.total_amount, 0) AS total_amount,
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
            ORDER BY
                rt.table_number ASC,
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
    interval=35000,
    key="waiter_refresh"
)

view_mode = st.radio(
    "Изглед",
    [
        f"🤵 Активни поръчки ({active_count})",
        "🧾 Сметки по маси",
        "📜 Приключени за 24ч"
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
# ПРИКЛЮЧВАНЕ НА ЦЯЛАТА СМЕТКА НА МАСАТА
# =====================================

def complete_table_bill(table_id):

    checkout_group_id = str(uuid.uuid4())

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Заключваме всички текущи поръчки на масата.
        cur.execute(
            """
            SELECT id
            FROM orders
            WHERE table_id = %s
              AND order_status <> 'COMPLETED'
            FOR UPDATE
            """,
            (table_id,)
        )

        order_rows = cur.fetchall()
        order_ids = [
            row[0]
            for row in order_rows
        ]

        if not order_ids:
            raise ValueError(
                "Няма активни поръчки за тази маса."
            )

        # Проверяваме дали има храна, която все още
        # не е готова или сервирана.
        # Напитките от BAR не блокират плащането.
        cur.execute(
            """
            SELECT COUNT(*)
            FROM order_items oi
            JOIN menu_items mi
                ON mi.id = oi.item_id
            WHERE oi.order_id = ANY(%s)
              AND LOWER(
                    COALESCE(mi.department, '')
                  ) <> 'bar'
              AND oi.kitchen_status NOT IN (
                    'READY',
                    'SERVED'
                  )
            """,
            (order_ids,)
        )

        result = cur.fetchone()
        blocked_items = int(
            result[0] or 0
        )

        if blocked_items > 0:
            raise ValueError(
                "Масата не може да бъде приключена, "
                "защото има артикули, които още "
                "не са готови."
            )

        # Всички готови артикули се отбелязват
        # автоматично като сервирани.
        cur.execute(
            """
            UPDATE order_items
            SET kitchen_status = 'SERVED'
            WHERE order_id = ANY(%s)
              AND kitchen_status = 'READY'
            """,
            (order_ids,)
        )

        # Всички поръчки от масата се приключват
        # като една обща сметка.
        cur.execute(
            """
            UPDATE orders
            SET
                order_status = 'COMPLETED',
                checkout_group_id = %s,
                updated_at = CURRENT_TIMESTAMP,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = ANY(%s)
            """,
            (
                checkout_group_id,
                order_ids
            )
        )

        conn.commit()

        return checkout_group_id

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
# ГРУПИРАНЕ НА ТЕКУЩИТЕ СМЕТКИ ПО МАСИ
# =====================================

def build_open_table_bills(rows):

    table_bills = {}

    for row in rows:

        order_id = row[0]
        table_id = row[1]
        table_number = row[2]
        created_at = row[3]
        total_amount = row[5]

        order_item = {
            "row_id": row[6],
            "name": row[7],
            "quantity": row[8],
            "notes": row[9],
            "department": row[10],
            "status": row[11],
            "order_id": order_id
        }

        if table_id not in table_bills:
            table_bills[table_id] = {
                "table_id": table_id,
                "table_number": table_number,
                "first_order_at": created_at,
                "order_ids": [],
                "orders_total": {},
                "items": []
            }

        table_bill = table_bills[table_id]

        if order_id not in table_bill["order_ids"]:
            table_bill["order_ids"].append(
                order_id
            )

            table_bill["orders_total"][order_id] = float(
                total_amount or 0
            )

        if (
            created_at
            and (
                table_bill["first_order_at"] is None
                or created_at
                < table_bill["first_order_at"]
            )
        ):
            table_bill["first_order_at"] = created_at

        table_bill["items"].append(
            order_item
        )

    for table_bill in table_bills.values():
        table_bill["grand_total"] = sum(
            table_bill["orders_total"].values()
        )

    return table_bills


# =====================================
# ГРУПИРАНЕ НА ПРИКЛЮЧЕНИТЕ СМЕТКИ
# =====================================

def build_completed_table_bills(rows):

    completed_bills = {}

    for row in rows:

        order_id = row[0]
        table_number = row[1]
        created_at = row[2]
        completed_at = row[3]
        total_amount = row[5]
        checkout_group_id = row[6]

        # Старите приключени поръчки може да нямат
        # checkout_group_id. Те остават отделни.
        if checkout_group_id:
            group_key = str(
                checkout_group_id
            )
        else:
            group_key = (
                f"legacy_order_{order_id}"
            )

        if group_key not in completed_bills:
            completed_bills[group_key] = {
                "checkout_group_id": checkout_group_id,
                "table_number": table_number,
                "created_at": created_at,
                "completed_at": completed_at,
                "order_ids": [],
                "orders_total": {},
                "items": []
            }

        completed_bill = completed_bills[
            group_key
        ]

        if order_id not in completed_bill["order_ids"]:
            completed_bill["order_ids"].append(
                order_id
            )

            completed_bill["orders_total"][order_id] = float(
                total_amount or 0
            )

        completed_bill["items"].append(
            {
                "row_id": row[7],
                "name": row[8],
                "quantity": row[9],
                "notes": row[10],
                "department": row[11],
                "status": row[12],
                "order_id": order_id
            }
        )

    for completed_bill in completed_bills.values():
        completed_bill["grand_total"] = sum(
            completed_bill[
                "orders_total"
            ].values()
        )

    return completed_bills

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
    st.title(" Сервитьор")

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
# ПОВИКВАНИЯ НА СЕРВИТЬОР
# =====================================

if notifications:

    st.markdown("### 🔔 Повиквания")

    for notification in notifications:

        notification_id = notification[0]
        table_id = notification[1]
        message = notification[3]

        col1, col2 = st.columns([5, 1])

        with col1:
            st.warning(message)

        with col2:

            if st.button(
                "✅ Обслужена",
                key=f"read_notification_{notification_id}"
            ):

                mark_notification_read(
                    notification_id
                )

                st.rerun()
# =====================================
# КОМПАКТЕН ИЗГЛЕД: СМЕТКИ ПО МАСИ
# =====================================

if view_mode == "🧾 Сметки по маси":

    open_bill_rows = get_open_table_bills()

    table_bills = build_open_table_bills(
        open_bill_rows
    )

    if not table_bills:
        st.success(
            "Няма отворени сметки по маси."
        )

    else:
        st.caption(
            "Всички неприключени поръчки от една "
            "маса са събрани в една обща сметка."
        )

        for table_id, table_bill in table_bills.items():

            table_number = table_bill[
                "table_number"
            ]

            order_ids = table_bill[
                "order_ids"
            ]

            items = table_bill[
                "items"
            ]

            grand_total = table_bill[
                "grand_total"
            ]

            first_order_at = table_bill[
                "first_order_at"
            ]

            blocking_items = [
                item
                for item in items
                if (
                    str(
                        item["department"] or ""
                    ).lower() != "bar"
                    and item["status"] not in (
                        "READY",
                        "SERVED"
                    )
                )
            ]

            can_complete_table = (
                len(blocking_items) == 0
            )

            with st.container(border=True):

                header_col, total_col = st.columns(
                    [5, 2],
                    vertical_alignment="center"
                )

                with header_col:
                    display_table = (
                        "🥡 TAKEAWAY"
                        if int(table_number) == 999
                        else f"🍽️ Маса № {table_number}"
                    )
                    
                    st.markdown(
                        f"""
                        <div style="
                            color:#FF8C42;
                            font-size:34px;
                            font-weight:900;
                        ">
                            {display_table}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    order_numbers = ", ".join(
                        f"№{order_id}"
                        for order_id in order_ids
                    )

                    st.caption(
                        "Поръчки в сметката: "
                        f"{order_numbers}"
                    )

                    if first_order_at:
                        st.caption(
                            "Сметката е отворена от: "
                            f"{first_order_at.strftime('%d.%m.%Y %H:%M')}"
                        )

                with total_col:
                    st.metric(
                        "Обща сметка",
                        f"€ {grand_total:.2f}"
                    )

                st.markdown(
                    "#### Обобщени артикули"
                )

                consolidated_items = {}

                for item in items:

                    item_key = (
                        item["name"],
                        item["notes"] or ""
                    )

                    if item_key not in consolidated_items:
                        consolidated_items[item_key] = {
                            "name": item["name"],
                            "quantity": 0,
                            "notes": item["notes"]
                        }

                    consolidated_items[
                        item_key
                    ]["quantity"] += int(
                        item["quantity"] or 0
                    )

                for consolidated_item in (
                    consolidated_items.values()
                ):

                    item_col, quantity_col = st.columns(
                        [6, 1],
                        vertical_alignment="center"
                    )

                    with item_col:
                        st.write(
                            f"**{consolidated_item['name']}**"
                        )

                        if consolidated_item["notes"]:
                            st.caption(
                                "📝 "
                                f"{consolidated_item['notes']}"
                            )

                    with quantity_col:
                        st.write(
                            f"**x{consolidated_item['quantity']}**"
                        )

                st.divider()

                if can_complete_table:
                    st.success(
                        "✅ Сметката е готова "
                        "за приключване."
                    )

                else:
                    st.warning(
                        f"⏳ Има {len(blocking_items)} "
                        "артикула, които още не са готови."
                    )

                confirm_payment = st.checkbox(
                    "Потвърждавам, че сметката е платена",
                    key=f"confirm_table_payment_{table_id}",
                    disabled=not can_complete_table
                )

                button_text = (
                    f"💳 Приключи и плати Маса № {table_number}"
                )

                if st.button(
                    button_text,
                    key=f"complete_table_bill_{table_id}",
                    type="primary",
                    use_container_width=True,
                    disabled=(
                        not can_complete_table
                        or not confirm_payment
                    )
                ):
                    try:
                        complete_table_bill(
                            table_id
                        )

                        st.success(
                            f"Маса № {table_number} "
                            "е приключена."
                        )

                        st.rerun()

                    except Exception as error:
                        st.error(
                            "Грешка при приключване: "
                            f"{error}"
                        )

    st.stop()

# =====================================
# КОМПАКТЕН АРХИВ НА ПРИКЛЮЧЕНИТЕ СМЕТКИ
# =====================================

if view_mode == "📜 Приключени за 24ч":

    completed_rows = get_completed_orders()

    completed_bills = build_completed_table_bills(
        completed_rows
    )

    if not completed_bills:
        st.info(
            "Няма приключени сметки през "
            "последните 24 часа."
        )

    else:
        daily_total = sum(
            bill["grand_total"]
            for bill in completed_bills.values()
        )

        metric_col1, metric_col2 = st.columns(2)

        with metric_col1:
            st.metric(
                "Приключени сметки",
                len(completed_bills)
            )

        with metric_col2:
            st.metric(
                "Общ оборот за последните 24 часа",
                f"€ {daily_total:.2f}"
            )

        for group_key, bill in completed_bills.items():

            table_number = bill["table_number"]
            order_ids = bill["order_ids"]
            items = bill["items"]
            grand_total = bill["grand_total"]
            completed_at = bill["completed_at"]

            expander_title = (
                f"🍽️ Маса № {table_number}"
                f"  |  € {grand_total:.2f}"
            )

            with st.expander(
                expander_title,
                expanded=False
            ):

                order_numbers = ", ".join(
                    f"№{order_id}"
                    for order_id in order_ids
                )

                st.write(
                    f"**Поръчки:** {order_numbers}"
                )

                if completed_at:
                    st.write(
                        "**Приключена:** "
                        f"{completed_at.strftime('%d.%m.%Y %H:%M')}"
                    )

                consolidated_items = {}

                for item in items:

                    item_key = (
                        item["name"],
                        item["notes"] or ""
                    )

                    if item_key not in consolidated_items:
                        consolidated_items[item_key] = {
                            "name": item["name"],
                            "quantity": 0,
                            "notes": item["notes"]
                        }

                    consolidated_items[
                        item_key
                    ]["quantity"] += int(
                        item["quantity"] or 0
                    )

                for consolidated_item in (
                    consolidated_items.values()
                ):

                    st.write(
                        "• "
                        f"{consolidated_item['name']} "
                        f"x{consolidated_item['quantity']}"
                    )

                    if consolidated_item["notes"]:
                        st.caption(
                            "📝 "
                            f"{consolidated_item['notes']}"
                        )

                st.divider()

                st.markdown(
                    f"### Общо: € {grand_total:.2f}"
                )

    st.stop()

# =====================================
# ЗАРЕЖДАНЕ И ГРУПИРАНЕ ПО ПОРЪЧКА
# =====================================

rows = active_rows


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
                    st.markdown(
                        f"""
                        <div style="
                            border:2px solid #FF4D4D;
                            background:rgba(60,0,0,0.35);
                            border-radius:10px;
                            padding:12px;
                            margin-bottom:6px;
                            color:#FFFFFF;
                            font-size:22px;
                            font-weight:900;
                        ">
                            {item_name} x{quantity}
                        </div>
                        """,
                        unsafe_allow_html=True
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
            # ИНФОРМАЦИЯ ЗА ОБЩАТА СМЕТКА
            # =====================================

            st.info(
                "🧾 Тази поръчка е добавена към общата "
                f"сметка на Маса № {table_number}. "
                "Приключването и плащането се извършват "
                "от изгледа „Сметки по маси“."
            )
