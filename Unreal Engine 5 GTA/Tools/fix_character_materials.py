import unreal,traceback
try:
 m=unreal.load_asset("/Game/GTA/Materials/M_Surface")
 m.set_editor_property("used_with_skeletal_mesh",True)
 m.set_editor_property("used_with_instanced_static_meshes",True)
 m.set_editor_property("used_with_nanite",True)
 unreal.MaterialEditingLibrary.recompile_material(m)
 unreal.EditorAssetLibrary.save_loaded_asset(m,False)
 for name in ['SK_Citizen','SK_CitizenF','SK_Police','SK_Tactical']:
  m=unreal.load_asset('/Game/GTA/Generated/'+name); slots=list(m.get_editor_property('materials'))
  for i,s in enumerate(slots):
   mn=str(s.get_editor_property('imported_material_slot_name'))
   mat=unreal.load_asset('/Game/GTA/Materials/MI_'+mn)
   if not mat: raise RuntimeError('Missing material '+mn)
   s.set_editor_property('material_interface',mat); slots[i]=s
  m.set_editor_property('materials',slots);unreal.EditorAssetLibrary.save_loaded_asset(m,False)
  unreal.log('PM_SK_MATERIALS '+name+' '+str([str(s.material_interface) for s in m.materials]))
 for name in ['SM_Tree0','SM_Tree1','SM_Tree2']:
  tree=unreal.load_asset('/Game/GTA/Generated/'+name);ns=tree.get_editor_property('nanite_settings');ns.set_editor_property('shape_preservation',unreal.NaniteShapePreservation.PRESERVE_AREA);tree.set_editor_property('nanite_settings',ns);unreal.EditorAssetLibrary.save_loaded_asset(tree,False)
 unreal.log('PM_SK_MATERIALS_SUCCESS')
except Exception:unreal.log_error(traceback.format_exc())
finally:unreal.SystemLibrary.quit_editor()
