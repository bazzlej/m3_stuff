from PIL import Image
import numpy
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input", dest="inp", type=str, help="name of input file")
parser.add_argument("--output", dest="out", type=str, help="name of out file")
args = parser.parse_args()

out_file = args.out
f = args.inp

channels = 1

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
        print("TIF extract complete")
    return

def main() :
    try :
        img = Image.open(f)
        print("opened "+f)
    except FileNotFoundError :
        print("\033[31mERR: file not found\033[0m")
        return

    width, height = img.size
    pixel_data = list(img.getdata())
    pixel_data = numpy.array(pixel_data).reshape((height,width,channels))
    print(pixel_data[0])
    out_data = []
    for i in range(len(pixel_data)) :
        out_data.append([])
        for j in range(len(pixel_data[i])) :
                out_data[i].append(pixel_data[i][j][0])
                

    make_file(out_file,out_data)

main()