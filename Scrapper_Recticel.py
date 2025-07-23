import pandas as pd # type: ignore
from bs4 import BeautifulSoup # type: ignore
import requests # type: ignore
import time
import re
from selenium.webdriver.support.ui import Select # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium import webdriver # type: ignore
from datetime import datetime

def scrape_online_insulation_sales(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_div = soup.find("p", class_ = "price")
        price_element = price_div.find("span", class_ = "woocommerce-Price-amount amount").text.strip()
        if price_element:
            if "eurowall" in url and "90mm" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*5, 2)
                return f"£{price_element}"
            elif "eurowall" in url and "115mm" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*5, 2)
                return f"£{price_element}"
            elif "eurowall" in url and "140mm" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*4, 2)
                return f"£{price_element}"
            return price_element
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

# Function to scrape ex-VAT price from Building Materials
def scrape_building_materials(url, series):
    try:
        print(f"Processing URL {url}")
        driver = webdriver.Chrome()
        driver.get(url)  
        thickness_div = driver.find_element(By.ID, "attribute1999")
        if thickness_div:
            thickness_div.click()
            time.sleep(5)
            select = Select(thickness_div)
            for option in select.options:
                select.select_by_visible_text(option.text)
                if option.text == "Choose an Option...":
                    continue
                updated_html = driver.page_source
                s1 = BeautifulSoup(updated_html, "html.parser") 
                title = s1.find("h1", class_ = re.compile("page-title")).text.strip() 
                if series in title:
                    price_element = s1.find_all("span", class_ = "price-wrapper")[1].text.strip().split()[0]
                    break
        if price_element:
            return price_element
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'
    finally:
        driver.quit()

# Function to scrape ex-VAT price from Insulation Superstore
def scrape_insulation_superstore(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("strong", class_ = re.compile("ex-vat"))
        if price_element:
            if soup.find("span", class_ = "rrp-price"):    
                return f"{price_element.text.strip()}-Sale Price"+ " old price: "+ soup.find("span", class_ = "rrp-price").text.strip()
            else:
                return price_element.text.strip()
        else:
            return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

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
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'
    
def scrape_b4l(url):
    try:
        print(f"Processing URL {url}")
        time.sleep(3)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_div = soup.find("div", class_ = "price__regular")
        price_element = price_div.find("span", class_ = re.compile("exc_vat_price"))
        if price_element:
            return price_element.text.strip()
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'
    
def scrape_bso(url):
    try:
        print(f"Processing URL {url}")
        time.sleep(3)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("span", class_ = re.compile("exc_vat_price"))  # Replace with actual class or ID
        if price_element:
            return price_element.text.strip()
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulationhub(url):
    print(f"Processing URL {url}")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit() 
    try:
        price_div = soup.find("div", class_ = "price-wrapper")
        price_elements = price_div.find_all("span", class_ = "woocommerce-Price-amount amount")
        if len(price_elements) > 2:
            price_element = price_elements[2].text.strip()
            old_price = float(price_elements[0].text.strip().replace("£", ""))
            return f"{price_element} presale price: £{round(old_price/1.2, 2)}"
        else:
            price_element = price_elements[1]
            return price_element.text.strip()
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_planetinsulation(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("span", class_ = "price-item price-item--sale price-item--last")  # Replace with actual class or ID
        if price_element:
            return price_element.text.strip()
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulationonline(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("span", class_ = "woocommerce-Price-amount amount")  
        if price_element:
            return price_element.text.strip()
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
        price_div = soup.find("div", class_ = "product-price-group")
        price_element = price_div.find("div", class_ = "product-price").text.split()[1].strip()
        if price_element == "Price:":
            price_elements = soup.find("div", class_ = "product-price").text.split()[2].strip()
            if "90mm" in url and "eurowall" in url:
                price_elements = price_elements.replace("£", "")
                price_elements = round(float(price_elements)*50, 2)
                return f'£{price_elements}'
            elif "115mm" in url and "eurowall" in url:
                price_elements = price_elements.replace("£", "")
                price_elements = round(float(price_elements)*40, 2)
                return f'£{price_elements}'
            elif "140mm" in url and "eurowall" in url:
                price_elements = price_elements.replace("£", "")
                price_elements = round(float(price_elements)*32, 2)
                return f'£{price_elements}'            
            return price_elements
        else: 
            if "90mm" in url and "eurowall" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*50, 2)
                return f'£{price_element}'
            elif "115mm" in url and "eurowall" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*40, 2)
                return f'£{price_element}'
            elif "140mm" in url and "eurowall" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*32, 2)
                return f'£{price_element}'
            return price_element
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_directinsulation(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("span", attrs={"data-hook": "formatted-primary-price"}) 
        if price_element:
            return price_element.text.strip()
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulationbee(url):
    print(f"Processing URL {url}")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    try:
        price_element = soup.find("span", id = "price-old")
        if price_element:
            return price_element.text.split()[0].strip()
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
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
            if "plus" in url and "90mm" in url: 
                price_element = price_element.replace("£", "")
                price_element =  round(float(price_element)*5, 2)
                return f"£{price_element}"
            elif "plus" in url and "115mm" in url:
                price_element = price_element.replace("£", "")
                price_element =  round(float(price_element)*5, 2)
                return f"£{price_element}"
            elif "plus" in url and "140mm" in url:
                price_element = price_element.replace("£", "")
                price_element =  round(float(price_element)*4, 2)
                return f"£{price_element}"
            return price_element
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
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
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulationuk(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("strong", class_ = "price__current js-price-without-vat") .text.split()[0].strip()
        if price_element:
            if "cavity-wall-insulation" in url and "90mm" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*5, 2)
                return f"£{price_element}"
            elif "cavity-wall-insulation" in url and "115mm" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*5, 2)
                return f"£{price_element}"
            elif "cavity-wall-insulation" in url and "140mm" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*4, 2)
                return f"£{price_element}"
            return price_element
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulationwholesale(url):
    print(f"Processing URL {url}")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    try:
        price_div = soup.find("span", class_ = "price")
        price_element = price_div.find("span", class_ = "woocommerce-Price-amount amount")
        if price_element:
            return price_element.text.strip()
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_diybuildingsupplies(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        price_tag = soup.find("div", class_="price__default")
        price_current = price_tag.find("strong", class_="price__current").text.split()[0].strip()
        price_was_tag = price_tag.find("s", class_="price__was")
        price_was = price_was_tag.text.strip() if price_was_tag else ""

        price_value = float(price_current.replace("£", ""))

        # Define conditions and their multipliers
        conditions = [
            (["90mm", "eurowall"], 5),
            (["115mm", "eurowall"], 5),
            (["140mm", "eurowall"], 5.34),
            (["50mm", "eurowall", "cavity-wall"], 3.34),
            (["100mm", "eurowall", "cavity-wall"], 1.67),
        ]

        for keywords, multiplier in conditions:
            if all(keyword in url.lower() for keyword in keywords):
                adjusted_price = round(price_value * multiplier, 2)
                return f"£{adjusted_price}"

        # Return based on presence of sale price
        if not price_was:
            return price_current
        else:
            return f"{price_current} Pre Sale Price-{price_was}"

    except AttributeError:
        return "POA or OOS"
    except Exception as e:
        return f"Error: {str(e)}"
        
df = pd.read_excel(r"C:\Users\Priyanka\Documents\Search_for_product_on_Competitor's\Celotex & Recticel Links.xlsx", sheet_name="Recticel")

result_data = []
for index, row in df.iterrows():
    sku = row["SKU"]
    product = row["Products"]
    series = row["Series"]
    scraped_prices = {
        "I4L": scrape_i4l(row["I4L"]) if pd.notna(row["I4L"]) else 'N/L',
        "B4L": scrape_b4l(row["B4L"]) if pd.notna(row["B4L"]) else 'N/L',
        "BSO": scrape_bso(row["BSO"]) if pd.notna(row["BSO"]) else 'N/L',
        "Insulation Superstore": scrape_insulation_superstore(row["Insulation Superstore"]) if pd.notna(row["Insulation Superstore"]) else 'N/L',
        "Materials Market": scrape_materialmarket(row["Materials Market"]) if pd.notna(row["Materials Market"]) else 'N/L',
        "Trade Insulations": scrape_tradeinsulation(row["Trade Insulations"]) if pd.notna(row["Trade Insulations"]) else 'N/L',
        "Insulation Wholesale": scrape_insulationwholesale(row["Insulation Wholesale"]) if pd.notna(row["Insulation Wholesale"]) else 'N/L',
        "Insulation Hub": scrape_insulationhub(row["Insulation Hub"]) if pd.notna(row["Insulation Hub"]) else 'N/L',
        "InsulationUK": scrape_insulationuk(row["InsulationUK"]) if pd.notna(row["InsulationUK"]) else 'N/L',
        "Online Insulation Sales": scrape_online_insulation_sales(row["Online Insulation Sales"]) if pd.notna(row["Online Insulation Sales"]) else 'N/L',
        "Building Materials": scrape_building_materials(row["Building Materials"], series) if pd.notna(row["Building Materials"]) else 'N/L',
        "Insulation Online": scrape_insulationonline(row["Insulation Online"]) if pd.notna(row["Insulation Online"]) else 'N/L',
        "Planet Insulation": scrape_planetinsulation(row["Planet Insulation"]) if pd.notna(row["Planet Insulation"]) else 'N/L',
        "Insulation Shop": scrape_insulationshop(row["Insulation Shop"]) if pd.notna(row["Insulation Shop"]) else 'N/L',
        "Building Materials Direct": scrape_directinsulation(row["Building Materials Direct"]) if pd.notna(row["Building Materials Direct"]) else 'N/L',
        "Insulation Bee": scrape_insulationbee(row["Insulation Bee"]) if pd.notna(row["Insulation Bee"]) else 'N/L',
        "DIY Building Supplies": scrape_diybuildingsupplies(row["DIY Building supplies"]) if pd.notna(row["DIY Building supplies"]) else 'N/L'
    }
    
    result_data.append({"SKU": sku, "Product": product, **scraped_prices})
        
result_df = pd.DataFrame(result_data)
current_date = datetime.now().strftime("%d-%m-%Y")  
output_file_name = f"C:\\Users\\Priyanka\\Documents\\Price_Comp_Dashboard\\Compititor's_Price\\Recticel_Prices\\Recticel_Prices_{current_date}.xlsx"
result_df.to_excel(output_file_name,index=False)
result_df
