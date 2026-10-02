import streamlit as st

from database.db import get_connection
from streamlit_autorefresh import st_autorefresh


# =========================================================
# НАСТРОЙКИ
# =========================================================
st.set_page_config(
    page_title="Bar Operations",
    page_icon="🍸",
    layout="wide"
)


# =========================================================
# ВИЗУАЛЕН СТИЛ
# =========================================================
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at top,
                rgba(28, 23, 15, 0.96) 0%,
                rgba(7, 10, 15, 0.98) 45%,
                rgba(3, 5, 8, 1) 100%
            );
        color: #F5E6C8;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    footer {
        visibility: hidden;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 0.7rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, p, label, span {
        color: #F5E6C8;
    }

    div[data-testid="stMetric"] {
        background: rgba(16, 20, 28, 0.78);
        border: 1px solid rgba(212, 175, 55, 0.42);
        border-radius: 14px;
        padding: 16px;
    }

    div[data-testid="stButton"] button,
    div[data-testid="stFormSubmitButton"] button {
        min-height: 42px !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
    }

    div[data-testid="stButton"] button[kind="primary"],
    div[data-testid="stFormSubmitButton"] button[kind="primary"] {
        background:
            linear-gradient(
                135deg,
                #B98528 0%,
                #D4AF37 48%,
                #F5D77B 100%
            ) !important;
        border: 1px solid #F5D77B !important;
        color: #101010 !important;
    }

    @media only screen and (max-width: 768px) {
        .block-container {
            padding-top: 0.3rem;
            padding-left: 0.7rem;
            padding-right: 0.7rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ДОСТЪП
# =========================================================
BAR_PASSWORD = "bar2026"

if "bar_auth" not in st.session_state:
    st.session_state.bar_auth = False


if not st.session_state.bar_auth:

    st.title("🍸 Bar Operations")

    st.caption(
        "Панел за напитки от Room Service и бар зоните"
    )

    password = st.text_input(
        "Парола",
        type="password",
        key="bar_password"
    )

    if st.button(
        "Вход",
        key="bar_login",
        type="primary",
        use_container_width=True
    ):
        if password == BAR_PASSWORD:
            st.session_state.bar_auth = True
            st.rerun()

        else:
            st.error(
                "Невалидна парола."
            )

    st.stop()


# =========================================================
# AUTO REFRESH
# 60000 милисекунди = 1 минута
# =========================================================
st_autorefresh(
    interval=60000,
    limit=None,
    key="bar_auto_refresh"
)




# =========================================================
# ПОМОЩНИ ФУНКЦИИ
# =========================================================
def normalize_text(value):
    return str(
        value or ""
    ).strip().lower()


def is_bar_item(item_name):
    normalized_name = normalize_text(
        item_name
    )

    return any(
        keyword in normalized_name
        for keyword in BAR_KEYWORDS
    )


def format_datetime(value):
    if value is None:
        return ""

    try:
        return value.strftime(
            "%d.%m.%Y %H:%M"
        )

    except Exception:
        return str(value)


def close_connection(
    cur,
    conn
):
    try:
        if cur is not None:
            cur.close()

    finally:
        if conn is not None:
            conn.close()


def get_item_status_label(status):
    labels = {
        "NEW": "🔴 Нова",
        "PREPARING": "🟡 Подготвя се",
        "READY": "🟢 Готова",
        "DELIVERING": "🚚 Доставя се",
        "COMPLETED": "✅ Завършена",
        "CANCELLED": "❌ Отказана"
    }

    normalized_status = str(
        status or "NEW"
    ).strip().upper()

    return labels.get(
        normalized_status,
        normalized_status
    )


# =========================================================
# ЗАРЕЖДАНЕ НА ROOM SERVICE НАПИТКИ
# =========================================================
def get_room_service_bar_items():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                rso.id AS order_id,
                hr.room_number,
                rso.created_at,
                rso.order_status,
                rso.total_amount,
                rsoi.id AS order_item_id,
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
            WHERE UPPER(TRIM(rso.order_status))
                  <> 'COMPLETED'
              AND UPPER(TRIM(rsoi.item_status))
                  NOT IN (
                      'COMPLETED',
                      'CANCELLED'
                  )
            ORDER BY
                rso.created_at ASC,
                rso.id ASC,
                rsoi.id ASC
            """
        )

        all_rows = cur.fetchall()

        return all_rows

    finally:
        close_connection(
            cur,
            conn
        )


# =========================================================
# БРОЙ ROOM SERVICE НАПИТКИ ПО СТАТУС
# =========================================================
def get_room_service_bar_counts(
    rows
):
    counts = {
        "NEW": 0,
        "PREPARING": 0,
        "READY": 0,
        "OTHER": 0
    }

    for row in rows:
        item_status = str(
            row[10] or "NEW"
        ).strip().upper()

        if item_status in counts:
            counts[item_status] += 1

        else:
            counts["OTHER"] += 1

    return counts


# =========================================================
# ПРОМЯНА НА СТАТУСА НА ЕДИН BAR АРТИКУЛ
#
# Не променя общия статус на цялата Room Service поръчка.
# Така кухнята и барът работят независимо.
# =========================================================
def update_room_service_bar_item_status(
    order_item_id,
    new_status
):
    allowed_statuses = {
        "NEW",
        "PREPARING",
        "READY",
        "DELIVERING",
        "COMPLETED",
        "CANCELLED"
    }

    normalized_status = str(
        new_status or ""
    ).strip().upper()

    if normalized_status not in allowed_statuses:
        raise ValueError(
            "Невалиден статус на напитката."
        )

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE room_service_order_items
            SET item_status = %s
            WHERE id = %s
            """,
            (
                normalized_status,
                order_item_id
            )
        )

        if cur.rowcount == 0:
            raise ValueError(
                "Артикулът не е намерен."
            )

        conn.commit()

    except Exception:
        if conn is not None:
            conn.rollback()

        raise

    finally:
        close_connection(
            cur,
            conn
        )


# =========================================================
# ГРУПИРАНЕ НА НАПИТКИТЕ ПО ROOM SERVICE ПОРЪЧКА
# =========================================================
def group_room_service_bar_orders(
    rows
):
    orders = {}

    for row in rows:
        order_id = row[0]

        if order_id not in orders:
            orders[order_id] = {
                "room_number": row[1],
                "created_at": row[2],
                "order_status": row[3],
                "total_amount": float(
                    row[4] or 0
                ),
                "items": []
            }

        orders[order_id]["items"].append(
            {
                "order_item_id": row[5],
                "item_name": row[6],
                "quantity": int(
                    row[7] or 0
                ),
                "unit_price": float(
                    row[8] or 0
                ),
                "notes": row[9],
                "item_status": str(
                    row[10] or "NEW"
                ).strip().upper()
            }
        )

    return orders


# =========================================================
# ГОРНА ЧАСТ
# =========================================================
title_col, logout_col = st.columns(
    [5, 1],
    vertical_alignment="center"
)

with title_col:
    st.title(
        "🍸 Bar Operations"
    )

    st.caption(
        "Room Service напитки и обслужващи бар зони"
    )

with logout_col:
    if st.button(
        "🚪 Изход",
        key="bar_logout",
        use_container_width=True
    ):
        st.session_state.bar_auth = False
        st.rerun()


# =========================================================
# ЗАРЕЖДАНЕ НА ROOM SERVICE НАПИТКИТЕ
# =========================================================
try:
    room_service_bar_rows = (
        get_room_service_bar_items()
    )

except Exception as error:
    st.error(
        "Room Service напитките не могат "
        "да бъдат заредени."
        "\n\n"
        f"Причина: {error}"
    )

    room_service_bar_rows = []


bar_counts = get_room_service_bar_counts(
    room_service_bar_rows
)


# =========================================================
# KPI
# =========================================================
metric_col1, metric_col2, metric_col3 = st.columns(
    3
)

with metric_col1:
    st.metric(
        "🔴 Нови напитки",
        bar_counts["NEW"]
    )

with metric_col2:
    st.metric(
        "🟡 Подготвят се",
        bar_counts["PREPARING"]
    )

with metric_col3:
    st.metric(
        "🟢 Готови",
        bar_counts["READY"]
    )


st.divider()


# =========================================================
# ИЗГЛЕДИ
# =========================================================
ROOM_SERVICE_VIEW = (
    "🏨 Room Service "
    f"({len(room_service_bar_rows)})"
)

LOBBY_BAR_VIEW = "🍸 Lobby Bar"

bar_views = [
    ROOM_SERVICE_VIEW,
    LOBBY_BAR_VIEW
]


if "bar_view" not in st.session_state:
    st.session_state.bar_view = ROOM_SERVICE_VIEW


if st.session_state.bar_view not in bar_views:
    st.session_state.bar_view = ROOM_SERVICE_VIEW


bar_view = st.radio(
    "Bar изглед",
    bar_views,
    horizontal=True,
    label_visibility="collapsed",
    key="bar_view"
)


st.divider()


# =========================================================
# ROOM SERVICE BAR ИЗГЛЕД
# =========================================================
if bar_view == ROOM_SERVICE_VIEW:

    st.subheader(
        "🏨 Room Service напитки"
    )

    st.caption(
        "Показват се само разпознатите напитки "
        "от активните Room Service поръчки."
    )

    room_service_bar_orders = (
        group_room_service_bar_orders(
            room_service_bar_rows
        )
    )

    if not room_service_bar_orders:

        st.success(
            "Няма активни напитки за Room Service."
        )

    else:
        item_status_options = [
            "NEW",
            "PREPARING",
            "READY",
            "DELIVERING",
            "COMPLETED",
            "CANCELLED"
        ]

        for order_id, order_data in (
            room_service_bar_orders.items()
        ):
            with st.container(
                border=True
            ):
                title_column, time_column = st.columns(
                    [5, 2]
                )

                with title_column:
                    st.subheader(
                        "🍸 Room Service "
                        f"поръчка #{order_id}"
                    )

                    st.markdown(
                        "### 🏨 "
                        f"Стая №"
                        f"{order_data['room_number']}"
                    )

                with time_column:
                    if order_data["created_at"]:
                        st.caption(
                            "Получена: "
                            f"{format_datetime(
                                order_data['created_at']
                            )}"
                        )

                    st.write(
                        "**Общ статус на поръчката:** "
                        f"{order_data['order_status']}"
                    )

                st.markdown(
                    "#### Напитки"
                )

                for item in order_data["items"]:
                    with st.container(
                        border=True
                    ):
                        item_col, qty_col, price_col = (
                            st.columns([5, 1, 2])
                        )

                        with item_col:
                            st.write(
                                f"**{item['item_name']}**"
                            )

                            st.write(
                                "Статус: "
                                f"{get_item_status_label(
                                    item['item_status']
                                )}"
                            )

                            if item["notes"]:
                                st.caption(
                                    "📝 "
                                    f"{item['notes']}"
                                )

                        with qty_col:
                            st.write(
                                f"x{item['quantity']}"
                            )

                        with price_col:
                            item_total = (
                                item["unit_price"]
                                * item["quantity"]
                            )

                            st.write(
                                f"€ {item_total:.2f}"
                            )

                        with st.form(
                            key=(
                                "bar_item_form_"
                                f"{item['order_item_id']}"
                            ),
                            clear_on_submit=False
                        ):
                            form_col1, form_col2 = (
                                st.columns(
                                    [2, 3],
                                    vertical_alignment="bottom"
                                )
                            )

                            with form_col1:
                                selected_status = (
                                    st.selectbox(
                                        "Статус на напитката",
                                        item_status_options,
                                        index=(
                                            item_status_options.index(
                                                item[
                                                    "item_status"
                                                ]
                                            )
                                            if item[
                                                "item_status"
                                            ]
                                            in item_status_options
                                            else 0
                                        ),
                                        format_func=(
                                            get_item_status_label
                                        ),
                                        key=(
                                            "bar_item_status_"
                                            f"{item[
                                                'order_item_id'
                                            ]}"
                                        )
                                    )
                                )

                            with form_col2:
                                save_item_status = (
                                    st.form_submit_button(
                                        "💾 Запази статуса",
                                        type="primary",
                                        use_container_width=True
                                    )
                                )

                            if save_item_status:
                                try:
                                    update_room_service_bar_item_status(
                                        order_item_id=(
                                            item[
                                                "order_item_id"
                                            ]
                                        ),
                                        new_status=(
                                            selected_status
                                        )
                                    )

                                    st.rerun()

                                except Exception as error:
                                    st.error(
                                        "Статусът не беше "
                                        "обновен."
                                        "\n\n"
                                        f"Причина: {error}"
                                    )


# =========================================================
# LOBBY BAR ИЗГЛЕД
# =========================================================
elif bar_view == LOBBY_BAR_VIEW:

    st.subheader(
        "🍸 Lobby Bar"
    )

    st.info(
        "Lobby Bar изгледът е подготвен. "
        "Следващата връзка ще бъде към "
        "реалните Lastoria поръчки по номер на маса."
    )

    st.markdown(
        """
        #### Бъдеща визуализация

        ```text
        Lobby Bar поръчка #15

        🍽️ Маса №3

        Коктейл x2
        Минерална вода x1

        Статус:
        NEW → PREPARING → READY → SERVED → COMPLETED
        ```
        """
    )


# =========================================================
# БРАНДИРАНЕ
# =========================================================
st.divider()

st.caption(
    "Powered by HMITSEVAPPS"
)
