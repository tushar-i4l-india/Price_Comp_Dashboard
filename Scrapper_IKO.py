import pandas as pd 
from bs4 import BeautifulSoup 
import requests 
import time
import re
from selenium.webdriver.support.ui import Select 
from selenium.webdriver.common.by import By 
from selenium import webdriver 
from datetime import datetime


# Function to scrape ex-VAT price from I4L
def scrape_i4l(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("span", class_ = re.compile("exc_vat_price"))  
        if price_element:
            return price_element.text.strip()
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'
    
def scrape_b4l(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_div = soup.find("div", class_ = "price__regular")
        price_element = price_div.find("span", class_ = re.compile("exc_vat_price"))
        if price_element:
            return price_element.text.strip()
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'
    
def scrape_bso(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("span", class_ = re.compile("exc_vat_price"))  # Replace with actual class or ID
        if price_element:
            return price_element.text.strip()
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'
    
# Function to scrape ex-VAT price from Insulation Superstore
def scrape_insulation_superstore(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("strong", class_ = re.compile("ex-vat"))  
        if price_element:
            return price_element.text.strip()
        return 'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'
    
def scrape_materialmarket(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_elements = soup.find("span", class_ = "c-product-information__price col l12 s6") 
        price_element = price_elements.find("span")["data-product-price-single-unit"]
        if price_element:
            return f"£{price_element}"
        return 'Price Not Found'
    except AttributeError:
        return f"POA or OOS"
    except Exception as e:
        return f'Error: {str(e)}'
    
def scrape_tradeinsulation(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.find("p", class_ = "price") 
        price_elements = price_tag.find_all("span", class_ = "woocommerce-Price-amount amount")
        if len(price_elements) == 2:
            price_element = price_elements[1].text.strip()
        else:
            price_element = price_elements[0].text.strip()
        if price_element:
            return price_element
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulationwholesale(url, driver):
    print(f"Processing URL {url}")
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    try:
        price_div = soup.find("span", class_ = "price")
        price_element = price_div.find("span", class_ = "woocommerce-Price-amount amount").text.strip()
        if price_element:
            return price_element
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_online_insulation_sales(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_div = soup.find("p", class_ = "price")
        price_element = price_div.find("span", class_ = "woocommerce-Price-amount amount").text.strip()
        if price_element:
            return price_element
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulationshop(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("div", class_ = "product-price").text.split()[1].strip()
        if price_element == "Price:":
            price_element = soup.find("div", class_ = "product-price").text.split()[2].strip()
        return price_element
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

df = pd.read_excel(r"C:\Users\Priyanka\Documents\Search_for_product_on_Competitor's\Celotex & Recticel Links.xlsx", sheet_name="IKO")

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

result_data = []
for index, row in df.iterrows():
    sku = row["SKU"]
    product = row["Products"]
    series = row["Code"]
    scraped_prices = {
        "I4L": scrape_i4l(row["I4L"]) if pd.notna(row["I4L"]) else 'N/L',
        "B4L": scrape_b4l(row["B4L"]) if pd.notna(row["B4L"]) else 'N/L',
        "BSO": scrape_bso(row["BSO"]) if pd.notna(row["BSO"]) else 'N/L',
        "Insulation Superstore": scrape_insulation_superstore(row["Insulation Superstore"]) if pd.notna(row["Insulation Superstore"]) else 'N/L',
        "Materials Market": scrape_materialmarket(row["Materials Market"]) if pd.notna(row["Materials Market"]) else 'N/L',
        "Trade Insulations": scrape_tradeinsulation(row["Trade Insulations"]) if pd.notna(row["Trade Insulations"]) else 'N/L',
        "Insulation Wholesale": scrape_insulationwholesale(row["Insulation Wholesale"], driver) if pd.notna(row["Insulation Wholesale"]) else 'N/L',
        "Online Insulation Sales": scrape_online_insulation_sales(row["Online Insulation Sales"]) if pd.notna(row["Online Insulation Sales"]) else 'N/L',
        "Insulation Shop": scrape_insulationshop(row["Insulation Shop"]) if pd.notna(row["Insulation Shop"]) else 'N/L',
    }
    
    result_data.append({"SKU": sku, "Product": product, **scraped_prices})
driver.quit()   
result_df = pd.DataFrame(result_data)
current_date = datetime.now().strftime("%d-%m-%Y")  # Format: DD-MM-YYYY
output_file_name = f"C:\\Users\\Priyanka\\Documents\\Price_Comp_Dashboard\\Compititor's_Price\\IKO_Prices\\IKO_Prices_{current_date}.xlsx"
result_df.to_excel(output_file_name, index=False)
