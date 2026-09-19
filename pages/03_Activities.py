
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
    page_title="Activities",
    page_icon="🎿",
    layout="wide"
)

# =====================================
# БАНЕР
# =====================================

try:
    st.image(
        "assets/activities_banner.png",
        use_container_width=True
    )
except:
    pass

# =====================================
# ЗАГЛАВИЕ
# =====================================

st.title("🎿 Hotel Activities")

st.markdown("---")

# =====================================
# АКТИВНОСТ
# =====================================

st.subheader("🎿 Ski Equipment Rental")

st.write(
    """
    Reserve ski equipment directly through the hotel.
    """
)

with st.popover("ℹ️ Information & Reservation"):

    st.markdown(
        """
### Reservation Request

Please enter your preferred date and additional details.

Example:

I would like to reserve ski equipment for 22.09.2026.

Reception will contact you to confirm your reservation.
"""
    )

    reservation_text = st.text_area(
        "Your message",
        placeholder="I would like to reserve ski equipment for 22.09.2026."
    )

    if st.button(
        "✅ Send Request",
        key="ski_request"
    ):
        st.success(
            "Your request has been sent successfully."
        )

st.markdown("---")

# =====================================
# БЪЛГАРСКА ВЕРСИЯ
# =====================================

st.subheader("🎿 Наем на ски оборудване")

st.write(
    """
    Резервирайте ски оборудване директно чрез хотела.
    """
)

with st.popover("ℹ️ Информация и резервация"):

    st.markdown(
        """
### Резервация

Моля напишете за кой ден желаете резервация.

Пример:

Желая да резервирам ски оборудване за 22.09.2026.

От рецепция ще се свържат с Вас за потвърждение.
"""
    )

    reservation_text_bg = st.text_area(
        "Вашето съобщение",
        placeholder="Желая да резервирам ски оборудване за 22.09.2026.",
        key="ski_bg"
    )

    if st.button(
        "✅ Изпрати заявка",
        key="ski_bg_request"
    ):
        st.success(
            "Заявката е изпратена успешно."
        )

st.markdown("---")

st.caption(
    "FlowSuite Hotel Activities Demo"
)
