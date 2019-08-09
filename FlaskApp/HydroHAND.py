import subprocess

def HAND():
    
    BASINang = './static/uploads/BASINang.tif'
    BASINfel = './static/uploads/BASINfel.tif'
    BASINNewsrc = './static/uploads/BASINNewsrc.tif'
    BASINhand = './static/uploads/BASINhand.tif'
    
    # Generate HAND output
    cmd1 = "mpiexec /usr/local/taudem/dinfdistdown -ang '{0}' -fel '{1}' -src '{2}' -dd '{3}' -m ave v".format(BASINang, BASINfel, BASINNewsrc, BASINhand)
    subprocess.call(cmd1, shell=True)


if __name__ == '__main__':

    HAND()
