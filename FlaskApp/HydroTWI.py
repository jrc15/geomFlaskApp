import subprocess

########################Define Print Function###########################
def Print():
    print ('\n')
    print ('***********************************************')
    print ('\n')

########################Define TWI###########################

def TWI():
    
    BASINang = './static/uploads/BASINang.tif'
    BASINslp = './static/uploads/BASINslp.tif'
    BASINfel = './static/uploads/BASINfel.tif'
    BASINsca = './static/uploads/BASINsca.tif'
    BASINtwi = './static/uploads/BASINtwi.tif'
    
    #Generate Basin slope grid
    cmd1 = "mpiexec /usr/local/taudem/dinfflowdir -ang '{0}' -slp '{1}' -fel '{2}'".format(BASINang, BASINslp, BASINfel)
    subprocess.call(cmd1, shell=True)
    Print()
    
    cmd2 = "mpiexec /usr/local/taudem/areadinf -ang '{0}' -sca '{1}'".format(BASINang, BASINsca)
    subprocess.call(cmd2, shell=True)
    Print()
    
    #Generate TWI
    cmd3 = "mpiexec /usr/local/taudem/twi -slp '{0}' -sca '{1}' -twi '{2}'".format(BASINslp, BASINsca, BASINtwi)
    subprocess.call(cmd3, shell=True)


if __name__ == '__main__':
    
    TWI()
