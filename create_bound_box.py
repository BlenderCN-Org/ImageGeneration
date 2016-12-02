'''
Create Bounding Box for the whole bird and then calculate the radius (Which is the L in the LGMD model)
'''
import bpy
import bmesh
from bpy.props import BoolProperty, FloatVectorProperty
import mathutils
from bpy_extras import object_utils

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

	return(((maxx-minx)/2) + ((maxz-minz)/2) +  ((maxy-miny)/2))/6.0)



