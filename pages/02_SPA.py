import streamlit as st
from database.db import get_connection
if "spa_request_success" not in st.session_state:
    st.session_state.spa_request_success = False
from translations import get_translations    

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


# =====================================
# ЗАПИС НА SPA ЗАЯВКА
# =====================================

def create_spa_request(
    room_number,
    service_name,
    guest_message
):
    clean_message = str(
        guest_message
    ).strip()

    if not clean_message:
        raise ValueError(
            "Моля, въведете съобщение."
        )

    conn = get_connection()
    cur = conn.cursor()

    try:
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

        cur.execute(
            """
            INSERT INTO spa_requests
            (
                room_id,
                service_name,
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
                str(service_name).strip(),
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
# НАСТРОЙКИ НА СТРАНИЦАТА
# =====================================

st.set_page_config(
    page_title="SPA",
    page_icon="🧘🏻‍♀️",
    layout="wide"
)
if "lang" not in st.session_state:
    st.session_state.lang = "bg"

t = get_translations()
if "spa_request_success" not in st.session_state:
    st.session_state.spa_request_success = False

if "spa_success_service_name" not in st.session_state:
    st.session_state.spa_success_service_name = ""

if "spa_success_service_price" not in st.session_state:
    st.session_state.spa_success_service_price = 0
# =====================================
# SPA УСЛУГА
# =====================================

SPA_SERVICE_NAME = t["relaxing_massage"]
SPA_SERVICE_PRICE = 50
SPA_CURRENCY = "€"
# =====================================
# НАВИГАЦИЯ
# =====================================

nav_col1, nav_col2 = st.columns([1, 5])

with nav_col1:
    if st.button(
        t["back"],
        use_container_width=True
    ):
        st.switch_page("app.py")

# =====================================
# SPA БАНЕР
# =====================================

try:

    st.image(
        "assets/Designer (18).png",
        use_container_width=True
    )

except Exception:
    pass
# =====================================
# SPA КАРТА
# =====================================

with st.container(border=True):

    activity_col, info_col = st.columns(
        [5.5, 2.5],
        vertical_alignment="center"
    )

    with activity_col:

        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                flex-wrap:wrap;
                gap:12px;
                margin-bottom:8px;
            ">
                <div style="
                    color:#F5F5F5;
                    font-size:28px;
                    font-weight:700;
                ">
                    🧘🏻‍♀️ {SPA_SERVICE_NAME}
                </div>

                <div style="
                    background:linear-gradient(
                        135deg,
                        #D4AF37,
                        #B68A24
                    );
                    color:#111111;
                    border-radius:8px;
                    padding:5px 12px;
                    font-size:16px;
                    font-weight:800;
                    white-space:nowrap;
                ">
                    {SPA_SERVICE_PRICE:.2f} {SPA_CURRENCY}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write(
            t["relaxing_massage_description"]
        )

        st.markdown(
            f"""
            <div style="
                background:rgba(212, 175, 55, 0.10);
                border-left:4px solid #D4AF37;
                border-radius:8px;
                padding:12px 14px;
                margin-top:14px;
                color:#E8E8E8;
                font-size:14px;
                line-height:1.5;
            ">
                <strong>ℹ️ {t["important_information"]}</strong>
                <br>
                {t["room_charge_information"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    with info_col:

        with st.popover(
            t["information_booking"],
            use_container_width=True
        ):

            st.markdown(
                f"""
### {t["reservation"]}

**🧘🏻‍♀️ {SPA_SERVICE_NAME}**

**💶 {t["price"]}: {SPA_SERVICE_PRICE:.2f} {SPA_CURRENCY}**

{t["spa_instruction"]}

{t["reception_contact"]}

---

ℹ️ {t["room_charge_information"]}
"""
            )

            reservation_text = st.text_area(
                t["your_message"],
                placeholder=t["spa_placeholder"],
                key="massage_request_text",
                height=130
            )

            if st.button(
                t["send_request"],
                key="massage_request",
                type="primary",
                use_container_width=True
            ):

                if not reservation_text.strip():

                    st.warning(
                        t["empty_message"]
                    )

                else:

                    try:

                        request_id = create_spa_request(
                            room_number=room_number,
                            service_name=(
                                f"{SPA_SERVICE_NAME} - "
                                f"{SPA_SERVICE_PRICE:.2f} "
                                f"{SPA_CURRENCY}"
                            ),
                            guest_message=reservation_text
                        )

                        st.session_state.spa_success_service_name = (
                            SPA_SERVICE_NAME
                        )

                        st.session_state.spa_success_service_price = (
                            SPA_SERVICE_PRICE
                        )

                        st.session_state.spa_request_success = True

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"{t['request_error']}: {error}"
                        )
# =====================================
# БРАНДИРАНЕ
# =====================================

st.divider()

st.caption(
    t["footer"]
)
