import bpy, math, random, json
from mathutils import Vector, Quaternion
ROOT = bpy.path.abspath('//').replace(chr(92), '/')
OUT = ROOT + 'SourceAssets/BlenderExports/'
def collection(name):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c
def mat(name,color,metal=0.0,rough=0.5,emission=0.0):
    m=bpy.data.materials.get(name)
    if m is None: m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value=(*color,1)
    n.inputs['Metallic'].default_value=metal; n.inputs['Roughness'].default_value=rough
    n.inputs['Emission Color'].default_value=(*color,1); n.inputs['Emission Strength'].default_value=emission
    m['pm_color']=list(color); m['pm_metal']=metal; m['pm_rough']=rough; m['pm_emit']=emission
    return m
def objmesh(name,verts,faces,m):
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o)
    if m:o.data.materials.append(m)
    return o
def apply(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
def bevel(o,width=0.02,seg=3):
    b=o.modifiers.new('Manufactured edge radius','BEVEL'); b.width=width; b.segments=seg
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.modifier_apply(modifier=b.name)
    return o
def box(name,loc,size,m,edge=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.scale=size
    apply(o)
    if m:o.data.materials.append(m)
    if edge:bevel(o,edge,3)
    return o
def ellipsoid(name,loc,size,m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=1,location=loc)
    o=bpy.context.object; o.name=name; o.scale=size; apply(o)
    if m:o.data.materials.append(m)
    for p in o.data.polygons:p.use_smooth=True
    return o
def rod(name,a,b,r,m,vertices=16,r2=None):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r,radius2=r if r2 is None else r2,depth=d.length,location=(a+b)*0.5)
    o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    if m:o.data.materials.append(m)
    for p in o.data.polygons:p.use_smooth=True
    return o
def line(name,points,r,m):
    return [rod(name+str(i),points[i],points[i+1],r,m,10) for i in range(len(points)-1)]
def loft(name,rings,m):
    verts=[p for ring in rings for p in ring]; k=len(rings[0]); n=len(rings)
    faces=[tuple(reversed(range(k))),tuple((n-1)*k+j for j in range(k))]
    for i in range(n-1):
        for j in range(k): faces.append((i*k+j,i*k+(j+1)%k,(i+1)*k+(j+1)%k,(i+1)*k+j))
    return objmesh(name,verts,faces,m)
def finish(name,objects,group='Vehicles',export=True,uv=True):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]; bpy.ops.object.join(); o=bpy.context.object; o.name=name
    bpy.context.scene.cursor.location=(0,0,0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    if uv:
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(island_margin=0.015); bpy.ops.object.mode_set(mode='OBJECT')
    c=collection('GTA_UNREAL_'+group)
    for old in list(o.users_collection): old.objects.unlink(o)
    c.objects.link(o)
    if export:
        bpy.ops.export_scene.fbx(filepath=OUT+name+'.fbx',use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False,mesh_smooth_type='FACE')
    return o
paint=mat('Paint_Ocean',(0.035,0.15,0.20),0.72,0.24)
dark=mat('Rubber',(0.015,0.019,0.021),0.0,0.8)
metal=mat('BrushedAlloy',(0.4,0.44,0.46),0.85,0.27)
glass=mat('SmokedGlass',(0.035,0.09,0.12),0.5,0.12)
black=mat('Graphite',(0.035,0.045,0.055),0.45,0.43)
white=mat('Ivory',(0.75,0.79,0.8),0.15,0.4)
headlight=mat('Headlamp',(0.82,0.93,1),0.2,0.19,3)
red=mat('TailLamp',(0.7,0.015,0.008),0.1,0.24,2)
blue=mat('PoliceBlue',(0.015,0.16,0.95),0.1,0.22,5)
concrete=mat('Concrete',(0.38,0.37,0.34),0,0.88)
brick=mat('Brick',(0.3,0.12,0.07),0,0.88)
cloth=mat('Fabric',(0.04,0.065,0.085),0,0.94)
wood=mat('Wood',(0.23,0.115,0.044),0,0.78)
leaf=mat('Foliage',(0.075,0.15,0.035),0,0.92)

for index,kind in enumerate(['Pistol','Revolver','SMG','Shotgun','Rifle','Carbine','Marksman','Sniper','Launcher','Knife','Bat','Grenade']):
    parts=[];gunmetal=mat('Gunmetal',(.08,.085,.095),.8,.35);grip=mat('WeaponPolymer',(.035,.033,.029),.05,.8)
    if kind in ['Knife','Bat','Grenade']:
        if kind=='Knife':
            parts.append(box('TexturedGrip',(-.055,0,0),(.13,.032,.027),grip,.008))
            parts.append(objmesh('GroundBlade',[(0,-.018,-.004),(0,.018,-.004),(.17,.012,-.004),(.225,0,0),(.17,-.012,-.004),(0,-.018,.004),(0,.018,.004),(.17,.012,.004),(.17,-.012,.004)],[(0,1,2,3,4),(5,8,3,7,6),(0,5,6,1),(1,6,7,2),(4,3,8),(4,8,5,0)],metal))
        elif kind=='Bat':
            parts.append(rod('Grip',(-.15,0,0),(.10,0,0),.015,grip,24))
            parts.append(rod('Bat',(.1,0,0),(.66,0,0),.017,metal,32,.038))
            parts.append(ellipsoid('EndCap',(.66,0,0),(.028,.038,.038),metal))
        else:
            parts.append(ellipsoid('FragmentBody',(0,0,0),(.035,.035,.06),mat('OrdnanceOlive',(.12,.15,.06),.35,.6)))
            parts.append(box('Lever',(.02,0,.03),(.017,.018,.08),metal,.003))
            parts.append(rod('FuseNeck',(0,0,.05),(0,0,.07),.014,metal,16))
    elif kind=='Launcher':
        parts.append(rod('LauncherTube',(-.25,0,.02),(.75,0,.02),.095,mat('Ordnance',(.17,.19,.07),.4,.65),32))
        parts.append(rod('Muzzle',(.72,0,.02),(.78,0,.02),.098,dark,32))
        parts.append(box('PistolGrip',(.02,0,-.08),(.07,.05,.15),grip,.008))
        parts.append(box('Sight',(.27,0,.14),(.12,.05,.10),metal,.01))
    else:
        pistol=kind in ['Pistol','Revolver'];length=.20 if pistol else .44 if kind=='SMG' else .84 if kind=='Shotgun' else 1.14 if kind=='Sniper' else .90
        parts.append(box('Receiver',(.12,0,.045),(.22 if pistol else .36,.038 if pistol else .055,.065),gunmetal,.010))
        if pistol:
            g=box('ErgonomicGrip',(.02,0,-.03),(.072,.034,.135),grip,.012);g.rotation_euler.y=-.18;parts.append(g)
            parts.append(rod('Barrel',(.14,0,.052),(.245,0,.052),.012,gunmetal,24))
            parts.append(rod('Bore',(.245,0,.052),(.248,0,.052),.007,dark,20))
            for j in range(7):parts.append(box('SlideSerration',(.018+j*.012,.020,.05),(.004,.003,.046),metal,.001))
            if kind=='Revolver':parts.append(rod('ChamberCylinder',(.08,0,.04),(.17,0,.04),.034,gunmetal,24))
        else:
            parts.append(rod('Barrel',(.25,0,.053),(length-.15,0,.053),.018,gunmetal,24))
            parts.append(rod('FlashHider',(length-.18,0,.053),(length-.11,0,.053),.026,gunmetal,20))
            parts.append(rod('Bore',(length-.11,0,.053),(length-.106,0,.053),.012,dark,16))
            parts.append(box('Handguard',(.40,0,.028),(.25,.062,.080),grip,.012))
            for j in range(10):
                parts.append(box('RailTooth',(.26+j*.025,0,.092),(.011,.06,.008),metal,.002))
                for s in [-1,1]:parts.append(box('CoolingSlot',(.3+j*.018,s*.032,.04),(.009,.003,.035),dark,.003))
            parts.append(box('Stock',(-.15,0,.024),(.28,.055,.095),grip,.022))
            parts.append(box('ButtPad',(-.295,0,.015),(.026,.064,.14),dark,.012))
            g=box('Grip',(.075,0,-.08),(.064,.046,.14),grip,.012);g.rotation_euler.y=-.22;parts.append(g)
            if kind!='Shotgun':parts.append(box('Magazine',(.18,0,-.095),(.08,.035,.19),gunmetal,.012))
            else:parts.append(rod('TubeMagazine',(.2,0,.003),(.66,0,.003),.018,gunmetal,20))
            if kind in ['Sniper','Marksman']:
                parts.append(rod('Optic',(.0,0,.15),(.29,0,.15),.025,black,24))
                parts.append(rod('Objective',(.26,0,.15),(.32,0,.15),.038,black,32))
                parts.append(rod('OpticLens',(.322,0,.15),(.325,0,.15),.031,glass,24))
                for x in [.06,.20]:parts.append(box('ScopeMount',(x,0,.104),(.032,.036,.050),metal,.006))
        parts+=line('TriggerGuard',[(.09,-.018,-.006),(.135,-.018,-.055),(.045,-.018,-.065),(.02,-.018,-.015)],.005,gunmetal)
        parts.append(rod('Trigger',(.084,0,.004),(.079,0,-.035),.003,metal,10))
        parts.append(box('FrontSight',(.19 if pistol else length-.16,0,.094),(.02,.012,.023),metal,.003))
    obj=finish('SM_'+kind,parts,'Weapons');obj.location=(index*1.5,165,1)
# Removable parts, particle geometry, parachute canopy.
finish('SM_Spoiler',[box('Wing',(0,0,0),(.3,1.8,.05),black,.022),box('MountL',(0,-.5,-.12),(.06,.045,.25),metal,.01),box('MountR',(0,.5,-.12),(.06,.045,.25),metal,.01)],'Vehicles').location=(0,175,1)
finish('SM_Rocket',[rod('RocketBody',(-.25,0,0),(.17,0,0),.045,metal,24),ellipsoid('Warhead',(.17,0,0),(.10,.045,.045),black)],'Weapons').location=(3,175,1)
finish('SM_Spark',[ellipsoid('Spark',(0,0,0),(.1,.1,.1),headlight)],'VFX_HelperMeshes').location=(5,175,1)
finish('SM_Smoke',[ellipsoid('Smoke',(0,0,0),(.35,.32,.3),mat('Smoke',(.12,.12,.13),0,1))],'VFX_HelperMeshes').location=(6,175,1)
parts=[]; canopy=mat('Canopy',(.65,.19,.06),0,.68)
verts=[];faces=[]
for i in range(17):
    y=(i-8)*.32;z=1.4-.05*y*y
    for x in [-1.0,-.5,0,.5,1.0]:verts.append((x,y,z-.20*x*x))
for i in range(16):
    for j in range(4):faces.append((i*5+j,i*5+j+1,(i+1)*5+j+1,(i+1)*5+j))
parts.append(objmesh('RamAirCanopy',verts,faces,canopy))
for s in [-1,1]:
    for y in [-2,-1,0,1,2]:parts.append(rod('SuspensionLine',(s*.8,y,1.4-.05*y*y),(0,s*.17,-1.1),.008,white,6))
finish('SM_Parachute',parts,'Vehicles').location=(10,175,2)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'UnrealGTA.blend')
print('12 weapons and supporting meshes exported')
