import unreal,pathlib,json,traceback
root=pathlib.Path(unreal.Paths.project_dir()).resolve();ea=unreal.EditorAssetLibrary
try:
 unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
 names=['SM_Tree0','SM_Tree1','SM_Tree2']
 manifest=json.loads((root/'SourceAssets/manifest.json').read_text())
 for name in names:
  sk=name.startswith('SK_');old=ea.load_asset('/Game/GTA/Generated/'+name);ui=unreal.FbxImportUI()
  ui.set_editor_property('automated_import_should_detect_type',False);ui.import_as_skeletal=sk;ui.import_mesh=True;ui.import_materials=False;ui.import_textures=False;ui.import_animations=False
  ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH if sk else unreal.FBXImportType.FBXIT_STATIC_MESH
  if sk:ui.skeleton=old.get_editor_property('skeleton');ui.create_physics_asset=False;ui.physics_asset=old.get_editor_property('physics_asset')
  else:ui.static_mesh_import_data.combine_meshes=True;ui.static_mesh_import_data.auto_generate_collision=True
  task=unreal.AssetImportTask();task.filename=str(root/'SourceAssets/BlenderExports'/(name+'.fbx'));task.destination_path='/Game/GTA/Generated';task.destination_name=name;task.automated=True;task.replace_existing=True;task.options=ui;task.save=True;task.factory=unreal.FbxFactory()
  unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
  mesh=ea.load_asset('/Game/GTA/Generated/'+name);slots=mesh.get_editor_property('materials' if sk else 'static_materials')
  for i,slot in enumerate(slots):
   mn=str(slot.get_editor_property('imported_material_slot_name'))
   path='/Game/GTA/Materials/MI_'+mn
   if ea.does_asset_exist(path):
    mat=ea.load_asset(path)
    if sk:
     slot.set_editor_property('material_interface',mat);slots[i]=slot
    else:mesh.set_material(i,mat)
  if sk:mesh.set_editor_property('materials',slots)
  ns=mesh.get_editor_property('nanite_settings');ns.enabled=True;mesh.set_editor_property('nanite_settings',ns)
  ea.save_loaded_asset(mesh)
 unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 unreal.log('PM_ART_UPDATE_SUCCESS')
except Exception:unreal.log_error(traceback.format_exc())
finally:unreal.SystemLibrary.quit_editor()
