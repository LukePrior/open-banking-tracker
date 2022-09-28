from mimetypes import guess_extension
import os
import requests
import json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

raw_file = open("brands/brands.json", "r")
brands = json.load(raw_file)
raw_file.close()

changed_images = 0

for brand in brands:
    try:
        r = requests.get(brands[brand]['logoUri'], headers=headers)

        file_extension = guess_extension(r.headers['Content-Type'].partition(';')[0].strip())

        if file_extension == None and r.headers['Content-Type'] == 'image/webp':
            file_extension = '.webp'
        if file_extension == '.jpe':
            file_extension = '.jpg'
        if file_extension == '.htm' or file_extension == '.html':
            continue

        path = 'logos/' + brand + file_extension
        oldFile = ""

        for file in os.listdir('logos/'):
            if brand in file:
                oldFile = 'logos/' + file 

        with open(path, 'wb') as f:
            f.write(r.content)

        if oldFile != "" and oldFile != path:
            os.remove(oldFile)

        if oldFile != path:
            changed_images += 1
            
        print(path)

    except Exception as e:
        print(e)

stats = {}
stats['changed_files'] = changed_images

raw_file = open("stats.json", "w")
json.dump(stats, raw_file, indent = 4)
raw_file.close()