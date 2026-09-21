import base64
from pathlib import Path

import streamlit as st
from translations import get_translations

# =========================================================
# НАСТРОЙКИ НА СТРАНИЦАТА
# =========================================================
st.set_page_config(
    page_title="FlowSuite Hotel",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# ПЪТИЩА ДО ФАЙЛОВЕТЕ
# =========================================================
ASSETS_DIR = Path("assets")

HOTEL_BANNER_CANDIDATES = [
    "Screenshot 2026-09-09 025734.png",
    "hotel_banner.png",
    "hotel.png",
    "Hotel.png",
    "hotel.jpeg",
    "hotel.jpg",
]


# =========================================================
# ПОМОЩНИ ФУНКЦИИ
# =========================================================
@st.cache_data
def get_base64_image(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


def find_asset(file_names):
    for file_name in file_names:
        file_path = ASSETS_DIR / file_name
        if file_path.exists():
            return file_path
    return None


def open_hotel_page(page_path, service_name_bg, service_name_en):
    target_page = Path(page_path)

    if target_page.exists():
        st.switch_page(page_path)
    elif st.session_state.lang == "bg":
        st.info(
            f"Секция „{service_name_bg}“ ще бъде добавена "
            "в следващата стъпка."
        )
    else:
        st.info(
            f"The “{service_name_en}” section will be added "
            "in the next step."
        )


# =========================================================
# SESSION STATE
# =========================================================
if "lang" not in st.session_state:
    st.session_state.lang = "bg"
t = get_translations()

# =========================================================
# НОМЕР НА СТАЯТА ОТ QR КОДА
# Пример: ?room=204
# =========================================================
raw_room_number = st.query_params.get("room", "204")

try:
    room_number = int(raw_room_number)
except (TypeError, ValueError):
    room_number = 204

if room_number < 1 or room_number > 9999:
    st.error(t["invalid_room"])
    st.stop()

# Запазваме стаята и в session_state за останалите страници.
st.session_state.room_number = room_number


# =========================================================
# ЗАРЕЖДАНЕ НА ХОТЕЛСКАТА СНИМКА
# =========================================================
hotel_banner_path = find_asset(HOTEL_BANNER_CANDIDATES)


# =========================================================
# ОСНОВЕН CSS
# ВАЖНО: няма f пред тройните кавички, затова CSS скобите са единични.
# =========================================================
page_style = """
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
[data-testid="stStatusWidget"],
[data-testid="stSpinner"],
.stSpinner {
    display: none !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stToolbar"] {
    right: 1rem;
}

footer {
    visibility: hidden;
}

.block-container {
    max-width: 1180px;
    padding-top: 0.45rem;
    padding-bottom: 2rem;
    padding-left: 1.25rem;
    padding-right: 1.25rem;
}

h1, h2, h3, p, label, span {
    color: #F5E6C8;
}

/* Всички Streamlit бутони */
div[data-testid="stButton"] button {
    min-height: 36px !important;
    height: 36px !important;
    padding: 0 0.65rem !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    line-height: 1 !important;
    transition: all 0.2s ease;
}

div[data-testid="stButton"] button p {
    margin: 0 !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    line-height: 1 !important;
}

/* Основни златни бутони */
div[data-testid="stButton"] button[kind="primary"],
div[data-testid="stButton"] button[data-testid="stBaseButton-primary"] {
    width: 100%;
    background: linear-gradient(
        135deg,
        #B98528 0%,
        #D4AF37 48%,
        #F5D77B 100%
    ) !important;
    border: 1px solid #F5D77B !important;
    color: #101010 !important;
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.18) !important;
}

div[data-testid="stButton"] button[kind="primary"] p,
div[data-testid="stButton"] button[data-testid="stBaseButton-primary"] p {
    color: #101010 !important;
}

div[data-testid="stButton"] button:hover {
    transform: translateY(-1px);
    border-color: #FFD96A !important;
}

/* Вторичен бутон, включително езиковия */
div[data-testid="stButton"] button[kind="secondary"],
div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"] {
    background: rgba(8, 12, 18, 0.86) !important;
    border: 1px solid rgba(212, 175, 55, 0.72) !important;
    color: #F5D77B !important;
}

div[data-testid="stButton"] button[kind="secondary"] p,
div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"] p {
    color: #F5D77B !important;
}

/* Компактен банер */
[data-testid="stImage"] img {
    width: 100% !important;
    max-height: 260px !important;
    object-fit: cover !important;
    border-radius: 14px !important;
}

.compact-welcome {
    margin: 8px 0 2px 0;
    text-align: center;
    font-size: 22px;
    font-weight: 750;
}

.hotel-services-title {
    margin: 2px 0 10px 0;
    text-align: center;
    font-size: 18px;
    font-weight: 700;
    color: #F5E6C8;
}

/* Намалява вертикалните празнини между Streamlit елементите */
[data-testid="stVerticalBlock"] {
    gap: 0.55rem;
}

[data-testid="stCaptionContainer"] p {
    margin: 0 !important;
    font-size: 12px !important;
    line-height: 1.2 !important;
}

@media only screen and (max-width: 768px) {
    .block-container {
        padding-top: 0.2rem;
        padding-left: 0.7rem;
        padding-right: 0.7rem;
        padding-bottom: 1.5rem;
    }

    [data-testid="stImage"] img {
        max-height: 180px !important;
        border-radius: 12px !important;
    }

    .compact-welcome {
        margin: 5px 0 0 0;
        font-size: 18px;
    }

    .hotel-services-title {
        margin: 0 0 7px 0;
        font-size: 16px;
    }

    div[data-testid="stButton"] button {
        min-height: 34px !important;
        height: 34px !important;
        padding: 0 0.5rem !important;
        font-size: 12px !important;
        border-radius: 9px !important;
    }

    div[data-testid="stButton"] button p {
        font-size: 12px !important;
    }

    [data-testid="stCaptionContainer"] p {
        font-size: 11px !important;
    }
}
</style>
"""

st.markdown(page_style, unsafe_allow_html=True)


language_space, language_column = st.columns([8.8, 1.2])

with language_column:
    language_button_text = (
        "🇬🇧 EN"
        if st.session_state.lang == "bg"
        else "🇧🇬 BG"
    )

    if st.button(
        language_button_text,
        key="language_toggle",
        use_container_width=True,
    ):
        st.session_state.lang = (
            "en"
            if st.session_state.lang == "bg"
            else "bg"
        )

        st.rerun()


# =========================================================
# ХОТЕЛСКИ БАНЕР
# =========================================================
if hotel_banner_path:
    st.image(
        str(hotel_banner_path),
        use_container_width=True,
    )

st.markdown(
    f'<div class="compact-welcome">{t["welcome"]}</div>',
    unsafe_allow_html=True,
)


# =========================================================
# КАРТИ НА УСЛУГИТЕ
# =========================================================
st.markdown("<div style='height:120px;'></div>", unsafe_allow_html=True)
room_service_column, spa_column, activities_column = st.columns(
    3,
    gap="medium",
)


# =========================================================
# ROOM SERVICE
# =========================================================
with room_service_column:
    st.markdown(
    f"""
    <div style="
        text-align:center;
        color:#F5D77B;
        font-size:15px;
        font-weight:600;
        margin-bottom:8px;
    ">
        st.caption(t["room_service_description"])
    </div>
    """,
    unsafe_allow_html=True
)

    if st.button(
        f"🍽️ {t['room_service']}"
        key="room_service_btn",
        type="primary",
        use_container_width=True,
    ):
        open_hotel_page(
            "pages/01_Room_Service.py",
            "Room Service",
            "Room Service",
        )


# =========================================================
# SPA
# =========================================================
with spa_column:
    st.markdown(
    f"""
    <div style="
        text-align:center;
        color:#F5D77B;
        font-size:15px;
        font-weight:600;
        margin-bottom:8px;
    ">
        st.caption(t["spa_description"])
    </div>
    """,
    unsafe_allow_html=True
)

    if st.button(
        f"💆 {t['spa']}"
        key="spa_btn",
        type="primary",
        use_container_width=True,
    ):
        open_hotel_page(
            "pages/02_SPA.py",
            "SPA",
            "SPA",
        )


# =========================================================
# ACTIVITIES
# =========================================================
with activities_column:
    st.markdown(
    f"""
    <div style="
        text-align:center;
        color:#F5D77B;
        font-size:15px;
        font-weight:600;
        margin-bottom:8px;
    ">
        st.caption(t["activities_description"])
    </div>
    """,
    unsafe_allow_html=True
)

    if st.button(
        f"🎿 {t['activities']}"
        key="activities_btn",
        type="primary",
        use_container_width=True,
    ):
        open_hotel_page(
            "pages/03_Activities.py",
            "Дейности",
            "Activities",
        )


# =========================================================
# БРАНДИРАНЕ
# =========================================================
st.caption("Powered by HMITSEVAPPS")
