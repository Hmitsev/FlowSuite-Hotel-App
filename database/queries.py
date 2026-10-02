import streamlit as st

from database.db import get_connection
from psycopg2 import Binary

# =====================================
# КАТЕГОРИИ
# =====================================

@st.cache_data(ttl=3600)

def get_categories():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT DISTINCT
                category_name,
                sort_order
            FROM menu_categories
            ORDER BY sort_order, category_name
            """
        )

        return cur.fetchall()

    finally:
        cur.close()
        conn.close()


# =====================================
# АРТИКУЛИ ПО КАТЕГОРИЯ
# =====================================

@st.cache_data(ttl=1)
def get_items_by_category(category_name):

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT DISTINCT ON (mi.sort_order, mi.item_name)
                mi.id,
                mi.item_name,
                mi.price,
                COALESCE(mi.description, ''),
                COALESCE(mi.drink_group, ''),
                COALESCE(mi.wine_type, ''),
                COALESCE(mi.alcohol_type, ''),
                COALESCE(mi.daily_group, '')
            FROM menu_items mi
            JOIN menu_categories mc
                ON mc.id = mi.category_id
            WHERE mc.category_name = %s
              AND mi.is_active = TRUE
              AND (
                    mc.category_name <> 'Дневно меню'
                    OR COALESCE(mi.available_today, FALSE) = TRUE
              )
            ORDER BY
                mi.sort_order,
                mi.item_name,
                mi.id
            """,
            (category_name,)
        )

        return cur.fetchall()

    finally:

        cur.close()
        conn.close()
# =====================================
# СЪЗДАВАНЕ НА ПОРЪЧКА
# =====================================

def create_order(table_number, cart):
    if not cart:
        raise ValueError("Количката е празна.")

    try:
        table_number = int(table_number)
    except (TypeError, ValueError) as error:
        raise ValueError("Невалиден номер на маса.") from error

    if table_number < 1 or table_number > 20:
        raise ValueError(
            "Номерът на масата трябва да бъде между 1 и 20."
        )

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Намираме вътрешното ID на масата
        cur.execute(
            """
            SELECT id
            FROM restaurant_tables
            WHERE table_number = %s
              AND is_active = TRUE
            LIMIT 1
            """,
            (table_number,)
        )

        table_result = cur.fetchone()

        if table_result is None:
            raise ValueError(
                f"Маса № {table_number} не е намерена или не е активна."
            )

        table_id = table_result[0]

        # Групиране по артикул и коментар
        # Еднакви ястия с различни коментари остават отделни позиции
        grouped_items = {}

        for cart_item in cart:
            item_id = int(cart_item["id"])
            item_name = str(cart_item["name"])
            price = float(cart_item["price"])
            note = str(cart_item.get("note", "")).strip()

            group_key = (item_id, note)

            if group_key not in grouped_items:
                grouped_items[group_key] = {
                    "id": item_id,
                    "name": item_name,
                    "price": price,
                    "note": note,
                    "quantity": 0
                }

            grouped_items[group_key]["quantity"] += 1

        total_amount = sum(
            grouped_item["price"] * grouped_item["quantity"]
            for grouped_item in grouped_items.values()
        )

        # Създаваме основната поръчка
        cur.execute(
            """
            INSERT INTO orders
            (
                table_id,
                total_amount,
                order_status
            )
            VALUES
            (
                %s,
                %s,
                'NEW'
            )
            RETURNING id
            """,
            (
                table_id,
                total_amount
            )
        )

        order_id = cur.fetchone()[0]

        # Записваме отделните позиции
        for grouped_item in grouped_items.values():
            cur.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    item_id,
                    quantity,
                    notes,
                    kitchen_status,
                    bar_status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    'NEW',
                    'NEW'
                )
                """,
                (
                    order_id,
                    grouped_item["id"],
                    grouped_item["quantity"],
                    (
                        grouped_item["note"]
                        if grouped_item["note"]
                        else None
                    )
                )
            )

        # Известие за новата поръчка
        cur.execute(
            """
            INSERT INTO notifications
            (
                table_id,
                notification_type,
                message,
                is_read
            )
            VALUES
            (
                %s,
                'NEW_ORDER',
                %s,
                FALSE
            )
            """,
            (
                table_id,
                (
                    f"Нова поръчка №{order_id} "
                    f"от маса №{table_number}"
                )
            )
        )

        conn.commit()

        return order_id

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()
# =====================================
# ФИНАЛИЗИРАНИ ПОРЪЧКИ (24 ЧАСА)
# =====================================

def get_completed_orders():

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
                o.id,
                t.table_number,
                o.created_at,
                o.order_status,
                o.total_amount,
                NULL,
                'Финализирана поръчка',
                0,
                NULL,
                NULL,
                'COMPLETED'
            FROM orders o
            JOIN restaurant_tables t
                ON t.id = o.table_id
            WHERE o.order_status = 'COMPLETED'
              AND o.created_at >=
                  NOW() - INTERVAL '24 HOURS'
            ORDER BY o.created_at DESC
            """
        )

        return cur.fetchall()

    finally:

        cur.close()
        conn.close()
        # =====================================
# СЪЗДАВАНЕ НА ROOM SERVICE ПОРЪЧКА
# =====================================

def create_room_service_order(room_number, cart):
    if not cart:
        raise ValueError("Количката е празна.")

    try:
        room_number = int(room_number)
    except (TypeError, ValueError) as error:
        raise ValueError(
            "Невалиден номер на стая."
        ) from error

    conn = get_connection()
    cur = conn.cursor()

    try:
        # =====================================
        # НАМИРАНЕ НА СТАЯТА
        # =====================================

        cur.execute(
            """
            SELECT id
            FROM hotel_rooms
            WHERE room_number = %s
              AND is_active = TRUE
            LIMIT 1
            """,
            (room_number,)
        )

        room_result = cur.fetchone()

        if room_result is None:
            raise ValueError(
                f"Стая №{room_number} не е намерена "
                "или не е активна."
            )

        room_id = room_result[0]

        # =====================================
        # ГРУПИРАНЕ НА АРТИКУЛИТЕ
        # =====================================

        grouped_items = {}

        for cart_item in cart:
            item_id = int(cart_item["id"])
            item_name = str(cart_item["name"])
            price = float(cart_item["price"])
            note = str(
                cart_item.get("note", "")
            ).strip()

            group_key = (
                item_id,
                item_name,
                note
            )

            if group_key not in grouped_items:
                grouped_items[group_key] = {
                    "id": item_id,
                    "name": item_name,
                    "price": price,
                    "note": note,
                    "quantity": 0
                }

            grouped_items[group_key]["quantity"] += 1

        # =====================================
        # ИЗЧИСЛЯВАНЕ НА ОБЩАТА СУМА
        # =====================================

        total_amount = sum(
            item["price"] * item["quantity"]
            for item in grouped_items.values()
        )

        # =====================================
        # СЪЗДАВАНЕ НА ПОРЪЧКАТА
        # =====================================

        cur.execute(
            """
            INSERT INTO room_service_orders
            (
                room_id,
                total_amount,
                order_status
            )
            VALUES
            (
                %s,
                %s,
                'NEW'
            )
            RETURNING id
            """,
            (
                room_id,
                total_amount
            )
        )

        order_id = cur.fetchone()[0]

        # =====================================
        # ЗАПИСВАНЕ НА АРТИКУЛИТЕ
        # =====================================

        for item in grouped_items.values():
            cur.execute(
                """
                INSERT INTO room_service_order_items
                (
                    order_id,
                    item_id,
                    item_name,
                    quantity,
                    unit_price,
                    notes,
                    item_status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    'NEW'
                )
                """,
                (
                    order_id,
                    item["id"],
                    item["name"],
                    item["quantity"],
                    item["price"],
                    item["note"]
                    if item["note"]
                    else None
                )
            )

        conn.commit()

        return order_id

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()
# =========================================================
# СЪЗДАВАНЕ НА ЗАЯВКА КЪМ ОБСЛУЖВАЩ ПЕРСОНАЛ
# =========================================================
def create_service_request(
    room_number,
    department,
    category,
    request_type,
    guest_message="",
    guest_image=None,
    guest_image_name=None,
    guest_image_type=None,
    priority="NORMAL"
):
    room_number = int(room_number)

    department = str(
        department or ""
    ).strip().upper()

    category = str(
        category or ""
    ).strip().upper()

    request_type = str(
        request_type or ""
    ).strip()

    guest_message = str(
        guest_message or ""
    ).strip()

    priority = str(
        priority or "NORMAL"
    ).strip().upper()

    allowed_departments = {
        "MAINTENANCE",
        "HOUSEKEEPING"
    }

    allowed_priorities = {
        "LOW",
        "NORMAL",
        "HIGH",
        "URGENT"
    }

    if department not in allowed_departments:
        raise ValueError(
            "Невалиден отдел за обслужване."
        )

    if not category:
        raise ValueError(
            "Не е избрана категория."
        )

    if not request_type:
        raise ValueError(
            "Не е избран вид на сигнала."
        )

    if priority not in allowed_priorities:
        priority = "NORMAL"

    image_binary = None

    if guest_image:
        if isinstance(
            guest_image,
            (
                bytes,
                bytearray,
                memoryview
            )
        ):
            image_binary = Binary(
                bytes(guest_image)
            )
        else:
            raise ValueError(
                "Невалиден формат на снимката."
            )

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Намираме вътрешното ID на хотелската стая.
        cur.execute(
            """
            SELECT id
            FROM hotel_rooms
            WHERE room_number = %s
            LIMIT 1
            """,
            (
                room_number,
            )
        )

        room_row = cur.fetchone()

        if room_row is None:
            raise ValueError(
                f"Стая №{room_number} не е намерена "
                "или не е активна."
            )

        room_id = room_row[0]

        # Създаваме новата заявка.
        cur.execute(
            """
            INSERT INTO service_requests (
                room_id,
                department,
                category,
                request_type,
                guest_message,
                guest_image,
                guest_image_name,
                guest_image_type,
                priority,
                request_status,
                created_at,
                updated_at
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'NEW',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            RETURNING id
            """,
            (
                room_id,
                department,
                category,
                request_type,
                guest_message,
                image_binary,
                (
                    str(guest_image_name).strip()
                    if guest_image_name
                    else None
                ),
                (
                    str(guest_image_type).strip()
                    if guest_image_type
                    else None
                ),
                priority
            )
        )

        created_request = cur.fetchone()

        if created_request is None:
            raise RuntimeError(
                "Заявката не беше създадена."
            )

        request_id = created_request[0]

        conn.commit()

        return request_id

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()
