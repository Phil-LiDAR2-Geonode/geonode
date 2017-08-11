#!/usr/bin/env python
from geonode.settings import GEONODE_APPS
import geonode.settings as settings

from geonode.layers.models import Style, Layer
from geoserver.catalog import Catalog
from os.path import dirname, abspath
import argparse
import logging
import os
import subprocess
import time
from datetime import datetime, timedelta
from geonode.base.models import TopicCategory
import getpass


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")

logger = logging.getLogger()
LOG_LEVEL = logging.INFO
FILE_LOG_LEVEL = logging.INFO
LOG_FOLDER = dirname(abspath(__file__)) + '/logs/'

cat = Catalog(settings.OGC_SERVER['default']['LOCATION'] + 'rest',
              username=settings.OGC_SERVER['default']['USER'],
              password=settings.OGC_SERVER['default']['PASSWORD'])

# STYLE = 'test_sld.sld'


def setup_logging():

    # Setup logging
    logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('[%(asctime)s] %(filename)s \
(%(levelname)s,%(lineno)d)\t: %(message)s')

    # Setup file logging
    filename = __file__.split('/')[-1]
    LOG_FILE_NAME = os.path.splitext(
        filename)[0] + '_' + time.strftime('%Y-%m-%d') + '.log'

    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

    LOG_FILE = LOG_FOLDER + LOG_FILE_NAME
    fh = logging.FileHandler(LOG_FILE, mode='w')
    fh.setLevel(FILE_LOG_LEVEL)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def import_layers(path, superuser):
    # Execute importlayers

    path = str(path)
    IMPORTLAYERS_LOG_FILE_NAME = 'importlayers_' + \
        time.strftime('%Y-%m-%d') + '.log'

    IMPORTLAYERS_LOG_FILE = LOG_FOLDER + IMPORTLAYERS_LOG_FILE_NAME

    importlayers_cmd = '/usr/bin/env python2 -u ../../manage.py importlayers -v 3 -u ' + superuser + ' '

    command = importlayers_cmd + path  # + log_cmd
    logger.info('Command: %s', command)

    try:

        logger.info('Execute command ...')
        output = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        output.wait()
        out, err = output.communicate()

        logger.info('Finished. Below is output of importlayers ')
        logger.info('Popen OUT %s', out)
        logger.info('Popen ERR %s', err)
        # print 'Finished. Below is output of Popen'
        # print text

    except Exception:

        print 'Exception occurred'
        logger.exception('Exception occurred')

    return out


def exists_in_geonode(style_name):
    try:
        style = Style.objects.get(name=style_name)
        logger.info('Style found in GeoNode.')
        return True
    except Exception:
        logger.exception('Style does not exist')
    return False


def exists_in_geoserver(style_name):

    style = cat.get_style(style_name)

    if style is not None:
        logger.info('Style found in GeoServer.')
        return True
    return False


def style_exists(style_name):

    if exists_in_geonode(style_name) and exists_in_geoserver(style_name):
        return True
    return False


def create_style(style, name):
    """Creates style in geonode and geoserver."""

    sld_url = (settings.OGC_SERVER['default'][
               'LOCATION'] + 'rest/styles/' + style).lower()

    #: Geoserver style object
    with open(style) as f:
        logger.info('Creating style in GeoServer... ')
        cat.create_style(name, f.read())

    #: Geonode style object
    try:
        created_style = cat.get_style(name)

        if created_style is not None:
            Style.objects.create(name=created_style.sld_name,
                                 sld_title=created_style.sld_title,
                                 sld_body=created_style.sld_body,
                                 sld_url=sld_url)
    except Exception:
        logger.exception('Error in creating Style!')
        return False

    return True


def own_thumbnail(layer):
    print 'USER', getpass.getuser()
    print layer.name, ': Setting thumbnail permissions...'
    thumbnail_str = 'layer-' + str(layer.uuid) + '-thumb.png'
    thumb_url = '/var/www/geonode/uploaded/thumbs/' + thumbnail_str
    subprocess.call(['sudo', '/bin/chown', 'www-data:www-data', thumb_url])
    subprocess.call(['sudo', '/bin/chmod', '666', thumb_url])


def update_style(layer, style_template):
    # Get equivalent geoserver layer
    gs_layer = cat.get_layer(layer.name)
    logger.info('%s: gs_layer: %s', layer.name, gs_layer.name)
    # print layer.name, ': gs_layer:', gs_layer.name

    # Get current style
    # pprint(dir(gs_layer))
    cur_def_gs_style = gs_layer._get_default_style()
    # pprint(dir(cur_def_gs_style))
    if cur_def_gs_style is not None:
        logger.info('%s: cur_def_gs_style.name: %s', layer.name, cur_def_gs_style.name)
        # print layer.name, ': cur_def_gs_style.name:', cur_def_gs_style.name

    # Get proper style
    gs_style = None
    gs_style = cat.get_style(style_template)

    # has_layer_changes = False
    try:
        if gs_style is not None:
            print layer.name, ': gs_style.name:', gs_style.name

            if cur_def_gs_style and cur_def_gs_style.name != gs_style.name:

                logger.info('%s: Setting default, style...', layer.name)
                # print layer.name, ': Setting default style...'
                gs_layer._set_default_style(gs_style)
                cat.save(gs_layer)

                logger.info('%s: Deleting old default style from geoserver...', layer.name)
                print layer.name, ': Deleting old default style from geoserver...'
                cat.delete(cur_def_gs_style)

                logger.info('%s: Deleting old default style from geonode...', layer.name)
                # print layer.name, ': Deleting old default style from geonode...'
                gn_style = Style.objects.get(name=layer.name)
                gn_style.delete()
    except Exception as e:
        logger.exception("Error setting style")



def update_text_content(layer):
    #: Updates purpose and topic category

    layer_title = layer.name.replace('_', ' ').title()

    if layer.title != layer_title:
        layer.title = layer_title
        layer.save()
        logger.info('Updated %s Title: %s', layer.name, layer.title)

    layer_purpose = """Integrated Agricultural and Coastal Land Cover Maps are needed by Government Agencies and Local Government Units for planning and decision making. This complements on-going programs of the Department of Agriculture by utilizing LiDAR data for the mapping of resources and vulnerability assessment."""
    if layer.purpose != layer_purpose:
        layer.purpose = layer_purpose
        logger.info('Updated Purpose %s', layer.name)

    if layer.category != TopicCategory.objects.get(identifier="imageryBaseMapsEarthCover"):
        layer.category = TopicCategory.objects.get(
            identifier="imageryBaseMapsEarthCover")
        logger.info('Updated Category %s', layer.name)

    layer.save()

def update_metadata(style_template, day_counter):

    last_day = datetime.now() - timedelta(days=int(day_counter))
    layers = Layer.objects.filter(upload_session__date__gte=last_day)

    logger.info('%s Layers', len(layers))

    for layer in layers:
        update_style(layer, style_template)

    for layer in layers:
        update_text_content(layer)


def parse_arguments():

    parser = argparse.ArgumentParser(description="""Stand alone script for migrating data. Does the following:
        1. Uploads layers from <path> via importlayers command.
        2. Checks if <style> exists in GeoNode and GeoServer. If not, this script creates the style object for GeoNode and GeoServer.
        3. Updates layer styles by applying <style>.""")

    parser.add_argument(
        '--superuser', help="""GeoNode superuser""", required=True)
    parser.add_argument(
        '--path', help="""Complete directory path of dataset to be imported.
            e.g. /mnt/pl2-storage_pool/CoastMap/SUC_UPLOADS/UPLB/PALAWAN/""",
        required=True)
    parser.add_argument(
        '--style', help="""Full name of SLD to be used. Must be in the same folder as this script.
            e.g. coastmap.sld """, required=True)
    parser.add_argument(
        '--daycount', help="""Update layers uploaded within X days""", required=True)
    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = parse_arguments()
    superuser = args.superuser
    path = args.path
    style = args.style
    day_counter = args.daycount

    setup_logging()
    logger.info('Importing Layers ... ')
    import_msg = import_layers(path, superuser)
    logger.info('Finished importing layers.')

    style_created = True
    name = style.split('.sld')[0]

    if import_msg != '':
        logger.info('SET STYLE')
        if not style_exists(name):
            style_created = create_style(style, name)

        if style_created:
            update_metadata(name, day_counter)

    logger.info('Finished script')
