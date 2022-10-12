# VF Planar UV

Numerical planar projection of 3D meshes into UV space, allowing for accurate and replicable results instead of relying on Blender's "Project From View" (which is either non-repeatable by default or non-customisable in "orthographic" mode).

![screenshot of the Blender 3D view interface with the add-on installed, showing "FBX — Unity3D" selected](images/screenshot1.png)

## Installation and Usage

- Download [VF_planarUV.py](https://raw.githubusercontent.com/jeinselenVF/VF-BlenderPlanarUV/main/VF_planarUV.py)
- Open Blender Preferences and navigate to the "Add-ons" tab
- Install and enable the Add-on
- It will show up in the 3D view `VF Tools` tab

## Settings

![screenshot of the Blender 3D view interface with the add-on installed, showing "FBX — Unity3D" selected](images/screenshot2.png)

- `Alignment` Determines how the mesh will be aligned to UV space, either:
  - `Zero` for raw data usage where standard UV mapping principles may not apply, and the centre of the defined are should align to 0.0, 0.0 in UV space
  - `Image` for standard UV map usage where the centre of the defined area will be aligned to 0.5, 0.5 in UV space
- `Axis` Sets the direction of the planar projection: `X`, `Y`, or `Z`
- `Centre` Sets the centre point of the projection space, allowing for any specific location to be focused on
- `Size` defines the scale of the projection, allowing for known numerical translation from object space into UV space

Note that this add-on operates in _**object space,**_ not _**world space.**_ Planar projection settings `centre` and `size` will not take into account the object's position, rotation, or scale in world space.

This software is provided without guarantee or warranty.