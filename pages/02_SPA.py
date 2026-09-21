import streamlit as st

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

                st.success(
                    "Заявката е изпратена успешно."
                )

# =====================================
# БРАНДИРАНЕ
# =====================================

st.divider()

st.caption(
    "Powered by HMITSEVAPPS"
)
