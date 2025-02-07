from PIL import Image
import argparse
import csv
from decimal import Decimal
import re
import numpy

parser = argparse.ArgumentParser()
parser.add_argument("--input", dest="msr", type=str, help="aligned tif file. All other preprocessing must be finished")
parser.add_argument("--xml", dest="xmls", type=str, help="xml file")
parser.add_argument("--run_name", dest="rn", type=str, help="naming prefix for output files")
args = parser.parse_args()

red_file = args.msr
xml_files = [args.xmls]
run_name = args.rn

## max bit level should be 2^n-1 power where n represents bit depth
max_bit_level = (2**16)-1

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
gain_red = Decimal(re.sub(r'"\W+','',str.split(find_in_xml(xml_files[0], r'.*SensorGainAdjustment=.*').string, '=')[1])[1:])
exposure_red = Decimal(re.sub(r'"\W+','',str.split(find_in_xml(xml_files[0], r'.*ExposureTime=.*').string, '=')[1])[1:])
irradiance_red = Decimal(re.sub(r'"\W+','',str.split(find_in_xml(xml_files[0], r'.*Irradiance=.*').string, '=')[1])[1:])
red_data,red_w,red_h = extract_TIF(red_file)
if(not type(red_data[0]) == int) :
    for i in range(len(red_data)) :
        red_data[i] = red_data[i][0]
red_b_level = Decimal(black_level_red / max_bit_level)
red_cam = []
red_raw = []
for i in range(len(red_data)) :
    normalized_value = Decimal(red_data[i] / max_bit_level)
    cam_value = (normalized_value-red_b_level) / (gain_red * (exposure_red / Decimal(1e6)))
    if(cam_value < 0 or red_data[i] == 0) :
        ##any negative values or border values will be set to zero. This can caused by the alignment correction
        cam_value = 0
    norm_value = (cam_value*gain_red)/irradiance_red
    red_cam.append(norm_value)

red_csv_writable = []
k = 0
for i in range(red_h) :
    red_csv_writable.append([])
    for j in range(red_w) :
        if(red_data[k] == 0) :
            ##preserves borders created by alignment
            red_csv_writable[i].append(0)
        else:
            red_csv_writable[i].append(red_cam[k])
        k = k + 1
make_file(run_name+"_normalized.csv", red_csv_writable)