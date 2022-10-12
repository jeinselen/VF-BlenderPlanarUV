bl_info = {
	"name": "VF Planar UV",
	"author": "John Einselen - Vectorform LLC",
	"version": (0, 2),
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
		align = float(bpy.context.scene.vf_planar_uv_settings.projection_align)
		axis = bpy.context.scene.vf_planar_uv_settings.projection_axis
		centre = bpy.context.scene.vf_planar_uv_settings.projection_centre
		size = bpy.context.scene.vf_planar_uv_settings.projection_size

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
		for f in bm.faces:
			if f.select:
				for l in f.loops:
					pos = l.vert.co.copy()
					pos[0] = ((pos[0] - centre[0]) / size[0]) + align
					pos[1] = ((pos[1] - centre[1]) / size[1]) + align
					pos[2] = ((pos[2] - centre[2]) / size[2]) + align
					if axis == "X":
						l[uv_layer].uv = (pos[1], pos[2])
					elif axis == "Y":
						l[uv_layer].uv = (pos[0], pos[2])
					else:
						l[uv_layer].uv = (pos[0], pos[1])

		# Update mesh
		bmesh.update_edit_mesh(obj.data)

		# Reset object mode to original
		bpy.ops.object.mode_set(mode=mode)

		# Done
		return {'FINISHED'}

###########################################################################
# Project settings and UI rendering classes

class vfPlanarUvSettings(bpy.types.PropertyGroup):
	projection_align: bpy.props.EnumProperty(
		name='Alignment',
		description='UV map alignment',
		items=[
			('0.0', 'Zero', 'Align mapped geometry centre to UV 0.0, 0.0'),
			('0.5', 'Image', 'Align mapped geometry centre to UV 0.5, 0.5')
			],
		default='0.5')
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

class VFTOOLS_PT_planar_uv(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = 'VF Tools'
	bl_order = 0
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
			layout.prop(context.scene.vf_planar_uv_settings, 'projection_align', expand=True)
			layout.prop(context.scene.vf_planar_uv_settings, 'projection_axis', expand=True)

			col=layout.column()
			col.prop(context.scene.vf_planar_uv_settings, 'projection_centre')
			col.prop(context.scene.vf_planar_uv_settings, 'projection_size')

			if bpy.context.view_layer.objects.active and bpy.context.view_layer.objects.active.type == "MESH":
				layout.operator(vf_planar_uv.bl_idname)
			else:
				box = layout.box()
				box.label(text="Active object must be a mesh with selected polygons")
		except Exception as exc:
			print(str(exc) + " | Error in VF Planar UV panel")

classes = (vf_planar_uv, vfPlanarUvSettings, VFTOOLS_PT_planar_uv)

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