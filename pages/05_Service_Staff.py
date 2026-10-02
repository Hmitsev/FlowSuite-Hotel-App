import streamlit as st

from database.db import get_connection
from streamlit_autorefresh import st_autorefresh


# =========================================================
# НАСТРОЙКИ НА СТРАНИЦАТА
# =========================================================
st.set_page_config(
    page_title="Обслужващ персонал",
    page_icon="🔧",
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
        max-width: 1180px;
        padding-top: 0.7rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, p, label, span {
        color: #F5E6C8;
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
SERVICE_STAFF_PASSWORD = "service2026"

if "service_staff_auth" not in st.session_state:
    st.session_state.service_staff_auth = False


if not st.session_state.service_staff_auth:

    st.title("🔧 Обслужващ персонал")

    st.caption(
        "Панел за технически и камериерски задачи"
    )

    password = st.text_input(
        "Парола",
        type="password",
        key="service_staff_password"
    )

    if st.button(
        "Вход",
        key="service_staff_login",
        type="primary",
        use_container_width=True
    ):
        if password == SERVICE_STAFF_PASSWORD:
            st.session_state.service_staff_auth = True
            st.rerun()

        else:
            st.error(
                "Невалидна парола."
            )

    st.stop()


# =========================================================
# АВТОМАТИЧНО ОБНОВЯВАНЕ
# =========================================================
st_autorefresh(
    interval=30000,
    limit=None,
    key="service_staff_auto_refresh"
)


# =========================================================
# ФУНКЦИЯ ЗА ЗАРЕЖДАНЕ НА АКТИВНИТЕ ЗАДАЧИ
# =========================================================
def get_active_service_requests(
    department=None
):
    conn = get_connection()
    cur = conn.cursor()

    try:
        query = """
            SELECT
                sr.id,
                hr.room_number,
                sr.department,
                sr.category,
                sr.request_type,
                sr.guest_message,
                sr.guest_image,
                sr.guest_image_name,
                sr.guest_image_type,
                sr.priority,
                sr.request_status,
                sr.staff_note,
                sr.assigned_to,
                sr.assigned_at,
                sr.created_at,
                sr.accepted_at,
                sr.started_at,
                sr.updated_at
            FROM service_requests sr
            JOIN hotel_rooms hr
                ON hr.id = sr.room_id
            WHERE sr.request_status IN (
                'NEW',
                'ACCEPTED',
                'IN_PROGRESS'
            )
        """

        parameters = []

        if department:

            query += """
                AND sr.department = %s
            """

            parameters.append(
                department
            )

        query += """
            ORDER BY
                CASE sr.priority
                    WHEN 'URGENT' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'NORMAL' THEN 3
                    WHEN 'LOW' THEN 4
                    ELSE 5
                END,
                sr.created_at ASC,
                sr.id ASC
        """

        cur.execute(
            query,
            tuple(parameters)
        )

        return cur.fetchall()

    finally:
        cur.close()
        conn.close()

# =========================================================
# ФУНКЦИЯ ЗА ЗАВЪРШЕНИТЕ ЗАДАЧИ
# =========================================================
def get_completed_service_requests():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT
                sr.id,
                hr.room_number,
                sr.department,
                sr.category,
                sr.request_type,
                sr.guest_message,
                sr.guest_image,
                sr.guest_image_name,
                sr.guest_image_type,
                sr.priority,
                sr.request_status,
                sr.staff_note,
                sr.assigned_to,
                sr.assigned_at,
                sr.created_at,
                sr.accepted_at,
                sr.started_at,
                sr.completed_at,
                sr.updated_at
            FROM service_requests sr
            JOIN hotel_rooms hr
                ON hr.id = sr.room_id
            WHERE sr.request_status IN (
                'COMPLETED',
                'CANCELLED'
            )
            ORDER BY
                COALESCE(
                    sr.completed_at,
                    sr.updated_at,
                    sr.created_at
                ) DESC,
                sr.id DESC
            LIMIT 200
            """
        )

        return cur.fetchall()

    finally:
        cur.close()
        conn.close()


# =========================================================
# БРОЙ ЗАДАЧИ ПО СТАТУС И ОТДЕЛ
# =========================================================
def get_service_request_counts():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT
                COUNT(*) FILTER (
                    WHERE request_status = 'NEW'
                ) AS new_count,

                COUNT(*) FILTER (
                    WHERE request_status = 'ACCEPTED'
                ) AS accepted_count,

                COUNT(*) FILTER (
                    WHERE request_status = 'IN_PROGRESS'
                ) AS in_progress_count,

                COUNT(*) FILTER (
                    WHERE department = 'MAINTENANCE'
                      AND request_status IN (
                          'NEW',
                          'ACCEPTED',
                          'IN_PROGRESS'
                      )
                ) AS maintenance_count,

                COUNT(*) FILTER (
                    WHERE department = 'HOUSEKEEPING'
                      AND request_status IN (
                          'NEW',
                          'ACCEPTED',
                          'IN_PROGRESS'
                      )
                ) AS housekeeping_count

            FROM service_requests
            """
        )

        row = cur.fetchone()

        return {
            "NEW": int(row[0] or 0),
            "ACCEPTED": int(row[1] or 0),
            "IN_PROGRESS": int(row[2] or 0),
            "MAINTENANCE": int(row[3] or 0),
            "HOUSEKEEPING": int(row[4] or 0)
        }

    finally:
        cur.close()
        conn.close()


# =========================================================
# ПРОМЯНА НА СТАТУС, ИЗПЪЛНИТЕЛ И СЛУЖЕБНА БЕЛЕЖКА
# =========================================================
def update_service_request(
    request_id,
    new_status,
    staff_note="",
    assigned_to=""
):
    allowed_statuses = {
        "NEW",
        "ACCEPTED",
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED"
    }

    normalized_status = str(
        new_status or ""
    ).strip().upper()

    normalized_note = str(
        staff_note or ""
    ).strip()

    normalized_assigned_to = str(
        assigned_to or ""
    ).strip()

    if normalized_status not in allowed_statuses:
        raise ValueError(
            "Невалиден статус на задачата."
        )

    conn = get_connection()
    cur = conn.cursor()

    try:
        # =================================================
        # NEW
        # Запазва избрания изпълнител, но нулира времената
        # за приемане, започване и приключване.
        # =================================================
        if normalized_status == "NEW":
            cur.execute(
                """
                UPDATE service_requests
                SET
                    request_status = 'NEW',
                    staff_note = %s,
                    assigned_to = NULLIF(%s, ''),
                    assigned_at = CASE
                        WHEN NULLIF(%s, '') IS NOT NULL
                        THEN COALESCE(
                            assigned_at,
                            CURRENT_TIMESTAMP
                        )
                        ELSE NULL
                    END,
                    accepted_at = NULL,
                    started_at = NULL,
                    completed_at = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    normalized_note,
                    normalized_assigned_to,
                    normalized_assigned_to,
                    request_id
                )
            )

        # =================================================
        # ACCEPTED
        # Записва изпълнител, assigned_at и accepted_at.
        # =================================================
        elif normalized_status == "ACCEPTED":
            cur.execute(
                """
                UPDATE service_requests
                SET
                    request_status = 'ACCEPTED',
                    staff_note = %s,
                    assigned_to = NULLIF(%s, ''),
                    assigned_at = CASE
                        WHEN NULLIF(%s, '') IS NOT NULL
                        THEN COALESCE(
                            assigned_at,
                            CURRENT_TIMESTAMP
                        )
                        ELSE NULL
                    END,
                    accepted_at = COALESCE(
                        accepted_at,
                        CURRENT_TIMESTAMP
                    ),
                    started_at = NULL,
                    completed_at = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    normalized_note,
                    normalized_assigned_to,
                    normalized_assigned_to,
                    request_id
                )
            )

        # =================================================
        # IN_PROGRESS
        # Записва изпълнител, приемане и начало на работа.
        # =================================================
        elif normalized_status == "IN_PROGRESS":

            cur.execute(
                """
                UPDATE service_requests
                SET
                    request_status = 'IN_PROGRESS',
                    staff_note = %s,
                    assigned_to = %s,
        
                    accepted_at = COALESCE(
                        accepted_at,
                        CURRENT_TIMESTAMP
                    ),
        
                    started_at = COALESCE(
                        started_at,
                        CURRENT_TIMESTAMP
                    ),
        
                    completed_at = NULL,
        
                    updated_at = CURRENT_TIMESTAMP
        
                WHERE id = %s
                """,
                (
                    normalized_note,
                    normalized_assigned_to,
                    request_id
                )
            )

        # =================================================
        # COMPLETED
        # Записва всички липсващи времена и приключва задачата.
        # =================================================
        elif normalized_status == "COMPLETED":

            cur.execute(
                """
                UPDATE service_requests
                SET
                    request_status = 'COMPLETED',
                    staff_note = %s,
                    assigned_to = %s,
        
                    accepted_at = COALESCE(
                        accepted_at,
                        CURRENT_TIMESTAMP
                    ),
        
                    started_at = COALESCE(
                        started_at,
                        CURRENT_TIMESTAMP
                    ),
        
                    completed_at = CURRENT_TIMESTAMP,
        
                    updated_at = CURRENT_TIMESTAMP
        
                WHERE id = %s
                """,
                (
                    normalized_note,
                    normalized_assigned_to,
                    request_id
                )
            )

        # =================================================
        # CANCELLED
        # Запазва изпълнителя и приключва задачата като отказана.
        # =================================================
        elif normalized_status == "CANCELLED":

            cur.execute(
                """
                UPDATE service_requests
                SET
                    request_status = 'CANCELLED',
                    staff_note = %s,
                    assigned_to = %s,
        
                    completed_at = CURRENT_TIMESTAMP,
        
                    updated_at = CURRENT_TIMESTAMP
        
                WHERE id = %s
                """,
                (
                    normalized_note,
                    normalized_assigned_to,
                    request_id
                )
            )
# =========================================================
# ПОМОЩНИ ФУНКЦИИ ЗА ИНТЕРФЕЙСА
# =========================================================
def get_department_label(
    department
):
    labels = {
        "MAINTENANCE": "🛠️ Техническа задача",
        "HOUSEKEEPING": "🧹 Камериерска задача"
    }

    return labels.get(
        department,
        department
    )


def get_status_label(
    status
):
    labels = {
        "NEW": "🔴 Нова",
        "ACCEPTED": "🟡 Приета",
        "IN_PROGRESS": "🔵 В процес",
        "COMPLETED": "🟢 Завършена",
        "CANCELLED": "⚫ Отказана"
    }

    return labels.get(
        status,
        status
    )


def get_priority_label(
    priority
):
    labels = {
        "URGENT": "🔴 Спешен",
        "HIGH": "🟠 Висок",
        "NORMAL": "🟡 Нормален",
        "LOW": "🟢 Нисък"
    }

    return labels.get(
        priority,
        priority
    )


def normalize_image_bytes(
    image_value
):
    if image_value is None:
        return None

    if isinstance(
        image_value,
        memoryview
    ):
        return image_value.tobytes()

    if isinstance(
        image_value,
        bytearray
    ):
        return bytes(image_value)

    if isinstance(
        image_value,
        bytes
    ):
        return image_value

    return None


# =========================================================
# ГОРНА ЧАСТ НА ПАНЕЛА
# =========================================================
title_col, logout_col = st.columns(
    [5, 1],
    vertical_alignment="center"
)

with title_col:
    st.title(
        "🔧 Обслужващ персонал"
    )

    st.caption(
        "Технически и камериерски задачи"
    )

with logout_col:
    if st.button(
        "🚪 Изход",
        key="service_staff_logout",
        use_container_width=True
    ):
        st.session_state.service_staff_auth = False
        st.rerun()


# =========================================================
# БРОЙ ЗАДАЧИ
# =========================================================
try:
    request_counts = get_service_request_counts()

except Exception as error:
    st.error(
        "Броят на задачите не може да бъде зареден."
        "\n\n"
        f"Причина: {error}"
    )

    request_counts = {
        "NEW": 0,
        "ACCEPTED": 0,
        "IN_PROGRESS": 0,
        "MAINTENANCE": 0,
        "HOUSEKEEPING": 0
    }


    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(
        4
    )
    
    with metric_col1:
        st.metric(
            "🔴 Нови",
            request_counts["NEW"]
        )
    
    with metric_col2:
        st.metric(
            "🟡 Приети",
            request_counts["ACCEPTED"]
        )
    
    with metric_col3:
        st.metric(
            "🔵 В процес",
            request_counts["IN_PROGRESS"]
        )
    
    with metric_col4:
        try:
    
            conn = get_connection()
            cur = conn.cursor()
    
            cur.execute(
                """
                SELECT COUNT(*)
                FROM service_requests
                WHERE completed_at IS NOT NULL
                  AND DATE(completed_at) = CURRENT_DATE
                """
            )
    
            completed_today = int(
                cur.fetchone()[0] or 0
            )
    
        except Exception:
            completed_today = 0
    
        finally:
            try:
                cur.close()
                conn.close()
            except:
                pass
    
        st.metric(
            "✅ Завършени днес",
            completed_today
        )
# =========================================================
# DASHBOARD
# =========================================================

dashboard_col1, dashboard_col2 = st.columns(2)

with dashboard_col1:

    unassigned_count = 0

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT COUNT(*)
            FROM service_requests
            WHERE request_status IN (
                'NEW',
                'ACCEPTED',
                'IN_PROGRESS'
            )
            AND (
                assigned_to IS NULL
                OR TRIM(assigned_to) = ''
            )
            """
        )

        unassigned_count = int(
            cur.fetchone()[0] or 0
        )

    except Exception:
        pass

    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

    if unassigned_count > 0:

        st.warning(
            f"⚠️ Има {unassigned_count} неназначени задачи"
        )

    else:

        st.success(
            "✅ Всички активни задачи имат изпълнител"
        )


with dashboard_col2:

    active_total = (
        request_counts["NEW"]
        + request_counts["ACCEPTED"]
        + request_counts["IN_PROGRESS"]
    )

    st.info(
        f"📋 Общо активни задачи: {active_total}"
    )

st.divider()

# =========================================================
# ИЗГЛЕДИ
# =========================================================
ALL_VIEW = "📋 Всички активни"

MAINTENANCE_VIEW = (
    f"🛠️ Технически "
    f"({request_counts['MAINTENANCE']})"
)

HOUSEKEEPING_VIEW = (
    f"🧹 Камериерски "
    f"({request_counts['HOUSEKEEPING']})"
)

COMPLETED_VIEW = "✅ Завършени"


view_options = [
    ALL_VIEW,
    MAINTENANCE_VIEW,
    HOUSEKEEPING_VIEW,
    COMPLETED_VIEW
]


if "service_staff_view" not in st.session_state:
    st.session_state.service_staff_view = ALL_VIEW


if st.session_state.service_staff_view not in view_options:
    st.session_state.service_staff_view = ALL_VIEW


selected_view = st.radio(
    "Изглед",
    view_options,
    horizontal=True,
    label_visibility="collapsed",
    key="service_staff_view"
)


st.divider()


# =========================================================
# ЗАРЕЖДАНЕ НА ЗАДАЧИТЕ
# =========================================================
try:
    if selected_view == MAINTENANCE_VIEW:
        service_rows = get_active_service_requests(
            department="MAINTENANCE"
        )

    elif selected_view == HOUSEKEEPING_VIEW:
        service_rows = get_active_service_requests(
            department="HOUSEKEEPING"
        )

    elif selected_view == COMPLETED_VIEW:
        service_rows = get_completed_service_requests()

    else:
        service_rows = get_active_service_requests()

except Exception as error:
    st.error(
        "Задачите не могат да бъдат заредени."
        "\n\n"
        f"Причина: {error}"
    )

    st.stop()


# =========================================================
# ЗАГЛАВИЕ НА ТЕКУЩИЯ ИЗГЛЕД
# =========================================================
if selected_view == COMPLETED_VIEW:
    st.subheader(
        "✅ Завършени задачи"
    )

else:
    st.subheader(
        "📋 Активни задачи"
    )


# =========================================================
# ПОКАЗВАНЕ НА ЗАДАЧИТЕ
# =========================================================
if not service_rows:

    if selected_view == COMPLETED_VIEW:
        st.info(
            "Все още няма завършени задачи."
        )

    else:
        st.success(
            "Няма активни задачи в този изглед."
        )

else:
    for row in service_rows:

        if selected_view == COMPLETED_VIEW:
            request_id = row[0]
            room_number = row[1]
            department = row[2]
            category = row[3]
            request_type = row[4]
            guest_message = row[5]
            guest_image = row[6]
            guest_image_name = row[7]
            guest_image_type = row[8]
            priority = row[9]
            request_status = row[10]
            staff_note = row[11]
            assigned_to = row[12]
            assigned_at = row[13]
            created_at = row[14]
            accepted_at = row[15]
            started_at = row[16]
            completed_at = row[17]
            updated_at = row[18]

        else:
            request_id = row[0]
            room_number = row[1]
            department = row[2]
            category = row[3]
            request_type = row[4]
            guest_message = row[5]
            guest_image = row[6]
            guest_image_name = row[7]
            guest_image_type = row[8]
            priority = row[9]
            request_status = row[10]
            staff_note = row[11]
            assigned_to = row[12]
            assigned_at = row[13]
            created_at = row[14]
            accepted_at = row[15]
            started_at = row[16]
            updated_at = row[17]

            completed_at = None

        request_status = str(
            request_status or "NEW"
        ).strip().upper()

        priority = str(
            priority or "NORMAL"
        ).strip().upper()

        with st.container(
            border=True
        ):
            title_col, status_col = st.columns(
                [5, 2]
            )

            with title_col:
                st.subheader(
                    f"{get_department_label(department)} "
                    f"#{request_id}"
                )

                st.markdown(
                    f"### 🏨 Стая №{room_number}"
                )

                st.write(
                    f"**Заявка:** {request_type}"
                )
                if assigned_to:

                    st.success(
                        f"👤 Изпълнител: {assigned_to}"
                    )
                
                else:
                
                    st.warning(
                        "⚠️ Няма назначен изпълнител"
                    )

                st.caption(
                    f"Категория: {category}"
                )

            with status_col:
                st.write(
                    f"**Статус:** "
                    f"{get_status_label(request_status)}"
                )

                priority_colors = {
                    "URGENT": "#dc2626",
                    "HIGH": "#ea580c",
                    "NORMAL": "#ca8a04",
                    "LOW": "#16a34a"
                }
                
                priority_icons = {
                    "URGENT": "🔴",
                    "HIGH": "🟠",
                    "NORMAL": "🟡",
                    "LOW": "🟢"
                }
                priority_labels = {
                    "URGENT": "СПЕШНО",
                    "HIGH": "ПРИОРИТЕТНО",
                    "NORMAL": "СТАНДАРТНО",
                    "LOW": "НИСКА ВАЖНОСТ"
                }

                st.markdown(
                    f"""
                    <div style="
                        background:{priority_colors.get(priority, '#374151')};
                        color:white;
                        border-radius:10px;
                        padding:10px;
                        text-align:center;
                        font-weight:800;
                        margin-top:8px;
                        margin-bottom:8px;
                    ">
                        {priority_icons.get(priority, '⚪')}
                        {priority_labels.get(priority, priority)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if created_at:
                    st.caption(
                        "Подадена: "
                        f"{created_at.strftime('%d.%m.%Y %H:%M')}"
                    )

            if guest_message:
                st.markdown(
                    "#### 💬 Коментар от госта"
                )

                st.info(
                    guest_message
                )

            image_bytes = normalize_image_bytes(
                guest_image
            )

            if image_bytes:
                st.markdown(
                    "#### 📷 Снимка от госта"
                )

                st.image(
                    image_bytes,
                    caption=(
                        guest_image_name
                        or f"Снимка към заявка #{request_id}"
                    ),
                    width=500
                )

            if selected_view == COMPLETED_VIEW:

                if staff_note:
                    st.markdown(
                        "#### 📝 Служебна бележка"
                    )

                    st.info(
                        staff_note
                    )

                history_col1, history_col2 = st.columns(
                    2
                )

                with history_col1:
                    if accepted_at:
                        st.caption(
                            "Приета: "
                            f"{accepted_at.strftime('%d.%m.%Y %H:%M')}"
                        )

                    if started_at:
                        st.caption(
                            "Започната: "
                            f"{started_at.strftime('%d.%m.%Y %H:%M')}"
                        )

                with history_col2:
                    if completed_at:
                        st.caption(
                            "Приключена: "
                            f"{completed_at.strftime('%d.%m.%Y %H:%M')}"
                        )

                    elif updated_at:
                        st.caption(
                            "Последна промяна: "
                            f"{updated_at.strftime('%d.%m.%Y %H:%M')}"
                        )

            else:
                status_options = [
                    "NEW",
                    "ACCEPTED",
                    "IN_PROGRESS",
                    "COMPLETED",
                    "CANCELLED"
                ]

                with st.form(
                    key=f"service_request_form_{request_id}",
                    clear_on_submit=False
                ):
                    form_col1, form_col2 = st.columns(
                        [2, 3]
                    )

                    with form_col1:
                        selected_status = st.selectbox(
                            "Статус",
                            status_options,
                            index=(
                                status_options.index(
                                    request_status
                                )
                                if request_status in status_options
                                else 0
                            ),
                            format_func=get_status_label,
                            key=f"service_status_{request_id}"
                        )

                    with form_col2:

                        selected_assigned_to = st.selectbox(
                            "Изпълнител",
                            [
                                "Изберете изпълнител",
                                "Иван",
                                "Служител 2",
                                "Служител 3",
                                "Служител 4",
                                "Служител 5"
                            ],
                            index=(
                                [
                                    "",
                                    "Иван",
                                    "Служител 2",
                                    "Служител 3",
                                    "Служител 4",
                                    "Служител 5"
                                ].index(assigned_to)
                                if assigned_to in [
                                    "",
                                    "Иван",
                                    "Служител 2",
                                    "Служител 3",
                                    "Служител 4",
                                    "Служител 5"
                                ]
                                else 0
                            ),
                            key=f"assigned_to_{request_id}"
                        )
                    
                        selected_staff_note = st.text_area(
                            "Служебна бележка",
                            value=staff_note or "",
                            placeholder="",
                            height=100,
                            key=f"service_note_{request_id}"
                        )

                    save_status = st.form_submit_button(
                        "💾 Запази статуса",
                        type="primary",
                        use_container_width=True
                    )

                    if save_status:
                        try:
                            update_service_request(
                                request_id=request_id,
                                new_status=selected_status,
                                staff_note=selected_staff_note,
                                assigned_to=selected_assigned_to
                            )

                            st.success(
                                "Статусът е обновен успешно."
                            )

                            st.rerun()

                        except Exception as error:
                            st.error(
                                "Статусът не беше обновен."
                                "\n\n"
                                f"Причина: {error}"
                            )


# =========================================================
# БРАНДИРАНЕ
# =========================================================
st.divider()

st.caption(
    "Powered by HMITSEVAPPS"
)
