# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 21:54:20 2021

@author: Sarthak
"""

from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt

ds = gdal.Open("Input.tif")
array = ds.GetRasterBand(3).ReadAsArray()
#plt.imshow(array)
#plt.colorbar()
#print(ds.GetGeoTransform())
#print(ds.GetProjection())

dsReprj = gdal.Warp("Output_Reprj.tif", ds, dstSRS = "EPSG:32617")

dsRes = gdal.Warp("Output_Res.tif", ds, xRes = 0.1, yRes = 0.1, resampleAlg ="bilinear")

array = dsRes.GetRasterBand(3).ReadAsArray()
plt.imshow(array)
plt.colorbar()
print(ds.GetGeoTransform())
print(ds.GetProjection())