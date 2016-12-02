def produce_video(camera_position, bird_position = (14.15445,23.74561,4.82148),FPS = 24.0,type_bird, colition,final_frame,L):

	import bpy
	import pickle
	from math import * 
	import numpy
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
		vec = mathutils.Vector((L*sin(pi*numpy.random.uniform(1),0.0,L*cos(pi*numpy.random.uniform(1)))))
		inv = camera.matrix_world.copy()
		inv.invert()
		# vec aligned to local axis
		vec_rot = vec * inv
		camera_new_location = cube.location + vec_rot
		return camera_new_location

	if type_bird = 1:
		filepath = "/home/josue/Desktop/Blender_trial/Owl.blend"
		group_name = "Owl"
	elif type_bird = 2:
		filepath = "/home/josue/Desktop/Blender_trial/Guacamaya-2013fb24.blend"
		group_name = "G-Guacamaya"
	elif type_bird = 0:
		fileparh = "/home/josue/Desktop/Blender_trial/Quetzal-2013mr07.blend"
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
	    if type_bird = 1:
	    	ob.scale = (0.4,0.4,0.4)
	    ob.location = bird_position
	    ob.keyframe_insert(data_path ='location',group="LocRot")

	    bpy.context.scene.frame_set(final_frame)
	    if colition = 1:
	    	ob.location = tuple(obj_camera.location)
	    else:
		ob.location = get_finalposition(obj_camera,L)
	    ob.keyframe_insert(data_path ='location',group='LocRot')	
	    


	ob.select = True
	obj_camera = True
	distances = []

	for fr in range(1, 115): 
		bpy.context.scene.frame_set(fr) 
		lst = []
		for obj in bpy.context.selected_objects:  # iterate over the selection NOTE: two object should be selected
	     	   lst.append(obj.location)  # populate the lst with the location info
		# calulate the distance of the two objects
		distance = sqrt((lst[0][0] - lst[1][0])**2 + (lst[0][1] - lst[1][1])**2 + (lst[0][2] - lst[1][2])**2)
		distances.append(distance)


	#Save distance to the camera for further analysis	
	f = open('data.pkl','wb')
	pickle.dump(distances,f,2)
	f.close()
	object_velocity = float(distances[0])/float((float(final_frame)/float(FPS)))
	bpy.data.scenes["Scene"].frame_end = final_frame
	bpy.data.scenes["Scene"].render.fps = FPS
	bpy.data.scenes["Scene"].render.image_settings.file_format = 'AVI_JPEG' 
	py.data.scenes["Scene"].render.filepath = '/home/josue/looming_stimuli_{}_{}_{}.avi'.format(type_bird,object_velocity,looming)
	bpy.ops.render.render( animation=True ) 



