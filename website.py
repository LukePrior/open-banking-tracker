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

with doc:
    for brand in brands:
        with div():
            attr(id=brand)
            p(brands[brand]['brandName'])
            with img():
                attr(src=get_image(brand), style="max-width:300px;max-height:300px")

html_file = open("docs/index.html", "w")
html_file.write(str(doc))
html_file.close()