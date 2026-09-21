import streamlit as st


TRANSLATIONS = {
    "bg": {
        # Навигация
        "back": "⬅ Назад",
        "language_bg": "🇧🇬 BG",
        "language_en": "🇬🇧 EN",
        "room": "Стая",
        "footer": "Powered by HMITSEVAPPS",

        # Начална страница
        "welcome": "Добре дошли",
        "hotel_services": "Хотелски услуги",
        "room_service": "РУМ СЪРВИЗ",
        "room_service_description": "Храна и напитки",
        "spa": "СПА",
        "spa_description": "Масажи и терапии",
        "activities": "Дейности",
        "activities_description": "Спорт и активности",
        "invalid_room": "Невалиден номер на стая.",

        # Общи действия
        "information_booking": "ℹ️ Информация и резервация",
        "reservation": "Резервация",
        "reservation_request": "Заявка за резервация",
        "your_message": "Вашето съобщение",
        "send_request": "✅ Изпрати заявка",
        "empty_message": "Моля, въведете съобщение.",
        "request_not_sent": "Заявката не беше изпратена.",
        "request_number": "Номер на заявката",
        "reception_contact": "Рецепцията ще се свърже с Вас.",
        "request_success": "Заявката е успешно изпратена до рецепцията.",

        # SPA
        "spa_page_title": "СПА",
        "relaxing_massage": "Релаксиращ масаж",
        "relaxing_massage_description": "Професионален масаж на цялото тяло.",
        "spa_instruction": "Моля, посочете деня и часа, за които желаете да направите резервация.",
        "spa_placeholder": "Пример: Искам масаж на 22.09.2026 г. в 16:00 ч.",
        "spa_success_service": "💆 Услуга: Релаксиращ масаж",
        "spa_success_contact": "🛎️ Рецепцията ще се свърже с Вас за потвърждение.",

        # Activities
        "activities_page_title": "Хотелски дейности",
        "ski_rental": "Наем на ски оборудване",
        "ski_description": "Резервирайте ски оборудване директно чрез хотела.",
        "activity_instruction": "Моля, посочете желания ден и добавете необходимата информация за резервацията.",
        "example_message": "Примерно съобщение:",
        "ski_example": "Желая да резервирам ски оборудване за 22.09.2026 г.",
        "activity_reception_message": "Рецепцията ще се свърже с Вас за уточняване и потвърждение на резервацията.",

        # Room Service
        "room_service_menu": "Меню Рум Сървиз",
        "breakfast": "Закуска",
        "main_courses": "Основни ястия",
        "desserts": "Десерти",
        "beverages": "Напитки",
        "english_breakfast": "Английска закуска",
        "english_breakfast_description": "Прясно приготвена закуска",
        "club_sandwich": "Клуб сандвич",
        "club_sandwich_description": "Сервира се с пържени картофи",
        "chocolate_souffle": "Шоколадово суфле",
        "chocolate_souffle_description": "Домашно приготвен десерт",
        "mineral_water": "Минерална вода",
        "mineral_water_description": "330 мл",
        "no_items": "В тази секция все още няма налични артикули.",
        "image_unavailable": "Снимката временно не е налична.",
        "alcohol_price_note": "🥃 Посочената цена е за 50 мл.",
        "no_description": "Няма описание.",
        "comment": "Коментар",
        "kitchen_comment": "Коментар към кухнята",
        "comment_placeholder": "Напишете коментар",
        "save_comment": "Запази коментар",
        "comment_saved": "Коментарът е запазен.",
        "added": "Добавено",
        "add": "Добави",
        "remove": "Премахни",
        "cart": "Вашата поръчка",
        "quantity": "Количество",
        "total": "Общо",
        "notes": "Бележка",
        "order_notes": "Бележка към поръчката",
        "clear_cart": "🗑️ Изчисти количката",
        "send_order": "✅ Изпрати поръчката",
        "empty_cart": "Поръчката е празна.",
        "no_selected_items": "Няма избрани артикули.",
        "order_success": "Поръчката е изпратена успешно до рецепцията.",
        "order_not_sent": "Поръчката не беше изпратена.",
        "order_number": "Номер на поръчката",
        "reception_sees_order": "Рецепцията вече вижда Вашата поръчка.",
        "room_service_banner_missing": "Банерът на Рум Сървиз не е намерен. Проверете името на снимката в папка assets.",
    },

    "en": {
        # Navigation
        "back": "⬅ Back",
        "language_bg": "🇧🇬 BG",
        "language_en": "🇬🇧 EN",
        "room": "Room",
        "footer": "Powered by HMITSEVAPPS",

        # Home page
        "welcome": "Welcome",
        "hotel_services": "Hotel Services",
        "room_service": "Room Service",
        "room_service_description": "Food and drinks",
        "spa": "SPA",
        "spa_description": "Massages and treatments",
        "activities": "Activities",
        "activities_description": "Sports and activities",
        "invalid_room": "Invalid room number.",

        # Common actions
        "information_booking": "ℹ️ Information and booking",
        "reservation": "Reservation",
        "reservation_request": "Reservation request",
        "your_message": "Your message",
        "send_request": "✅ Send request",
        "empty_message": "Please enter a message.",
        "request_not_sent": "The request was not sent.",
        "request_number": "Request number",
        "reception_contact": "Reception will contact you.",
        "request_success": "Your request has been successfully sent to reception.",

        # SPA
        "spa_page_title": "SPA",
        "relaxing_massage": "Relaxing massage",
        "relaxing_massage_description": "Professional full-body massage.",
        "spa_instruction": "Please specify the preferred date and time for the reservation.",
        "spa_placeholder": "Example: I would like a massage on September 22, 2026 at 4:00 PM.",
        "spa_success_service": "💆 Service: Relaxing massage",
        "spa_success_contact": "🛎️ Reception will contact you for confirmation.",

        # Activities
        "activities_page_title": "Hotel Activities",
        "ski_rental": "Ski equipment rental",
        "ski_description": "Reserve ski equipment directly through the hotel.",
        "activity_instruction": "Please enter the preferred date and add the necessary reservation details.",
        "example_message": "Example message:",
        "ski_example": "I would like to reserve ski equipment for September 22, 2026.",
        "activity_reception_message": "Reception will contact you to finalize and confirm the reservation.",

        # Room Service
        "room_service_menu": "Room Service Menu",
        "breakfast": "Breakfast",
        "main_courses": "Main Courses",
        "desserts": "Desserts",
        "beverages": "Beverages",
        "english_breakfast": "English Breakfast",
        "english_breakfast_description": "Freshly prepared breakfast",
        "club_sandwich": "Club Sandwich",
        "club_sandwich_description": "Served with fries",
        "chocolate_souffle": "Chocolate Soufflé",
        "chocolate_souffle_description": "Homemade dessert",
        "mineral_water": "Mineral Water",
        "mineral_water_description": "330 ml",
        "no_items": "There are no available items in this section yet.",
        "image_unavailable": "The image is temporarily unavailable.",
        "alcohol_price_note": "🥃 The listed price is for 50 ml.",
        "no_description": "No description is available.",
        "comment": "Comment",
        "kitchen_comment": "Kitchen comment",
        "comment_placeholder": "Write a comment",
        "save_comment": "Save comment",
        "comment_saved": "The comment has been saved.",
        "added": "Added",
        "add": "Add",
        "remove": "Remove",
        "cart": "Your order",
        "quantity": "Quantity",
        "total": "Total",
        "notes": "Note",
        "order_notes": "Order notes",
        "clear_cart": "🗑️ Clear cart",
        "send_order": "✅ Send order",
        "empty_cart": "Your order is empty.",
        "no_selected_items": "No items have been selected.",
        "order_success": "Your order has been successfully sent to reception.",
        "order_not_sent": "The order was not sent.",
        "order_number": "Order number",
        "reception_sees_order": "Reception can now see your order.",
        "room_service_banner_missing": "The Room Service banner was not found. Please check the image name in the assets folder.",
    },
}


def get_language():
    return st.session_state.get("lang", "bg")


def get_translations():
    language = st.session_state.get("lang", "bg")

    if language not in TRANSLATIONS:
        language = "bg"
        st.session_state.lang = "bg"

    return TRANSLATIONS[language]
