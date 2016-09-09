from spaceNet import evalTools as eT
from spaceNet import geoTools as gT
import numpy as np
import sys
import multiprocessing
import time
import os
import pickle
from osgeo import ogr
from spaceNet import labelTools as lT


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

        lT.createTruthPixelPickle(pixelgeojson, pickleLocation='')




