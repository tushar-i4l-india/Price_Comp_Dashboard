import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, timedelta
import re
import glob
import streamlit.components.v1 as components
from PIL import Image
import time

# MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Price Comparison Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

# ---------------- USERS ---------------- #

USERS = {
    "admin": "price@123",
    "Nicola": "admin@123",
    "Shubham": "admin@123",
    "Ashish": "admin@123"
}

# ---------------- SESSION ---------------- #

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

if "last_activity" not in st.session_state:
    st.session_state.last_activity = time.time()

SESSION_TIMEOUT = 1800

# ---------------- AUTO LOGOUT ---------------- #

if st.session_state.logged_in:
    if time.time() - st.session_state.last_activity > SESSION_TIMEOUT:
        st.session_state.logged_in = False
        st.warning("Session expired. Please login again.")
        st.rerun()

st.session_state.last_activity = time.time()


# ---------------- LOGIN PAGE ---------------- #

def login_page():

    st.markdown("""
    <style>

    [data-testid="stAppViewContainer"]{
    background: radial-gradient(circle at top,#141e30,#000000);
    }

    .login-box{
    width:420px;
    margin:auto;
    margin-top:150px;
    padding:40px;
    background:rgba(0,0,0,0.75);
    border-radius:12px;
    box-shadow:0 20px 60px rgba(0,0,0,0.9);
    text-align:center;
    animation: float 6s ease-in-out infinite;
    }

    @keyframes float{
    0%{transform:translateY(0px)}
    50%{transform:translateY(-10px)}
    100%{transform:translateY(0px)}
    }

    .title{
    font-size:26px;
    font-weight:700;
    margin-bottom:20px;
    color:white;
    }

    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.markdown('<div class="login-box">', unsafe_allow_html=True)

        st.image(
            "https://cdn.shopify.com/s/files/1/0250/6198/2261/files/Insulation4less_main_logo.png",
            width=180
        )

        st.markdown('<div class="title">Dashboard Login</div>', unsafe_allow_html=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if username in USERS and USERS[username] == password:

                st.session_state.logged_in = True
                st.session_state.user = username
                st.success("Login successful")
                st.rerun()

            else:
                st.error("Invalid username or password")

        st.markdown('</div>', unsafe_allow_html=True)


# ---------------- LOGIN CHECK ---------------- #

if not st.session_state.logged_in:
    login_page()
    st.stop()


# ---------------- SIDEBAR ---------------- #

st.sidebar.image(
    "https://cdn.shopify.com/s/files/1/0250/6198/2261/files/Insulation4less_main_logo.png?v=1767346032",
    width=200
)

st.sidebar.write(f"👤 Logged in: **{st.session_state.user}**")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.title("Price Comparison Dashboard 💷")


# ---------------- YOUR ORIGINAL DASHBOARD CODE ---------------- #

@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    return df


def extract_price(price):
    if pd.isna(price):
        return None
    if isinstance(price, (int, float)):
        return round(float(price), 2)
    if isinstance(price, str):
        match = re.search(r"[\d,.]+", price)
        if match:
            return round(float(match.group().replace(",", "")), 2)
    return None


base_directory = os.path.join(os.getcwd(), "Compititor's_Price")

brands = [
    "Celotex", "Recticel", "Ecotherm", "Unilin",
    "IKO", "Mannok", "Core-Products", "Cladco",
    "Novia", "Powerlon", "Superfoil", "Rockwool"
]

selected_brand = st.sidebar.selectbox("Select Brand", brands)

if selected_brand:

    brand_directory = os.path.join(base_directory, f"{selected_brand}_Prices")

    files = [f for f in os.listdir(brand_directory) if f.endswith(".xlsx")]

    dates = []

    for f in files:
        try:
            date_str = f.split("_")[-1].replace(".xlsx", "").strip()
            date_obj = datetime.strptime(date_str, "%d-%m-%Y")
            dates.append(date_obj)
        except:
            pass

    dates = sorted(dates, reverse=True)

    selected_date = st.sidebar.date_input(
        "Select Date",
        value=max(dates).date()
    )

    selected_date = selected_date.strftime("%d-%m-%Y")

    file_name = f"{selected_brand}_Prices_{selected_date}.xlsx"

    data_path = os.path.join(brand_directory, file_name)

    if os.path.exists(data_path):

        df = load_data(data_path)

        st.write(f"### Price list for `{selected_brand}`")

        st.dataframe(df, height=600)

        products = df["Product"].unique()

        selected_product = st.sidebar.selectbox("Select Product", products)

        product_data = df[df["Product"] == selected_product]

        melted_data = product_data.melt(
            id_vars=["Product", "SKU"],
            var_name="Competitor",
            value_name="Price"
        )

        melted_data["Price"] = melted_data["Price"].astype(str).apply(extract_price)

        melted_data = melted_data.dropna()

        fig = px.bar(
            melted_data,
            x="Competitor",
            y="Price",
            color="Competitor",
            title=f"Price Comparison for {selected_product}",
            text="Price"
        )

        st.plotly_chart(fig)

    else:

        st.error("❌ Data for selected date not available")