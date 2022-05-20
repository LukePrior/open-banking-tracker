from mimetypes import guess_extension
import os
import requests
import json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'x-v': '3'}

raw_file = open("brands/brands.json", "r")
brands = json.load(raw_file)
raw_file.close()

changed_products = 0

for brand in brands:
    try:
        r = requests.get(brands[brand]['productReferenceDataApi']+'?page-size=1000', headers=headers)
        response = r.json()
        path = 'brands/products/' + brand + ".json"
        raw_file = open(path, "w")
        json.dump(response, raw_file, indent = 4)
        raw_file.close()
        changed_products += 1
    except Exception as e:
        print(e)

stats = {}
stats['changed_products'] = changed_products

raw_file = open("stats.json", "w")
json.dump(stats, raw_file, indent = 4)
raw_file.close()