import os
import traceback
from geonode.settings import GEONODE_APPS
from geonode.geoserver.helpers import ogc_server_settings
from geoserver.catalog import Catalog
from geonode.layers.models import Style
import geonode.settings as settings
from geonode.layers.models import Layer
from pprint import pprint
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")

class Muni:
    def __init__(self, MCode, PCode, MName, PName):
        self.MCode = MCode
        self.PCode = PCode
        self.MName = MName
        self.PName = PName

    def getMName(self):
        return self.MName

    def getPName(self):
        return self.PName

def getLayerType(split):
    layertypes = ["dtm", "chm", "cov", "boundary", "class", "diss", "classdiss", "agb", "cs"]
    for layertype in layertypes:
        if layertype in split:
            return layertype
    return "unknown"

def getSupp(split):
    supps = ["bp", "bpf", "ob", "obf", "cb", "cbf", "nm", "nmf"]
    for supp in supps:
        if supp in split:
            return supp
    return ""

def getTitle(muni, layertype, supp):
    if supp == "bp" or supp == "bpf":
        supp = " of Broadleaf Plantation"
    elif supp == "ob" or supp == "obf":
        supp = " of Open Broadleaf Forest"
    elif supp == "cb" or supp  == "cbf":
        supp = " of Closed Broadleaf Forest"
    elif supp == "nm" or supp == "nmf":
        supp == " of Natural Mangrove Forest"
    if layertype == "dtm":
        return "Digital Terrain Model (DTM) for the Municipality of %s, %s." % (muni.MName, muni.PName)
    elif layertype == "chm":
        return "Canopy Height Model (CHM) for the Municipality of %s, %s." % (muni.MName, muni.PName)
    elif layertype == "cov":
        return "Canopy Cover Model (CCM)%s for the Municipality of %s, %s." % (muni.MName, muni.PName)
    elif layertype == "boundary":
        return "LiDAR Boundary for the Municipality of %s, %s." % (muni.MName, muni.PName)
    elif layertype == "class" or layertype == "diss" or layertype == "classdiss":
        return "Forest Cover Classification for the Municipality of %s, %s." % (muni.MName, muni.PName)
    elif layertype == "agb":
        return "Above-Ground Biomass (AGB)%s estimation for the Municipality of %s, %s." % (supp, muni.MName, muni.PName)
    elif layertype == "cs":
        return "Carbon Stock (CS)%s estimation for the Municipality of %s, %s." % (supp, muni.MName, muni.PName)

def getAbstract(layertype):
    if layertype == "dtm":
        return "A raster dataset (tif file) of the terrain's surface created from the LiDAR elevation values. The dataset was prepared by the Phil-LiDAR 2: Project 3 of (SUC/HEI) and reviewed by Phil-LiDAR 2 Project 3 of the University of the Philippines Training Center for Applied Geodesy and Photogrammetry. The use of this dataset is covered by End Users License Agreement (EULA). Datasets are subjected to updating and only shows land cover on the date of LiDAR acquisition."
    elif layertype == "chm":
        return "A raster dataset (tif file) that maps out the height of trees as a continuous surface. The dataset was prepared by the Phil-LiDAR 2: Project 3 of (SUC/HEI) and reviewed by Phil-LiDAR 2 Project 3 of the University of the Philippines Training Center for Applied Geodesy and Photogrammetry. The use of this dataset is covered by End Users License Agreement (EULA). Datasets are subjected to updating and only shows land cover on the date of LiDAR acquisition."
    elif layertype == "cov":
        return "A raster dataset (tif file) that maps out the proportion of the forest floor covered by the vertical projection. The dataset was prepared by the Phil-LiDAR 2: Project 3 of (SUC/HEI) and reviewed by Phil-LiDAR 2 Project 3 of the University of the Philippines Training Center for Applied Geodesy and Photogrammetry. The use of this dataset is covered by End Users License Agreement (EULA). Datasets are subjected to updating and only shows land cover on the date of LiDAR acquisition."    
    elif layertype == "boundary":
        return "A vector dataset (shapefile) that provides the LiDAR boundary used in the processing. The dataset was prepared by the Phil-LiDAR 2: Project 3 of (SUC/HEI) and reviewed by Phil-LiDAR 2 Project 3 of the University of the Philippines Training Center for Applied Geodesy and Photogrammetry. The use of this dataset is covered by End Users License Agreement (EULA). Datasets are subjected to updating and only shows land cover on the date of LiDAR acquisition."
    elif layertype == "class" or layertype == "diss" or layertype == "classdiss":
        return "A vector dataset (shapefile) that maps the classified forest cover of the municipality using LiDAR data. The forest boundary used for the processing was based on the NAMRIA 2010 Land Cover Map. The dataset was prepared by the Phil-LiDAR 2: Project 3 of (SUC/HEI) and reviewed by Phil-LiDAR 2 Project 3 of the University of the Philippines Training Center for Applied Geodesy and Photogrammetry. The use of this dataset is covered by End Users License Agreement (EULA). Datasets are subjected to updating and only shows land cover on the date of LiDAR acquisition."
    elif layertype == "agb":
        return "A raster data (tif format) that maps the AGB estimation obtained by applying the estimated mean DBH to Brown's formula. The dataset was prepared by the Phil-LiDAR 2: Project 3 of (SUC/HEI) and reviewed by Phil-LiDAR 2 Project 3 of the University of the Philippines Training Center for Applied Geodesy and Photogrammetry. The use of this dataset is covered by End Users License Agreement (EULA). Datasets are subjected to updating and only shows land cover on the date of LiDAR acquisition."
    elif layertype == "cs":
        return "A raster data (tif format) that maps the amount of carbon on the forested areas in the municipality. The dataset was prepared by the Phil-LiDAR 2: Project 3 of (SUC/HEI) and reviewed by Phil-LiDAR 2 Project 3 of the University of the Philippines Training Center for Applied Geodesy and Photogrammetry. The use of this dataset is covered by End Users License Agreement (EULA). Datasets are subjected to updating and only shows land cover on the date of LiDAR acquisition."

def style_update(layer, style_template):
    cat = Catalog(settings.OGC_SERVER['default']['LOCATION'] + 'rest',
                  username=settings.OGC_SERVER['default']['USER'],
                  password=settings.OGC_SERVER['default']['PASSWORD'])
    try:
        layer_attrib = layer.attributes[0].attribute.encode("utf-8")
    except Exception as e:
        pprint("No layer attribute!")
        return

    style = None
    style = cat.get_style(style_template)

    if style is not None:
        try:
            gs_layer = cat.get_layer(layer.name)
            pprint("GS LAYER: %s ", gs_layer.name)
            gs_layer._set_default_style(style)
            cat.save(gs_layer)
            gs_style = cat.get_style(layer.name)
            if gs_style:
                pprint("GS STYLE: %s " % gs_style.name)
                pprint("Geoserver: Will delete style %s ", gs_style.name)
                cat.delete(gs_style)
                gn_style = Style.objects.get(name=layer.name)
                pprint("Geonode: Will delete style %s ", gn_style.name)
                gn_style.delete()

            layer.sld_body = style.sld_body
            layer.save()
        except Exception as e:
            pprint("Error setting style")

def _update(layer, style_template):
    try:
        municipalities = {}
        csv = open("PH_codes.csv")
        for line in csv.readlines():
            split = line.strip().split(",")
            split = [str(x) for x in split]
            muni = Muni(split[0], split[1], split[2], split[3])
            municipalities[(split[0].lower(),split[1].lower())] = muni
        
        split = layer.name.split("_")
        split = [str(x.lower()) for x in split]
        muni = municipalities[(split[1],split[0])]
        layertype = getLayerType(split[2:])
        supp = getSupp(split[2:])

        if layertype == "unknown":
            raise Exception

        pprint(layer.name)
        pprint("Setting title")
        layer.title = getTitle(muni, layertype, supp)
        pprint("Setting abstract")
        layer.abstract = getAbstract(layertype)
        pprint("Saving layer")
        layer.save()
        pprint("Success")

    except Exception:
        #print traceback.format_exc()
        pprint("Error setting metadata!")

layers = Layer.objects.filter(name__icontains="")
style_template = '<sld template name>'

counter = 0
for layer in layers:
    if len(layer.title) == len(layer.name):
        _update(layer, style_template)
        counter = counter + 1
pprint(counter)
