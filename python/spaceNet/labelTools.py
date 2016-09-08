from osgeo import gdal, osr, ogr
import numpy as np
import os
import csv
import rtree
import subprocess
import geoTools as gT
import evalTools as eT
import math

def evaluateLineStringPlane(geom, label='plane'):
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
    Direction = math.atan2(pt2[1]-pt0[1], pt2[0]-pt0[0])*180/math.pi


    geom.Transform(transform_UTM_To_WGS84)

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
            poly, Length, Width, Aspect, Direction = evaluateLineStringPlane(geom, label='plane')

            outFeature.SetGeometry(poly)
            outFeature.SetField("Length_m", Length)
            outFeature.SetField("Width_m", Length)
            outFeature.SetField("Aspect(L/W)", Length)
            outFeature.SetField("compassDeg", Length)

            outLayer.CreateFeature(outFeature)


if __name__ == '__main__':


    srcVectorFile = '/Users/dlindenbaum/dataStorage/dgData/Airports/sample_polygon_labels/054841475060_01_assembly_2_3_LondonHeathrow_airplane.shp'
    dstVectorFile = '/Users/dlindenbaum/dataStorage/dgData/Airports/sample_polygon_labels/054841475060_01_assembly_2_3_LondonHeathrow_airplanePoly.geojson'
    srcRasterFile = '/Users/dlindenbaum/dataStorage/dgData/Airports/sample_polygon_labels/054841475060_01_assembly_2_3_LondonHeathrow.tif'

    convertLabelStringToPoly(srcVectorFile, dstVectorFile, labelType='Airplane')


