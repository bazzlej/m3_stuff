from PIL import Image
import argparse
import re

def make_file(fName, fData) :
    with open(fName, 'w', newline="") as file:
        for i in fData :
            if(not i[0:3] == "700") :
                file.write(f"{i}\n")
            else :
                dat = re.sub(r"[\t\s]*","",i)
                dar = dat.split("\\n")
                for j in dar :
                    file.write(f"{j}\n")
        print("EXIF dump complete")
    return

parser = argparse.ArgumentParser()
parser.add_argument("--input", dest="inp", type=str, help="name of input file, must be I;16 .TIF format for Mavic M3")
parser.add_argument("--output", dest="out", type=str, help="name of out file for all EXIF data")
parser.add_argument("--xml", dest="xfile", type=str, help="optional name of xml file for EXIF channel 700")
args = parser.parse_args()

out_file = args.out
in_file = args.inp
if args.xfile :
    x_file = args.xfile
img = Image.open(in_file)
x = img.getexif()

k = []
for key, val in x.items():
    k.append(f'{key}:{val}')

make_file(out_file,k)

if x_file :
    with open(x_file, "w", newline="") as file:
        for i in k :
            if(i[0:3] == "700") :
                print('XML data found')
                xdat = i[6:].split("\\n")
                for j in xdat :
                    file.write(f"{j}\n")
        print("XML complete")