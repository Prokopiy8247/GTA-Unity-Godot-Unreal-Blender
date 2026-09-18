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

for n in ['Cube','Camera','Light']:
    o=bpy.data.objects.get(n)
    if o:bpy.data.objects.remove(o,do_unlink=True)
print('mode enums', [i.identifier for i in bpy.ops.object.mode_set.get_rna_type().properties['mode'].enum_items])
print('modifier enums', [i.identifier for i in bpy.types.Modifier.bl_rna.properties['type'].enum_items])
parts=[]
parts.append(rod('Tire',(0,-0.115,0),(0,0.115,0),0.34,dark,48))
for s in [-1,1]:
    parts.append(rod('Rim',(0,s*0.119,0),(0,s*0.127,0),0.248,metal,48))
    parts.append(rod('BrakeDisc',(0,s*0.13,0),(0,s*0.135,0),0.205,black,40))
    for i in range(10):
        a=i*math.tau/10
        parts.append(rod('ForgedSpoke',(math.cos(a)*0.055,s*0.143,math.sin(a)*0.055),(math.cos(a+0.12)*0.23,s*0.142,math.sin(a+0.12)*0.23),0.016,metal,8))
    parts.append(rod('Hub',(0,s*0.15,0),(0,s*0.165,0),0.061,metal,24))
    for i in range(48):
        a=i*math.tau/48
        parts.append(rod('Tread',(math.cos(a)*0.339,-0.10,math.sin(a)*0.339),(math.cos(a+0.045)*0.341,0.10,math.sin(a+0.045)*0.341),0.004,black,4))
wheel=finish('SM_Wheel',parts)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'UnrealGTA.blend')
print('Wheel exported',list(wheel.dimensions))
