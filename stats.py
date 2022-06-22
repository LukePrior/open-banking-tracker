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

def calculate_interest(lendingRates):
    global lowest_rate
    product_rates = []
    for lendingRate in lendingRates:
        if "calculationFrequency" not in lendingRate:
            continue

        if "loanPurpose" in lendingRate and lendingRate["loanPurpose"] == "INVESTMENT":
            continue

        calculationFrequency = lendingRate["calculationFrequency"]
        duration = parse_duration(calculationFrequency)

        if duration == None:
            continue

        if duration.total_seconds() == 0:
            continue

        rate = round(float(lendingRate["rate"])*100,2)

        formatted = {"rate": rate, "lendingRateType": lendingRate["lendingRateType"]}

        if lendingRate["lendingRateType"] == "VARIABLE" or lendingRate["lendingRateType"] == "FIXED":
            formatted["primary"] = True
        elif len(lendingRates) == 1:
            continue
        else:
            formatted["primary"] = False

        if lendingRate["lendingRateType"] == "FIXED" and "additionalValue" in lendingRate:
            period = parse_duration(lendingRate["additionalValue"])
            months = int(period.years)*12 + int(period.months)

            if period != None:
                formatted["period"] = months

        if "repaymentType" in lendingRate and lendingRate["repaymentType"] != None:
            formatted["repaymentType"] = lendingRate["repaymentType"]

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

        processed = {"brandId": brand, "brandName": "placeholder", "productId": product["data"]["productId"], "productName": product["data"]["name"], "description": product["data"]["description"], "rate": rate}

        if "brandName" in product["data"]:
            processed["brandName"] = product["data"]["brandName"]
        else:
            processed["brandName"] = product["data"]["brand"]

        data.append(processed)

with open('aggregate/RESIDENTIAL_MORTGAGES/data.json', 'w') as outfile:
    json.dump(data, outfile)
        