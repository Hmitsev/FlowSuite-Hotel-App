
import streamlit as st
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
st.set_page_config(
    page_title="SPA",
    page_icon="💆",
    layout="wide"
)

try:
    st.image(
        "assets/spa_banner.png",
        use_container_width=True
    )
except:
    pass

st.title("💆 SPA & Wellness")

st.markdown("---")

st.subheader("💆 Relaxing Massage")

st.write(
    "Professional full body massage."
)

with st.popover("ℹ️ Информация и резервация"):

    st.markdown("""
### Резервация

Моля напишете за кой ден и час желаете резервация.

От рецепция ще се свържат с Вас.
""")

    reservation_text = st.text_area(
        "Вашето съобщение",
        placeholder="Пример: Желая масаж на 22.09.2026 от 16:00 часа."
    )

    if st.button(
        "✅ Изпрати заявка",
        key="massage_request"
    ):
        st.success(
            "Заявката е изпратена успешно."
        )

st.markdown("---")

st.caption(
    "Hotel SPA Reservation Demo"
)
