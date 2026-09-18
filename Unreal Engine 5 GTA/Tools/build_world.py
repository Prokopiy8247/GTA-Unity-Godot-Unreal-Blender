import unreal, pathlib, traceback, json
ROOT=pathlib.Path(unreal.Paths.project_dir()).resolve()
MAP='/Game/GTA/Maps/PortMeridian'
def log(x):unreal.log('PM_WORLD_BUILD '+str(x))
def prop(obj,name,value):
    try:obj.set_editor_property(name,value)
    except Exception as e:log('Optional property '+name+': '+str(e))
try:
    level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    assert level is not None and actors is not None,'Full editor subsystems required'
    assert level.new_level(MAP,True),'Cannot create World Partition map'
    world=unreal.EditorLevelLibrary.get_editor_world()
    for a in list(actors.get_all_level_actors()):
        n=a.get_class().get_name()
        if n not in ['WorldSettings','WorldDataLayers','WorldPartitionMiniMap']:
            actors.destroy_actor(a)
    settings=world.get_world_settings()
    prop(settings,'default_game_mode',unreal.load_class(None,'/Script/Unreal_GTA.PMGameMode'))
    prop(settings,'kill_z',-30000)
    wp=settings.get_editor_property('world_partition')
    if wp:
        log('WorldPartition '+str(wp))
        prop(wp,'enable_streaming',True)
        try:
            rh=wp.get_editor_property('runtime_hash');log('Runtime hash '+str(rh))
            grids=rh.get_editor_property('grids')
            for g in grids:g.set_editor_property('cell_size',25000);g.set_editor_property('loading_range',85000)
            rh.set_editor_property('grids',grids)
        except Exception as e:log('Grid tuning: '+str(e))
    def spawn(cls,name,p=(0,0,0),r=(0,0,0)):
        a=actors.spawn_actor_from_class(cls,unreal.Vector(*p),unreal.Rotator(*r));a.set_actor_label(name);return a
    sun=spawn(unreal.DirectionalLight,'Meridian_Sun',(0,0,10000),(-35,-45,0))
    light=sun.get_component_by_class(unreal.DirectionalLightComponent)
    light.set_mobility(unreal.ComponentMobility.MOVABLE);prop(light,'atmosphere_sun_light',True);light.set_intensity(7)
    prop(light,'dynamic_shadow_distance_movable_light',30000)
    sky=spawn(unreal.SkyAtmosphere,'Meridian_Atmosphere')
    sky_light=spawn(unreal.SkyLight,'Meridian_Skylight',(0,0,15000))
    sc=sky_light.get_component_by_class(unreal.SkyLightComponent);sc.set_mobility(unreal.ComponentMobility.MOVABLE);sc.set_intensity(.85);prop(sc,'real_time_capture',True)
    fog=spawn(unreal.ExponentialHeightFog,'Coastal_Haze')
    fc=fog.get_component_by_class(unreal.ExponentialHeightFogComponent);fc.set_fog_density(.0025);prop(fc,'enable_volumetric_fog',True)
    pp=spawn(unreal.PostProcessVolume,'Meridian_Grade')
    prop(pp,'unbound',True)
    ps=pp.get_editor_property('settings')
    for n,v in [('override_auto_exposure_min_brightness',True),('override_auto_exposure_max_brightness',True),('auto_exposure_min_brightness',.35),('auto_exposure_max_brightness',1.5),('override_auto_exposure_bias',True),('auto_exposure_bias',0.0),('override_bloom_intensity',True),('bloom_intensity',.22),('override_motion_blur_amount',True),('motion_blur_amount',.12),('override_vignette_intensity',True),('vignette_intensity',.17)]:
        prop(ps,n,v)
    pp.set_editor_property('settings',ps)
    player=spawn(unreal.PlayerStart,'Free_Roam_Start',(0,-650,190),(0,15,0))
    manager=spawn(unreal.load_class(None,'/Script/Unreal_GTA.PMWorld'),'Port_Meridian_World')
    prop(manager,'is_spatially_loaded',False)
    unreal.PMEditorLibrary.configure_world(manager)
    Sector=unreal.load_class(None,'/Script/Unreal_GTA.PMSector')
    count=0
    for gx in range(-8,8):
        for gy in range(-8,9):
            a=spawn(Sector,'District_%+03d_%+03d'%(gx,gy),(gx*25000,gy*25000,0))
            a.set_editor_property('grid_x',gx);a.set_editor_property('grid_y',gy);a.generate()
            prop(a,'is_spatially_loaded',True)
            count+=1
        log('Sectors '+str(count))
    # Landmark signs are original project text and remain legible in world space.
    for text,p,rot in [
        ('MERIDIAN SUPPLY',(4200,3270,400),-90),
        ('COVE HOUSE',(9650,3680,280),-90),
        ('FOUNDRY MOTORWORKS',(4200,-5700,430),-90),
        ('PORT MERIDIAN',(123000,-49300,1100),-90),
        ('MERIDIAN AIRFIELD',(-174000,-79000,600),-90)]:
        t=spawn(unreal.TextRenderActor,text,p,(0,rot,0));c=t.get_component_by_class(unreal.TextRenderComponent)
        c.set_text(text);c.set_world_size(75);c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER);c.set_text_render_color(unreal.Color(202,224,221,255))
    for p in [(1100,1100,790),(1100,-3900,790),(6100,1100,790),(-3900,1100,790),(4200,3100,340)]:
        a=spawn(unreal.PointLight,'Street_LED',p);c=a.get_component_by_class(unreal.PointLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity(2500);c.set_attenuation_radius(1400);c.set_cast_shadows(False)
    # Data composition Blueprints expose the native runtime classes without graph wiring.
    for name,parent in [('BP_MeridianPlayer','PMPlayer'),('BP_MeridianVehicle','PMVehicle'),('BP_MeridianCitizen','PMHuman')]:
        path='/Game/GTA/Blueprints/'+name
        if not unreal.EditorAssetLibrary.does_asset_exist(path):
            factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.load_class(None,'/Script/Unreal_GTA.'+parent))
            bp=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/GTA/Blueprints',unreal.Blueprint,factory)
            unreal.BlueprintEditorLibrary.compile_blueprint(bp);unreal.EditorAssetLibrary.save_loaded_asset(bp)
    assert unreal.EditorLoadingAndSavingUtils.save_map(world,MAP),'Map save failed'
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    (ROOT/'.astra-run/world_build.json').write_text(json.dumps({'map':MAP,'sectors':count,'size_m':[4000,4250],'world_partition':bool(wp)},indent=2))
    log('SUCCESS '+str(count)+' sectors')
except Exception:
    unreal.log_error(traceback.format_exc())
finally:
    unreal.SystemLibrary.quit_editor()
