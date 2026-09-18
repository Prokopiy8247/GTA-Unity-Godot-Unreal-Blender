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

specs=[('Compact',3.95,1.75,1.46,0.1,(0.24,0.38,0.42)),('Sedan',4.72,1.88,1.43,0,(0.04,0.13,0.19)),('Sport',4.45,1.94,1.16,-0.2,(0.55,0.075,0.025)),('Muscle',4.95,1.96,1.31,-0.05,(0.21,0.25,0.29)),('SUV',4.96,2.02,1.87,0.25,(0.16,0.18,0.14)),('Pickup',5.38,2.01,1.83,0.30,(0.28,0.13,0.065)),('Van',5.12,1.95,2.1,0.40,(0.63,0.62,0.56)),('Police',4.85,1.94,1.5,0,(0.035,0.045,0.055))]
for index,(kind,L,W,H,extra,color) in enumerate(specs):
    parts=[]; p=mat('Paint_'+kind,color,0.68,0.27); half=L*0.5; w=W*0.5
    stations=[(-half,0.82,0.62),(-half+0.18,0.95,0.85),(-half+0.60,1,0.93),(-L*0.28,1,1),(-0.4,1,1),(0.5,1,1),(L*0.29,1,0.96),(half-0.22,0.94,0.86),(half,0.8,0.69)]
    rings=[]
    ztop=0.85+extra*0.6
    for x,ww,h in stations:
        rings.append([(x,-w*ww*0.9,0.28),(x,-w*ww,0.49),(x,-w*ww,ztop*h),(x,-w*ww*0.88,ztop*h+0.09),(x,w*ww*0.88,ztop*h+0.09),(x,w*ww,ztop*h),(x,w*ww,0.49),(x,w*ww*0.9,0.28)])
    shell=loft(kind+'_sculpted_body',rings,p); bevel(shell,0.045,3)
    wheelx=[-L*0.30,L*0.30]
    for x in wheelx:
        for s in [-1,1]:
            cut=rod('ArchTool',(x,s*w-0.40,0.36),(x,s*w+0.40,0.36),0.405 if kind not in ['SUV','Pickup'] else 0.44,None,48)
            mod=shell.modifiers.new('Wheel housing','BOOLEAN'); mod.object=cut
            bpy.context.view_layer.objects.active=shell; bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cut,do_unlink=True)
    parts.append(shell)
    rear=-L*0.27 if kind not in ['Van','Pickup'] else (-L*0.40 if kind=='Van' else -0.2)
    front=L*0.22 if kind!='Van' else L*0.35
    cabinrings=[]
    for x,width,z in [(rear-0.2,w*.88,ztop),(rear+0.25,w*.76,H-.10),(front-.35,w*.75,H),(front+.32,w*.89,ztop+.05)]:
        cabinrings.append([(x,-width,ztop),(x,-width,z),(x,width,z),(x,width,ztop)])
    cabin=loft(kind+'_glazing',cabinrings,glass); bevel(cabin,0.035,3); parts.append(cabin)
    parts.append(box('Roof',((rear+front)*.5,0,H-.045),(front-rear-.2,W*.77,.09),p,.05))
    for s in [-1,1]:
        for x in [rear+.25,front-.35]:
            parts+=line('Pillar',[(x+(-.43 if x==rear+.25 else .5),s*w*.89,ztop+.02),(x,s*w*.765,H-.08)],.037,p)
        parts.append(rod('CenterPillar',(-.15,s*w*.89,ztop),(-.15,s*w*.77,H-.07),.027,black,12))
        parts.append(rod('WindowSill',(rear-.2,s*w*.91,ztop+.015),(front+.32,s*w*.91,ztop+.015),.018,metal,10))
        for dx in [-.8,.55]:
            if kind=='Pickup' and dx<0:continue
            parts.append(box('FlushDoorHandle',(dx,s*(w+.006),ztop-.08),(.19,.025,.038),metal,.012))
            parts+=line('DoorShutline',[(dx+.31,s*(w+.008),ztop-.14),(dx+.3,s*(w+.008),.48),(dx-.75,s*(w+.008),.48)],.004,dark)
        parts.append(box('MirrorHousing',(front+.03,s*(w+.10),ztop+.16),(.25,.18,.14),p,.055))
        parts.append(box('MirrorGlass',(front-.105,s*(w+.11),ztop+.16),(.008,.15,.105),glass,.006))
        parts.append(box('SideSkirt',(0,s*w,.32),(L*.62,.075,.08),black,.015))
        parts.append(box('Headlamp',(half-.035,s*w*.63,.69),(.05,W*.25,.14),headlight,.045))
        parts.append(box('TailLamp',(-half-.012,s*w*.64,.73),(.045,W*.26,.12),red,.025))
        parts.append(rod('Exhaust',(-half-.1,s*.60,.28),(-half+.13,s*.60,.28),.055,metal,20))
        parts.append(box('SeatBase',(-.20,s*.39,.60),(.53,.46,.15),cloth,.07))
        parts.append(box('SeatBack',(-.45,s*.39,.95),(.16,.46,.60),cloth,.075))
        parts.append(box('Headrest',(-.47,s*.39,1.26),(.16,.25,.19),cloth,.06))
    parts.append(box('FrontValance',(half-.03,0,.39),(.11,W*.91,.13),black,.035))
    parts.append(box('RearBumper',(-half,0,.4),(.08,W*.87,.15),black,.025))
    parts.append(box('Grille',(half+.018,0,.66),(.035,W*.40,.19),dark,.025))
    for j in range(7):
        parts.append(box('GrilleSlat',(half+.04,(j-3)*.095,.66),(.018,.022,.15),metal,.006))
    parts.append(box('Plate',(-half-.06,0,.52),(.012,.44,.10),white,.005))
    parts.append(box('Dashboard',(.55,0,.91),(.35,W*.75,.15),black,.04))
    for s in [-1,1]:
        parts+=line('HoodCrease',[(.8,s*.38,ztop+.08),(half-.23,s*.5,ztop*.87+.10)],.005,black)
    if kind=='Pickup':
        parts.append(box('BedLiner',(-1.45,0,1.04),(1.85,W*.8,.06),black,.012))
        for s in [-1,1]:parts.append(box('BedRail',(-1.5,s*w,1.24),(1.85,.085,.15),p,.035))
    if kind=='Sport':
        parts.append(box('RearWing',(-1.82,0,1.14),(.28,1.78,.045),black,.015))
        for s in [-1,1]:parts.append(box('WingSupport',(-1.78,s*.53,1.0),(.06,.035,.24),metal,.008))
    if kind=='Police':
        for s in [-1,1]:
            parts.append(box('WhiteDoorPanel',(-.28,s*(w+.008),.70),(1.58,.008,.32),white,.025))
        parts.append(box('LightbarMount',(-.10,0,H+.05),(.24,1.25,.055),black,.015))
        for s in [-1,1]:parts.append(box('EmergencyLight',(-.10,s*.37,H+.13),(.22,.54,.11),blue if s>0 else red,.027))
    o=finish('SM_'+kind,parts)
    o['wheelbase']=L*.60; o['track']=W*.98; o['height']=H
    o.location=(index*7,0,0)
    for x in wheelx:
        for s in [-1,1]:
            wh=bpy.data.objects['SM_Wheel'].copy(); wh.data=bpy.data.objects['SM_Wheel'].data
            collection('GTA_UNREAL_Vehicles').objects.link(wh); wh.name=kind+'_Wheel_'+str(x)+'_'+str(s); wh.location=(index*7+x,s*(w-.05),.36)
    print(kind,'created',len(o.data.vertices),'vertices')
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'UnrealGTA.blend')
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_distance=8
        area.spaces.active.region_3d.view_location=(7,0,.7)
        area.spaces.active.region_3d.view_rotation=Quaternion((.82,.37,.18,.38)).normalized()
        area.spaces.active.shading.type='MATERIAL'
