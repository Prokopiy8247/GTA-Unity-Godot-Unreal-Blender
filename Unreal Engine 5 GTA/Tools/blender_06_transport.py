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

# Motorcycle: tubular frame, fork, finned engine, tank, saddle, exhaust, controls.
p=mat('Paint_Motorcycle',(.19,.025,.018),.65,.23)
parts=[]
parts+=line('TrellisFrame',[(-.75,0,.4),(-.15,0,.85),(.5,0,.70),(.65,0,.40),(-.4,0,.37),(-.75,0,.4)],.033,metal)
parts.append(ellipsoid('FuelTank',(.10,0,.84),(.35,.205,.19),p))
parts.append(box('Saddle',(-.47,0,.87),(.64,.29,.11),dark,.065))
parts.append(rod('ForkLeft',(.62,-.14,.40),(.40,-.14,1.04),.026,metal,20))
parts.append(rod('ForkRight',(.62,.14,.40),(.40,.14,1.04),.026,metal,20))
parts+=line('Handlebar',[(.4,-.40,1.05),(.42,-.2,1.02),(.42,.2,1.02),(.4,.40,1.05)],.02,metal)
for s in [-1,1]:
    parts.append(rod('Grip',(.40,s*.28,1.05),(.40,s*.42,1.05),.032,dark,20))
    parts.append(rod('EngineCylinder',(-.18,s*.11,.45),(.02,s*.12,.67),.12,black,24))
    for i in range(8):parts.append(box('CoolingFin',(-.12,s*.1,.45+i*.025),(.26,.14,.012),metal,.01))
    parts+=line('Exhaust',[(-.1,s*.17,.45),(.2,s*.23,.31),(-.65,s*.28,.30)],.035,metal)
    parts.append(rod('RearShock',(-.72,s*.16,.4),(-.32,s*.17,.78),.03,metal))
parts.append(rod('Headlamp',(.51,0,.96),(.60,0,.96),.105,headlight,32))
parts.append(box('TailLamp',(-.82,0,.85),(.025,.18,.05),red,.016))
parts.append(ellipsoid('FrontFender',(.70,0,.60),(.30,.17,.08),p))
parts.append(ellipsoid('RearFender',(-.76,0,.61),(.32,.17,.07),p))
finish('SM_Motorcycle',parts,'Vehicles').location=(0,190,0)
# Speedboat with a planing V-hull, deck rim, windscreen and seating.
parts=[];rings=[]
for x,w,z in [(-3.1,.94,.2),(-2.6,1.13,.40),(-1,1.15,.44),(1.0,.98,.53),(2.4,.56,.72),(3.2,.05,.91)]:
    rings.append([(x,0,-.48),(x,-w*.72,-.18),(x,-w,z),(x,w,z),(x,w*.72,-.18)])
parts.append(loft('PlaningHull',rings,white))
parts.append(box('CockpitFloor',(-1.1,0,.48),(3.6,1.78,.07),wood,.10))
for s in [-1,1]:
    parts+=line('Gunwale',[(-3,s*.98,.42),(-1,s*1.15,.64),(1,s*.98,.73),(2.6,s*.45,.92)],.065,white)
    parts.append(box('SeatBase',(-.7,s*.52,.72),(.8,.58,.22),white,.12))
    parts.append(box('SeatBack',(-1.0,s*.52,1.05),(.19,.60,.7),white,.09))
    parts+=line('BowRail',[(1,s*.90,.94),(2,s*.60,1.13),(2.9,0,1.25)],.022,metal)
parts.append(box('Console',(.4,0,.88),(.58,1.5,.50),white,.10))
parts.append(loft('Windscreen',[[(.53,-.85,.95),(.33,-.74,1.55),(.33,.74,1.55),(.53,.85,.95)],[(.56,-.85,.95),(.36,-.74,1.55),(.36,.74,1.55),(.56,.85,.95)]],glass))
parts.append(box('Outboard',(-3.08,0,.40),(.44,.54,.70),black,.14))
parts.append(rod('DriveLeg',(-3.1,0,.25),(-3.1,0,-.55),.095,metal,24))
finish('SM_Boat',parts,'Vehicles').location=(10,190,0)
# Helicopter silhouette: rounded fuselage, glazed cockpit, tapering tail and skids.
for idx,kind in enumerate(['Helicopter','PoliceHelicopter']):
    p=mat('Paint_'+kind,(.64,.67,.66) if idx==0 else (.035,.055,.07),.60,.30)
    parts=[ellipsoid('Fuselage',(0,0,1.25),(2.50,1.02,1.08),p)]
    parts.append(ellipsoid('Cockpit',(1.49,0,1.44),(1.12,.91,.80),glass))
    parts.append(ellipsoid('Nose',(2.08,0,1.03),(.60,.78,.47),p))
    parts.append(rod('TailBoom',(-1.8,0,1.54),(-6.9,0,2.15),.44,p,32,.14))
    parts.append(objmesh('TailFin',[(-6.9,-.065,1.95),(-6.25,-.065,2.1),(-6.72,-.065,3.38),(-7.15,-.065,3.38),(-6.9,.065,1.95),(-6.25,.065,2.1),(-6.72,.065,3.38),(-7.15,.065,3.38)],[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],p))
    parts.append(box('Tailplane',(-5.7,0,2.1),(.75,2.4,.11),p,.06))
    for s in [-1,1]:
        parts+=line('LandingSkid',[(-1.6,s*1.2,.13),(1.6,s*1.2,.13),(2.05,s*1.2,.42)],.065,metal)
        for x in [-1.1,1.1]:parts+=line('SkidStrut',[(x,s*.60,.56),(x,s*.83,.25),(x,s*1.2,.13)],.06,metal)
        parts.append(box('CabinDoor',(-.55,s*1.025,1.33),(1.28,.055,1.36),p,.18))
        parts.append(box('CabinWindow',(-.55,s*1.07,1.64),(1.0,.035,.64),glass,.14))
        parts.append(rod('DoorHandle',(-.85,s*1.10,1.28),(-.59,s*1.10,1.28),.014,metal))
        parts+=line('WindshieldFrame',[(1.04,s*.74,2.12),(1.66,s*.91,1.67),(2.3,s*.62,1.13)],.03,p)
    parts.append(rod('MainShaft',(0,0,2.06),(0,0,2.76),.12,metal,24))
    parts.append(box('EngineCover',(-.7,0,2.19),(1.70,.92,.45),p,.18))
    for s in [-1,1]:parts.append(rod('TurbineExhaust',(-1.25,s*.46,2.24),(-1.58,s*.47,2.24),.14,metal,24))
    parts.append(rod('TailRotorHub',(-6.83,-.31,2.34),(-6.83,.31,2.34),.07,metal))
    for a in [0,math.pi/2]:parts.append(rod('TailBlade',(-6.83-math.cos(a)*.85,-.34,2.34-math.sin(a)*.85),(-6.83+math.cos(a)*.85,-.34,2.34+math.sin(a)*.85),.045,black))
    if idx:
        parts.append(ellipsoid('Searchlight',(1.6,0,.30),(.22,.24,.20),headlight))
        parts.append(box('PoliceMark',(-.40,-1.066,1.1),(.86,.022,.20),white,.02))
    finish('SM_'+kind,parts,'Vehicles').location=(25+idx*14,190,0)
parts=[rod('RotorHub',(0,0,-.12),(0,0,.12),.20,metal,24)]
for i in range(4):
    a=i*math.pi/2
    o=box('CompositeBlade',(math.cos(a)*2.2,math.sin(a)*2.2,0),(4.2,.26,.045),black,.025);o.rotation_euler.z=a;parts.append(o)
finish('SM_Rotor',parts,'Vehicles').location=(60,190,3)
# Light airplane: lofted fuselage and cambered aerofoil wing.
parts=[];rings=[];p=mat('Paint_Airplane',(.76,.75,.68),.55,.3)
for x,ry,rz,z in [(-4.4,.08,.18,1.3),(-3,.3,.4,1.22),(-1.5,.58,.67,1.14),(0,.65,.75,1.14),(1.5,.57,.63,1.10),(2.7,.4,.44,1.06),(3.5,.16,.20,1.06)]:
    rings.append([(x,math.cos(j*math.tau/24)*ry,z+math.sin(j*math.tau/24)*rz) for j in range(24)])
parts.append(loft('MonocoqueFuselage',rings,p))
parts.append(ellipsoid('Canopy',(.6,0,1.77),(1.25,.56,.48),glass))
for s in [-1,1]:
    verts=[(-.7,s*.45,1.32),(1.1,s*.45,1.3),(.25,s*5.5,1.28),(-.68,s*5.5,1.28),(-.6,s*.45,1.45),(1.0,s*.45,1.44),(.2,s*5.5,1.35),(-.64,s*5.5,1.35)]
    parts.append(objmesh('TaperedWing',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],p))
    parts.append(box('Flap',(-.75,s*3,1.33),(.16,3.5,.06),metal,.025))
    parts.append(rod('LandingStrut',(.32,s*.65,.7),(.05,s*1.22,.23),.055,metal))
    parts.append(rod('LandingTire',(.05,s*1.22-.10,.23),(.05,s*1.22+.10,.23),.25,dark,32))
    parts.append(box('NavigationLight',(.1,s*5.5,1.32),(.17,.11,.08),red if s<0 else headlight,.025))
parts.append(box('Tailplane',(-3.65,0,1.29),(1.12,3.05,.10),p,.04))
parts.append(objmesh('Rudder',[(-4.3,-.055,1.33),(-3.0,-.055,1.33),(-3.8,-.055,2.8),(-4.35,-.055,2.8),(-4.3,.055,1.33),(-3,.055,1.33),(-3.8,.055,2.8),(-4.35,.055,2.8)],[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],p))
parts.append(rod('NoseGear',(2,0,.9),(2,0,.18),.045,metal))
parts.append(rod('NoseTire',(2,-.085,.19),(2,.085,.19),.20,dark,24))
finish('SM_Airplane',parts,'Vehicles').location=(75,190,0)
parts=[ellipsoid('Spinner',(0,0,0),(.24,.19,.19),metal)]
for i in range(3):
    a=i*math.tau/3;parts.append(rod('PropBlade',(0,math.cos(a)*.15,math.sin(a)*.15),(0,math.cos(a)*1.15,math.sin(a)*1.15),.065,black,10))
finish('SM_Propeller',parts,'Vehicles').location=(88,190,1)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'UnrealGTA.blend')
print('Motorcycle, boat, helicopters and airplane exported')
