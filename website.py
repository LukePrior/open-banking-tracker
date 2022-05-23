import dominate
from dominate.tags import *
import json
import os
import base64
import mimetypes

raw_file = open("brands/brands.json", "r")
brands = json.load(raw_file)
raw_file.close()

doc = dominate.document(title='Open Banking Brands')

def get_image(id):
    for file in os.listdir('brands/logos/'):
        file_name = os.path.splitext(file)[0]
        if file_name == id:
            raw_file = open('brands/logos/' + file, "rb")
            encode = base64.b64encode(raw_file.read())
            raw_file.close()
            type = mimetypes.guess_type(file)[0]
            if type == None and os.path.splitext(file)[1] == ".webp":
                type = "image/webp"
            image = "data:" + str(type) + ";base64, " + str(encode, 'utf-8')
            return image

def get_products(id):
    for file in os.listdir('brands/products/'):
        file_name = os.path.splitext(file)[0]
        if file_name == id:
            raw_file = open('brands/products/' + file, "rb")
            contents = json.load(raw_file)
            raw_file.close()
            return contents

def get_product(brand, product):
    for file in os.listdir('brands/product/'+brand+"/"):
        file_name = os.path.splitext(file)[0]
        if file_name == product:
            raw_file = open('brands/product/' + brand + "/" + file, "rb")
            contents = json.load(raw_file)
            raw_file.close()
            return contents

with doc:
    with div():
        attr(style="display:flex;flex-wrap:wrap;")
        for brand in brands:
            with div():
                attr(id=brand, style="width:300px;height:300px;border-style:solid;margin:25px;padding:25px;cursor:pointer;", onclick="location.href='brands/" + brand + "/index.html';")
                p(brands[brand]['brandName'])
                with img():
                    attr(src=get_image(brand), style="max-width:90%;max-height:70%")

html_file = open("docs/index.html", "w")
html_file.write(str(doc))
html_file.close()

for brand in brands:
    products = get_products(brand)
    if products != None and "data" in products:
        products = products["data"]["products"]
    else:
        continue
    doc1 = dominate.document(title=brands[brand]["brandName"])
    with doc1:
        with div():
            attr(style="display:flex;flex-wrap:wrap;")
            for product in products:
                with div():
                    attr(id=product["productId"], style="width:300px;height:300px;border-style:solid;margin:25px;padding:25px;cursor:pointer;", onclick="location.href='" + product["productId"] + ".html';")
                    p(product['name'])
                    if "cardArt" in product and len(product['cardArt']) > 0:
                        source = product['cardArt'][0]['imageUri']
                    else:
                        source = get_image(brand)
                    with img():
                        attr(src=source, style="max-width:90%;max-height:70%")
    
    html_file = open("docs/brands/" + brand + "/index.html", "w")
    html_file.write(str(doc1))
    html_file.close()

for root, dirs, files in os.walk("brands/product/"):
    for file in files:
        brand = root.split("/")[2]
        id = os.path.splitext(file)[0]

        product = get_product(brand, id)
        if "data" in product:
            product = product['data']
        else:
            continue

        doc2 = dominate.document(title=product["name"])
        with doc2:
            with div():
                with textarea(str(json.dumps(product, indent = 4))):
                    attr(style="width:90vw;height:90vh")

        html_file = open("docs/brands/" + brand + "/" + id + ".html", "w")
        html_file.write(str(doc2))
        html_file.close()
