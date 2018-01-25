#!/usr/bin/python

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

input_directory = "/home/geonode/geonode/DATA/VA_MAPS_PNG/"

def connect_db():
	conn = psycopg2.connect(("host={0} dbname={1} user={2} password={3}".format
							 (settings.DATABASE_HOST,
							  settings.DATABASES[
								  'datastore']['NAME'],
							  settings.DATABASE_USER,
							  settings.DATABASE_PASSWORD)))

	cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

	return conn, cur

def close_db(conn, cur):
	cur.close()
	conn.close()

def select_by_muncode(cur, muncode):

	# Construct query
	cur.execute('''
SELECT city_munic, province,
	   muncode, suc_hei
FROM muni_metadata
WHERE muncode = %s''', (muncode,))

	# Return results
	return cur.fetchall()

def upload_map(map_obj):
	keyword_list = []

	# get scale
	if "local" in map_obj:
		scale = "Local"
		muncode = map_obj.split("_")[2]
		conn, cur = connect_db()
		results = select_by_muncode(cur, muncode)
		muni = results[0]['city_munic'].title().replace(u'\xf1',"n")
		prov = results[0]['province'].title()
		suc_hei = results[0]['suc_hei'].replace(u'\xf1',"n")
		keyword_list.append(muni)
		keyword_list.append(prov)
		keyword_list.append(suc_hei)
		keyword_list.append(muncode)
	else:
		scale = "National"
		keyword_list.append("University of the Philippines Diliman")

	# get hazard
	if "flood" in map_obj:
		hazard = "Flood"
	elif "drought" in map_obj:
		hazard = "Drought"
	else:
		hazard = "Seawater Intrusion"

	# get component
	if "adaptivecapacity" in map_obj:
		component = "Adaptive Capacity"
		style_sld = "adaptivecapacity_va"
	elif "exposure" in map_obj:
		component = "Exposure"
		style_sld = "exposure_va"
	elif "sensitivity" in map_obj:
		component = "Sensitivity"
		style_sld = "sensitivity_va"
	else:
		component = "Vulnerability"
		style_sld = "va"

	# get aggregation method
	if "am" in map_obj:
		agg_method = "(Arithmetic Mean)"
	elif  "gm" in map_obj:
		agg_method = "(Geometric Mean)"
	elif "med" in map_obj:
		agg_method = "(Median)"
	else:
		agg_method = None

	if scale == "National":
		if agg_method:
			map_title = "{0} {1} Map of the Philippines {2}".format(hazard, component, agg_method)
		else:
			map_title = "{0} {1} Map of the Philippines".format(hazard, component)
	else:
		if agg_method:
			map_title = "{0} {1} Map of {2}, {3} {4}".format(hazard, component, muni, prov, agg_method)
		else:
			map_title = "{0} {1} Map of {2}, {3}".format(hazard, component, muni, prov)

	print map_obj, ': map title:', map_title

	if scale == "National":
		map_abstract = """Maps prepared by University of the Philippines Training Center for Applied Geodesy and Photogrammetry (Phil-LiDAR 2 Program A Project 1). The use of the datasets provided herewith are covered by End Users License Agreement (EULA). Maps include {0} National Level Exposure, Sensitivity, Adaptive Capacity and Vulnerabiliy Maps of Agricultural Resources.

Notice: The assessment covers physical, agro-ecological, and socio-economic indicators relevant for composite index measuring degree of vulnerability.

Major Source of Information: LiDAR Datasets from DREAM/Phil-LiDAR 1 Program with validation from participatory methods such as focus group discussions (FGDs) and key informant interviews (KIIs)

Accuracy and Limitations: The accuracy of the delivered products/outputs are dependent on the source datasets, software limitations, algorithms, and procedures used. The products are provided "as is" without warranty of any kind, expressed, or implied. Phil-LiDAR 2 Program does not warrant that the products will meet the needs or expectations of the end users, or that the operations or use of the products will be error-free.""".format(hazard)

	else:
		if suc_hei == "University of the Philippines Diliman":
			map_abstract = """Maps prepared by University of the Philippines Training Center for Applied Geodesy and Photogrammetry (Phil-LiDAR 2 Program A Project 1). The use of the datasets provided herewith are covered by End Users License Agreement (EULA). Maps include {0} Municipal Level Exposure, Sensitivity, Adaptive Capacity and Vulnerabiliy Maps of Agricultural Resources.

Notice: The assessment covers physical, agro-ecological, and socio-economic indicators relevant for composite index measuring degree of vulnerability.

Major Source of Information: LiDAR Datasets from DREAM/Phil-LiDAR 1 Program with validation from participatory methods such as focus group discussions (FGDs) and key informant interviews (KIIs)

Accuracy and Limitations: The accuracy of the delivered products/outputs are dependent on the source datasets, software limitations, algorithms, and procedures used. The products are provided "as is" without warranty of any kind, expressed, or implied. Phil-LiDAR 2 Program does not warrant that the products will meet the needs or expectations of the end users, or that the operations or use of the products will be error-free.""".format(hazard)

		else:
			map_abstract = """Maps prepared by {0} (Phil-LiDAR 2 Program B) and reviewed by the University of the Philippines Training Center for Applied Geodesy and Photogrammetry (Phil-LiDAR 2 Program A Project 1). The use of the datasets provided herewith are covered by End Users License Agreement (EULA). Maps include {1} Municipal Level Exposure, Sensitivity, Adaptive Capacity and Vulnerabiliy Maps of Agricultural Resources.

Notice: The assessment covers physical, agro-ecological, and socio-economic indicators relevant for composite index measuring degree of vulnerability.

Major Source of Information: LiDAR Datasets from DREAM/Phil-LiDAR 1 Program with validation from participatory methods such as focus group discussions (FGDs) and key informant interviews (KIIs)

Accuracy and Limitations: The accuracy of the delivered products/outputs are dependent on the source datasets, software limitations, algorithms, and procedures used. The products are provided "as is" without warranty of any kind, expressed, or implied. Phil-LiDAR 2 Program does not warrant that the products will meet the needs or expectations of the end users, or that the operations or use of the products will be error-free.""".format(suc_hei, hazard)

	print map_obj, ': map abstract:', map_abstract

	map_purpose = "Vulnerability assessment maps are effective planning and decision-making tools for government agencies and local government units to increase resililence to specific hazards. It also complements ongoing programs of the Department of Agriculture on mapping of agricultural resources and assessing vulnerability."

	print map_obj, ': map purpose:', map_purpose

	keyword_list.append(scale)
	keyword_list.append(hazard)
	keyword_list.append("Agriculture")
	keyword_list.append("Vulnerability")
	keyword_list.append("VA")
	keyword_list.append("Phil-LiDAR 2")
	keyword_list.append("PARMap")

	map_category = TopicCategory.objects.get(
		identifier="environment")

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
