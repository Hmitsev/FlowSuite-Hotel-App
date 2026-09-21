
import streamlit as st

from database.db import get_connection


# =====================================
# НАСТРОЙКИ
# =====================================

st.set_page_config(
    page_title="Reception",
    page_icon="🛎️",
    layout="wide"
)


# =====================================
# БАНЕР НА РЕЦЕПЦИЯТА
# =====================================

st.image(
    "assets/Screenshot 2026-09-09 025744.png",
    use_container_width=True
)
# =====================================
# ДОСТЪП ДО РЕЦЕПЦИЯ
# =====================================

RECEPTION_PASSWORD = "reception2026"

if "reception_auth" not in st.session_state:
    st.session_state.reception_auth = False


if not st.session_state.reception_auth:
    st.title("🛎️ Reception")

    password = st.text_input(
        "Парола",
        type="password",
        key="reception_password"
    )

    if st.button(
        "Вход",
        key="reception_login",
        type="primary"
    ):
        if password == RECEPTION_PASSWORD:
            st.session_state.reception_auth = True
            st.rerun()
        else:
            st.error("Невалидна парола.")

    st.stop()


# =====================================
# ИЗХОД
# =====================================

logout_col1, logout_col2 = st.columns([5, 1])

with logout_col2:
    if st.button(
        "🚪 Изход",
        key="reception_logout",
        use_container_width=True
    ):
        st.session_state.reception_auth = False
        st.rerun()


# =====================================
# ЗАГЛАВИЕ И КАМБАНКА ЗА ИЗВЕСТИЯ
# =====================================

st.markdown(
    """
    <style>

    @keyframes bellShake {
        0% { transform: rotate(0deg); }
        15% { transform: rotate(18deg); }
        30% { transform: rotate(-16deg); }
        45% { transform: rotate(12deg); }
        60% { transform: rotate(-10deg); }
        75% { transform: rotate(6deg); }
        100% { transform: rotate(0deg); }
    }

    @keyframes notificationPulse {
        0% {
            box-shadow: 0 0 0 0 rgba(255,70,70,.75);
        }

        70% {
            box-shadow: 0 0 0 10px rgba(255,70,70,0);
        }

        100% {
            box-shadow: 0 0 0 0 rgba(255,70,70,0);
        }
    }

    .notification-bell-wrapper {
        display:flex;
        justify-content:flex-end;
        align-items:center;
        width:100%;
        min-height:80px;
    }

    .notification-bell {
        position:relative;
        font-size:56px;
        animation: bellShake 0.85s ease-in-out infinite;
        transform-origin:75% 10%;
        line-height:1;
    }

    .notification-count {
        position:absolute;
        top:-10px;
        right:-14px;

        min-width:26px;
        height:26px;

        display:flex;
        align-items:center;
        justify-content:center;

        background:#ff3b3b;
        color:white;

        border-radius:999px;
        border:2px solid white;

        font-size:13px;
        font-weight:900;

        animation: notificationPulse 1.4s infinite;
    }

    @media only screen and (max-width:768px){

        .notification-bell{
            font-size:46px;
        }

        .notification-count{
            min-width:22px;
            height:22px;
            font-size:11px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)

title_left_col, title_center_col, bell_col = st.columns(
    [1.3, 5, 1.3],
    vertical_alignment="center"
)

with title_center_col:
    st.markdown(
        """
        <div style="
            text-align:center;
            color:#D4AF37;
            font-size:34px;
            font-weight:800;
            letter-spacing:1px;
            margin-top:15px;
            margin-bottom:20px;
        ">
            ROOM SERVICE
        </div>
        """,
        unsafe_allow_html=True
    )

with bell_col:
    notification_bell_placeholder = st.empty()
# =====================================
# ЗАРЕЖДАНЕ НА ROOM SERVICE ПОРЪЧКИТЕ
# =====================================

def get_room_service_orders():
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
            WHERE rso.order_status <> 'COMPLETED'
            ORDER BY
                rso.created_at ASC,
                rso.id ASC,
                rsoi.id ASC
            """
        )

        return cur.fetchall()

    finally:
        cur.close()
        conn.close()


# =====================================
# ИСТОРИЯ НА ПРИКЛЮЧЕНИТЕ ПОРЪЧКИ
# =====================================

def get_completed_room_service_orders():
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
            WHERE rso.order_status = 'COMPLETED'
            ORDER BY
                rso.completed_at DESC,
                rso.id DESC,
                rsoi.id ASC
            LIMIT 100
            """
        )

        return cur.fetchall()

    finally:
        cur.close()
        conn.close()


# =====================================
# ПРОМЯНА НА СТАТУСА НА ПОРЪЧКАТА
# =====================================

def update_room_service_order_status(
    order_id,
    new_status
):
    conn = get_connection()
    cur = conn.cursor()

    try:
        if new_status == "COMPLETED":
            cur.execute(
                """
                UPDATE room_service_orders
                SET
                    order_status = %s,
                    updated_at = CURRENT_TIMESTAMP,
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    new_status,
                    order_id
                )
            )

            cur.execute(
                """
                UPDATE room_service_order_items
                SET item_status = 'COMPLETED'
                WHERE order_id = %s
                """,
                (order_id,)
            )

        else:
            cur.execute(
                """
                UPDATE room_service_orders
                SET
                    order_status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    new_status,
                    order_id
                )
            )

            cur.execute(
                """
                UPDATE room_service_order_items
                SET item_status = %s
                WHERE order_id = %s
                """,
                (
                    new_status,
                    order_id
                )
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()
# =====================================
# ЗАРЕЖДАНЕ НА ACTIVITIES ЗАЯВКИТЕ
# =====================================

def get_activity_requests():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT
                ar.id,
                hr.room_number,
                ar.activity_name,
                ar.guest_message,
                ar.request_status,
                ar.created_at
            FROM activity_requests ar
            JOIN hotel_rooms hr
                ON hr.id = ar.room_id
            WHERE UPPER(TRIM(ar.request_status)) IN (
                'NEW',
                'CONTACTED',
                'CONFIRMED'
            )
            ORDER BY
                ar.created_at ASC,
                ar.id ASC
            """
        )

        return cur.fetchall()

    finally:
        cur.close()
        conn.close()
# =====================================
# БРОЙ НОВИ ACTIVITIES ЗАЯВКИ
# =====================================

def get_new_activity_notifications():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT
                COUNT(*) AS new_request_count,
                ARRAY_AGG(
                    DISTINCT hr.room_number
                    ORDER BY hr.room_number
                ) AS room_numbers
            FROM activity_requests ar
            JOIN hotel_rooms hr
                ON hr.id = ar.room_id
            WHERE ar.request_status = 'NEW'
            """
        )

        result = cur.fetchone()

        new_request_count = int(
            result[0] or 0
        )

        room_numbers = (
            list(result[1])
            if result[1]
            else []
        )

        return (
            new_request_count,
            room_numbers
        )

    finally:
        cur.close()
        conn.close()


# =====================================
# ПРОМЯНА НА СТАТУС НА ACTIVITY ЗАЯВКА
# =====================================

def update_activity_request_status(
    request_id,
    new_status
):
    conn = get_connection()
    cur = conn.cursor()

    try:
        if new_status in (
            "COMPLETED",
            "CANCELLED"
        ):
            cur.execute(
                """
                UPDATE activity_requests
                SET
                    request_status = %s,
                    updated_at = CURRENT_TIMESTAMP,
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    new_status,
                    request_id
                )
            )

        else:
            cur.execute(
                """
                UPDATE activity_requests
                SET
                    request_status = %s,
                    updated_at = CURRENT_TIMESTAMP,
                    completed_at = NULL
                WHERE id = %s
                """,
                (
                    new_status,
                    request_id
                )
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()


# =====================================
# БРОЙ НОВИ ROOM SERVICE ПОРЪЧКИ
# =====================================

def get_new_room_service_notifications():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT COUNT(*)
            FROM room_service_orders
            WHERE order_status = 'NEW'
            """
        )

        return cur.fetchone()[0]

    finally:
        cur.close()
        conn.close()
# =====================================
# ЗАРЕЖДАНЕ НА ИЗВЕСТИЯТА
# =====================================

try:
    (
        new_activity_count,
        new_activity_rooms
    ) = get_new_activity_notifications()

except Exception:
    new_activity_count = 0
    new_activity_rooms = []


try:
    new_room_service_count = (
        get_new_room_service_notifications()
    )

except Exception:
    new_room_service_count = 0


# =====================================
# ОБЩ БРОЙ НОВИ ИЗВЕСТИЯ
# =====================================

total_new_notifications = (
    int(new_room_service_count or 0)
    + int(new_activity_count or 0)
)


# =====================================
# ПОКАЗВАНЕ НА ОБЩАТА КАМБАНКА
# =====================================

if total_new_notifications > 0:
    notification_bell_placeholder.markdown(
        f'<div class="notification-bell-wrapper">'
        f'<div class="notification-bell">'
        f'🔔'
        f'<span class="notification-count">'
        f'{total_new_notifications}'
        f'</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

else:
    notification_bell_placeholder.empty()


# =====================================
# ACTIVITIES НАДПИС
# =====================================

if new_activity_count > 0:
    ACTIVITIES_VIEW = (
        f"🔴 {new_activity_count} | "
        "🎿 Activities заявки"
    )

else:
    ACTIVITIES_VIEW = (
        "🎿 Activities заявки"
    )


# =====================================
# ПРИКЛЮЧЕНИ ПОРЪЧКИ
# =====================================

COMPLETED_VIEW = (
    "📜 Приключени поръчки"
)


# =====================================
# ИЗБОР НА ИЗГЛЕД
# =====================================

view_mode = st.radio(
    "Изглед",
    [
        ACTIVE_VIEW,
        ACTIVITIES_VIEW,
        COMPLETED_VIEW
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="reception_view_mode"
)



# =====================================
# ACTIVITIES ИЗГЛЕД
# =====================================

if view_mode == ACTIVITIES_VIEW:
    try:
        activity_rows = get_activity_requests()

    except Exception as error:
        st.error(
            "Activities заявките не могат "
            "да бъдат заредени.\n\n"
            f"Причина: {error}"
        )
        st.stop()

    # Останалата Activities логика продължава тук

    st.markdown("##  Activities заявки")

    activity_col1, activity_col2 = st.columns(2)

    with activity_col1:
        st.metric(
            "Активни заявки",
            len(activity_rows)
        )

    with activity_col2:
        new_activity_count = sum(
            1
            for row in activity_rows
            if row[4] == "NEW"
        )

        st.metric(
            "Нови заявки",
            new_activity_count
        )

    st.divider()

    if not activity_rows:
        st.success(
            "Няма активни Activities заявки."
        )

    else:
        for activity_row in activity_rows:
            request_id = activity_row[0]
            room_number = activity_row[1]
            activity_name = activity_row[2]
            guest_message = activity_row[3]
            request_status = activity_row[4]
            created_at = activity_row[5]

            with st.container(border=True):
                title_col, status_col = st.columns(
                    [5, 2]
                )

                with title_col:
                    st.subheader(
                        f"Activities заявка #{request_id}"
                    )

                    st.markdown(
                        f"### 🛎️ Стая №{room_number}"
                    )

                    st.write(
                        f"**Дейност:** {activity_name}"
                    )

                with status_col:
                    status_labels = {
                        "NEW": "🔴 NEW",
                        "CONTACTED": "🟡 CONTACTED",
                        "CONFIRMED": "🟢 CONFIRMED",
                        "COMPLETED": "✅ COMPLETED",
                        "CANCELLED": "❌ CANCELLED"
                    }

                    st.write(
                        "Статус: "
                        f"{status_labels.get(
                            request_status,
                            request_status
                        )}"
                    )

                    if created_at:
                        st.caption(
                            "Получена: "
                            f"{created_at.strftime(
                                '%d.%m.%Y %H:%M'
                            )}"
                        )

                st.markdown("#### Съобщение от госта")

                st.info(
                    guest_message
                )

                status_select_col, save_col = st.columns(
                    [2, 3]
                )

                activity_statuses = [
                    "NEW",
                    "CONTACTED",
                    "CONFIRMED",
                    "COMPLETED",
                    "CANCELLED"
                ]

                with status_select_col:
                    selected_activity_status = st.selectbox(
                        "Статус",
                        activity_statuses,
                        index=(
                            activity_statuses.index(
                                request_status
                            )
                            if request_status
                            in activity_statuses
                            else 0
                        ),
                        key=(
                            f"activity_status_"
                            f"{request_id}"
                        )
                    )

                with save_col:
                    if st.button(
                        "✅ Запази статуса",
                        key=(
                            f"save_activity_status_"
                            f"{request_id}"
                        ),
                        type="primary",
                        use_container_width=True
                    ):
                        try:
                            update_activity_request_status(
                                request_id=request_id,
                                new_status=(
                                    selected_activity_status
                                )
                            )

                            st.success(
                                "Статусът на заявката "
                                "е обновен."
                            )

                            st.rerun()

                        except Exception as error:
                            st.error(
                                "Статусът не беше обновен."
                                "\n\n"
                                f"Причина: {error}"
                            )

    st.divider()

    if st.button(
        "🔄 Обнови Activities заявките",
        key="refresh_activity_requests",
        use_container_width=True
    ):
        st.rerun()

    st.caption(
        "Powered by HMITSEVAPPS"
    )

    st.stop()

# =====================================
# ЗАРЕЖДАНЕ НА ROOM SERVICE ДАННИТЕ
# =====================================

try:
    if view_mode == ACTIVE_VIEW:
        rows = get_room_service_orders()
    else:
        rows = get_completed_room_service_orders()

except Exception as error:
    st.error(
        "Поръчките не могат да бъдат заредени.\n\n"
        f"Причина: {error}"
    )

    st.stop()

# =====================================
# ГРУПИРАНЕ ПО ПОРЪЧКА
# =====================================

orders = {}

for row in rows:
    order_id = row[0]

    if order_id not in orders:
        orders[order_id] = {
            "room_number": row[1],
            "created_at": row[2],
            "order_status": row[3],
            "total_amount": row[4],
            "items": []
        }

    orders[order_id]["items"].append(
        {
            "order_item_id": row[5],
            "item_id": row[6],
            "item_name": row[7],
            "quantity": row[8],
            "unit_price": row[9],
            "notes": row[10],
            "item_status": row[11]
        }
    )


# =====================================
# ОБОБЩЕНИЕ
# =====================================

active_order_count = len(orders)

metric_col1, metric_col2 = st.columns(2)

with metric_col1:
    st.metric(
        "Room Service поръчки",
        active_order_count
    )

with metric_col2:
    total_value = sum(
        float(order["total_amount"] or 0)
        for order in orders.values()
    )

    st.metric(
        "Обща стойност",
        f"€ {total_value:.2f}"
    )

st.divider()


# =====================================
# ПОКАЗВАНЕ НА ПОРЪЧКИТЕ
# =====================================

if not orders:
    st.success(
        "Няма поръчки в този изглед."
    )

else:
    for order_id, order_data in orders.items():
        room_number = order_data["room_number"]
        created_at = order_data["created_at"]
        order_status = order_data["order_status"]
        total_amount = float(
            order_data["total_amount"] or 0
        )

        with st.container(border=True):
            title_col, time_col, total_col = st.columns(
                [4, 2, 2]
            )

            with title_col:
                st.subheader(
                    f" Room Service Order #{order_id}"
                )

                st.markdown(
                    f"### 🛎️ Стая №{room_number}"
                )

            with time_col:
                if created_at:
                    st.caption(
                        "Получена: "
                        f"{created_at.strftime('%d.%m.%Y %H:%M')}"
                    )

                status_colors = {
                    "NEW": "🔴 NEW",
                    "PREPARING": "🟡 PREPARING",
                    "READY": "🟢 READY",
                    "DELIVERING": "🚚 DELIVERING",
                    "COMPLETED": "✅ COMPLETED"
                }
                
                st.write(
                    f"Статус: {status_colors.get(order_status, order_status)}"
                )

            with total_col:
                st.metric(
                    "Общо",
                    f"€ {total_amount:.2f}"
                )

            st.markdown("#### Артикули")

            for item in order_data["items"]:
                item_col, qty_col, price_col = st.columns(
                    [6, 1, 2]
                )

                with item_col:
                    st.write(
                        f"**{item['item_name']}**"
                    )

                    if item["notes"]:
                        st.caption(
                            f"📝 {item['notes']}"
                        )

                with qty_col:
                    st.write(
                        f"x{item['quantity']}"
                    )

                with price_col:
                    item_total = (
                        float(item["unit_price"])
                        * int(item["quantity"])
                    )

                    st.write(
                        f"€ {item_total:.2f}"
                    )

            if view_mode == ACTIVE_VIEW:
                status_col, action_col = st.columns(
                    [2, 3]
                )

                with status_col:
                    selected_status = st.selectbox(
                        "Статус",
                        [
                            "NEW",
                            "PREPARING",
                            "READY",
                            "DELIVERING",
                            "COMPLETED"
                        ],
                        index=(
                            [
                                "NEW",
                                "PREPARING",
                                "READY",
                                "DELIVERING",
                                "COMPLETED"
                            ].index(order_status)
                            if order_status in [
                                "NEW",
                                "PREPARING",
                                "READY",
                                "DELIVERING",
                                "COMPLETED"
                            ]
                            else 0
                        ),
                        key=f"status_{order_id}"
                    )

                with action_col:
                    if st.button(
                        "✅ Запази статуса",
                        key=f"save_status_{order_id}",
                        type="primary",
                        use_container_width=True
                    ):
                        try:
                            update_room_service_order_status(
                                order_id=order_id,
                                new_status=selected_status
                            )

                            st.success(
                                "Статусът е обновен."
                            )

                            st.rerun()

                        except Exception as error:
                            st.error(
                                "Статусът не беше обновен.\n\n"
                                f"Причина: {error}"
                            )


# =====================================
# ОБНОВЯВАНЕ
# =====================================

st.divider()

if st.button(
    "🔄 Обнови поръчките",
    key="refresh_reception_orders",
    use_container_width=True
):
    st.rerun()


# =====================================
# БРАНДИРАНЕ
# =====================================

st.caption(
    "Powered by HMITSEVAPPS"
)
