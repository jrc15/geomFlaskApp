from osgeo import gdal, ogr
import subprocess

#Variables
Outlets = './static/uploads/Outlet.shp'
Basin = './static/uploads/Basin.shp'
Source = './static/uploads/Source.shp'

def ContaminationFlow():
    
    BASINang = './static/uploads/BASINang.tif'
    BASINdm = './static/uploads/BASINdm.tif'
    SourceR = './static/uploads/SourceR.tif'
    BASINdg = './static/uploads/BASINdg.tif'
    BASINctpt = './static/uploads/BASINctpt.tif'
    BASINnet = './static/uploads/BASINsrcndCrop.tif'
    ContamArea = './static/uploads/ContaminationAreas.tif'
    R1 = './static/uploads/R1.tif'
    R2 = './static/uploads/R2.tif'
    R3 = './static/uploads/R3.tif'
    ContamShp = './static/uploads/ContaminationAreas.shp'
    
    
    raster = gdal.Open('./static/uploads/BASINang.tif')
    gt =raster.GetGeoTransform()
    pixelSizeX = gt[1]
    pixelSizeY =-gt[5]
    print (pixelSizeX)
    print (pixelSizeY)
    minx = gt[0]
    maxy = gt[3]
    maxx = minx + gt[1]*raster.RasterXSize
    miny = maxy + gt[5]*raster.RasterYSize
    print (minx,miny,maxx,maxy)
    
    # Generate Contaminate Flow - including fertilisers
    #Rasterize Source
    cmd1="gdal_rasterize -a id -tr '{0}' '{1}' -a_nodata 0.0 -te '{2}' '{3}' '{4}' '{5}' -ot Float32 -of GTiff '{6}' '{7}'".format(pixelSizeX, pixelSizeY, minx, miny, maxx, maxy, Source, SourceR)
    subprocess.call(cmd1, shell=True)
    #Translate Source
    cmd2="gdal_translate -a_nodata -9999 -of GTiff '{0}' '{1}'".format(SourceR, BASINdg)
    subprocess.call(cmd2, shell=True)
    #Rasterize Basin
    cmd3="gdal_rasterize -a fid -tr '{0}' '{1}' -a_nodata 0.0 -te '{2}' '{3}' '{4}' '{5}' -ot Float32 -of GTiff '{6}' '{7}'".format(pixelSizeX, pixelSizeY, minx, miny, maxx, maxy, Basin, BASINdm) 
    subprocess.call(cmd3, shell=True)
    #Execute contamination flow command
    cmd4 = "mpiexec /usr/local/taudem/dinfconclimaccum -ang '{0}' -dg '{1}' -dm '{2}' -ctpt '{3}' -q '{4}' -csol 1 -o '{5}' -nc".format(BASINang, BASINdg, BASINdm, BASINctpt, BASINdm, Outlets)
    subprocess.call(cmd4, shell=True)
    
    #Output Contamination Areas
    cmd5="gdal_translate -a_nodata -9999 -of GTiff '{0}' '{1}'".format(BASINctpt, R1)
    subprocess.call(cmd5, shell=True)
    cmd6="gdalwarp -of GTiff -cutline '{0}' -crop_to_cutline '{1}' '{2}'".format(Basin, R1, R2)
    subprocess.call(cmd6, shell=True)
    cmd7="gdal_translate -a_nodata -9999 -of GTiff '{0}' '{1}'".format(R2, R3)
    subprocess.call(cmd7, shell=True)
    cmd8="gdal_calc.py --calc 'A*logical_not(A<0)' --format GTiff --type Float32 -A '{0}' --A_band 1 --outfile '{1}'".format(R3, ContamArea)
    subprocess.call(cmd8, shell=True)
    cmd9="gdal_polygonize.py '{0}' -8 -b 1 -f 'ESRI Shapefile' '{1}'".format(ContamArea, ContamShp)
    subprocess.call(cmd9, shell=True)
    
    shapefile = ogr.Open(ContamShp, 1)
    
    layer = shapefile.GetLayer()
    layer.SetAttributeFilter("DN = 0")
    
    for feat in layer:
        print (feat.GetField("DN"))
        layer.DeleteFeature(feat.GetFID())


if __name__ == '__main__':

    ContaminationFlow()
