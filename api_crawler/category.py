import requests
import json

url = "https://papi.fptshop.com.vn/gw/v1/public/fulltext-search-service/category"

skipCount = 0
maxResultCount = 50

payload = json.dumps({
    "skipCount": skipCount,
    "maxResultCount": maxResultCount,
    "sortMethod": "noi-bat",
    "slug": "dien-thoai",
    "categoryType": "category"
})

headers = {
	'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

data = json.loads(response.text)

totalCount = data.get('totalCount')

while (skipCount + maxResultCount) < totalCount:
    skipCount += maxResultCount
    payload = json.dumps({
        "skipCount": skipCount,
        "maxResultCount": maxResultCount,
        "sortMethod": "noi-bat",
        "slug": "dien-thoai",
        "categoryType": "category"
    })
    response = requests.request("POST", url, headers=headers, data=payload)
    reponse_json = json.loads(response.text)
    data['items'].extend(reponse_json['items'])

print('Number of items cralwed: ', len(data['items']), '/', totalCount)

with open('category.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
