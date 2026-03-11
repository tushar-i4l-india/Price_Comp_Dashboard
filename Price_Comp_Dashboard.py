import streamlit as st 
import pandas as pd 
import os
import plotly.express as px  
from datetime import datetime, timedelta
import re
import glob
import streamlit.components.v1 as components 
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# ---- USER LOGIN ---- #

USER_CREDENTIALS = {
    "admin": "price@123",
    "Ashish": "admin123",
    "Shubham": "admin@123",
    "Nicola": "admin@123"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ---- LOGIN PAGE ---- #

def animated_login():

    components.html("""
    <!DOCTYPE html>
    <html>
    <head>

    <style>

    body{
    margin:0;
    height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
    background:linear-gradient(-45deg,#667eea,#764ba2,#6a11cb,#2575fc);
    background-size:400% 400%;
    animation:gradient 10s ease infinite;
    font-family:Arial;
    }

    @keyframes gradient{
    0%{background-position:0% 50%;}
    50%{background-position:100% 50%;}
    100%{background-position:0% 50%;}
    }

    .card{
    width:350px;
    padding:40px;
    border-radius:12px;
    background:rgba(255,255,255,0.15);
    backdrop-filter:blur(12px);
    text-align:center;
    color:white;
    }

    input{
    width:100%;
    padding:10px;
    margin:10px 0;
    border:none;
    border-radius:6px;
    }

    button{
    width:100%;
    padding:12px;
    border:none;
    background:#f6b300;
    border-radius:6px;
    font-weight:bold;
    cursor:pointer;
    }

    </style>

    </head>

    <body>

    <div class="card">

    <h2>INSULATION4LESS</h2>
    <p>Dashboard Login</p>

    <input placeholder="Username">
    <input type="password" placeholder="Password">

    <button>Login</button>

    </div>

    </body>
    </html>
    """, height=700)


# ---- SHOW LOGIN FIRST ---- #

if not st.session_state.logged_in:
    animated_login()

    # Real login form below animation
    st.markdown("### Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.rerun()

        else:
            st.error("Invalid username or password")

    st.stop()


# ---- DASHBOARD AFTER LOGIN ---- #

st.title("Price Comparison Dashboard")
st.success("Welcome Ashish 🎉")

# ✅ MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Price Comparison Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    menu_items={
        'Get Help': 'https://insulation4less.co.uk/pages/contact-us',
        'Report a bug': "https://www.insulation4less.co.uk",
        'About': "This app is a price comparison dashboard",
    }
)

# ✅ Sidebar logo (NOW SAFE)
st.sidebar.image(
    "https://cdn.shopify.com/s/files/1/0250/6198/2261/files/Insulation4less_main_logo.png?v=1767346032",
    width=200
)
st.set_page_config(page_title="Price Comparison Dashboard", page_icon=":bar_chart:", layout="wide", menu_items={
    'Get Help': 'https://insulation4less.co.uk/pages/contact-us',
    'Report a bug': "https://www.insulation4less.co.uk",
    'About': "This app is a price comparison dashboard",
})

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
        if "price not found" in price.lower() or "no link" in price.lower() or price.lower().startswith("error:"):
            return None
        match = re.search(r"[\d,.]+", price)
        if match:
            return round(float(match.group().replace(",", "")), 2)
    return None

def highlight_changes(row):
    styles = []
    for col in website_columns:
        today_price = extract_price(row[col])
        prev_col = col + "_yesterday"

        prev_price_str = df_merged.loc[row.name, prev_col] if prev_col in df_merged.columns else None
        prev_price = extract_price(prev_price_str)

        style = ""
        if today_price is not None and prev_price is not None:
            if today_price > prev_price:
                style = "color: red; font-weight: bold;"
            elif today_price < prev_price:
                style = "color: green; font-weight: bold;"
            elif today_price == prev_price:
                style = "color: blue;"
        styles.append(style)
    return styles

base_directory = os.path.join(os.getcwd(), "Compititor's_Price")

if 'selected_brand' not in st.session_state:
    st.session_state.selected_brand = None
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'previous_date_str' not in st.session_state:
    st.session_state.previous_date_str = None

st.sidebar.title("Price Comparison Dashboard 💷")

brands = ["Celotex", "Recticel", "Ecotherm", "Unilin", "IKO", "Mannok", "Core-Products", "Cladco", "Novia", "Powerlon", "Superfoil", "Rockwool"]
st.session_state.selected_brand = st.sidebar.selectbox("Select Brand", brands)

if st.session_state.selected_brand:
    brand_directory = os.path.join(base_directory, f"{st.session_state.selected_brand}_Prices")
    files = [f for f in os.listdir(brand_directory) if f.endswith(".xlsx")]

    # FIXED: Safely parse dates from filenames
    dates = []
    for f in files:
        try:
            date_str = f.split("_")[-1].replace(".xlsx", "").strip()
            date_obj = datetime.strptime(date_str, "%d-%m-%Y")
            dates.append(date_obj)
        except ValueError:
            print(f"Skipping file with invalid date format: {f}")
    dates = sorted(dates, reverse=True)
    sorted_dates = [date.strftime("%d-%m-%Y") for date in dates]

    st.session_state.selected_date = st.sidebar.date_input(
        "Select Date", 
        value=max(dates).date() if dates else datetime.today().date(),
        min_value=min(dates).date() if dates else datetime.today().date()
    )
    st.session_state.selected_date = st.session_state.selected_date.strftime("%d-%m-%Y")

    file_name = f"{st.session_state.selected_brand}_Prices_{st.session_state.selected_date}.xlsx"
    data_path = os.path.join(brand_directory, file_name)

    if st.session_state.selected_date and os.path.exists(data_path):
        selected_date_obj = datetime.strptime(st.session_state.selected_date, "%d-%m-%Y")
        previous_date_obj = selected_date_obj - timedelta(days=1)
        previous_date_str = previous_date_obj.strftime("%d-%m-%Y")
        st.session_state.previous_date_str = previous_date_str
        prev_file_name = f"{st.session_state.selected_brand}_Prices_{st.session_state.previous_date_str}.xlsx"
        prev_data_path = os.path.join(brand_directory, prev_file_name)

        if st.sidebar.button("Preview Data") or st.session_state.data_loaded:
            st.session_state.data_loaded = True
            tab1, tab2, tab3 = st.tabs(["🗃 Data", ":bar_chart: Price Comparison", ":chart_with_upwards_trend: Price Trend (Average Price)"])
            df = load_data(data_path)

            with tab1:
                st.write(f"### Price list for `{st.session_state.selected_brand}`")
                website_columns = df.columns[2:]
                try:
                    prev_df = load_data(prev_data_path)
                    df_merged = df.merge(prev_df, on=["SKU", "Product"], how="left", suffixes=("_today", "_yesterday"))
                    df_display = df_merged[["SKU", "Product"] + [col + "_today" for col in website_columns]].copy()
                    rename_dict = {col + "_today": col for col in website_columns}
                    df_display.rename(columns=rename_dict, inplace=True)
                    styled_df = df_display.style.apply(highlight_changes, axis=1, subset=website_columns)
                    for col in website_columns:
                        df_display[col] = df_display[col].astype(str)
                        df_display[col + "_Arrow"] = ""
                        for index, row in df_display.iterrows():
                            today_price = extract_price(row[col])
                            prev_col = col + "_yesterday"
                            prev_price_str = df_merged.loc[index, prev_col] if prev_col in df_merged.columns else None
                            prev_price = extract_price(prev_price_str)
                            if today_price is not None and prev_price is not None:
                                if today_price > prev_price:
                                    df_display.at[index, col + "_Arrow"] = "🔺"
                                elif today_price < prev_price:
                                    df_display.at[index, col + "_Arrow"] = "🔻"
                    for col in website_columns:
                        df_display[col] = df_display[col] + " " + df_display[col + "_Arrow"]
                        df_display.drop(columns=[col + "_Arrow"], inplace=True)
                    st.dataframe(styled_df, hide_index=True, height=600)
                except:
                    st.dataframe(df, hide_index=True, height=600)

            with tab2:
                products = df["Product"].unique()
                st.session_state.selected_product = st.sidebar.selectbox("Select Product", products)
                if st.session_state.selected_product:
                    product_data = df[df["Product"] == st.session_state.selected_product]
                    if not product_data.empty:
                        melted_data = product_data.melt(id_vars=["Product", "SKU"], var_name="Competitor", value_name="Price")
                        for column in melted_data.columns:
                            if 'Price' in column:
                                melted_data[column] = melted_data[column].astype(str).apply(extract_price)
                        melted_data = melted_data.dropna(subset=["Price"])
                        melted_data.sort_values(by="Price", ascending=True, inplace=True)
                        st.write(f"Showing price comparison for `{st.session_state.selected_product}`:")
                        fig = px.bar(
                            melted_data,
                            x="Competitor",
                            y="Price",
                            color="Competitor",
                            title=f"Price Comparison for {st.session_state.selected_product}",
                            text="Price"
                        )
                        st.plotly_chart(fig)

            with tab3:
                folder_path = brand_directory
                file_pattern = os.path.join(folder_path, f"{st.session_state.selected_brand}_Prices_*.xlsx")
                all_files = sorted([f for f in glob.glob(file_pattern)])
                combined_df = []
                for file in all_files:
                    try:
                        date_str = file.split("_")[-1].replace(".xlsx", "").strip()
                        date = datetime.strptime(date_str, "%d-%m-%Y")
                    except ValueError:
                        print(f"Skipping file with invalid date format: {file}")
                        continue
                    df_temp = pd.read_excel(file, dtype=str)
                    df_temp.columns = df_temp.columns.str.strip().str.lower()
                    df_temp["date"] = date
                    combined_df.append(df_temp)
                if combined_df:
                    df_all = pd.concat(combined_df, ignore_index=True)
                    df_long = df_all.melt(id_vars=["sku", "product", "date"],
                                          var_name="website", value_name="price")
                    df_long["price_numeric"] = df_long["price"].astype(str).apply(extract_price)
                    df_long = df_long.dropna(subset=["price"])
                    selected_product = st.session_state.selected_product
                    avg_price_trend = df_long[df_long["product"] == selected_product].groupby("date")["price_numeric"].mean().reset_index()
                    avg_price_trend["product"] = selected_product
                    st.write(f"📈 Average Price Trend for `{selected_product}` over time: ")
                    fig = px.line(avg_price_trend, x="date", y="price_numeric", title=f"Average Price Trend for {selected_product}", hover_data= ["price_numeric"], 
                                  markers=True, labels={"date": "Date", "price_numeric": "Price in £"}, hover_name="product")
                    st.plotly_chart(fig)
        else:
            components.html(
                """
                <!DOCTYPE html>
                <html>
                <head>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                * {box-sizing: border-box;}
                body {font-family: Verdana, sans-serif;}
                .mySlides {display: none;}
                img {vertical-align: middle; width: 100%; border-radius: 10px;}
                .slideshow-container {max-width: 800px; position: relative; margin: auto; padding-top: 40px;}
                .title-text {color: #ffffff; font-size: 24px; font-weight: bold; padding: 12px; position: absolute; top: 0; width: 100%; text-align: center; background-color: rgba(0, 0, 0, 0.5); border-top-left-radius: 10px; border-top-right-radius: 10px;}
                .dot {height: 15px; width: 15px; margin: 0 2px; background-color: #bbb; border-radius: 50%; display: inline-block; transition: background-color 0.6s ease;}
                .active {background-color: #717171;}
                .fade {animation-name: fade; animation-duration: 1.5s;}
                @keyframes fade {from {opacity: 0.001} to {opacity: 1}}
                </style>
                </head>
                <body>
                <div class="slideshow-container">
                    <div class="mySlides fade"><div class="title-text">Celotex</div><img src="https://www.building-supplies-online.co.uk/cdn/shop/files/walls_-_external_wall_insulation_-_timber_frame_walls_1.png?v=1737114043&width=1946"></div>
                    <div class="mySlides fade"><div class="title-text">Recticel</div><img src="https://www.building-supplies-online.co.uk/cdn/shop/files/Eurothane_20gp_11_1.jpg"></div>
                    <div class="mySlides fade"><div class="title-text">Ecotherm</div><img src="//build4less.co.uk/cdn/shop/files/Untitleddesign-2024-03-22T094324.755_64d98e44-6e84-46e8-8385-f6acb6837e9f.png?v=1711108001&width=1946"></div>
                </div>
                <br>
                <div style="text-align:center"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
                <script>
                let slideIndex = 0; showSlides();
                function showSlides() {
                    let i;
                    let slides = document.getElementsByClassName("mySlides");
                    let dots = document.getElementsByClassName("dot");
                    for (i = 0; i < slides.length; i++) {slides[i].style.display = "none";}
                    slideIndex++;
                    if (slideIndex > slides.length) {slideIndex = 1}    
                    for (i = 0; i < dots.length; i++) {dots[i].className = dots[i].className.replace(" active", "");}
                    slides[slideIndex-1].style.display = "block";  
                    dots[slideIndex-1].className += " active";
                    setTimeout(showSlides, 6000);
                }
                </script>
                </body>
                </html>
                """,
                height=650,
            )
    else:
        st.markdown(
            """
            <div style="display: flex; justify-content: center; align-items: center; height: 100px;">
                <p style="background-color: #FFDDDD; color: red; padding: 15px; font-size: 18px; font-weight: bold; border-radius: 10px;">
                    ❌ Data for the selected date is not available. 
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
