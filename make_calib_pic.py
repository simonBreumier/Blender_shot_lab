"""
Generate calibration pictures for camera intrisinc parameters calibration
"""
import bpy
import numpy as np
import math
import random

def del_all():
	for elem in bpy.context.scene.objects:
		elem.select_set(True)
	bpy.ops.object.delete()
		
def make_make_plate(L, h):
	bpy.ops.mesh.primitive_cube_add(size=L, enter_editmode=False, location=(0, 0, 0))
	bpy.ops.transform.resize(value=(1, 1, h))
	cubeObj = bpy.context.scene.objects["Cube"]
	cubeObj.select_set(True)
	
	mat = bpy.data.materials.new(name="test")
	mat.use_nodes = True
	bsdf = mat.node_tree.nodes["Principled BSDF"]
	texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
	texImage.image = bpy.data.images.load("Y:\\0_Travaux\\Blender_lab\\pattern.png")
	texImage.projection = "FLAT"
	texImage.texture_mapping.scale= (4., 4., 1.)
	texImage.texture_mapping.translation = (0.5, 0., 0.)
	mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

	# Assign it to object
	if cubeObj.data.materials:
		cubeObj.data.materials[0] = mat
	else:
		cubeObj.data.materials.append(mat)
	
	# cubeObj.data.materials.append(mat)
	return cubeObj

del_all()
L = 2
h = 0.1
f = h/L

scene = bpy.context.scene
plateCalib = make_make_plate(L, f)
cam_data = bpy.data.cameras.new('camera')
cam = bpy.data.objects.new('camera', cam_data)
cam.location = (0., 0., 11.)
cam.data.type = "ORTHO"
bpy.ops.object.light_add(type='SUN', location=(0, 0, 11.))
scene.camera = cam
scene.render.image_settings.file_format = 'PNG'

angles = range(0, 20)
bpy.ops.object.select_all(action='DESELECT')
i = 0
plateCalib.select_set(True)
for ang_actu in angles:
	ang1 = -math.pi/3 + random.random()*math.pi/3
	bpy.ops.transform.rotate(value=ang1, orient_axis='Y')
	ang2 = -math.pi/3 + random.random()*math.pi/3
	bpy.ops.transform.rotate(value=ang2, orient_axis='X')
	scene.render.filepath = "Y:\\0_Travaux\\Blender_lab\\lens_dist_calib3\\ang_"+str(i)+".png"
	bpy.ops.render.render(write_still = 1)
	bpy.ops.transform.rotate(value=-ang2, orient_axis='X')
	bpy.ops.transform.rotate(value=-ang1, orient_axis='Y')
	i+=1
