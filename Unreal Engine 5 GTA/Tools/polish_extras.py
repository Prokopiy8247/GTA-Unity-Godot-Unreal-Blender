import unreal,pathlib,traceback
root=pathlib.Path(unreal.Paths.project_dir()).resolve()
ea=unreal.EditorAssetLibrary;me=unreal.MaterialEditingLibrary
try:
 unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
 for name in ['SM_Suppressor','SM_Foregrip','SM_ExtendedMagazine']:
  ui=unreal.FbxImportUI();ui.automated_import_should_detect_type=False;ui.import_as_skeletal=False;ui.import_materials=False;ui.import_textures=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;ui.static_mesh_import_data.combine_meshes=True
  t=unreal.AssetImportTask();t.filename=str(root/'SourceAssets/BlenderExports'/(name+'.fbx'));t.destination_path='/Game/GTA/Generated';t.destination_name=name;t.automated=True;t.replace_existing=True;t.options=ui;t.factory=unreal.FbxFactory()
  unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
  m=unreal.load_asset('/Game/GTA/Generated/'+name)
  for i,s in enumerate(m.static_materials):m.set_material(i,unreal.load_asset('/Game/GTA/Materials/MI_'+str(s.get_editor_property('imported_material_slot_name'))))
  ea.save_loaded_asset(m,False)
 name='M_BayWater';m=unreal.load_asset('/Game/GTA/Materials/'+name) if ea.does_asset_exist('/Game/GTA/Materials/'+name) else unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/GTA/Materials',unreal.Material,unreal.MaterialFactoryNew())
 me.delete_all_material_expressions(m)
 def ex(cls):return me.create_material_expression(m,cls)
 def link(a,b,p):
  if not me.connect_material_expressions(a,'',b,p):
   assert me.connect_material_expressions(a,'',b,''),'Unconnected input '+str(b.get_class().get_name())+' '+p
 def num(v):
  n=ex(unreal.MaterialExpressionConstant);n.r=v;return n
 def mul(a,b):
  n=ex(unreal.MaterialExpressionMultiply);link(a,n,'A');link(b,n,'B');return n
 def add(a,b):
  n=ex(unreal.MaterialExpressionAdd);link(a,n,'A');link(b,n,'B');return n
 def append(a,b):
  n=ex(unreal.MaterialExpressionAppendVector);link(a,n,'A');link(b,n,'B');return n
 color=ex(unreal.MaterialExpressionConstant3Vector);color.constant=unreal.LinearColor(.014,.09,.13,1);me.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
 me.connect_material_property(num(.48),'',unreal.MaterialProperty.MP_METALLIC);me.connect_material_property(num(.19),'',unreal.MaterialProperty.MP_ROUGHNESS)
 pos=ex(unreal.MaterialExpressionWorldPosition);tm=ex(unreal.MaterialExpressionTime);waves=[]
 for channel,freq,vel in [('r',.035,.2),('g',.046,.16)]:
  mask=ex(unreal.MaterialExpressionComponentMask);mask.set_editor_property('r',channel=='r');mask.set_editor_property('g',channel=='g');mask.set_editor_property('b',False);mask.set_editor_property('a',False);link(pos,mask,'Input')
  phase=add(mul(mask,num(freq)),mul(tm,num(vel)))
  si=ex(unreal.MaterialExpressionSine);link(phase,si,'Input');waves.append(mul(si,num(.12)))
 normal=append(append(waves[0],waves[1]),num(1))
 norm=ex(unreal.MaterialExpressionNormalize);link(normal,norm,'VectorInput');me.connect_material_property(norm,'',unreal.MaterialProperty.MP_NORMAL)
 m.set_editor_property('used_with_instanced_static_meshes',True);m.set_editor_property('two_sided',True);me.recompile_material(m);ea.save_loaded_asset(m,False)
 water=unreal.load_asset('/Game/GTA/Generated/SM_Water');water.set_material(0,m);ea.save_loaded_asset(water,False)
 w=unreal.EditorLoadingAndSavingUtils.load_map('/Game/GTA/Maps/PortMeridian');sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 for a in sub.get_all_level_actors():
  if isinstance(a,unreal.PlayerStart):a.set_actor_location(unreal.Vector(1250,-1600,160),False,True);a.set_editor_property('is_spatially_loaded',False)
  if isinstance(a,unreal.PointLight) and a.get_actor_label().startswith('Street_LED'):sub.destroy_actor(a)
  if isinstance(a,unreal.PostProcessVolume):
   s=a.get_editor_property('settings');s.auto_exposure_bias=.15;a.set_editor_property('settings',s)
 clouds=[a for a in sub.get_all_level_actors() if isinstance(a,unreal.VolumetricCloud)]
 if not clouds:
  a=sub.spawn_actor_from_class(unreal.VolumetricCloud,unreal.Vector(0,0,0));a.set_actor_label('Meridian_Clouds');a.set_editor_property('is_spatially_loaded',False)
  c=a.get_component_by_class(unreal.VolumetricCloudComponent);c.set_editor_property('material',unreal.load_asset('/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst'))
  c.set_editor_property('layer_bottom_altitude',2.0);c.set_editor_property('layer_height',5.0)
 unreal.EditorLoadingAndSavingUtils.save_map(w,'/Game/GTA/Maps/PortMeridian');unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 unreal.log('PM_EXTRAS_SUCCESS')
except Exception:unreal.log_error(traceback.format_exc())
finally:unreal.SystemLibrary.quit_editor()
