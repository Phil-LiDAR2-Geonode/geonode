#!/usr/bin/env python
from geonode.settings import GEONODE_APPS
import geonode.settings as settings

import logging
import os
from os.path import dirname, abspath
import time
import getpass
import subprocess
from geoserver.catalog import Catalog
from geonode.layers.models import Style, Layer
from datetime import datetime, timedelta
import argparse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")

logger = logging.getLogger()
LOG_LEVEL = logging.INFO
FILE_LOG_LEVEL = logging.INFO
LOG_FOLDER = dirname(abspath(__file__)) + '/logs/'


cat = Catalog(settings.OGC_SERVER['default']['LOCATION'] + 'rest',
              username=settings.OGC_SERVER['default']['USER'],
              password=settings.OGC_SERVER['default']['PASSWORD'])


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


def own_thumbnail(layer, thumbnail_url):
    logger.info('Updating thumbnail.')

    print 'USER', getpass.getuser()
    logger.info('USER %s', getpass.getuser())

    print layer.name, ': Setting thumbnail permissions...'
    logger.info('%s: Setting thumbnail permissions...', layer.name)

    thumbnail_str = 'layer-' + str(layer.uuid) + '-thumb.png'
    thumb_url = thumbnail_url + thumbnail_str
    subprocess.call(['sudo', '/bin/chown', 'geonode:apache', thumb_url])
    subprocess.call(['sudo', '/bin/chmod', '666', thumb_url])

    layer.save()


def update_style(layer, style_template):
    logger.info('Updating style.')

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


def parse_arguments():

    parser = argparse.ArgumentParser(description="""1. Updates layer styles by applying <style>.
        2. Updates thumbnails and stores thumbs on provided local thumbnail url.""")

    parser.add_argument(
        '--style', help="""Full name of SLD to be used. Must be in the same folder as this script.
            e.g. coastmap.sld """, required=True)
    parser.add_argument(
        '--daycount', help="""Update layers uploaded within X days""", required=True)
    parser.add_argument(
        '--thumbnail_url', help="""Thumbnail url of thumbnail images eg
        /home/geonode/geonode/geonode/uploaded/thumbs/""", required=True)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_arguments()
    style = args.style
    day_counter = args.daycount
    thumbnail_url = args.thumbnail_url

    setup_logging()

    last_day = datetime.now() - timedelta(days=int(day_counter))
    layers = Layer.objects.filter(upload_session__date__gte=last_day)

    style_created = True
    name = style.split('.sld')[0]

    if not style_exists(name):
        style_created = create_style(style, name)

    if style_created:
        for layer in layers:
            update_style(layer, name)
            own_thumbnail(layer, thumbnail_url)
