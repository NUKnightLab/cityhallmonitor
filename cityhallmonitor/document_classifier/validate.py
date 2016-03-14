def verify(res, lines):

    #define a dictionary of (classification: trunc_titles)
    res_dict = dict()
    res_dict["Public_Use"] = ['grant(s) of privilege in public way', 'grant(s) of privilege in the public way','amendment of grant(s) of privilege in public way', 'canopy(s)', 'awning(s)', 'sidewalk cafe(s)', 'issuance of permits']
    res_dict["Parking"] = ['handicapped parking permit', 'handicapped permit parking', 'residential permit parking', 'industrial permit parking']
    res_dict["Claims"] =  ['various small claims', 'senior citizen sewer refund(s)', 'payment of various small', 'payment of hospital and', 'condominium claim', "payment of", "condominium refuse rebate claim"]
    res_dict["Traffic"] = ['traffic sign(s)', 'vehicle weight limitation', 'sundry traffic regulation(s) and', 'loading/standing/tow zone', 'buffer zone', 'tow-away zone', 'traffic direction', 'tow zone', 'parking prohibited']
    res_dict["Recognition"] = ['congratulations extended', 'gratitude extended', 'honorary street designation', 'recognition extended', 'tribute']
    res_dict["Development"] = ['sale of city-owned property', 'zoning reclassification map', 'negotiated sale of city-owned property']
    res_dict["Exemptions"] = ['cancellation of water/sewer fee(s)', 'exemption from physical barrier requirement', 'waiver of special event license and/or permit fee(s)', 'cancellation of', 'not-for-profit fee exemption(s)', 'free permit(s)', 'historical landmark fee waiver', 'waiver of', 'license fee exemption']
    res_dict["Permit"] = ['issuance of special event license(s) and/or permit(s)', 'tag day permit(s)']
    res_dict["Proceedings"] = ['correction of city council', 'oath of office of', 'time fixed']
    res_dict["Other"] = ['scope of services, budget and management agreement']
    res_dict["Tax"] = ['tax increment financing (tif)', 'support of class 6(b) tax incentive']

    #open the correct file
    file_ = open("results/"+res, "w")

    #verify lines
    trunc_list = res_dict[res]
    for line in lines:
        line = line.lower()
        if any(line.startswith(trunc) for trunc in trunc_list) == False:
            file_.write(line)

    file_.close()

#################################
results = ["Claims", "Development", "Exemptions", "Other", "Parking", "Permit", "Proceedings", "Public_Use", "Recognition", "Tax", "Traffic"]

for res in results:

    #get lines from file
    file_ = open("results/"+res,"r")
    lines = file_.readlines()
    file_.close()

    verify(res, lines)


