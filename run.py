#!/usr/bin/env python3

import os
import sys
#sys.path.append('/apps/quants/python')
import glob

import flywheel
import logging
import zipfile
import itk
import numpy as np
import quants 
import pandas as pd

# get value from bids tag-value pair
def bidsTagValue( tag ):
    parts = tag.split("-")
    parts.pop(0)
    val = "-".join(parts)
    return(val)
    
# get sub and ses from a filename
# can this be obtained more easily/directly?
def parseFile( fname ):

    file = os.path.basename(fname)
    fileParts = file.split("_")
    sub = bidsTagValue( fileParts[0] )
    ses = bidsTagValue( fileParts[1] )
    
    return((sub,ses))




##Initialize logging and set its level
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

context = flywheel.GearContext()
config = context.config

#minSize = config['min_size']
#if minSize==0:
#    minSize=1

zipPath=context.get_input_path('zip')
log.info("input: "+zipPath)
unzipPath="/tmp/unzip"
os.mkdir( unzipPath )
with zipfile.ZipFile(zipPath, 'r') as zip_ref:
    zip_ref.extractall(unzipPath)

imgFiles = quants.getFTDCInputs(unzipPath)

for tag in imgFiles.keys():
    files = imgFiles[tag]
    tryRead=True
    if len(files)==0:
        log.warning("No image found for [%s]", tag)
        tryRead=False
    if (len(files)>1):
        log.warning("Multiple images found for [%s]", tag)
        tryRead=False
    
    if not tryRead:
        imgFiles[tag] = []

bidsInfo = parseFile(imgFiles["t1"][0])

quantsify = quants.getFTDCQuantsifier( imgFiles )
quantsify.SetConstants({"id": bidsInfo[0], "date": bidsInfo[1]})
quantsify.Update()
stats = quantsify.GetOutput()

oname = os.path.join("/flywheel/v0/output/", "sub-" + bidsInfo[0] + "_ses-" + bidsInfo[1] + "_desc-quants.csv")
stats.to_csv(oname, index=False, float_format='%.4f')


