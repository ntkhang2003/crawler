import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
import json
import os
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
API_CATEGORY = os.getenv('API_CATEGORY')
BASE_URL = os.getenv('BASE_URL')

def getData(skipCount = 0, slug = "dien-thoai", maxResultCount = 16):
    response = requests.post(API_CATEGORY, json={
        "skipCount": skipCount,
        "maxResultCount": maxResultCount,
        "sortMethod": "noi-bat",
        "slug": slug,
        "categoryType": "category"
    })
    if response.status_code != 200:
        return False
    return response.json()

def extract_data_from_script_with_keyword(url, keyword="Thông tin hàng hóa"):
    # Fetch the webpage
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all <script> tags
    script_tags = soup.find_all('script')
    
    for script in script_tags:
        if keyword in script.text:
            try:
                data = script.text.split("self.__next_f.push(")[1].replace('\\n', '').replace('\\', '')
                data = f"[{{\"groupName\":\"{keyword}\"" + data[:len(data)-1].split(f'{{"groupName":"{keyword}"')[1].split('},"productAttributeHighlight"')[0]
                return json.loads(data) 
            except:
                pass
    return None

def raw_to_table_data(raw_data, slug, keyword):
    data_fpt = []
    if raw_data:
        for item in tqdm(raw_data["items"]):
            list_item = item["skus"]

            link = BASE_URL + item["slug"]
            detail_raw = extract_data_from_script_with_keyword(link, keyword)
            detail = {}
            if detail_raw != None:
                for d in detail_raw:
                    att = {}
                    for a in d["attributes"]:
                        if a["value"] is not None:
                            att[a["displayName"]] = a["value"]
                    if att != {}:
                        detail[d["groupName"].replace("u0026", "và")] = att

            brand = item["brand"]["name"] if "brand" in item else ""
            productType = item["productType"]["name"] if "productType" in item else ""
            group = item["group"]["name"] if "group" in item else ""
            keySellingPoints = [f'{i["title"]} {i["description"]}' for i in item["keySellingPoints"]]
            promotions = [i["content"] for i in item["promotions"]]

            for data in list_item:
                # variant_info = {}
                # for i in range(len(data["variants"])):
                #     variant_info[data["variants"][i]["propertyName"]] = data["variants"][i]["displayValue"]

                data_fpt.append(
                    {
                        "sku": data["sku"] if "sku" in data else "",
                        "Tên": data["displayName"],
                        "Trạng thái": data["statusOnWeb"]["displayName"],
                        "Nhãn hàng": brand,
                        "Loại": productType,
                        "Nhóm": group,
                        "Đặc điểm nổi bật": keySellingPoints,
                        "Giá gốc": data["originalPrice"],
                        "Giá hiện tại": data["currentPrice"],
                        "Giảm giá": data["discountPercentage"],
                        "Thời gian kết thúc giảm giá": data["endTimeDiscount"],
                        "Khuyến mãi": promotions,
                        "Link đặt hàng": BASE_URL + data["slug"],
                        "Ảnh": data["image"],
                        "Màu": data["variants"][0]["displayValue"] if data["variants"] != [] else ""
                    }
                )
                # data_fpt[-1].update(variant_info)
                data_fpt[-1].update(detail)
    return data_fpt

def crawl_data(category, keyword):
    data_fpt = []
    slug = category
    data = getData(0, slug)
    data_fpt = data_fpt + raw_to_table_data(data,slug,keyword)
    for i in range(16, data['totalCount'], 16):
        print(i)
        res = getData(i, slug)
        data_fpt = data_fpt + raw_to_table_data(res,slug,keyword)
    return data_fpt

category_list = ["dien-thoai", "may-tinh-xach-tay",'may-tinh-bang',"smartwatch","phu-kien",'tivi','may-giat','robot-hut-bui','may-tinh-de-ban','man-hinh','may-lanh-dieu-hoa','tu-lanh','may-loc-nuoc','quat-dieu-hoa']
#sim-fpt , linh-kien, dien-gia-dung, may-doi-tra
keyword_list = ["Thông tin hàng hóa","Bộ xử lý","Thông tin hàng hóa","Thông tin hàng hóa","Thông tin hàng hóa","Thông tin hàng hóa","Thông tin hàng hóa","Thông tin hàng hóa",'Bộ xử lý',"Thông tin hàng hóa","Thông tin hàng hóa","Thông tin hàng hóa","Thông tin hàng hóa","Thông tin hàng hóa"]

for i in range(len(category_list)):
    print(f'###Start crawling: {category_list[i]}')
    try:
        data = crawl_data(category_list[i], keyword_list[i])
        df = pd.DataFrame(data)
        df.to_csv(f'./data/{category_list[i]}.csv', header=True, encoding='utf-8-sig')
    except:
        print(f'Error at {category_list[i]}, still continue to crawl')
        pass
    print(f'###Finish crawling: {category_list[i]}')

# test 1 sample
# data_fpt = []
# slug = "may-tinh-xach-tay"
# data = getData(256, slug, 16)
# data_fpt = data_fpt + raw_to_table_data(data,slug, "Bộ xử lý")
# df = pd.DataFrame(data_fpt)

# df.to_csv('./sample.csv', header=True, encoding='utf-8-sig')

# def crawl_1(i):
#     print(f'###Start crawling: {category_list[i]}')
#     data = crawl_data(category_list[i], keyword_list[i])
#     df = pd.DataFrame(data)
#     df.to_csv(f'./data/{category_list[i]}.csv', header=True, encoding='utf-8-sig')
#     print(f'###Finish crawling: {category_list[i]}')
# crawl_1(5)