
from pathlib import Path

import streamlit as st

from database.queries import create_room_service_order
from translations import get_translations


# =====================================
# НАСТРОЙКИ НА СТРАНИЦАТА
# =====================================

st.set_page_config(
    page_title="Room Service",
    page_icon="🍽️",
    layout="wide"
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

if "cart" not in st.session_state:
    st.session_state.cart = []

if "last_order_id" not in st.session_state:
    st.session_state.last_order_id = None

if "room_service_sent" not in st.session_state:
    st.session_state.room_service_sent = False

if "room_service_error" not in st.session_state:
    st.session_state.room_service_error = None
``


# =====================================
# ФУНКЦИИ ЗА КОЛИЧКАТА
# =====================================

def add_to_cart(
    item_id,
    item_name,
    price,
    note=""
):
    st.session_state.cart.append(
        {
            "id": int(item_id),
            "name": str(item_name),
            "price": float(price),
            "note": str(note).strip()
        }
    )


def remove_one_from_cart(
    item_id,
    note=""
):
    note = str(note).strip()

    for index, cart_item in enumerate(
        st.session_state.cart
    ):
        same_item = (
            int(cart_item["id"]) == int(item_id)
        )

        same_note = (
            str(
                cart_item.get(
                    "note",
                    ""
                )
            ).strip()
            == note
        )

        if same_item and same_note:
            st.session_state.cart.pop(index)
            break

# =====================================
# НАВИГАЦИЯ
# =====================================

nav_col1, nav_col2 = st.columns([1, 5])

with nav_col1:
    if st.button(
        t["back"],
        key="room_service_back",
        use_container_width=True
    ):
        st.switch_page("app.py")




# =====================================
# БАНЕР НА ROOM SERVICE
# =====================================

ROOM_SERVICE_BANNER_CANDIDATES = [
    "room_service_banner.png",
    "Screenshot 2026-09-09 025759.png",
    "room_service.png",
    "Room Service.png",
    "room_service_banner.jpg",
    "room_service_banner.jpeg",
]

room_service_banner_path = None

for banner_name in ROOM_SERVICE_BANNER_CANDIDATES:
    candidate_path = Path("assets") / banner_name

    if candidate_path.exists():
        room_service_banner_path = candidate_path
        break


if room_service_banner_path:
    st.image(
        str(room_service_banner_path),
        use_container_width=True
    )
else:
    st.warning(
        "Room Service банерът не е намерен. "
        "Провери точното име на снимката в папка assets."
    )


# =====================================
# НОМЕР НА СТАЯТА ОТ QR КОДА
# =====================================

raw_room_number = st.query_params.get("room", "204")

try:
    room_number = int(raw_room_number)
except (TypeError, ValueError):
    room_number = 204

if room_number < 1 or room_number > 9999:
    st.error("Невалиден QR код за стая.")
    st.stop()


# =====================================
# КАРТА С НОМЕРА НА СТАЯТА
# =====================================

st.markdown(
    f"""
    <div style="
        border:1px solid #D4AF37;
        border-radius:14px;
        padding:14px 18px;
        margin-top:14px;
        margin-bottom:18px;
        text-align:center;
        color:#F5E6C8;
        background:linear-gradient(
            135deg,
            rgba(15,23,42,0.96),
            rgba(8,14,25,0.96)
        );
        font-size:22px;
        font-weight:800;
        box-shadow:0 0 12px rgba(212,175,55,0.18);
    ">
        🛎️ Room {room_number}
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================
# ЗАГЛАВИЕ НА МЕНЮТО
# =====================================

st.markdown(
    """
    <div style="
        color:#F5E6C8;
        font-size:28px;
        font-weight:800;
        margin-top:28px;
        margin-bottom:18px;
        padding-bottom:10px;
        border-bottom:1px solid rgba(212,175,55,0.40);
    ">
        t["room_service_menu"]
    </div>
    """,
    unsafe_allow_html=True
)
categories = [
    ("Breakfast",),
    ("Main Course",),
    ("Desserts",),
    ("Drinks",)
]

category_display = {
    "Breakfast": f"🍳 {t['breakfast']}",
    "Main Courses": f"🍽️ {t['main_courses']}",
    "Desserts": f"🍰 {t['desserts']}",
    "Beverages": f"🥤 {t['beverages']}"
}

category_grams = {}

category_banners = {}

reverse_display = {
    value: key
    for key, value in category_display.items()
}

category_names = [
    category_display.get(
        category[0],
        category[0]
    )
    for category in categories
]

selected_display = st.segmented_control(
    "",
    category_names,
    default=category_names[0],
    key="main_category_selector"
)

selected_category = reverse_display.get(
    selected_display,
    selected_display
)

demo_items = {
    "Breakfast": [
        (
            1,
            "English Breakfast",
            18,
            "Fresh breakfast"
        )
    ],
    "Main Course": [
        (
            2,
            "Club Sandwich",
            24,
            "Served with fries"
        )
    ],
    "Desserts": [
        (
            3,
            "Chocolate Soufflé",
            12,
            "Homemade dessert"
        )
    ],
    "Drinks": [
        (
            4,
            "Mineral Water",
            4,
            "330 ml"
        )
    ]
}

items = demo_items.get(
    selected_category,
    []
)

# =====================================
# СНИМКИ НА ROOM SERVICE АРТИКУЛИТЕ
# =====================================

burger_images = {}

# =====================================
# ПОКАЗВАНЕ НА АРТИКУЛИТЕ
# =====================================

if not items:

    st.info(
        "В тази секция все още няма налични артикули."
    )

else:

    for item_index, item in enumerate(items):

        item_id = item[0]
        item_name = item[1]
        price = float(item[2])
        description = item[3] if len(item) > 3 else ""
        item_drink_group = item[4] if len(item) > 4 else ""
        item_wine_type = item[5] if len(item) > 5 else ""
        item_alcohol_type = item[6] if len(item) > 6 else ""

        col1, col2, col3, col4 = st.columns(
            [6, 0.7, 1.3, 1.7]
        )

        # =====================================
        # ИМЕ НА АРТИКУЛА
        # =====================================

        with col1:

            st.markdown(
                f"""
                <div style="
                    background-color:#0F172A;
                    border:1px solid #24324A;
                    border-radius:12px;
                    padding:12px 14px;
                    color:#F5E6C8;
                    font-weight:700;
                    font-size:18px;
                    min-height:52px;
                    display:flex;
                    align-items:center;
                ">
                    {item_name}
                </div>
                """,
                unsafe_allow_html=True
            )
            drink_variants = {

                "Кока-Кола 250ml": [
                    "Coca-Cola",
                    "Coca-Cola Zero"
                ],

                "Фанта 250ml": [
                    "Портокал",
                    "Лимон",
                    "Екзотик"
                ],

                "Натурален сок Cappy": [
                    "Праскова",
                    "Портокал",
                    "Ябълка",
                    "Мултивитамин"
                ],

                "Студен чай Fuzetea": [
                    "Праскова",
                    "Лимон",
                    "Зелен чай"
                ],

                "Schweppes Сода": [
                    "Сода",
                    "Тоник",
                    "Bitter Lemon"
                ]
            }

            selected_variant = ""

            if item_name in drink_variants:
                
                variant_col, _ = st.columns([2, 8])

                with variant_col:
                
                    selected_variant = st.selectbox(
                        "",
                        drink_variants[item_name],
                        key=f"variant_{item_id}_{item_index}"
                    )

        # =====================================
        # ИНФОРМАЦИЯ И КОМЕНТАР
        # =====================================
        
        with col2:
        
            with st.popover("ℹ️"):
        
                st.markdown(
                    f"""
                    <div style="
                        color:#F5E6C8;
                        font-size:28px;
                        font-weight:800;
                        text-align:center;
                        margin-bottom:10px;
                    ">
                        {item_name}
                    </div>
                    """,
                    unsafe_allow_html=True
            )
    
                drink_images = {
                    "Кока-Кола 250ml": "assets/kola.png",
                    "Спрайт 250ml": "assets/sprite.png",
                    "Фанта 250ml": "assets/fanta port.png",
                    "Минерална вода Банкя 330ml": "assets/bankq.png",
                
                    "Натурален сок Cappy": "assets/kapu praskova.png",
                    "Студен чай Fuzetea": "assets/stud.chai.png",
                    "Red Bull": "assets/red bul.png",
                    "Фреш 200ml": "assets/фреш.png",
                
                    "Капучино": "assets/kapochino.png",
                    "Бяло фрапе": "assets/фон топла напитка.png",
                    "Бяло фрапе с вкус": "assets/фон топла напитка.png",
                    "Черно фрапе": "assets/фон топла напитка.png",
                
                    "Beluga": "assets/beluga.png",
                    "Руски стандарт": "assets/ruski stand.png",
                    "Бургас 63": "assets/burgas 63.png",
                
                    "Bushmills": "assets/bushmils.png",
                    "Bushmills Black": "assets/bushmils black.png",
                    "Jack Daniels": "assets/jack.png",
                    "Jameson": "assets/jameson.png",
                    "Jameson Black Barrel": "assets/jameson.png"
                }
    
                image_path = burger_images.get(item_name)
    
                if not image_path:
                    image_path = drink_images.get(item_name)

                if image_path:
        
                    try:
                        st.image(
                            image_path,
                            use_container_width=True
                        )
        
                    except Exception:
                        st.caption(
                            "Снимката временно не е налична."
                        )
        
                if item_drink_group == "🥃 Алкохол":
        
                    st.markdown(
                        """
                        <div style="
                            background:#1F2937;
                            color:#FFD54F;
                            border:1px solid #D4AF37;
                            border-radius:10px;
                            padding:10px;
                            text-align:center;
                            font-weight:700;
                            margin-bottom:10px;
                        ">
                            🥃 Посочената цена е за 50 мл.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
                if description:
        
                    st.write(
                        description
                    )
        
                else:
        
                    st.info(
                        "Няма описание."
                    )
        
                comment_label = "Коментар"
        
                if selected_category not in (
                    "Напитки",
                ):
                    comment_label = "Коментар към кухнята"
        
                comment = st.text_area(
                    comment_label,
                    placeholder=" коментар",
                    key=f"comment_{item_id}_{item_index}",
                    height=80
                )
        
                if st.button(
                    "Запази коментар",
                    key=f"save_{item_id}_{item_index}"
                ):
        
                    st.session_state[
                        f"saved_note_{item_id}_{item_index}"
                    ] = comment
        
                    st.success(
                        "Коментарът е запазен."
                    )
        # =====================================
        # ЦЕНА
        # =====================================

        with col3:

            st.markdown(
                f"""
                <div style="
                    color:#FFD54F;
                    font-weight:700;
                    font-size:18px;
                    padding-left:15px;
                ">
                    € {price:.2f}
                </div>
                """,
                unsafe_allow_html=True
            )

        # =====================================
        # ДОБАВЯНЕ В КОЛИЧКАТА
        # =====================================
        

        with col4:

            item_is_in_cart = any(
                cart_item["id"] == item_id
                for cart_item in st.session_state.cart
            )

            if item_is_in_cart:

                st.markdown(
                    """
                    <div style="
                        background:#198754;
                        color:white;
                        border-radius:8px;
                        padding:4px 8px;
                        text-align:center;
                        font-size:12px;
                        font-weight:700;
                        margin-bottom:4px;
                    ">
                        ✅ Добавено
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if st.button(
                "🛒 Добави",
                key=f"add_{item_id}_{item_index}"
            ):

                saved_comment = st.session_state.get(
                    f"saved_note_{item_id}_{item_index}",
                    ""
                )

                final_name = item_name

                if item_name in drink_variants and selected_variant:
                    final_name = (
                        f"{item_name} - {selected_variant}"
                    )

                add_to_cart(
                    item_id=item_id,
                    item_name=final_name,
                    price=price,
                    note=saved_comment
                )

                st.rerun()
# =====================================
# КОЛИЧКА
# =====================================

st.divider()

st.subheader("🛒 Вашата поръчка")


if st.session_state.room_service_error:
    st.error(
        "Поръчката не беше изпратена.\n\n"
        f"Причина: {st.session_state.room_service_error}"
    )

    st.session_state.room_service_error = None


if st.session_state.last_order_id is not None:
    st.success(
        f"✅ Room Service поръчката е изпратена успешно!\n\n"
        f"🧾 Номер на поръчката: "
        f"{st.session_state.last_order_id}\n\n"
        f"🛎️ Стая № {room_number}\n\n"
        "Рецепцията вече вижда Вашата поръчка."
    )

    st.session_state.last_order_id = None


if not st.session_state.cart:
    st.info(
        "Няма избрани артикули."
    )

else:
    grouped = {}

    for item in st.session_state.cart:
        group_key = (
            item["id"],
            item.get("note", "")
        )

        if group_key not in grouped:
            grouped[group_key] = {
                "id": item["id"],
                "name": item["name"],
                "price": item["price"],
                "note": item.get("note", ""),
                "qty": 0
            }

        grouped[group_key]["qty"] += 1

    total = 0

    for data in grouped.values():
        qty = data["qty"]
        row_total = qty * data["price"]

        c1, c2, c3, c4, c5 = st.columns(
            [5, 1, 1, 1, 1]
        )

        with c1:
            st.write(
                data["name"]
            )

            if data["note"]:
                st.caption(
                    f"📝 {data['note']}"
                )

        with c2:
            if st.button(
                "➖",
                key=(
                    f"minus_{data['id']}_"
                    f"{data['note']}"
                )
            ):
                remove_one_from_cart(
                    data["id"],
                    data["note"]
                )

                st.rerun()

        with c3:
            st.write(
                f"x{qty}"
            )

        with c4:
            if st.button(
                "➕",
                key=(
                    f"plus_{data['id']}_"
                    f"{data['note']}"
                )
            ):
                add_to_cart(
                    item_id=data["id"],
                    item_name=data["name"],
                    price=data["price"],
                    note=data["note"]
                )

                st.rerun()

        with c5:
            st.write(
                f"€ {row_total:.2f}"
            )

        total += row_total

    st.success(
        f"Общо: € {total:.2f}"
    )

    # =====================================
    # ФИНАЛНИ БУТОНИ
    # =====================================

    clear_col, send_col = st.columns(2)

    with clear_col:
        if st.button(
            "🗑️ Изчисти количката",
            key="clear_room_service_cart",
            use_container_width=True
        ):
            st.session_state.cart = []
            st.rerun()

    with send_col:
        if st.button(
            "✅ Изпрати поръчка",
            key="send_room_service_order",
            type="primary",
            use_container_width=True
        ):
            try:
                order_id = create_room_service_order(
                    room_number=room_number,
                    cart=st.session_state.cart
                )

                st.session_state.cart = []
                st.session_state.last_order_id = order_id
                st.session_state.room_service_error = None

                st.rerun()

            except Exception as error:
                st.session_state.room_service_error = str(
                    error
                )

                st.rerun()


# =====================================
# БРАНДИРАНЕ
# =====================================

st.divider()

st.caption(
    "Powered by HMITSEVAPPS"
)
