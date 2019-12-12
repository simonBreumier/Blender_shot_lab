"""
Generate calibration pictures for camera intrisinc parameters calibration: moves a 7x7 chessboard in front of a camera
with different angle.
"""
import bpy
import numpy as np
import math
import mathutils


def del_all():
    """
    Resets the scene

    :return:
    """
    for elem in bpy.context.scene.objects:
        elem.select_set(True)
    bpy.ops.object.delete()
    bpy.context.scene.use_nodes = True
    for elem in bpy.context.scene.node_tree.nodes.keys():
        if not(elem == "Render Layers" or elem == "Composite"):
            bpy.context.scene.node_tree.nodes.remove(bpy.context.scene.node_tree.nodes[elem])


def make_make_plate(L, h, chess_path):
    """
    Generate the calibration chessborad plate

    :param L: chessboard square size (bu)
    :param h: chessboard height to length ratio
    :param chess_path: chessboard picture path
    :return:
    """
    bpy.ops.mesh.primitive_cube_add(size=L, enter_editmode=False, location=(0, 0, 0))
    bpy.ops.transform.resize(value=(1, 1, h))
    cubeObj = bpy.context.scene.objects["Cube"]
    cubeObj.select_set(True)

    mat = bpy.data.materials.new(name="test")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load(chess_path)
    texImage.texture_mapping.scale= (4., 4., 1.)
    texImage.texture_mapping.translation = (0.5, 0., 0.)
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
    if cubeObj.data.materials:
        cubeObj.data.materials[0] = mat
    else:
        cubeObj.data.materials.append(mat)

    return cubeObj


def make_camera(camPos, shot_coor)
    """
    Generate a camera at a given position and make it point given coordinates
    
    :param camPos: Camera position triplet
    :param shot_coor: object to look at position triplet
    :return: 
    """
    bpy.ops.object.camera_add()
    cam_object = bpy.context.object
    # cam_object.data.type = 'ORTHO'
    cam_object.location = camPos
    point_at(cam_object, shot_coor)
    bpy.context.scene.camera = cam_object
    return cam_object


def point_at(obj, target, roll=0):
    """
    Rotate obj to look at target

    :param obj: the object to be rotated. Usually the camera
    :param target: the location (3-tuple or Vector) to be looked at
    :param roll: The angle of rotation about the axis from obj to target in radians.
    Based on: https://blender.stackexchange.com/a/5220/12947 (ideasman42)
    """
    if not isinstance(target, mathutils.Vector):
        target = mathutils.Vector(target)
    loc = obj.location
    # direction points from the object to the target
    direction = target - loc

    quat = direction.to_track_quat('-Z', 'Y')

    # /usr/share/blender/scripts/addons/add_advanced_objects_menu/arrange_on_curve.py
    quat = quat.to_matrix().to_4x4()
    rollMatrix = mathutils.Matrix.Rotation(roll, 4, 'Z')

    # remember the current location, since assigning to obj.matrix_world changes it
    loc = loc.to_tuple()
    obj.matrix_world = quat @ rollMatrix
    obj.location = loc

#################### MAIN CODE #############################
del_all()
L = 2.
h = 0.1
f = h/L
bpy.context.scene.render.resolution_x = 500
bpy.context.scene.render.resolution_y = 500
dist_param = 0.
chess_path = "C:/Users/Simon/Documents/GitHub/Blender_shot_lab/sources/chessboard.png"
render_path = "C:/Users/Simon/Documents/GitHub/Blender_shot_lab/lens_dist_calib"

scene = bpy.context.scene
plateCalib = make_make_plate(L, f, chess_path)

bpy.ops.object.light_add(type='SUN', location=(0, 0, 5.))
point_at(bpy.context.scene.objects['Sun'], (0. ,10. ,0.))
scene.render.image_settings.file_format = 'PNG'

bpy.context.scene.use_nodes = True
distNode = bpy.context.scene.node_tree.nodes.new('CompositorNodeLensdist')
bpy.context.scene.node_tree.links.new(bpy.context.scene.node_tree.nodes["Render Layers"].outputs[0], distNode.inputs[0])
bpy.context.scene.node_tree.links.new(bpy.context.scene.node_tree.nodes["Composite"].inputs[0], distNode.outputs[0])
distNode.inputs[1].default_value = dist_param
distNode.use_projector = False

cam = make_camera((0., 0., 5.), (0., 0., 0.))
scene.camera = cam

bpy.context.scene.render.image_settings.color_mode = 'BW'
angles = np.linspace(-math.pi/4, math.pi/4, 20)
ang_pert = np.linspace(-math.pi/12, math.pi/12, 20)
bpy.ops.object.select_all(action='DESELECT')
i = 0
plateCalib.select_set(True)
angMax = math.pi/5

for ang_actu in angles:
    ang1 = ang_pert[i]
    bpy.ops.transform.rotate(value=ang1, orient_axis='Y')
    ang2 = (-1)**i * ang_pert[i]
    bpy.ops.transform.rotate(value=ang2, orient_axis='X')
    bpy.ops.transform.rotate(value=ang_actu, orient_axis='Z')
    scene.render.filepath = render_path+"/ang_"+str(i)+".png"
    bpy.ops.render.render(write_still = 1)
    bpy.ops.transform.rotate(value=-ang_actu, orient_axis='Z')
    bpy.ops.transform.rotate(value=-ang2, orient_axis='X')
    bpy.ops.transform.rotate(value=-ang1, orient_axis='Y')
    i+=1
