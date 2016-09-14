from osgeo import gdal, osr, ogr
import numpy as np
import os
import csv
import subprocess
import math
try:
    import rtree
except:
    print("rtree not installed, Will break evaluation code")


def importgeojson(geojsonfilename):
    # driver = ogr.GetDriverByName('geojson')
    datasource = ogr.Open(geojsonfilename, 0)

    layer = datasource.GetLayer()
    print(layer.GetFeatureCount())

    polys = []
    for idx, feature in enumerate(layer):

        poly = feature.GetGeometryRef()

        if poly:
            polys.append({'ImageId': feature.GetField('ImageId'), 'BuildingId': feature.GetField('BuildingId'),
                          'poly': feature.GetGeometryRef().Clone()})

    return polys


def mergePolyList(geojsonfilename):

    multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)
    datasource = ogr.Open(geojsonfilename, 0)

    layer = datasource.GetLayer()
    print(layer.GetFeatureCount())


    for idx, feature in enumerate(layer):

        poly = feature.GetGeometryRef()

        if poly:

            multipolygon.AddGeometry(feature.GetGeometryRef().Clone())

    return multipolygon

def readwktcsv(csv_path):
    #
    # csv Format Expected = ['ImageId', 'BuildingId', 'PolygonWKT_Pix', 'PolygonWKT_Geo']
    # returns list of Dictionaries {'ImageId': image_id, 'BuildingId': building_id, 'poly': poly}
    # image_id is a string,
    # BuildingId is an integer,
    # poly is a ogr.Geometry Polygon

    # buildinglist = []
    # polys_df = pd.read_csv(csv_path)
    # image_ids = set(polys_df['ImageId'].tolist())
    # for image_id in image_ids:
    #    img_df = polys_df.loc[polys_df['ImageId'] == image_id]
    #    building_ids = set(img_df['BuildingId'].tolist())
    #    for building_id in building_ids:
    #
    #            building_df = img_df.loc[img_df['BuildingId'] == building_id]
    #            poly = ogr.CreateGeometryFromWkt(building_df.iloc[0, 2])
    #            buildinglist.append({'ImageId': image_id, 'BuildingId': building_id, 'poly': poly})
    buildinglist = []
    with open(csv_path, 'rb') as csvfile:
        building_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(building_reader, None)  # skip the headers
        for row in building_reader:
            poly = ogr.CreateGeometryFromWkt(row[2])
            buildinglist.append({'ImageId': row[0], 'BuildingId': int(row[1]), 'poly': poly})

    return buildinglist


def exporttogeojson(geojsonfilename, buildinglist):
    #
    # geojsonname should end with .geojson
    # building list should be list of dictionaries
    # list of Dictionaries {'ImageId': image_id, 'BuildingId': building_id, 'poly': poly}
    # image_id is a string,
    # BuildingId is an integer,
    # poly is a ogr.Geometry Polygon
    #
    # returns geojsonfilename

    driver = ogr.GetDriverByName('geojson')
    if os.path.exists(geojsonfilename):
        driver.DeleteDataSource(geojsonfilename)
    datasource = driver.CreateDataSource(geojsonfilename)
    layer = datasource.CreateLayer('buildings', geom_type=ogr.wkbPolygon)
    field_name = ogr.FieldDefn("ImageId", ogr.OFTString)
    field_name.SetWidth(75)
    layer.CreateField(field_name)
    layer.CreateField(ogr.FieldDefn("BuildingId", ogr.OFTInteger))

    # loop through buildings
    for building in buildinglist:
        # create feature
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetField("ImageId", building['ImageId'])
        feature.SetField("BuildingId", building['BuildingId'])
        feature.SetGeometry(building['poly'])

        # Create the feature in the layer (geojson)
        layer.CreateFeature(feature)
        # Destroy the feature to free resources
        feature.Destroy()

    datasource.Destroy()

    return geojsonfilename


def createmaskfrompolygons(polygons):
    pass


def latlon2pixel(lat, lon, input_raster='', targetsr='', geom_transform=''):
    # type: (object, object, object, object, object) -> object

    sourcesr = osr.SpatialReference()
    sourcesr.ImportFromEPSG(4326)

    geom = ogr.Geometry(ogr.wkbPoint)
    geom.AddPoint(lon, lat)

    if targetsr == '':
        src_raster = gdal.Open(input_raster)
        targetsr = osr.SpatialReference()
        targetsr.ImportFromWkt(src_raster.GetProjectionRef())
    coord_trans = osr.CoordinateTransformation(sourcesr, targetsr)
    if geom_transform == '':
        src_raster = gdal.Open(input_raster)
        transform = src_raster.GetGeoTransform()
    else:
        transform = geom_transform

    x_origin = transform[0]
    # print x_origin
    y_origin = transform[3]
    # print y_origin
    pixel_width = transform[1]
    # print pixel_width
    pixel_height = transform[5]
    # print pixel_height
    geom.Transform(coord_trans)
    # print geom.GetPoint()
    x_pix = (geom.GetPoint()[0] - x_origin) / pixel_width
    y_pix = (geom.GetPoint()[1] - y_origin) / pixel_height

    return (x_pix, y_pix)


def returnBoundBox(xOff, yOff, pixDim, inputRaster, targetSR='', pixelSpace=False):
    # Returns Polygon for a specific for a square defined by a center Pixel and
    # number of pixels in each dimension.
    # Leave targetSR as empty string '' or specify it as a osr.SpatialReference()
    # targetSR = osr.SpatialReference()
    # targetSR.ImportFromEPSG(4326)
    if targetSR == '':
        targetSR = osr.SpatialReference()
        targetSR.ImportFromEPSG(4326)
    xCord = [xOff - pixDim / 2, xOff - pixDim / 2, xOff + pixDim / 2,
             xOff + pixDim / 2, xOff - pixDim / 2]
    yCord = [yOff - pixDim / 2, yOff + pixDim / 2, yOff + pixDim / 2,
             yOff - pixDim / 2, yOff - pixDim / 2]

    ring = ogr.Geometry(ogr.wkbLinearRing)
    for idx in xrange(len(xCord)):
        if pixelSpace == False:
            geom = pixelToLatLon(xCord[idx], yCord[idx], inputRaster)
            ring.AddPoint(geom[0], geom[1], 0)
        else:
            ring.AddPoint(xCord[idx], yCord[idx], 0)

    poly = ogr.Geometry(ogr.wkbPolygon)
    if pixelSpace == False:
        poly.AssignSpatialReference(targetSR)

    poly.AddGeometry(ring)

    return poly

def createBoxFromLine(tmpGeom, ratio=1, halfWidth=-999, transformRequired=True, transform_WGS84_To_UTM='', transform_UTM_To_WGS84=''):
    if transformRequired:
        if transform_WGS84_To_UTM == '':
            transform_WGS84_To_UTM, transform_UTM_To_WGS84 = createUTMTransform(tmpGeom)

        tmpGeom.Transform(transform_WGS84_To_UTM)


    # calculatuate Centroid
    centroidX, centroidY, centroidZ = tmpGeom.Centroid().GetPoint()
    lengthM = tmpGeom.Length()
    if halfWidth ==-999:
        halfWidth = lengthM/(2*ratio)

    envelope=tmpGeom.GetPoints()
    cX1 = envelope[0][0]
    cY1 = envelope[0][1]
    cX2 = envelope[1][0]
    cY2 = envelope[1][1]
    angRad = math.atan2(cY2-cY1,cX2-cX1)

    d_X = math.cos(angRad-math.pi/2)*halfWidth
    d_Y = math.sin(angRad-math.pi/2)*halfWidth

    e_X = math.cos(angRad+math.pi/2)*halfWidth
    e_Y = math.sin(angRad+math.pi/2)*halfWidth

    ring = ogr.Geometry(ogr.wkbLinearRing)

    ring.AddPoint(cX1+d_X, cY1+d_Y)
    ring.AddPoint(cX1+e_X, cY1+e_Y)
    ring.AddPoint(cX2+e_X, cY2+e_Y)
    ring.AddPoint(cX2+d_X, cY2+d_Y)
    ring.AddPoint(cX1+d_X, cY1+d_Y)
    polyGeom = ogr.Geometry(ogr.wkbPolygon)
    polyGeom.AddGeometry(ring)
    areaM = polyGeom.GetArea()






    if transformRequired:
        tmpGeom.Transform(transform_UTM_To_WGS84)
        polyGeom.Transform(transform_UTM_To_WGS84)


    return (polyGeom, areaM, angRad, lengthM)


def pixelToLatLon(xPix, yPix, inputRaster, targetSR=''):
    if targetSR == '':
        targetSR = osr.SpatialReference()
        targetSR.ImportFromEPSG(4326)

    geom = ogr.Geometry(ogr.wkbPoint)
    srcRaster = gdal.Open(inputRaster)
    source_sr = osr.SpatialReference()
    source_sr.ImportFromWkt(srcRaster.GetProjectionRef())
    coord_trans = osr.CoordinateTransformation(source_sr, targetSR)

    transform = srcRaster.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]

    xCoord = (xPix * pixelWidth) + xOrigin
    yCoord = (yPix * pixelHeight) + yOrigin
    geom.AddPoint(xCoord, yCoord)
    geom.Transform(coord_trans)
    return (geom.GetX(), geom.GetY())


def geoPolygonToPixelPolygonWKT(geom, inputRaster, targetSR, geomTransform):
    # Returns Pixel Coordinate List and GeoCoordinateList

    polygonPixBufferList = []
    polygonPixBufferWKTList = []
    if geom.GetGeometryName() == 'POLYGON':
        polygonPix = ogr.Geometry(ogr.wkbPolygon)
        for ring in geom:
            # GetPoint returns a tuple not a Geometry
            ringPix = ogr.Geometry(ogr.wkbLinearRing)

            for pIdx in xrange(ring.GetPointCount()):
                lon, lat, z = ring.GetPoint(pIdx)
                xPix, yPix = latlon2pixel(lat, lon, inputRaster, targetSR, geomTransform)
                ringPix.AddPoint(xPix, yPix)

            polygonPix.AddGeometry(ringPix)
            polygonPixBuffer = polygonPix.Buffer(0.0)
            polygonPixBufferList.append([polygonPixBuffer, geom])

    elif geom.GetGeometryName() == 'MULTIPOLYGON':

        for poly in geom:
            polygonPix = ogr.Geometry(ogr.wkbPolygon)
            for ring in geom:
                # GetPoint returns a tuple not a Geometry
                ringPix = ogr.Geometry(ogr.wkbLinearRing)

                for pIdx in xrange(ring.GetPointCount()):
                    lon, lat, z = ring.GetPoint(pIdx)
                    xPix, yPix = latlon2pixel(lat, lon, inputRaster, targetSR, geomTransform)
                    ringPix.AddPoint(xPix, yPix)

                polygonPix.AddGeometry(ringPix)
                polygonPixBuffer = polygonPix.Buffer(0.0)
                polygonPixBufferList.append([polygonPixBuffer, geom])

    for polygonTest in polygonPixBufferList:
        if polygonTest[0].GetGeometryName() == 'POLYGON':
            polygonPixBufferWKTList.append([polygonTest[0].ExportToWkt(), polygonTest[1].ExportToWkt()])
        elif polygonTest[0].GetGeometryName() == 'MULTIPOLYGON':
            for polygonTest2 in polygonTest[0]:
                polygonPixBufferWKTList.append([polygonTest2.ExportToWkt(), polygonTest[1].ExportToWkt()])

    return polygonPixBufferWKTList

def geoWKTToPixelWKT(geom, inputRaster, targetSR, geomTransform):
    # Returns Pixel Coordinate List and GeoCoordinateList

    geom_list = []
    geom_pix_wkt_list = []
    if geom.GetGeometryName() == 'POLYGON':
        polygonPix = ogr.Geometry(ogr.wkbPolygon)
        for ring in geom:
            # GetPoint returns a tuple not a Geometry
            ringPix = ogr.Geometry(ogr.wkbLinearRing)

            for pIdx in xrange(ring.GetPointCount()):
                lon, lat, z = ring.GetPoint(pIdx)
                xPix, yPix = latlon2pixel(lat, lon, inputRaster, targetSR, geomTransform)
                ringPix.AddPoint(xPix, yPix)

            polygonPix.AddGeometry(ringPix)
            polygonPixBuffer = polygonPix.Buffer(0.0)
            geom_list.append([polygonPixBuffer, geom])

    elif geom.GetGeometryName() == 'MULTIPOLYGON':

        for poly in geom:
            polygonPix = ogr.Geometry(ogr.wkbPolygon)
            for ring in geom:
                # GetPoint returns a tuple not a Geometry
                ringPix = ogr.Geometry(ogr.wkbLinearRing)

                for pIdx in xrange(ring.GetPointCount()):
                    lon, lat, z = ring.GetPoint(pIdx)
                    xPix, yPix = latlon2pixel(lat, lon, inputRaster, targetSR, geomTransform)
                    ringPix.AddPoint(xPix, yPix)

                polygonPix.AddGeometry(ringPix)
                polygonPixBuffer = polygonPix.Buffer(0.0)
                geom_list.append([polygonPixBuffer, geom])
    elif geom.GetGeometryName() == 'LINESTRING':
        line = ogr.Geometry(ogr.wkbLineString)
        for pIdx in xrange(geom.GetPointCount()):
            lon, lat, z = geom.GetPoint(pIdx)
            xPix, yPix = latlon2pixel(lat, lon, inputRaster, targetSR, geomTransform)
            line.AddPoint(xPix, yPix)
        geom_list.append([line, geom])

    elif geom.GetGeometryName() == 'POINT':
        point = ogr.Geometry(ogr.wkbPoint)
        for pIdx in xrange(geom.GetPointCount()):
            lon, lat, z = geom.GetPoint(pIdx)
            xPix, yPix = latlon2pixel(lat, lon, inputRaster, targetSR, geomTransform)
            point.AddPoint(xPix, yPix)
        geom_list.append([point, geom])


    for polygonTest in geom_list:
        if polygonTest[0].GetGeometryName() == 'POLYGON' or \
                        polygonTest[0].GetGeometryName() == 'LINESTRING' or \
                        polygonTest[0].GetGeometryName() == 'POINT':
            geom_pix_wkt_list.append([polygonTest[0].ExportToWkt(), polygonTest[1].ExportToWkt()])
        elif polygonTest[0].GetGeometryName() == 'MULTIPOLYGON':
            for polygonTest2 in polygonTest[0]:
                geom_pix_wkt_list.append([polygonTest2.ExportToWkt(), polygonTest[1].ExportToWkt()])

    return geom_pix_wkt_list


def convert_wgs84geojson_to_pixgeojson(wgs84geojson, inputraster, image_id=[], pixelgeojson=[], only_polygons=True):
    dataSource = ogr.Open(wgs84geojson, 0)
    layer = dataSource.GetLayer()
    print(layer.GetFeatureCount())
    building_id = 0
    # check if geoJsonisEmpty
    buildinglist = []
    if not image_id:
        image_id = inputraster.replace(".tif", "")

    if layer.GetFeatureCount() > 0:
        srcRaster = gdal.Open(inputraster)
        targetSR = osr.SpatialReference()
        targetSR.ImportFromWkt(srcRaster.GetProjectionRef())
        geomTransform = srcRaster.GetGeoTransform()

        for feature in layer:

            geom = feature.GetGeometryRef()

            ## Calculate 3 band
            if only_polygons:
                geom_wkt_list = geoPolygonToPixelPolygonWKT(geom, inputraster, targetSR, geomTransform)
            else:
                geom_wkt_list = geoWKTToPixelWKT(geom, inputraster, targetSR, geomTransform)

            for geom_wkt in geom_wkt_list:
                building_id += 1
                buildinglist.append({'ImageId': image_id,
                                     'BuildingId': building_id,
                                     'poly': ogr.CreateGeometryFromWkt(geom_wkt[0])
                                     })

    if pixelgeojson:
        exporttogeojson(pixelgeojson, buildinglist=buildinglist)

    return buildinglist


def create_rtreefromdict(buildinglist):
    # create index
    index = rtree.index.Index(interleaved=False)
    for idx, building in enumerate(buildinglist):
        index.insert(idx, building['poly'].GetEnvelope())

    return index


def create_rtree_from_poly(poly_list):
    # create index
    index = rtree.index.Index(interleaved=False)
    for idx, building in enumerate(poly_list):
        index.insert(idx, building.GetEnvelope())

    return index


def search_rtree(test_building, index):
    # input test poly ogr.Geometry  and rtree index
    if test_building.GetGeometryName() == 'POLYGON' or \
                    test_building.GetGeometryName() == 'MULTIPOLYGON':
        fidlist = index.intersection(test_building.GetEnvelope())
    else:
        fidlist = []

    return fidlist


def get_envelope(poly):
    env = poly.GetEnvelope()

    # Get Envelope returns a tuple (minX, maxX, minY, maxY)
    # Create ring
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(env[0], env[2])
    ring.AddPoint(env[0], env[3])
    ring.AddPoint(env[1], env[3])
    ring.AddPoint(env[1], env[2])
    ring.AddPoint(env[0], env[2])

    # Create polygon
    poly1 = ogr.Geometry(ogr.wkbPolygon)
    poly1.AddGeometry(ring)

    return poly1

def utm_getZone(longitude):
    return (int(1+(longitude+180.0)/6.0))


def utm_isNorthern(latitude):
    if (latitude < 0.0):
        return 0
    else:
        return 1


def createUTMTransform(polyGeom):
    # pt = polyGeom.Boundary().GetPoint()
    utm_zone = utm_getZone(polyGeom.GetEnvelope()[0])
    is_northern = utm_isNorthern(polyGeom.GetEnvelope()[2])
    utm_cs = osr.SpatialReference()
    utm_cs.SetWellKnownGeogCS('WGS84')
    utm_cs.SetUTM(utm_zone, is_northern);
    wgs84_cs = osr.SpatialReference()
    wgs84_cs.ImportFromEPSG(4326)

    transform_WGS84_To_UTM = osr.CoordinateTransformation(wgs84_cs, utm_cs)
    transform_UTM_To_WGS84 = osr.CoordinateTransformation(utm_cs, wgs84_cs)

    return transform_WGS84_To_UTM, transform_UTM_To_WGS84, utm_cs


def getRasterExtent(srcImage):
    geoTrans = srcImage.GetGeoTransform()
    ulX = geoTrans[0]
    ulY = geoTrans[3]
    xDist = geoTrans[1]
    yDist = geoTrans[5]
    rtnX = geoTrans[2]
    rtnY = geoTrans[4]

    cols = srcImage.RasterXSize
    rows = srcImage.RasterYSize

    lrX = ulX + xDist * cols
    lrY = ulY + yDist * rows

    # Create ring
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(lrX, lrY)
    ring.AddPoint(lrX, ulY)
    ring.AddPoint(ulX, ulY)
    ring.AddPoint(ulX, lrY)
    ring.AddPoint(lrX, lrY)

    # Create polygon
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)

    return geoTrans, poly, ulX, ulY, lrX, lrY


def createPolygonFromCorners(lrX,lrY,ulX, ulY):
    # Create ring
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(lrX, lrY)
    ring.AddPoint(lrX, ulY)
    ring.AddPoint(ulX, ulY)
    ring.AddPoint(ulX, lrY)
    ring.AddPoint(lrX, lrY)

    # Create polygon
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)

    return poly


def clipShapeFile(shapeSrc, outputFileName, polyToCut, minpartialPerc=0.0, debug=False):

    source_layer = shapeSrc.GetLayer()
    source_srs = source_layer.GetSpatialRef()
    # Create the output Layer
    outGeoJSon = outputFileName.replace('.tif', '.geojson')
    outDriver = ogr.GetDriverByName("geojson")
    if os.path.exists(outGeoJSon):
        outDriver.DeleteDataSource(outGeoJSon)

    if debug:
        outGeoJSonDebug = outputFileName.replace('.tif', 'outline.geojson')
        outDriverDebug = ogr.GetDriverByName("geojson")
        if os.path.exists(outGeoJSonDebug):
            outDriverDebug.DeleteDataSource(outGeoJSonDebug)
        outDataSourceDebug = outDriver.CreateDataSource(outGeoJSonDebug)
        outLayerDebug = outDataSourceDebug.CreateLayer("groundTruth", source_srs, geom_type=ogr.wkbPolygon)

        outFeatureDebug = ogr.Feature(source_layer.GetLayerDefn())
        outFeatureDebug.SetGeometry(polyToCut)
        outLayerDebug.CreateFeature(outFeatureDebug)


    outDataSource = outDriver.CreateDataSource(outGeoJSon)
    outLayer = outDataSource.CreateLayer("groundTruth", source_srs, geom_type=ogr.wkbPolygon)
    # Add input Layer Fields to the output Layer
    inLayerDefn = source_layer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)
    outLayer.CreateField(ogr.FieldDefn("partialBuilding", ogr.OFTReal))
    outLayer.CreateField(ogr.FieldDefn("partialDec", ogr.OFTReal))
    outLayerDefn = outLayer.GetLayerDefn()
    source_layer.SetSpatialFilter(polyToCut)
    for inFeature in source_layer:

        outFeature = ogr.Feature(outLayerDefn)

        for i in range (0, inLayerDefn.GetFieldCount()):
            outFeature.SetField(inLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))

        geom = inFeature.GetGeometryRef()
        geomNew = geom.Intersection(polyToCut)
        partialDec = -1
        if geomNew:
            partialDec = geomNew.GetArea() / geom.GetArea()
            outFeature.SetField("partialDec", partialDec)
            if geom.GetArea() == geomNew.GetArea():
                outFeature.SetField("partialBuilding", 0)
            else:
                outFeature.SetField("partialBuilding", 1)
        else:
            outFeature.SetField("partialBuilding", 1)


        outFeature.SetGeometry(geomNew)
        if partialDec >= minpartialPerc:
            outLayer.CreateFeature(outFeature)
            print ("AddFeature")
        else:
            print("PartialPercent={}".format(partialDec))


def cutChipFromMosaic(rasterFile, shapeFileSrc, outlineSrc='',outputDirectory='', outputPrefix='clip_',
                      clipSizeMX=100, clipSizeMY=100, clipOverlap=0.0, minpartialPerc=0.0, createPix=False):

    srcImage = gdal.Open(rasterFile)
    geoTrans, poly, ulX, ulY, lrX, lrY = getRasterExtent(srcImage)
    rasterFileBase = os.path.basename(rasterFile)
    if outputDirectory=="":
        outputDirectory=os.path.dirname(rasterFile)
    transform_WGS84_To_UTM, transform_UTM_To_WGS84, utm_cs = createUTMTransform(poly)
    poly.Transform(transform_WGS84_To_UTM)
    env = poly.GetEnvelope()
    minX = env[0]
    minY = env[2]
    maxX = env[1]
    maxY = env[3]

    #return poly to WGS84
    poly.Transform(transform_UTM_To_WGS84)

    shapeSrc = ogr.Open(shapeFileSrc,0)
    if outlineSrc == '':
        geomOutline = poly
    else:
        outline = ogr.Open(outlineSrc)
        layer = outline.GetLayer()
        featureOutLine = layer.GetFeature(0)
        geomOutlineBase = featureOutLine.GetGeometryRef()
        geomOutline = geomOutlineBase.Intersection(poly)



    for llX in np.arange(minX, maxX, clipSizeMX*(1.0-clipOverlap)):
        for llY in np.arange(minY, maxY, clipSizeMY*(1.0-clipOverlap)):
            uRX = llX+clipSizeMX
            uRY = llY+clipSizeMY

            polyCut = createPolygonFromCorners(llX, llY, uRX, uRY)
            polyCut.Transform(transform_UTM_To_WGS84)
            if (polyCut).Intersects(geomOutline):
                print "Do it."
                envCut = polyCut.GetEnvelope()
                minXCut = envCut[0]
                minYCut = envCut[2]
                maxXCut = envCut[1]
                maxYCut = envCut[3]
                polyCutWGS = createPolygonFromCorners(minXCut, minYCut, maxXCut, maxYCut)
                outputFileName = os.path.join(outputDirectory, outputPrefix+rasterFileBase.replace('.tif', "_{}_{}.tif".format(minXCut,minYCut)))
                ## Clip Image
                subprocess.call(["gdalwarp", "-te", "{}".format(minXCut), "{}".format(minYCut),
                                 "{}".format(maxXCut),  "{}".format(maxYCut), rasterFile, outputFileName])
                outGeoJson = outputFileName.replace('.tif', '.geojson')
                ### Clip poly to cust to Raster Extent
                polyVectorCut=polyCutWGS.Intersection(poly)
                clipShapeFile(shapeSrc, outputFileName, polyVectorCut, minpartialPerc=minpartialPerc)

                if createPix:
                    #print('outGeoJson_{}'.format(outGeoJson))
                    #print('outputFileName_{}'.format(outputFileName))
                    convert_wgs84geojson_to_pixgeojson(outGeoJson, outputFileName, pixelgeojson=outGeoJson.replace('.geojson', '_PIX.geojson'))

def cutChipFromRasterCenter(rasterFile, shapeFileSrc, outlineSrc='',outputDirectory='', outputPrefix='clip_',
                      clipSizeMin=1, clipSizeSquare=True, bufferPerc=1.3, createPix=False):
    srcImage = gdal.Open(rasterFile)
    geoTrans, poly, ulX, ulY, lrX, lrY = getRasterExtent(srcImage)
    rasterFileBase = os.path.basename(rasterFile)
    if outputDirectory == "":
        outputDirectory = os.path.dirname(rasterFile)
    transform_WGS84_To_UTM, transform_UTM_To_WGS84, utm_cs = createUTMTransform(poly)
    poly.Transform(transform_WGS84_To_UTM)
    env = poly.GetEnvelope()
    minX = env[0]
    minY = env[2]
    maxX = env[1]
    maxY = env[3]

    # return poly to WGS84
    poly.Transform(transform_UTM_To_WGS84)

    shapeSrc = ogr.Open(shapeFileSrc, 0)
    if outlineSrc == '':
        geomOutline = poly
    else:
        outline = ogr.Open(outlineSrc)
        layer = outline.GetLayer()
        featureOutLine = layer.GetFeature(0)
        geomOutlineBase = featureOutLine.GetGeometryRef()
        geomOutline = geomOutlineBase.Intersection(poly)

    shapeSrcBase = ogr.Open(shapeFileSrc, 0)
    layerBase = shapeSrcBase.GetLayer()
    layerBase.SetSpatialFilter(geomOutline)

    for feature in layerBase:
        featureGeom = feature.GetGeometryRef()
        geomEnv = featureGeom.GetEnvelope()



def createMaskedMosaic(input_raster, output_raster, outline_file):

    subprocess.call(["gdalwarp", "-q", "-cutline", outline_file, "-of", "GTiff", input_raster, output_raster])


