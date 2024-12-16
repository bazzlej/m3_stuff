import cv2
from decimal import Decimal
import argparse
import re
import math
import numpy

#######         Dewarping Setup                         #######
## Dewarp Data : yyyy-mm-dd; fx, fy, px, py, k1, k2, p1, p2, k3
## cameraMatrix = [(fx,0,cx-px),(0,fy,cy-py),(0,0,1)]
## dist = [k1,k2,p1,p2,k3]

parser = argparse.ArgumentParser()
parser.add_argument("--input", dest="inp", type=str, help="name of input file, should be extracted csv data")
parser.add_argument("--output", dest="out", type=str, help="name of out file for corrected data")
parser.add_argument("--xml", dest="x", type=str, help="xml data sheet for the image, obtained from exif data")
args = parser.parse_args()

in_file = args.inp
out_file = args.out

cmx = re.match
cmy = re.match
dw = re.match
chm = re.match
with open(args.x, 'r') as file :
    for row in file :
        tmp = re.match(r'.*dOpticalCenterX.*',row)
        if tmp :
            cmx = tmp
        tmp = re.match(r'.*dOpticalCenterY.*',row)
        if tmp :
            cmy = tmp
        tmp = re.match(r'.*DewarpData.*',row)
        if tmp :
            dw = tmp
        tmp = re.match(r'.*CalibratedHMatrix.*',row)
        if tmp :
            chm = tmp

##      Dewarp

cx = int(float(re.sub(r'"','',str.split(cmx.string,'=')[1])))
cy = int(float(re.sub(r'"','',str.split(cmy.string,'=')[1])))
dw_data = list(map(float, str.split(re.sub(r'"\W+','',str.split(str.split(dw.string,'=')[1],';')[1]),',')))

camera_matrix = numpy.array([(dw_data[0],0,cx-dw_data[2]),(0,dw_data[1],cy-dw_data[3]),(0,0,1)])
dist_coeffs = numpy.array([[dw_data[4],dw_data[5],dw_data[6],dw_data[7],dw_data[8]]])

img = cv2.imread(in_file)
h, w = img.shape[:2]

new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w,h), 1, (w,h))
dst = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_camera_matrix)
##cv2.imwrite(out_file, dst)

##      Phase/Rotation alignment

c_hover_matrix = str.split(re.sub(r'"\W+','',str.split(chm.string,'=')[1]),',')
if(c_hover_matrix[0][0] == '"') :
    c_hover_matrix[0] = c_hover_matrix[0][1:]
c_hover_matrix = list(map(float, c_hover_matrix))
ch_matrix = numpy.array([[c_hover_matrix[0],c_hover_matrix[1],c_hover_matrix[2]],[c_hover_matrix[3],c_hover_matrix[4],c_hover_matrix[5]],[c_hover_matrix[6],c_hover_matrix[7],c_hover_matrix[8]]])

dst2 = cv2.warpPerspective(dst, ch_matrix, (w,h), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
cv2.imwrite(out_file, dst2)
print("Image aligned")