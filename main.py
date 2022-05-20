from mimetypes import guess_extension
import os
import requests
import json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

brands = {}

r = requests.get('https://api.cdr.gov.au/cdr-register/v1/banking/register')

available_brands = r.json()

try:
    raw_file = open("brands/raw.json", "w")
    
    json.dump(available_brands, raw_file, indent = 4)
    
    raw_file.close()

except Exception as e:
    print(e)

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

try:
    brands_file = open("brands/brands.json", "w")
    
    json.dump(brands, brands_file, indent = 4)
    
    brands_file.close()

except Exception as e:
    print(e)

changed_images = 0

for brand in brands:
    try:
        r = requests.get(brands[brand]['logoUrl'], headers=headers)
        file_extension = guess_extension(r.headers['Content-Type'].partition(';')[0].strip())
        if file_extension == None and r.headers['Content-Type'] == 'image/webp':
            file_extension = '.webp'
        if file_extension == '.jpe':
            file_extension = '.jpg'
        if file_extension == '.htm' or file_extension == '.html':
            continue
        path = 'brands/logos/' + brand + file_extension
        oldFile = ""
        for file in os.listdir('brands/logos/'):
            if brand in file:
                oldFile = 'brands/logos/' + file     
        with open(path, 'wb') as f:
            f.write(r.content)
        if oldFile != "" and oldFile != path:
            os.remove(oldFile)
        if oldFile != path:
            changed_images += 1

    except Exception as e:
        print(e)

stats = {}
stats['changed_images'] = changed_images

try:
    raw_file = open("stats.json", "w")
    
    json.dump(stats, raw_file, indent = 4)
    
    raw_file.close()

except Exception as e:
    print(e)