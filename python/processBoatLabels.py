from spaceNet import evalTools as eT
from spaceNet import geoTools as gT
from spaceNet import labelTools as lT
from spaceNet import dataTools as dT
import numpy as np
import sys
import multiprocessing
import time
import os
import pickle
from osgeo import ogr, gdal, osr

import cv2
from math import ceil
import math



if __name__ == "__main__":

    rasterFileName = '/Users/dlindenbaum/dataStorage/dgData/panamaCanal/Validation/WV02_10032015/wv02_10032015_R2C2_mask.tif'
    shapeFile = '/Users/dlindenbaum/dataStorage/dgData/panamaCanal/Validation/combinedTruthLine/TruthLine_BoatOnly_PanamaCanalValidate.shp'
    outputDirectory = '/Users/dlindenbaum/dataStorage/dgData/test'

    newGeoJson = shapeFile.replace('.shp', "full.geojson")
    lT.convertLabelStringToPoly(shapeFileSrc=shapeFile,outGeoJSon=shapeFile.replace('.shp', "full.geojson"), labelType='Boat')
    dT.chipImage(rasterFileName,
                 newGeoJson,
                 outputDirectory,
                 finalImageSize=256,
                 rotationList=np.arange(0,360,5),
                 rotateNorth=True,
                 windowSize='adjust')
