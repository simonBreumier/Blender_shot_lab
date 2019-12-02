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
	bpy.ops.transform.rotate(value=math.pi/4, orient_axis='X')
	bpy.ops.transform.rotate(value=math.pi/4, orient_axis='Y')
	cubeObj = bpy.context.scene.objects["Cube"]
	cubeObj.select_set(True)
	
	mat = bpy.data.materials.new(name="test")
	mat.use_nodes = True
	bsdf = mat.node_tree.nodes["Principled BSDF"]
	texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
	texImage.image = bpy.data.images.load("Y:\\0_Travaux\\VUMAT_Khan\\Blender_shot_lab\\pattern.png")
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

def make_cam(location):
	cam_data = bpy.data.cameras.new('camera')
	cam = bpy.data.objects.new('camera', cam_data)
	cam.location = location
	cam.data.type = "ORTHO"
	cam.data.lens = 0.1
	return cam
	
	
del_all()
L = 2
h = 0.1
f = h/L

scene = bpy.context.scene
plateCalib = make_make_plate(L, f)

bpy.ops.object.light_add(type='SUN', location=(0, 0, 11.))

scene.render.image_settings.file_format = 'PNG'
# cam.data.dof.aperture_ratio = 0.1
bpy.context.scene.use_nodes = True
distNode = bpy.context.scene.node_tree.nodes.new('CompositorNodeLensdist')
bpy.context.scene.node_tree.links.new(bpy.context.scene.node_tree.nodes["Render Layers"].outputs[0], distNode.inputs[0])
bpy.context.scene.node_tree.links.new(bpy.context.scene.node_tree.nodes["Composite"].inputs[0], distNode.outputs[0])
distNode.inputs[1].default_value = 0.1
distNode.use_projector = False

cam = make_cam((0., 0., 11.))
scene.camera = cam
scene.render.filepath = "Y:\\0_Travaux\\VUMAT_Khan\\Blender_shot_lab\\2cam_top.png"
bpy.ops.render.render(write_still = 1)

cam = make_cam((-11., 0. ,0.))
cam.rotation_euler = (0., -math.pi/2, 0.)
scene.camera = cam
scene.render.filepath = "Y:\\0_Travaux\\VUMAT_Khan\\Blender_shot_lab\\2cam_left.png"
bpy.ops.render.render(write_still = 1)
