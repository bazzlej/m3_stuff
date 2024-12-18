import csv
#import xml.etree.ElementTree as ET
from PIL import Image
import math
import argparse
import numpy
from decimal import Decimal
import re

#######         Vignetting Correction FORMULAS:         #######
#   x = i-(2592*(i//2592))          y = (i//2592)
#   r = math.sqrt(((x-center_x)**2)+((y-center_y)**2))
#   V = px_data[i]*((k[5]*r**6)+(k[4]*r**5)+(k[3]*r**4)+(k[2]*r**3)+(k[1]*r**2)+(k[0]*r)+1)

verbose = 0

parser = argparse.ArgumentParser()
parser.add_argument("--input", dest="inp", type=str, help="name of input file, should be extracted csv data")
parser.add_argument("--output", dest="out", type=str, help="name of out file for corrected data")
parser.add_argument("--xml", dest="x", type=str, help="xml data sheet for the image, obtained from exif data")
args = parser.parse_args()

in_file = args.inp
out_file = args.out

xml = args.x

m = re.match
cmx = re.match
cmy = re.match
dw = re.match
with open(args.x, 'r') as file :
    for row in file :
        tmp = re.match(r'.*VignettingData.*',row)
        if tmp :
            m = tmp
        tmp = re.match(r'.*dOpticalCenterX.*',row)
        if tmp :
            cmx = tmp
        tmp = re.match(r'.*dOpticalCenterY.*',row)
        if tmp :
            cmy = tmp
        tmp = re.match(r'.*DewarpData.*',row)
        if tmp :
            dw = tmp

## Vignetting
cx = int(float(re.sub(r'"','',str.split(cmx.string,'=')[1])))
cy = int(float(re.sub(r'"','',str.split(cmy.string,'=')[1])))
k = re.sub(r'"\W+','',str.split(m.string,'=')[1])
k = str.split(k,',')
k = list(map(Decimal, k))

## Dewarping
dw_data = str.split(re.sub(r'"\W+','',str.split(str.split(dw.string,'=')[1],';')[1]),',')

print("XML opened")

def make_file(fName, fData) :
    with open(fName, 'w', newline="") as file:
        writer = csv.writer(file)
		##field = []
		##writer.writerow(field)
        count = 0
        I = 0
        for x in fData :
            writer.writerow(x)
            count = count + 1
            I = I + 1
            if(count == 100) :
                print("That's 100")
                print("Total lines written : "+str(I))
                count = 0
        print("Saving corrected data complete")
    return

def extract_TIF(f, channels) :
    img = Image.open(f)
    print("opened "+f)
    width, height = img.size
    pixel_data = list(img.getdata())
    return pixel_data

img_raw_data = extract_TIF(in_file, 1)
img_cor_data = []

for i in range(len(img_raw_data)) :
    x = i-(2592*(i//2592))
    y = (i//2592)
    r = Decimal.from_float(math.sqrt(((x-cx)**2)+((y-cy)**2)))
    kco = ((k[5]*(r**6))+(k[4]*(r**5))+(k[3]*(r**4))+(k[2]*(r**3))+(k[1]*(r**2))+(k[0]*1)+1)
    V = img_raw_data[i]*kco
    if(V > 65535) :
        if(verbose == 1) :
            print("ERR - out of range, defaulting to max value : Value = "+str(V))
            print("Position : "+str(x)+","+str(y))
            print("Distance : "+str(r))
            print("Input : "+str(img_raw_data[i]))
            print("K : "+str(kco))
        V = 65535
    V = int(V)
    img_cor_data.append(V)

print("Vignette corrected - writing")

img_cor_data = numpy.array(img_cor_data, dtype="uint16")
cor_img = Image.new("I;16", (2592,1944))
cor_img.putdata(img_cor_data)
cor_img.save(out_file)

print("Correction complete")