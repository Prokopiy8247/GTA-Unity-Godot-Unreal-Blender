import unreal,pathlib,json,traceback
ROOT=pathlib.Path(unreal.Paths.project_dir()).resolve()
EA=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();ME=unreal.MaterialEditingLibrary
def get(path):return EA.load_asset(path) if EA.does_asset_exist(path) else None
def expr(m,c,x=0,y=0):return ME.create_material_expression(m,c,x,y)
def link(a,p,b,q):ME.connect_material_expressions(a,p,b,q)
def log(s):unreal.log('PM_REPAIR '+str(s))
try:
    assert unreal.PMEditorLibrary.repair_characters()==4
    data=json.loads((ROOT/'SourceAssets/manifest.json').read_text())
    master=get('/Game/GTA/Materials/M_Surface')
    collection=get('/Game/GTA/Materials/MPC_Weather')
    if not collection:
        collection=AT.create_asset('MPC_Weather','/Game/GTA/Materials',unreal.MaterialParameterCollection,unreal.MaterialParameterCollectionFactoryNew())
        p=unreal.CollectionScalarParameter();p.set_editor_property('parameter_name','Wetness');p.set_editor_property('default_value',0)
        collection.set_editor_property('scalar_parameters',[p]);EA.save_loaded_asset(collection)
    wet=expr(master,unreal.MaterialExpressionCollectionParameter,-450,650);wet.set_editor_property('collection',collection);wet.set_editor_property('parameter_name','Wetness')
    rough=expr(master,unreal.MaterialExpressionScalarParameter,-450,550);rough.set_editor_property('parameter_name','Roughness');rough.set_editor_property('default_value',.6)
    lerp=expr(master,unreal.MaterialExpressionLinearInterpolate,-150,550);lerp.set_editor_property('const_b',.14)
    link(rough,'',lerp,'A');link(wet,'',lerp,'Alpha');ME.connect_material_property(lerp,'',unreal.MaterialProperty.MP_ROUGHNESS)
    ME.recompile_material(master);EA.save_loaded_asset(master)
    mats={}
    for name,d in data['materials'].items():
        path='/Game/GTA/Materials/MI_'+name;m=get(path)
        if not m:m=AT.create_asset('MI_'+name,'/Game/GTA/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
        ME.set_material_instance_parent(m,master)
        ME.set_material_instance_vector_parameter_value(m,'BaseColor',unreal.LinearColor(*d['color'],1))
        ME.set_material_instance_scalar_parameter_value(m,'Metallic',d['metal'])
        ME.set_material_instance_scalar_parameter_value(m,'Roughness',d['rough'])
        ME.set_material_instance_scalar_parameter_value(m,'Emissive',d['emit'])
        mats[name]=m;EA.save_loaded_asset(m)
    for name,d in data['assets'].items():
        mesh=get('/Game/GTA/Generated/'+name)
        if not mesh:raise RuntimeError(name+' missing')
        sk=name.startswith('SK_');slots=mesh.get_editor_property('materials' if sk else 'static_materials')
        for i,slot in enumerate(slots):
            name0=str(slot.get_editor_property('imported_material_slot_name'))
            if name0 not in mats:
                name0=next((n for n in d['materials'] if n.replace('.','_')==name0),d['materials'][i] if i<len(d['materials']) else '')
            if name0 in mats:
                if sk:slot.set_editor_property('material_interface',mats[name0])
                else:mesh.set_material(i,mats[name0])
        if sk:
            mesh.set_editor_property('materials',slots)
            assert mesh.get_editor_property('skeleton') is not None
            assert mesh.get_editor_property('physics_asset') is not None
            log(name+' skeleton + physics verified')
        EA.save_loaded_asset(mesh)
    world=unreal.EditorLoadingAndSavingUtils.load_map('/Game/GTA/Maps/PortMeridian')
    subsystem=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=subsystem.get_all_level_actors()
    context=next(a for a in actors if a.get_class().get_name()=='PMWorld')
    assert unreal.PMEditorLibrary.configure_world(context)
    for a in actors:
        if isinstance(a,unreal.ExponentialHeightFog):
            c=a.get_component_by_class(unreal.ExponentialHeightFogComponent);c.set_editor_property('enable_volumetric_fog',True)
    unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/GTA/Maps/PortMeridian')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    for name in ['Citizen','CitizenF','Police','Tactical']:
        for suffix in ['_Skeleton','_Physics']:
            assert EA.does_asset_exist('/Game/GTA/Generated/SK_'+name+suffix)
    log('SUCCESS characters, materials, streaming')
except Exception:unreal.log_error(traceback.format_exc())
finally:unreal.SystemLibrary.quit_editor()
