# SabiPrice
Market Intelligence Platform for Rural Farmers.

# 🌾 SabiPrice: Market Intelligence Platform for Rural Farmers

## The Problem
In Nigeria, rural farmers lose a significant percentage of their potential revenue to predatory middlemen. Due to a lack of transparent, localized market data, farmers at the farm gate often accept prices far below the actual market value of their crops.

## The Solution: SabiPrice
SabiPrice is an interactive, data-driven web application designed to bridge this information gap. By leveraging live World Food Programme (WFP) commodity data and geographic distance calculations, the platform empowers farmers to discover the most profitable nearby markets.

### Key Features
* **Geographic Arbitrage Engine:** Uses the **Haversine formula** to calculate the exact distance between the farmer's local town and higher-paying regional markets.
* **Live Data Pipeline:** Automatically fetches and caches the latest Humanitarian Data Exchange (HDX) food price datasets, ensuring no manual database maintenance is required.
* **Smart Filtering:** Removes extreme inflationary outliers using standard deviation filtering, ensuring farmers see realistic negotiation targets.
* **Farmer-Friendly UI:** Translates complex spatial radii into intuitive transport categories (e.g., "I can hire a local truck").

## Technical Stack
* **Language:** Python
* **Frontend/UI:** Streamlit
* **Data Manipulation:** Pandas, NumPy
* **Data Source:** World Food Programme (HDX API)

## Data Limitations & Future Scope
This PoC currently relies on WFP humanitarian data, which heavily indexes conflict zones (like the Northeast) and major trade hubs (like Dawanau), leaving blind spots in rural, stable regions. 
* **Future Iteration:** Transition from WFP batch data to a live crowdsourced database (via SMS/USSD) where local market agents update daily prices, creating a true, second-by-second agricultural exchange.

## How to Run Locally
1. Clone this repository.
2. Install the requirements: `pip install -r requirements.txt`
3. Run the application: `streamlit run app.py`
