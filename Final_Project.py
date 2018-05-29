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
parcel_output = arcpy.GetParametersAsText(12)

#Extract & Clip Inputs
basin_clip_save = arcpy.GetParametersAsText(13)
lc_clip_save = arcpy.GetParametersAsText(14)


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
    
    #Extracting rasters by polygon for the wetlands areas
    basin_clip = arcpy.Clip_analysis(wria_basin,
                                     dissolved_buffer,
                                     basin_clip_save)
    lc_clip = arcpy.Clip_analysis(output_landcover,
                                  dissolved_buffer,
                                  lc_clip_save)
    parcel_clip = arcpy.Clip_analysis(parcels,
                                  dissolved_buffer,
                                  parcel_output)

except arcpy.ExecuteError:
    arcpy.AddMessage("Unable to execute script.")
except TypeError, ValueError:
    arcpy.AddMessage("The object is not callable or the value is not valid.")
except IOError, EnvironmentError:
    arcpy.AddMessage("A File was not found.")
finally:
    arcpy.AddMessage("Script Finished.")

#Intersect for Desired Areas
inFeatures = ["basin_clip", "lc_clip", "parcel_clip"]
intersectOutput = "intersect_Output"
clusterTolerance = 1.5    
arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "polygon")

#Study Area
##Writing Geometries

study_area_save = arcpy.GetParametersAsText(15)
array = arcpy.Array([arcpy.Point(Lat1, Long1),
                     arcpy.Point(Lat2, Long2),
                     arcpy.Point(Lat3, Long3),
                     arcpy.Point(Lat4, Long4)])
arcpy.AddMessage["Creating polygon from these points: " +array]
polygon = arcpy.Polygon(array)

arcpy.CopyFeatures_management([polygon], study_area_save)
arcpy.AddMessage["Study Area Created"]


#Clip to Study Area
StudyArea_Clip = arcpy.GetParametersAsText(16)
xy_tolerance = ""
arcpy.Clip_analysis(intersectOuput, study_area_save, StudyArea_Clip, xy_tolerance)

#Wetland Scores and Ratings
##Cursor to Update Attribute Table Based on Parameters
fc = ""
newfield = ""
fieldtype = ""
fieldname = arcpy.ValidateFieldName(newfield)
arcpy.AddField_management (fc, fieldname, fieldtype, "", "", 10)
print "New field created."


cursor = arcpy.da.UpdateCursor(fc, ["", ""])
for row in cursor:
    if (row[0] < ):
        row[1] = ""
    elif (row[0] >=  and row[0] < ):
        row[1] = ""
    elif (row[0] >= ):
        row[1] = ""
    cursor.updateRow(row)
del row
del cursor
print "Rows updated with ratings."

#Map Creation

#Previously Created MXD file
mxd = arcpy.mapping.MapDocument("C:/GitHub/GEOG-565-Final-Project/GEOG565Map.mxd")

# Map Document Properties
mxd = arcpy.mapping.MapDocument("C:/Users/saman/OneDrive/Documents/GitHub/GEOG-565-Final-Project/GEOG565Map.mxd")
try:
    # Map Document Properties
    mxd.author = "Amy Dearborn, Samantha Thompson, Patrick Warner"
    mxd.title = "Name of Study Area"
    mxd.summary = "Will add summary later"
    mxd.save()
except Exception as e:
    del mxd
    raise e

try:
    # Adding Layers
    df = arcpy.mapping.ListDataFrames(mxd,"*")[0]
    for df_layer in df:
        if df_layer.name == "contourouput":
            arcpy.mapping.RemoveLayer(df, df_layer)
    addLayer = arcpy.mapping.Layer("C:/Users/saman/Desktop/GEOG 565/Assignment 7/contourouput.shp")
    arcpy.mapping.AddLayer(df, addLayer, "TOP")
    mxd.save()
except Exception as e:
    del mxd
    raise e

#Add Map Elements - North Arrow, Scale Bar, Legend
try:
    scaleBar = arcpy.mapping.ListLayoutElements(mxd, "MAPSURROUND_ELEMENT", "*Scale Bar*")[0]
except Exception as e:
    del mxd
    raise e

try:
    df = arcpy.mapping.ListDataFrames(mxd, scaleBar.parentDataFrameName)[0]
    scaleBar.elementPositionX = df.elementPositionX + (df.elementWidth / 2)
    mxd.save()
except Exception as e:
    del mxd
    raise e

try:
    northArrow = arcpy.mapping.ListLayoutElements(mxd, "MAPSURROUND_ELEMENT", "*North Arrow*")[0]
    df = arcpy.mapping.ListDataFrames(mxd, northArrow.parentDataFrameName)[0]
    scaleBar.elementPositionX = df.elementPositionX + (df.elementWidth / 2)
    mxd.save()
except Exception as e:
    del mxd
    raise e

try:
    # Add Legend
    lyr1 = arcpy.mapping.Layer("C:/Users/saman/Desktop/GEOG 565/Assignment 7/contourouput.shp")
    legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT", "*Legend*")[0]
    legend.autoAdd = True
    arcpy.mapping.AddLayer(df, lyr1, "BOTTOM")
    legend.adjustColumnCount(2)
    mxd.save()
except Exception as e:
    raise e
finally:
    del mxd


#Add Aerial and Topographic Files

df = arcpy.mapping.ListDataFrames(mxd, "New Data Frame")[0]
addLayer = arcpy.mapping.Layer(r"TopoMap.lyr")
arcpy.mapping.AddLayer(df, addLayer, "BOTTOM")
mxd.saveACopy("AS A PDF")

df = arcpy.mapping.ListDataFrames(mxd, "New Data Frame")[0]
addLayer = arcpy.mapping.Layer(r"Aerial Map.lyr")
arcpy.mapping.AddLayer(df, addLayer, "BOTTOM")
mxd.saveACopy("AS A PDF")

del mxd, addLayer


#Create PDF of Map Pages
pdfpath = ""
pdfdoc = arcpy.mapping.PDFDocumentCreate(pdfpath)

mapdoc = arcpy.mapping.MapDocument(".mxd")
mapdoc.dataDrivenPages.exportToPDF(".pdf")

pdfdoc.appendPages("Reference Page")
pdfdoc.appendPages("Aerial Map")
pdfdoc.appendPages ("Topo Map")

pdfdoc.updateDocProperties(pdf_title="",
                           pdf_author="")
                        
pdfdoc.saveAndClose()
del mapdoc
