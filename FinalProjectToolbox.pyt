import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "WaterRatingsToolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [ IntersectTool, StudyAreaTool, ImportLayerTool, MapProductionTool ]


class IntersectTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Intersect Tool"
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


class StudyAreaTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "StudyAreaTool"
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
        #intersect_output = arcpy.Parameter(
        #   displayName="Input to be Clipped to Study Area",
        #  name="intersect_output",
        # datatype="DEShapefile",
        #parameterType="Required",
        #direction="Input")
        #study_area_clip = arcpy.Parameter(
            #displayName="Study Area Clip to Intersect Input",
            #name="study_area_clip",
            #datatype="DEShapefile",
            #parameterType="Required",
            #direction="Output")
        
        return [ point1, point2, point3, point4, study_area_polygon ]
        

    def execute(self, parameters, messages):
        """The source code of the tool."""
        point1_params = parameters[0].valueAsText.split(",")
        point2_params = parameters[1].valueAsText.split(",")
        point3_params = parameters[2].valueAsText.split(",")
        point4_params = parameters[3].valueAsText.split(",")

        study_area_polygon = parameters[4].valueAsText
        # intersect_output = parameters[5].valueAsText
        # study_area_clip = parameters[6].valueAsText

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

        # Clip to Study Area
       # xy_tolerance = ""
       # arcpy.Clip_analysis(intersect_output, study_area_polygon, study_area_clip, xy_tolerance)


class ImportLayerTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "ImportLayerTool"
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
            arcpy.AddMessage("Creating Mapbook")
            pdfdoc = arcpy.mapping.PDFDocumentCreate(pdf_file)
            mxd.dataDrivenPages.exportToPDF(".pdf")

            pdfdoc.appendPages("Map 1")
            pdfdoc.appendPages("Map 2")
            pdfdoc.appendPages("Map 3")

            pdfdoc.updateDocProperties(pdf_title=title, pdf_author=author)
            pdfdoc.saveAndClose()
          
        else:
            arcpy.AddMessage("No Output Mapbook Provided")
        del mxd
