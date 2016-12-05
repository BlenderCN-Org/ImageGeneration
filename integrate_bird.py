'''
Create Bounding Box for the whole bird and then calculate the radius (Which is the L in the LGMD model)
'''
import bpy
import bmesh
from bpy.props import BoolProperty, FloatVectorProperty
import mathutils
from bpy_extras import object_utils
from mathutils import Vector

def CreateBoundingBox(context):
    minx, miny, minz = (999999.0,)*3
    maxx, maxy, maxz = (-999999.0,)*3
    for obj in context.selected_objects:
        for v in obj.bound_box:
            v_world = obj.matrix_world * mathutils.Vector((v[0],v[1],v[2]))
            if v_world[0] < minx:
                minx = v_world[0]
            if v_world[0] > maxx:
                maxx = v_world[0]
            if v_world[1] < miny:
                miny = v_world[1]
            if v_world[1] > maxy:
                maxy = v_world[1]
            if v_world[2] < minz:
                minz = v_world[2]
            if v_world[2] > maxz:
                maxz = v_world[2]

    values = (((maxx-minx)/2.0) + ((maxz-minz)/2.0) + ((maxy-miny)/2.0))/6.0
    return values



class Box:

    dim_x = 1
    dim_y = 1

    def __init__(self, min_x, min_y, max_x, max_y, dim_x=dim_x, dim_y=dim_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.dim_x = dim_x
        self.dim_y = dim_y

    @property
    def x(self):
        return round(self.min_x * self.dim_x)

    @property
    def y(self):
        return round(self.dim_y - self.max_y * self.dim_y)

    @property
    def width(self):
        return round((self.max_x - self.min_x) * self.dim_x)

    @property
    def height(self):
        return round((self.max_y - self.min_y) * self.dim_y)

    def __str__(self):
        return "<Box, x=%i, y=%i, width=%i, height=%i>" % \
               (self.x, self.y, self.width, self.height)

    def to_tuple(self):
        if self.width == 0 or self.height == 0:
            return (0, 0, 0, 0)
        return (self.x, self.y, self.width, self.height)

def clamp(x, minimum, maximum):
    return max(minimum, min(x, maximum))

def camera_view_bounds_2d(scene, cam_ob, me_ob):
    """
    Returns camera space bounding box of mesh object.
    Negative 'z' value means the point is behind the camera.
    Takes shift-x/y, lens angle and sensor size into account
    as well as perspective/ortho projections.
    :arg scene: Scene to use for frame size.
    :type scene: :class:`bpy.types.Scene`
    :arg obj: Camera object.
    :type obj: :class:`bpy.types.Object`
    :arg me: Untransformed Mesh.
    :type me: :class:`bpy.types.Mesh´
    :return: a Box object (call its to_tuple() method to get x, y, width and height)
    :rtype: :class:`Box`
    """

    mat = cam_ob.matrix_world.normalized().inverted()
    me = me_ob.to_mesh(scene, True, 'PREVIEW')
    me.transform(me_ob.matrix_world)
    me.transform(mat)

    camera = cam_ob.data
    frame = [-v for v in camera.view_frame(scene=scene)[:3]]
    camera_persp = camera.type != 'ORTHO'

    lx = []
    ly = []

    for v in me.vertices:
        co_local = v.co
        z = -co_local.z

        if camera_persp:
            if z == 0.0:
                lx.append(0.5)
                ly.append(0.5)
            # Does it make any sense to drop these?
            #if z <= 0.0:
            #    continue
            else:
                frame = [(v / (v.z / z)) for v in frame]

        min_x, max_x = frame[1].x, frame[2].x
        min_y, max_y = frame[0].y, frame[1].y

        x = (co_local.x - min_x) / (max_x - min_x)
        y = (co_local.y - min_y) / (max_y - min_y)

        lx.append(x)
        ly.append(y)

    min_x = clamp(min(lx), 0.0, 1.0)
    max_x = clamp(max(lx), 0.0, 1.0)
    min_y = clamp(min(ly), 0.0, 1.0)
    max_y = clamp(max(ly), 0.0, 1.0)

    bpy.data.meshes.remove(me)

    r = scene.render
    fac = r.resolution_percentage * 0.01
    dim_x = r.resolution_x * fac
    dim_y = r.resolution_y * fac

    return Box(min_x, min_y, max_x, max_y, dim_x, dim_y)
'''
Produce AVI video for stimuli
'''
def produce_video(camera_position,type_bird, colition,final_frame,L, bird_position = (14.15445,23.74561,4.82148),FPS = 24.0):

	import bpy
	import pickle
	import math
	import random
	import mathutils

	def look_at(obj_camera, point):
	    loc_camera = obj_camera.matrix_world.to_translation()
	    direction = point - loc_camera
	    # point the cameras '-Z' and use its 'Y' as up
	    rot_quat = direction.to_track_quat('-Z', 'Y')
	    # assume we're using euler rotation
	    obj_camera.rotation_euler = rot_quat.to_euler()
	    obj_camera.keyframe_insert(data_path ='Rotation',group="LocRot")

	def get_finalposition(camera,L):
		vec = mathutils.Vector((L*math.sin(math.pi*random.uniform(0,1),0.0,L*math.cos(math.pi*random.uniform(0,1)))))
		inv = camera.matrix_world.copy()
		inv.invert()
		# vec aligned to local axis
		vec_rot = vec * inv
		camera_new_location = camera.location + vec_rot
		return camera_new_location

	if type_bird == 1:
		filepath = "/home/josue/Desktop/Blender_trial/Owl.blend"
		group_name = "Owl"
	elif type_bird == 2:
		filepath = "/home/josue/Desktop/Blender_trial/Guacamaya-2013fb24.blend"
		group_name = "G-Guacamaya"
	elif type_bird == 0:
		filepath = "/home/josue/Desktop/Blender_trial/Quetzal-2013mr07.blend"
		group_name = "Quetzal"

	# append, set to true to keep the link to the original file
	link = False

	# append all groups from the .blend file
	with bpy.data.libraries.load(filepath, link=link) as (data_src, data_dst):
	    ## all groups
	    # data_to.groups = data_from.groups

	    # only append a single group we already know the name of
	    data_dst.groups = [group_name]

	# add the group instance to the scene
	scene = bpy.context.scene
	scene.frame_end = final_frame
	obj_camera = bpy.data.objects["Camera"]
	for group in data_dst.groups:
		ob = bpy.data.objects.new(group.name, None)
		ob.dupli_group = group
		ob.dupli_type = 'GROUP'
		scene.objects.link(ob)
	    #look_at(ob, obj_camera.matrix_world.to_translation())

		#obj_camera.select = True
		#ob.select = True
		ob.select = True
		bpy.context.scene.frame_set(1)
          if colition == 1:
               look_at(obj_camera,ob.location)
		if type_bird == 1:
	    		ob.scale = (0.4,0.4,0.4)
	    		ob.location = bird_position
	    		ob.keyframe_insert(data_path ='location',group="LocRot")

		bpy.context.scene.frame_set(final_frame)
		if colition == 1:
	    		ob.location = tuple(obj_camera.location)
		else:
			ob.location = get_finalposition(obj_camera,L)

		ob.keyframe_insert(data_path ='location',group='LocRot')



	ob.select = True
	obj_camera.select = True
	distances = []

	for fr in range(1, 115):
		bpy.context.scene.frame_set(fr)
		lst = []
		for obj in bpy.context.selected_objects:  # iterate over the selection NOTE: two object should be selected
	     	   lst.append(obj.location)  # populate the lst with the location info
		# calulate the distance of the two objects
		#tuple_position = camera_view_bounds_2d(scene, obj_camera,ob)
		#print(tuple_position)
		distance = math.sqrt((lst[0][0] - lst[1][0])**2 + (lst[0][1] - lst[1][1])**2 + (lst[0][2] - lst[1][2])**2)
		distances.append(distance)


	#Save distance to the camera for further analysis
	f = open('data_{}_{}_{}.pkl'.format(type_bird,object_velocity,colition,'wb')
	pickle.dump(distances,f,2)
	f.close()
	object_velocity = float(distances[0])/float((float(final_frame)/float(FPS)))
	bpy.data.scenes["Scene"].frame_end = final_frame
	bpy.data.scenes["Scene"].render.fps = FPS
	bpy.data.scenes["Scene"].render.image_settings.file_format = 'AVI_JPEG'
	bpy.data.scenes["Scene"].render.filepath = '/home/josue/looming_stimuli_{}_{}_{}.avi'.format(type_bird,object_velocity,colition)
	bpy.ops.render.render( animation=True )



produce_video(camera_position = (4.15445,13.74561,-4.82148), bird_position = (14.15445,23.74561,4.82148),FPS = 24.0,type_bird=1, colition=1,final_frame=115,L=2)
