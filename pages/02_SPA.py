import streamlit as st
from database.db import get_connection
if "spa_request_success" not in st.session_state:
    st.session_state.spa_request_success = False

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
    page_icon="💆",
    layout="wide"
)

# =====================================
# НАВИГАЦИЯ
# =====================================

nav_col1, nav_col2 = st.columns([1, 5])

with nav_col1:
    if st.button(
        "⬅ Back",
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
# УСПЕШНО ИЗПРАТЕНА ЗАЯВКА
# =====================================

if st.session_state.spa_request_success:

    st.success(
        """
✅ Заявката е изпратена успешно до рецепция.

💆 Услуга: Relaxing Massage

🛎️ От рецепция ще се свържат с Вас за потвърждение.
        """
    )

    st.session_state.spa_request_success = False
# =====================================
# SPA КАРТА
# =====================================

with st.container(border=True):

    activity_col, info_col = st.columns(
        [5.5, 2.5],
        vertical_alignment="center"
    )

    with activity_col:

        st.subheader(
            "💆 Relaxing Massage"
        )

        st.write(
            "Professional full body massage."
        )

    with info_col:

        with st.popover(
            "ℹ️ Информация и резервация",
            use_container_width=True
        ):

            st.markdown(
                """
                ### Резервация

                Моля напишете за кой ден и час желаете резервация.

                От рецепция ще се свържат с Вас.
                """
            )

            reservation_text = st.text_area(
                "Вашето съобщение",
                placeholder=(
                    "Пример: Желая масаж на "
                    "22.09.2026 от 16:00 часа."
                ),
                key="massage_request_text",
                height=130
            )

            if st.button(
                "✅ Изпрати заявка",
                key="massage_request",
                type="primary",
                use_container_width=True
            ):

                if not reservation_text.strip():

                    st.warning(
                        "Моля, въведете съобщение."
                    )

                else:

                    try:

                        request_id = create_spa_request(
                            room_number=room_number,
                            service_name="Relaxing Massage",
                            guest_message=reservation_text
                        )


                        st.session_state.spa_request_success = True
                        st.rerun()

                    except Exception as error:

                        st.session_state.activity_request_error = str(error)

                        st.rerun()
# =====================================
# БРАНДИРАНЕ
# =====================================

st.divider()

st.caption(
    "Powered by HMITSEVAPPS"
)
