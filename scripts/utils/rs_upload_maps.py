# -*- coding: utf-8 -*-
#!/usr/bin/python
# Geonode

__version__ = "0.1.0"

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
from django.contrib.auth.models import Group
from geonode.people.models import Profile
from geonode.settings import GEONODE_APPS
import geonode.settings as settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from geonode.documents.models import Document
from geonode.base.models import ResourceBase
from guardian.shortcuts import assign_perm, get_anonymous_user
import psycopg2
import psycopg2.extras
from geonode.base.models import TopicCategory

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

input_directory = "/home/geonode/geonode/DATA/RS_MAPS/VI/"

def upload_map(map_obj):
	keyword_list = []

	year = map_obj.split("_")[1].replace(".png","")

	# get scale
	if "tci" in map_obj:
		index = "Temperature Condition Index"
		index_abbr = "TCI"
	elif "vci" in map_obj:
		index = "Vegetation Condition Index"
		index_abbr = "VCI"

	elif "vhi" in map_obj:
		index = "Vegetation Health Index"
		index_abbr = "VHI"
	else:
		index = None

	# Add keywords
	keyword_list.append("PARMap")
	keyword_list.append("Agriculture")
	keyword_list.append(index_abbr)
	keyword_list.append("Vegetation Index")
	keyword_list.append("Drought")
	keyword_list.append("Phil-LiDAR 2")
	keyword_list.append("University of the Philippines Diliman")

	map_title = "{0} {1}".format(year, index)

	print map_obj, ": map title:", map_title

	map_abstract = """Maps prepared and reviewed by the University of the Philippines Training Center for Applied Geodesy and Photogrammetry (Phil-LiDAR 2 Program A Project 1). The use of the datasets provided herewith are covered by End Users License Agreement (EULA). Maps include vegetation index maps of Agricultural Resources.

Major Source of Information: MODIS data (MOD13A3 and MOD11B3); 2010 land cover maps from the Department of Environment and Natural Resources-National Mapping and Resources Information Authority; field-acquired data points

Accuracy and Limitations: The accuracy of the delivered products/outputs are dependent on the source datasets, software limitations, algorithms, and procedures used. The products are provided "as is" without warranty of any kind, expressed, or implied. Phil-LiDAR 2 Program does not warrant that the products will meet the needs or expectations of the end users, or that the operations or use of the products will be error-free."""

	print map_obj, ': map abstract:', map_abstract

	map_purpose = "The time-series datasets of satellite-derived vegetation indices can be used for monitoring the development of dry spells and drought."

	print map_obj, ': map purpose:', map_purpose

	map_category = TopicCategory.objects.get(
		identifier="imageryBaseMapsEarthCover")

	t = open(input_directory + map_obj, 'r')
	f = SimpleUploadedFile(map_obj, t.read(), 'application/png')
	superuser = Profile.objects.get(id=1)
	c = Document.objects.create(
	doc_file=f,
	owner=superuser,
	title=map_title,
	abstract=map_abstract,
	purpose=map_purpose,
	category=map_category)

	for keyword in (keyword_list):
		print map_obj, ': map keyword:', keyword
		c.keywords.add(keyword)

	print c, ': Updating map permissions...'
	anon_group = Group.objects.get(name='anonymous')
	assign_perm('view_resourcebase', anon_group, c.get_self_resource())
	assign_perm('view_resourcebase', get_anonymous_user(),
				c.get_self_resource())
	assign_perm('download_resourcebase', anon_group, c.get_self_resource())
	assign_perm('download_resourcebase', get_anonymous_user(),
				c.get_self_resource())

if __name__ == "__main__":
	path, dirs, files = os.walk(input_directory).next()
	file_count = len(files)
	print "Total number of maps: ", file_count
	ctr = 0

	for map_obj in sorted(os.listdir(input_directory)):
		ctr += 1
		print '#' * 40

		print "Uploading ", str(ctr), " of ", file_count, ":", map_obj
		upload_map(map_obj)

	print "Finished"
