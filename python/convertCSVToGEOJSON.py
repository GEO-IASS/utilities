from spaceNet import evalTools as eT
from spaceNet import geoTools as gT
import numpy as np
import sys
import multiprocessing
import time
import os
from shutil import copyfile





if __name__ == "__main__":

    spaceNetDataDirectory = '/Users/dlindenbaum/cosmiQGit/spacenet/testData/'
    spaceNetRegion = 'AOI_0_TEST'
    csv_path3Band = '../testData/AOI_1_Rio_polygons_solution_3band.csv'
    csv_path8Band = '../testData/AOI_1_Rio_polygons_solution_8band.csv'
    geojsonfilename3band = csv_path3Band.replace('.csv', '.geojson')
    geojsonfilename8band = csv_path8Band.replace('.csv', '.geojson')
    public_3bandRasterLocation = os.path.join(spaceNetDataDirectory, spaceNetRegion, '3band')
    public_8bandRasterLocation = os.path.join(spaceNetDataDirectory, spaceNetRegion, '8band')
    public_geoJsonFileLocation = os.path.join(spaceNetDataDirectory, spaceNetRegion, 'vectorData', 'geoJson')
    public_summaryFileLocation = os.path.join(spaceNetDataDirectory, spaceNetRegion, 'vectorData', 'summaryData')


    buildinglist = gT.readwktcsv(csv_path3Band)
    gT.exporttogeojson(geojsonfilename3band, buildinglist)



    buildinglist = gT.readwktcsv(csv_path8Band)
    gT.exporttogeojson(geojsonfilename8band, buildinglist)


    # imageIDList = set([item['ImageId'] for item in buildinglist])
    #
    # for imageID in imageIDList:
    #
    #     print('startingCopying')
    #     imageIDRaster_3band = '3band_'+imageID+".tif"
    #     imageIDRaster_8band = '8band_' + imageID + ".tif"
    #     imageIDVector = imageID+"_Geo.geojson"
    #     truthJsonFp = ''.join(['/Users/dlindenbaum/cosmiQGit/spacenet/aws/AOI_1_Rio/vectorData/geoJson/', imageIDVector])
    #     inputRaster = ''.join(['/Users/dlindenbaum/cosmiQGit/spacenet/aws/AOI_1_Rio/3band/', imageIDRaster_3band])
    #     eightbandRaster = ''.join(['/Users/dlindenbaum/cosmiQGit/spacenet/aws/AOI_1_Rio/8band/', imageIDRaster_8band])
    #
    #
    #     # cp 3bandrasterFile to public/private and rename
    #     copyfile(inputRaster, os.path.join(public_3bandRasterLocation, imageIDRaster_3band))
    #
    #     # cp 8bandrasterFile to public/private and rename
    #     copyfile(eightbandRaster, os.path.join(public_8bandRasterLocation, imageIDRaster_8band))
    #
    #     # cp cpGeoJson to 3band/8band public/private
    #     copyfile(truthJsonFp, os.path.join(public_geoJsonFileLocation, imageIDVector))
    #
    # copyfile(geojsonfilename3band, os.path.join(public_summaryFileLocation, os.path.basename(geojsonfilename3band)))
    # copyfile(geojsonfilename8band, os.path.join(public_summaryFileLocation, os.path.basename(geojsonfilename8band)))
    # copyfile(csv_path3Band, os.path.join(public_summaryFileLocation, os.path.basename(csv_path3Band)))
    # copyfile(csv_path8Band, os.path.join(public_summaryFileLocation, os.path.basename(csv_path8Band)))



