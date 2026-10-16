import streamlit as st

from database.queries import create_service_request


# =========================================================
# НАСТРОЙКИ НА СТРАНИЦАТА
# =========================================================
st.set_page_config(
    page_title="Помощ и обслужване",
    page_icon="🛎️",
    layout="wide"
)


# =========================================================
# ЕЗИК
# =========================================================
if "lang" not in st.session_state:
    st.session_state.lang = "bg"

language = st.session_state.get(
    "lang",
    "bg"
)


# =========================================================
# ТЕКСТОВЕ
# =========================================================
TEXTS = {
    "bg": {
        "back": "⬅ Назад",
        "title": "Помощ и обслужване",
        "subtitle": (
            "Подайте сигнал или заявка към "
            "обслужващия персонал."
        ),
        "room": "Стая",
        "department": "Изберете категория",
        "maintenance": "🛠️ Технически проблем",
        "housekeeping": "🧹 Камериерско обслужване",
        "request_type": "Изберете вид на заявката",
        "comment": "Допълнителен коментар",
        "comment_placeholder": (
            "Опишете проблема или желаната услуга..."
        ),
        "photo_title": "📷 Снимка към сигнала",
        "photo_help": (
            "При желание направете снимка, "
            "за да покажете проблема."
        ),
        "send": "✅ Изпрати сигнал",
        "sending": "Сигналът се изпраща...",
        "success": "Сигналът е изпратен успешно.",
        "request_number": "Номер на заявката",
        "staff_information": (
            "Обслужващият персонал вече вижда "
            "Вашата заявка."
        ),
        "new_request": "➕ Подай нов сигнал",
        "error": "Сигналът не беше изпратен.",
        "select_request": (
            "Моля, изберете конкретен вид "
            "на заявката."
        ),
        "camera_note": (
            "На телефон бутонът по-долу ще Ви позволи "
            "да използвате камерата на устройството."
        ),
        "footer": "Powered by HMITSEVAPPS"
    },
    "en": {
        "back": "⬅ Back",
        "title": "Help and service",
        "subtitle": (
            "Send a request or report a problem "
            "to the hotel service staff."
        ),
        "room": "Room",
        "department": "Select a category",
        "maintenance": "🛠️ Technical problem",
        "housekeeping": "🧹 Housekeeping service",
        "request_type": "Select request type",
        "comment": "Additional comment",
        "comment_placeholder": (
            "Describe the problem or requested service..."
        ),
        "photo_title": "📷 Photo attachment",
        "photo_help": (
            "You can take a photo to show the problem."
        ),
        "send": "✅ Send request",
        "sending": "Sending request...",
        "success": "Your request was sent successfully.",
        "request_number": "Request number",
        "staff_information": (
            "The hotel service staff can now see "
            "your request."
        ),
        "new_request": "➕ Send another request",
        "error": "The request was not sent.",
        "select_request": (
            "Please select a specific request type."
        ),
        "camera_note": (
            "On a mobile device, the button below "
            "allows you to use the device camera."
        ),
        "footer": "Powered by HMITSEVAPPS"
    }
}

t = TEXTS.get(
    language,
    TEXTS["bg"]
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

    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    footer {
        visibility: hidden;
    }

    .block-container {
        max-width: 980px;
        padding-top: 3rem;
        padding-bottom: 2.5rem;
    }

    h1, h2, h3, p, label, span {
        color: #F5E6C8;
    }

    .assistance-header {
        border: 1px solid rgba(212, 175, 55, 0.65);
        border-radius: 18px;
        padding: 10px;
        margin-top: 6px;
        margin-bottom: 20px;
        text-align: center;
        background:
            linear-gradient(
                135deg,
                rgba(15, 23, 42, 0.97),
                rgba(8, 14, 25, 0.97)
            );
        box-shadow:
            0 8px 28px rgba(0, 0, 0, 0.32),
            0 0 18px rgba(212, 175, 55, 0.12);
    }

    .assistance-title {
        color: #F5D77B;
        font-size: 30px;
        font-weight: 900;
        margin-bottom: 8px;
    }

    .assistance-subtitle {
        color: #F5E6C8;
        font-size: 16px;
        line-height: 1.5;
    }

    .room-card {
        border: 1px solid #D4AF37;
        border-radius: 14px;
        padding: 13px 18px;
        margin-bottom: 18px;
        text-align: center;
        color: #F5E6C8;
        background: rgba(15, 23, 42, 0.94);
        font-size: 21px;
        font-weight: 800;
    }

    .section-title {
        color: #F5D77B;
        font-size: 19px;
        font-weight: 800;
        margin-top: 12px;
        margin-bottom: 7px;
    }

    div[data-testid="stButton"] button,
    div[data-testid="stFormSubmitButton"] button {
        min-height: 44px !important;
        border-radius: 11px !important;
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
    /* Разгъващи се категории */
    div[data-testid="stExpander"] {
        border: 1px solid rgba(212, 175, 55, 0.65) !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        background: rgba(15, 23, 42, 0.90) !important;
    }
    
    div[data-testid="stExpander"] details {
        border: none !important;
    }
    
    div[data-testid="stExpander"] summary {
        min-height: 58px !important;
        padding: 10px 16px !important;
        font-weight: 800 !important;
        color: #F5E6C8 !important;
        background: rgba(15, 23, 42, 0.96) !important;
    }
    
    div[data-testid="stExpander"] summary:hover {
        background: rgba(26, 37, 58, 0.98) !important;
        color: #F5D77B !important;
    }
    
    div[data-testid="stExpander"] details[open] > summary {
        border-bottom: 1px solid rgba(212, 175, 55, 0.45) !important;
        color: #F5D77B !important;
    }
    
    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        padding: 12px !important;
        background: rgba(8, 14, 25, 0.96) !important;
    }

    @media only screen and (max-width: 768px) {
        .block-container {
            padding-top: 0.4rem;
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }

        .assistance-header {
            padding: 17px 12px;
        }

        .assistance-title {
            font-size: 24px;
        }

        .assistance-subtitle {
            font-size: 14px;
        }
        div[data-testid="stExpander"] summary {
            min-height: 52px !important;
            padding: 8px 12px !important;
            font-size: 14px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================
if "assistance_request_id" not in st.session_state:
    st.session_state.assistance_request_id = None

if "assistance_error" not in st.session_state:
    st.session_state.assistance_error = None


# =========================================================
# НАВИГАЦИЯ
# =========================================================
if st.button(
    t["back"],
    key="assistance_back",
    use_container_width=True
):
    st.switch_page("app.py")

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)


# =========================================================
# НОМЕР НА СТАЯТА
# =========================================================
room_number = st.session_state.get(
    "room_number",
    204
)


# =========================================================
# БАНЕР
# =========================================================
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.image(
        "assets/Designer (24).png",
        use_container_width=True
    )

st.markdown(
    f"""
    <div class="assistance-header">
        <div class="assistance-subtitle">
            {t["subtitle"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# УСПЕШНО ИЗПРАТЕНА ЗАЯВКА
# =========================================================
if st.session_state.assistance_request_id is not None:
    request_id = st.session_state.assistance_request_id

    st.success(
        f"✅ {t['success']}\n\n"
        f"🧾 {t['request_number']}: #{request_id}\n\n"
        f"🏨 {t['room']} №{room_number}\n\n"
        f"{t['staff_information']}"
    )

    if st.button(
        t["new_request"],
        key="new_assistance_request",
        type="primary",
        use_container_width=True
    ):
        st.session_state.assistance_request_id = None
        st.session_state.assistance_error = None
        st.rerun()

    st.caption(
        t["footer"]
    )

    st.stop()


# =========================================================
# ПОКАЗВАНЕ НА ГРЕШКА
# =========================================================
if st.session_state.assistance_error:
    st.error(
        f"{t['error']}\n\n"
        f"Причина: {st.session_state.assistance_error}"
    )

    st.session_state.assistance_error = None


# =========================================================
# КАТЕГОРИИ И ВИДОВЕ ЗАЯВКИ
# =========================================================
maintenance_requests = {
    "bg": [
        (
            "CLIMATE",
            "Климатикът не работи",
            "HIGH"
        ),
        (
            "LIGHTING",
            "Проблем с осветлението",
            "NORMAL"
        ),
        (
            "TELEVISION",
            "Телевизорът не работи",
            "NORMAL"
        ),
        (
            "INTERNET",
            "Проблем с интернет",
            "NORMAL"
        ),
        (
            "BATHROOM",
            "Технически проблем в банята",
            "HIGH"
        ),
        (
            "ELECTRICITY",
            "Проблем с електрозахранването",
            "URGENT"
        ),
        (
            "DOOR_LOCK",
            "Проблем с вратата или ключалката",
            "HIGH"
        ),
        (
            "OTHER_TECHNICAL",
            "Друг технически проблем",
            "NORMAL"
        )
    ],
    "en": [
        (
            "CLIMATE",
            "The air conditioning is not working",
            "HIGH"
        ),
        (
            "LIGHTING",
            "Lighting problem",
            "NORMAL"
        ),
        (
            "TELEVISION",
            "The television is not working",
            "NORMAL"
        ),
        (
            "INTERNET",
            "Internet problem",
            "NORMAL"
        ),
        (
            "BATHROOM",
            "Technical problem in the bathroom",
            "HIGH"
        ),
        (
            "ELECTRICITY",
            "Electrical problem",
            "URGENT"
        ),
        (
            "DOOR_LOCK",
            "Door or lock problem",
            "HIGH"
        ),
        (
            "OTHER_TECHNICAL",
            "Other technical problem",
            "NORMAL"
        )
    ]
}

housekeeping_requests = {
    "bg": [
        (
            "TOWELS",
            "Смяна на кърпи",
            "NORMAL"
        ),
        (
            "BED_LINEN",
            "Смяна на спално бельо",
            "NORMAL"
        ),
        (
            "EXTRA_CLEANING",
            "Допълнително почистване",
            "NORMAL"
        ),
        (
            "BATHROOM_CLEANING",
            "Почистване на банята",
            "NORMAL"
        ),
        (
            "AMENITIES",
            "Липсващи консумативи",
            "NORMAL"
        ),
        (
            "TOILETRIES",
            "Необходими тоалетни принадлежности",
            "NORMAL"
        ),
        (
            "OTHER_HOUSEKEEPING",
            "Друга камериерска заявка",
            "NORMAL"
        )
    ],
    "en": [
        (
            "TOWELS",
            "Towel replacement",
            "NORMAL"
        ),
        (
            "BED_LINEN",
            "Bed linen replacement",
            "NORMAL"
        ),
        (
            "EXTRA_CLEANING",
            "Additional room cleaning",
            "NORMAL"
        ),
        (
            "BATHROOM_CLEANING",
            "Bathroom cleaning",
            "NORMAL"
        ),
        (
            "AMENITIES",
            "Missing room amenities",
            "NORMAL"
        ),
        (
            "TOILETRIES",
            "Toiletries required",
            "NORMAL"
        ),
        (
            "OTHER_HOUSEKEEPING",
            "Other housekeeping request",
            "NORMAL"
        )
    ]
}


# =========================================================
# ИЗБОР НА КАТЕГОРИЯ И ВИД НА ЗАЯВКАТА
# =========================================================
st.markdown(
    f'<div class="section-title">{t["department"]}</div>',
    unsafe_allow_html=True
)

# Начални стойности
selected_department = None
selected_category = None
selected_request_type = None
selected_priority = None


# =========================================================
# ФУНКЦИИ ПРИ ИЗБОР
# =========================================================
def select_maintenance_request():
    selected_value = st.session_state.get(
        "maintenance_request_select",
        ""
    )

    if selected_value:
        st.session_state.housekeeping_request_select = ""


def select_housekeeping_request():
    selected_value = st.session_state.get(
        "housekeeping_request_select",
        ""
    )

    if selected_value:
        st.session_state.maintenance_request_select = ""


# =========================================================
# СПИСЪЦИ СПОРЕД ЕЗИКА
# =========================================================
current_maintenance_requests = maintenance_requests.get(
    language,
    maintenance_requests["bg"]
)

current_housekeeping_requests = housekeeping_requests.get(
    language,
    housekeeping_requests["bg"]
)

maintenance_labels = [
    request_data[1]
    for request_data in current_maintenance_requests
]

housekeeping_labels = [
    request_data[1]
    for request_data in current_housekeeping_requests
]


# =========================================================
# ДВЕ РАЗГЪВАЩИ СЕ КАТЕГОРИИ
# =========================================================
category_col1, category_col2 = st.columns(2)

with category_col1:
    with st.expander(
        t["maintenance"],
        expanded=False
    ):
        maintenance_choice = st.selectbox(
            t["request_type"],
            options=[""] + maintenance_labels,
            format_func=lambda value: (
                t["request_type"]
                if value == ""
                else value
            ),
            label_visibility="collapsed",
            key="maintenance_request_select",
            on_change=select_maintenance_request
        )

with category_col2:
    with st.expander(
        t["housekeeping"],
        expanded=False
    ):
        housekeeping_choice = st.selectbox(
            t["request_type"],
            options=[""] + housekeeping_labels,
            format_func=lambda value: (
                t["request_type"]
                if value == ""
                else value
            ),
            label_visibility="collapsed",
            key="housekeeping_request_select",
            on_change=select_housekeeping_request
        )


# =========================================================
# ОБРАБОТКА НА ИЗБРАНАТА ЗАЯВКА
# =========================================================
if maintenance_choice:
    selected_department = "MAINTENANCE"

    selected_request_data = next(
        (
            request_data
            for request_data in current_maintenance_requests
            if request_data[1] == maintenance_choice
        ),
        None
    )

elif housekeeping_choice:
    selected_department = "HOUSEKEEPING"

    selected_request_data = next(
        (
            request_data
            for request_data in current_housekeeping_requests
            if request_data[1] == housekeeping_choice
        ),
        None
    )

else:
    selected_request_data = None


if selected_request_data is not None:
    selected_category = selected_request_data[0]
    selected_request_type = selected_request_data[1]
    selected_priority = selected_request_data[2]


# =========================================================
# КОМЕНТАР
# =========================================================
st.markdown(
    f'<div class="section-title">{t["comment"]}</div>',
    unsafe_allow_html=True
)

guest_message = st.text_area(
    t["comment"],
    placeholder=t["comment_placeholder"],
    height=120,
    label_visibility="collapsed",
    key="assistance_guest_message"
)


# =========================================================
# СНИМКА ОТ КАМЕРАТА
# =========================================================
st.markdown(
    f'<div class="section-title">{t["photo_title"]}</div>',
    unsafe_allow_html=True
)

st.caption(
    t["photo_help"]
)

st.info(
    t["camera_note"]
)

guest_photo = None

if st.toggle(
    "📷 Добави снимка към сигнала",
    key="enable_camera"
):
    guest_photo = st.camera_input(
        "",
        key="assistance_guest_photo"
    )

# =========================================================
# ИЗПРАЩАНЕ НА ЗАЯВКАТА
# =========================================================
st.divider()

if st.button(
    t["send"],
    key="send_assistance_request",
    type="primary",
    use_container_width=True
):
    if selected_department is None:
        st.warning(t["department"])
        st.stop()

    if selected_request_type is None:
        st.warning(t["select_request"])
        st.stop()

    try:
        guest_image_bytes = None
        guest_image_name = None
        guest_image_type = None

        if guest_photo is not None:
            guest_image_bytes = guest_photo.getvalue()

            guest_image_name = (
                getattr(
                    guest_photo,
                    "name",
                    None
                )
                or f"room_{room_number}_photo.jpg"
            )

            guest_image_type = (
                getattr(
                    guest_photo,
                    "type",
                    None
                )
                or "image/jpeg"
            )

        with st.spinner(
            t["sending"]
        ):
            request_id = create_service_request(
                room_number=room_number,
                department=selected_department,
                category=selected_category,
                request_type=selected_request_type,
                guest_message=guest_message,
                guest_image=guest_image_bytes,
                guest_image_name=guest_image_name,
                guest_image_type=guest_image_type,
                priority=selected_priority
            )

        st.session_state.assistance_request_id = request_id
        st.session_state.assistance_error = None

        st.rerun()

    except Exception as error:
        st.session_state.assistance_error = str(
            error
        )

        st.rerun()


# =========================================================
# БРАНДИРАНЕ
# =========================================================
st.divider()

st.caption(
    t["footer"]
)
