bl_info = {
	"name": "VF Planar UV",
	"author": "John Einselen - Vectorform LLC",
	"version": (0, 4, 1),
	"blender": (2, 80, 0),
	"location": "Scene > VF Tools > Planar UV",
	"description": "Numerical planar projection of 3D meshes into UV space",
	"warning": "inexperienced developer, use at your own risk",
	"wiki_url": "",
	"tracker_url": "",
	"category": "3D View"}

# Based in part on basic code found here:
# https://blenderartists.org/t/set-face-uv-coordinates-while-in-edit-mode/1317947
# https://blender.stackexchange.com/questions/9399/add-uv-layer-to-mesh-add-uv-coords-with-python
# https://blender.stackexchange.com/questions/30421/create-a-radio-button-via-python
# https://gifguide2code.com/2017/05/14/python-how-to-loop-through-every-vertex-in-a-mesh/

import bpy
import bmesh

###########################################################################
# Main class

class vf_planar_uv(bpy.types.Operator):
	bl_idname = "vfplanaruv.set"
	bl_label = "Set UV Map"
	bl_description = "Numerical planar projection of 3D meshes into UV space"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		if not bpy.context.view_layer.objects.active.data.vertices:
			return {'CANCELLED'}

		# Set up local variables
		axis = bpy.context.scene.vf_planar_uv_settings.projection_axis
		rotation = bpy.context.scene.vf_planar_uv_settings.projection_rotation
		flip = float(bpy.context.scene.vf_planar_uv_settings.projection_flip)
		align = float(bpy.context.scene.vf_planar_uv_settings.projection_align)
		centre = bpy.context.scene.vf_planar_uv_settings.projection_centre
		size = bpy.context.scene.vf_planar_uv_settings.projection_size

		# Prevent divide by zero errors
		size[0] = size[0] if size[0] > 0.0 else 1.0
		size[1] = size[1] if size[1] > 0.0 else 1.0
		size[2] = size[2] if size[2] > 0.0 else 1.0

		# Save current mode
		mode = bpy.context.active_object.mode
		# Switch to edit mode
		bpy.ops.object.mode_set(mode='EDIT')

		# Get object
		obj = bpy.context.active_object
		bm = bmesh.from_edit_mesh(obj.data)
		# Get UV map
		uv_layer = bm.loops.layers.uv.verify()

		# Loop through faces
		U = 0.0
		V = 0.0
		for f in bm.faces:
			if f.select:
				for l in f.loops:
					# Process input coordinates
					pos = l.vert.co.copy()
					pos[0] = (pos[0] - centre[0]) / size[0]
					pos[1] = (pos[1] - centre[1]) / size[1]
					pos[2] = (pos[2] - centre[2]) / size[2]

					# Projection Axis
					if axis == "X":
						U = pos[1]
						V = pos[2]
					elif axis == "Y":
						U = pos[0]
						V = pos[2]
					else:
						U = pos[0]
						V = pos[1]

					# Projection Rotation
					if "YX" in rotation:
						U, V = V, U
						U *= -1.0
					if "-" in rotation:
						U *= -1.0
						V *= -1.0

					# Projection Flip
					U *= flip

					# Set UV map values with image centre or zero point alignment
					l[uv_layer].uv = (U + align, V + align)

		# Update mesh
		bmesh.update_edit_mesh(obj.data)

		# Reset object mode to original
		bpy.ops.object.mode_set(mode=mode)

		# Done
		return {'FINISHED'}

class vf_load_selection(bpy.types.Operator):
	bl_idname = "vfloadselection.set"
	bl_label = "Load Selection"
	bl_description = "Set the Centre and Size variables to the bounding box properties of the selected geometry"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		if not bpy.context.view_layer.objects.active.data.vertices:
			return {'CANCELLED'}

		# Save current mode
		mode = bpy.context.active_object.mode
		# Switch to edit mode
		bpy.ops.object.mode_set(mode='EDIT')

		# Loop through selected vertices
#		mesh = bpy.context.active_object.data
		# Undoing after using the active object data method causes a segmentation fault in Blender 3.3.x
		obj = bpy.context.active_object
		mesh = bmesh.from_edit_mesh(obj.data)
		minX = False
		minY = False
		minZ = False
		maxX = False
		maxY = False
		maxZ = False
#		for vert in mesh.vertices:
		for vert in mesh.verts:
			if vert.select:
				minX = min(minX, vert.co.x) if minX else vert.co.x
				minY = min(minY, vert.co.y) if minY else vert.co.y
				minZ = min(minZ, vert.co.z) if minZ else vert.co.z
				maxX = max(maxX, vert.co.x) if maxX else vert.co.x
				maxY = max(maxY, vert.co.y) if maxY else vert.co.y
				maxZ = max(maxZ, vert.co.z) if maxZ else vert.co.z

		# Calculate bounding box and centre point
		boundX = maxX-minX
		boundY = maxY-minY
		boundZ = maxZ-minZ
		centrX = minX+(boundX*0.5)
		centrY = minY+(boundY*0.5)
		centrZ = minZ+(boundZ*0.5)

		# Prevent zero scale entries
		boundX = boundX if boundX > 0.0 else 1.0
		boundY = boundY if boundY > 0.0 else 1.0
		boundZ = boundZ if boundZ > 0.0 else 1.0

		# Set local variables
		bpy.context.scene.vf_planar_uv_settings.projection_centre[0] = centrX
		bpy.context.scene.vf_planar_uv_settings.projection_centre[1] = centrY
		bpy.context.scene.vf_planar_uv_settings.projection_centre[2] = centrZ
		bpy.context.scene.vf_planar_uv_settings.projection_size[0] = boundX
		bpy.context.scene.vf_planar_uv_settings.projection_size[1] = boundY
		bpy.context.scene.vf_planar_uv_settings.projection_size[2] = boundZ

		# Reset object mode to original
		bpy.ops.object.mode_set(mode=mode)

		# Done
		return {'FINISHED'}

###########################################################################
# Project settings and UI rendering classes

class vfPlanarUvSettings(bpy.types.PropertyGroup):
	projection_axis: bpy.props.EnumProperty(
		name='Axis',
		description='Planar projection axis',
		items=[
			('X', 'X', 'X axis projection'),
			('Y', 'Y', 'Y axis projection'),
			('Z', 'Z', 'Z axis projection')
			],
		default='X')
	projection_centre: bpy.props.FloatVectorProperty(
		name="Centre",
		description="Centre of the planar projection mapping area",
		subtype="TRANSLATION",
		default=[0.0, 0.0, 0.0],
		step=1.25,
		precision=3)
	projection_size: bpy.props.FloatVectorProperty(
		name="Size",
		description="Size of the planar projection mapping area",
		subtype="TRANSLATION",
		default=[1.0, 1.0, 1.0],
		step=1.25,
		precision=3)
	projection_rotation: bpy.props.EnumProperty(
		name='Rotation',
		description='Planar projection axis',
		items=[
			('+XY', '0°', 'XY orientation projection'),
			('+YX', '90', 'YX orientation projection'),
			('-XY', '180', '-XY orientation projection'),
			('-YX', '270', '-YX orientation projection')
			],
		default='+XY')
	projection_flip: bpy.props.EnumProperty(
		name='Flip',
		description='Planar projection axis',
		items=[
			('1.0', 'Front', 'Projection from positive direction'),
			('-1.0', 'Back', 'Projection from negative direction')
			],
		default='1.0')
	projection_align: bpy.props.EnumProperty(
		name='Alignment',
		description='UV map alignment',
		items=[
			('0.5', 'Image', 'Align mapped geometry centre to UV 0.5, 0.5'),
			('0.0', 'Zero', 'Align mapped geometry centre to UV 0.0, 0.0')
			],
		default='0.5')

class VFTOOLS_PT_planar_uv(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = 'VF Tools'
	bl_order = 10
	bl_options = {'DEFAULT_CLOSED'}
	bl_label = "Planar UV"
	bl_idname = "VFTOOLS_PT_planar_uv"

	@classmethod
	def poll(cls, context):
		return True

	def draw_header(self, context):
		try:
			layout = self.layout
		except Exception as exc:
			print(str(exc) + " | Error in VF Planar UV panel header")

	def draw(self, context):
		try:
			layout = self.layout
			layout.use_property_split = True
			layout.use_property_decorate = False # No animation
			layout.prop(context.scene.vf_planar_uv_settings, 'projection_axis', expand=True)

			col=layout.column()
			col.prop(context.scene.vf_planar_uv_settings, 'projection_centre')
			col.prop(context.scene.vf_planar_uv_settings, 'projection_size')

			layout.prop(context.scene.vf_planar_uv_settings, 'projection_rotation', expand=True)
			layout.prop(context.scene.vf_planar_uv_settings, 'projection_flip', expand=True)
			layout.prop(context.scene.vf_planar_uv_settings, 'projection_align', expand=True)

			if bpy.context.view_layer.objects.active and bpy.context.view_layer.objects.active.type == "MESH":
				col.operator(vf_load_selection.bl_idname)
				layout.operator(vf_planar_uv.bl_idname)
			else:
				box = layout.box()
				box.label(text="Active object must be a mesh with selected polygons")
		except Exception as exc:
			print(str(exc) + " | Error in VF Planar UV panel")

classes = (vf_planar_uv, vf_load_selection, vfPlanarUvSettings, VFTOOLS_PT_planar_uv)

###########################################################################
# Addon registration functions

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.vf_planar_uv_settings = bpy.props.PointerProperty(type=vfPlanarUvSettings)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.vf_planar_uv_settings

if __name__ == "__main__":
	register()