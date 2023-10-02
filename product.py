from mimetypes import guess_extension
import os
import requests
import json
from multiprocessing.pool import ThreadPool as Pool

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'x-v': '4'}

brand_size = 10
product_size = 5

def get_data(url):
    r = requests.get(url, headers=headers)
    response = r.json()

    return response


# https://stackoverflow.com/a/25851972/9389353
def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj

def process_brand(file):
    id = file.replace(".json","")

    raw_file = open("brands/products/"+file, "r")
    brand = json.load(raw_file)
    raw_file.close()

    if 'data' not in brand:
        return

    folder = "brands/product/" + id
    if not os.path.exists(folder):
        os.makedirs(folder)

    product_pool = Pool(product_size)

    try:
        for product in brand['data']['products']:
            product_pool.apply_async(process_product, (product, id,))

    except Exception as e:
        print(e)

    product_pool.close()
    product_pool.join()


def process_product(product, id):
    try:
        url = (brands[id]['publicBaseUri'].rstrip('/') + "/cds-au/v1/banking/products/" + product['productId'])

        response = get_data(url)
        
        skip_update = False

        try:
            for file in os.listdir('brands/product/' + id):
                if file == (product['productId'] + ".json"):
                    flag = True
                    raw_file = open("brands/product/"+id+"/"+file, "r")
                    response_compare = json.load(raw_file)
                    raw_file.close()
                    if ordered(response) == ordered(response_compare):
                        skip_update = True

        except Exception as e:
            print(e)

        path = 'brands/product/' + id + "/" + product['productId'] + ".json"

        if (skip_update == False):
            raw_file = open(path, "w")
            json.dump(response, raw_file, indent = 4)
            raw_file.close()

        print(path)

    except Exception as e:
        print(e)


raw_file = open("brands/brands.json", "r")
brands = json.load(raw_file)
raw_file.close()

brand_pool = Pool(brand_size)
for file in os.listdir('brands/products/'):
    brand_pool.apply_async(process_brand, (file,))

brand_pool.close()
brand_pool.join()

for root, dirs, files in os.walk("brands/product/"):
    for file in files:
        try:
            brand = root.split("/")[2]
            id = os.path.splitext(file)[0]

            raw_file = open("brands/products/"+brand+".json", "r")
            products = json.load(raw_file)
            raw_file.close()

            if 'data' not in products or 'products' not in products['data']:
                continue

            found = False

            for product in products['data']['products']:
                if product['productId'] == id:
                    found = True
            
            if found is False:
                path = "brands/product/" + brand + "/" + file
                os.remove(path)

        except Exception as e:
            print(e)
