#!/usr/bin/python
#===============================================================================


#GEOG 565 FINAL: WESTERN WASHINGTON WETLANDS RATINGS DATA CLIPPER TOOL

#By Amy Dearborn, Samantha Thompson, and Patrick Warner


#===============================================================================
import arcpy, os
from arcpy import env
from arcpy.sa import *


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [ Intersect, Study_Area, Import_Layer, Map_Production,
            Data_Driven_Pages, Merge_PDFs, Clip_Buffer ]


class Intersect(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Intersect"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        clip_1 = arcpy.Parameter(
            displayName="Clip File 1",
            name="clip_1",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")
        clip_2 = arcpy.Parameter(
            displayName="Clip File 2",
            name="clip_2",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")
        clip_3 = arcpy.Parameter(
            displayName="Clip File 3",
            name="clip_3",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")
        intersect_output = arcpy.Parameter(
            displayName="Intersect Output File",
            name="intersect_output",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Output")
        
        return [ clip_1, clip_2, clip_3, intersect_output ]

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Intersect for Desired Areas
        clip_1 = parameters[0].valueAsText
        clip_2 = parameters[1].valueAsText
        clip_3 = parameters[2].valueAsText
        intersect_output = parameters[3].valueAsText

        cluster_tolerance = 1.5
        in_features = [ clip_1, clip_2, clip_3 ]
        arcpy.Intersect_analysis(in_features, intersect_output, "ALL", cluster_tolerance)


class Study_Area(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Study_Area"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        point1 = arcpy.Parameter(
            displayName="First Point (lat, long)",
            name="point1",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        point2 = arcpy.Parameter(
            displayName="Second Point (lat, long)",
            name="point2",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        point3 = arcpy.Parameter(
            displayName="Third Point (lat, long)",
            name="point3",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        point4 = arcpy.Parameter(
            displayName="Fourth Point (lat, long)",
            name="point4",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        study_area_polygon = arcpy.Parameter(
            displayName="Study Area",
            name="study_area_polygon",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Output")
        
        return [ point1, point2, point3, point4, study_area_polygon ]

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Split the comma separated values into tuples (eg. "1, 4" => ("1", " 4"))
        point1_params = parameters[0].valueAsText.split(",")
        point2_params = parameters[1].valueAsText.split(",")
        point3_params = parameters[2].valueAsText.split(",")
        point4_params = parameters[3].valueAsText.split(",")

        study_area_polygon = parameters[4].valueAsText
        # intersect_output = parameters[5].valueAsText
        # study_area_clip = parameters[6].valueAsText

        # Lambda function for converting tuples into a Point and removing
        # any leading or trailing white space
        to_point = lambda pt: arcpy.Point(pt[0].strip(), pt[1].strip())
        array = arcpy.Array([
            to_point(point1_params),
            to_point(point2_params),
            to_point(point3_params),
            to_point(point4_params)])
        arcpy.AddMessage("Creating polygon from these points: " + 
            ','.join(point1_params) + ", " + ','.join(point1_params) + ", " + 
            ','.join(point1_params) + ", " + ','.join(point1_params))
        
        polygon = arcpy.Polygon(array)
        arcpy.CopyFeatures_management([polygon], study_area_polygon)
        arcpy.AddMessage("Study Area Created")


class Import_Layer(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Import_Layer"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        mxd_file = arcpy.Parameter(
            displayName="Map Document",
            name="mxd_file",
            datatype="DEMapDocument",
            parameterType="Required",
            direction="Input")
        layer = arcpy.Parameter(
            displayName="Layer",
            name="layers",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")
        return [ mxd_file, layer ]
    
    def execute(self, parameters, messages):
        """The source code of the tool."""
        mxd_file = parameters[0].valueAsText
        layer = parameters[1].valueAsText

        #Previously Created MXD file
        mxd = arcpy.mapping.MapDocument(mxd_file)

        # Adding Layer
        arcpy.AddMessage("Adding Layer")
        try:
            df = arcpy.mapping.ListDataFrames(mxd,"*")[0]
            # Remove existing layers with the same name
            for df_layer in df:
                if df_layer.name == layer:
                    arcpy.mapping.RemoveLayer(df, df_layer)
            add_layer = arcpy.mapping.Layer(layer)
            arcpy.mapping.AddLayer(df, add_layer, "TOP")
            legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT", "*Legend*")[0]
            legend.autoAdd = True
            arcpy.mapping.AddLayer(df, add_layer, "BOTTOM")
            legend.adjustColumnCount(2)
            del add_layer
            mxd.save()
        except Exception as e:
            raise e
        finally:
            del mxd


class Map_Production(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Map_Production "
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        mxd_file = arcpy.Parameter(
            displayName="Map Document",
            name="mxd_file",
            datatype="DEMapDocument",
            parameterType="Required",
            direction="Input")
        author = arcpy.Parameter(
            displayName="Mxd Author",
            name="author",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        title = arcpy.Parameter(
            displayName="Mxd Title",
            name="title",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        summary = arcpy.Parameter(
            displayName="Mxd Summary",
            name="summary",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        reference_file = arcpy.Parameter(
            displayName="Aerial/Topographic Imagery",
            name="reference_file",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input")
        pdf_file = arcpy.Parameter(
            displayName="PDF File",
            name="pdf_file",
            datatype="DEFile",
            parameterType="Optional",
            direction="Output")
        return [ mxd_file, author, title, summary, reference_file, pdf_file ]

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Lambda function for getting text value if the input is not null
        # Handles optional (null) values
        optional_as_text = lambda p: None if p is None else p.valueAsText
        arcpy.AddMessage("Running MapProductionTool")

        mxd_file = parameters[0].valueAsText
        author = optional_as_text(parameters[1])
        title = optional_as_text(parameters[2])
        summary = optional_as_text(parameters[3])

        reference_file = optional_as_text(parameters[4])
        pdf_file = optional_as_text(parameters[5])

        #Previously Created MXD file
        mxd = arcpy.mapping.MapDocument(mxd_file)

        # Map Document Properties
        if author:
            mxd.author = author
        if title:
            mxd.title = title
        if summary:
            mxd.summary = summary

        if author or title or summary:
            try:
                mxd.save()
            except Exception as e:
                del mxd
                raise e

        #Map Elements - North Arrow, Scale Bar, Legend
        try:
            scale_bar = arcpy.mapping.ListLayoutElements(mxd, "MAPSURROUND_ELEMENT", "*Scale Bar*")[0]
        except Exception as e:
            del mxd
            raise e

        try:
            df = arcpy.mapping.ListDataFrames(mxd, scale_bar.parentDataFrameName)[0]
            scale_bar.elementPositionX = df.elementPositionX + (df.elementWidth / 2)
            mxd.save()
        except Exception as e:
            del mxd
            raise e

        try:
            north_arrow = arcpy.mapping.ListLayoutElements(mxd, "MAPSURROUND_ELEMENT", "*North Arrow*")[0]
            df = arcpy.mapping.ListDataFrames(mxd, north_arrow.parentDataFrameName)[0]
            scale_bar.elementPositionX = df.elementPositionX + (df.elementWidth / 3)
            mxd.save()
        except Exception as e:
            del mxd
            raise e
         
        #Add Aerial and Topographic Files - Files must already exist

        df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        if reference_file:
            arcpy.AddMessage("Adding Reference Map")
            add_layer = arcpy.mapping.Layer(reference_file)
            arcpy.mapping.AddLayer(df, add_layer, "BOTTOM")
            mxd.save()
            del add_layer
        else:
            arcpy.AddMessage("No Reference Map Provided")
        
        if pdf_file:
            #Create PDF of Map Pages
            arcpy.AddMessage("Creating PDF")
            arcpy.mapping.ExportToPDF(mxd, pdf_file)
        else:
            arcpy.AddMessage("No Output Mapbook Provided")
        del mxd


class Data_Driven_Pages(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Data_Driven_Pages "
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        mxd_file = arcpy.Parameter(
            displayName="Map Document",
            name="mxd_file",
            datatype="DEMapDocument",
            parameterType="Required",
            direction="Input")
        pages = arcpy.Parameter(
            displayName="Pages (range, list, or range and list, all - leave blank)",
            name="pages",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        pdf_file = arcpy.Parameter(
            displayName="PDF File",
            name="pdf_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Output")
        return [ mxd_file, pages, pdf_file ]

    def execute(self, parameters, messages):
        """The source code of the tool."""
        mxd_file = parameters[0].valueAsText
        pages = parameters[1].valueAsText
        pdf_file = parameters[2].valueAsText

        mxd = arcpy.mapping.MapDocument(mxd_file)
        if pages:
            mxd.dataDrivenPages.exportToPDF(pdf_file, "RANGE", pages)
        else:
            mxd.dataDrivenPages.exportToPDF(pdf_file, "ALL")
        del mxd


class Merge_PDFs(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Merge_PDFs"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        in_pdf1 = arcpy.Parameter(
            displayName="Input PDF File",
            name="in_pdf1",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")
        in_pdf2 = arcpy.Parameter(
            displayName="Input PDF File",
            name="in_pdf2",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")
        out_pdf = arcpy.Parameter(
            displayName="Output PDF File",
            name="out_pdf",
            datatype="DEFile",
            parameterType="Required",
            direction="Output")
        return [ in_pdf1, in_pdf2, out_pdf ]

    def execute(self, parameters, messages):
        """The source code of the tool."""
        in_pdf1 = parameters[0].valueAsText
        in_pdf2 = parameters[1].valueAsText
        out_pdf = parameters[2].valueAsText

        pdfDoc = arcpy.mapping.PDFDocumentCreate(out_pdf)
        pdfDoc.appendPages(in_pdf1)
        pdfDoc.appendPages(in_pdf2)
        pdfDoc.saveAndClose()
        del pdfDoc


class Clip_Buffer(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Clip_Buffer"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        workspace = arcpy.Parameter(
            displayName="Workspace",
            name="workspace",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")
        out_path = arcpy.Parameter(
            displayName="Output Path",
            name="out_path",
            datatype="DEFolder",
            parameterType="Required",
            direction="Output")
        clip_feature = arcpy.Parameter(
            displayName="Clip Feature",
            name="clip_feature",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")
        input_streams = arcpy.Parameter(
            displayName="River / Streams Input",
            name="input_streams",
            datatype="DEShapefile",
            parameterType="Optional",
            direction="Input")
        dissolve_field_streams = arcpy.Parameter(
            displayName="River / Streams Dissolve Input",
            name="dissolve_field_streams",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        input_bodies = arcpy.Parameter(
            displayName="Water Bodies Input",
            name="input_bodies",
            datatype="DEShapefile",
            parameterType="Optional",
            direction="Input")
        dissolve_field_bodies = arcpy.Parameter(
            displayName="Water Bodies Dissolve Field",
            name="dissolve_field_bodies",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        input_landcover = arcpy.Parameter(
            displayName="NLCD Landcover Raster Input",
            name="input_landcover",
            datatype="GPRasterLayer",
            parameterType="Optional",
            direction="Input")
        lc_shapefile = arcpy.Parameter(
            displayName="Landcover / Wetlands Shapefile Input",
            name="lc_shapefile",
            datatype="DEShapefile",
            parameterType="Optional",
            direction="Input")
        wria_basin = arcpy.Parameter(
            displayName="WRIA Basin Input",
            name="wria_basin",
            datatype="DEShapefile",
            parameterType="Optional",
            direction="Input")
        soils = arcpy.Parameter(
            displayName="Soils Input",
            name="soils",
            datatype="DEShapefile",
            parameterType="Optional",
            direction="Input")
        parcels = arcpy.Parameter(
            displayName="Parcels Input",
            name="soils",
            datatype="DEShapefile",
            parameterType="Optional",
            direction="Input")
        
        
        return [ workspace, out_path, clip_feature, input_streams, dissolve_field_streams, input_bodies,
            dissolve_field_bodies, input_landcover, lc_shapefile, wria_basin, soils, parcels ]

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # The variable i makes it easier to rearrange parameters.
        # Don't have to change the index, just copy/paste the line where you want it
        i = 0
        workspace = parameters[i].valueAsText
        i += 1
        out_path = parameters[i].valueAsText
        i += 1
        env.workspace = workspace
        env.overwriteOutput = True
        
        # Inputs for the tool
        # Buffer Inputs
        clip_feature = parameters[i].valueAsText
        i += 1
        input_streams = parameters[i].valueAsText
        i += 1
        dissolve_field_streams = parameters[i].valueAsText
        i += 1
        input_bodies = parameters[i].valueAsText
        i += 1
        dissolve_field_bodies = parameters[i].valueAsText
        i += 1
        
        #Landcover Inputs
        input_landcover = parameters[i].valueAsText
        i += 1
        lc_shapefile = parameters[i].valueAsText
        i += 1
        
        # Basin Inputs OPTIONAL
        wria_basin = parameters[i].valueAsText
        i += 1

        # Soil Input OPTIONAL
        soils = parameters[i].valueAsText
        i += 2

        # Parcel ownership input
        parcels = parameters[i].valueAsText
        try:
            # Container for intermediate clip layers
            clip_dict=[]

            # Clipping inital water shapefiles meant to be buffered.
            buffer_distance = "1 Kilometer"
            arcpy.AddMessage("Clipping " + input_streams + " to " + clip_feature +"...")
            clip_streams = os.path.join(out_path, os.path.basename("streams_clip"))
            arcpy.Clip_analysis(input_streams, clip_feature, clip_streams)
            arcpy.AddMessage("Feature clipped.")
            
            # First Buffer is created. 
            arcpy.AddMessage("Creating " + buffer_distance + " buffer around flowline....")
            output_buffer_streams = os.path.join(out_path, 
                                                os.path.basename("streams_buffer"))
            arcpy.Buffer_analysis(clip_streams,
                                output_buffer_streams,
                                buffer_distance,
                                "", "", "LIST",
                                dissolve_field_streams)
            
            # Repair Geometries to make buffers uncorruptable
            arcpy.AddMessage("Flowline Buffer Created...repairing geometries...")
            arcpy.RepairGeometry_management(output_buffer_streams)
            arcpy.AddMessage("Geometries repaired.")
            
            if input_bodies != "":
                # Iif there are two buffers, then creates another buffer,
                # merges it with the first, and dissolves it, or it just dissolves the first buffer.
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
            elif input_bodies == "":
                #Only one buffer, then the elif dissolves it by the specified field
                arcpy.AddMessage("Dissolving buffer...")
                dissolved_buffer_final = os.path.join(out_path,
                                                os.path.basename("buff_final"))
                arcpy.Dissolve_management(output_buffer_streams,
                                        dissolved_buffer_final,
                                        dissolve_field_streams)
                arcpy.AddMessage("Buffer dissolved...deleting previous buffer...")
                arcpy.Delete_management(output_buffer_streams)
                arcpy.AddMessage("Buffer deleted.")

            if arcpy.CheckExtension("Spatial") == "Available":
                #Loop to determine if the landcover is either a raster or a shapefile
                #Both fields will be optional, but one needs to be filled for the tool to work
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

            # Next series of loops to determine if they have files to clip     
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

