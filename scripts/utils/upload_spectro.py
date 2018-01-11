# encoding=utf8
import sys
import xlrd
import os
import traceback
from datetime import datetime
from datetime import time
import geonode.settings as settings
from os.path import abspath, dirname, join
PROJECT_ROOT = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(join(PROJECT_ROOT, 'geonode'))
sys.path.append(PROJECT_ROOT)
from geonode.settings import GEONODE_APPS
from django.db.models import Q
from spectral_library.models import Target, Queue
from django.conf import settings
from xlrd import open_workbook


def read_excel(excel_file):
	# open excel file
	uploaded_dir = "/home/admin/geonode/geonode/uploaded/"
	target_name = os.path.basename(excel_file).replace("metadata_ss.xlsx","ss")
	book = open_workbook(excel_file,on_demand=True)
	sheet = book.sheet_by_index(0)

	site_id = sheet.row(1)[2].value.strip()

	try:
		date_acquired = str(datetime(*xlrd.xldate_as_tuple(sheet.row(2)[2].value, book.datemode)).strftime("%Y-%m-%d"))
	except:
		date_acquired = str(datetime.strptime(sheet.row(2)[2].value, '%m/%d/%Y').strftime("%Y-%m-%d"))

	purpose = sheet.row(3)[2].value.strip()
	observer = sheet.row(4)[2].value.strip()

	try:
		time_acquired = str(sheet.row(5)[2].value.strip()).replace(' AM','') + ":00"
	except:
		time_acquired = str(xlrd.xldate.xldate_as_datetime(sheet.row(5)[2].value, book.datemode)).split()[1]

	try:
		waypoint = sheet.row(6)[2].value.strip()
	except:
		waypoint = str(sheet.row(6)[2].value)

	try:
		latitude = sheet.row(7)[2].value.strip()
	except:
		latitude = str(sheet.row(7)[2].value)

	try:
		longitude = sheet.row(8)[2].value.strip()
	except:
		longitude = str(sheet.row(8)[2].value)

	try:
		altitude = sheet.row(9)[2].value.strip()
	except:
		altitude = str(sheet.row(9)[2].value)

	gps_unit = sheet.row(10)[2].value.strip()
	province = sheet.row(11)[2].value.strip().title()
	city_municipality = sheet.row(12)[2].value.strip().title()
	barangay = sheet.row(13)[2].value.strip().title()
	land_cover_class = sheet.row(14)[2].value.strip()
	land_cover_type = sheet.row(15)[2].value.strip()
	spectrum = sheet.row(16)[2].value.strip()
	target_homogeneity = str(int(sheet.row(17)[2].value * 100)) + "%"
	pictures_file_name = sheet.row(18)[2].value.strip()
	num_of_spectra = str(int(sheet.row(19)[2].value))
	white_reference = sheet.row(20)[2].value.strip()
	sensor = sheet.row(21)[2].value.strip()
	instrument = sheet.row(22)[2].value.strip()
	try:
		fiber_optic_cable_length = sheet.row(23)[2].value.strip()
	except:
		fiber_optic_cable_length = str(sheet.row(23)[2].value)

	if sheet.row(24)[2].value.strip() == u'\xfc':
		reflectance = True
	else:
		reflectance = False

	if sheet.row(25)[2].value.strip() == u'\xfc':
		digital_numbers = True
	else:
		digital_numbers = False

	try:
		cloud_cover = sheet.row(26)[2].value.strip()
	except:
		cloud_cover = str(sheet.row(26)[2].value)

	file_format = sheet.row(27)[2].value.strip()
	target_irradiance_1 = sheet.row(28)[2].value.strip()
	target_irradiance_2 = sheet.row(29)[2].value.strip()
	target_irradiance_3 = sheet.row(30)[2].value.strip()
	white_reference_file_names = sheet.row(31)[2].value.strip()
	reflectance_1 = sheet.row(32)[2].value.strip()
	reflectance_2 = sheet.row(33)[2].value.strip()
	reflectance_3 = sheet.row(34)[2].value.strip()
	common_name = sheet.row(35)[2].value.strip().title().replace("(","").replace(")","")
	scientific_name = sheet.row(36)[2].value.strip().capitalize()
	leaf_canopy = sheet.row(37)[2].value.strip()

	try:
		ground_canopy_distance = sheet.row(38)[2].value.strip()
	except:
		ground_canopy_distance = str(sheet.row(38)[2].value)

	phenologic_stage = sheet.row(39)[2].value.strip().title()

	if sheet.row(40)[2].value.strip() == u'\xfc':
		presence_of_irrigation = True
	else:
		presence_of_irrigation = False

	background = sheet.row(41)[2].value.strip()
	soil_type = sheet.row(42)[2].value.strip()
	target_file = "spectral_target/%s.zip" % target_name
	graph = "spectral_graph/%s.png" % target_name
	image = "spectral_image/%s.jpg" % target_name

	if not os.path.exists(os.path.join(uploaded_dir, "spectral_image/%s.jpg" % target_name)):
		image = image.replace(".jpg",".JPG")

	target = Target()
	target.site_id = site_id
	target.date_acquired = date_acquired
	target.purpose = purpose
	target.observer = observer
	target.time_acquired = time_acquired
	target.waypoint = waypoint
	target.latitude = latitude
	target.longitude = longitude
	target.altitude = altitude
	target.gps_unit = gps_unit
	target.province = province
	target.city_municipality = city_municipality
	target.barangay = barangay
	target.land_cover_class = land_cover_class
	target.land_cover_type = land_cover_type
	target.spectrum = spectrum
	target.target_homogeneity = target_homogeneity
	target.pictures_file_name = pictures_file_name
	target.num_of_spectra = num_of_spectra
	target.white_reference = white_reference
	target.sensor = sensor
	target.instrument = instrument
	target.fiber_optic_cable_length = fiber_optic_cable_length
	target.reflectance = reflectance
	target.digital_numbers = digital_numbers
	target.cloud_cover = cloud_cover
	target.file_format = file_format
	target.target_irradiance_1 = target_irradiance_1
	target.target_irradiance_2 = target_irradiance_2
	target.target_irradiance_3 = target_irradiance_3
	target.white_reference_file_names = white_reference_file_names
	target.reflectance_1 = reflectance_1
	target.reflectance_2 = reflectance_2
	target.reflectance_3 = reflectance_3
	target.common_name = common_name
	target.scientific_name = scientific_name
	target.leaf_canopy = leaf_canopy
	target.ground_canopy_distance = ground_canopy_distance
	target.phenologic_stage = phenologic_stage
	target.presence_of_irrigation = presence_of_irrigation
	target.background = background
	target.soil_type = soil_type
	target.target_file = target_file
	target.graph = graph
	target.image = image
	target.save()

if __name__ == "__main__":
	input_directory = "/home/admin/geonode/scripts/utils/sample_spectro"

	for x in sorted(os.listdir(input_directory)):
		target_src = os.path.join(input_directory,x)
		try:
			read_excel(target_src)
			print "Successfully uploaded %s" % x
		except:
			print "Error uploading %s" % x
			traceback.print_exc()
