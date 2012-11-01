#!/usr/bin/python
# getGeo.py
# Aryeh Hillman
# 
# Gets data from GEO2R
#
# TODO: probably great to have some logging capabilities baked in (see below)

import httplib2
import json
h = httplib2.Http(".cache")

GSEBaseURL = "http://www.ncbi.nlm.nih.gov/geo/geo2r/?acc="
url = GSEBaseURL + "GSE32982"

response, content = h.request(url)

def makeMetaURL(mode="geo2r", **kwargs):
   metaURL = "http://www.ncbi.nlm.nih.gov/geo/tools/geometa.cgi?"
   shortnames = { 'view':'view',
                  'series': 'series',
                  'accession': 'acc',
                  'platform': 'platform',
                  'mode': 'mode' }
   
   for attr in kwargs:
      firstAttr = False
      if not firstAttr:
         metaURL += "&"
      
      shortname = attr
      if (shortnames.has_key(attr)):
         shortname = shortnames[attr]
      
      metaURL += shortname + "=" + kwargs[attr]
      
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

def getSamples(accession, platform):
   metaURL = makeMetaURL(series=accession, platform=platform, view='samples', mode='geo2r')
   print metaURL
   response, content = h.request(metaURL)
   
   metaJSON = json.loads(content)
   return metaJSON

getPlatformList("GSE21032")
getSamples("GSE21032", getPlatformList("GSE21032")[0])


