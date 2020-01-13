"""
Generate picture of a sphere with a given trajectory file, filmed by two cameras
"""
import bpy
import colorsys
import numpy as np
import mathutils
import math
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


def make_shot(R, X, Y, Z):
    """
    Generate the sphere object to be moved
    :param R: sphere radius (bu)
    :param X,Y,Z: sphere coordinates
    :return: sphere blender object
    """
    bpy.ops.mesh.primitive_uv_sphere_add(radius=R, location = (X,Y,Z))
    current = bpy.context.scene.objects["Sphere"]
    current.name = 'Shot'
    current.data.name = 'Mesh'
    mat = bpy.data.materials.new(name='ShotMat')
    mat.diffuse_color[:3] = colorsys.hsv_to_rgb(0.5, 0.5, 0.5)
    current.data.materials.append(mat)
    return current


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


def make_shot_film(shot_traj, fps, tot_time):
    """
    Generate keyframes of the sphere trajectory to make the animation
    :param shot_traj: trajectory as a list of triplets (X,Y,Z)
    :param fps: number of frame per seconds (not verified)
    :param tot_time: number of time increments (eg keyframes)
    :return:
    """
    fcount = tot_time
    fincr = fps
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = tot_time*fps
    shot_obj = make_shot(0.1, -5, 0., 0.)
    currframe = bpy.context.scene.frame_start
    for f in range(0, fcount, 1):
        bpy.context.scene.frame_set(currframe)
        shot_obj.location = shot_traj[f]
        shot_obj.keyframe_insert(data_path='location')
        currframe += fincr


def add_lens_dist(f):
    """
    add lens distortion of parameter f to the current camera using the CompositorNodeLensdist

    :param f: lens distortion parameter
    :return:
    """
    bpy.context.scene.use_nodes = True
    distNode = bpy.context.scene.node_tree.nodes.new('CompositorNodeLensdist')
    bpy.context.scene.node_tree.links.new(bpy.context.scene.node_tree.nodes["Render Layers"].outputs[0], distNode.inputs[0])
    bpy.context.scene.node_tree.links.new(bpy.context.scene.node_tree.nodes["Composite"].inputs[0], distNode.outputs[0])
    distNode.inputs[1].default_value = f
    distNode.use_projector = False


def make_anim(camPos, doublesin_traj, fpath, resx, resy, rot_euler, f=0.):
    """
    Render the animation as black and white JPEGs

    :param camPos: camera position triplet
    :param doublesin_traj: sphere trajectory as a triplet list
    :param fpath: path to save the pictures to
    :param resx, resy: camera resolution
    :param rot_euler: camera euler angles
    :param f: lens distortion parameter
    :return:
    """
    del_all()
    camera_left = make_camera(camPos, (0, 0, 0))
    camera_left.rotation_euler = rot_euler
    bpy.ops.object.light_add(type='SUN', radius=1, location=camPos)
    point_at(bpy.context.scene.objects['Sun'], (0., 0., 0.))
    make_shot_film(doublesin_traj, 1, numFrame)
    # add_lens_dist(f)
    # bpy.context.scene.render.resolution_x = resx
    # bpy.context.scene.render.resolution_y = resy
    # bpy.context.scene.render.filepath = fpath
    # bpy.context.scene.render.image_settings.color_mode = 'BW'
    # bpy.context.scene.render.image_settings.file_format='JPEG'
    #bpy.ops.render.render(animation=True)


def import_traj(file_path):
    """Import a trajectory from a column file (t, X, Y, Z)

    :param file_path: trajectory file path
    """
    file = open(file_path, "r")
    data = file.read().split("\n")
    file.close()
    traj_coords = []
    for line in data:
        data = list(map(float, line.split()))
        if len(data) > 0 and not(np.isnan(data[0]) or np.isnan(data[1]) or np.isnan(data[2]) or np.isnan(data[3])):
            traj_coords.append((data[0], data[1], data[2]))

    return traj_coords

#################### MAIN CODE #############################
doublesin_traj = import_traj("C:/Users/Simon/Documents/GitHub/Blender_shot_lab/Trajectory.txt")
numFrame = len(doublesin_traj)
f = 0.
resx = 500
resy = 500
make_anim((0.,-5., 0.), doublesin_traj, '', resx, resy, (math.pi/2, 0., 0.), f)
