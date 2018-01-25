#!/usr/bin/env python2

__version__ = "0.1"

# Setup GeoNode environment
import os
import sys
from pprint import pprint
from os.path import abspath, dirname, join
PROJECT_ROOT = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(join(PROJECT_ROOT, 'geonode'))
sys.path.append(PROJECT_ROOT)

from geonode.settings import GEONODE_APPS
import geonode.settings as settings

from datetime import datetime, timedelta
from django.contrib.auth.models import Group
from django.db.models import Q
from geonode.base.models import TopicCategory
from geonode.layers.models import Layer, Style
from geoserver.catalog import Catalog
from guardian.shortcuts import assign_perm, get_anonymous_user, get_perms
from pprint import pprint
from threading import Thread
import multiprocessing
import subprocess
import traceback
import psycopg2
import psycopg2.extras
import calendar
from geonode.people.models import Profile


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")

def update_thumb_perms(layer):

	print layer.name, ': Setting thumbnail permissions...'
	thumbnail_str = 'layer-' + str(layer.uuid) + '-thumb.png'
	thumb_url = '/home/geonode/geonode/geonode/uploaded/thumbs/' + thumbnail_str
	subprocess.call(['sudo', '/bin/chown', 'apache:apache', thumb_url])
	subprocess.call(['sudo', '/bin/chmod', '666', thumb_url])

def update_layer_perms(layer):
	try:
		print layer.name, ': Updating layer permissions...'
		anon_group = Group.objects.get(name='anonymous')
		assign_perm('view_resourcebase', anon_group, layer.get_self_resource())
		assign_perm('view_resourcebase', get_anonymous_user(),
					layer.get_self_resource())
		assign_perm('download_resourcebase', anon_group, layer.get_self_resource())
		assign_perm('download_resourcebase', get_anonymous_user(),
					layer.get_self_resource())

	except Exception:
		print layer.name, ': Error updating layer permissions!'
		traceback.print_exc()
		# raise


def update_rs(layer):
	print layer.name, ': layer name:', layer.name
	keywords_list = []

	if "tci" in layer.name:
		index = "Temperature Condition Index"
		index_abbr = "TCI"
	elif "vci" in layer.name:
		index = "Vegetation Condition Index"
		index_abbr = "VCI"

	elif "vhi" in layer.name:
		index = "Vegetation Health Index"
		index_abbr = "VHI"
	else:
		index = None

	year = layer.name.split("_")[1]
	month = int(layer.name.split("_")[2])

	layer_title = "{0} {1} {2}".format(calendar.month_name[month], year, index)

	print layer.name, ': layer title:', layer_title

	# Add keywords
	keywords_list.append("PARMap")
	keywords_list.append("Agriculture")
	keywords_list.append(index_abbr)
	keywords_list.append("Vegetation Index")
	keywords_list.append("Drought")
	keywords_list.append("Phil-LiDAR 2")
	keywords_list.append("University of the Philippines Diliman")

	layer_abstract = """Maps prepared and reviewed by the University of the Philippines Training Center for Applied Geodesy and Photogrammetry (Phil-LiDAR 2 Program A Project 1). The use of the datasets provided herewith are covered by End Users License Agreement (EULA). Maps include vegetation index maps of Agricultural Resources.

Major Source of Information: MODIS data (MOD13A3 and MOD11B3); 2010 land cover maps from the Department of Environment and Natural Resources-National Mapping and Resources Information Authority; field-acquired data points

Accuracy and Limitations: The accuracy of the delivered products/outputs are dependent on the source datasets, software limitations, algorithms, and procedures used. The products are provided "as is" without warranty of any kind, expressed, or implied. Phil-LiDAR 2 Program does not warrant that the products will meet the needs or expectations of the end users, or that the operations or use of the products will be error-free."""

	print layer.name, ': layer abstract:', layer_abstract

	layer_purpose = "The time-series datasets of satellite-derived vegetation indices can be used for monitoring the development of dry spells and drought."

	print layer.name, ': layer purpose:', layer_purpose

	# Check if there are changes
	has_layer_changes = False
	if layer.title != layer_title:
		print layer.name, ': Setting layer.title...'
		has_layer_changes = True
		layer.title = layer_title
	if layer.abstract != layer_abstract:
		print layer.name, ': Setting layer.abstract...'
		has_layer_changes = True
		layer.abstract = layer_abstract
	if layer.purpose != layer_purpose:
		print layer.name, ': Setting layer.purpose...'
		has_layer_changes = True
		layer.purpose = layer_purpose

	layer.keywords.clear()
	for keyword in keywords_list:
		print layer.name, ': layer_keyword:', keyword
		print layer.name, ': Adding keyword...'
		layer.keywords.add(keyword)
		has_layer_changes = True

	if layer.category != TopicCategory.objects.get(identifier="imageryBaseMapsEarthCover"):
		print layer.name, ': Setting layer.category...'
		has_layer_changes = True
		layer.category = TopicCategory.objects.get(
			identifier="imageryBaseMapsEarthCover")

	# Update style
	# update_style(layer, style_sld)

	# Update thumbnail permissions
	update_thumb_perms(layer)

	# Update layer permissions
	update_layer_perms(layer)

	return has_layer_changes
def update_metadata(layer):

	try:
		has_layer_changes = False
		has_layer_changes = update_rs(layer)

		# Save layer if there are changes
		if has_layer_changes:
			print layer.name, ': Saving layer...'
			layer.save()
			seed_layers(layer)
		else:
			print layer.name, ': No changes to layer. Skipping...'

	except Exception:
		print layer.name, ': Error updating metadata!'
		traceback.print_exc()

	return has_layer_changes

def seed_layers(layer):
	try:
			out = subprocess.check_output(['/home/geonode/geonode/' + '/gwc.sh', 'seed',
																		 '{0}:{1}'.format(
																				 layer.workspace, layer.name), 'EPSG:900913', '-v', '-a',
																		 settings.OGC_SERVER['default']['USER'] + ':' +
																		 settings.OGC_SERVER['default'][
																				 'PASSWORD'], '-u',
																		 settings.OGC_SERVER['default']['LOCATION'] + 'gwc/rest'],
																		stderr=subprocess.STDOUT)
			print out
	except subprocess.CalledProcessError as e:
			print 'Error seeding layer:', layer
			print 'e.returncode:', e.returncode
			print 'e.cmd:', e.cmd
			print 'e.output:', e.output

if __name__ == "__main__":

	layers = Layer.objects.filter(title__icontains='tci')

	total = len(layers)
	print 'Updating', total, 'layers!'

	# Update metadata
	counter = 0
	start_time = datetime.now()
	for layer in layers:
		print '#' * 40

		update_metadata(layer)

		counter += 1
		duration = datetime.now() - start_time
		total_time = duration.total_seconds() * total / float(counter)
		print counter, '/', total, 'ETA:', start_time + timedelta(seconds=total_time)
