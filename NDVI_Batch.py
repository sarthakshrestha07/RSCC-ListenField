#!/usr/bin/env python
# coding: utf-8

# SET PATH VARIABLES
img_dir = 'E:/2021/Companies/ListenField/GDAL_Data/Sentinel_L1C/' #Set Path of input folder
img_frmt = 'jp2'                                                  #Set Input image format
out_dir = 'E:/2021/Companies/ListenField/GDAL_Data/NDVI/'        #Set Path of output folder


#Funtions for 
#List  of all the files(specific type) in the folder (jpg2, tif, ... csv etc)
#Required library
import rasterio, numpy
import os, glob
import pathlib

def file_list(img_dir, band_name, file_frmt):
    list_files = sorted(glob.glob('{}/*/*/*/*_{}*.{}'.format(img_dir, band_name, file_frmt), recursive=True))
    return list_files

#Read file as array
def read_image_file(file_name):
    ds = rasterio.open(file_name, mode='r')
    ds_as_array =  ds.read(1)
    ds.close()
    return ds_as_array

#Prepare metadata for output file (GeoTiff)
def prepare_meta(file_name):
    ds = rasterio.open(file_name, mode='r')
    kwargs = ds.meta
    kwargs.update(
    driver= 'GTiff',
    dtype=rasterio.float32,
    count=1, #1 band.. 
    compress='lzw')
    ds.close()
    return kwargs

#Writing output file
def write_raster(file_name, out_dir, ndvi_arr, kwargs):
    with rasterio.open(out_dir+file_name+'.tif', 'w', **kwargs) as dst:
        dst.write_band(1, ndvi_arr.astype(rasterio.float32))
    print("Done")


img_list = [i.path for i in os.scandir(img_dir)]
for i in img_list:
    #Get band 4 and band 8 file
    B04_file = file_list(i, 'B04', img_frmt)
    B08_file = file_list(i, 'B08', img_frmt)
    
    #Read the file as numpy array
    ds_b04 = read_image_file(B04_file[0])
    ds_b08 = read_image_file(B08_file[0])
    
    # Prepare an NDVI array which is same size as input
    ndvi = numpy.zeros(ds_b04.shape, dtype=rasterio.float32)
    
    # Calcuate the value of each pixel and store them in the array 
    ndvi = (ds_b08.astype(float)-ds_b04.astype(float))/(ds_b08+ds_b04)
    
    # Prepare the metadata of NDVI array (CRS, dataype, format, etc..)
    kwargs = prepare_meta(B04_file[0])
    
    # Preapre name for output file (Names based on .SAFE folder)
    out_file_name = i.split('/')[-1].split('.')[0]  #based on input folder name
    
    #Write outputfile
    print("Writing File:", out_file_name)
    write_raster(out_file_name, out_dir, ndvi, kwargs)
 

