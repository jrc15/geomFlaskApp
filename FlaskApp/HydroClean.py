import glob, os, shutil

#Variables
DEM = './static/uploads/DEM.tif'

################Delete Unneeded Files#########################

def tidyFiles():

    List = []
    List.append('./static/uploads/R1.tif')
    List.append('./static/uploads/R2.tif')
    List.append('./static/uploads/R3.tif')
    List.append('./static/uploads/SourceR.tif')
    List.append('./static/uploads/ThresOutput.csv')
    List.append('./static/uploads/outputPixel.csv')
    List.append('./static/uploads/BASINThresOutput.csv')
    List.append('./static/uploads/BASINtree.dat')
    List.append('./static/uploads/BASINcoord.dat')
    List.append('./static/uploads/BASINNewsrc.tif')
    List.append('./static/uploads/BASINsrc.tif')
    List.append('./static/uploads/BASINsrcnTrn.tif')
    List.append('./static/uploads/BASINsrcTrnCrop.tif')
    List.append('./static/uploads/DEMtree.dat')
    List.append('./static/uploads/DEMcoord.dat')
    List.append('./static/uploads/BASINctpt.tif')
    List.append('./static/uploads/BASINdg.tif')
    List.append('./static/uploads/BASINdm.tif')
    List.append('./static/uploads/BASINsrcTrn.tif')
    List.append('./static/uploads/BASINThresholds.csv')
    List.append('./static/uploads/Thresholds.csv')

    for file in List:
        if os.path.isfile(file):
            os.remove(file)


################Sort Files#########################

def sortFiles():
    # Sort Files
    print('Sorting Files...')
    
    #Make Directories
    os.mkdir('./static/uploads/Input')
    os.mkdir('./static/uploads/DEMNetwork')
    os.mkdir('./static/uploads/BASINNetwork')
    os.mkdir('./static/uploads/Stats')
    os.mkdir('./static/uploads/Other')
    os.mkdir('./static/uploads/Contamination')
    
    # Make lists and Move files
    #Inputs
    BList = glob.glob('./static/uploads/Basin*')
    for f in BList:
        shutil.move(f, './static/uploads/Input')
    SList = glob.glob('./static/uploads/DEMshp*')
    for f in SList:
        shutil.move(f, './static/uploads/Input')
    OList = glob.glob('./static/uploads/Outlet*')
    for f in OList:
        shutil.move(f, './static/uploads/Input')
    CList = glob.glob('./static/uploads/Source.*')
    for f in CList:
        shutil.move(f, './static/uploads/Input')
    shutil.move(DEM, './static/uploads/Input')

    #DEM products
    DEMlist = glob.glob('./static/uploads/DEM*')
    for f in DEMlist:
        shutil.move(f, './static/uploads/DEMNetwork')

    #Statistical products
    STATSlist = glob.glob('./static/uploads/*.csv')
    for f in STATSlist:
        shutil.move(f, './static/uploads/Stats')
        
    #Basin products
    BASINlist = glob.glob('./static/uploads/BASIN*')
    for f in BASINlist:
        shutil.move(f, './static/uploads/BASINNetwork')

    #Other products
    OTHERlist = glob.glob('./static/uploads/Dr*')
    for f in OTHERlist:
        shutil.move(f, './static/uploads/Other')
    MList = glob.glob('./static/uploads/MovedOutlets*')
    for f in MList:
        shutil.move(f, './static/uploads/Other')

    #Contamination products
    Conlist = glob.glob('./static/uploads/Contamination*')
    for f in Conlist:
        shutil.move(f, './static/uploads/Contamination')

    print ('\n' + 'END' + '\n')


if __name__ == '__main__':

    tidyFiles()
    sortFiles()
