from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import numpy as np
import re
import time
import random
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import LabelEncoder
import joblib

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36')

cities = [
    "tehran", "mashhad", "isfahan", "shiraz", "tabriz", 
    "ahvaz", "karaj", "qom", "kermanshah", "rasht",
    "urmia", "zahedan", "hamedan", "yazd", "ardabil",
    "bandar-abbas", "arak", "eslamshahr", "qazvin", "zanjan"
]

def clean_price(price_str):
    if not price_str:
        return None
    price_str = str(price_str).replace('تومان', '').replace(',', '').strip()
    try:
        return int(price_str)
    except:
        return None

def extract_ad_data(ad_text, city):
    lines = ad_text.split('\n')
    title = lines[0] if lines else ''
    
    price = None
    metrage = None
    age = None
    
    for line in lines:
        line = line.strip()
        if 'تومان' in line and not price:
            price = clean_price(line)
        match = re.search(r'(\d+)\s*متر', line)
        if match and not metrage:
            metrage = int(match.group(1))
        match = re.search(r'(\d+)\s*سال', line)
        if match and not age:
            age = int(match.group(1))
    
    if metrage and price:
        return {'city': city, 'metrage': metrage, 'price': price, 'age': age if age else 0}
    return None

def scrape_city(driver, city):
    url = f"https://divar.ir/s/{city}/buy-apartment?map_interaction=search_this_area_disabled"
    driver.get(url)
    time.sleep(random.uniform(3, 5))
    
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 400);")
        time.sleep(random.uniform(1, 2))
    
    ads = driver.find_elements(By.CSS_SELECTOR, 'div.kt-post-card, article, a.kt-post-card')
    
    city_ads = []
    for ad in ads:
        data = extract_ad_data(ad.text, city)
        if data:
            city_ads.append(data)
    
    return city_ads

print("🚀 شروع اسکریپ شهرهای ایران...")
driver = webdriver.Chrome(options=options)
all_ads = []

for i, city in enumerate(cities):
    print(f"\n📍 [{i+1}/{len(cities)}] {city}...")
    city_ads = scrape_city(driver, city)
    all_ads.extend(city_ads)
    print(f"   ✅ {len(city_ads)} آگهی | جمع کل: {len(all_ads)}")
    time.sleep(random.uniform(2, 4))

driver.quit()

print(f"\n🎉 مجموع آگهی‌ها: {len(all_ads)}")

df = pd.DataFrame(all_ads)
df = df[df['price'] > 100000000]
df = df[df['metrage'].between(20, 2000)]
df = df[df['price'] <= df['price'].quantile(0.95)]
df = df[df['metrage'] <= df['metrage'].quantile(0.95)]

print(f"📊 بعد از تمیزکاری: {len(df)} آگهی")

le = LabelEncoder()
df['city_code'] = le.fit_transform(df['city'])

X = df[['metrage', 'age', 'city_code']].values
y = df['price'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"\nداده آموزش: {len(X_train)}")
print(f"داده تست: {len(X_test)}")

model = XGBRegressor(n_estimators=100, max_depth=5, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

print(f"\n📉 خطای مدل (MAE): {mae:,.0f} تومان")
print(f"📊 میانگین قیمت: {y.mean():,.0f} تومان")
print(f"✅ دقت تقریبی: {(1 - mae/y.mean())*100:.1f}%")
joblib.dump(model, r'C:\Users\lenovo\Desktop\model_v3.pkl')
joblib.dump(le, r'C:\Users\lenovo\Desktop\encoder_v3.pkl')
df.to_csv(r'C:\Users\lenovo\Desktop\iran_apartments.csv', index=False)
print("\n💾 ذخیره شد تو Desktop")
print("🎉 حالا app.py رو اجرا کن!")