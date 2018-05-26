#==========================================================================

# GEOG 565 Final Project script for Western Washington water ratings

# Authors: Amy Dearborn, Samantha Thompson, & Patrick Warner

#==========================================================================

#Imports
import arcpy, os
from arcpy import env
from arcpy.sa import *

#Set workspace
env.overwriteOutput = True
env.workspace = arcpy.GetParametersAsText(0)

#Inputs for the tool
#Buffer Inputs
input_shapefile = arcpy.GetParametersAsText(1)
buffer_distance = arcpy.GetParametersAsText(2)
output_buffer = arcpy.GetParametersAsText(3)
dissolved_buffer = arcpy.GetParametersAsText(4)
dissolve_fields = arcpy.GetParametersAsText(5)

#Basin Inputs
wria_basin = arcpy.GetParametersAsText(6)

#Landcover Inputs
input_landcover = arcpy.GetParametersAsText(7)
landcover_column = arcpy.GetParametersAsText(8)
query = arcpy.GetParametersAsText(9) 
output_landcover = arcpy.GetParametersAsText(10)

#Potential Parcels Inputs
parcels = arcpy.GetParametersAsText(11)

#Extract & Clip Inputs
basin_clip_save = arcpy.GetParametersAsText(12)
lc_clip_save = arcpy.GetParametersAsText(13)
basin_extract_save = arcpy.GetParametersAsText(14)


#intial geoprocessing from tool inputs
try:
    arcpy.AddMessage("Creating " + buffer_distance + " buffer...")
    arcpy.Buffer_analysis(input_shapefile,
                          output_buffer,
                          buffer_distance,
                          "", "", "",
                          dissolve_fields)
    arcpy.AddMessage("Buffer Created.")
    arcpy.AddMessage("Dissolving buffer...")
    arcpy.Dissolve_management(output_buffer,
                              dissolved_buffer,
                              dissolve_fields,
                              "", "MULTI_PART",
                              "DISSOLVE_LINES")
    arcpy.AddMessage("Dissolve complete...deleting previous buffer shapefile...")
    arcpy.Delete_management(output_buffer)
    arcpy.AddMessage("Previous buffer shapefile deleted.")

    #Export landcover values from nlcd raster that represent potential wetlands
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
        arcpy.AddMessage("Checked out Spatial Analyst Extension.")
        arcpy.AddMessage("Extracting wetland attributes from landcover raster...")
        wet_lc = ExtractByAttributes(input_landcover,
                                     query)
        arcpy.AddMessage("Converting raster to polygon...")
        rast_to_fc = arcpy.RasterToPolygon_conversion(wet_lc,
                                                      output_landcover)
        arcpy.AddMessage("Raster to polygon conversion complete.")
    else:
        arcpy.AddMessage("Spatial Analyst is unavailable")
        break    
    
    #Extracting rasters by polygon for the wetlands areas
    basin_clip = arcpy.Clip_Analysis(wria_basin,
                                     dissolved_buffer,
                                     basin_clip_save)
    lc_clip = arcpy.Clip_Analysis(output_landcover,
                                  dissolved_buffer,
                                  lc_clip_save)

except arcpy.ExecuteError:
    arcpy.AddMessage("Unable to execute script.")
except TypeError, ValueError:
    arcpy.AddMessage("The object is not callable or the value is not valid.")
except IOError, EnvironmentError:
    arcpy.AddMessage("A File was not found.")
finally:
    arcpy.AddMessage("Script Finished.")


#---------- Mapping portion ----------
# Set study area/ Clip?
mxd = arcpy.mapping.MapDocument("C:/Users/saman/OneDrive/Documents/GitHub/GEOG-565-Final-Project/GEOG565Map.mxd")

# Map Document Properties

mxd.author = "Amy Dearborn, Patrick Warner, Samantha Thompson"
mxd.title = "Study Area"
mxd.summary = "Will Add Summary"

mxd.save()
del mxd

### Adding Layers
##InsertLayers
##
###Add Aerial and Topographic Imagery
##
##
##
## Add Map Elements - North Arrow, Scale Bar

##scaleBar = arcpy.mapping.ListLayoutElements(mxd, "MAPSURROUND_ELEMENT", "ScaleBar")[0]
##df = arcpy.mapping.ListDataFrames(mxd, scaleBar.parentDataFrameName)[0]
##scaleBar.elementPositionX = df.elementPositionX + (df.elementWidth / 2)


##scaleBar = arcpy.mapping.ListLayoutElements(mxd, "MAPSURROUND_ELEMENT", "NorthArrow")[0]
##df = arcpy.mapping.ListDataFrames(mxd, northArrow.parentDataFrameName)[0]
##scaleBar.elementPositionX = df.elementPositionX + (df.elementWidth / 2)

## Add Legend
##lyr1 = arcpy.mapping.Layer(r"C:\Project\Data\Parcels.lyr")
##lyr2 = arcpy.mapping.Layer(r"C:\Project\Data\MapIndex.lyr")
##lyr3 = arcpy.mapping.Layer(r"C:\Project\Data\Orthophoto.lyr")
##legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT", "Legend")[0]
##legend.autoAdd = True
##arcpy.mapping.AddLayer(df, lyr1, "BOTTOM")
##arcpy.mapping.AddLayer(df, lyr2, "BOTTOM")
##legend.autoAdd = False
##arcpy.mapping.AddLayer(df, lyr3, "BOTTOM")
##legend.adjustColumnCount(2)
##mxd.save()
##del mxd
##mxd.save()

