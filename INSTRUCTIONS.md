Should be run in the following order for ndvi calculations:

exif_dump > correct_vignette > dewarp > ndvi_calculator

Usage for each is as follows:

exif_dump.py --input original_tif.TIF --output EXIF_data.txt --xml XML_data.xml

correct_vignette --input original_tif.TIF --output corrected_tif.TIF --xml XML_data.xml

dewarp --input corrected_tif.TIF --output aligned_tif.TIF --xml XML_data.xml


##run these for all of the TIF files##


it is important to correct the vignette before dewarping, as dewarping will shift the images and affect the shape of the vignette

ndvi_calculator.py --red aligned_red.TIF --nir aligned_nir.TIF --xml XML_data_red.XML:XML_data_nir.XML --out (0|1) --run_name unique_identifier_without_extension

--xml should be written with a ":" separating the two files, with red first and nir second

--out 1 will generate an image and csv while --out 0 just generates a csv

--run_name is a prefix added to the output file(s)
