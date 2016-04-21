class TitleTermClassifier(object):
    """Instantiate a TitleTermClassifier with a list of title terms and a classification label"""

    def __init__(self,label,terms):
        """"parkingClassifier = TitleTermClassifier("Parking",["permit parking", "parking permit"])"""
        self.label = label
        self.terms = terms

    def test_terms(self, title):
        if (any(term in title for term in self.terms)):
            return self.label
        return None

    def __call__(self, title):
        return self.test_terms(title)

class ShortCircuitClassifier(TitleTermClassifier):
    def __call__(self, title):
        if (title.startswith("payment ")):
            return "Claims"
        elif ("special city council meeting" in title):
            return "Interesting Documents"
        else:
            return self.test_terms(title)



def apply_strategies(title, strategies):
    #apply classification strategies one-by-one to the title
 
    for strat in strategies:
        result = strat(title)
        if result != None:
            return result

    return result

def cleanTitle(title):
    #clean title
    title = title.lower()
    title = title.replace('(', '')
    title = title.replace(')', '')
    title = title.replace('/', ' ')
    title = title.replace('  ', ' ') #get rid of double spaces

    return title




def classifyTitle(title):
    #return the classification of a title
    
    #apply classifying strategies to title
    strategies = [TitleTermClassifier("Traffic", ["tow zone", "tow-away zone", "buffer zone", "traffic sign", 
                                                  "traffic regulation", "vehicle weight", "parking prohibited", 
                                                  "traffic direction", "loading zone", "standing zone",
                                                  "closed to traffic", "parking meter", "miscellaneous sign",
                                                  "parking restrict", "parking limit"]), 
		  TitleTermClassifier("Parking", ['permit parking', 'parking permit', 'handicapped parking']),
                  ShortCircuitClassifier("Claims", ["refund", "claim"]), 
		  TitleTermClassifier("Exemptions", ["free permit", "cancellation", "exemption", "waiver",
                                                     "refund of fee"]), 
		  TitleTermClassifier("Public Use", ["public way", "awning", "sidewalk cafe", "canopy", 
		                                     "issuance of permit", "vacation of public", "public alley",
                                                     "sidewalk sales permit"]), 
                  ShortCircuitClassifier("Proceedings", ["city council journal", "city council meeting", 
		                                     "oath of office", "appointment of"]),
		  TitleTermClassifier("Permits", ['tag day permit', 'issuance of special event license', 
                                                 'issuance of special event permit']), 
		  TitleTermClassifier("Developments", ['city-owned propert', 'zoning reclassification',
                                                      'development agreement', 'city-owned building']), 
		  TitleTermClassifier("Services & Budgets", ["scope of services, budget and management agreement"]), 
		  TitleTermClassifier("Recognitions", ["honorary street", "tribute", "extended to", "congratulations",
                                                      "commemoration", "anniversary", "historical landmark designation",
                                                      "declaration of"]), 
		  TitleTermClassifier("Tax", ["tif", "tax incentive", "tax increment financing", 
                                              "tax increment allocation", "property tax levy", "tifworks",
                                              "special service area"]),
		  TitleTermClassifier("Interesting Documents", ["call for ", "letter of support", "expenditure of", "settlement agreement"]),
                  TitleTermClassifier("Licenses", ["liquor license", "package goods license"])

		  ]
    result = apply_strategies(title, strategies)
    return result

