from PIL import Image
import argparse
import csv
from decimal import Decimal
import re
import numpy

parser = argparse.ArgumentParser()
parser.add_argument("--red", dest="msr", type=str, help="Corrected red file")
parser.add_argument("--nir", dest="msnir", type=str, help="Corrected near infrared file")
parser.add_argument("--xml", dest="xmls", type=str, help="Both XML files in format 'Red:NIR' -- Exactly like that")
parser.add_argument("--out", dest="out", type=int, help="Output format, 0=csv_only 1=ndvi_TIF")
parser.add_argument("--run_name", dest="rn", type=str, help="naming prefix for output files")
args = parser.parse_args()

red_file = args.msr
nir_file = args.msnir
xml_files = str.split(args.xmls, ":")
output = args.out
run_name = args.rn

## Mavic M3 TIF files are 16 bit. For other files you can typically check EXIF channel 258 to get the bit depth
## the bit depth is used for normalization, an incorrect value will have a major impact on results
bit_depth = 16

def find_in_xml(f,m) :
    with open(f, 'r') as file:
        for row in file :
            tmp = re.match(m,row)
            if(tmp) :
                return(tmp)

def make_file(fName, fData) :
    with open(fName, 'w', newline="") as file:
        writer = csv.writer(file)
        for x in fData :
            writer.writerow(x)
    return

def extract_TIF(f) :
    img = Image.open(f)
    print("opened "+f)
    width, height = img.size
    pixel_data = list(img.getdata())
    return pixel_data,width,height

def write_TIF(dat, f) :
    img_dat = numpy.array(dat, dtype="uint16")
    new_img = Image.new("I;16", (2592,1944))
    new_img.putdata(img_dat)
    new_img.save(f)

black_level_red = Decimal(re.sub(r'"\W+','',str.split(find_in_xml(xml_files[0], r'.*BlackLevel.*').string, '=')[1])[1:])
black_level_nir = Decimal(re.sub(r'"\W+','',str.split(find_in_xml(xml_files[1], r'.*BlackLevel.*').string, '=')[1])[1:])
gain_red = Decimal(re.sub(r'"\W+','',str.split(find_in_xml(xml_files[0], r'.*SensorGainAdjustment=.*').string, '=')[1])[1:])
gain_nir = Decimal(re.sub(r'"\W+','',str.split(find_in_xml(xml_files[1], r'.*SensorGainAdjustment=.*').string, '=')[1])[1:])
exposure_red = Decimal(re.sub(r'"\W+','',str.split(find_in_xml(xml_files[0], r'.*ExposureTime=.*').string, '=')[1])[1:])
exposure_nir = Decimal(re.sub(r'"\W+','',str.split(find_in_xml(xml_files[1], r'.*ExposureTime=.*').string, '=')[1])[1:])
irradiance_red = Decimal(re.sub(r'"\W+','',str.split(find_in_xml(xml_files[0], r'.*Irradiance=.*').string, '=')[1])[1:])
irradiance_nir = Decimal(re.sub(r'"\W+','',str.split(find_in_xml(xml_files[1], r'.*Irradiance=.*').string, '=')[1])[1:])

red_data,red_w,red_h = extract_TIF(red_file)
nir_data,nir_w,nir_h = extract_TIF(nir_file)

if(not type(red_data[0]) == int) :
    for i in range(len(red_data)) :
        red_data[i] = red_data[i][0]

if(not type(nir_data[0]) == int) :
    for i in range(len(nir_data)) :
        nir_data[i] = nir_data[i][0]

max_bit_level = (2**bit_depth)-1
nir_b_level = Decimal(black_level_nir / max_bit_level)
red_b_level = Decimal(black_level_red / max_bit_level)

red_cam = []
for i in range(len(red_data)) :
    normalized_value = Decimal(red_data[i] / max_bit_level)
    cam_value = (normalized_value-red_b_level) / (gain_red * (exposure_red / Decimal(1e6)))
    red_cam.append(cam_value)

nir_cam = []
for i in range(len(nir_data)) :
    normalized_value = Decimal(nir_data[i] / max_bit_level)
    cam_value = (normalized_value-nir_b_level) / (gain_nir * (exposure_nir / Decimal(1e6)))
    nir_cam.append(cam_value)

ndvi_data = []
for i in range(len(red_cam)) :
    dat = Decimal((((nir_cam[i]*gain_nir)/irradiance_nir)-((red_cam[i]*gain_red)/irradiance_red)) / (((nir_cam[i]*gain_nir)/irradiance_nir)+((red_cam[i]*gain_red)/irradiance_red)))
    ndvi_data.append(dat)

ndvi_csv_writable = []
k = 0
for i in range(red_h) :
    ndvi_csv_writable.append([])
    for j in range(red_w) :
        if(not red_data[k] == 0 and not nir_data[k] == 0):
            if(ndvi_data[k] > 1) :
                ndvi_csv_writable[i].append(1)
            elif(ndvi_data[k] <1) :
                ndvi_csv_writable[i].append(-1)
            else:
                ndvi_csv_writable[i].append(ndvi_data[k])
        else :
            ndvi_csv_writable[i].append(0)
        k = k + 1

make_file(run_name+"ndvi_out.csv",ndvi_csv_writable)

if(output==1) :
    for i in range(len(ndvi_data)) :
        ##      Potential data loss due to truncated decimal places --- accuracy limited by bit depth
        ndvi_data[i] = ndvi_data[i] * 65535
        ndvi_data[i] = int(ndvi_data[i])
        if(ndvi_data[i] > 65535) :
            ndvi_data[i] = 65535
        if(ndvi_data[i] < 0) :
            ndvi_data[i] = 0
        if(red_data[i] == 0 or nir_data[i] == 0) :
            ndvi_data[i] = 0
    write_TIF(ndvi_data,run_name+"ndvi_image_out.TIF")