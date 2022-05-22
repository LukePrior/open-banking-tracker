from mimetypes import guess_extension
import os
import requests
import json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'x-v': '3'}

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

raw_file = open("brands/brands.json", "r")
brands = json.load(raw_file)
raw_file.close()

changed_products = 0

for brand in brands:
    try:
        response = get_data(brands[brand]['productReferenceDataApi'])

        flag = False
        skip_update = False

        try:
            for file in os.listdir('brands/products/'):
                if file == (brand + ".json"):
                    flag = True
                    raw_file = open("brands/products/"+file, "r")
                    response_compare = json.load(raw_file)
                    raw_file.close()
                    if response != response_compare:
                        changed_products += 1
                    else:
                        skip_update = True

        except Exception as e:
            print(e)

        if flag == False:
            changed_products += 1

        if (skip_update == False):
            path = 'brands/products/' + brand + ".json"
            raw_file = open(path, "w")
            json.dump(response, raw_file, indent = 4)
            raw_file.close()

        print(path)

    except Exception as e:
        print(e)


stats = {}
stats['changed_files'] = changed_products

raw_file = open("stats.json", "w")
json.dump(stats, raw_file, indent = 4)
raw_file.close()