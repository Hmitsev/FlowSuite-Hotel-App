import streamlit as st

from database.db import get_connection
from streamlit_autorefresh import st_autorefresh


# =========================================================
# НАСТРОЙКИ
# =========================================================
st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="👑",
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
        max-width: 1380px;
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

    div[data-testid="stButton"] button {
        min-height: 42px !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
    }

    div[data-testid="stButton"] button[kind="primary"] {
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
ADMIN_PASSWORD = "admin2026"

if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False


if not st.session_state.admin_auth:

    st.title("👑 Admin Dashboard")

    st.caption(
        "Управленски профил за наблюдение на хотелските операции"
    )

    password = st.text_input(
        "Парола",
        type="password",
        key="admin_password"
    )

    if st.button(
        "Вход",
        key="admin_login",
        type="primary",
        use_container_width=True
    ):
        if password == ADMIN_PASSWORD:
            st.session_state.admin_auth = True
            st.rerun()

        else:
            st.error(
                "Невалидна парола."
            )

    st.stop()


# =========================================================
# AUTO REFRESH
# 120000 милисекунди = 2 минути
# =========================================================
st_autorefresh(
    interval=120000,
    limit=None,
    key="admin_auto_refresh"
)


# =========================================================
# ПОМОЩНИ ФУНКЦИИ
# =========================================================
def format_datetime(value):
    if value is None:
        return ""

    try:
        return value.strftime(
            "%d.%m.%Y %H:%M"
        )

    except Exception:
        return str(value)


def normalize_status(value):
    return str(
        value or ""
    ).strip().upper()


def get_status_label(status):
    labels = {
        "NEW": "🔴 Нова",
        "CONTACTED": "🟡 Свързване",
        "CONFIRMED": "🟢 Потвърдена",
        "PREPARING": "🟡 Подготвя се",
        "READY": "🟢 Готова",
        "DELIVERING": "🚚 Доставя се",
        "ACCEPTED": "🟡 Приета",
        "IN_PROGRESS": "🔵 В процес",
        "COMPLETED": "✅ Завършена",
        "CANCELLED": "❌ Отказана"
    }

    return labels.get(
        normalize_status(status),
        str(status or "")
    )


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


# =========================================================
# KPI ДАННИ
# =========================================================
def get_admin_kpis():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                (
                    SELECT COUNT(*)
                    FROM room_service_orders
                    WHERE UPPER(TRIM(order_status))
                          <> 'COMPLETED'
                ) AS active_room_service,

                (
                    SELECT COUNT(*)
                    FROM spa_requests
                    WHERE UPPER(TRIM(request_status)) IN (
                        'NEW',
                        'CONTACTED',
                        'CONFIRMED'
                    )
                ) AS active_spa,

                (
                    SELECT COUNT(*)
                    FROM activity_requests
                    WHERE UPPER(TRIM(request_status)) IN (
                        'NEW',
                        'CONTACTED',
                        'CONFIRMED'
                    )
                ) AS active_activities,

                (
                    SELECT COUNT(*)
                    FROM service_requests
                    WHERE UPPER(TRIM(request_status)) IN (
                        'NEW',
                        'ACCEPTED',
                        'IN_PROGRESS'
                    )
                ) AS active_service,

                (
                    SELECT COUNT(*)
                    FROM service_requests
                    WHERE UPPER(TRIM(request_status)) IN (
                        'NEW',
                        'ACCEPTED',
                        'IN_PROGRESS'
                    )
                    AND (
                        assigned_to IS NULL
                        OR TRIM(assigned_to) = ''
                    )
                ) AS unassigned_service,

                (
                    SELECT
                        (
                            SELECT COUNT(*)
                            FROM room_service_orders
                            WHERE completed_at IS NOT NULL
                              AND DATE(completed_at)
                                  = CURRENT_DATE
                        )
                        +
                        (
                            SELECT COUNT(*)
                            FROM spa_requests
                            WHERE completed_at IS NOT NULL
                              AND DATE(completed_at)
                                  = CURRENT_DATE
                        )
                        +
                        (
                            SELECT COUNT(*)
                            FROM activity_requests
                            WHERE completed_at IS NOT NULL
                              AND DATE(completed_at)
                                  = CURRENT_DATE
                        )
                        +
                        (
                            SELECT COUNT(*)
                            FROM service_requests
                            WHERE completed_at IS NOT NULL
                              AND DATE(completed_at)
                                  = CURRENT_DATE
                        )
                ) AS completed_today
            """
        )

        row = cur.fetchone()

        return {
            "room_service": int(row[0] or 0),
            "spa": int(row[1] or 0),
            "activities": int(row[2] or 0),
            "service": int(row[3] or 0),
            "unassigned": int(row[4] or 0),
            "completed_today": int(row[5] or 0)
        }

    finally:
        close_connection(
            cur,
            conn
        )


# =========================================================
# ROOM SERVICE АКТИВНИ ОПЕРАЦИИ
# =========================================================
def get_active_room_service_operations():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                rso.id,
                hr.room_number,
                rso.order_status,
                rso.total_amount,
                rso.created_at
            FROM room_service_orders rso
            JOIN hotel_rooms hr
                ON hr.id = rso.room_id
            WHERE UPPER(TRIM(rso.order_status))
                  <> 'COMPLETED'
            ORDER BY
                rso.created_at DESC,
                rso.id DESC
            """
        )

        rows = cur.fetchall()

        return [
            {
                "record_id": row[0],
                "room_number": row[1],
                "module": "ROOM_SERVICE",
                "title": "Room Service поръчка",
                "status": row[2],
                "amount": float(row[3] or 0),
                "created_at": row[4],
                "assigned_to": None,
                "priority": None
            }
            for row in rows
        ]

    finally:
        close_connection(
            cur,
            conn
        )


# =========================================================
# SPA АКТИВНИ ОПЕРАЦИИ
# =========================================================
def get_active_spa_operations():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                sr.id,
                hr.room_number,
                sr.service_name,
                sr.request_status,
                sr.created_at,
                sr.reservation_date,
                sr.reservation_time
            FROM spa_requests sr
            JOIN hotel_rooms hr
                ON hr.id = sr.room_id
            WHERE UPPER(TRIM(sr.request_status)) IN (
                'NEW',
                'CONTACTED',
                'CONFIRMED'
            )
            ORDER BY
                sr.created_at DESC,
                sr.id DESC
            """
        )

        rows = cur.fetchall()

        results = []

        for row in rows:
            reservation_text = ""

            if row[5] is not None:
                reservation_text = row[5].strftime(
                    "%d.%m.%Y"
                )

            if row[6] is not None:
                time_text = row[6].strftime(
                    "%H:%M"
                )

                if reservation_text:
                    reservation_text += (
                        f" от {time_text}"
                    )

                else:
                    reservation_text = time_text

            results.append(
                {
                    "record_id": row[0],
                    "room_number": row[1],
                    "module": "SPA",
                    "title": row[2],
                    "status": row[3],
                    "amount": None,
                    "created_at": row[4],
                    "assigned_to": None,
                    "priority": None,
                    "reservation": reservation_text
                }
            )

        return results

    finally:
        close_connection(
            cur,
            conn
        )


# =========================================================
# ACTIVITIES АКТИВНИ ОПЕРАЦИИ
# =========================================================
def get_active_activity_operations():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                ar.id,
                hr.room_number,
                ar.activity_name,
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
                ar.created_at DESC,
                ar.id DESC
            """
        )

        rows = cur.fetchall()

        return [
            {
                "record_id": row[0],
                "room_number": row[1],
                "module": "ACTIVITIES",
                "title": row[2],
                "status": row[3],
                "amount": None,
                "created_at": row[4],
                "assigned_to": None,
                "priority": None
            }
            for row in rows
        ]

    finally:
        close_connection(
            cur,
            conn
        )


# =========================================================
# SERVICE STAFF АКТИВНИ ОПЕРАЦИИ
# =========================================================
def get_active_service_operations():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                sr.id,
                hr.room_number,
                sr.department,
                sr.request_type,
                sr.request_status,
                sr.priority,
                sr.assigned_to,
                sr.created_at
            FROM service_requests sr
            JOIN hotel_rooms hr
                ON hr.id = sr.room_id
            WHERE UPPER(TRIM(sr.request_status)) IN (
                'NEW',
                'ACCEPTED',
                'IN_PROGRESS'
            )
            ORDER BY
                CASE UPPER(TRIM(sr.priority))
                    WHEN 'URGENT' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'NORMAL' THEN 3
                    WHEN 'LOW' THEN 4
                    ELSE 5
                END,
                sr.created_at DESC,
                sr.id DESC
            """
        )

        rows = cur.fetchall()

        return [
            {
                "record_id": row[0],
                "room_number": row[1],
                "module": "SERVICE",
                "department": row[2],
                "title": row[3],
                "status": row[4],
                "priority": row[5],
                "assigned_to": row[6],
                "created_at": row[7],
                "amount": None
            }
            for row in rows
        ]

    finally:
        close_connection(
            cur,
            conn
        )


# =========================================================
# ВСИЧКИ АКТИВНИ ОПЕРАЦИИ
# =========================================================
def get_all_active_operations():

    operations = []

    operations.extend(
        get_active_room_service_operations()
    )

    operations.extend(
        get_active_spa_operations()
    )

    operations.extend(
        get_active_activity_operations()
    )

    operations.extend(
        get_active_service_operations()
    )

    return sorted(
        operations,
        key=lambda item: (
            item["created_at"].timestamp()
            if item["created_at"]
            else 0
        ),
        reverse=True
    )


# =========================================================
# СТАТИСТИКА ЗА ДНЕС
# =========================================================
def get_today_statistics():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                (
                    SELECT COUNT(*)
                    FROM room_service_orders
                    WHERE DATE(created_at)
                          = CURRENT_DATE
                ) AS room_service_today,

                (
                    SELECT COUNT(*)
                    FROM spa_requests
                    WHERE DATE(created_at)
                          = CURRENT_DATE
                ) AS spa_today,

                (
                    SELECT COUNT(*)
                    FROM activity_requests
                    WHERE DATE(created_at)
                          = CURRENT_DATE
                ) AS activities_today,

                (
                    SELECT COUNT(*)
                    FROM service_requests
                    WHERE DATE(created_at)
                          = CURRENT_DATE
                ) AS service_today,

                (
                    SELECT COALESCE(
                        SUM(total_amount),
                        0
                    )
                    FROM room_service_orders
                    WHERE DATE(created_at)
                          = CURRENT_DATE
                ) AS room_service_revenue_today
            """
        )

        row = cur.fetchone()

        return {
            "room_service": int(row[0] or 0),
            "spa": int(row[1] or 0),
            "activities": int(row[2] or 0),
            "service": int(row[3] or 0),
            "room_service_revenue": float(
                row[4] or 0
            )
        }

    finally:
        close_connection(
            cur,
            conn
        )


# =========================================================
# НАТОВАРВАНЕ ПО СЛУЖИТЕЛИ
# =========================================================
def get_staff_workload():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                assigned_to,
                COUNT(*) AS active_count,
                COUNT(*) FILTER (
                    WHERE UPPER(
                        TRIM(request_status)
                    ) = 'IN_PROGRESS'
                ) AS in_progress_count
            FROM service_requests
            WHERE UPPER(TRIM(request_status)) IN (
                'NEW',
                'ACCEPTED',
                'IN_PROGRESS'
            )
              AND assigned_to IS NOT NULL
              AND TRIM(assigned_to) <> ''
            GROUP BY assigned_to
            ORDER BY
                active_count DESC,
                assigned_to ASC
            """
        )

        return cur.fetchall()

    finally:
        close_connection(
            cur,
            conn
        )


# =========================================================
# НАТОВАРВАНЕ ПО СТАИ ЗА ПОСЛЕДНИТЕ 30 ДНИ
# =========================================================
def get_room_workload():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                room_number,
                SUM(request_count) AS total_requests
            FROM (
                SELECT
                    hr.room_number,
                    COUNT(*) AS request_count
                FROM room_service_orders rso
                JOIN hotel_rooms hr
                    ON hr.id = rso.room_id
                WHERE rso.created_at
                      >= CURRENT_TIMESTAMP
                         - INTERVAL '30 days'
                GROUP BY hr.room_number

                UNION ALL

                SELECT
                    hr.room_number,
                    COUNT(*) AS request_count
                FROM spa_requests sr
                JOIN hotel_rooms hr
                    ON hr.id = sr.room_id
                WHERE sr.created_at
                      >= CURRENT_TIMESTAMP
                         - INTERVAL '30 days'
                GROUP BY hr.room_number

                UNION ALL

                SELECT
                    hr.room_number,
                    COUNT(*) AS request_count
                FROM activity_requests ar
                JOIN hotel_rooms hr
                    ON hr.id = ar.room_id
                WHERE ar.created_at
                      >= CURRENT_TIMESTAMP
                         - INTERVAL '30 days'
                GROUP BY hr.room_number

                UNION ALL

                SELECT
                    hr.room_number,
                    COUNT(*) AS request_count
                FROM service_requests sr
                JOIN hotel_rooms hr
                    ON hr.id = sr.room_id
                WHERE sr.created_at
                      >= CURRENT_TIMESTAMP
                         - INTERVAL '30 days'
                GROUP BY hr.room_number
            ) AS combined_room_requests
            GROUP BY room_number
            ORDER BY
                total_requests DESC,
                room_number ASC
            LIMIT 10
            """
        )

        return cur.fetchall()

    finally:
        close_connection(
            cur,
            conn
        )


# =========================================================
# НАЙ-ЧЕСТИ СЕРВИЗНИ ЗАЯВКИ
# =========================================================
def get_top_service_request_types():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                request_type,
                COUNT(*) AS request_count
            FROM service_requests
            WHERE created_at
                  >= CURRENT_TIMESTAMP
                     - INTERVAL '30 days'
            GROUP BY request_type
            ORDER BY
                request_count DESC,
                request_type ASC
            LIMIT 10
            """
        )

        return cur.fetchall()

    finally:
        close_connection(
            cur,
            conn
        )


# =========================================================
# ГОРНА ЧАСТ
# =========================================================
title_col, logout_col = st.columns(
    [5, 1],
    vertical_alignment="center"
)

with title_col:
    st.title(
        "👑 Admin Dashboard"
    )

    st.caption(
        "Обобщена оперативна информация за хотела"
    )

with logout_col:
    if st.button(
        "🚪 Изход",
        key="admin_logout",
        use_container_width=True
    ):
        st.session_state.admin_auth = False
        st.rerun()


# =========================================================
# ЗАРЕЖДАНЕ НА KPI
# =========================================================
try:
    kpis = get_admin_kpis()

except Exception as error:
    st.error(
        "Управленските показатели не могат "
        "да бъдат заредени."
        "\n\n"
        f"Причина: {error}"
    )

    kpis = {
        "room_service": 0,
        "spa": 0,
        "activities": 0,
        "service": 0,
        "unassigned": 0,
        "completed_today": 0
    }


# =========================================================
# KPI КАРТИ
# =========================================================
kpi_col1, kpi_col2, kpi_col3 = st.columns(
    3
)

with kpi_col1:
    st.metric(
        "🍽️ Активен Room Service",
        kpis["room_service"]
    )

with kpi_col2:
    st.metric(
        "💆 Активни SPA заявки",
        kpis["spa"]
    )

with kpi_col3:
    st.metric(
        "🎿 Активни Activities",
        kpis["activities"]
    )


kpi_col4, kpi_col5, kpi_col6 = st.columns(
    3
)

with kpi_col4:
    st.metric(
        "🔧 Активни сервизни задачи",
        kpis["service"]
    )

with kpi_col5:
    st.metric(
        "⚠️ Без изпълнител",
        kpis["unassigned"]
    )

with kpi_col6:
    st.metric(
        "✅ Завършени днес",
        kpis["completed_today"]
    )


st.divider()


# =========================================================
# ИЗГЛЕДИ
# =========================================================
OVERVIEW_VIEW = "📋 Оперативен център"
STATISTICS_VIEW = "📊 Статистика"
STAFF_VIEW = "👥 Служители"
ROOMS_VIEW = "🏨 Стаи"

admin_views = [
    OVERVIEW_VIEW,
    STATISTICS_VIEW,
    STAFF_VIEW,
    ROOMS_VIEW
]

if "admin_view" not in st.session_state:
    st.session_state.admin_view = OVERVIEW_VIEW

if st.session_state.admin_view not in admin_views:
    st.session_state.admin_view = OVERVIEW_VIEW

admin_view = st.radio(
    "Admin изглед",
    admin_views,
    horizontal=True,
    label_visibility="collapsed",
    key="admin_view"
)


st.divider()


# =========================================================
# ОПЕРАТИВЕН ЦЕНТЪР
# =========================================================
if admin_view == OVERVIEW_VIEW:

    st.subheader(
        "📋 Всички активни операции"
    )

    try:
        active_operations = (
            get_all_active_operations()
        )

    except Exception as error:
        st.error(
            "Активните операции не могат "
            "да бъдат заредени."
            "\n\n"
            f"Причина: {error}"
        )

        active_operations = []

    if not active_operations:
        st.success(
            "В момента няма активни операции."
        )

    else:
        for operation in active_operations:

            module = operation["module"]

            module_labels = {
                "ROOM_SERVICE": "🍽️ Room Service",
                "SPA": "💆 SPA",
                "ACTIVITIES": "🎿 Activities",
                "SERVICE": "🔧 Обслужване"
            }

            with st.container(
                border=True
            ):
                row_col1, row_col2, row_col3 = (
                    st.columns([5, 2, 2])
                )

                with row_col1:
                    st.subheader(
                        module_labels.get(
                            module,
                            module
                        )
                    )

                    st.markdown(
                        "### 🏨 "
                        f"Стая №"
                        f"{operation['room_number']}"
                    )

                    st.write(
                        f"**{operation['title']}**"
                    )

                    if (
                        operation.get(
                            "reservation"
                        )
                    ):
                        st.write(
                            "📅 Резервация: "
                            f"{operation['reservation']}"
                        )

                    if (
                        module == "SERVICE"
                        and operation.get(
                            "assigned_to"
                        )
                    ):
                        st.success(
                            "👤 Изпълнител: "
                            f"{operation['assigned_to']}"
                        )

                    elif module == "SERVICE":
                        st.warning(
                            "⚠️ Няма назначен изпълнител"
                        )

                with row_col2:
                    st.write(
                        "**Статус:**"
                    )

                    st.write(
                        get_status_label(
                            operation["status"]
                        )
                    )

                    if operation.get(
                        "priority"
                    ):
                        st.write(
                            "**Приоритет:** "
                            f"{operation['priority']}"
                        )

                with row_col3:
                    if operation.get(
                        "amount"
                    ) is not None:
                        st.metric(
                            "Стойност",
                            "€ "
                            f"{operation['amount']:.2f}"
                        )

                    if operation.get(
                        "created_at"
                    ):
                        st.caption(
                            "Получена: "
                            f"{format_datetime(
                                operation['created_at']
                            )}"
                        )


# =========================================================
# СТАТИСТИКА
# =========================================================
elif admin_view == STATISTICS_VIEW:

    st.subheader(
        "📊 Оперативна статистика"
    )

    try:
        today_statistics = (
            get_today_statistics()
        )

        top_service_types = (
            get_top_service_request_types()
        )

    except Exception as error:
        st.error(
            "Статистиката не може да бъде заредена."
            "\n\n"
            f"Причина: {error}"
        )

        today_statistics = {
            "room_service": 0,
            "spa": 0,
            "activities": 0,
            "service": 0,
            "room_service_revenue": 0
        }

        top_service_types = []

    stat_col1, stat_col2, stat_col3, stat_col4 = (
        st.columns(4)
    )

    with stat_col1:
        st.metric(
            "🍽️ Room Service днес",
            today_statistics["room_service"]
        )

    with stat_col2:
        st.metric(
            "💆 SPA днес",
            today_statistics["spa"]
        )

    with stat_col3:
        st.metric(
            "🎿 Activities днес",
            today_statistics["activities"]
        )

    with stat_col4:
        st.metric(
            "🔧 Сервизни заявки днес",
            today_statistics["service"]
        )

    st.metric(
        "💶 Room Service оборот днес",
        "€ "
        f"{today_statistics[
            'room_service_revenue'
        ]:.2f}"
    )

    st.divider()

    st.subheader(
        "🔧 Най-чести сервизни заявки "
        "за последните 30 дни"
    )

    if not top_service_types:
        st.info(
            "Няма достатъчно данни за периода."
        )

    else:
        for request_type, request_count in (
            top_service_types
        ):
            st.write(
                f"**{request_type}**"
            )

            st.progress(
                min(
                    float(request_count)
                    / float(
                        top_service_types[0][1] or 1
                    ),
                    1.0
                ),
                text=(
                    f"{request_count} заявки"
                )
            )


# =========================================================
# СЛУЖИТЕЛИ
# =========================================================
elif admin_view == STAFF_VIEW:

    st.subheader(
        "👥 Натоварване по служители"
    )

    try:
        staff_rows = get_staff_workload()

    except Exception as error:
        st.error(
            "Натоварването по служители "
            "не може да бъде заредено."
            "\n\n"
            f"Причина: {error}"
        )

        staff_rows = []

    if not staff_rows:
        st.info(
            "Няма назначени активни задачи."
        )

    else:
        for staff_name, active_count, in_progress_count in (
            staff_rows
        ):
            with st.container(
                border=True
            ):
                staff_col1, staff_col2, staff_col3 = (
                    st.columns([4, 2, 2])
                )

                with staff_col1:
                    st.subheader(
                        f"👤 {staff_name}"
                    )

                with staff_col2:
                    st.metric(
                        "Активни задачи",
                        int(active_count or 0)
                    )

                with staff_col3:
                    st.metric(
                        "В процес",
                        int(in_progress_count or 0)
                    )


# =========================================================
# СТАИ
# =========================================================
elif admin_view == ROOMS_VIEW:

    st.subheader(
        "🏨 Натоварване по стаи "
        "за последните 30 дни"
    )

    try:
        room_rows = get_room_workload()

    except Exception as error:
        st.error(
            "Натоварването по стаи "
            "не може да бъде заредено."
            "\n\n"
            f"Причина: {error}"
        )

        room_rows = []

    if not room_rows:
        st.info(
            "Няма достатъчно данни за периода."
        )

    else:
        maximum_room_requests = float(
            room_rows[0][1] or 1
        )

        for room_number, total_requests in (
            room_rows
        ):
            st.write(
                f"**🏨 Стая №{room_number}**"
            )

            st.progress(
                min(
                    float(total_requests)
                    / maximum_room_requests,
                    1.0
                ),
                text=(
                    f"{int(total_requests or 0)} "
                    "операции"
                )
            )


# =========================================================
# БРАНДИРАНЕ
# =========================================================
st.divider()

st.caption(
    "Powered by HMITSEVAPPS"
)
