from osgeo import gdal, osr, ogr, gdalnumeric
import numpy as np
import os
import geoTools as gT
import math
import cPickle as pickle
import csv
import glob


def evaluateLineStringPlane(geom, label='Airplane'):
    ring = ogr.Geometry(ogr.wkbLinearRing)

    for i in range(0, geom.GetPointCount()):
        # GetPoint returns a tuple not a Geometry
        pt = geom.GetPoint(i)
        ring.AddPoint(pt[0], pt[1])
    pt = geom.GetPoint(0)
    ring.AddPoint(pt[0], pt[1])
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)

    transform_WGS84_To_UTM, transform_UTM_To_WGS84, utm_cs = gT.createUTMTransform(geom)
    geom.Transform(transform_WGS84_To_UTM)
    pt0 = geom.GetPoint(0) # Tail
    pt1 = geom.GetPoint(1) # Wing
    pt2 = geom.GetPoint(2) # Nose
    pt3 = geom.GetPoint(3) # Wing
    Length = math.sqrt((pt2[0]-pt0[0])**2 + (pt2[1]-pt0[1])**2)
    Width = math.sqrt((pt3[0] - pt1[0])**2 + (pt3[1] - pt1[1])**2)
    Aspect = Length/Width
    Direction = (math.atan2(pt2[0]-pt0[0], pt2[1]-pt0[1])*180/math.pi) % 360


    geom.Transform(transform_UTM_To_WGS84)

    return [poly, Length, Width, Aspect, Direction]

def evaluateLineStringBoat(geom, label='Boat', aspectRatio=3):


    transform_WGS84_To_UTM, transform_UTM_To_WGS84, utm_cs = gT.createUTMTransform(geom)

    geom.Transform(transform_WGS84_To_UTM)
    pt0 = geom.GetPoint(0) # Stern
    pt1 = geom.GetPoint(1) # Bow
    Length = math.sqrt((pt1[0]-pt0[0])**2 + (pt1[1]-pt0[1])**2)
    Direction = (math.atan2(pt1[0]-pt0[0], pt1[1]-pt0[1])*180/math.pi) % 360
    geom.Transform(transform_UTM_To_WGS84)

    poly, areaM, angRad, lengthM = gT.createBoxFromLine(geom, aspectRatio,
                                                              transformRequired=True,
                                                              transform_WGS84_To_UTM=transform_WGS84_To_UTM,
                                                              transform_UTM_To_WGS84=transform_UTM_To_WGS84)

    Width = Length/aspectRatio
    Aspect = aspectRatio

    return [poly, Length, Width, Aspect, Direction]


def convertLabelStringToPoly(shapeFileSrc, outGeoJSon, labelType='Airplane'):

        shapeSrc = ogr.Open(shapeFileSrc)
        source_layer = shapeSrc.GetLayer()
        source_srs = source_layer.GetSpatialRef()
        # Create the output Layer
        outDriver = ogr.GetDriverByName("geojson")
        if os.path.exists(outGeoJSon):
            outDriver.DeleteDataSource(outGeoJSon)


        outDataSource = outDriver.CreateDataSource(outGeoJSon)
        outLayer = outDataSource.CreateLayer("groundTruth", source_srs, geom_type=ogr.wkbPolygon)
        # Add input Layer Fields to the output Layer
        inLayerDefn = source_layer.GetLayerDefn()
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            outLayer.CreateField(fieldDefn)
        outLayer.CreateField(ogr.FieldDefn("Length_m", ogr.OFTReal))
        outLayer.CreateField(ogr.FieldDefn("Width_m", ogr.OFTReal))
        outLayer.CreateField(ogr.FieldDefn("Aspect(L/W)", ogr.OFTReal))
        outLayer.CreateField(ogr.FieldDefn("compassDeg", ogr.OFTReal))

        outLayerDefn = outLayer.GetLayerDefn()
        for inFeature in source_layer:

            outFeature = ogr.Feature(outLayerDefn)

            for i in range(0, inLayerDefn.GetFieldCount()):
                outFeature.SetField(inLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))

            geom = inFeature.GetGeometryRef()
            if labelType == 'Airplane':
                poly, Length, Width, Aspect, Direction = evaluateLineStringPlane(geom, label='Airplane')
            elif labelType == 'Boat':
                poly, Length, Width, Aspect, Direction = evaluateLineStringBoat(geom, label='Boat')

            outFeature.SetGeometry(poly)
            outFeature.SetField("Length_m", Length)
            outFeature.SetField("Width_m", Width)
            outFeature.SetField("Aspect(L/W)", Aspect)
            outFeature.SetField("compassDeg", Direction)

            outLayer.CreateFeature(outFeature)


def createTruthPixelLinePickle(truthLineFile, pickleLocation=''):
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


def createTruthPixelPolyPickle(truthPoly, pickleLocation=''):
    # returns dictionary with list of minX, maxX, minY, maxY

    if pickleLocation=='':
        extension = os.path.splitext(truthPoly)[1]
        pickleLocation = truthPoly.replace(extension, 'PixPoly.p')
    if truthPoly != '':
        # get Source Line File Information
        shapef = ogr.Open(truthPoly, 0)
        truthLayer = shapef.GetLayer()
        envList = []

        for tmpFeature in truthLayer:
            tmpGeom = tmpFeature.GetGeometryRef()
            env = tmpGeom.GetEvnelope()
            envList.append(env)

        envArray = np.asarray(envList)
        envelopeData = {'minX': envArray[:,0],
                        'maxX': envArray[:,1],
                        'minY': envArray[:,2],
                        'maxY': envArray[:,3]
                        }


        with open(pickleLocation, 'wb') as f:
            pickle.dump(envelopeData, f)
            # get Source Line File Information


def createNPPixArray(rasterSrc, vectorSrc, npDistFileName='', units='pixels'):

    ## open source vector file that truth data
    source_ds = ogr.Open(vectorSrc)
    source_layer = source_ds.GetLayer()

    ## extract data from src Raster File to be emulated
    ## open raster file that is to be emulated
    srcRas_ds = gdal.Open(rasterSrc)
    cols = srcRas_ds.RasterXSize
    rows = srcRas_ds.RasterYSize
    noDataValue = 0

    if units=='meters':
        geoTrans, poly, ulX, ulY, lrX, lrY = gT.getRasterExtent(srcRas_ds)
        transform_WGS84_To_UTM, transform_UTM_To_WGS84, utm_cs = gT.createUTMTransform(poly)
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint(geoTrans[0], geoTrans[3])
        line.AddPoint(geoTrans[0]+geoTrans[1], geoTrans[3])

        line.Transform(transform_WGS84_To_UTM)
        metersIndex = line.Length()
    else:
        metersIndex = 1

    ## create First raster memory layer
    memdrv = gdal.GetDriverByName('MEM')
    dst_ds = memdrv.Create('', cols, rows, 1, gdal.GDT_Byte)
    dst_ds.SetGeoTransform(srcRas_ds.GetGeoTransform())
    dst_ds.SetProjection(srcRas_ds.GetProjection())
    band = dst_ds.GetRasterBand(1)
    band.SetNoDataValue(noDataValue)

    gdal.RasterizeLayer(dst_ds, [1], source_layer, burn_values=[255])
    srcBand = dst_ds.GetRasterBand(1)

    memdrv2 = gdal.GetDriverByName('MEM')
    prox_ds = memdrv2.Create('', cols, rows, 1, gdal.GDT_Int16)
    prox_ds.SetGeoTransform(srcRas_ds.GetGeoTransform())
    prox_ds.SetProjection(srcRas_ds.GetProjection())
    proxBand = prox_ds.GetRasterBand(1)
    proxBand.SetNoDataValue(noDataValue)

    options = ['NODATA=0']

    gdal.ComputeProximity(srcBand, proxBand, options)

    memdrv3 = gdal.GetDriverByName('MEM')
    proxIn_ds = memdrv3.Create('', cols, rows, 1, gdal.GDT_Int16)
    proxIn_ds.SetGeoTransform(srcRas_ds.GetGeoTransform())
    proxIn_ds.SetProjection(srcRas_ds.GetProjection())
    proxInBand = proxIn_ds.GetRasterBand(1)
    proxInBand.SetNoDataValue(noDataValue)
    options = ['NODATA=0', 'VALUES=0']
    gdal.ComputeProximity(srcBand, proxInBand, options)

    proxIn = gdalnumeric.BandReadAsArray(proxInBand)
    proxOut = gdalnumeric.BandReadAsArray(proxBand)

    proxTotal = proxIn.astype(float) - proxOut.astype(float)
    proxTotal = proxTotal*metersIndex

    if npDistFileName != '':
        np.save(npDistFileName, proxTotal)

    return proxTotal


def createGeoJSONFromRaster(geoJsonFileName, array2d, geom, proj,
                            layerName="BuildingID",
                            fieldName="BuildingID"):

    memdrv = gdal.GetDriverByName('MEM')
    src_ds = memdrv.Create('', array2d.shape[1], array2d.shape[0], 1)
    src_ds.SetGeoTransform(geom)
    src_ds.SetProjection(proj)
    band = src_ds.GetRasterBand(1)
    band.WriteArray(array2d)

    dst_layername = "BuildingID"
    drv = ogr.GetDriverByName("geojson")
    dst_ds = drv.CreateDataSource(geoJsonFileName)
    dst_layer = dst_ds.CreateLayer(layerName, srs=None)

    fd = ogr.FieldDefn(fieldName, ogr.OFTInteger)
    dst_layer.CreateField(fd)
    dst_field = 1

    gdal.Polygonize(band, None, dst_layer, dst_field, [], callback=None)

    return


def createCSVSummaryFile(chipSummaryList, outputFileName, outputdirectory=''):


    with open(outputFileName, 'wb') as csvfile:
        writerTotal = csv.writer(csvfile, delimiter=',', lineterminator='\n')

        writerTotal.writerow(['ImageId', 'BuildingId', 'PolygonWKT_Pix', 'PolygonWKT_Geo'])

        for chipSummary in chipSummaryList:
            chipName = chipSummary['chipName']
            geoVectorName = chipSummary['geoVectorName']
            pixVectorName = chipSummary['pixVectorName']
            buildingList = gT.convert_wgs84geojson_to_pixgeojson(geoVectorName,
                                                                 os.path.join(outputdirectory,chipName))
            if len(buildingList) > 0:
                for building in buildingList:
                    writerTotal.writerow([os.path.basename(building['ImageId']), building['BuildingId'],
                                          building['polyPix'], building['polyGeo']])
            else:
                writerTotal.writerow([os.path.basename(chipName), -1,
                                      'POLYGON((0 0, 0 0, 0 0, 0 0))', 'POLYGON ((0 0, 0 0, 0 0, 0 0))'])



def createCSVSummaryFileFromJsonList(geoJsonList, outputFileName, chipnameList=[],
                                     input='Geo'):

    if chipnameList:
        pass
    else:
        for geoJson in geoJsonList:
            chipnameList.append(os.path.basename(os.path.splitext(geoJson)[0]))



    with open(outputFileName, 'wb') as csvfile:
        writerTotal = csv.writer(csvfile, delimiter=',', lineterminator='\n')

        writerTotal.writerow(['ImageId', 'BuildingId', 'PolygonWKT_Pix', 'PolygonWKT_Geo'])

        for geoVectorName, chipName in zip(geoJsonList, chipnameList):

            buildingList = gT.convert_wgs84geojson_to_pixgeojson(geoVectorName, '',
                                                                 image_id=chipName)
            if len(buildingList) > 0:
                for building in buildingList:
                    writerTotal.writerow([os.path.basename(building['ImageId']), building['BuildingId'],
                                          building['polyPix'], building['polyGeo']])
            else:
                writerTotal.writerow([os.path.basename(chipName), -1,
                                  'POLYGON((0 0, 0 0, 0 0, 0 0))', 'POLYGON ((0 0, 0 0, 0 0, 0 0))'])














