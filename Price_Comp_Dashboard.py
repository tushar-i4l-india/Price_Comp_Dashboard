import streamlit as st
import pandas as pd
import os
import plotly.express as px 
from datetime import datetime

st.set_page_config(page_title="Competitor Price Comparison Dashboard", layout="wide", menu_items={'Get Help': 'https://www.extremelycoolapp.com/help', 
                                                                                                  'Report a bug': "https://www.extremelycoolapp.com/bug", 
                                                                                                  'About': "# This is a header. This is an *extremely* cool app!"})
# Function to load data
@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    return df

# Set the base directory containing brand directories
# base_directory = r"C:\Users\Priyanka\Documents\Search_for_product_on_Competitor's\Compititor's_Price"
base_directory = os.path.join(os.getcwd(), "Compititor's_Price")

if 'selected_brand' not in st.session_state:
    st.session_state.selected_brand = None
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None

# Streamlit app
st.title("Price Comparison Dashboard 💷")

col1, col2 = st.columns(2)
with col1:
    brands = ["Celotex", "Recticel"]
    st.session_state.selected_brand = st.selectbox("Select Brand", brands)

if st.session_state.selected_brand:
    # Construct the directory path for the selected brand
    brand_directory = os.path.join(base_directory, f"{st.session_state.selected_brand}_Prices")

    # List available files (dates) for the selected brand
    files = [f for f in os.listdir(brand_directory) if f.endswith(".xlsx")]
    
    with col2:
        dates = [f.split("_")[-1].replace(".xlsx", "") for f in files]
        dates = sorted(dates, key=lambda x: datetime.strptime(x, "%d-%m-%Y"), reverse=True)
        st.session_state.selected_date = st.selectbox("Select Date", dates)

    if st.session_state.selected_date:
        # Construct the file path for the selected date
        file_name = f"{st.session_state.selected_brand}_Prices_{st.session_state.selected_date}.xlsx"
        data_path = os.path.join(brand_directory, file_name)
        # Load data
        
        if st.button("Preview Data") or st.session_state.data_loaded:
            st.session_state.data_loaded = True
            # Display data
            df = load_data(data_path)
            st.write(f"### Price list for `{st.session_state.selected_brand}`")
            st.dataframe(df, hide_index=True)

            # Select product
            products = df["Product"].unique()
            st.session_state.selected_product = st.selectbox("Select Product", products)

            if st.session_state.selected_product:
                # Filter data for the selected product
                product_data = df[df["Product"] == st.session_state.selected_product]

                # Visualization
                # st.subheader(f"Price Comparison for {selected_product}")

                # chart_type = st.radio("Select Chart Type", ("Bar Chart", "Pie Chart"))

                # if chart_type == "Bar Chart":
                #     st.bar_chart(product_data.set_index("Competitor")["Price"])
                # elif chart_type == "Pie Chart":
                #     st.write(product_data.set_index("Competitor")["Price"].plot.pie(autopct="%1.1f%%"))
                #     st.pyplot()
                if not product_data.empty:
                    melted_data = product_data.melt(id_vars=["Product", "SKU"], var_name="Competitor", value_name="Price")
                    st.write(f"Showing price comparison for `{st.session_state.selected_product}`:")
                    melted_data["Price"] = melted_data["Price"].replace({'[£,]': '', 'Price Not Found': '0'}, regex=True)
                    melted_data["Price"] = pd.to_numeric(melted_data["Price"], errors='coerce')
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