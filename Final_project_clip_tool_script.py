#===============================================================================


#GEOG 565 FINAL: WESTERN WASHINGTON WETLANDS RATINGS DATA CLIPPER TOOL

#By Amy Dearborn, Samantha Thompson, and Patrick Warner


#===============================================================================


import arcpy, os
from arcpy import env
from arcpy.sa import *

#Set workspace and out path (preferably the tool gdb).
env.workspace = arcpy.GetParameterAsText(0)
env.overwriteOutput = True
out_path = arcpy.GetParameterAsText(1)
clip_feature = arcpy.GetParameterAsText(2)

#Inputs for the tool
#Buffer Inputs
input_streams = arcpy.GetParameterAsText(3)
dissolve_field_streams = arcpy.GetParameterAsText(4)
input_bodies = arcpy.GetParameterAsText(5)
dissolve_field_bodies = arcpy.GetParameterAsText(6)

#Landcover Inputs
input_landcover = arcpy.GetParameterAsText(7)
lc_shapefile = arcpy.GetParameterAsText(8)

#Basin Inputs
wria_basin = arcpy.GetParameterAsText(9)

#Soil Input
soils = arcpy.GetParameterAsText(10)

#Parcel ownership input
parcels = arcpy.GetParameterAsText(11)


try:
    #Container for intermediate clip layers
    clip_dict=[]
    #Clipping inital water shapefiles meant to be buffered.
    buffer_distance = "1 Kilometer"
    arcpy.AddMessage("Clipping " + input_streams + " to " + clip_feature +"...")
    clip_streams = os.path.join(out_path, os.path.basename("streams_clip"))
    arcpy.Clip_analysis(input_streams, clip_feature, clip_streams)
    arcpy.AddMessage("Feature clipped.")
    #First Buffer is created. 
    arcpy.AddMessage("Creating " + buffer_distance + " buffer around flowline....")
    output_buffer_streams = os.path.join(out_path, 
                                         os.path.basename("streams_buffer"))
    arcpy.Buffer_analysis(clip_streams,
                          output_buffer_streams,
                          buffer_distance,
                          "", "", "LIST",
                          dissolve_field_streams)
    #Repair Geometries to make buffers uncorruptable
    arcpy.AddMessage("Flowline Buffer Created...repairing geometries...")
    arcpy.RepairGeometry_management(output_buffer_streams)
    arcpy.AddMessage("Geometries repaired.")
    #If loop to determine if there are two buffers, if so, then it creates another buffer,
    #merges it with the first, and dissolves it, or it just dissolves the first buffer.
    if input_bodies != "":
        arcpy.AddMessage("Clipping " + input_streams + " to " + clip_feature +"...")
        clip_body = os.path.join(out_path, os.path.basename("bodies_clip"))
        arcpy.Clip_analysis(input_bodies, clip_feature, clip_body)
        arcpy.AddMessage("Feature clipped.")
        arcpy.AddMessage("Creating " + buffer_distance + " buffer around waterbodies....")
        output_buffer_bodies = os.path.join(out_path,
                                        os.path.basename("water_bodies_buffer"))
        arcpy.Buffer_analysis(clip_body,
                              output_buffer_bodies,
                              buffer_distance,
                              "", "", "LIST",
                              dissolve_field_bodies)
        arcpy.AddMessage("Water Bodies Buffer Created...repairing geometries...")
        arcpy.RepairGeometry_management(output_buffer_bodies)
        arcpy.AddMessage("Geometries repaired...uniting flowline and water bodies buffers...")
        union_buffer = os.path.join(out_path,
                                    os.path.basename("water_union"))
        arcpy.Union_analysis([output_buffer_streams, output_buffer_bodies], union_buffer)
        arcpy.AddMessage("Union complete...deleting previous buffer shapefiles...")
        arcpy.Delete_management(output_buffer_streams)
        arcpy.Delete_management(output_buffer_bodies)
        arcpy.AddMessage("Previous buffer shapefiles deleted....dissolving union buffer...")
        dissolved_buffer_final = os.path.join(out_path,
                                              os.path.basename("final_buff"))
        arcpy.Dissolve_management(union_buffer,
                                  dissolved_buffer_final,
                                  [dissolve_field_streams,
                                   dissolve_field_bodies])
        arcpy.AddMessage("Dissolve complete....deleting union buffer...")
        arcpy.Delete_management(union_buffer)
        arcpy.AddMessage("Union Buffer deleted.")
        #Only one buffer, then the elif dissolves it by the specified field
    elif input_bodies == "":
        arcpy.AddMessage("Dissolving buffer...")
        dissolved_buffer_final = os.path.join(out_path,
                                        os.path.basename("buff_final"))
        arcpy.Dissolve_management(output_buffer_streams,
                                  dissolved_buffer_final,
                                  dissolve_field_streams)
        arcpy.AddMessage("Buffer dissolved...deleting previous buffer...")
        arcpy.Delete_management(output_buffer_streams)
        arcpy.AddMessage("Buffer deleted.")
    #Loop to determine if the landcover is either a raster or a shapefile
    #Both fields will be optional, but one needs to be filled for the tool to work
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
        arcpy.AddMessage("Checked out Spatial Analyst Extension.")
        if input_landcover != "":
            query = "VALUE IN (90, 95)"
            arcpy.AddMessage("Extracting wetland attributes from landcover raster...")
            wet_lc = ExtractByAttributes(input_landcover,
                                         query)
            arcpy.AddMessage("Converting raster to polygon...")
            output_lc = os.path.join(out_path, os.path.basename("lc_to_shp"))
            rast_to_fc = arcpy.RasterToPolygon_conversion(wet_lc,
                                                          output_lc)
            arcpy.AddMessage("Raster to polygon conversion complete....clipping to " + clip_feature + "...")
            clip_lc = os.path.join(out_path, os.path.basename("lc_clip"))
            arcpy.Clip_analysis(output_lc, clip_feature, clip_lc)
            clip_dict.append(clip_lc)
            arcpy.AddMessage(clip_lc + " clipped to " + clip_feature + ".")
        elif input_landcover == "":
            pass
        if lc_shapefile != "":
            arcpy.AddMessage("Clipping " + lc_shapefile + " to " + clip_feature + "...")
            clip_lc = os.path.join(out_path, os.path.basename("lc_clip"))
            arcpy.Clip_analysis(lc_shapefile, clip_feature, clip_lc)
            clip_dict.append(clip_lc)
            arcpy.AddMessage(clip_lc + " clipped to " + clip_feature + ".")
        elif lc_shapefile == "":
            pass
            
    else:
        arcpy.AddMessage("Spatial Analyst is unavailable")

    #Next series of loops to determine if they have files to clip     
    arcpy.AddMessage("Clipping Remaining features to " + clip_feature + "...")
    if soils != "":
        clip_soils = os.path.join(out_path, os.path.basename("soils_clip"))
        arcpy.Clip_analysis(soils, clip_feature, clip_soils)
        clip_dict.append(clip_soils)
        arcpy.AddMessage(clip_soils + " clipped.")
    elif soils == "":
        pass
    if wria_basin != "":
        clip_wria = os.path.join(out_path, os.path.basename("wria_clip"))
        arcpy.Clip_analysis(wria_basin, clip_feature, clip_wria)
        clip_dict.append(clip_wria)
        arcpy.AddMessage(clip_wria + " clipped.")
    elif wria_basin == "":
        pass
    if parcels != "":
        clip_parcels = os.path.join(out_path, os.path.basename("parcels_clip"))
        arcpy.Clip_analysis(parcels, clip_feature, clip_parcels)
        clip_dict.append(clip_parcels)
        arcpy.AddMessage(clip_parcels + " clipped!")
    elif parcels == "":
        pass
    arcpy.AddMessage("All available features clipped to " + clip_feature + ".")
                                                                    
    #Clip all files to the buffer 
    for clip in clip_dict:
        desc = arcpy.Describe(clip)
        arcpy.AddMessage("Clipping " + str(desc.basename) + "...")
        clipper = arcpy.Clip_analysis(clip, dissolved_buffer_final, os.path.join(out_path, os.path.basename(str(clip) + "_final")))
        arcpy.AddMessage(str(desc.basename) + " shapefile clipped...")

    #Get rid of intermediate clip shapefiles
    arcpy.AddMessage("Deleting non-buffer clipped shapefiles...")
    arcpy.Delete_management(clip_soils)
    arcpy.Delete_management(clip_lc)
    arcpy.Delete_management(clip_wria)
    arcpy.Delete_management(clip_parcels)
    arcpy.Delete_management(clip_streams)
    if input_bodies != "":
        arcpy.Delete_management(clip_body)
    else:
        pass
    arcpy.AddMessage("Shapefiles deleted.")

except arcpy.ExecuteError as d:
    raise d
except TypeError as e:
    raise e
except ValueError as f:
   raise f
except IOError as g:
    raise g
except EnvironmentError as h:
    raise h
finally:
    arcpy.AddMessage("Script Finished.")
