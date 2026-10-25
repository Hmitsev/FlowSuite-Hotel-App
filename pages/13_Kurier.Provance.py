import streamlit as st
from lastoria.database.db import get_connection
st.set_page_config(page_title="Provence Courier",page_icon="🚚",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>[data-testid='stSidebar'],[data-testid='collapsedControl']{display:none!important}.stApp{background:#0b0f14}h1,h2,h3{color:#d8b76a!important}</style>""",unsafe_allow_html=True)
PASSWORD="courier2026"
if not st.session_state.get("provence_courier_auth"):
    st.title("🚚 Provence Courier")
    p=st.text_input("Парола",type="password")
    if st.button("Вход",type="primary"):
        if p==PASSWORD: st.session_state.provence_courier_auth=True; st.rerun()
        else: st.error("Невалидна парола.")
    st.stop()
def db(q,p=(),fetch=True):
    c=get_connection();x=c.cursor()
    try:x.execute(q,p);r=x.fetchall() if fetch else None;c.commit();return r
    except Exception:c.rollback();raise
    finally:x.close();c.close()
def orders():
    return db("""SELECT o.id,o.created_at,o.customer_name,o.customer_phone,o.delivery_address,COALESCE(o.total_amount,0),o.order_status,COALESCE(o.courier_status,'WAITING_KITCHEN'),
        STRING_AGG(mi.item_name||' x'||oi.quantity::text,', ' ORDER BY oi.id)
        FROM orders o JOIN order_items oi ON oi.order_id=o.id JOIN menu_items mi ON mi.id=oi.item_id
        WHERE o.order_source='PROVANCE_TAKEAWAY' AND COALESCE(o.courier_status,'')<>'DELIVERED'
        GROUP BY o.id ORDER BY CASE WHEN o.order_status='READY' THEN 0 ELSE 1 END,o.created_at""")
def update(oid,status):
    extra={"SEEN":"courier_seen_at=CURRENT_TIMESTAMP","PICKED_UP":"courier_picked_at=CURRENT_TIMESTAMP","DELIVERED":"delivered_at=CURRENT_TIMESTAMP,order_status='COMPLETED',completed_at=CURRENT_TIMESTAMP"}[status]
    db(f"UPDATE orders SET courier_status=%s,{extra},updated_at=CURRENT_TIMESTAMP WHERE id=%s",(status,oid),False)
st.title("🚚 Куриер · Restaurant Provence")
st.caption("Последователност: Видяна → Взета → Доставена")
@st.fragment(run_every="20s")
def live():
    rows=orders(); ready=sum(1 for r in rows if r[6]=="READY")
    st.info(f"Заявки: {len(rows)} · Готови за вземане: {ready}")
    if not rows: st.success("Няма активни доставки.")
    for oid,created,name,phone,address,total,kitchen,status,items in rows:
        with st.container(border=True):
            a,b=st.columns([5,2]);a.subheader(f"📦 Поръчка №{oid}");b.metric("Сума",f"€ {float(total):.2f}")
            st.write(f"**{name}** · 📞 {phone}");st.write(f"📍 **{address}**");st.caption(items)
            if kitchen!="READY": st.warning("⏳ Кухнята още приготвя поръчката.")
            else: st.success("✅ Поръчката е готова за вземане.")
            if status in ("WAITING_KITCHEN","READY_FOR_PICKUP"):
                if st.button("👁️ Видяна",key=f"seen_{oid}",use_container_width=True):update(oid,"SEEN");st.rerun(scope="fragment")
            elif status=="SEEN":
                if st.button("🛍️ Взета от ресторанта",key=f"pick_{oid}",type="primary",disabled=kitchen!="READY",use_container_width=True):update(oid,"PICKED_UP");st.rerun(scope="fragment")
            elif status=="PICKED_UP":
                if st.button("🏁 Доставена",key=f"del_{oid}",type="primary",use_container_width=True):update(oid,"DELIVERED");st.rerun(scope="fragment")
            st.caption(f"Статус: {status}")
live()

