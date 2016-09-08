from spaceNet import evalTools as eT
from spaceNet import geoTools as gT
import numpy as np
import sys
import multiprocessing
import time
import os
import pickle
from osgeo import ogr

def createTruthPixelPickle(truthLineFile, pickleLocation=''):
    if pickleLocation=='':
        extension = os.path.splitext(truthLineFile)[1]
        pickleLocation = truthLineFile.replace(extension, 'Pixline.p')
    if truthLineFile != '':
        # get Source Line File Information
        shapef = ogr.Open(truthLineFile, 0)
        truthLayer = shapef.GetLayer()
        pt1X = []
        pt1Y = []
        pt2X = []
        pt2Y = []
        for tmpFeature in truthLayer:
            tmpGeom = tmpFeature.GetGeometryRef()
            for i in range(0, tmpGeom.GetPointCount()):
                pt = tmpGeom.GetPoint(i)

                if i == 0:
                    pt1X.append(pt[0])
                    pt1Y.append(pt[1])
                elif i == 1:
                    pt2X.append(pt[0])
                    pt2Y.append(pt[1])

        lineData = {'pt1X': np.asarray(pt1X),
                    'pt1Y': np.asarray(pt1Y),
                    'pt2X': np.asarray(pt2X),
                    'pt2Y': np.asarray(pt2Y)
                    }

        with open(pickleLocation, 'wb') as f:
            pickle.dump(lineData, f)
            # get Source Line File Information

if __name__ == "__main__":

    if len(sys.argv) > 1:
        truth_fp = sys.argv[1]
        test_fp = sys.argv[2]
    else:
        test_fp = '../testData/public_polygons_solution_3Band_envelope.geojson'
        truth_fp = '../testData/public_polygons_solution_3Band.geojson'

    wgs84List = ['/Users/dlindenbaum/dataStorage/dgData/panamaCanal/Validation/localizationValidationRegions/AOI1_lines.shp',
                 '/Users/dlindenbaum/dataStorage/dgData/panamaCanal/Validation/localizationValidationRegions/AOI2_lines.shp',
                 '/Users/dlindenbaum/dataStorage/dgData/panamaCanal/Validation/localizationValidationRegions/AOI3_lines.shp',
                 '/Users/dlindenbaum/dataStorage/dgData/panamaCanal/Validation/localizationValidationRegions/AOI4_lines.shp']

    rasterList = ['/Users/dlindenbaum/dataStorage/dgData/panamaCanal/Validation/localizationValidationRegions/AOI1.tif',
                 '/Users/dlindenbaum/dataStorage/dgData/panamaCanal/Validation/localizationValidationRegions/AOI2.tif',
                 '/Users/dlindenbaum/dataStorage/dgData/panamaCanal/Validation/localizationValidationRegions/AOI3.tif',
                 '/Users/dlindenbaum/dataStorage/dgData/panamaCanal/Validation/localizationValidationRegions/AOI4.tif']

    for wgs84geojson, inputraster in zip(wgs84List, rasterList):
        pixelgeojson = wgs84geojson.replace('.shp', '_PIX.geojson')
        gT.convert_wgs84geojson_to_pixgeojson(wgs84geojson, inputraster, image_id=os.path.basename(inputraster.replace(".tif",'')), pixelgeojson=pixelgeojson,
                                           only_polygons=False)

        createTruthPixelPickle(pixelgeojson, pickleLocation='')




