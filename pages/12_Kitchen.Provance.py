import io
from datetime import datetime
import pandas as pd
import streamlit as st
from lastoria.database.db import get_connection

st.set_page_config(page_title="Provence Kitchen & Admin", page_icon="👨‍🍳", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>[data-testid='stSidebar'],[data-testid='collapsedControl']{display:none!important}.stApp{background:#0b0f14;color:#f4ead4}h1,h2,h3{color:#d8b76a!important}[data-testid='stMetricValue']{color:#e8c978!important}</style>""", unsafe_allow_html=True)
PASSWORD = "provence2026"
if not st.session_state.get("provence_kitchen_auth"):
    st.title("👨‍🍳 Restaurant Provence")
    password=st.text_input("Парола за кухня/админ",type="password")
    if st.button("Вход",type="primary"):
        if password==PASSWORD: st.session_state.provence_kitchen_auth=True; st.rerun()
        else: st.error("Невалидна парола.")
    st.stop()

def db(query, params=(), fetch=True):
    conn=get_connection(); cur=conn.cursor()
    try:
        cur.execute(query,params)
        result=cur.fetchall() if fetch else None
        conn.commit(); return result
    except Exception:
        conn.rollback(); raise
    finally: cur.close(); conn.close()

def ensure_schema():
    for q in [
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS order_source VARCHAR(40)",
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS customer_name VARCHAR(160)",
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS customer_phone VARCHAR(40)",
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivery_address TEXT",
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS courier_status VARCHAR(30) DEFAULT 'WAITING_KITCHEN'",
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS courier_seen_at TIMESTAMP",
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS courier_picked_at TIMESTAMP",
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP"]:
        db(q,fetch=False)
ensure_schema()

def set_order_status(order_id,status):
    if status=="IN_PROGRESS":
        db("UPDATE order_items SET kitchen_status='PREPARING' WHERE order_id=%s AND kitchen_status='NEW'",(order_id,),False)
        db("UPDATE orders SET order_status='IN_PROGRESS',updated_at=CURRENT_TIMESTAMP WHERE id=%s",(order_id,),False)
    elif status=="READY":
        db("UPDATE order_items SET kitchen_status='READY' WHERE order_id=%s AND kitchen_status IN ('NEW','PREPARING')",(order_id,),False)
        db("UPDATE orders SET order_status='READY',courier_status='READY_FOR_PICKUP',updated_at=CURRENT_TIMESTAMP WHERE id=%s",(order_id,),False)

def active_orders():
    return db("""SELECT o.id,o.created_at,o.order_status,COALESCE(o.total_amount,0),o.customer_name,o.customer_phone,o.delivery_address,
        oi.id,mi.item_name,oi.quantity,COALESCE(oi.notes,''),oi.kitchen_status
        FROM orders o JOIN order_items oi ON oi.order_id=o.id JOIN menu_items mi ON mi.id=oi.item_id
        WHERE o.order_source='PROVANCE_TAKEAWAY' AND o.order_status NOT IN ('COMPLETED','DELIVERED')
        ORDER BY o.created_at,o.id,oi.id""")

def archive_rows(date_from,date_to):
    return db("""SELECT o.id,o.created_at,o.updated_at,o.delivered_at,o.order_status,o.courier_status,
        o.customer_name,o.customer_phone,o.delivery_address,COALESCE(o.total_amount,0),mi.item_name,oi.quantity,COALESCE(oi.notes,'')
        FROM orders o JOIN order_items oi ON oi.order_id=o.id JOIN menu_items mi ON mi.id=oi.item_id
        WHERE o.order_source='PROVANCE_TAKEAWAY' AND DATE(o.created_at) BETWEEN %s AND %s
        ORDER BY o.created_at DESC,o.id,oi.id""",(date_from,date_to))

def daily_catalog():
    return db("""SELECT id,item_name,price,COALESCE(daily_group,''),COALESCE(available_today,FALSE)
        FROM menu_items WHERE is_daily_item=TRUE AND is_active=TRUE ORDER BY daily_group,item_name""")

def save_daily(ids):
    db("UPDATE menu_items SET available_today=FALSE WHERE is_daily_item=TRUE",fetch=False)
    if ids: db("UPDATE menu_items SET available_today=TRUE WHERE id=ANY(%s) AND is_daily_item=TRUE",(list(ids),),False)

def add_daily(name,price,group):
    cats=db("SELECT id FROM menu_categories WHERE category_name='Дневно меню' LIMIT 1")
    if not cats: raise ValueError("Липсва категория Дневно меню.")
    db("""INSERT INTO menu_items(category_id,item_name,price,description,department,daily_group,is_daily_item,available_today,is_active)
        VALUES(%s,%s,%s,'','kitchen',%s,TRUE,TRUE,TRUE)""",(cats[0][0],name.strip(),price,group),False)

st.title("👨‍🍳 Provence Kitchen & Admin")
tab_orders,tab_daily,tab_admin=st.tabs(["🔥 Активни поръчки","📅 Дневно меню","📊 Админ и архив"])
with tab_orders:
    @st.fragment(run_every="20s")
    def live_orders():
        rows=active_orders(); orders={}
        for r in rows:
            orders.setdefault(r[0],{"created":r[1],"status":r[2],"total":float(r[3]),"name":r[4],"phone":r[5],"address":r[6],"items":[]})["items"].append(r[7:])
        st.info(f"Активни заявки: {len(orders)}")
        if not orders: st.success("Няма активни заявки.")
        for oid,o in orders.items():
            with st.container(border=True):
                a,b=st.columns([5,2]); a.subheader(f"🥡 Поръчка №{oid}"); b.metric("Общо",f"€ {o['total']:.2f}")
                st.write(f"**Клиент:** {o['name']}  |  **Телефон:** {o['phone']}")
                st.write(f"**Адрес:** {o['address']}")
                st.caption(f"Получена: {o['created'].strftime('%d.%m.%Y %H:%M') if o['created'] else '-'}")
                for item in o['items']:
                    _,name,qty,note,status=item
                    st.markdown(f"**{name} × {qty}** · {status}")
                    if note: st.caption(f"📝 {note}")
                c1,c2=st.columns(2)
                if c1.button("🟡 Приготвя се",key=f"prep_{oid}",use_container_width=True): set_order_status(oid,"IN_PROGRESS"); st.rerun(scope="fragment")
                if c2.button("✅ Готова за куриер",key=f"ready_{oid}",type="primary",use_container_width=True): set_order_status(oid,"READY"); st.rerun(scope="fragment")
    live_orders()
with tab_daily:
    rows=daily_catalog(); labels={r[0]:f"{r[3]} | {r[1]} | € {float(r[2]):.2f}" for r in rows}; ids=[r[0] for r in rows]
    selected=st.multiselect("Активни предложения за деня",ids,default=[r[0] for r in rows if r[4]],format_func=lambda x:labels[x])
    if st.button("💾 Запази дневното меню",type="primary"): save_daily(selected); st.success("Дневното меню е обновено."); st.rerun()
    with st.expander("➕ Добави нов артикул"):
        group=st.selectbox("Секция",["🍲 Супи","🍽️ Готови ястия","🍰 Десерт"]); name=st.text_input("Име"); price=st.number_input("Цена €",min_value=0.0,step=0.1)
        if st.button("Добави и активирай"):
            if not name.strip(): st.error("Въведете име.")
            else: add_daily(name,price,group); st.success("Добавено."); st.rerun()
    if ids:
        delete_id=st.selectbox("Изтриване на артикул",ids,format_func=lambda x:labels[x])
        if st.button("🗑️ Изтрий избрания"): db("DELETE FROM menu_items WHERE id=%s AND is_daily_item=TRUE",(delete_id,),False); st.rerun()
with tab_admin:
    c1,c2=st.columns(2); date_from=c1.date_input("От",datetime.now().date().replace(day=1)); date_to=c2.date_input("До",datetime.now().date())
    rows=archive_rows(date_from,date_to)
    cols=["Поръчка","Създадена","Обновена","Доставена","Статус кухня","Статус куриер","Клиент","Телефон","Адрес","Общо €","Артикул","Количество","Коментар"]
    df=pd.DataFrame(rows,columns=cols)
    unique=df.drop_duplicates("Поръчка") if not df.empty else df
    delivered=unique[unique["Статус куриер"]=="DELIVERED"] if not unique.empty else unique
    m1,m2,m3=st.columns(3); m1.metric("Поръчки",len(unique)); m2.metric("Доставени",len(delivered)); m3.metric("Оборот",f"€ {unique['Общо €'].sum():.2f}" if not unique.empty else "€ 0.00")
    st.dataframe(df,use_container_width=True,hide_index=True)
    out=io.BytesIO()
    with pd.ExcelWriter(out,engine="openpyxl") as writer: df.to_excel(writer,index=False,sheet_name="Provence orders")
    st.download_button("⬇️ Изтегли Excel архив",out.getvalue(),file_name=f"provence_orders_{date_from}_{date_to}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)

