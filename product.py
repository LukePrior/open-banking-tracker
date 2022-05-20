from mimetypes import guess_extension
import os
import requests
import json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'x-v': '3'}

def get_data(url):
    r = requests.get(url, headers=headers)
    response = r.json()

    return response

raw_file = open("brands/brands.json", "r")
brands = json.load(raw_file)
raw_file.close()

changed_product = 0

for file in os.listdir('brands/products/'):
    try:
        id = file.replace(".json","")

        raw_file = open("brands/products/"+file, "r")
        brand = json.load(raw_file)
        raw_file.close()

        if id not in brands:
            break

        if 'data' not in brand:
            break

        folder = "brands/product/" + id
        if not os.path.exists(folder):
            os.makedirs(folder)

        for product in brand['data']['products']:
            url = (brands[id]['productReferenceDataApi'] + "/" + product['productId'])

            response = get_data(url)

            flag = False

            try:
                for file in os.listdir('brands/product/' + id):
                    if file == (product['productId'] + ".json"):
                        flag = True
                        raw_file = open("brands/product/"+id+"/"+file, "r")
                        response_compare = json.load(raw_file)
                        raw_file.close()
                        if response != response_compare:
                            changed_product += 1

            except Exception as e:
                print(e)

            if flag == False:
                changed_product += 1

            path = 'brands/product/' + id + "/" + product['productId'] + ".json"

            raw_file = open(path, "w")
            json.dump(response, raw_file, indent = 4)
            raw_file.close()

            print(path)

    except Exception as e:
        print(e)

stats = {}
stats['changed_product'] = changed_product

raw_file = open("stats.json", "w")
json.dump(stats, raw_file, indent = 4)
raw_file.close()