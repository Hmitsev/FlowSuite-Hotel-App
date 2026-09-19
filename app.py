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
# ХОТЕЛСКИ HERO БАНЕР
# =========================================================
if hotel_banner_base64:

    st.markdown(
        f"""
        <div
            class="hotel-hero"
            style="
                position: relative;
                min-height: 360px;
                margin-top: 4px;
                margin-bottom: 26px;
                border: 1px solid rgba(212,175,55,0.60);
                border-radius: 22px;
                overflow: hidden;
                background-image:
                    linear-gradient(
                        90deg,
                        rgba(3,5,8,0.86) 0%,
                        rgba(3,5,8,0.40) 52%,
                        rgba(3,5,8,0.10) 100%
                    ),
                    linear-gradient(
                        0deg,
                        rgba(3,5,8,0.68) 0%,
                        rgba(3,5,8,0.05) 58%
                    ),
                    url('data:image/png;base64,{hotel_banner_base64}');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                box-shadow:
                    0 18px 50px rgba(0,0,0,0.50),
                    0 0 18px rgba(212,175,55,0.10);
            "
        >
            <div
                class="hotel-hero-content"
                style="
                    position: absolute;
                    left: 0;
                    bottom: 0;
                    max-width: 700px;
                    padding: 42px 46px;
                "
            >
                <div
                    style="
                        color: #D4AF37;
                        font-size: 14px;
                        font-weight: 800;
                        letter-spacing: 4px;
                        text-transform: uppercase;
                        margin-bottom: 10px;
                    "
                >
                    FlowSuite Hotel
                </div>

                <div
                    class="hotel-hero-title"
                    style="
                        color: #FFF5D6;
                        font-size: 43px;
                        font-weight: 800;
                        line-height: 1.05;
                        text-shadow: 0 4px 18px rgba(0,0,0,0.70);
                    "
                >
                    {t["welcome"]}
                </div>

                <div
                    class="hotel-hero-room"
                    style="
                        display: inline-block;
                        margin-top: 18px;
                        padding: 9px 18px;
                        color: #F5D77B;
                        background: rgba(3,5,8,0.76);
                        border: 1px solid rgba(212,175,55,0.72);
                        border-radius: 999px;
                        font-size: 19px;
                        font-weight: 800;
                        letter-spacing: 0.5px;
                        backdrop-filter: blur(8px);
                    "
                >
                    🛎️ {t["room"]} № {room_number}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.warning(
        "Хотелската снимка не е намерена в папка assets. "
        "Провери името в HOTEL_BANNER_CANDIDATES."
    )

    st.markdown(
        f"""
        <div
            style="
                padding: 38px 30px;
                margin-bottom: 26px;
                border: 1px solid rgba(212,175,55,0.60);
                border-radius: 22px;
                background:
                    linear-gradient(
                        135deg,
                        rgba(19,24,32,0.98),
                        rgba(7,10,15,0.98)
                    );
                text-align: center;
            "
        >
            <div
                style="
                    color: #D4AF37;
                    font-size: 14px;
                    font-weight: 800;
                    letter-spacing: 4px;
                    text-transform: uppercase;
                "
            >
                FlowSuite Hotel
            </div>

            <div
                style="
                    color: #FFF5D6;
                    font-size: 38px;
                    font-weight: 800;
                    margin-top: 10px;
                "
            >
                {t["welcome"]}
            </div>

            <div
                style="
                    color: #F5D77B;
                    font-size: 19px;
                    font-weight: 700;
                    margin-top: 12px;
                "
            >
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
    <div
        style="
            text-align: center;
            margin-top: 10px;
            margin-bottom: 24px;
        "
    >
        <div
            class="hotel-services-title"
            style="
                color: #F5E6C8;
                font-size: 31px;
                font-weight: 800;
                letter-spacing: 0.5px;
            "
        >
            {t["hotel_services"]}
        </div>

        <div
            style="
                width: 90px;
                height: 2px;
                margin: 12px auto 0 auto;
                background: linear-gradient(
                    90deg,
                    transparent,
                    #D4AF37,
                    transparent
                );
            "
        ></div>
    </div>
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

    st.markdown(
        f"""
        <div
            class="hotel-card"
            style="
                min-height: 145px;
                padding: 22px 20px;
                margin-bottom: 12px;
                border: 1px solid rgba(212,175,55,0.42);
                border-radius: 18px;
                background:
                    linear-gradient(
                        145deg,
                        rgba(19,24,32,0.94),
                        rgba(7,10,15,0.97)
                    );
                box-shadow: 0 10px 30px rgba(0,0,0,0.28);
                text-align: center;
            "
        >
            <div
                style="
                    font-size: 34px;
                    margin-bottom: 9px;
                "
            >
                🍽️
            </div>

            <div
                style="
                    color: #F5D77B;
                    font-size: 22px;
                    font-weight: 800;
                "
            >
                {t["room_service"]}
            </div>

            <div
                style="
                    color: #C8C4B9;
                    font-size: 14px;
                    line-height: 1.45;
                    margin-top: 8px;
                "
            >
                {t["room_service_description"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        f"🍽️ {t['room_service']}",
        key="open_room_service",
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

    st.markdown(
        f"""
        <div
            class="hotel-card"
            style="
                min-height: 145px;
                padding: 22px 20px;
                margin-bottom: 12px;
                border: 1px solid rgba(212,175,55,0.42);
                border-radius: 18px;
                background:
                    linear-gradient(
                        145deg,
                        rgba(19,24,32,0.94),
                        rgba(7,10,15,0.97)
                    );
                box-shadow: 0 10px 30px rgba(0,0,0,0.28);
                text-align: center;
            "
        >
            <div
                style="
                    font-size: 34px;
                    margin-bottom: 9px;
                "
            >
                💆
            </div>

            <div
                style="
                    color: #F5D77B;
                    font-size: 22px;
                    font-weight: 800;
                "
            >
                {t["spa"]}
            </div>

            <div
                style="
                    color: #C8C4B9;
                    font-size: 14px;
                    line-height: 1.45;
                    margin-top: 8px;
                "
            >
                {t["spa_description"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        f"💆 {t['spa']}",
        key="open_spa",
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

    st.markdown(
        f"""
        <div
            class="hotel-card"
            style="
                min-height: 145px;
                padding: 22px 20px;
                margin-bottom: 12px;
                border: 1px solid rgba(212,175,55,0.42);
                border-radius: 18px;
                background:
                    linear-gradient(
                        145deg,
                        rgba(19,24,32,0.94),
                        rgba(7,10,15,0.97)
                    );
                box-shadow: 0 10px 30px rgba(0,0,0,0.28);
                text-align: center;
            "
        >
            <div
                style="
                    font-size: 34px;
                    margin-bottom: 9px;
                "
            >
                🎿
            </div>

            <div
                style="
                    color: #F5D77B;
                    font-size: 22px;
                    font-weight: 800;
                "
            >
                {t["activities"]}
            </div>

            <div
                style="
                    color: #C8C4B9;
                    font-size: 14px;
                    line-height: 1.45;
                    margin-top: 8px;
                "
            >
                {t["activities_description"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        f"🎿 {t['activities']}",
        key="open_activities",
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
    <div
        style="
            position: fixed;
            right: 18px;
            bottom: 12px;
            color: #D4AF37;
            font-family: Arial, sans-serif;
            text-align: right;
            opacity: 0.78;
            z-index: 999;
            pointer-events: none;
        "
    >
        <div
            style="
                font-size: 17px;
                font-weight: 900;
                line-height: 1;
            "
        >
            HA
        </div>

        <div
            style="
                margin-top: 3px;
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 2px;
            "
        >
            HMITSEVAPPS
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
