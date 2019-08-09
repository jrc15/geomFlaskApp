from osgeo import gdal, ogr
import subprocess, glob, os, csv, pandas, shutil

#Variables
DEM = './static/uploads/DEM.tif'
Outlets = './static/uploads/Outlet.shp'
Basin = './static/uploads/Basin.shp'
Source = './static/uploads/Source.shp'

########################Define Print Function###########################
def Print():
    print ('\n')
    print ('***********************************************')
    print ('\n')

########################Define Stream Analysis###########################
def StreamDelineation():

    # Outlet Variables
    MovedOutlets = './static/uploads/MovedOutlets.shp'
    
    # DEM Computed Variables
    DEMfel = DEM[:-4] + 'fel.tif' #Filled Elevation
    DEMp = './static/uploads/DEMp.tif' #D8 flow direction grid
    DEMsd8 = './static/uploads/DEMsd8.tif' #D8 slope grid
    DEMad8 = './static/uploads/DEMad8.tif' #D8 contributing area grid
    DEMang = './static/uploads/DEMang.tif' #D-infinity flow direction grid
    DEMslp = './static/uploads/DEMslp.tif' #D-infinity slope grid
    DEMsca = './static/uploads/DEMsca.tif' #D-infinity contributing area grid
    DEMss = './static/uploads/DEMss.tif' #Stream Source Grid
    DEMssa = './static/uploads/DEMssa.tif' #Accumulated Stream Source Grid
    DEMdrp = './static/uploads/DEMdrp.csv' #Stream drop analysis table
    DEMsrc = './static/uploads/DEMsrc.tif' #Stream raster grid 1
    DEMord = './static/uploads/DEMord.tif' #Network order grid
    DEMtree = './static/uploads/DEMtree.dat' #Stream Network tree text file
    DEMcoord = './static/uploads/DEMcoord.dat' #Network coordinates file
    DEMnet = './static/uploads/DEMStreamNetwork.shp' #Stream network shapefile
    DEMw = './static/uploads/DEMw.tif' #Watershed grid
    DEMsa = './static/uploads/DEMsa.tif' #Slope Area
    
    # Computed Basin Variables
    BASINfel = './static/uploads/BASINfel.tif'
    BASINp = './static/uploads/BASINp.tif'
    BASINad8 = './static/uploads/BASINad8.tif'
    BASINsrc = './static/uploads/BASINsrc.tif'
    BASINord = './static/uploads/BASINord.tif'
    BASINtree = './static/uploads/BASINtree.dat'
    BASINcoord = './static/uploads/BASINcoord.dat'
    BASINnet = './static/uploads/BASINStreamNetworkLine.shp'
    BASINw = './static/uploads/BASINW.tif'
    BASINssa = './static/uploads/BASINssa.tif'
    BASINdrp = './static/uploads/BASINdrp.csv'
    BASINang = './static/uploads/BASINang.tif'
    BASINNewsrc = './static/uploads/BASINNewsrc.tif'
    BASINsrcnd = './static/uploads/BASINsrcTrn.tif'
    BASINsrcndCrop = './static/uploads/BASINsrcTrnCrop.tif'
    BASINStreamNetwork = './static/uploads/BASINStreamNetworkPoly.tif'
    BASINStreamNetworkShp = './static/uploads/BASINStreamNetworkPoly.shp'
    
    # Thresholds
    Thresh1 = 250
    
    # Remove Pits
    cmd1 = "mpiexec /usr/local/taudem/pitremove '{0}'".format(DEM)
    subprocess.call(cmd1, shell=True)
    Print()
    
    # D8 Flow Directions - D8 & D-Infinite
    cmd2 = "mpiexec /usr/local/taudem/d8flowdir -p '{0}' -sd8 '{1}' -fel '{2}'".format(DEMp, DEMsd8, DEMfel)
    subprocess.call(cmd2, shell=True)
    Print()
    cmd3 = "mpiexec /usr/local/taudem/dinfflowdir -ang '{0}' -slp '{1}' -fel '{2}'".format(DEMang, DEMslp, DEMfel)
    subprocess.call(cmd3, shell=True)
    Print()
    
    # D8 Contributing Area
    cmd4 = "mpiexec /usr/local/taudem/aread8 -p '{0}' -ad8 '{1}'".format(DEMp, DEMad8)
    subprocess.call(cmd4, shell=True)
    Print()
    
    cmd5 = "mpiexec /usr/local/taudem/areadinf -ang '{0}' -sca '{1}'".format(DEMang, DEMsca)
    subprocess.call(cmd5, shell=True)
    Print()
    
    # Raster Stats
    cmd6 = "/usr/bin/gdalinfo '{0}' | tee ./static/uploads/DEMinfo.csv".format(DEM)
    subprocess.call(cmd6, shell=True)
    
    with open('./static/uploads/DEMinfo.csv') as inp, open('./static/uploads/outputPixel.csv','w') as resultFile:
        values = list(csv.reader(inp, delimiter=' '))
        newCSV=values[0:][0:3]
        #print(newCSV)
        wr = csv.writer(resultFile)
        wr.writerows(newCSV)
    
    with open('./static/uploads/outputPixel.csv') as csvDataFile:
        data=list(csv.reader(csvDataFile))
        X = data[2][2]
        print (X)
        Y = data[2][3]
        print(Y)
        removeChar = ","
        for char in removeChar: X=X.replace(char, "")

    ThresPar=int(float(X))*int(float(Y))
    print("\n" + "Total Pixels = ", ThresPar)
    Print()

    # Stream Threshold Test
    cmd6 = "mpiexec /usr/local/taudem/threshold -ssa '{0}' -src '{1}' -thresh '{2}'".format(DEMad8, DEMsrc, Thresh1)
    subprocess.call(cmd6, shell=True)
    Print()
    
    #Move Outlets to stream
    cmd7 = "mpiexec /usr/local/taudem/moveoutletstostrm -p '{0}' -src '{1}' -o '{2}' -om '{3}'".format(DEMp, DEMsrc, Outlets, MovedOutlets)
    subprocess.call(cmd7, shell=True)
    Print()
    
    # Slope Area
    cmd8 = "mpiexec /usr/local/taudem/slopearea -slp '{0}' -sca '{1}' -sa '{2}'".format(DEMslp, DEMsca, DEMsa)
    subprocess.call(cmd8, shell=True)
    Print()
    
    # Extreme Upslope Value
    cmd9 = "mpiexec /usr/local/taudem/d8flowpathextremeup -p '{0}' -sa '{1}' -ssa '{2}'".format(DEMp, DEMsa, DEMssa)
    subprocess.call(cmd9, shell=True)
    Print()
    
    # Peuker Douglas
    cmd10 = "mpiexec /usr/local/taudem/peukerdouglas -fel '{0}' -ss '{1}'".format(DEMfel, DEMss)
    subprocess.call(cmd10, shell=True)
    Print()
    print(ThresPar)
    
    cmd11 = "mpiexec /usr/local/taudem/dropanalysis -p '{0}' -fel '{1}' -ad8 '{2}' -ssa '{3}' -drp '{4}' -o '{5}' -par 1 '{6}' 30 0 | tee ./static/uploads/Thresholds.csv".format(DEMp, DEMfel, DEMad8, DEMssa, DEMdrp, MovedOutlets, ThresPar)
    subprocess.call(cmd11, shell=True)
    Print()
    
    with open('./static/uploads/Thresholds.csv') as inp, open('./static/uploads/ThresOutput.csv','w') as resultFile:
        values = list(csv.reader(inp, delimiter=' '))
        newCSV=values[0:][13:45]
        #print(newCSV)
        wr = csv.writer(resultFile)
        wr.writerows(newCSV)

    # Read CSV and return Threshold value
    with open('./static/uploads/ThresOutput.csv') as csvDataFile:
        data=list(csv.reader(csvDataFile))
        OptimumThreshold = data[-1][0]
        removeChar = "OptimuThresldVauo: "
        for char in removeChar: OptimumThreshold=OptimumThreshold.replace(char, "")

    OptThrsh = int(float(OptimumThreshold))
    print("Optimum Threshold Value =", OptThrsh)

    # Get a list of Threshold values
    n = 3
    sum = 0 # initialize sum and counter
    i = 1
    
    while i <= n:
        sum = sum + i
        colnames = ['Threshold', 'DrainDen', 'NoFirstOrd', 'NoHighOrd', 'MeanDFirstOrd', 'MeanDHighOrd', 'StdDevFirstOrd', 'StdDevHighOrd', 'T']
        data = pandas.read_csv('./static/uploads/ThresOutput.csv', names=colnames)
        TStat = data['Threshold'].values.tolist()
        T = TStat[1:-1]
        T = [s.replace(' ', '') for s in T]
        print(T)
        mynumber = OptThrsh
        
        # Find the 3 values closest to the Optimum Threshold
        def closest(list, Number):
            temp = []
            for i in list:
                i = float(i)
                temp.append(abs(Number-i))
            return temp.index(min(temp))
        
        a = closest(T, mynumber)
        print ("First index is : ",a)
        print ("First Closet value is : ",T[a])
        b = a-1
        print ("Second index is : ",a - 1)
        print ("Second Closet value is : ",T[b])
        c = a+1
        print ("Third index is : ",a + 1)
        print ("Third Closet value is : ",T[c])
        ThresholdPar1=T[b]
        print("Parameter1 = ", ThresholdPar1)
        ThresholdPar2=T[c]
        print("Parameter2 = ", ThresholdPar2)
        print ("New Threshold Parameters are :", ThresholdPar1, ThresholdPar2, "10 0")
        
        #Repeat Drop Analysis with new parameters
        cmd13 = "mpiexec /usr/local/taudem/dropanalysis -p '{0}' -fel '{1}' -ad8 '{2}' -ssa '{3}' -drp '{4}' -o '{5}' -par '{6}' '{7}' 30 0 | tee ./static/uploads/Thresholds.csv".format(DEMp, DEMfel, DEMad8, DEMssa, DEMdrp, MovedOutlets, ThresholdPar1, ThresholdPar2)
        subprocess.call(cmd13, shell=True)
        
        # Read CSV and return Threshold value
        with open('./static/uploads/Thresholds.csv') as inp, open('./static/uploads/ThresOutput.csv','w') as resultFile:
            values = list(csv.reader(inp, delimiter=' '))
            newCSV=values[0:][13:45]
            #print(newCSV)
            wr = csv.writer(resultFile)
            wr.writerows(newCSV)
        
        with open('./static/uploads/ThresOutput.csv') as csvDataFile:
            data=list(csv.reader(csvDataFile))
            OptimumThreshold = data[-1][0]
            removeChar = "OptimuThresldVauo: "
            for char in removeChar: OptimumThreshold=OptimumThreshold.replace(char, "")
            print ('\n')
            OptThrsh = int(float(OptimumThreshold))
            print("Optimum Threshold Value =", OptThrsh)
            i = i+1    # update counter
        
        Print()
    
    # Stream Threshold Test
    cmd14 = "mpiexec /usr/local/taudem/threshold -ssa '{0}' -src '{1}' -thresh '{2}'".format(DEMssa, DEMsrc, OptThrsh)
    subprocess.call(cmd14, shell=True)
    Print()

    # Clip Rasters by basin shapefile
    InputList = []
    InputList.append(DEMfel)
    InputList.append(DEMp)
    InputList.append(DEMad8)
    InputList.append(DEMssa)
    InputList.append(DEMang)
    print (InputList)

    for inFile in InputList:
        print(inFile)
        outFile=inFile.replace('DEM','BASIN')
        cmd15="/usr/bin/gdalwarp -overwrite -of GTiff -cutline '{0}' -crop_to_cutline '{1}' '{2}'".format(Basin, inFile, outFile)
        subprocess.call(cmd15,shell=True)
        Print()

    # DEM - Stream Reach and Watershed
    cmd16 = "mpiexec /usr/local/taudem/streamnet -fel '{0}' -p '{1}' -ad8 '{2}' -src '{3}' -ord '{4}' -tree '{5}' -coord '{6}' -net '{7}' -w '{8}' -o '{9}'".format(DEMfel, DEMp, DEMad8, DEMsrc, DEMord, DEMtree, DEMcoord, DEMnet, DEMw, MovedOutlets)
    subprocess.call(cmd16, shell=True)
    Print()
    
    # Apply Drop Analysis to clipped Basin Rasters
    print(ThresPar)
    cmd17 = "mpiexec /usr/local/taudem/dropanalysis -p '{0}' -fel '{1}' -ad8 '{2}' -ssa '{3}' -drp '{4}' -o '{5}' -par 1 '{6}' 30 0 | tee ./static/uploads/BASINThresholds.csv".format(BASINp, BASINfel, BASINad8, BASINssa, BASINdrp, MovedOutlets, ThresPar)
    subprocess.call(cmd17, shell=True)
    Print()
    
    with open('./static/uploads/BASINThresholds.csv') as inp, open('./static/uploads/BASINThresOutput.csv','w') as resultFile:
        values = list(csv.reader(inp, delimiter=' '))
        newCSV=values[0:][13:45]
        #print(newCSV)
        wr = csv.writer(resultFile)
        wr.writerows(newCSV)
    
    # Read CSV and return Threshold value
    with open('./static/uploads/BASINThresOutput.csv') as csvDataFile:
        data=list(csv.reader(csvDataFile))
        OptimumThreshold = data[-1][0]
        removeChar = "OptimuThresldVauo: "
        for char in removeChar: OptimumThreshold=OptimumThreshold.replace(char, "")

    OptThrsh = int(float(OptimumThreshold))
    print("Optimum Threshold Value =", OptThrsh)

    # Get a list of Threshold values
    n = 2
    sum = 0 # initialize sum and counter
    i = 1
    
    while i <= n:
        sum = sum + i
        colnames = ['Threshold', 'DrainDen', 'NoFirstOrd', 'NoHighOrd', 'MeanDFirstOrd', 'MeanDHighOrd', 'StdDevFirstOrd', 'StdDevHighOrd', 'T']
        data = pandas.read_csv('./static/uploads/BASINThresOutput.csv', names=colnames)
        TStat = data['Threshold'].values.tolist()
        T = TStat[1:-1]
        T = [s.replace(' ', '') for s in T]
        print(T)
        mynumber = OptThrsh
        
        # Find the 3 values closest to the Optimum Threshold
        def closest(list, Number):
            temp = []
            for i in list:
                i = float(i)
                temp.append(abs(Number-i))
            return temp.index(min(temp))
        
        a = closest(T, mynumber)
        print ("First index is : ",a)
        print ("First Closet value is : ",T[a])
        b = a-1
        print ("Second index is : ",a - 1)
        print ("Second Closet value is : ",T[b])
        c = a+1
        print ("Third index is : ",a + 1)
        print ("Third Closet value is : ",T[c])
        ThresholdPar1=T[b]
        print("Parameter1 = ", ThresholdPar1)
        ThresholdPar2=T[c]
        print("Parameter2 = ", ThresholdPar2)
        print ("New Threshold Parameters are :", ThresholdPar1, ThresholdPar2, "10 0")
        
        #Repeat Drop Analysis with new parameters
        cmd18 = "mpiexec /usr/local/taudem/dropanalysis -p '{0}' -fel '{1}' -ad8 '{2}' -ssa '{3}' -drp '{4}' -o '{5}' -par '{6}' '{7}' 30 0 | tee ./static/uploads/BASINThresholds.csv".format(BASINp, BASINfel, BASINad8, BASINssa, BASINdrp, MovedOutlets, ThresholdPar1, ThresholdPar2)
        subprocess.call(cmd18, shell=True)
        
        # Read CSV and return Threshold value
        with open('./static/uploads/BASINThresholds.csv') as inp, open('./static/uploads/BASINThresOutput.csv','w') as resultFile:
            values = list(csv.reader(inp, delimiter=' '))
            newCSV=values[0:][13:45]
            #print(newCSV)
            wr = csv.writer(resultFile)
            wr.writerows(newCSV)
        
        with open('./static/uploads/BASINThresOutput.csv') as csvDataFile:
            data=list(csv.reader(csvDataFile))
            OptimumThreshold = data[-1][0]
            removeChar = "OptimuThresldVauo: "
            for char in removeChar: OptimumThreshold=OptimumThreshold.replace(char, "")
            print ('\n')
            OptThrsh = int(float(OptimumThreshold))
            print("Optimum Threshold Value =", OptThrsh)
            i = i+1    # update counter
        
        Print()

    # Stream Threshold Test
    cmd19 = "mpiexec /usr/local/taudem/threshold -ssa '{0}' -src '{1}' -thresh '{2}'".format(BASINssa, BASINsrc, OptThrsh)
    subprocess.call(cmd19, shell=True)
    Print()

    # Obtain correct stream network from BASINsrc
    #Step 1 - reapply no data value
    cmd20="/usr/bin/gdal_translate -a_nodata 0.0 -of GTiff '{0}' '{1}'".format(BASINsrc, BASINsrcnd)
    subprocess.call(cmd20, shell=True)
    print("Translate complete")
    #Step 2 - clip to required data area
    cmd21="/usr/bin/gdalwarp -of GTiff -cutline '{0}' -crop_to_cutline '{1}' '{2}'".format(Basin, BASINsrcnd, BASINsrcndCrop)
    subprocess.call(cmd21, shell=True)
    print("Clip complete")
    #Step 3 - extract stream area
    cmd22="/usr/bin/gdal_calc.py --calc 'A + (A*-1) + 1' --format GTiff --type Float32 -A '{0}' --A_band 1 --outfile '{1}'".format(BASINsrcndCrop, BASINStreamNetwork)
    subprocess.call(cmd22, shell=True)
    print("Calc complete")
    # Step 4 - Polygonise - Rename output as Stream Polygon?
    cmd23="/usr/bin/gdal_polygonize.py '{0}' -8 -b 1 -f 'ESRI Shapefile' '{1}'".format(BASINStreamNetwork, BASINStreamNetworkShp)
    subprocess.call(cmd23, shell=True)
    print("Polygonise complete")
    #Step 3 - extract stream area
    cmd24="/usr/bin/gdal_merge.py -a_nodata -32768 -ot Float32 -of GTiff -o '{0}' '{1}' '{2}'".format(BASINNewsrc, BASINStreamNetwork, BASINsrc)
    subprocess.call(cmd24, shell=True)
    print("Merge complete")
    Print()
    
    cmd25 = "mpiexec /usr/local/taudem/streamnet -fel '{0}' -p '{1}' -ad8 '{2}' -src '{3}' -ord '{4}' -tree '{5}' -coord '{6}' -net '{7}' -w '{8}' -o '{9}'".format(BASINfel, BASINp, BASINad8, BASINNewsrc, BASINord, BASINtree, BASINcoord, BASINnet, BASINw, MovedOutlets)
    subprocess.call(cmd25, shell=True)
    Print()


if __name__ == '__main__':
    
    StreamDelineation()
