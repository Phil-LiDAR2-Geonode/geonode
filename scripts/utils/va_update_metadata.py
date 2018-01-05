#!/usr/bin/env python2

__version__ = "0.1.1"

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
from guardian.shortcuts import assign_perm, get_anonymous_user
from pprint import pprint
from threading import Thread
import multiprocessing
import subprocess
import traceback
import psycopg2
import psycopg2.extras

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")


def update_style(layer, style_template):

	# Get geoserver catalog
	cat = Catalog(settings.OGC_SERVER['default']['LOCATION'] + 'rest',
				  username=settings.OGC_SERVER['default']['USER'],
				  password=settings.OGC_SERVER['default']['PASSWORD'])

	# Get equivalent geoserver layer
	gs_layer = cat.get_layer(layer.name)
	print layer.name, ': gs_layer:', gs_layer.name

	# Get current style

	cur_def_gs_style = gs_layer._get_default_style()

	if cur_def_gs_style is not None:
		print layer.name, ': cur_def_gs_style.name:', cur_def_gs_style.name

	gs_style = cat.get_style(style_template)

	try:
		if gs_style is not None:
			print layer.name, ': gs_style.name:', gs_style.name

			if cur_def_gs_style and cur_def_gs_style.name != gs_style.name:

				print layer.name, ': Setting default style...'
				gs_layer._set_default_style(gs_style)
				cat.save(gs_layer)

				# print layer.name, ': Deleting old default style from geoserver...'
				# cat.delete(cur_def_gs_style)
				#
				# print layer.name, ': Deleting old default style from geonode...'
				# gn_style = Style.objects.get(name=layer.name)
				# gn_style.delete()

	except Exception:
		print layer.name, ': Error setting style!'
		traceback.print_exc()
		raise


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

	except Exception:
		print layer.name, ': Error updating layer permissions!'
		traceback.print_exc()
		# raise


def update_va(layer):
	print layer.name, ': layer name:', layer.name
	keywords_list = []
	muni = "Kalibo (Capital)"
	prov = "Aklan"
	# get scale
	if "local" in layer.name:
		scale = "Local"
	else:
		scale = "National"

	# get hazard
	if "flood" in layer.name:
		hazard = "Flood"
	elif "drought" in layer.name:
		hazard = "Drought"
	else:
		hazard = "Seawater Intrusion"

	# get component
	if "adaptivecapacity" in layer.name:
		component = "Adaptive Capacity"
		style_sld = "adaptivecapacity_va"
	elif "exposure" in layer.name:
		component = "Exposure"
		style_sld = "exposure_va"
	elif "sensitivity" in layer.name:
		component = "Sensitivity"
		style_sld = "sensitivity_va"
	else:
		component = "Vulnerability"
		style_sld = "va"

	# get aggregation method
	if "am" in layer.name:
		agg_method = "(Arithmetic Mean)"
	elif  "gm" in layer.name:
		agg_method = "(Geometric Mean)"
	elif "med" in layer.name:
		agg_method = "(Median)"
	else:
		agg_method = None

	# Add city/muni, muncode, province and suc to keywords
	keywords_list.append(scale)
	keywords_list.append(hazard)
	keywords_list.append(muni)
	keywords_list.append(prov)
	keywords_list.append("Agriculture")
	keywords_list.append("Vulnerability")
	keywords_list.append("VA")
	keywords_list.append("Phil-LiDAR 2")
	keywords_list.append("PARMap")
	keywords_list.append("University of the Philippines Diliman")

	if scale == "National":
		if agg_method:
			layer_title = "{0} {1} Map of the Philippines {2}".format(hazard, component, agg_method)
		else:
			layer_title = "{0} {1} Map of the Philippines".format(hazard, component)
	else:
		if agg_method:
			layer_title = "{0} {1} Map of {2}, {3} {4}".format(hazard, component, muni, prov, agg_method)
		else:
			layer_title = "{0} {1} Map of {2}, {3}".format(hazard, component, muni, prov)

	print layer.name, ': layer title:', layer_title

	if scale == "National":
		layer_abstract = """Maps prepared by University of the Philippines Training Center for Applied Geodesy and Photogrammetry (Phil-LiDAR 2 Program A Project 1). The use of the datasets provided herewith are covered by End Users License Agreement (EULA). Shapefiles include {0} National Level Exposure, Sensitivity, Adaptive Capacity and Vulnerabiliy Maps of Agricultural Resources.

Notice: The assessment covers physical, agro-ecological, and socio-economic indicators relevant for composite index measuring degree of vulnerability.

Major Source of Information: LiDAR Datasets from DREAM/Phil-LiDAR 1 Program with validation from participatory methods such as focus group discussions (FGDs) and key informant interviews (KIIs).

Accuracy and Limitations: The accuracy of the delivered products/outputs are dependent on the source datasets, software limitations, algorithms, and procedures used. The products are provided "as is" without warranty of any kind, expressed, or implied. Phil-LiDAR 2 Program does not warrant that the products will meet the needs or expectations of the end users, or that the operations or use of the products will be error-free.""".format(hazard)

	else:
		layer_abstract = """Maps prepared by University of the Philippines Training Center for Applied Geodesy and Photogrammetry (Phil-LiDAR 2 Program A Project 1). The use of the datasets provided herewith are covered by End Users License Agreement (EULA). Shapefiles include {0} Municipal Level Exposure, Sensitivity, Adaptive Capacity and Vulnerabiliy Maps of Agricultural Resources.

Notice: The assessment covers physical, agro-ecological, and socio-economic indicators relevant for composite index measuring degree of vulnerability.

Major Source of Information: LiDAR Datasets from DREAM/Phil-LiDAR 1 Program with validation from participatory methods such as focus group discussions (FGDs) and key informant interviews (KIIs).

Accuracy and Limitations: The accuracy of the delivered products/outputs are dependent on the source datasets, software limitations, algorithms, and procedures used. The products are provided "as is" without warranty of any kind, expressed, or implied. Phil-LiDAR 2 Program does not warrant that the products will meet the needs or expectations of the end users, or that the operations or use of the products will be error-free.""".format(hazard)

	print layer.name, ': layer abstract:', layer_abstract

	layer_purpose = "Vulnerability assessment maps are effective planning and decision-making tools for government agencies and local government units to increase resililence to specific hazards. It also complements ongoing programs of the Department of Agriculture on mapping of agricultural resources and assessing vulnerability."

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

	if layer.category != TopicCategory.objects.get(identifier="environment"):
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
		has_layer_changes = update_va(layer)

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

	layers = Layer.objects.filter(title__icontains='_va')

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
