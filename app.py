import streamlit as st
import joblib
import numpy as np

st.set_page_config(
    page_title="🏠 قیمت‌یاب ملک ایران",
    page_icon="🏠",
    layout="centered"
)

st.markdown("""
<style>
body {
    direction: rtl;
    text-align: right;
}
</style>
<div style="position: fixed; top: 10px; left: 10px; font-size: 11px; color: gray; z-index: 999;">
    Developer: Mohammad Porrali
</div>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    model = joblib.load(r'C:\Users\lenovo\Desktop\model_v3.pkl')
    encoder = joblib.load(r'C:\Users\lenovo\Desktop\encoder_v3.pkl')
    return model, encoder

try:
    model, le = load_model()
    model_loaded = True
    cities_list = list(le.classes_)
except:
    model_loaded = False
    cities_list = ["tehran", "mashhad", "isfahan", "shiraz", "tabriz"]

st.title("🏠 قیمت‌یاب ملک ایران")
st.markdown("### قیمت تقریبی آپارتمان در شهرهای ایران")

if not model_loaded:
    st.error("❌ مدل پیدا نشد! لطفاً ابتدا scraper.py را اجرا کنید.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    selected_city = st.selectbox(
        "🏙️ شهر را انتخاب کنید:",
        cities_list
    )
    
    metrage = st.number_input(
        "📐 متراژ (متر مربع):",
        min_value=20,
        max_value=2000,
        value=80,
        step=10
    )

with col2:
    age = st.number_input(
        "🏗️ سن بنا (سال):",
        min_value=0,
        max_value=50,
        value=5,
        step=1
    )
    
    rooms = st.selectbox(
        "🚪 تعداد اتاق:",
        ["نمی‌دانم", "۱", "۲", "۳", "۴+"]
    )

st.markdown("---")

if st.button("💰 محاسبه قیمت", type="primary", use_container_width=True):
    
    city_code = le.transform([selected_city])[0]
    
    base_price = model.predict([[metrage, age, city_code]])[0]
    
    if rooms == "۱":
        base_price *= 0.85
    elif rooms == "۲":
        base_price *= 0.95
    elif rooms == "۳":
        base_price *= 1.0
    elif rooms == "۴+":
        base_price *= 1.15
    
    price_per_meter = base_price / metrage
    
    st.success("✅ قیمت تقریبی محاسبه شد!")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("💰 قیمت کل", f"{base_price:,.0f} تومان")
    
    with c2:
        st.metric("📊 قیمت هر متر", f"{price_per_meter:,.0f} تومان")
    
    with c3:
        st.metric("📐 متراژ", f"{metrage} متر")
    
    st.markdown("---")
    st.markdown(f"""
    ### 📋 مشخصات ملک
    - 🏙️ شهر: {selected_city}
    - 📐 متراژ: {metrage} متر مربع
    - 🏗️ سن بنا: {age} سال
    - 🚪 اتاق: {rooms}
    """)

st.markdown("---")
st.caption("""
⚠️ توجه: این قیمت‌ها تقریبی و بر اساس داده‌های دیوار محاسبه شده‌اند.
قیمت واقعی ممکن است با توجه به موقعیت دقیق، امکانات و شرایط بازار متفاوت باشد.
""")