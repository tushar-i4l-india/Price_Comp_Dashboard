import streamlit as st
import pandas as pd
import os
import plotly.express as px 
from datetime import datetime, timedelta
import re

st.set_page_config(page_title="Price Comparison Dashboard", page_icon= ":bar_chart:",layout="wide", menu_items={'Get Help': 'https://insulation4less.co.uk/pages/contact-us', 
                                                                                                  'Report a bug': "https://www.insulation4less.co.uk", 
                                                                                                  'About': "This app is a price comparison dashboard",})
# Function to load data
@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    return df
# Function to get the numerical price with string
def extract_price(price):
    if isinstance(price, str):
        if "price not found" in price.lower() or "no link" in price.lower() or price.lower().startswith("error:"):
            return None
        match = re.search(r"[\d,.]+", price)
        if match:
            return float(match.group().replace(",", ""))
    return None
# Function to apply background colors and arrows dynamically
def highlight_changes(row):
    styles = []
    for col in website_columns:
        today_price = extract_price(row[col])
        prev_col = col + "_yesterday"

        prev_price_str = df_merged.loc[row.name, prev_col] if prev_col in df_merged.columns else None
        prev_price = extract_price(prev_price_str)

        # Default style (no change)
        style = ""

        # Price increased: Light Red background with Dark Red text
        if today_price is not None and prev_price is not None and today_price > prev_price:
            # style = "background-color: #ffcccc; color: darkred; font-weight: bold;"
            style = "color: red; font-weight: bold;"

        # Price decreased: Light Green background with Dark Green text
        elif today_price is not None and prev_price is not None and today_price < prev_price:
            # style = "background-color: #ccffcc; color: darkgreen; font-weight: bold;"
            style = "color: green; font-weight: bold;"

        # Price unchanged: Light Blue background
        elif today_price is not None and prev_price is not None and today_price == prev_price:
            # style = "background-color: #e6f2ff; color: blue; font-weight: bold;"
            style = "color: blue; font-weight: bold;"

        styles.append(style)

    return styles

# Set the base directory containing brand directories
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

# Streamlit app
st.sidebar.title("Price Comparison Dashboard 💷")

brands = ["Celotex", "Recticel", "Ecotherm", "Unilin"]
st.session_state.selected_brand = st.sidebar.selectbox("Select Brand", brands)

if st.session_state.selected_brand:
    # Construct the directory path for the selected brand
    brand_directory = os.path.join(base_directory, f"{st.session_state.selected_brand}_Prices")

    # List available files (dates) for the selected brand
    files = [f for f in os.listdir(brand_directory) if f.endswith(".xlsx")]
    
    dates = sorted([datetime.strptime(f.split("_")[-1].replace(".xlsx", ""), "%d-%m-%Y") for f in files], reverse=True)
    st.session_state.selected_date = st.sidebar.date_input("Select Date", value=max(dates).date() if dates else datetime.today().date(),
                                                    min_value=min(dates).date() if dates else datetime.today().date()) # , max_value=datetime.today().date()
    # st.session_state.selected_date = st.selectbox("Select Date", dates)
    st.session_state.selected_date = st.session_state.selected_date.strftime("%d-%m-%Y")
            # Construct the file path for the selected date
    file_name = f"{st.session_state.selected_brand}_Prices_{st.session_state.selected_date}.xlsx"
    data_path = os.path.join(brand_directory, file_name)
    if st.session_state.selected_date and os.path.exists(data_path):
        selected_date_obj = datetime.strptime(st.session_state.selected_date, "%d-%m-%Y")
        previous_date_obj = selected_date_obj - timedelta(days=1)
        previous_date_str = previous_date_obj.strftime("%d-%m-%Y") # get the date before the selected date 
        st.session_state.previous_date_str = previous_date_str
        prev_file_name = f"{st.session_state.selected_brand}_Prices_{st.session_state.previous_date_str}.xlsx"
        prev_data_path = os.path.join(brand_directory, prev_file_name)
        # Load data
        if st.sidebar.button("Preview Data") or st.session_state.data_loaded:
            st.session_state.data_loaded = True
            # Display data
            df = load_data(data_path)
            st.write(f"### Price list for `{st.session_state.selected_brand}`")
            website_columns = df.columns[2:]
            try:
                prev_df = load_data(prev_data_path)
                df_merged = df.merge(prev_df, on=["SKU", "Product"], how="left", suffixes=("_today", "_yesterday"))
                # Rename columns for readability
                df_display = df_merged[["SKU", "Product"] + [col + "_today" for col in website_columns]].copy()
                
                rename_dict = {col + "_today": col for col in website_columns}
                df_display.rename(columns=rename_dict, inplace=True)
                
                # Apply styling to the dataframe
                styled_df = df_display.style.apply(highlight_changes, axis=1, subset=website_columns)

                # Adding arrows directly into the dataframe as new columns
                for col in website_columns:
                    df_display[col] = df_display[col].astype(str)  # Ensure it's string type for concatenation
                    df_display[col + "_Arrow"] = ""

                    for index, row in df_display.iterrows():
                        today_price = extract_price(row[col])
                        prev_col = col + "_yesterday"

                        prev_price_str = df_merged.loc[index, prev_col] if prev_col in df_merged.columns else None
                        prev_price = extract_price(prev_price_str)

                        # Adding arrows based on price changes
                        if today_price is not None and prev_price is not None:
                            if today_price > prev_price:
                                df_display.at[index, col + "_Arrow"] = "🔺"
                            elif today_price < prev_price:
                                df_display.at[index, col + "_Arrow"] = "🔻"

                # Merge arrow columns with price columns for display
                for col in website_columns:
                    df_display[col] = df_display[col] + " " + df_display[col + "_Arrow"]
                    df_display.drop(columns=[col + "_Arrow"], inplace=True)

                
                # Display styled dataframe in Streamlit
                st.dataframe(styled_df, hide_index=True, height=400)
            except:
                # Display normal dataframe in Streamlit
                st.dataframe(df, hide_index=True, height=400)
            # Select product
            products = df["Product"].unique()
            st.session_state.selected_product = st.sidebar.selectbox("Select Product", products)

            if st.session_state.selected_product:
                # Filter data for the selected product
                product_data = df[df["Product"] == st.session_state.selected_product]

                if not product_data.empty:
                    melted_data = product_data.melt(id_vars=["Product", "SKU"], var_name="Competitor", value_name="Price")
                    st.write(f"Showing price comparison for `{st.session_state.selected_product}`:")
                    for column in melted_data.columns:
                        if 'Price' in column :
                            melted_data[column] = melted_data[column].astype(str).apply(extract_price)
                    melted_data = melted_data.dropna(subset=["Price"])
                    melted_data.sort_values(by = "Price", ascending= True, inplace = True)
                    
                    fig = px.bar(
                        melted_data,
                        x="Competitor",
                        y="Price",
                        color="Competitor",
                        title=f"Price Comparison for {st.session_state.selected_product}",
                        text = "Price",
                        # barmode="group"
                    )
                    st.plotly_chart(fig)
        else:
            import streamlit.components.v1 as components
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

                /* Slideshow container */
                .slideshow-container {
                    max-width: 800px;
                    position: relative;
                    margin: auto;
                    padding-top: 40px;
                }

                /* Title text (top of image) */
                .title-text {
                    color: #ffffff;
                    font-size: 24px;
                    font-weight: bold;
                    padding: 12px;
                    position: absolute;
                    top: 0;
                    width: 100%;
                    text-align: center;
                    background-color: rgba(0, 0, 0, 0.5);
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                }

                /* Dots */
                .dot {
                    height: 15px;
                    width: 15px;
                    margin: 0 2px;
                    background-color: #bbb;
                    border-radius: 50%;
                    display: inline-block;
                    transition: background-color 0.6s ease;
                }

                .active {
                    background-color: #717171;
                }

                .fade {
                    animation-name: fade;
                    animation-duration: 1.5s;
                }

                @keyframes fade {
                    from {opacity: 0.001} 
                    to {opacity: 1}
                }

                </style>
                </head>
                <body>

                <div class="slideshow-container">

                    <div class="mySlides fade">
                        <div class="title-text">Celotex</div>
                        <img src="https://www.building-supplies-online.co.uk/cdn/shop/files/walls_-_external_wall_insulation_-_timber_frame_walls_1.png?v=1737114043&width=1946">
                    </div>
                    
                    <div class="mySlides fade">
                        <div class="title-text">Recticel</div>
                        <img src="https://www.building-supplies-online.co.uk/cdn/shop/files/Eurothane_20gp_11_1.jpg">
                    </div>

                    <div class="mySlides fade">
                        <div class="title-text">Ecotherm</div>
                        <img src="//build4less.co.uk/cdn/shop/files/Untitleddesign-2024-03-22T094324.755_64d98e44-6e84-46e8-8385-f6acb6837e9f.png?v=1711108001&width=1946">
                    </div>

                </div>
                <br>

                <div style="text-align:center">
                    <span class="dot"></span> 
                    <span class="dot"></span> 
                    <span class="dot"></span> 
                </div>

                <script>
                let slideIndex = 0;
                showSlides();

                function showSlides() {
                    let i;
                    let slides = document.getElementsByClassName("mySlides");
                    let dots = document.getElementsByClassName("dot");
                    for (i = 0; i < slides.length; i++) {
                        slides[i].style.display = "none";  
                    }
                    slideIndex++;
                    if (slideIndex > slides.length) {slideIndex = 1}    
                    for (i = 0; i < dots.length; i++) {
                        dots[i].className = dots[i].className.replace(" active", "");
                    }
                    slides[slideIndex-1].style.display = "block";  
                    dots[slideIndex-1].className += " active";
                    setTimeout(showSlides, 6000); // Change image every 2 seconds
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