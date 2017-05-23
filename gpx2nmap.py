#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

import gpxpy
import json
import uuid
import argparse
import os
import re
import zipfile
import csv

version = "3.9.7"

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('input_file', type=argparse.FileType('r', encoding='UTF-8'), help='input file name')
	parser.add_argument('-f', '--folder-name', dest='folder_name', default='', help='folder name in Yandex.Disk')
	parser.add_argument('-t', '--file-type', dest='file_type', help='set file type to FILE_TYPE. Ex.: -t gpx')
	parser.add_argument('-p', dest='print_data', action='store_true', help='print output to stdout')
	parser.add_argument('-v', '--version', action='version', version=parser.prog + ' ' + version, help='display the version of Gpx2Nmap and exit')
	args = parser.parse_args()

	if args.folder_name:
		args.folder_name += '/'

# Calculate middle point of path. Simple math.
def middle_point(path):
	if len(path) > 2:
		return path[((len(path)-1)//2)]
	elif len(path) == 2:
		lon = sum([path[0][0], path[1][0]])/2
		lat = sum([path[0][1], path[1][1]])/2
		return [lon, lat]
	else:
		return path[0]

def gpx_parse(input_file):
	gpx_file = open(input_file, errors='ignore')
	gpx = gpxpy.parse(gpx_file)

	points = {}
	paths = {}
	for track in gpx.tracks:
		trk_coord = []
		for segment in track.segments:
			for point in segment.points:
				trk_coord.append([point.longitude, point.latitude])
		if trk_coord:
			paths[str(uuid.uuid4())] = trk_coord
			# Add middle point of path to gpx.waypoints
			if track.name:
				trk_middle = middle_point(trk_coord)
				gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(trk_middle[1], trk_middle[0], name='\n'.join(filter(None, (track.name, track.comment, track.description)))))

	for route in gpx.routes:
		path_coord = []
		for point in route.points:
			path_coord.append([point.longitude, point.latitude])
		if path_coord:
			paths[str(uuid.uuid4())] = path_coord
			# Add middle point of path to gpx.waypoints
			if route.name:
				path_middle = middle_point(path_coord)
				gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(path_middle[1], path_middle[0], name='\n'.join(filter(None, (route.name, route.comment, route.description)))))

	for waypoints in gpx.waypoints:
		uid = str(uuid.uuid4())
		point = {'coords': [waypoints.longitude, waypoints.latitude]}
		point['desc'] = '\n'.join(filter(None, (waypoints.name, waypoints.comment, waypoints.description)))
		if bool(waypoints.extensions):
			# Windows version want aq:picture key
			if "aq:picture" in waypoints.extensions:
				# Need check if output_folder is root /
				point['photo'] = '/' + args.folder_name + os.path.basename(waypoints.extensions["aq:picture"])
			elif "picture" in waypoints.extensions:
				point['photo'] = '/' + args.folder_name + os.path.basename(waypoints.extensions["picture"])
		points[uid] = point

	out = {}
	out['paths'] = paths
	out['points'] = points

	index_json(out)

def kml_parse(input_file, output_folder = ''):
	import lxml.objectify as objectify
	with open(input_file, errors='ignore') as xml:
		kml = objectify.parse(xml).getroot()

	namespace = {"ns": "http://www.opengis.net/kml/2.2", "gx":"http://www.google.com/kml/ext/2.2"}
	points = {}
	paths = {}
	# Find all Placemarks in root
	for pm in kml.findall(".//ns:Placemark", namespaces=namespace):
		if hasattr(pm, 'Point'):
			point = {'coords': [float(x) for x in str(pm.Point.coordinates).split()[0].split(',')[:2]]}
			desc = []
			if hasattr(pm, 'name'):
				desc.append(str(pm.name))
			if hasattr(pm, 'description'):
				# Strip all html tags from point.description
				desc.append(re.sub('<.*?>','',str(pm.description)))
				# Get image name from point.description
				photos = re.findall('<img.*?src="(?!http[s]?://)(.*?)"', str(pm.description))
				if photos:
					point['photo'] = '/' + args.folder_name + output_folder + os.path.basename(photos.pop(0))
					if len(photos)>0:
						for photo in photos:
							desc.append(photo)
				
			point['desc'] = '\n'.join(filter(None, desc))
			points[str(uuid.uuid4())] = point
		elif hasattr(pm, 'MultiGeometry'):
			for LineString in pm.MultiGeometry.findall(".//ns:LineString", namespaces=namespace):
				path_point = []
				for coord in str(LineString.coordinates).split():
					path_point.append([float(x) for x in coord.split(',')[:2]])
				if hasattr(pm, "name"):
					points[str(uuid.uuid4())] = {'coords': middle_point(path_point), 'desc': str(pm.name)}
				paths[str(uuid.uuid4())] = path_point

		elif hasattr(pm, 'LineString'):
			path_point = []
			for coord in str(pm.LineString.coordinates).split():
				path_point.append([float(x) for x in coord.split(',')[:2]])
			if hasattr(pm, "name"):
				points[str(uuid.uuid4())] = {'coords': middle_point(path_point), 'desc': str(pm.name)}
			paths[str(uuid.uuid4())] = path_point

		elif hasattr(pm, "{http://www.google.com/kml/ext/2.2}MultiTrack") is not None:
			MultiTrack = getattr(pm, "{http://www.google.com/kml/ext/2.2}MultiTrack", None)
			for mt in MultiTrack:
				for tr in getattr(mt, "{http://www.google.com/kml/ext/2.2}Track", None):
					path_point = []
					for co in getattr(tr, "{http://www.google.com/kml/ext/2.2}coord", None):
						path_point.append([float(x) for x in str(co).split()[:2]])
					paths[str(uuid.uuid4())] = path_point
					if hasattr(pm, "name"):
						points[str(uuid.uuid4())] = {'coords': middle_point(path_point), 'desc': str(pm.name)}

	out = {}
	out['paths'] = paths
	out['points'] = points

	index_json(out)

def kmz_parse(input_file):
	from pykml import parser
	images_output_folder = ''
	output_folder = ''
	filename = os.path.splitext(os.path.basename(input_file))[0]
	with zipfile.ZipFile(input_file) as kmz_file:
		for images in kmz_file.namelist():
			if images.startswith('files/'):
				kmz_file.extract(images)
				images_output_folder = 'files/'
		if images_output_folder:
			output_folder = filename + '/' + images_output_folder
		# with kmz_file.open('doc.kml', 'r') as kml_file:
		kmz_file.extract('doc.kml')
		kml_parse('doc.kml', output_folder)

def csv_parse(input_file):
	with open(input_file, encoding='utf-8') as csv_file:
		csv_sample = csv_file.read(1024)
		sniffer = csv.Sniffer()
		try:
			header = sniffer.has_header(csv_sample)
		except:
			header = None
		try:
			dialect = sniffer.sniff(csv_sample)
		except:
			dialect = 'excel'
			
		csv_file.seek(0)

		fieldnames = None

		if not header:
			csv_data = csv.reader(csv_file, dialect=dialect)
			sample = next(csv_data)
			csv_file.seek(0)

			fieldnames = []
			coords = ["Latitude", "Longitude"]
			i = 0
			for column in sample:
				i += 1
				if re.match("^-?\d+\.\d+$", column):
					fieldnames.append(coords.pop(0))
				else:
					fieldnames.append(str(i))

		if header or fieldnames:
			csv_data = csv.DictReader(csv_file, fieldnames=fieldnames, dialect=dialect)

		fields = ["Latitude", "Longitude"]
		points = {}
		for row in csv_data:
			if all(field in row for field in fields):
				points[str(uuid.uuid4())] = {'coords': [float(row.pop("Longitude")), float(row.pop("Latitude"))], 'desc': '\n'.join(['{}: {}'.format(k,v) for k,v in sorted(row.items())])}
		
		out = {}
		out['paths'] = {}
		out['points'] = points
		
		index_json(out)

def index_json(data):
	if args.print_data:
		print(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
	else:
		index_file = open('index.json', 'w')
		json.dump(data, index_file, ensure_ascii=False, separators=(',', ':'))
		index_file.close

switch={'gpx':gpx_parse, 'kml':kml_parse, 'kmz':kmz_parse, 'csv':csv_parse}

if args.file_type:
	extension = args.file_type
else:
	extension = os.path.splitext(args.input_file.name)[1][1:]

try:
	switch[str(extension.lower())](args.input_file.name)
except KeyError:
	print("Error: unsupported file extension\nSupported extensions: .gpx, .kml, .kmz, .csv. Try -t option\n")
	parser.print_help()
	raise
except:
	print("Error: something went wrong. Unsupported file type or other error.")
	raise
