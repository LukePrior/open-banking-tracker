import requests
import json

brands = {}

r = requests.get(
    'https://api.cdr.gov.au/cdr-register/v1/banking/data-holders/brands/summary', 
    headers={
        "x-v":"1",
        "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
    }
)

available_brands = r.json()

raw_file = open("brands/raw.json", "w")
json.dump(available_brands, raw_file, indent = 4)
raw_file.close()

available_brands = available_brands['data']

for brand in available_brands:
    brandId = ""
    if ('dataHolderBrandId' in brand or 'interimId' in brand):
        if ('dataHolderBrandId' in brand):
            brandId = brand['dataHolderBrandId']
        else:
            brandId = brand['interimId']
        brands[brandId] = {}
        if 'dataHolderBrandId' in brand:
            brands[brandId]['dataHolderBrandId'] = brand['dataHolderBrandId']
        if 'interimId' in brand:
            brands[brandId]['interimId'] = brand['interimId']
        brands[brandId]['brandName'] = brand['brandName']
        brands[brandId]['logoUri'] = brand['logoUri']
        brands[brandId]['publicBaseUri'] = brand['publicBaseUri']
        brands[brandId]['lastUpdated'] = brand['lastUpdated']
        if 'abn' in brand:
            brands[brandId]['abn'] = brand['abn']
        if 'acn' in brand:
            brands[brandId]['acn'] = brand['acn']
        if 'arbn' in brand:
            brands[brandId]['arbn'] = brand['arbn']


brands_file = open("brands/brands.json", "w")
json.dump(brands, brands_file, indent = 4)
brands_file.close()