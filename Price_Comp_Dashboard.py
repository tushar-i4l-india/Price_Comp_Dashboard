import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, timedelta
import re
import glob

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="Price Comparison Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------- LOGIN SYSTEM ---------------- #

USERS = {
    "Admin": "Price@123",
    "Nicola": "admin@123",
    "Shubham": "admin@123",
    "Ashish": "admin@123"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


def login():

    st.title("🔐 Price Dashboard Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid login")


if not st.session_state.logged_in:
    login()
    st.stop()


# ---------------- HEADER ---------------- #

col1, col2 = st.columns([6, 1])

with col1:
    st.markdown(f"### 👋 Welcome **{st.session_state.username}**")

with col2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ---------------- PATH ---------------- #

BASE_DIR = os.path.join(os.getcwd(), "Compititor's_Price")


# ---------------- FUNCTIONS ---------------- #

@st.cache_data
def load_excel(file):
    return pd.read_excel(file)


def extract_price(value):

    if pd.isna(value):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value)

    if "price not found" in value.lower():
        return None

    match = re.search(r"[\d,.]+", value)

    if match:
        return float(match.group().replace(",", ""))

    return None


def get_brands():

    brands = []

    for folder in os.listdir(BASE_DIR):
        if folder.endswith("_Prices"):
            brands.append(folder.replace("_Prices", ""))

    return sorted(brands)


def get_available_dates(brand):

    folder = os.path.join(BASE_DIR, f"{brand}_Prices")

    files = glob.glob(os.path.join(folder, "*.xlsx"))

    dates = []

    for f in files:
        try:
            date = f.split("_")[-1].replace(".xlsx", "")
            dates.append(datetime.strptime(date, "%d-%m-%Y"))
        except:
            continue

    return sorted(dates, reverse=True)


def load_brand_data(brand, date):

    folder = os.path.join(BASE_DIR, f"{brand}_Prices")

    file = os.path.join(folder, f"{brand}_Prices_{date}.xlsx")

    return load_excel(file)


# ---------------- SIDEBAR ---------------- #

st.sidebar.image(
    "https://cdn.shopify.com/s/files/1/0250/6198/2261/files/Insulation4less_main_logo.png?v=1767346032",
    width=200
)

st.sidebar.title("📊 Dashboard")

brands = get_brands()

selected_brand = st.sidebar.selectbox("Select Brand", brands)

dates = get_available_dates(selected_brand)

selected_date = st.sidebar.date_input(
    "Select Date",
    value=dates[0].date() if dates else datetime.today()
)

selected_date = selected_date.strftime("%d-%m-%Y")

# ---------------- LOAD DATA ---------------- #

try:

    df = load_brand_data(selected_brand, selected_date)

except:

    st.error("No data available for selected date")

    st.stop()


# ---------------- TABS ---------------- #

tab1, tab2, tab3 = st.tabs(
    ["📋 Data", "📊 Price Comparison", "📈 Price Trend"]
)

# ---------------- TAB 1 DATA ---------------- #

with tab1:

    st.subheader(f"{selected_brand} Price List")

    st.dataframe(df, use_container_width=True)


# ---------------- TAB 2 COMPARISON ---------------- #

with tab2:

    products = df["Product"].unique()

    selected_product = st.selectbox(
        "Select Product",
        products
    )

    product_data = df[df["Product"] == selected_product]

    melted = product_data.melt(
        id_vars=["Product", "SKU"],
        var_name="Competitor",
        value_name="Price"
    )

    melted["Price"] = melted["Price"].apply(extract_price)

    melted = melted.dropna()

    melted = melted.sort_values("Price")

    fig = px.bar(
        melted,
        x="Competitor",
        y="Price",
        color="Competitor",
        text="Price",
        title=f"Price Comparison: {selected_product}"
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------------- TAB 3 TREND ---------------- #

with tab3:

    folder = os.path.join(BASE_DIR, f"{selected_brand}_Prices")

    files = glob.glob(os.path.join(folder, "*.xlsx"))

    data = []

    for file in files:

        try:

            date_str = file.split("_")[-1].replace(".xlsx", "")

            date = datetime.strptime(date_str, "%d-%m-%Y")

            temp = pd.read_excel(file)

            temp["date"] = date

            data.append(temp)

        except:
            continue

    if not data:
        st.warning("No historical data")
        st.stop()

    df_all = pd.concat(data)

    df_long = df_all.melt(
        id_vars=["SKU", "Product", "date"],
        var_name="website",
        value_name="price"
    )

    df_long["price"] = df_long["price"].apply(extract_price)

    df_long = df_long.dropna()

    selected_product = st.selectbox(
        "Product for Trend",
        df_long["Product"].unique()
    )

    trend = df_long[df_long["Product"] == selected_product]

    trend = trend.groupby("date")["price"].mean().reset_index()

    fig = px.line(
        trend,
        x="date",
        y="price",
        markers=True,
        title=f"Average Price Trend: {selected_product}"
    )

    st.plotly_chart(fig, use_container_width=True)