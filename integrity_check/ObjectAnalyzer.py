#!/usr/bin/env python3.9
import pymeshlab as ml
import os
import json
import sys
import time
import subprocess
import traceback
import hashlib

# create a hashcode
def create_hashcode(path):
	md5_hash = hashlib.md5()
	a_file = open(path, "rb")
	content = a_file.read()
	md5_hash.update(content)
	hashcode = md5_hash.hexdigest()

	return hashcode

# check object for requirements
def check_object_for_requirements(data):
	success = True
	#data.update({
	#	"defects": {}
	#})
	
	if data["originally"]["Objectformat"] == '.ply':
		if data["textures"] != None:
			if data["textures"]["Number of missing textures"] > 0:
				print('  >>> Error! missing textures.')
				success = False
			if data["textures"]["Number of missing TIF textures"] > 0:
				print('  >>> Error! missing TIF textures.')
				success = False
				#data["defects"].update({"missing textures": data["textures"]["Number of missing textures"]})

	if data["originally"]["Objectformat"] == '.obj':
		if data["materials"] != None:
			if data["materials"]["Found"] == False:
				print('  >>> Error! missing materials.')
				success = False
				#data["defects"].update({"missing materials": data["materials"]["Number of missing materials"]})
			else:
				if data["materials"]["textures"] != None:
					if data["materials"]["textures"]["Number of missing textures"] > 0:
						print('  >>> Error! missing textures.')
						success	= False
					if data["materials"]["textures"]["Number of missing TIF textures"] > 0:
						print('  >>> Error! missing TIF textures.')
						success = False
	
	if data["non manifoldness"]["non manifold edges"] == True:
		print('  >>> Error! non manifold edges.')
		success = False

	if data["non manifoldness"]["non manifold vertices"] > 10:
		print('  >>> Error! to many non manifold vertices.')
		success = False
		# non manifold edges
	#if success:
		#data["defects"] = None
	if (data["originally"]["Codeformat"] == 'ascii') == False and (data["originally"]["Codeformat"] == 'ascii 1.0') == False:
		print('  >>> Error! The Object is not in acsii Format.')
		success = False
	return success

#find and check texture in mtl
def check_mtl_for_texture(mtllib_path, mtl_directory_path):
	texture_num = founded_textures = not_founded_textures = tiff_num = 0
	textures = {}
	temp = {}
	try:
		with open(mtllib_path, 'r', encoding='Latin-1') as read_mtl: 
			for texture_file in read_mtl: 
				if 'map_Kd ' in texture_file:
					texture_num += 1
					texture_file = texture_file.replace('map_Kd ', '')
					texture_file = texture_file.replace('\n', '')
					basename_tf    = os.path.basename(texture_file)
					obform		   = os.path.splitext(basename_tf)[1]
					if obform == '.tif':
						tiff_num += 1
					texture_path = mtl_directory_path + '/' + texture_file
					print(texture_path)
					texname = 'texture_'
					texname += str(texture_num)

					if os.path.exists(texture_path):
						founded_textures += 1
						print('Texture file', texture_file, 'found.')
						# get the filesize in byte (/1024 in KB and so on..)
						texture_size = os.path.getsize(texture_path)
						temp[texname] = ({"Name/Path from MTL": texture_file, "Found" : True, "Size": texture_size})
					else:
						not_founded_textures += 1
						temp[texname] = ({"Name/Path from MTL" : texture_file, "Found" : False})
						print('Texture file', texture_file, 'not found.')
		if texture_num == 0:
			print('Material file has no textures.')
			textures = None
		else:
			print(texture_num, 'Texture file/s is/are required.')
			print(founded_textures, 'Texture file/s found.')
			print(not_founded_textures, 'Texture file/s not found.')
			print(tiff_num, 'Texture in .tif format.')
			print(texture_num - tiff_num, 'Texture not in .tif format.')
			textures["Number of required textures"] = texture_num
			textures["Number of found textures"] = founded_textures
			textures["Number of missing textures"] = not_founded_textures
			textures["Number of TIF textures"] = tiff_num
			textures["Number of missing TIF textures"] = texture_num - tiff_num
			textures.update(temp)
			#print(textures)
		return textures
	except Exception as e:
		print(e)
		traceback.print_exc()
		time.sleep(10)

#find and check mtl file in obj
def check_obj_for_mtl(path, directory_path):
	texture_num = 0
	material_exists = False
	materials = {
		"materials": {}
	}
	temp = {}

	try:
		with open(path, 'r', encoding='Latin-1') as read_obj: 
			for mtllib_file in read_obj: 
				if 'mtllib ' in mtllib_file:
					material_exists = True
					mtllib_file = mtllib_file.replace('mtllib ', '')
					mtllib_file = mtllib_file.replace('\n', '')
					mtllib_path = directory_path + '/' + mtllib_file
					if os.path.exists(mtllib_path):
						print('Material file', mtllib_file, 'found.')
						material_size = os.path.getsize(mtllib_path)
						mtl_directory_path = os.path.dirname(mtllib_path)
						temp = ({"Name/Path": mtllib_file, "Found" : True, "Size": material_size, "textures" : check_mtl_for_texture(mtllib_path, mtl_directory_path)})
						
					else: 
						print('Material file', mtllib_file, 'not found.')
						print('Information about texture cant be researched.')
						temp = ({"Name/Path": mtllib_file, "Found" : False})
		
		if material_exists == False:
			print('Object has no material file.')
			materials["materials"] = None
		else:
			materials["materials"].update(temp)

		return materials
	except Exception as e:
		print(e)
		traceback.print_exc()
		time.sleep(10)

#find and check texture files in ply
def check_ply_for_texture(path, directory_path):
	
	texture_num = founded_textures = not_founded_textures = tiff_num = 0
	textures = {
		"textures": {},
	}
	temp = {}
	try:
		with open(path, 'r',encoding='Latin-1') as read_ply: 
			for texture_file in read_ply: 
				if 'comment TextureFile' in texture_file:
					texture_num += 1
					texture_file   = texture_file.replace('comment TextureFile ', '')
					texture_file   = texture_file.replace('\n', '')
					basename_tf    = os.path.basename(texture_file)
					obform		   = os.path.splitext(basename_tf)[1]
					if obform == '.tif':
						tiff_num += 1
					texture_path = directory_path + '/' + texture_file
					texname = 'texture_'
					texname += str(texture_num)
					
					if os.path.exists(texture_path):
						founded_textures += 1
						print('Texture file', texture_file, 'found.')
						# get the filesize in byte (/1024 in KB and so on..)
						texture_size = os.path.getsize(texture_path)
						temp[texname] = ({"Name/Path from PLY": texture_file, "Found" : True, "Size": texture_size})
					else:
						not_founded_textures += 1
						temp[texname] = ({"Name/Path from PLY" : texture_file, "Found" : False})
						print('Texture file', texture_file, 'not found.')
	
		if texture_num == 0:
			print('Object has no textures.')
			textures["textures"] = None
		else:
			print(texture_num, 'Texture file/s is/are required.')
			print(founded_textures, 'Texture file/s found.')
			print(not_founded_textures, 'Texture file/s not found.')
			print(tiff_num, 'Texture in .tif format.')
			print(texture_num - tiff_num, 'Texture not in .tif format.')
			textures["textures"]["Number of required textures"] = texture_num
			textures["textures"]["Number of found textures"] = founded_textures
			textures["textures"]["Number of missing textures"] = not_founded_textures
			textures["textures"]["Number of linked TIF textures"] = tiff_num
			textures["textures"]["Number of missing TIF textures"] = texture_num - tiff_num
			textures["textures"].update(temp)
			#print(textures)
		return textures
	except Exception as e:
		print(e)
		traceback.print_exc()

# display jsonData
def display_Data(data):
	print()
	print(json.dumps(data, indent=4))
	print()

# creating a las file
def create_las(path, objectname, las_folder):
	#cmd = start CloudCompare.exe -O Keller.ply -C_EXPORT_FMT LAS -SAVE_CLOUDS FILE Keller.las
	
	current_working_directory = os.path.abspath(os.getcwd())
	object_las_path 		  = las_folder + '/' + objectname + '.las'
	CloudCompareConverter_cmd = current_working_directory + '/CloudCompare/CloudCompare.exe -O ' + path + ' -C_EXPORT_FMT LAS -SAVE_CLOUDS FILE ' + object_las_path
	print(current_working_directory)
	print(CloudCompareConverter_cmd)

	if os.path.exists(object_las_path) == False:
		print('The Object is being converted in a las file for Potree...')
		process = subprocess.Popen(CloudCompareConverter_cmd, shell = True)
		returncode = process.poll()
		while returncode == None:
			returncode = process.poll()
			time.sleep(1)
		print('  >>> Object is sucessfully converted.')
	else:
		print('File %s already exists.' % object_las_path)
	return object_las_path

# Creating metadata for Potree
def create_PotreeMetadata(path, objectname, potree_folder, data):
	current_working_directory = os.path.abspath(os.getcwd())
	
	object_Potree_path 		  = potree_folder + '/' + objectname
	metadata_path 			  = object_Potree_path + '/' + 'metadata.json'
	potreeConverter_cmd		  = current_working_directory + '/potree_converter/PotreeConverter.exe ' + path + ' -o ' + object_Potree_path
	if os.path.exists(metadata_path) == False:
		 
		print('The Object is being converted in a Metadata file for Potree...')
		process = subprocess.Popen(potreeConverter_cmd, shell = True)
		returncode = process.poll()
		while returncode == None:
			returncode = process.poll()
			time.sleep(1)
		print('  >>> Object is sucessfully converted.')
	else:
		print('File %s already exists.' % metadata_path)
	
	objectsize = 0
	content = {}
	for path, dirs, files in os.walk(object_Potree_path):
		for f in files:
			fp = os.path.join(path, f)
			print(fp)
			objectsize += os.path.getsize(fp)
			content.update({
				f : {
					"filesize": os.path.getsize(fp)
				}
			})
	print('Folder Size:', objectsize, 'bytes')

	data.update({
		"POTREE Convertion": {
			"Foldername": object_Potree_path,
			"Objectformat": ".bin/.json",
			"Codeformat": "binary/acsii",
			"Totalsize": objectsize,
			"content":{}
		}
	})
	data["POTREE Convertion"]["content"].update(content)
	
#create new Json Data
def create_JsonData(jsonData_path, data):
	# controll, if File exists, delete it
	if os.path.exists(jsonData_path):
		os.remove(jsonData_path)
		print(jsonData_path, 'is removed.')
	# Creating Json file
	print(jsonData_path, 'is being created...')
	f = open(jsonData_path, "w")
	f.write(json.dumps(data, indent=4))
	f.close()
	print(jsonData_path, 'is sucessfully created.')

# Creating NXS and NXZ file
def create_NXS_NXZ(georeference, objecttype, objectname, path, nexus_folder):
	waiting = True
	georeference_option = ''
	pointcloud_option = ''

	if georeference == True:
		georeference_option = ' -G'
		print('georeference option', georeference_option, 'is on.')

	if objecttype == 'pointcloud':
		pointcloud_option = ' -p'

	if objecttype == 'pointcloud' and georeference == True:
		print('Pointclouds with Georeferences can not converted in a nxs-file.')
		time.sleep(5)
		sys.exit(0)
	current_working_directory = os.path.abspath(os.getcwd())
	object_NXS_path = nexus_folder + '/' + objectname + '.nxs'
	object_NXZ_path = nexus_folder + '/' + objectname + '.nxz'
	nxsbuild_cmd    = current_working_directory+'/nexus_converter/nxsbuild.exe ' + path + ' -o ' + object_NXS_path + pointcloud_option + georeference_option
	nxscompress_cmd = current_working_directory+'/nexus_converter/nxscompress.exe ' + object_NXS_path + ' -o ' + object_NXZ_path

	if os.path.exists(object_NXS_path)  == False:
		print('The Object is being converted in a nxs file...')
		process = subprocess.Popen(nxsbuild_cmd, shell = True)
		returncode = process.poll()
		while returncode == None:
			returncode = process.poll()
		#	print (returncode)
			time.sleep(0.2)
		print('  >>> Object is sucessfully converted.')
	else:
		print('File %s already exists.' % object_NXS_path)
	
	if os.path.exists(object_NXZ_path) == False: 
		waiting = True
		print('The Object is being converted in a nxz file...')
		process = subprocess.Popen(nxscompress_cmd, shell = True)
		returncode = process.poll()
		while returncode == None:
			returncode = process.poll()
			time.sleep(0.2)
		print('  >>> Object is sucessfully converted.')
	else:
		print('File %s already exists.' % object_NXZ_path)

# check_non_manifold_vertices (only for mesh)
def check_non_manifold_vertices(ms, num_verts):
	print('The object is being checked by non manifold vertices...')
	print(ms.apply_filter('select_non_manifold_vertices'))
	ms.apply_filter('delete_selected_vertices')
	new_num_verts   =  ms.current_mesh().vertex_number() 
	non_manifold_vertices = new_num_verts - num_verts
	non_manifold_vertices = abs(non_manifold_vertices)
	print('non_manifold_vertices:', non_manifold_vertices)
	if non_manifold_vertices != 0:
		print('  >>> ERROR!!! This object has', non_manifold_vertices ,'non manifold vertices.')
		return non_manifold_vertices
	else:
		print('  >>> This object hasnt non manifold vertices.')
		return non_manifold_vertices

# check_non_manifold_edges (only for mesh)
def check_non_manifold_edges(ms):
	print('The object is being checked by non manifold edges...')
	print (ms.apply_filter('select_non_manifold_edges_'))
	faces_from_non_manifold_edges = ms.current_mesh().selected_face_number()
	if faces_from_non_manifold_edges != 0:
		print('  >>> ERROR!!! This object has non manifold edges from non manifold faces.')
		return True
	else:
		print('  >>> This object hasnt non manifold edges and non manifold faces.')
		return False

# Checking for Georeference
def check_Georeference(vert_matrix):
	for x in range(len(vert_matrix)):
		for y in range(len(vert_matrix[x])):
			if vert_matrix[x][y] > 1000:
				return True
	return False

# Mesh or Pointcloud
def get_ObjectType(num_face):
	if num_face > 0:
		return 'mesh'
	if num_face == 0 and num_verts > 0:
		return 'pointcloud'

# get plyformat from .ply
def get_plyformat(path):
	try:
		with open(path, 'r',encoding='Latin-1') as read_obj: 
			for line in read_obj: 
				if 'format' in line:
					line = line.replace('format ', '')
					line = line.replace('\n', '')
					return line
	except Exception as e:
		print(e)
		traceback.print_exc()
		time.sleep(20)

# check codeformat
def get_codeformat(objectformat, path):
	if objectformat == '.ply':
		return get_plyformat(path)
	elif objectformat == '.obj':
		return 'ascii'
	elif objectformat == '.las' or objectformat == '.laz':
		return 'binary'

# create to folder
def create_folder(json_folder, nexus_folder, potree_folder, las_folder, pymeshlab_folder):
	try:
		os.mkdir(json_folder)
	except OSError:
		print ("Creation of the directory %s failed. Folder already exists." % json_folder)
	else:
		print ("Successfully created the directory %s." % json_folder)
	try:
		os.mkdir(nexus_folder)
	except OSError:
		print("Creation of the directory %s failed. Folder already exists." % nexus_folder)
	else:
		print("Successfully created the directory %s." % nexus_folder)
	try:
		os.mkdir(potree_folder)
	except OSError:
		print("Creation of the directory %s failed. Folder already exists." % potree_folder)
	else:
		print("Successfully created the directory %s." % potree_folder)
	try:
		os.mkdir(las_folder)
	except OSError:
		print ("Creation of the directory %s failed. Folder already exists." % las_folder)
	else:
		print ("Successfully created the directory %s." % las_folder)
	try:
		os.mkdir(pymeshlab_folder)
	except OSError:
		print ("Creation of the directory %s failed. Folder already exists." % pymeshlab_folder)
	else:
		print ("Successfully created the directory %s." % pymeshlab_folder)

if __name__ == '__main__':
	#print (sys.argv)
	for argv in sys.argv:
		# Name of folders
		json_folder      = 'jsonData'
		nexus_folder     = 'nexusData'
		potree_folder    = 'potreeData'
		las_folder		 = 'lasData'
		pymeshlab_folder = 'pymeshlabData'
		conversion = False

		# get console input
		path = argv
		path = os.path.abspath(path)
		#print(path)
		#print(os.path.abspath(__file__))

		# get name from path
		basename        			 = os.path.basename(path)
		directory_path				 = os.path.dirname(path)
		objectname      			 = os.path.splitext(basename)[0]
		objectformat				 = os.path.splitext(basename)[1]
		obformat					 = objectformat.replace(".","_")
		json_nexus_potree_objectname = objectname + obformat #Warum habe ich mir diesen Namen ausgedacht?
		
		# skip first argument
		if objectname == "ObjectAnalyzer":
			continue
		# check fileformat
		if objectformat != '.ply' and objectformat != '.obj':
			print('The file has not the right format.')
			time.sleep(3)
			#exit()
		else:
			# get the filesize in byte (/1024 in KB and so on..)
			objectsize = os.path.getsize(path)
			print('File Size:', objectsize, 'bytes')

			create_folder(json_folder, nexus_folder, potree_folder, las_folder, pymeshlab_folder)
			
			# get format from object (Ascii, binary)
			codeformat = get_codeformat(objectformat, path)
			
			data = {
				"originally":{
					"Objectname": objectname,
					"Objectformat": objectformat,
					"Codeformat": codeformat,
					"Objectsize": objectsize,
					"hash code": create_hashcode(path)
				}
			}

			#creating meshset
			print('The Meshset is being created...')
			ms = ml.MeshSet()
			print('  >>> The Meshset is created.')
			time.sleep(5)
			# Load 3D model
			print('The object is being loaded...')
			if ms.load_new_mesh(path):
				print('  >>> Error loading object.')
			else:
				print('  >>> The Object is successfully loaded.')

			print('The object is being analysed...')

			# vertices, faces and edges from object
			num_verts    = ms.current_mesh().vertex_number() 
			num_face     = ms.current_mesh().face_number()
			num_edge     = ms.current_mesh().edge_number()
			vert_matrix  = ms.current_mesh().vertex_matrix()
			face_matrix  = ms.current_mesh().face_matrix()
			objecttype 	 = get_ObjectType(num_face)
			georeference = check_Georeference(vert_matrix)
			
			data.update({
				"characteristics": {
					"Type": objecttype,
					"Vertices": num_verts,
					"Faces": num_face,
					"Edges": num_edge,
					"Georeferences": georeference
				}
			})

			# falls hier festgestellt wird, dass es sich um eine Punktwolke im ply format handelt, wird die Datei in eine las Datei konvertiert, wenn nicht fahre fort
			if objectformat == '.ply' and objecttype == 'pointcloud':
				
				if (codeformat == 'ascii') or (codeformat == 'ascii 1.0'):

					path_las_object_file = create_las(path, json_nexus_potree_objectname, las_folder)
					
					las_objectsize = os.path.getsize(path_las_object_file)
					print('LAS File Size:', las_objectsize, 'bytes')
					
					# aktuelle Info über Objekt + Umwandlung von ply zu las
					las_name   = os.path.splitext(os.path.basename(path_las_object_file))[0]
					las_format = os.path.splitext(os.path.basename(path_las_object_file))[1]
					
					data.update({
						"LAS Convertion": {
							"Objectname": las_name,
							"Objectformat": las_format,
							"Codeformat": "binary",
							"Objectsize": las_objectsize
						}
					})
					
					json_nexus_potree_objectname = json_nexus_potree_objectname + '_las'
					
					create_PotreeMetadata(path_las_object_file, json_nexus_potree_objectname, potree_folder, data)
					jsonData_path = json_folder + '/' + json_nexus_potree_objectname + '.json'
				else:
					print('  >>> Error! The Object is not in acsii Format.')
					jsonData_path = json_folder + '/' + json_nexus_potree_objectname + '_Error.json'
				
				display_Data(data)
				create_JsonData(jsonData_path, data)
			else:
				
				non_manifold_edges 	  = check_non_manifold_edges(ms)
				print('The Object is being reloaded...')
				ms.load_current_mesh(path)
				print('  >>> The object is reloaded')
				non_manifold_vertices = check_non_manifold_vertices(ms, num_verts)
				
				data.update({
					"non manifoldness": {
						"non manifold edges": non_manifold_edges,
						"non manifold vertices": non_manifold_vertices
					}
				})
				
				if objectformat == '.ply':
					data.update(check_ply_for_texture(path, directory_path))
					
				if objectformat == '.obj':
					data.update(check_obj_for_mtl(path, directory_path))

				display_Data(data)
				
				if check_object_for_requirements(data) == False:
					print('The Object does not meet the requirements.')
					jsonData_path   = json_folder + '/' + json_nexus_potree_objectname + '_Error.json'
				else:
					print('The object meets the requirements.')
					create_NXS_NXZ(georeference, objecttype, json_nexus_potree_objectname, path, nexus_folder)
					jsonData_path   = json_folder + '/' + json_nexus_potree_objectname + '.json'
				create_JsonData(jsonData_path, data)
				
		time.sleep(3)
	time.sleep(10)	
