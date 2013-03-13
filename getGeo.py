#!/usr/bin/python
# getGeo.py
# Aryeh Hillman
# 
# Gets data from GEO2R
#
# TODO: probably great to have some logging capabilities baked in (see below)

import httplib2
import json
import sys
from subprocess import Popen, PIPE, STDOUT
import StringIO
debug = 0
h = httplib2.Http(".cache")
USAGE = """%s accession platform featureOutfile dataOutfile""" % sys.argv[0]
USAGE = """Enter - to avoid specifying a platform"""

if len(sys.argv) != 5:
   print USAGE
   sys.exit(-1)

accession = sys.argv[1]
platform = sys.argv[2]
featureOutfile = sys.argv[3]
dataOutfile = sys.argv[4]

def generateRText(accession, platform, dataOutfile):
   text = """
library(Biobase)
library(GEOquery)

gset <- getGEO("%s", GSEMatrix =TRUE)
if (length(gset) > 1) idx <- grep("%s", attr(gset, "names")) else idx <- 1
gset <- gset[[idx]]

write.table(gset, file="%s")
""" % (accession, platform, dataOutfile)
   return text

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
   if debug:
      print metaURL
   response, content = h.request(metaURL)
   
   metaJSON = json.loads(content)
   return metaJSON

def jsonSamplesString(j):
   string = "accession title " + " ".join(j['GeoMetaData'][0]['entity']['sample'].keys()) + "\n"
   for sample in j['GeoMetaData']:
      string += "%s\t%s" % (sample['acc'], sample['title'])
      string += '\t'.join(sample['entity']['sample']['channels'].values())

def getSampleHeader(sample):
   headerString = "tite\tacc\t"
   
   channelKeys = dict()
   for channel in sample['entity']['sample']['channels']:
      for key in channel.keys():
         if channelKeys.has_key(key):
            channelKeys[key] = d[key] + 1
         else:
            channelKeys[key] = 1
   
   channelKeyString = ""
   for key, numAppearances in channelKeys.iteritems():
      for x in range(1,numAppearances + 1):
         channelKeyString += key + str(x) + "\t"
   
   headerString += channelKeyString
   return headerString

#http://stackoverflow.com/questions/8477550/
#flattening-a-list-of-dicts-of-lists-of-dicts-etc-of-unknown-depth-in-python-n
keys = []
def flatten(l):
    global keys
    out = []
    if isinstance(l, (list, tuple)):
        for item in l:
            keys.append(keys[-1])
            out.extend(flatten(item))
    elif isinstance(l, (dict)):
        for dictkey in l.keys():
            keys.append(dictkey)
            out.extend(flatten(l[dictkey]))
    elif isinstance(l, (str, int, unicode)):
        keys.append(keys[-1])
        out.append(l)
    return out

def main():
   global platform
   platforms = getPlatformList(accession)
   
   if platform == "-":
      if len(platforms) != 1:
         print "Multiple platforms exist for accession %s" % accession
         sys.exit(-1)
      platform = platforms[0]
#      print platform
   
   if len(platforms) == 0:
      print "Accession %s does not exist" % accession
      sys.exit(1)
   if platforms.count(platform) == 0:
      print "Platform %s does not exist for accession %s" % (platform, accession)
      sys.exit(1)
   
   samplesJSON = getSamples(accession, platform)
   samples = flatten(samplesJSON)
   
   line = []
   lines = []
   for item in samples:
      if not isinstance(item, int):
         if item[:3] == 'ftp':
            continue
         if item[:3] == 'GSM':
            if line != []:
               lines.append(line)
            line = []
      line.append(item)
   
   featuresFile = open(featureOutfile, 'w')
   for line in lines:
      lineString = line.__repr__()[1:-1] + "\n"
      featuresFile.write(lineString)
   featuresFile.close()

   rString = generateRText(accession, platform, dataOutfile)

#    rfile = open("rfile.tmp", 'w')
#    rfile.write(generateRText(accession, platform))
#    rfile.close()
   
   from subprocess import Popen, PIPE, STDOUT
   p = Popen(['R', '--no-save'], stdin=PIPE, stderr=PIPE, stdout=PIPE)
   print
   print rString
   print
   print p.communicate(input=rString)
#   print p.communicate(rString)

if __name__=="__main__":
   main()
