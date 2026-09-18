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

# Modular facade architecture; real meters, grounded origins.
for idx,(name,w,d,h,floors,style) in enumerate([('Office',28,24,76,19,0),('Tower',33,28,132,33,0),('Apartment',22,18,24,7,1),('House',13,11,6.5,2,2),('Warehouse',38,30,11,2,3),('Hangar',48,44,16,1,3),('Shop',22,17,5.3,1,4),('Garage',26,24,6,1,3)]):
    parts=[]; wall=concrete if style in [0,3,4] else (brick if style==1 else white)
    parts.append(box(name+'_structure',(0,0,h/2),(w,d,h),wall,.10))
    parts.append(box('Foundation',(0,0,.16),(w+.4,d+.4,.32),concrete,.04))
    for s in [-1,1]:
        for floor in range(floors):
            z=2.3+floor*(h-2)/floors
            if z+1.5>h:continue
            for col in range(max(2,int(w/3.3))):
                x=-w/2+1.9+col*3.3
                parts.append(box('Window',(x,s*(d/2+.025),z),(2.3,.065,2.05 if style!=3 else .9),glass,.015))
                if style==1:
                    parts.append(box('Sill',(x,s*(d/2+.09),z-1.1),(2.6,.28,.10),concrete,.01))
                    if col%2==0:
                        parts.append(box('Balcony',(x,s*(d/2+.8),z-.93),(2.75,1.4,.12),concrete,.02))
                        parts.append(rod('Railing',(x-1.3,s*(d/2+1.4),z),(x+1.3,s*(d/2+1.4),z),.035,metal,8))
            if style==0:
                parts.append(box('Spandrel',(0,s*(d/2+.05),z-1.23),(w,.10,.35),black,.012))
                for col in range(int(w/3.3)+1):
                    parts.append(box('Mullion',(-w/2+col*3.3,s*(d/2+.075),z),(.10,.1,2.75),metal,.006))
        if style==0:
            for floor in range(floors):
                z=2.3+floor*(h-2)/floors
                for col in range(int(d/3.3)):
                    y=-d/2+1.9+col*3.3
                    parts.append(box('SideWindow',(s*(w/2+.025),y,z),(.065,2.3,2.05),glass,.01))
        parts.append(box('RoofParapet',(s*(w/2-.1),0,h+.32),(.22,d,.64),wall,.03))
    parts.append(box('Cornice',(0,0,h-.12),(w+.5,d+.5,.24),black,.035))
    for i in range(2 if style==2 else 4):
        parts.append(box('HVAC',(-w*.25+i*w*.16,0,h+.5),(1.4,2,1),metal,.09))
    if style==2:
        roofverts=[(-w/2-.6,-d/2-.6,h),(-w/2-.6,d/2+.6,h),(w/2+.6,-d/2-.6,h),(w/2+.6,d/2+.6,h),(-w/2-.6,0,h+2.2),(w/2+.6,0,h+2.2)]
        parts.append(objmesh('PitchedTileRoof',roofverts,[(0,2,5,4),(1,4,5,3),(0,4,1),(2,3,5)],brick))
        parts.append(box('Porch',(0,-d/2-1.2,.16),(4,2.4,.32),concrete,.05))
    parts.append(box('EntryRecess',(0,-d/2-.055,1.3),(2.8,.12,2.6),black,.02))
    parts.append(box('DoorGlass',(0,-d/2-.13,1.25),(2.3,.05,2.35),glass,.015))
    parts.append(rod('DoorPull',(.3,-d/2-.18,.8),(.3,-d/2-.18,1.6),.024,metal,12))
    if style in [3,4]:
        for i in range(3 if style==3 else 1):
            x=(i-1)*7 if style==3 else 0
            parts.append(box('RollerDoor',(x,-d/2-.06,2.25),(5,.1,4.5),metal,.025))
            for k in range(18):parts.append(box('ShutterRib',(x,-d/2-.13,.2+k*.24),(5,.045,.035),black,.008))
    o=finish('SM_'+name,parts,'Buildings'); o.location=(idx*55,45,0)
# Ground / road profiles are original authored meshes, rather than engine placeholders.
for name,color in [('Ground',(.19,.22,.12)),('Asphalt',(.044,.052,.059)),('Sidewalk',(.4,.39,.35)),('Sand',(.52,.43,.27)),('Water',(.018,.17,.22)),('Marking',(.79,.77,.62))]:
    m=mat(name,color,0.08 if name=='Water' else 0,.15 if name=='Water' else .87)
    o=finish('SM_'+name,[box(name,(0,0,-.05),(1,1,.1),m,0)],'World')
    o.location=(len(bpy.data.objects)*.2,100,0)
# Lamp with arched arm, traffic lights, street furniture.
parts=[rod('Pole',(0,0,0),(0,0,7.8),.10,metal,20),rod('Base',(0,0,0),(0,0,.6),.21,black,20)]
parts+=line('SweptArm',[(0,0,7.8),(0,.5,8.1),(0,1.6,8.15),(0,2.4,8.0)],.065,metal)
parts.append(box('LEDHousing',(0,2.5,7.96),(.38,.95,.12),black,.08))
parts.append(box('LEDLens',(0,2.5,7.89),(.28,.75,.035),headlight,.01))
finish('SM_Lamp',parts,'StreetProps').location=(0,110,0)
parts=[rod('SignalPole',(0,0,0),(0,0,5.6),.09,black,16),rod('CrossArm',(0,0,5.6),(0,5.2,5.6),.075,black,16),box('SignalBox',(0,5,4.95),(.34,.32,1.0),black,.05)]
for j,m in enumerate([red,mat('Amber',(1,.35,.02),0,.3,2),mat('Green',(0.02,.62,.18),0,.3,2)]):
    parts.append(rod('Lens',(.17,5,5.22-j*.28),(.2,5,5.22-j*.28),.095,m,24))
finish('SM_TrafficLight',parts,'StreetProps').location=(6,110,0)
parts=[]
for j in range(6):parts.append(box('SeatSlat',(0,(j-2.5)*.085,.47),(1.9,.065,.065),wood,.015))
for j in range(4):parts.append(box('BackSlat',(0,.27,.66+j*.09),(1.9,.065,.065),wood,.015))
for s in [-1,1]:
    parts+=line('BenchFrame',[(s*.7,-.2,0),(s*.7,-.2,.44),(s*.7,.25,.44),(s*.7,.29,.98)],.034,black)
finish('SM_Bench',parts,'StreetProps').location=(12,110,0)
parts=[rod('HydrantBody',(0,0,0),(0,0,.8),.13,red,24),ellipsoid('Cap',(0,0,.8),(.16,.16,.12),red)]
parts += [rod('Outlet',(-.27,0,.58),(.27,0,.58),.075,metal,20)]
finish('SM_Hydrant',parts,'StreetProps').location=(16,110,0)
parts=[box('JerseyBarrier',(0,0,.4),(3,.6,.8),concrete,.15)]
parts.append(box('Reflector',(0,-.315,.65),(.45,.015,.14),headlight,.01))
finish('SM_Barrier',parts,'StreetProps').location=(20,110,0)
parts=[box('Container',(0,0,1.3),(12.2,2.44,2.6),mat('ContainerTeal',(.055,.19,.21),.4,.55),.035)]
for s in [-1,1]:
    for i in range(48):parts.append(box('Corrugation',(-5.95+i*.25,s*1.235,1.3),(.045,.05,2.5),metal,.008))
finish('SM_Container',parts,'StreetProps').location=(35,110,0)
parts=[rod('Bin',(0,0,0),(0,0,.9),.28,black,32),rod('Rim',(0,0,.9),(0,0,.96),.30,metal,32)]
finish('SM_Bin',parts,'StreetProps').location=(48,110,0)
parts=[box('BusShelterRoof',(0,0,2.6),(4.5,1.65,.12),metal,.05)]
for s in [-1,1]:parts.append(rod('ShelterPost',(s*2,0,0),(s*2,0,2.6),.06,metal,12))
parts.append(box('ShelterGlass',(0,.6,1.4),(4,.04,2.1),glass,.01))
parts.append(box('Seat',(0,.2,.5),(3,.38,.08),wood,.02))
finish('SM_BusStop',parts,'StreetProps').location=(55,110,0)
# Detailed trees use individually authored leaf clusters, branches and irregular crowns.
random.seed(1978)
for k in range(3):
    parts=[rod('Bark',(0,0,0),(0,0,5+k),.28,wood,16,.10)]
    for j in range(14):
        angle=j*2.4
        tip=Vector((math.cos(angle)*(1.6+random.random()),math.sin(angle)*(1.6+random.random()),3.8+random.random()*3+k))
        parts.append(rod('Branch',(0,0,2.4+j*.19),tip,.095,wood,10,.02))
        for n in range(9):
            p=tip+Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-.6,.7)))
            parts.append(ellipsoid('LeafCluster',p,(.48+random.random()*.3,.5,.30),leaf))
    finish('SM_Tree'+str(k),parts,'Nature').location=(k*12,130,0)
parts=[]
for j in range(6):parts.append(ellipsoid('Boulder',(random.uniform(-.6,.6),random.uniform(-.6,.6),.25),(.8,.65,.5),concrete))
finish('SM_Rock',parts,'Nature').location=(40,130,0)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'UnrealGTA.blend')
print('Environment library complete')
