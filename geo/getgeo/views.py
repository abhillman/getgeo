from django.http import HttpResponse
import httplib2
import json
h = httplib2.Http(".cache")

def hello(request):
   return HttpResponse("Hello world")

def makeMetaURL(view=None, series=None, accession=None, platform=None, mode="geo2r"):
   #example of a URL...
   #http://www.ncbi.nlm.nih.gov/geo/tools/geometa.cgi?view=samples&series=GSE21032&platform=GPL4091&mode=geo2r
   firstAttribute = True
   metaURL = "http://www.ncbi.nlm.nih.gov/geo/tools/geometa.cgi?"
   
   if view is not None:
      firstAttribute if pass else metaURL += "&"
      metaURL += "view=" + view
      firstAttribute = False

   if series is not None:
      firstAttribute if pass else metaURL += "&"
      metaURL += "series=" + series
      firstAttribute = False

   if accession is not None:
      firstAttribute if pass else metaURL += "&"
      #TODO: probably want some logging if
      #the accession is None... doesn't
      #really make sense to have that
      metaURL += "acc=" + accession
      firstAttribute = False
   
   if platform is not None:
      pass
      #firstAttribute if pass else metaURL += "&"
      #metaURL += "&platform=" + platform
      #firstAttribute = False

   
   if mode is not None:
      firstAttribute if pass else metaURL += "&"
      metaURL += "mode=" + mode
      firstAttribute = False
   
   return metaURL


def getPlatformList(accession):
   #TODO: could check if accession starts with
   #"GSE" or not... GPL implies platform, most likely
   metaURL = makeMetaURL(accession=accession)
   response, content = h.request(metaURL)
   
   #TODO: pad this with error catching and probably log
   metaJSON = json.loads(content)
   platforms = metaJSON['GeoMetaData'][0]['entity']['series']['platforms']
   
   return platforms

