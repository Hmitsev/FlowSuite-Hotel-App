from pathlib import Path

import streamlit as st

from database.db import get_connection
from translations import get_translations


# =====================================
# НАСТРОЙКИ НА СТРАНИЦАТА
# =====================================

st.set_page_config(
    page_title="Hotel Activities",
    page_icon="🎿",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =====================================
# ОБЩ ЕЗИК
# =====================================

if "lang" not in st.session_state:
    st.session_state.lang = "bg"

t = get_translations()


# =====================================
# SESSION STATE
# =====================================

if "activity_request_id" not in st.session_state:
    st.session_state.activity_request_id = None

if "activity_request_error" not in st.session_state:
    st.session_state.activity_request_error = None

# =====================================
# ПРЕВОДИ
# =====================================

TRANSLATIONS = {
    "bg": {
        "back": "⬅ Назад",
        "room": "Стая",
        "activity_name": "Наем на ски оборудване",
        "activity_description": (
            "Резервирайте ски оборудване директно чрез хотела."
        ),
        "info_button": "ℹ️ Информация и резервация",
        "reservation_title": "Заявка за резервация",
        "reservation_instruction": (
            "Моля, напишете за кой ден желаете резервация "
            "и добавете необходимата информация."
        ),
        "example_label": "Примерен коментар:",
        "example": (
            "Желая за 22.09.2026 г. да резервирам "
            "ски оборудване."
        ),
        "reception_message": (
            "От рецепцията ще се свържат с Вас за "
            "уточняване и потвърждение на резервацията."
        ),
        "message_label": "Вашето съобщение",
        "message_placeholder": (
            "Желая за 22.09.2026 г. да резервирам "
            "ски оборудване."
        ),
        "send_button": "✅ Изпрати заявка",
        "empty_message": (
            "Моля, напишете съобщение преди изпращане."
        ),
        "success": (
            "Заявката е изпратена успешно до рецепцията."
        ),
        "request_number": "Номер на заявката",
        "error": "Заявката не беше изпратена.",
        "footer": "Powered by HMITSEVAPPS",
    },
    "en": {
        "back": "⬅ Back",
        "room": "Room",
        "activity_name": "Ski Equipment Rental",
        "activity_description": (
            "Reserve ski equipment directly through the hotel."
        ),
        "info_button": "ℹ️ Information & Reservation",
        "reservation_title": "Reservation Request",
        "reservation_instruction": (
            "Please enter your preferred date and add the "
            "necessary information for the reservation."
        ),
        "example_label": "Example message:",
        "example": (
            "I would like to reserve ski equipment for "
            "22 September 2026."
        ),
        "reception_message": (
            "Reception will contact you to confirm the details "
            "of your reservation."
        ),
        "message_label": "Your message",
        "message_placeholder": (
            "I would like to reserve ski equipment for "
            "22 September 2026."
        ),
        "send_button": "✅ Send request",
        "empty_message": (
            "Please enter a message before sending the request."
        ),
        "success": (
            "Your request has been sent successfully to reception."
        ),
        "request_number": "Request number",
        "error": "The request was not sent.",
        "footer": "Powered by HMITSEVAPPS",
    },
}

t = TRANSLATIONS[st.session_state.activities_lang]


# =====================================
# CSS
# =====================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at top,
                rgba(28, 23, 15, 0.96) 0%,
                rgba(7, 10, 15, 0.98) 48%,
                rgba(3, 5, 8, 1) 100%
            );
        color: #F5E6C8;
    }

    [data-testid="stSidebar"] {
        display: none !important;
    }

    [data-testid="collapsedControl"] {
        display: none !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    [data-testid="stSpinner"] {
        display: none !important;
    }

    footer {
        visibility: hidden;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.2rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3, h4 {
        color: #F5E6C8 !important;
    }

    div[data-testid="stButton"] button {
        border-radius: 12px;
        font-weight: 700;
        min-height: 44px;
    }

    div[data-testid="stButton"] button[kind="primary"] {
        background:
            linear-gradient(
                135deg,
                #B98528,
                #D4AF37,
                #F5D77B
            ) !important;
        border: 1px solid #F5D77B !important;
        color: #111111 !important;
        font-weight: 800 !important;
    }

    div[data-testid="stButton"] button[kind="primary"] p {
        color: #111111 !important;
        font-weight: 800 !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(7, 11, 18, 0.92);
        border: 1px solid rgba(212, 175, 55, 0.38);
        border-radius: 18px;
        box-shadow:
            0 14px 35px rgba(0, 0, 0, 0.32);
    }

    [data-testid="stAlert"] {
        border-radius: 14px;
    }

    @media only screen and (max-width: 768px) {

        .block-container {
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        h1 {
            font-size: 29px !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =====================================
# НОМЕР НА СТАЯТА ОТ QR КОДА
# =====================================

raw_room_number = st.query_params.get(
    "room",
    "204"
)

try:
    room_number = int(raw_room_number)
except (TypeError, ValueError):
    room_number = 204

if room_number < 1 or room_number > 9999:
    st.error(
        "Невалиден номер на стая."
        if st.session_state.activities_lang == "bg"
        else "Invalid room number."
    )
    st.stop()


# =====================================
# ЗАПИС НА ЗАЯВКАТА В NEON
# =====================================

def create_activity_request(
    room_number,
    activity_name,
    guest_message
):
    clean_message = str(
        guest_message
    ).strip()

    if not clean_message:
        raise ValueError(
            t["empty_message"]
        )

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Намиране на активната стая
        cur.execute(
            """
            SELECT id
            FROM hotel_rooms
            WHERE room_number = %s
              AND is_active = TRUE
            LIMIT 1
            """,
            (int(room_number),)
        )

        room_result = cur.fetchone()

        if room_result is None:
            raise ValueError(
                f"Стая №{room_number} не е намерена "
                "или не е активна."
            )

        room_id = room_result[0]

        # Запис на Activities заявката
        cur.execute(
            """
            INSERT INTO activity_requests
            (
                room_id,
                activity_name,
                guest_message,
                request_status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                'NEW'
            )
            RETURNING id
            """,
            (
                room_id,
                str(activity_name).strip(),
                clean_message
            )
        )

        request_id = cur.fetchone()[0]

        conn.commit()

        return request_id

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()


# =====================================
# ГОРНА НАВИГАЦИЯ
# =====================================

back_col, space_col = st.columns(
    [1.3, 7]
)

with back_col:
    if st.button(
        t["back"],
        key="activities_back",
        use_container_width=True
    ):
        st.switch_page("app.py")

# =====================================
# БАНЕР
# =====================================

ACTIVITIES_BANNER_CANDIDATES = [
    "ChatGPT Image 19.09.2026 г., 16_12_00.png",
    "activities_banner.png",
    "activities_banner.jpg",
    "activities_banner.jpeg",
    "Hotel Activities.png",
    "Activities.png",
]

activities_banner_path = None

for banner_name in ACTIVITIES_BANNER_CANDIDATES:
    candidate_path = (
        Path("assets") / banner_name
    )

    if candidate_path.exists():
        activities_banner_path = candidate_path
        break

if activities_banner_path:
    st.image(
        str(activities_banner_path),
        use_container_width=True
    )


# =====================================
# ЗАГЛАВИЕ
# =====================================

st.markdown(
    f"""
    <div style="
        text-align:center;
        margin-top:18px;
        margin-bottom:22px;
    ">
        <div style="
            color:#D4AF37;
            font-size:36px;
            font-weight:900;
            letter-spacing:1px;
        ">
    </div>
    """,
    unsafe_allow_html=True
)


# =====================================
# СЪОБЩЕНИЕ ЗА УСПЕХ ИЛИ ГРЕШКА
# =====================================

if st.session_state.activity_request_error:
    st.error(
        f"{t['error']}\n\n"
        f"{st.session_state.activity_request_error}"
    )

    st.session_state.activity_request_error = None


if st.session_state.activity_request_id is not None:
    st.success(
        f"✅ {t['success']}\n\n"
        f"🧾 {t['request_number']}: "
        f"{st.session_state.activity_request_id}\n\n"
        f"🛎️ {t['room']} № {room_number}"
    )

    st.session_state.activity_request_id = None

# =====================================
# СКИ ОБОРУДВАНЕ
# =====================================

with st.container(border=True):

    activity_col, info_col = st.columns(
        [5.5, 2.5],
        vertical_alignment="center"
    )

    with activity_col:
        st.subheader("🎿 Наем на ски оборудване")

        st.write(
            "Резервирайте ски оборудване директно чрез хотела."
        )

    with info_col:
        with st.popover(
            "ℹ️ Информация и резервация",
            use_container_width=True
        ):

            st.markdown("### Заявка за резервация")

            st.write(
                "Моля, посочете дата и необходимата информация."
            )

            reservation_text = st.text_area(
                "Вашето съобщение",
                placeholder="Желая за 22.09.2026 г. да резервирам ски оборудване.",
                key="ski_reservation_message",
                height=130
            )

            st.caption(
                t["reception_message"]
            )

            if st.button(
                "✅ Изпрати заявка",
                key="send_ski_request",
                type="primary",
                use_container_width=True
            ):

                if not reservation_text.strip():

                    st.warning(
                        t["empty_message"]
                    )

                else:

                    try:

                        request_id = create_activity_request(
                            room_number=room_number,
                            activity_name="Ski Equipment Rental",
                            guest_message=reservation_text
                        )

                        st.session_state.activity_request_id = request_id
                        st.session_state.activity_request_error = None

                        st.rerun()

                    except Exception as error:

                        st.session_state.activity_request_error = str(error)

                        st.rerun()
                        # =====================================
# ВЕЛОСИПЕДИ
# =====================================

with st.container(border=True):

    activity_col, info_col = st.columns(
        [5.5, 2.5],
        vertical_alignment="center"
    )

    with activity_col:
        st.subheader("🚴 Наем на велосипед")

        st.write(
            "Резервирайте велосипед директно чрез хотела."
        )

    with info_col:
        with st.popover(
            "ℹ️ Информация и резервация",
            use_container_width=True
        ):

            st.markdown("### Заявка за резервация")

            st.write(
                "Моля, посочете дата, час и брой велосипеди."
            )

            bike_reservation_text = st.text_area(
                "Вашето съобщение",
                placeholder="Желая да наема 2 велосипеда за 22.09.2026 г. от 10:00 ч.",
                key="bike_reservation_message",
                height=130
            )

            st.caption(
                t["reception_message"]
            )

            if st.button(
                "✅ Изпрати заявка",
                key="send_bike_request",
                type="primary",
                use_container_width=True
            ):

                if not bike_reservation_text.strip():

                    st.warning(
                        t["empty_message"]
                    )

                else:

                    try:

                        request_id = create_activity_request(
                            room_number=room_number,
                            activity_name="Bike Rental",
                            guest_message=bike_reservation_text
                        )

                        st.session_state.activity_request_id = request_id
                        st.session_state.activity_request_error = None

                        st.rerun()

                    except Exception as error:

                        st.session_state.activity_request_error = str(error)

                        st.rerun()
# =====================================
# ФИНАЛНА ИНФОРМАЦИЯ
# =====================================

st.info(
    t["reception_message"]
)


# =====================================
# БРАНДИРАНЕ
# =====================================

st.divider()

st.caption(
    t["footer"]
)
