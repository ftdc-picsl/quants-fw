#!/usr/bin/env python3

import os
import sys
sys.path.append('/apps/quants/python')
import glob

import flywheel
import logging
import zipfile
import itk
import numpy as np
import quantsUtilities as qu
import quantsifier as qf

log = logging.getLogger(__name__)

##Initialize logging and set its level
##logging.basicConfig()
##log = logging.getLogger()
log.setLevel(logging.INFO)

context = flywheel.GearContext()
config = context.config

minSize = config['min_size']
if minSize==0:
    minSize=40

zipPath=context.get_input_path('zip')
os.mkdir( os.path.join('/flywheel/v0/input', 'unzip'))
with zipfile.ZipFile(zipPath, 'r') as zip_ref:
    zip_ref.extractall('/flywheel/v0/input/unzip')

imgsFiles = qu.getFTDCInputs('/flywheel/v0/input/unzip')
for tag in imgFiles.keys():
    files = imgFiles[tag]
    if len(files)==0:
        print("No image found for ["+tag+"]")
    if (len(files)>1):
        print("Multiple images found for ["+tag+"]")
        
    imgFiles[tag] = files[len(files)-1]

quantsify = qu.getFTDCQuantsifier( imgFiles )




sys=qu.loadLabelSystem(system)
print(sys)

# Check for image header consistency
validHeaders = [  qu.compareImageHeaders(t1, x) for x in [thick,lbl,n4,mask,gmp] ]
if sum(validHeaders) != len(validHeaders):
    print("All images must have same header information")

# Get array views for all images
t1View = itk.array_view_from_image(t1)
segView = itk.array_view_from_image(seg)
thickView = itk.array_view_from_image(thick)
lblView = itk.array_view_from_image(lbl)
maskView = itk.array_view_from_image(mask)
gmpView = itk.array_view_from_image(gmp)
n4View = itk.array_view_from_image(n4)

# Eliminate CSF from volume measures
volumeMask = np.copy(mask)
volumeMask[ segView==1 ]=0

# Cortex mask
cortexMask = np.copy(segView)
cortexMask[segView != 2] = 0
cortexMask[cortexMask==2] = 1
cortexMask[thickView < 0.000001] = 0

# Deep gray mask (not CSF or whitematter)
grayMask = np.copy(segView)
grayMask[ segView==1 ] = 0
grayMask[ segView==3 ] = 0
grayMask[ grayMask > 0 ] = 1

whiteMask = np.copy(segView)
whiteMask[ whiteMask !=3 ]=0
whiteMask[ whiteMask > 0]=1


# ROI Volumes
voxvol = np.prod( itk.GetArrayFromVnlVector(itk.spacing(t1).GetVnlVector()))
#labelValues = np.unique(lblView)
#labelValues = labelValues[labelValues != 0]
#vol = [ (int(i),voxvol*float(np.sum(lblView==i))) for i in labelValues ]
#print("Volumes")
#print(vol)

grayLabelValues = np.array(sys['number'][sys['ants6']==4])
stemLabelValues = np.array(sys['number'][sys['ants6']==5])
grayLabelValues = np.concatenate((grayLabelValues, stemLabelValues))
grayLabels = np.copy(lblView)
grayLabels[grayMask==0]=0
if len(grayLabelValues) > 0:
    vol = [ (int(i),voxvol*float(np.sum(grayLabels==i))) for i in grayLabelValues ]
    print("Volumes")
    print(vol)

whiteLabels = np.copy(lblView)
whiteLabels[ whiteMask ==0 ] = 0
wmLabelValues = np.array(sys['number'][sys['ants6']==3])
if len(wmLabelValues) > 0:
    wmVols = [ (int(i),voxvol*float(np.sum(whiteLabels==i))) for i in wmLabelValues ]
    print("White matter volumes")
    print(wmVols)

# ROI Thickness measures
print("Cortical Thickness")
#ctx = [ (int(i),float(np.mean(thickView[lblView==i]))) for i in np.unique(lblView) ]
lblView[ thickView==0 ]=0
cortexLabelValues = np.array(sys['number'][sys['ants6']==1])
if len(cortexLabelValues) > 0:
    stats = [ ( qu.scalarStats(thickView[lblView==i], int(i), voxvol, "thickness") ) for i in cortexLabelValues ]
    print(stats)
