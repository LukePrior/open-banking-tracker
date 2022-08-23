import git
import json
import os
import isodate

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

def calculate_interest(lendingRates, product_rates, time):
    if len(product_rates) == 0:
        for lendingRate in lendingRates:
            rate = round(float(lendingRate["rate"])*100,2)
    
            formatted = {"rates": [{"time": time, "rate": rate}], "lendingRateType": lendingRate["lendingRateType"]}
            if "repaymentType" in lendingRate and lendingRate["repaymentType"] != None:
                    formatted["repaymentType"] = lendingRate["repaymentType"]
            if "loanPurpose" in lendingRate and lendingRate["loanPurpose"] != None:
                    formatted["loanPurpose"] = lendingRate["loanPurpose"]
            if "additionalValue" in lendingRate and lendingRate["additionalValue"] != None:
                formatted["additionalValue"] = lendingRate["additionalValue"]
            if "tiers" in lendingRate:
                formatted["tiers"] = lendingRate["tiers"]
            if "additionalInfo" in lendingRate:
                formatted["additionalInfo"] = lendingRate["additionalInfo"]
            product_rates.append(formatted)
    
    else:
        for lendingRate in lendingRates:
            rate = round(float(lendingRate["rate"])*100,2)

            matches = []
            for offering in product_rates:
                if offering["lendingRateType"] == lendingRate["lendingRateType"] and ("loanPurpose" not in offering or "loanPurpose" not in lendingRate or offering["loanPurpose"] == lendingRate["loanPurpose"]) and ("repaymentType" not in offering or "repaymentType" not in lendingRate or offering["repaymentType"] == lendingRate["repaymentType"]):
                    matches.append(offering)

            tempmatches = []
            if len(matches) > 1:
                for match in matches:
                    if ("additionalValue" in match and "additionalValue" in lendingRate and (match["additionalValue"] != lendingRate["additionalValue"])):
                        continue
                    if ("tiers" in match and "tiers" in lendingRate and (match["tiers"] != lendingRate["tiers"])):
                        continue
                    if ("additionalInfo" in match and "additionalInfo" in lendingRate and (match["additionalInfo"] != lendingRate["additionalInfo"])):
                        continue
                    tempmatches.append(match)
                matches = tempmatches

            if len(matches) == 0:
                formatted = {"rates": [{"time": time, "rate": rate}], "lendingRateType": lendingRate["lendingRateType"]}
                if "repaymentType" in lendingRate and lendingRate["repaymentType"] != None:
                    formatted["repaymentType"] = lendingRate["repaymentType"]
                if "loanPurpose" in lendingRate and lendingRate["loanPurpose"] != None:
                    formatted["loanPurpose"] = lendingRate["loanPurpose"]
                if "additionalValue" in lendingRate and lendingRate["additionalValue"] != None:
                    formatted["additionalValue"] = lendingRate["additionalValue"]
                if "tiers" in lendingRate:
                    formatted["tiers"] = lendingRate["tiers"]
                if "additionalInfo" in lendingRate:
                    formatted["additionalInfo"] = lendingRate["additionalInfo"]
                product_rates.append(formatted)

            elif len(matches) == 1:
                if matches[0]["rates"][-1]["rate"] == rate:
                    matches[0]["rates"][-1]["time"] = time
                else:
                    matches[0]["rates"].append({"time": time, "rate": rate})

    return product_rates

repo = git.Repo()

list = open('aggregate/RESIDENTIAL_MORTGAGES/data.json')
products = json.load(list)
for product in products:
    try:
        path = "brands/product/" + product["brandId"] + "/" + product["productId"] + ".json"

        commits = repo.iter_commits(paths=path)

        product_rates = []
        for commit in commits:
            try:
                filecontents = (commit.tree / path).data_stream.read()
            except:
                continue
            if check_product(json.loads(filecontents)):
                calculate_interest(json.loads(filecontents)["data"]["lendingRates"], product_rates, commit.committed_date)

        temp_product_rates = []
        for rate in product_rates:
            formatted = {"rates": rate["rates"]}
            name = []
            if "additionalValue" in rate:
                name.append(rate["additionalValue"])
                try:
                    period = isodate.parse_duration(rate["additionalValue"])
                    formatted["period"] = int(period.years)*12 + int(period.months)
                except:
                    formatted["period"] = rate["additionalValue"]
            if "lendingRateType" in rate:
                name.append(rate["lendingRateType"])
                formatted["lendingRateType"] = rate["lendingRateType"]
            if "repaymentType" in rate:
                name.append(rate["repaymentType"])
                formatted["repaymentType"] = rate["repaymentType"]
            if "loanPurpose" in rate:
                name.append(rate["loanPurpose"])
                formatted["purpose"] = rate["loanPurpose"]
            if len(name) == 0:
                name.append("DEFAULT")
            formatted["name"] = " ".join(name)
            temp_product_rates.append(formatted)
        product_rates = temp_product_rates

        product_rates = sorted(product_rates, key=lambda d: d['name']) 

        folder = "history/product/" + product["brandId"]
        if not os.path.exists(folder):
            os.makedirs(folder)

        save = "history/product/" + product["brandId"] + "/" + product["productId"] + ".json"

        raw_file = open(save, "w")
        json.dump(product_rates, raw_file, indent = 4)
        raw_file.close()
    except Exception as e:
        print(e)
