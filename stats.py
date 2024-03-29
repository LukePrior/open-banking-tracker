from bdb import effective
import json
from logging import error
import os
import re
import isodate
import json

lowest_rate = 100
mortgage_amount = 600000

def parse_duration(duration):
    try:
        interest_period = isodate.parse_duration(duration)
    except:
        return None
    return interest_period

def get_product(brand, product):
    for file in os.listdir('brands/product/'+brand+"/"):
        file_name = os.path.splitext(file)[0]
        if file_name == product:
            raw_file = open('brands/product/' + brand + "/" + file, "rb")
            contents = json.load(raw_file)
            raw_file.close()
            return contents

def check_product(product):
    if "data" not in product:
        return False
    if product["data"]["productCategory"] != "RESIDENTIAL_MORTGAGES":
        return False
    if "lendingRates" not in product["data"]:
        return False
    if "brandName" not in product["data"] and "brand" not in product["data"]:
        return False
    if "name" not in product["data"]:
        return False
    if "description" not in product["data"]:
        return False
    if "productId" not in product["data"]:
        return False
    return True 

def check_eligability(product):
    if "constraints" in product["data"]:
        for constraint in product["data"]["constraints"]:
            if constraint["constraintType"] == "MAX_LIMIT" or constraint["constraintType"] == "MAX_BALANCE":
                try:
                    if float(constraint["additionalValue"]) < mortgage_amount:
                        return False
                except:
                    return False
    return True

def check_offset(product):
    if "features" in product["data"]:
        for feature in product["data"]["features"]:
            if feature["featureType"] == "OFFSET":
                if "additionalValue" in feature and (feature["additionalValue"] == "No" or feature["additionalValue"] == "Not available"):
                    continue
                return True
    return False


def check_redraw(product):
    if "features" in product["data"]:
        for feature in product["data"]["features"]:
            if feature["featureType"] == "REDRAW":
                if "additionalValue" in feature and (feature["additionalValue"] == "No" or feature["additionalValue"] == "Not available"):
                    continue
                return True
    return False

def calculate_interest(lendingRates):
    global lowest_rate
    product_rates = []
    for lendingRate in lendingRates:
        if lendingRate["lendingRateType"] != "VARIABLE" and lendingRate["lendingRateType"] != "FIXED":
            continue

        try:
            rate = round(float(lendingRate["rate"])*100,2)
        except:
            continue

        formatted = {"rate": rate, "lendingRateType": lendingRate["lendingRateType"]}

        if "loanPurpose" in lendingRate:
            formatted["purpose"] = lendingRate["loanPurpose"]

        if lendingRate["lendingRateType"] == "FIXED" and "additionalValue" in lendingRate and lendingRate["additionalValue"] != None:
            try:
                period = parse_duration(lendingRate["additionalValue"])
                months = int(period.years)*12 + int(period.months)
            except:
                period = None

            if period != None:
                formatted["period"] = months

        if "repaymentType" in lendingRate and lendingRate["repaymentType"] != None:
            formatted["repaymentType"] = lendingRate["repaymentType"]

        if "tiers" in lendingRate:
            for tier in lendingRate["tiers"]:
                if ("LVR" in tier["name"].upper() and tier["unitOfMeasure"] == "PERCENT" and "minimumValue" in tier and "maximumValue" in tier):
                    if (tier["minimumValue"] != None):
                        if (float(tier["minimumValue"]) <= 1):
                            formatted["minLVR"] = float(tier["minimumValue"])*100
                        else:
                            formatted["minLVR"] = float(tier["minimumValue"])
                    if (tier["maximumValue"] != None):
                        if (float(tier["maximumValue"]) <= 1):
                            formatted["maxLVR"] = float(tier["maximumValue"])*100
                        else:
                            formatted["maxLVR"] = float(tier["maximumValue"])

        product_rates.append(formatted)

    if len(product_rates) == 0:
        return None

    return product_rates

data = []
for root, dirs, files in os.walk("brands/product/"):
    for file in files:
        brand = root.split("/")[2]
        id = os.path.splitext(file)[0]

        product = get_product(brand, id)
        if not check_product(product):
            continue
        if not check_eligability(product):
            continue

        rate = calculate_interest(product["data"]["lendingRates"])
        if rate == None:
            continue

        processed = {"brandId": brand, "brandName": "placeholder", "productId": product["data"]["productId"], "productName": product["data"]["name"], "rate": rate, "offset": check_offset(product), "redraw": check_redraw(product)}

        if "brandName" in product["data"]:
            processed["brandName"] = product["data"]["brandName"]
        else:
            processed["brandName"] = product["data"]["brand"]

        data.append(processed)

with open('aggregate/RESIDENTIAL_MORTGAGES/data.json', 'w') as outfile:
    json.dump(data, outfile)
        
