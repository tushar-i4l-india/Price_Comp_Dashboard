import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ========== SCRAPER FUNCTIONS ==========
def scrape_i4l(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("span", class_=re.compile("exc_vat_price"))
        return price_element.text.strip() if price_element else 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_b4l(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_div = soup.find("div", class_="price__regular")
        price_element = price_div.find("span", class_=re.compile("exc_vat_price")) if price_div else None
        return price_element.text.strip() if price_element else 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_bso(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("span", class_=re.compile("exc_vat_price"))
        return price_element.text.strip() if price_element else 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulation_superstore(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("strong", class_=re.compile("ex-vat"))
        return price_element.text.strip() if price_element else 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_materialmarket(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_wrapper = soup.find("span", class_="c-product-information__price col l12 s6")
        if price_wrapper:
            raw_price = price_wrapper.find("span")["data-product-price-single-unit"]
            price = float(raw_price)
            if "xr4165" in url or "xr4200" in url:
                return f"£{round(price * 12, 2)}"
            elif "thermaclass" in url:
                return f"£{round(price * 16, 2)}"
            return f"£{price}"
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_tradeinsulation(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.find("p", class_="price")
        price_elements = price_tag.find_all("span", class_="woocommerce-Price-amount amount")
        price_text = price_elements[1].text if len(price_elements) > 1 else price_elements[0].text
        price_value = float(price_text.replace("£", ""))
        if "165mm" in url or "200mm-celotex" in url:
            return f"£{round(price_value * 12, 2)}"
        elif "thermaclass" in url:
            return f"£{round(price_value * 16, 2)}"
        return f"£{price_value}"
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulationwholesale(url):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        price_div = soup.find("span", class_ = "price")
        price_element = price_div.find("span", class_ = "woocommerce-Price-amount amount").text.strip()
        if price_element:
            if "xr4165" in url or "xr4200" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*12, 2)
                return f'£{price_element}'
            elif "thermaclass" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*16, 2)
                return f'£{price_element}'
            return price_element
        else:
            return 'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'
    
def scrape_insulationhub(url):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        price_div = soup.find("div", class_="price-wrapper")
        price_elements = price_div.find_all("span", class_="woocommerce-Price-amount amount")
        if len(price_elements) > 2:
            new_price = price_elements[2].text.strip()
            old_price = float(price_elements[0].text.strip().replace("£", ""))
            return f"{new_price} presale price: £{round(old_price / 1.2, 2)}"
        else:
            price_element = price_elements[1].text.strip()
            if "xr4165" in url or "xr4200" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*12, 2)
                return f'£{price_element}'
            elif "thermaclass" in url and "90mm" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*96, 2)
                return f'£{price_element}'
            elif "thermaclass" in url and "115mm" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*80, 2)
                return f'£{price_element}'
            elif "thermaclass" in url and "140mm" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*64, 2)
                return f'£{price_element}'
            elif "cw4100" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*6, 2)
                return f'£{price_element}'   
            elif "cw4050" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*11, 2)
                return f'£{price_element}'    
            elif "cw4075" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*8, 2)
                return f'£{price_element}'
            return price_element if price_element else 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'
    
def scrape_insulationuk(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("strong", class_="price__current js-price-without-vat")
        return price_element.text.split()[0].strip() if price_element else 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'
    
def scrape_online_insulation_sales(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_div = soup.find("p", class_ = "price")
        price_element = price_div.find("span", class_ = "woocommerce-Price-amount amount").text.strip()
        if "thermaclass" in url:
            price_element = price_element.replace("£", "")
            price_element = round(float(price_element)*16, 2)
        return price_element if price_element else 'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'
    
def scrape_building_materials(url, series):
    try:
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
            if "CW4085" in title:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*16, 2)
                return f'£{price_element}'
            return price_element
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'
    finally:
        driver.quit()

# ========== SCRAPER MAPPING ==========
SCRAPERS = {
    "I4L": scrape_i4l,
    "B4L": scrape_b4l,
    "BSO": scrape_bso,
    "Insulation Superstore": scrape_insulation_superstore,
    "Materials Market": scrape_materialmarket,
    "Trade Insulations": scrape_tradeinsulation,
    "Insulation Wholesale": scrape_insulationwholesale,
    "Insulation Hub": scrape_insulationhub,
    "InsulationUK": scrape_insulationuk,
    "Building Materials" : scrape_building_materials,  
    "Online Insulation Sales": scrape_online_insulation_sales,
}

# ========== SCRAPE A ROW ==========
def scrape_row(row):
    sku = row["SKU"]
    product = row["Products"]
    series = row.get("Series", "")
    result = {"SKU": sku, "Product": product}
    for site, scraper in SCRAPERS.items():
        url = row.get(site, "")
        if pd.notna(url):
            try:
                if "Building Materials" in site:
                    result[site] = scraper(url, series)
                else:
                    result[site] = scraper(url)
            except Exception as e:
                result[site] = f"Error: {str(e)}"
        else:
            result[site] = "N/L"
    return result

# ========== MAIN EXECUTION ==========
input_file = r"C:\\Users\\Priyanka\\Documents\\Search_for_product_on_Competitor's\\Celotex & Recticel Links.xlsx"
df = pd.read_excel(input_file, sheet_name="Celotex")

result_data = []
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(scrape_row, row) for _, row in df.iterrows()]
    for future in as_completed(futures):
        result_data.append(future.result())

result_df = pd.DataFrame(result_data)
current_date = datetime.now().strftime("%d-%m-%Y")
output_file = fr"C:\\Users\\Priyanka\\Documents\\Search_for_product_on_Competitor's\\Compititor's_Price\\Celotex_Prices\\Celotex_Prices_{current_date}.xlsx"
result_df.to_excel(output_file, index=False)

print("Scraping complete. File saved:", output_file)
