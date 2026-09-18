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

parts=[]
yellow=mat('CraneOchre',(.48,.28,.065),.55,.55)
for s in [-1,1]:
    parts+=line('CraneLeg',[(s*7,-5,0),(s*6,-4,21),(s*4,-3,24)],.35,yellow)
    parts+=line('CraneLeg',[(s*7,5,0),(s*6,4,21),(s*4,3,24)],.35,yellow)
    parts.append(rod('TopRail',(-9,s*3,24),(27,s*3,24),.30,yellow))
    parts.append(rod('LowerRail',(-9,s*3,21),(27,s*3,21),.24,yellow))
    for j in range(12):parts.append(rod('Truss',(-9+j*3,s*3,21),(-6+j*3,s*3,24),.12,yellow))
    parts.append(rod('Cable',(20,s*1.4,24),(20,s*1.4,4),.035,dark,8))
parts.append(box('OperatorCab',(5,-3.7,21),(3,2.5,2.8),glass,.18))
parts.append(box('LiftingSpreader',(20,0,4),(2.5,4.4,.5),yellow,.06))
finish('SM_PortCrane',parts,'Buildings').location=(0,230,0)
parts=[]
for z,r in [(0,2.2),(2,2.15),(5,1.95),(8,1.8),(11,1.6),(14,1.5)]:
    parts.append(rod('Masonry',(0,0,z),(0,0,z+3),r,white if z%2==0 else brick,48,r-.12))
parts.append(rod('Lantern',(0,0,17),(0,0,19.5),1.45,glass,32))
parts.append(rod('LanternRoof',(0,0,19.5),(0,0,20.5),1.8,metal,32,.05))
for j in range(8):
    a=j*math.tau/8;parts.append(rod('LanternFrame',(math.cos(a)*1.45,math.sin(a)*1.45,17),(math.cos(a)*1.45,math.sin(a)*1.45,19.5),.05,metal))
finish('SM_Lighthouse',parts,'Buildings').location=(45,230,0)
# Terrain hill with original seeded ridges; 240m square and 75m summit.
random.seed(44);verts=[];faces=[];N=49
for i in range(N):
    x=(i/(N-1)-.5)*240
    for j in range(N):
        y=(j/(N-1)-.5)*240
        radial=max(0,1-(x*x+y*y)**.5/118)
        h=(radial**1.6)*75*(.78+.22*math.sin(x*.052)*math.cos(y*.071))
        verts.append((x,y,h-1))
for i in range(N-1):
    for j in range(N-1):
        a=i*N+j;faces.append((a,a+N,a+N+1,a+1))
terrain=objmesh('RidgedTerrain',verts,faces,mat('TerrainRock',(.21,.23,.15),0,.94))
for p in terrain.data.polygons:p.use_smooth=True
finish('SM_Hill',[terrain],'Nature').location=(100,300,0)
# Usable small safehouse interior with open south doorway.
parts=[box('Floor',(0,0,-.12),(12,10,.24),wood,.03),box('BackWall',(0,5,1.6),(12,.2,3.2),white,.03)]
for s in [-1,1]:
    parts.append(box('SideWall',(s*6,0,1.6),(.2,10,3.2),white,.03))
    parts.append(box('EntryWall',(s*3.65,-5,1.6),(4.7,.2,3.2),white,.03))
parts.append(box('DoorLintel',(0,-5,2.9),(2.6,.2,.6),white,.025))
parts.append(box('SofaSeat',(-3.4,2,.43),(3.2,1.0,.45),cloth,.17))
parts.append(box('SofaBack',(-3.4,2.5,.85),(3.2,.28,1.0),cloth,.14))
parts.append(box('Table',(-3.4,.3,.53),(1.7,.8,.09),wood,.04))
for s in [-1,1]:parts.append(box('TableLeg',(-3.4+s*.6,.3,.25),(.08,.6,.5),metal,.01))
parts.append(box('BedBase',(3,2,.33),(2,2.5,.5),wood,.08));parts.append(box('Mattress',(3,2,.67),(1.9,2.4,.24),white,.12))
parts.append(box('Pillow',(3,2.7,.86),(1.2,.45,.20),white,.08))
parts.append(box('Wardrobe',(4,-3,1.2),(1.8,.6,2.4),wood,.04))
parts.append(box('Display',(-5.85,1,1.5),(.06,1.6,1),black,.02))
finish('SM_Safehouse',parts,'Interiors').location=(40,260,0)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'UnrealGTA.blend')
for win in bpy.context.window_manager.windows:
    for a in win.screen.areas:
        if a.type=='VIEW_3D':
            a.spaces.active.region_3d.view_location=(75,190,1)
            a.spaces.active.region_3d.view_distance=17
            a.spaces.active.region_3d.view_rotation=Quaternion((.82,.37,.18,.38)).normalized()
            a.tag_redraw()
print('Four additional landmarks/interior/terrain meshes exported')
