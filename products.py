from mimetypes import guess_extension
import os
import requests
import json
from multiprocessing.pool import ThreadPool as Pool

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'x-v': '3'}

brand_size = 10

def get_data(url):
    r = requests.get(url, headers=headers)
    response = r.json()

    if 'links' in response and 'next' in response['links'] and response['links']['next'] != None:
        temp = get_data(response['links']['next'])
        response['data']['products'].extend(temp['data']['products'])
    
    if 'links' in response:
        del response['links']

    if 'meta' in response:
        del response['meta']

    return response


# https://stackoverflow.com/a/25851972/9389353
def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def process_brand(brand):
    try:
        response = get_data(brands[brand]['publicBaseUri'].rstrip('/') + "/cds-au/v1/banking/products")

        skip_update = False

        try:
            for file in os.listdir('brands/products/'):
                if file == (brand + ".json"):
                    raw_file = open("brands/products/"+file, "r")
                    response_compare = json.load(raw_file)
                    raw_file.close()
                    if ordered(response) == ordered(response_compare):
                        skip_update = True

        except Exception as e:
            print(e)

        path = 'brands/products/' + brand + ".json"

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
for brand in brands:
    brand_pool.apply_async(process_brand, (brand,))

brand_pool.close()
brand_pool.join()
