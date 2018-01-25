# -*- coding: utf-8 -*-
#!/usr/bin/python
# Geonode

__version__ = "0.4.1"

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

if __name__ == "__main__":
	input_directory = "/home/geonode/geonode/DATA/LULC_MAPS/"
	path, dirs, files = os.walk(input_directory).next()
	file_count = len(files)
	print "Total number of maps: ", file_count
	ctr = 1

	for map_obj in os.listdir(input_directory):

		print '#' * 40

		print "Uploading ", str(ctr), " of ", file_count, ":", map_obj

		try:
			resource_type = map_obj.split("_")[0]
			muncode = map_obj.split("_")[1]

			conn, cur = connect_db()
			results = select_by_muncode(cur, muncode)

			keyword_list = []
			muni = results[0]['city_munic'].title().replace(u'\xf1',"n")
			prov = results[0]['province'].title()
			suc_hei = results[0]['suc_hei'].replace(u'\xf1',"n")

			if resource_type == "agricoast":
				map_title = "{0}, {1} Agricultural and Coastal Landcover Map".format(muni, prov)
				resource_desc = "Agricultural Resources integrated with Coastal Resources"
				map_purpose = "Integrated Agricultural and Coastal Land Cover Maps are effective planning and decision-making tools for government agencies and local government units. It also complements ongoing programs of the Department of Agriculture on mapping of agricultural resources and assessing vulnerability."
				keyword_list.extend(["PARMap", "Agriculture", "CoastMap", "Mangrove", "Aquaculture",
									  "Landcover", "Phil-LiDAR 2", "LULC"])
			else:
				map_title = "{0}, {1} Agricultural Landcover Map".format(muni, prov)
				resource_desc = "Agricultural Resources"
				map_purpose = "Detailed Agricultural Land Cover Maps are effective planning and decision-making tools for government agencies and local government units. It also complements ongoing programs of the Department of Agriculture on mapping of agricultural resources and assessing vulnerability."
				keyword_list.extend(
					["PARMap", "Agriculture", "Landcover", "Phil-LiDAR 2", "LULC"])
			print map_obj, ": map title:", map_title

			if suc_hei == "University of the Philippines Diliman":
				map_abstract = """Maps prepared by University of the Philippines Training Center for Applied Geodesy and Photogrammetry (Phil-LiDAR 2 Program A Project 1). The use of the datasets provided herewith are covered by End Users License Agreement (EULA). Maps include initial Land Cover Map of {0}.

Notice: Datasets subject to updating. Maps show land cover on date of data acquisition and may not reflect present land cover.

Major Source of Information: LiDAR Datasets from DREAM/Phil-LiDAR 1 Program

Accuracy and Limitations: The accuracy of the delivered products/outputs are dependent on the source datasets, software limitations, algorithms, and procedures used. The products are provided "as is" without warranty of any kind, expressed, or implied. Phil-LiDAR 2 Program does not warrant that the products will meet the needs or expectations of the end users, or that the operations or use of the products will be error-free.""".format(resource_desc)
			else:
				map_abstract = """Maps prepared by {0} (Phil-LiDAR 2 Program B) and reviewed by the University of the Philippines Training Center for Applied Geodesy and Photogrammetry (Phil-LiDAR 2 Program A Project 1). The use of the datasets provided herewith are covered by End Users License Agreement (EULA). Maps include initial Land Cover Map of {1}.

Notice: Datasets subject to updating. Maps show land cover on date of data acquisition and may not reflect present land cover.

Major Source of Information: LiDAR Datasets from DREAM/Phil-LiDAR 1 Program

Accuracy and Limitations: The accuracy of the delivered products/outputs are dependent on the source datasets, software limitations, algorithms, and procedures used. The products are provided "as is" without warranty of any kind, expressed, or implied. Phil-LiDAR 2 Program does not warrant that the products will meet the needs or expectations of the end users, or that the operations or use of the products will be error-free.""".format(suc_hei, resource_desc)

			print map_obj, ": map abstract:", map_abstract
			print map_obj, ": map purpose:", map_purpose

			keyword_list.append(muni)
			keyword_list.append(prov)
			keyword_list.append(suc_hei)
			keyword_list.append(muncode)

			map_category = TopicCategory.objects.get(
				identifier="imageryBaseMapsEarthCover")

			t = open(input_directory + map_obj, 'r')
			f = SimpleUploadedFile(map_obj, t.read(), 'application/jpeg')
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
			ctr+=1
		except Exception:
			print "ERROR in", map_obj
	print "Finished"
