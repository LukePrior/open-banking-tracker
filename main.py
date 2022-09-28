import requests
import json

brands = {}

r = requests.get('https://api.cdr.gov.au/cdr-register/v1/banking/data-holders/brands/summary', headers={"x-v":"1"})

available_brands = r.json()

raw_file = open("brands/raw.json", "w")
json.dump(available_brands, raw_file, indent = 4)
raw_file.close()

available_brands = available_brands['data']

for brand in available_brands:
    if ('dataHolderBrandId' in brand or 'interimId' in brand):
        brands[brand['dataHolderBrandId']] = {}
        if 'dataHolderBrandId' in brand:
            brands[brand['dataHolderBrandId']]['dataHolderBrandId'] = brand['dataHolderBrandId']
        if 'interimId' in brand:
            brands[brand['dataHolderBrandId']]['interimId'] = brand['interimId']
        brands[brand['dataHolderBrandId']]['brandName'] = brand['brandName']
        brands[brand['dataHolderBrandId']]['logoUri'] = brand['logoUri']
        brands[brand['dataHolderBrandId']]['publicBaseUri'] = brand['publicBaseUri']
        brands[brand['dataHolderBrandId']]['lastUpdated'] = brand['lastUpdated']
        if 'abn' in brand:
            brands[brand['dataHolderBrandId']]['abn'] = brand['abn']
        if 'acn' in brand:
            brands[brand['dataHolderBrandId']]['acn'] = brand['acn']
        if 'arbn' in brand:
            brands[brand['dataHolderBrandId']]['arbn'] = brand['arbn']


brands_file = open("brands/brands.json", "w")
json.dump(brands, brands_file, indent = 4)
brands_file.close()