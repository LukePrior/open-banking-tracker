import requests
import json

brands = {}

r = requests.get('https://api.cdr.gov.au/cdr-register/v1/banking/register')

available_brands = r.json()

raw_file = open("brands/raw.json", "w")
json.dump(available_brands, raw_file, indent = 4)
raw_file.close()

available_brands = available_brands['registerDetails']

for entity in available_brands:
    for brand in entity['brands']:
        if 'productReferenceDataApi' in brand:
            brands[brand['brandRef']] = {}
            brands[brand['brandRef']]['legalEntityId'] = entity['legalEntityId']
            brands[brand['brandRef']]['legalEntityName'] = entity['legalEntityName']
            brands[brand['brandRef']]['accreditationDate'] = entity['accreditationDate']
            brands[brand['brandRef']]['brandRef'] = brand['brandRef']
            brands[brand['brandRef']]['brandName'] = brand['brandName']
            brands[brand['brandRef']]['productReferenceDataApi'] = brand['productReferenceDataApi']
            brands[brand['brandRef']]['logoUrl'] = brand['logoUrl']
            brands[brand['brandRef']]['cdrPolicyUrl'] = brand['cdrPolicyUrl']
            if 'website' in brand:
                brands[brand['brandRef']]['website'] = brand['website']
            elif 'website' in entity:
                brands[brand['brandRef']]['website'] = entity['website']
            if 'brandDescription' in brand:
                brands[brand['brandRef']]['brandDescription'] = brand['brandDescription']


brands_file = open("brands/brands.json", "w")
json.dump(brands, brands_file, indent = 4)
brands_file.close()