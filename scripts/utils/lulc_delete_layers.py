#!/usr/bin/env python2
# Geonode

__version__ = "0.2.1"

# Setup GeoNode environment
import os
import sys
from pprint import pprint
from os.path import abspath, dirname, join
PROJECT_ROOT = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(join(PROJECT_ROOT, 'geonode'))
sys.path.append(PROJECT_ROOT)

import os
from datetime import datetime
from geonode.settings import GEONODE_APPS
from geonode.layers.models import Layer
from geoserver.catalog import Catalog
from geonode.geoserver.helpers import ogc_server_settings
from geonode.layers.models import Style
import geonode.settings as settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")
cat = Catalog(settings.OGC_SERVER['default']['LOCATION'] + 'rest',
                  username=settings.OGC_SERVER['default']['USER'],
                  password=settings.OGC_SERVER['default']['PASSWORD'])
layers = Layer.objects.filter(title__icontains='lulc')
for layer in layers:
    try:
        gs_style = cat.get_style(layer.name)
        print "[" + datetime.now().strftime('%y-%m-%d %h:%m:%s') + "]:",\
        "Deleting style: ", layer.name
        cat.delete(gs_style)
        print "[" + datetime.now().strftime('%y-%m-%d %h:%m:%s') + "]:",\
        "Successfully deleted style:", layer.name
    except Exception:
        pass
    try:
        gs_layer = cat.get_layer(layer.name)
        print "[" + datetime.now().strftime('%y-%m-%d %h:%m:%s') + "]:",\
        "Deleting layer: ", layer.name
        cat.delete(gs_layer)
        print "[" + datetime.now().strftime('%y-%m-%d %h:%m:%s') + "]:",\
        "Successfully deleted layer:", layer.name
    except Exception:
        pass
    print "[" + datetime.now().strftime('%y-%m-%d %h:%m:%s') + "]:",\
    "Deleting object: ", layer.name
    layer.delete()
    print "[" + datetime.now().strftime('%y-%m-%d %h:%m:%s') + "]:",\
    "Successfully deleted object", layer.name
