#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#https://dg-cms-uploads-production.s3.amazonaws.com/uploads/document/file/207/Radiometric_Use_of_WorldView-3_v2.pdf
#https://www.digitalglobe.com/resources/product-samples/rio-de-janerio-brazil
#https://cdn1-originals.webdamdb.com/13264_102978826?cache=1581093759&response-content-disposition=inline%3Bfilename%3D30004_arc_202001.pdf.pdf&response-content-type=application%2Fpdf&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cCo6Ly9jZG4xLW9yaWdpbmFscy53ZWJkYW1kYi5jb20vMTMyNjRfMTAyOTc4ODI2P2NhY2hlPTE1ODEwOTM3NTkmcmVzcG9uc2UtY29udGVudC1kaXNwb3NpdGlvbj1pbmxpbmUlM0JmaWxlbmFtZSUzRDMwMDA0X2FyY18yMDIwMDEucGRmLnBkZiZyZXNwb25zZS1jb250ZW50LXR5cGU9YXBwbGljYXRpb24lMkZwZGYiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjIxNDc0MTQ0MDB9fX1dfQ__&Signature=C0jVjal-2zWoGAivWwcl2-Ob5s8V-VtudJn6hhN96gFkloZObxc20rfdhEJIB~BxZGQ~zwBMjFBKvPZifB~yVZD5eFbXyutPf9AQV1hHNCwoXjPwRqVbjaEtxxHw6QMa8Cy9f5FO3L2A-1snDC1KLfFEqK66uBXL7tNAgDhAkkX6pUfVmcVJwe46JNlzKgvM5hugxmn6BzYrBq2VSh8cadGLYBT4umu3GpdSN1Bbl9L8lVqQtF7kiIYpdazCcPloWvWUoLvw1IvVh8jV~B4Qvau-wMZ~G9zFRjidhn1sXQj29EcroN-e0oxZiu6Ujgyo3HH2~Au1NKV1edzkcFjQVQ__&Key-Pair-Id=APKAI2ASI2IOLRFF2RHA

import rasterio as rio
import numpy
import math
 
_gain = {"BAND_P": 0.955, 
         "BAND_C": 0.938, 
         "BAND_B": 0.946, 
         "BAND_G": 0.958, 
         "BAND_Y": 0.979, 
         "BAND_R": 0.969, 
         "BAND_RE": 1.027,
         "BAND_N": 0.977, 
         "BAND_N2": 1.007, 
         "SWIR1" : 1.030, 
         "SWIR2" : 1.052, 
         "SWIR3" : 0.992, 
         "SWIR4" : 1.014, 
         "SWIR5" : 1.012, 
         "SWIR6" : 1.082, 
         "SWIR7" : 1.056, 
         "SWIR8" : 1.101}

_offset = { "BAND_P": -5.505,
        "BAND_C": -13.099,
        "BAND_B": -9.409,
        "BAND_G": -7.771,
        "BAND_Y": -5.489,
        "BAND_R": -4.579,
        "BAND_RE": -5.552,
        "BAND_N": -6.508,
        "BAND_N2": -3.699,
        "SWIR1": 0.000,
        "SWIR2": 0.000,
        "SWIR3": 0.000,
        "SWIR4": 0.000,
        "SWIR5": 0.000,
        "SIWR6": 0.000,
        "SIWR7": 0.000,
        "SIWR8": 0.000}
 
f = open(_IMDPath,'r')
metadata = f.read()
f.close()
 
def calRadiance(DN,BandName):
    #print "------ Prepare data for conversion -------"
    absCalFactor =  metadata.split(BandName)[1].split("absCalFactor = ")[1].split("\n")[0][:-1]
    effectiveBandwidth =  metadata.split(BandName)[1].split("effectiveBandwidth = ")[1].split("\n")[0][:-1]
    gain = _gain[BandName]
    offset = _offset[BandName]
 
    #print "------ Conversion to Top-of-Atmosphere Spectral Radiance -------"
    L = (gain * DN * (float(absCalFactor)/float(effectiveBandwidth))) + offset
    return L
 
def Earth_Sun_Distance():
    UTCDatetime = metadata.split("firstLineTime = ")[1].split("\n")[0][:-1]
    year = int(UTCDatetime.split("-")[0])
    month = int(UTCDatetime.split("-")[1])
    day = int(UTCDatetime.split("-")[2].split("T")[0])
    hh = int(UTCDatetime.split("T")[1].split(":")[0])
    mm = int(UTCDatetime.split("T")[1].split(":")[1])
    ss_dddddd = float(UTCDatetime.split("T")[1].split(":")[2].split("Z")[0])
 
    #Get year, month, day, hh, mm, ss_dddddd
    UT = hh + (mm/60.0) + (ss_dddddd/3600.0)
    year = year - 1
    month = month + 12
 
    #-------- Calculate Julian Day (JD) --------#
    A = int(year/100)
    B = 2- A + int(A/4)
    JD = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1 )) + day + (UT/24.0) + B - 1524.5
 
    #-------- Calculate Earth-Sun Distance --------#
    D = JD - 2451545.0
    g = 357.529 + (0.98560028 * D)
    g = g*(2*math.pi/360.0) #to radians unit
    dES = 1.00014 - 0.01671 * math.cos(g) - 0.00014 * math.cos(2*g)
    return dES
 
def SolarZenithAngle():
    sunEl = float(metadata.split("meanSunEl = ")[1].split("\n")[0][:-1])
    SolarZenith = 90.0 - sunEl
    SolarZenith = SolarZenith * (2*math.pi/360.0) #to radians unit
    return SolarZenith
 
def TOAReflectance(Llamda, d, SolarZenithAngle, ELamda):
    TOAReflectanceArray = (Llamda * (math.pow(d,2)) * math.pi) / (ELamda * (math.cos(SolarZenithAngle)))
    return TOAReflectanceArray


dES = Earth_Sun_Distance()
SolarZenith = SolarZenithAngle()
ESun_By_WRC =  {    "BAND_P": 1583.58, "BAND_C": 1743.81, "BAND_B": 1971.48, "BAND_G": 1856.26, "BAND_Y": 1749.4
                , "BAND_R": 1555.11,"BAND_RE": 1343.95, "BAND_N": 1071.98, "BAND_N2": 863.296, "SWIR1" : 494.595
                , "SWIR2" : 261.494, "SWIR3" : 230.518, "SWIR4" : 196.766, "SWIR5" : 80.365, "SWIR6" : 74.7211
                , "SWIR7" : 69.043, "SWIR8" : 59.8224 }


# In[ ]:


##Set path for input image file, metadata file and output folder
_imgPath = r"paht/to/input.tif"
_IMDPath = r"paht/to/input_metadata.IMD"
_out_img_folder = r"path/to/output/folder"   


# In[ ]:


## Open Input Image
with rio.open(_imgPath) as src:
    ras_data = src.read()
    ras_meta = src.profile


# In[ ]:


## Open Each Band
PanArray = ras_data[0]    
CostalArray = ras_data[1]
BlueArray = ras_data[2]
GreenArray = ras_data[3]
YellowArray = ras_data[4]
RedArray = ras_data[5]
RedEdgeArray = ras_data[6]
Nir1Array = ras_data[7]
Nir2Array = ras_data[8]
Swir1Array = ras_data[9]
Swir2Array = ras_data[10]
Swir3Array = ras_data[11]
Swir4Array = ras_data[12]
Swir5Array = ras_data[13]
Swir6Array = ras_data[14]
Swir7Array = ras_data[15]
Swir8Array = ras_data[16]


# In[ ]:


## Calculate Radiance For Each Band
Radiance_Pan = calRadiance(PanArray,"BAND_P")
Radiance_Coastal = calRadiance(CostalArray,"BAND_C")
Radiance_Blue = calRadiance(BlueArray,"BAND_B")
Radiance_Green = calRadiance(GreenArray,"BAND_G")
Radiance_Yellow = calRadiance(YellowArray,"BAND_Y")
Radiance_Red = calRadiance(RedArray,"BAND_R")
Radiance_RedEdge = calRadiance(RedArray,"BAND_RE")
Radiance_Nir1 = calRadiance(Nir1Array,"BAND_N")
Radiance_Nir2 = calRadiance(Nir2Array,"BAND_N2")
Radiance_Swir1 = calRadiance(Swir1Array,"SWIR1")
Radiance_Swir2 = calRadiance(Swir2Array,"SWIR2")
Radiance_Swir3 = calRadiance(Swir3Array,"SWIR3")
Radiance_Swir4 = calRadiance(Swir4Array,"SWIR4")
Radiance_Swir5 = calRadiance(Swir5Array,"SWIR5")
Radiance_Swir6 = calRadiance(Swir6Array,"SWIR6")
Radiance_Swir7 = calRadiance(Swir7Array,"SWIR7")
Radiance_Swir8 = calRadiance(Swir8Array,"SWIR8")

# In[ ]:


## Calculate TOA Reflectance For Each Band
TOAReflectance_Pan = TOAReflectance(Radiance_Blue, dES, SolarZenith, ESun_By_WRC["BAND_P"])
TOAReflectance_Coastal = TOAReflectance(Radiance_Blue, dES, SolarZenith, ESun_By_WRC["BAND_C"])

TOAReflectance_Blue = TOAReflectance(Radiance_Blue, dES, SolarZenith, ESun_By_WRC["BAND_B"])
TOAReflectance_Green = TOAReflectance(Radiance_Green, dES, SolarZenith, ESun_By_WRC["BAND_G"])

TOAReflectance_Yellow = TOAReflectance(Radiance_Blue, dES, SolarZenith, ESun_By_WRC["BAND_Y"])

TOAReflectance_Red = TOAReflectance(Radiance_Red, dES, SolarZenith, ESun_By_WRC["BAND_R"])
TOAReflectance_RedEdge = TOAReflectance(Radiance_Blue, dES, SolarZenith, ESun_By_WRC["BAND_RE"])

TOAReflectance_Nir1 = TOAReflectance(Radiance_Nir1, dES, SolarZenith, ESun_By_WRC["BAND_N"])
TOAReflectance_Nir2 = TOAReflectance(Radiance_Blue, dES, SolarZenith, ESun_By_WRC["BAND_N2"])

TOAReflectance_Swir1 = TOAReflectance(Radiance_Blue, dES, SolarZenith, ESun_By_WRC["SWIR1"])
TOAReflectance_Swir2 = TOAReflectance(Radiance_Blue, dES, SolarZenith, ESun_By_WRC["SWIR2"])
TOAReflectance_Swir3 = TOAReflectance(Radiance_Blue, dES, SolarZenith, ESun_By_WRC["SWIR3"])
TOAReflectance_Swir4 = TOAReflectance(Radiance_Blue, dES, SolarZenith, ESun_By_WRC["SWIR4"])
TOAReflectance_Swir5 = TOAReflectance(Radiance_Blue, dES, SolarZenith, ESun_By_WRC["SWIR5"])
TOAReflectance_Swir6 = TOAReflectance(Radiance_Blue, dES, SolarZenith, ESun_By_WRC["SWIR6"])
TOAReflectance_Swir7 = TOAReflectance(Radiance_Blue, dES, SolarZenith, ESun_By_WRC["SWIR7"])
TOAReflectance_Swir8 = TOAReflectance(Radiance_Blue, dES, SolarZenith, ESun_By_WRC["SWIR8"])


# In[ ]:


## Prepare metadata for output
out_meta = ras_meta.copy()
out_meta.update({"count": 1,
                 "dtype": "float64" })


# In[ ]:


## Write each band to output file
with rio.open(_out_img_folder+"Pan_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Pan, 1)
with rio.open(_out_img_folder+"Coastal_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Coastal, 1)
    
with rio.open(_out_img_folder+"Blue_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Blue, 1)
with rio.open(_out_img_folder+"Green_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Green, 1)
with rio.open(_out_img_folder+"Yellow_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Yellow, 1)
    
with rio.open(_out_img_folder+"Red_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Red, 1)
with rio.open(_out_img_folder+"RedEdge_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_RedEdge, 1)    
    
with rio.open(_out_img_folder+"Nir1_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Nir1, 1)
with rio.open(_out_img_folder+"Nir2_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Nir2, 1)

with rio.open(_out_img_folder+"Swir1_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Swir1, 1)
with rio.open(_out_img_folder+"Swir2_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Swir2, 1)
with rio.open(_out_img_folder+"Swir3_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Swir3, 1)
with rio.open(_out_img_folder+"Swir4_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Swir4, 1)
with rio.open(_out_img_folder+"Swir5_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Swir5, 1)
with rio.open(_out_img_folder+"Swir6_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Swir6, 1)
with rio.open(_out_img_folder+"Swir7_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Swir7, 1)
with rio.open(_out_img_folder+"Swir8_TOA.tif", 'w', **out_meta) as dst:
    dst.write(TOAReflectance_Swir8, 1)

# In[ ]:




