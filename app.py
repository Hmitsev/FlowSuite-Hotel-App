import base64
from pathlib import Path

import streamlit as st


# =========================================================
# НАСТРОЙКИ НА СТРАНИЦАТА
# =========================================================
st.set_page_config(
    page_title="FlowSuite Hotel",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# ПЪТИЩА ДО ФАЙЛОВЕТЕ
# =========================================================
ASSETS_DIR = Path("assets")

# Приложението ще потърси първата намерена снимка.
# Ако в GitHub името е различно, добави го най-отгоре в списъка.
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
    """
    Връща първия намерен файл от assets.
    """
    for file_name in file_names:
        file_path = ASSETS_DIR / file_name

        if file_path.exists():
            return file_path

    return None


def open_hotel_page(page_path, service_name_bg, service_name_en):
    """
    Отваря съответната Streamlit страница, ако вече съществува.
    Ако още не е създадена, показва информационно съобщение.
    """
    target_page = Path(page_path)

    if target_page.exists():
        st.switch_page(page_path)
    else:
        if st.session_state.lang == "bg":
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


# =========================================================
# ПРЕВОДИ
# =========================================================
T = {
    "bg": {
        "hotel_services": "Хотелски услуги",
        "welcome": "Добре дошли",
        "room": "Стая",
        "room_service": "Room Service",
        "room_service_description": (
            "Поръчайте храна и напитки директно до Вашата стая."
        ),
        "spa": "SPA",
        "spa_description": (
            "Изпратете заявка за масаж или SPA процедура."
        ),
        "activities": "Дейности",
        "activities_description": (
            "Разгледайте и резервирайте хотелски активности."
        ),
        "reception_help": (
            "За допълнителна информация се свържете с рецепцията."
        ),
        "invalid_room": "Невалиден номер на стая.",
        "language": "BG",
    },
    "en": {
        "hotel_services": "Hotel Services",
        "welcome": "Welcome",
        "room": "Room",
        "room_service": "Room Service",
        "room_service_description": (
            "Order food and drinks directly to your room."
        ),
        "spa": "SPA",
        "spa_description": (
            "Send a request for a massage or SPA treatment."
        ),
        "activities": "Activities",
        "activities_description": (
            "Explore and book hotel activities."
        ),
        "reception_help": (
            "For additional information, please contact reception."
        ),
        "invalid_room": "Invalid room number.",
        "language": "ENG",
    },
}

t = T[st.session_state.lang]


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


# =========================================================
# ЗАРЕЖДАНЕ НА ХОТЕЛСКАТА СНИМКА
# =========================================================
hotel_banner_path = find_asset(HOTEL_BANNER_CANDIDATES)

hotel_banner_base64 = ""

if hotel_banner_path:
    hotel_banner_base64 = get_base64_image(hotel_banner_path)


# =========================================================
# ОСНОВЕН CSS
# =========================================================
page_style = f"""
<style>

/* =====================================================
   ОСНОВЕН ФОН
===================================================== */
.stApp {{
    background:
        radial-gradient(
            circle at top,
            rgba(28, 23, 15, 0.96) 0%,
            rgba(7, 10, 15, 0.98) 45%,
            rgba(3, 5, 8, 1) 100%
        );
    color: #F5E6C8;
}}


/* =====================================================
   СКРИВАНЕ НА STREAMLIT ЕЛЕМЕНТИ
===================================================== */
[data-testid="stSidebar"] {{
    display: none !important;
}}

[data-testid="collapsedControl"] {{
    display: none !important;
}}

[data-testid="stHeader"] {{
    background: transparent !important;
}}

[data-testid="stToolbar"] {{
    right: 1rem;
}}

[data-testid="stStatusWidget"] {{
    display: none !important;
}}

[data-testid="stSpinner"] {{
    display: none !important;
}}

.stSpinner {{
    display: none !important;
}}

footer {{
    visibility: hidden;
}}


/* =====================================================
   ОСНОВЕН КОНТЕЙНЕР
===================================================== */
.block-container {{
    max-width: 1450px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
    padding-left: 2rem;
    padding-right: 2rem;
}}


/* =====================================================
   ТЕКСТОВЕ
===================================================== */
h1, h2, h3 {{
    color: #F5E6C8 !important;
}}

p, label, span {{
    color: #F5E6C8;
}}


/* =====================================================
   ЕЗИКОВ БУТОН
===================================================== */
div[data-testid="stButton"] button {{
    border-radius: 14px;
    transition: all 0.25s ease;
}}


/* =====================================================
   ОСНОВНИ БУТОНИ
===================================================== */
div[data-testid="stButton"] button[kind="primary"] {{
    min-height: 66px;
    width: 100%;
    background:
        linear-gradient(
            135deg,
            #B98528 0%,
            #D4AF37 48%,
            #F5D77B 100%
        ) !important;
    border: 1px solid #F5D77B !important;
    border-radius: 16px !important;
    color: #101010 !important;
    font-size: 19px !important;
    font-weight: 800 !important;
    letter-spacing: 0.4px !important;
    box-shadow:
        0 8px 24px rgba(212, 175, 55, 0.22),
        inset 0 1px 0 rgba(255, 255, 255, 0.35);
}}

div[data-testid="stButton"] button[kind="primary"]:hover {{
    transform: translateY(-2px);
    border-color: #FFF0B3 !important;
    box-shadow:
        0 12px 30px rgba(212, 175, 55, 0.35),
        0 0 14px rgba(245, 215, 123, 0.18);
}}

div[data-testid="stButton"] button[kind="primary"] p {{
    color: #101010 !important;
    font-weight: 800 !important;
}}


/* =====================================================
   ВТОРИЧНИ БУТОНИ
===================================================== */
div[data-testid="stButton"] button[kind="secondary"] {{
    min-height: 42px;
    background: rgba(8, 12, 18, 0.86) !important;
    border: 1px solid rgba(212, 175, 55, 0.72) !important;
    color: #F5D77B !important;
    font-weight: 700 !important;
}}

div[data-testid="stButton"] button[kind="secondary"]:hover {{
    border-color: #FFD96A !important;
    color: #FFD96A !important;
    background: rgba(20, 23, 28, 0.95) !important;
}}


/* =====================================================
   МОБИЛЕН ИЗГЛЕД
===================================================== */
@media only screen and (max-width: 768px) {{

    .block-container {{
        padding-top: 0.8rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
        padding-bottom: 4rem;
    }}

    .hotel-hero {{
        min-height: 210px !important;
        border-radius: 16px !important;
    }}

    .hotel-hero-content {{
        padding: 22px 18px !important;
    }}

    .hotel-hero-title {{
        font-size: 28px !important;
    }}

    .hotel-hero-room {{
        font-size: 17px !important;
    }}

    .hotel-services-title {{
        font-size: 25px !important;
    }}

    .hotel-card {{
        min-height: 122px !important;
    }}

    div[data-testid="stButton"] button[kind="primary"] {{
        min-height: 58px;
        font-size: 17px !important;
    }}
}}

</style>
"""

st.markdown(
    page_style,
    unsafe_allow_html=True
)


# =========================================================
# ЕЗИКОВ БУТОН
# =========================================================
language_space, language_column = st.columns([8.6, 1.4])

with language_column:
    language_button_text = (
        "🇧🇬 BG"
        if st.session_state.lang == "bg"
        else "🇬🇧 ENG"
    )

    if st.button(
        language_button_text,
        key="language_toggle",
        use_container_width=True
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
        use_container_width=True
    )

    st.markdown(
        f"# {t['welcome']}"
    )
    
    st.markdown(
        f"### 🛎️ {t['room']} № {room_number}"
    )
        margin-top:10px;
        margin-bottom:20px;
        background:rgba(15,23,42,0.85);
        border:1px solid #D4AF37;
        border-radius:16px;
    ">
        <div style="
            color:#D4AF37;
            font-size:16px;
            font-weight:700;
            letter-spacing:3px;
        ">
            FLOWSUITE HOTEL
        </div>

        <div style="
            color:#FFFFFF;
            font-size:34px;
            font-weight:800;
            margin-top:10px;
        ">
            {t["welcome"]}
        </div>

        <div style="
            color:#F5D77B;
            font-size:20px;
            font-weight:700;
            margin-top:12px;
        ">
            🛎️ {t["room"]} № {room_number}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# ЗАГЛАВИЕ НА УСЛУГИТЕ
# =========================================================

st.markdown(
    f"""
    <h2 style="
        text-align:center;
        color:#F5E6C8;
        margin-top:20px;
        margin-bottom:30px;
    ">
        {t["hotel_services"]}
    </h2>
    """,
    unsafe_allow_html=True
)

# =========================================================
# КАРТИ НА УСЛУГИТЕ
# =========================================================
room_service_column, spa_column, activities_column = st.columns(
    3,
    gap="large"
)


# =========================================================
# ROOM SERVICE
# =========================================================
with room_service_column:

    st.markdown("## 🍽️")
    st.subheader("Room Service")
    st.caption("Поръчайте храна и напитки директно до Вашата стая.")

    if st.button(
        "🍽️ Room Service",
        key="room_service_btn",
        type="primary",
        use_container_width=True
    ):
        open_hotel_page(
            "pages/01_Room_Service.py",
            "Room Service",
            "Room Service"
        )

# =========================================================
# SPA
# =========================================================
with spa_column:

    st.markdown("## 💆")
    st.subheader("SPA")
    st.caption("Изпратете заявка за масаж или SPA процедура.")

    if st.button(
        "💆 SPA",
        key="spa_btn",
        type="primary",
        use_container_width=True
    ):
        open_hotel_page(
            "pages/02_SPA.py",
            "SPA",
            "SPA"
        )
# =========================================================
# ACTIVITIES
# =========================================================
with activities_column:

    st.markdown("## 🎿")
    st.subheader("Дейности")
    st.caption("Разгледайте и резервирайте хотелски активности.")

    if st.button(
        "🎿 Дейности",
        key="activities_btn",
        type="primary",
        use_container_width=True
    ):
        open_hotel_page(
            "pages/03_Activities.py",
            "Дейности",
            "Activities"
        )

# =========================================================
# ИНФОРМАЦИЯ ЗА РЕЦЕПЦИЯТА
# =========================================================
st.markdown(
    f"""
    <div
        style="
            max-width: 820px;
            margin: 36px auto 0 auto;
            padding: 15px 20px;
            border-top: 1px solid rgba(212,175,55,0.34);
            border-bottom: 1px solid rgba(212,175,55,0.18);
            color: #C8C4B9;
            font-size: 14px;
            text-align: center;
            letter-spacing: 0.2px;
        "
    >
        ☎️ {t["reception_help"]}
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# БРАНДИРАНЕ
# =========================================================
st.markdown(
    """
    <div style="
        text-align:center;
        color:#D4AF37;
        margin-top:30px;
        opacity:0.7;
        font-size:12px;
    ">
        Powered by HMITSEVAPPS
    </div>
    """,
    unsafe_allow_html=True
)
