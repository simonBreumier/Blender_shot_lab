"""
Generate calibration pictures of the chessboard position in the sample frame
"""
import bpy
import numpy as np
import math
import random
import mathutils
import os


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


def make_camera(camPos, shot_coor):
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


def make_tilted_sample(angle, axis, camPos, title, chess_path):
    """
    Generate a chessboard tilted in the sample frame

    :param angle: sample rotation agle
    :param axis: sample rotation axis
    :param camPos: camera position triplet
    :param title: file path to save the pictures to
    :return:
    """
    del_all()
    L = 2
    h = 0.1
    f = h / L

    scene = bpy.context.scene
    plateCalib = make_make_plate(L, f, chess_path)
    bpy.ops.object.light_add(type='SUN', radius=1, location=(0, 0, 11))
    point_at(bpy.context.scene.objects['Sun'], (0., 10., 0.))
    bpy.ops.object.select_all(action='DESELECT')
    cam = make_camera(camPos, (0., 0., 0.))
    cam.select_set(True)
    bpy.ops.transform.rotate(value=angle, orient_axis=axis)

    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = 500
    scene.render.resolution_y = 500
    scene.camera = cam
    scene.render.filepath = title+".png"
    bpy.ops.render.render(write_still = 1)

#################### MAIN CODE #############################
conver = math.pi/180
#rep = "C:/Users/Simon/Documents/GitHub/Blender_shot_lab/sources/"
rep = os.path.dirname(os.path.abspath(( bpy.context.space_data.text.filepath)))+ "/../sources/"
chessboard_path = rep  + "chessboard.png"
make_tilted_sample(0., 'X', (0., 0., 5.), rep+"tilted_top", chessboard_path)
make_tilted_sample(0., 'Z', (0., 0., 5.), rep+"tilted_left", chessboard_path)