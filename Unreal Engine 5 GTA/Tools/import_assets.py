import unreal, json, pathlib, traceback
ROOT = pathlib.Path(unreal.Paths.project_dir()).resolve()
MANIFEST=json.loads((ROOT/'SourceAssets/manifest.json').read_text())
EA=unreal.EditorAssetLibrary
AT=unreal.AssetToolsHelpers.get_asset_tools()
ME=unreal.MaterialEditingLibrary
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
def log(x): unreal.log('PM_IMPORT '+str(x))
def asset(name,path,cls,factory):
    a=EA.load_asset(path+'/'+name) if EA.does_asset_exist(path+'/'+name) else None
    return a or AT.create_asset(name,path,cls,factory)
def expr(material,cls,x=0,y=0): return ME.create_material_expression(material,cls,x,y)
def connect(a,p,b,q): ME.connect_material_expressions(a,p,b,q)
def material_master():
    m=asset('M_Surface','/Game/GTA/Materials',unreal.Material,unreal.MaterialFactoryNew())
    ME.delete_all_material_expressions(m)
    color=expr(m,unreal.MaterialExpressionVectorParameter,-700,0);color.set_editor_property('parameter_name','BaseColor');color.set_editor_property('default_value',unreal.LinearColor(.3,.3,.3,1))
    rough=expr(m,unreal.MaterialExpressionScalarParameter,-300,180);rough.set_editor_property('parameter_name','Roughness');rough.set_editor_property('default_value',.6)
    metal=expr(m,unreal.MaterialExpressionScalarParameter,-300,280);metal.set_editor_property('parameter_name','Metallic');metal.set_editor_property('default_value',0)
    emit=expr(m,unreal.MaterialExpressionScalarParameter,-500,440);emit.set_editor_property('parameter_name','Emissive');emit.set_editor_property('default_value',0)
    pos=expr(m,unreal.MaterialExpressionWorldPosition,-900,-220)
    noise=expr(m,unreal.MaterialExpressionNoise,-700,-220);noise.set_editor_property('scale',.035);noise.set_editor_property('levels',2);noise.set_editor_property('quality',1);noise.set_editor_property('output_min',.75);noise.set_editor_property('output_max',1.0)
    connect(pos,'',noise,'Position')
    mult=expr(m,unreal.MaterialExpressionMultiply,-350,0);connect(color,'',mult,'A');connect(noise,'',mult,'B')
    em=expr(m,unreal.MaterialExpressionMultiply,-300,420);connect(color,'',em,'A');connect(emit,'',em,'B')
    ME.connect_material_property(mult,'',unreal.MaterialProperty.MP_BASE_COLOR)
    ME.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
    ME.connect_material_property(metal,'',unreal.MaterialProperty.MP_METALLIC)
    ME.connect_material_property(em,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    m.set_editor_property('two_sided',True)
    m.set_editor_property('used_with_skeletal_mesh',True)
    m.set_editor_property('used_with_instanced_static_meshes',True)
    m.set_editor_property('used_with_nanite',True)
    ME.recompile_material(m);EA.save_loaded_asset(m)
    return m
try:
    master=material_master(); materials={}
    for name,md in MANIFEST['materials'].items():
        mi=asset('MI_'+name,'/Game/GTA/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
        ME.set_material_instance_parent(mi,master)
        ME.set_material_instance_vector_parameter_value(mi,'BaseColor',unreal.LinearColor(*md['color'],1))
        ME.set_material_instance_scalar_parameter_value(mi,'Roughness',md['rough'])
        ME.set_material_instance_scalar_parameter_value(mi,'Metallic',md['metal'])
        ME.set_material_instance_scalar_parameter_value(mi,'Emissive',md['emit'])
        EA.save_loaded_asset(mi);materials[name]=mi
    smsys=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    inventory=[]
    for f in sorted((ROOT/'SourceAssets/BlenderExports').glob('*.fbx')):
        name=f.stem; skeletal=name.startswith('SK_')
        existing=EA.load_asset('/Game/GTA/Generated/'+name) if EA.does_asset_exist('/Game/GTA/Generated/'+name) else None
        if existing is None:
            task=unreal.AssetImportTask();task.set_editor_property('filename',str(f));task.set_editor_property('destination_path','/Game/GTA/Generated');task.set_editor_property('destination_name',name)
            task.set_editor_property('automated',True);task.set_editor_property('replace_existing',True);task.set_editor_property('save',True)
            ui=unreal.FbxImportUI();ui.set_editor_property('automated_import_should_detect_type',False)
            ui.set_editor_property('import_mesh',True);ui.set_editor_property('import_materials',False);ui.set_editor_property('import_textures',False);ui.set_editor_property('import_animations',False)
            ui.set_editor_property('import_as_skeletal',skeletal)
            ui.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_SKELETAL_MESH if skeletal else unreal.FBXImportType.FBXIT_STATIC_MESH)
            if skeletal:
                ui.set_editor_property('create_physics_asset',True)
                ui.skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose',True)
                ui.skeletal_mesh_import_data.set_editor_property('import_morph_targets',False)
            else:
                ui.static_mesh_import_data.set_editor_property('combine_meshes',True)
                ui.static_mesh_import_data.set_editor_property('auto_generate_collision',True)
                ui.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs',False)
                ui.static_mesh_import_data.set_editor_property('import_mesh_lo_ds',False)
            task.set_editor_property('options',ui);task.set_editor_property('factory',unreal.FbxFactory())
            AT.import_asset_tasks([task])
            existing=EA.load_asset('/Game/GTA/Generated/'+name) if EA.does_asset_exist('/Game/GTA/Generated/'+name) else None
        if not existing: raise RuntimeError('Missing imported mesh '+name)
        slots=existing.get_editor_property('materials' if skeletal else 'static_materials')
        names=MANIFEST['assets'].get(name,{}).get('materials',[])
        for i,slot in enumerate(slots):
            original=str(slot.get_editor_property('imported_material_slot_name'))
            if original not in materials:
                original=next((n for n in names if n==original or n.replace('.','_')==original),names[i] if i<len(names) else '')
            if original in materials:
                if skeletal:
                    slot.set_editor_property('material_interface',materials[original]);slots[i]=slot
                else: existing.set_material(i,materials[original])
        if skeletal:existing.set_editor_property('materials',slots)
        else:
            if name in ['SM_Office','SM_Tower','SM_Apartment','SM_House','SM_Warehouse','SM_Hangar','SM_Shop','SM_Garage','SM_Container','SM_Tree0','SM_Tree1','SM_Tree2']:
                ns=existing.get_editor_property('nanite_settings');ns.enabled=True
                existing.set_editor_property('nanite_settings',ns)
            setup=existing.get_editor_property('body_setup')
            if setup and name not in ['SM_Wheel','SM_Sedan','SM_Compact','SM_Sport','SM_Muscle','SM_SUV','SM_Pickup','SM_Van','SM_Police','SM_Motorcycle','SM_Helicopter','SM_Airplane','SM_Boat']:
                setup.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        EA.save_loaded_asset(existing)
        bounds=str(existing.get_bounds()) if not skeletal else 'skeletal'
        inventory.append({'name':name,'slots':len(slots),'bounds':bounds})
        log(name+' imported '+bounds)
    for f in (ROOT/'SourceAssets/Audio').glob('*.wav'):
        task=unreal.AssetImportTask();task.filename=str(f);task.destination_path='/Game/GTA/Audio';task.destination_name=f.stem;task.automated=True;task.replace_existing=True;task.save=True
        AT.import_asset_tasks([task]);a=EA.load_asset('/Game/GTA/Audio/'+f.stem)
        if a and f.stem in ['Engine','Rotor','Siren','City','Rain','Ocean']:a.set_editor_property('looping',True);EA.save_loaded_asset(a)
    (ROOT/'.astra-run/import_inventory.json').write_text(json.dumps(inventory,indent=2))
    unreal.PMEditorLibrary.repair_characters()
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log('SUCCESS '+str(len(inventory))+' meshes')
except Exception:
    unreal.log_error(traceback.format_exc());raise
