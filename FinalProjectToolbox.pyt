import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "WaterRatingsToolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [ IntersectTool, StudyAreaTool, MapProductionTool ]


class IntersectTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "MapProductionTool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        basin_clip = arcpy.Parameter(
            displayName="Basin Clip File",
            name="basin_clip",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")
        lc_clip = arcpy.Parameter(
            displayName="Landcover Clip File",
            name="lc_clip",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")
        parcel_clip = arcpy.Parameter(
            displayName="Parcel Clip File",
            name="parcel_clip",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")
        intersect_output = arcpy.Parameter(
            displayName="Intersect Output File",
            name="intersect_output",
            datatype="GPString",
            parameterType="Required",
            direction="Output")
        
        return [ basin_clip, lc_clip, parcel_clip, intersect_output ]

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Intersect for Desired Areas
        basin_clip = parameters[0].valueAsText
        lc_clip = parameters[1].valueAsText
        parcel_clip = parameters[2].valueAsText
        intersect_output = parameters[3].valueAsText

        cluster_tolerance = 1.5
        in_features = [ basin_clip, lc_clip, parcel_clip ]
        arcpy.Intersect_analysis(in_features, intersect_output, "", cluster_tolerance, "polygon")


class StudyAreaTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "MapProductionTool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        study_area_polygon = arcpy.Parameter(
            displayName="Define Study Area",
            name="study_area_polygon",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")
            
        point1 = arcpy.Parameter(
            displayName="First Point (lat, long)",
            name="study_area_clip",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        point2 = arcpy.Parameter(
            displayName="Second Point (lat, long)",
            name="study_area_clip",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        point3 = arcpy.Parameter(
            displayName="Third Point (lat, long)",
            name="study_area_clip",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        point4 = arcpy.Parameter(
            displayName="Forth Point (lat, long)",
            name="study_area_clip",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        study_area_output = arcpy.Parameter(
            displayName="Study Area",
            name="study_area_output",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        return [ study_area_clip, point1, point2, point3, point4, study_area_output ]
        

    def execute(self, parameters, messages):
        """The source code of the tool."""
        study_area_polygon = parameters[0].valueAsText

        point1_params = parameters[1].valueAsText.split(",")
        point2_params = parameters[2].valueAsText.split(",")
        point3_params = parameters[3].valueAsText.split(",")
        point4_params = parameters[4].valueAsText.split(",")

        study_area_output = parameters[5].valueAsText

        to_point = lambda pt: arcpy.Point(pt[0].strip(), pt[1].strip())
        array = arcpy.Array(
            to_point(point1_params),
            to_point(point2_params),
            to_point(point3_params),
            to_point(point4_params))
        arcpy.AddMessage("Creating polygon from these points: " + 
            point1_params + ", " + point1_params + ", " + 
            point1_params + ", " + point1_params)
        
        polygon = arcpy.Polygon(array)
        arcpy.CopyFeatures_management([polygon], study_area_polygon)
        arcpy.AddMessage["Study Area Created"]

        # Clip to Study Area
        xy_tolerance = ""
        arcpy.Clip_analysis(intersectOuput, study_area_polygon, study_area_output, xy_tolerance)


class MapProductionTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "MapProductionTool"
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
        
        layers = arcpy.Parameter(
            displayName="Layers (Comma separated)",
            name="layers",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        aerial_file = arcpy.Parameter(
            displayName="Aerial File",
            name="aerial_file",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        topographic_file = arcpy.Parameter(
            displayName="Topographic File",
            name="topographic_file",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        pdf_file = arcpy.Parameter(
            displayName="PDF File",
            name="pdf_file",
            datatype="GPString",
            parameterType="Optional",
            direction="Output")
        
        return [ mxd_file, author, title, summary, layers, aerial_file, topographic_file, pdf_file ]

    def execute(self, parameters, messages):
        """The source code of the tool."""
        optional_as_text = lambda p: None if p is None else p.valueAsText
        arcpy.AddMessage("Running MapProductionTool")

        mxd_file = parameters[0].valueAsText
        author = optional_as_text(parameters[1])
        title = optional_as_text(parameters[2])
        summary = optional_as_text(parameters[3])

        layers = optional_as_text(parameters[4])
        aerial_file = optional_as_text(parameters[5])
        topographic_file = optional_as_text(parameters[6])
        pdf_file = optional_as_text(parameters[7])

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

        # Adding Layers
        if layers:
            layers = layers.split(",")
            arcpy.AddMessage("Adding Layers")
            try:
                for layer in layers:
                    layer = layer.strip()
                    df = arcpy.mapping.ListDataFrames(mxd,"*")[0]
                    # Remove existing layers with the same name
                    for df_layer in df:
                        if df_layer.name == layer:
                            arcpy.mapping.RemoveLayer(df, df_layer)
                    add_layer = arcpy.mapping.Layer(layer + ".shp")
                    arcpy.mapping.AddLayer(df, add_layer, "TOP")
                    del add_layer
                mxd.save()
            except Exception as e:
                del mxd
                raise e
        else:
            arcpy.AddMessage("No Layers Provided")


        # Add Map Elements - North Arrow, Scale Bar, Legend
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

        try:
            for layer in layers:
                layer = layer.strip()
                lyr = arcpy.mapping.Layer(layer + ".shp")
                legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT", "*Legend*")[0]
                legend.autoAdd = True
                arcpy.mapping.AddLayer(df, lyr, "BOTTOM")
                legend.adjustColumnCount(2)
                mxd.save()
        except Exception as e:
            raise e
        finally:
            del mxd
        arcpy.AddMessage("Map Elments Edited")


        #Add Aerial and Topographic Files - Files must already exist

        df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        if aerial_file:
            arcpy.AddMessage("Adding Aerial Map")
            add_layer = arcpy.mapping.Layer(aerial_file)
            arcpy.mapping.AddLayer(df, add_layer, "BOTTOM")
            mxd.saveACopy()
            del add_layer
        else:
            arcpy.AddMessage("No Aerial Map Provided")
        
        if aerial_file:
            arcpy.AddMessage("Adding Topo Map")
            add_layer = arcpy.mapping.Layer(topographic_file)
            arcpy.mapping.AddLayer(df, add_layer, "BOTTOM")
            mxd.saveACopy()
            del add_layer
        else:
            arcpy.AddMessage("No Topo Map Provided")

        del mxd

        if pdf_file:
            #Create PDF of Map Pages
            arcpy.AddMessage("Creating Mapbook")
            pdfdoc = arcpy.mapping.PDFDocumentCreate(pdf_file)
            mapdoc = arcpy.mapping.MapDocument(".mxd")
            mapdoc.dataDrivenPages.exportToPDF(".pdf")

            pdfdoc.appendPages("Map 1")
            pdfdoc.appendPages("Map 2")
            pdfdoc.appendPages("Map 3")

            pdfdoc.updateDocProperties(pdf_title=title, pdf_author=author)
            pdfdoc.saveAndClose()
            del mapdoc
        else:
            arcpy.AddMessage("No Output Mapbook Provided")
