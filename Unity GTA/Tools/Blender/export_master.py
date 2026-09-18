# Execute this whole file through blender_unity.execute_blender_code.
# Safe-mode compatible: no external Python execution or filesystem APIs in Blender.
import bpy
BASE=bpy.path.abspath('//').replace(chr(92),'/')
assert bpy.data.filepath.replace(chr(92),'/').endswith('/UnityGTA.blend')
lod_names=['OfficeTower','OfficeMid','Apartment','House','Warehouse','Hangar','Storefront','Parking','Oak','Palm','Rock']
for obj in bpy.context.scene.objects:
 obj.hide_set(False)
 obj.select_set(False)
count=0
for category in bpy.data.collections['GTA_UNITY'].children:
 for collection in category.children:
  if not collection.objects:
   continue
  objects=list(collection.objects)
  body=next((obj for obj in objects if obj.name.startswith('Body')),objects[0])
  anchor=body.location.copy()
  for obj in objects:
   obj.location-=anchor
   obj.select_set(True)
  bpy.context.view_layer.objects.active=body
  bpy.ops.export_scene.fbx(filepath=BASE+'Assets/GTA/Generated/Models/'+collection.name+'.fbx',use_selection=True,axis_forward='-Z',axis_up='Y',apply_scale_options='FBX_SCALE_ALL',bake_anim=False,add_leaf_bones=False)
  if collection.name in lod_names:
   modifiers=[]
   for obj in objects:
    mod=obj.modifiers.new('Export-only LOD','DECIMATE')
    mod.ratio=.28 if collection.name in ['Oak','Palm'] else .12
    modifiers.append((obj,mod))
   bpy.ops.export_scene.fbx(filepath=BASE+'Assets/GTA/Generated/LODs/'+collection.name+'.fbx',use_selection=True,axis_forward='-Z',axis_up='Y',apply_scale_options='FBX_SCALE_ALL',bake_anim=False,add_leaf_bones=False)
   for obj,mod in modifiers:obj.modifiers.remove(mod)
  for obj in objects:
   obj.location+=anchor
   obj.select_set(False)
  count+=1
bpy.ops.wm.save_as_mainfile(filepath=BASE+'UnityGTA.blend')
print('Canonical asset collections exported:',count)

