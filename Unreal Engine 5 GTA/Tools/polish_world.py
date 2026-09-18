import unreal,json,pathlib,traceback
R=pathlib.Path(unreal.Paths.project_dir()).resolve()
try:
 w=unreal.EditorLoadingAndSavingUtils.load_map('/Game/GTA/Maps/PortMeridian')
 sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 for a in sub.get_all_level_actors():
  if isinstance(a,(unreal.DirectionalLight,unreal.SkyLight,unreal.SkyAtmosphere,unreal.ExponentialHeightFog,unreal.PostProcessVolume)):
   a.set_editor_property('is_spatially_loaded',False)
  if isinstance(a,unreal.PostProcessVolume):
   s=a.get_editor_property('settings')
   for n,v in [('override_auto_exposure_min_brightness',True),('override_auto_exposure_max_brightness',True),('auto_exposure_min_brightness',-2.0),('auto_exposure_max_brightness',15.0),('override_auto_exposure_bias',True),('auto_exposure_bias',.65),('override_auto_exposure_speed_up',True),('override_auto_exposure_speed_down',True),('auto_exposure_speed_up',5.0),('auto_exposure_speed_down',5.0)]:
    s.set_editor_property(n,v)
   a.set_editor_property('settings',s)
  if isinstance(a,unreal.DirectionalLight):a.get_component_by_class(unreal.DirectionalLightComponent).set_intensity(50000)
  if isinstance(a,unreal.SkyLight):
   c=a.get_component_by_class(unreal.SkyLightComponent)
   c.set_editor_property('lower_hemisphere_is_black',False)
   c.set_editor_property('min_occlusion',.18);c.set_intensity(1.25)
 for name in ['SK_Citizen','SM_Tower','SM_Sedan','SM_Tree0','SM_Asphalt']:
  m=unreal.EditorAssetLibrary.load_asset('/Game/GTA/Generated/'+name)
  slots=m.get_editor_property('materials' if name.startswith('SK_') else 'static_materials')
  data=[{'slot':str(s.get_editor_property('imported_material_slot_name')),'material':str(s.get_editor_property('material_interface'))} for s in slots]
  unreal.log('PM_MATERIALS '+name+' '+json.dumps(data))
 unreal.EditorLoadingAndSavingUtils.save_map(w,'/Game/GTA/Maps/PortMeridian')
 unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 unreal.log('PM_LIGHTING_SUCCESS')
except Exception:unreal.log_error(traceback.format_exc())
finally:unreal.SystemLibrary.quit_editor()
