import json
from shapely.geometry import LineString, Polygon, LinearRing, shape, Point
import gdal, ogr, osr, gdalnumeric
import numpy as np
import matplotlib.pyplot as plt
import sys

vectorSrc = '/Users/dlindenbaum/cosmiQGit/spaceNetUtilities/testData/AOI_0_TEST/vectorData/geoJson/013022223130_Public_img8_Geo.geojson'
rasterSrc = '/Users/dlindenbaum/cosmiQGit/spaceNetUtilities/testData/AOI_0_TEST/8band/8band_013022223130_Public_img8.tif'

fn = sys.argv[1]
path = '/raid/data/spacenetFromAWS_08122016/processedData/'
print fn
#fn = '013022223130_Public_img111'

def Pixel2World ( geoMatrix, i , j ):
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    rtnX = geoMatrix[2]
    rtnY = geoMatrix[4]
   
    return(1.0 * i * xDist  + ulX, -1.0 * j * xDist + ulY)

#ds8 = gdal.Open(path+'8band/'+'8band_'+fn+'.tif')
#ds3 = gdal.Open(path+'3band/'+'3band_'+fn+'.tif')

ds8 = gdal.Open(rasterSrc)
print ds8.RasterXSize, ds8.RasterYSize
#print ds3.RasterXSize, ds3.RasterYSize
geoTrans = ds8.GetGeoTransform()



with open(vectorSrc,'r') as f:
    js = json.load(f)


dist = np.zeros((ds8.RasterXSize, ds8.RasterYSize))
for i in range(ds8.RasterXSize):
    for j in range(ds8.RasterYSize):
         point = Point(Pixel2World( geoTrans, i , j ))
         pd = -100000.0
         for feature in js['features']:
             polygon = shape(feature['geometry'])
             newpd = point.distance(polygon.boundary)
             if False == polygon.contains(point):
                 newpd = -1.0 * newpd
             if newpd > pd :
                 print point.wkt
                 print polygon.wkt
                 break
                 pd = newpd
         dist[i,j] = pd


#print dist.shape
#plt.imshow(dist)
#plt.show()

np.save(path+'CosmiQ_distance/'+fn+'.distance',dist)


#WKT POINT (-43.68028391328727 -22.97494898261454)
# POLYGON Z ((-43.68206459999993 -22.97422559999995 0, -43.68194719999997 -22.97417909999996 0, -43.68192029999994 -22.97424689999997 0, -43.68203769999997 -22.97429339999997 0, -43.68206459999993 -22.97422559999995 0))

polygonOGR = ogr.CreateGeometryFromWkt('POLYGON ((-43.68206459999993 -22.97422559999995 0, -43.68194719999997 -22.97417909999996 0, -43.68192029999994 -22.97424689999997 0, -43.68203769999997 -22.97429339999997 0, -43.68206459999993 -22.97422559999995 0))')
pointOGR = ogr.CreateGeometryFromWkt('POINT (-43.68028391328727 -22.97494898261454)')

#######################

vectorSrc = '/Users/dlindenbaum/cosmiQGit/spaceNetUtilities/testData/AOI_0_TEST/vectorData/geoJson/013022223130_Public_img9_Geo.geojson'
rasterSrc = '/Users/dlindenbaum/cosmiQGit/spaceNetUtilities/testData/AOI_0_TEST/8band/8band_013022223130_Public_img9.tif'
rasterTest = '/Users/dlindenbaum/cosmiQGit/spaceNetUtilities/testData/AOI_0_TEST/8band/8band_013022223130_Public_img9Rasterizd1.tif'
rasterProxOut = '/Users/dlindenbaum/cosmiQGit/spaceNetUtilities/testData/AOI_0_TEST/8band/8band_013022223130_Public_img9ProxOut1.tif'
rasterProxInside = '/Users/dlindenbaum/cosmiQGit/spaceNetUtilities/testData/AOI_0_TEST/8band/8band_013022223130_Public_img9ProxIn1.tif'
rasterProxFinal = '/Users/dlindenbaum/cosmiQGit/spaceNetUtilities/testData/AOI_0_TEST/8band/8band_013022223130_Public_img9ProxFinal1.tif'
ds8 = gdal.Open(rasterSrc)

if units == 'meters':
    geoTrans, poly, ulX, ulY, lrX, lrY = gT.getRasterExtent(ds8)
    transform_WGS84_To_UTM, transform_UTM_To_WGS84, utm_cs = gT.createUTMTransform(poly)
    line = ogr.Geometry(ogr.wkbLineString)
    line.AddPoint(geoTrans[0], geoTrans[3])
    line.AddPoint(geoTrans[0] + geoTrans[1], geoTrans[3])

    line.Transform(transform_WGS84_To_UTM)
    metersIndex = line.Length()

    transform_WGS84_To_UTM, transform_UTM_To_WGS84, utm_cs = gT.createUTMTransform(poly)
    line2 = ogr.Geometry(ogr.wkbLineString)
    line2.AddPoint(geoTrans[0], geoTrans[3])
    line2.AddPoint(geoTrans[0] , geoTrans[3]+ geoTrans[5])

    line2.Transform(transform_WGS84_To_UTM)
    metersIndex2 = line.Length()

else:
    metersIndex = 1



source_ds = ogr.Open(vectorSrc)
source_layer = source_ds.GetLayer()
geoTrans = ds8.GetGeoTransform()
pixel_size = geoTrans[1]
cols = ds8.RasterXSize
rows = ds8.RasterYSize
noDataValue = 0
memdrv = gdal.GetDriverByName('Gtiff')
dst_ds = memdrv.Create(rasterTest, cols, rows, 1, gdal.GDT_Byte)
dst_ds.SetGeoTransform(ds8.GetGeoTransform())
dst_ds.SetProjection(ds8.GetProjection())
band = dst_ds.GetRasterBand(1)
band.SetNoDataValue(noDataValue)

gdal.RasterizeLayer(dst_ds, [1], source_layer, burn_values=[255])
srcBand = dst_ds.GetRasterBand(1)


memdrv2 = gdal.GetDriverByName('Gtiff')
prox_ds = memdrv2.Create(rasterProxOut, cols, rows, 1, gdal.GDT_Int16)
prox_ds.SetGeoTransform(ds8.GetGeoTransform())
prox_ds.SetProjection(ds8.GetProjection())
proxBand = prox_ds.GetRasterBand(1)
proxBand.SetNoDataValue(noDataValue)

options = ['NODATA=0']


gdal.ComputeProximity(srcBand, proxBand, options)


memdrv3 = gdal.GetDriverByName('Gtiff')
proxIn_ds = memdrv3.Create(rasterProxInside, cols, rows, 1, gdal.GDT_Int16)
proxIn_ds.SetGeoTransform(ds8.GetGeoTransform())
proxIn_ds.SetProjection(ds8.GetProjection())
proxInBand = proxIn_ds.GetRasterBand(1)
proxInBand.SetNoDataValue(noDataValue)
options = ['NODATA=0', 'VALUES=0']
gdal.ComputeProximity(srcBand, proxInBand, options)



memdrv4 = gdal.GetDriverByName('Gtiff')
proxFin_ds = memdrv3.Create(rasterProxFinal, cols, rows, 1, gdal.GDT_Int16)
proxFin_ds.SetGeoTransform(ds8.GetGeoTransform())
proxFin_ds.SetProjection(ds8.GetProjection())
proxFinBand = proxFin_ds.GetRasterBand(1)
proxFinBand.SetNoDataValue(-99)
options = ['NODATA=0', 'VALUES=0']

proxIn = gdalnumeric.BandReadAsArray(proxInBand)
proxOut = gdalnumeric.BandReadAsArray(proxBand)

proxTotal = proxIn.astype(float)-proxOut.astype(float)
gdalnumeric.BandWriteArray(proxFinBand, proxTotal)



dst_ds= None
prox_ds = None
proxIn_ds = None
proxFinBand = None


band.WriteArray(contour)

dst_layername = "BuildingID"
drv = ogr.GetDriverByName("geojson")
dst_ds = drv.CreateDataSource('./geojson/' + fn + dst_layername + ".geojson")
dst_layer = dst_ds.CreateLayer(dst_layername, srs=None)
# dst_layer = dst_ds.CreateLayer( dst_layername, proj, ogr.wkbPolygon )
dst_fieldname = 'BuildingID'
fd = ogr.FieldDefn(dst_fieldname, ogr.OFTInteger)
dst_layer.CreateField(fd)
dst_field = 1

gdal.Polygonize(band, None, dst_layer, dst_field, [], callback=None)
# gdal.Polygonize( band  , None, dst_layer, dst_field, [], callback=None )

srcBand =

