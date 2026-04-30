import streamlit as st
import pandas as pd
import numpy as np

# Set up the webpage layout
st.set_page_config(page_title="SabiPrice: Market Finder", page_icon="🌾", layout="wide")

# ==========================================
# BACKEND LOGIC 
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    r = 6371
    return c * r

@st.cache_data(ttl=86400)
def load_and_clean_data():
    url = "https://data.humdata.org/dataset/42db041f-7aaf-4ab4-961f-2a12096861e7/resource/12b51155-0cd3-4806-9924-61ede4077591/download/wfp_food_prices_nga.csv"
    df_raw = pd.read_csv(url, skiprows=[1])
    df_clean = df_raw.copy()

    # 1. Basic Cleaning
    df_clean = df_clean[(df_clean['latitude'] != 0) | (df_clean['longitude'] != 0)]
    df_clean['date'] = pd.to_datetime(df_clean['date'])
    df_clean['commodity'] = df_clean['commodity'].str.strip()

    # 2. Standardize all units to 1 KG (No early return here!)
    unit_map = {
        'KG': 1, '100 KG': 100, '50 KG': 50, '2.7 KG': 2.7, '2.6 KG': 2.6, 
        '2.8 KG': 2.8, '2.5 KG': 2.5, '2.2 KG': 2.2, '2.1 KG': 2.1, 
        '1.3 KG': 1.3, '0.5 KG': 0.5, 'L': 1, '100 L': 100, 
        '500 G': 0.5, '400 G': 0.4, '300 G': 0.3, '250 G': 0.25,
        '750 ML': 0.75, '150 G': 0.15, '1.4 KG': 1.4, '20 G': 0.02, '400 ML': 0.4,
        '100 Tubers': 250, '30 pcs': 1.5, 'Unit': 1 
    }
    df_clean['weight_kg'] = df_clean['unit'].map(unit_map)
    df_clean = df_clean.dropna(subset=['weight_kg'])
    df_clean['price_per_kg'] = df_clean['price'] / df_clean['weight_kg']
    
    # 3. Filter Outliers
    def filter_outliers(group):
        mean = group['price_per_kg'].mean()
        std = group['price_per_kg'].std()
        if pd.isna(std) or std == 0: return group 
        return group[(group['price_per_kg'] >= mean - 3*std) & (group['price_per_kg'] <= mean + 3*std)]
    
    df_clean = df_clean.groupby('commodity', group_keys=False).apply(filter_outliers)
    
    return df_clean # THE ONLY RETURN STATEMENT

def find_best_markets(df, my_lat, my_lon, selected_commodity, max_distance_km):
    # FIXED: We use the variable 'selected_commodity' instead of the word 'commodity'
    df_target = df[df['commodity'].str.contains(selected_commodity, case=False, na=False)].copy()
    
    if df_target.empty: 
        return f"No data found for {selected_commodity}."
        
    # Filter for the last 12 months to ensure we have enough data points
    max_date = df_target['date'].max()
    recent_cutoff = max_date - pd.DateOffset(months=12) 
    df_target = df_target[df_target['date'] >= recent_cutoff]
    
    if df_target.empty: 
        return f"No recent data found for {selected_commodity}."

    latest_prices = df_target.loc[df_target.groupby('market')['date'].idxmax()].copy()
    latest_prices['distance_km'] = haversine(my_lat, my_lon, latest_prices['latitude'], latest_prices['longitude'])
    
    nearby_markets = latest_prices[latest_prices['distance_km'] <= max_distance_km].copy()
    if nearby_markets.empty: 
        return f"No markets found within {max_distance_km}km of your location."
        
    nearby_markets = nearby_markets.sort_values('price_per_kg', ascending=False)
    
    report = nearby_markets[['market', 'admin1', 'pricetype', 'distance_km', 'price_per_kg', 'date']].head(5)
    report.columns = ['Market', 'State', 'Market Type', 'Distance (KM)', 'Price/KG (NGN)', 'Last Updated']
    report['Distance (KM)'] = report['Distance (KM)'].round(1)
    report['Price/KG (NGN)'] = report['Price/KG (NGN)'].round(2)
    report['Last Updated'] = report['Last Updated'].dt.strftime('%Y-%m-%d')
    
    return report

# ==========================================
# FRONTEND UI
# ==========================================
clean_df = load_and_clean_data()

st.title("🌾 SabiPrice: Get the Best Price for Your Harvest")
st.markdown("### **See where your crops are selling for the highest price so you don't get cheated.**")
st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📍 Where are you?")
    states = sorted(clean_df['admin1'].dropna().unique())
    selected_state = st.selectbox("Choose your State:", states)
    
    state_data = clean_df[clean_df['admin1'] == selected_state]
    local_markets = sorted(state_data['market'].dropna().unique())
    selected_market = st.selectbox("Choose your nearest town:", local_markets)
    
    market_info = state_data[state_data['market'] == selected_market].iloc[0]
    farmer_lat = market_info['latitude']
    farmer_lon = market_info['longitude']
    
    st.subheader("🚚 Transport & Crop")
    distance_options = {
        "Local (50km)": 50,
        "Regional (150km)": 150,
        "Interstate (300km)": 300,
        "National (1000km)": 1000
    }
    
    selected_dist_text = st.selectbox("How far can you go?", options=list(distance_options.keys()), index=1)
    max_dist = distance_options[selected_dist_text]
    
    # Using crops we know exist in the dataset
    target_crops = ['Maize', 'Rice', 'Sorghum', 'Beans', 'Yam', 'Cassava', 'Cowpeas', 'Onions']
    selected_crop = st.selectbox("Crop to sell:", target_crops)
    
    search_button = st.button("🔍 Find Prices", type="primary", use_container_width=True)

with col2:
    if search_button:
        with st.spinner("Analyzing market data..."):
            report = find_best_markets(clean_df, farmer_lat, farmer_lon, selected_crop, max_distance_km=max_dist)
            
            if isinstance(report, str):
                st.warning(report)
            else:
                st.success(f"Top markets found near {selected_market}!")
                st.dataframe(report, use_container_width=True, hide_index=True)
                
                top_price = report.iloc[0]['Price/KG (NGN)']
                top_market = report.iloc[0]['Market']
                
                st.info(f"💡 **ADVICE:** {selected_crop} is selling for **₦{top_price}/KG** in {top_market}. Use this to negotiate with middlemen!")
    else:
        st.info("👈 Enter your details and click 'Find Prices' to begin.")
