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

def anatomy(name,rings,m,segments=20):
    rr=[]
    for z,rx,ry,cx,cy in rings:
        rr.append([(cx+rx*math.cos(j*math.tau/segments),cy+ry*math.sin(j*math.tau/segments),z) for j in range(segments)])
    o=loft(name,rr,m)
    for p in o.data.polygons:p.use_smooth=True
    return o
for index,kind in enumerate(['Citizen','CitizenF','Police','Tactical']):
    female=kind=='CitizenF'; police=kind in ['Police','Tactical']
    skin=mat('Skin_'+kind,(.46,.255,.15) if index%2==0 else (.66,.39,.26),0,.60)
    jacket=mat('Jacket_'+kind,(.055,.082,.115) if police else ((.12,.18,.19) if female else (.12,.095,.07)),0,.86)
    pants=mat('Denim_'+kind,(.035,.045,.064),0,.91)
    hair=mat('Hair_'+kind,(.035,.022,.013),0,.86)
    parts=[]
    def add(o,bone):
        vg=o.vertex_groups.new(name=bone);vg.add(list(range(len(o.data.vertices))),1,'REPLACE');parts.append(o);return o
    hips=.15 if female else .145; shoulders=.21 if female else .235
    add(anatomy('TailoredJacket',[(.91,.13,hips,0,0),(1.02,.145,hips+.018,0,0),(1.14,.13,.17,0,0),(1.36,.16,shoulders,0,0),(1.48,.13,shoulders,0,0),(1.54,.11,.12,0,0)],jacket),'spine')
    add(anatomy('Pelvis',[(.86,.11,.15,0,0),(.97,.13,hips+.018,0,0),(1.04,.13,.145,0,0)],pants),'pelvis')
    add(rod('Neck',(0,0,1.5),(0,0,1.62),.062,skin,24),'neck')
    add(anatomy('Head',[(1.55,.057,.05,.025,0),(1.58,.083,.072,.02,0),(1.64,.099,.08,.012,0),(1.73,.092,.086,0,0),(1.79,.07,.069,-.005,0),(1.82,.025,.025,-.01,0)],skin,32),'head')
    add(ellipsoid('HairCap',(-.015,0,1.785),(.083,.087,.052 if not female else .075),hair),'head')
    if female:add(ellipsoid('Ponytail',(-.092,0,1.72),(.05,.06,.145),hair),'head')
    add(ellipsoid('Nose',(.106,0,1.674),(.027,.021,.041),skin),'head')
    add(ellipsoid('Chin',(.080,0,1.595),(.019,.046,.019),skin),'head')
    add(rod('Mouth',(.097,-.03,1.624),(.097,.03,1.624),.0035,mat('Lips',(.31,.105,.075),0,.6),12),'head')
    for s in [-1,1]:
        add(ellipsoid('Ear',(-.006,s*.087,1.688),(.028,.015,.046),skin),'head')
        add(ellipsoid('EyeSocket',(.083,s*.041,1.710),(.023,.027,.018),hair),'head')
        add(ellipsoid('Eye',(.099,s*.041,1.710),(.013,.019,.010),white),'head')
        add(ellipsoid('Iris',(.110,s*.041,1.710),(.005,.008,.008),black),'head')
        add(rod('Brow',(.096,s*.025,1.736),(.088,s*.064,1.738),.004,hair,8),'head')
        suffix='l' if s<0 else 'r'; y=s*.105
        add(anatomy('Trousers',[(.53,.080,.074,0,y),(.63,.087,.083,0,y),(.84,.10,.090,0,y),(.97,.098,.09,0,y)],pants),'thigh_'+suffix)
        add(anatomy('TrouserLower',[(.12,.056,.061,0,y),(.24,.064,.066,-.005,y),(.44,.071,.073,0,y),(.56,.079,.074,0,y)],pants),'calf_'+suffix)
        add(box('LeatherShoe',(.067,y,.075),(.30,.136,.135),dark,.035),'foot_'+suffix)
        add(box('Sole',(.069,y,.021),(.30,.14,.038),black,.014),'foot_'+suffix)
        for j in range(4):add(rod('Laces',(.06+j*.022,y-.035,.14),(.06+j*.022,y+.035,.14),.0025,white,6),'foot_'+suffix)
        yarm=s*(shoulders+.047)
        add(anatomy('JacketSleeve',[(1.16,.063,.060,0,yarm*1.10),(1.29,.074,.070,0,yarm*1.05),(1.43,.078,.075,0,yarm),(1.50,.063,.059,0,yarm*.96)],jacket),'upperarm_'+suffix)
        add(anatomy('ForearmSleeve',[(.92,.044,.043,.03,yarm*1.14),(1.07,.055,.053,.014,yarm*1.12),(1.18,.060,.06,0,yarm*1.1)],jacket),'forearm_'+suffix)
        add(ellipsoid('Hand',(.037,yarm*1.14,.87),(.036,.051,.077),skin),'hand_'+suffix)
        for j in range(4):
            add(rod('Finger',(.045+(j-1.5)*.016,yarm*1.14,.86),(.058+(j-1.5)*.017,yarm*1.14,.79+abs(j-1.5)*.009),.0085,skin,10),'hand_'+suffix)
        add(rod('Thumb',(.047,yarm*1.14-s*.04,.88),(.075,yarm*1.14-s*.055,.83),.012,skin,12),'hand_'+suffix)
        add(box('ChestPocket',(.15,s*.103,1.32),(.012,.086,.1),jacket,.008),'spine')
        add(box('Collar',(.065,s*.065,1.51),(.11,.072,.035),jacket,.014),'spine')
    add(rod('JacketZip',(.151,0,1.02),(.158,0,1.48),.0035,metal,8),'spine')
    add(box('Belt',(0,0,1.0),(.265,.325,.035),dark,.018),'pelvis')
    add(box('Buckle',(.14,0,1.0),(.018,.055,.036),metal,.004),'pelvis')
    if police:
        add(box('Badge',(.168,-.10,1.4),(.012,.040,.055),mat('Badge',(.61,.45,.16),.85,.25),.008),'spine')
        add(box('Radio',(.19,.14,1.40),(.04,.048,.07),black,.008),'spine')
        add(rod('RadioAntenna',(.185,.14,1.43),(.185,.14,1.55),.003,black,8),'spine')
        add(ellipsoid('DutyCap',(-.01,0,1.80),(.10,.10,.045),pants),'head')
        add(box('CapBrim',(.089,0,1.79),(.17,.18,.018),pants,.04),'head')
    if kind=='Tactical':
        add(box('BallisticVest',(.03,0,1.27),(.31,.40,.31),black,.035),'spine')
        for s in [-1,1]:
            for j in range(3):add(box('VestPouch',(.207,s*(.037+j*.05),1.26),(.045,.043,.115),cloth,.01),'spine')
    body=finish('SK_'+kind,parts,'Characters',export=False)
    bpy.ops.object.armature_add(enter_editmode=True,location=(0,0,0)); rig=bpy.context.object;rig.name='Rig_'+kind
    arm=rig.data;arm.edit_bones.remove(arm.edit_bones[0])
    boneinfo=[('root',(0,0,0),(0,0,.12),None),('pelvis',(0,0,.92),(0,0,1.06),'root'),('spine',(0,0,1.06),(0,0,1.50),'pelvis'),('neck',(0,0,1.50),(0,0,1.60),'spine'),('head',(0,0,1.60),(0,0,1.80),'neck')]
    for s in [-1,1]:
        suffix='l' if s<0 else 'r'; y=s*.105; a=s*(shoulders+.047)
        boneinfo += [('thigh_'+suffix,(0,y,.94),(0,y,.54),'pelvis'),('calf_'+suffix,(0,y,.54),(0,y,.13),'thigh_'+suffix),('foot_'+suffix,(0,y,.13),(.19,y,.075),'calf_'+suffix),('upperarm_'+suffix,(0,a,1.47),(0,a*1.1,1.17),'spine'),('forearm_'+suffix,(0,a*1.1,1.17),(.03,a*1.14,.94),'upperarm_'+suffix),('hand_'+suffix,(.03,a*1.14,.94),(.05,a*1.14,.80),'forearm_'+suffix)]
    for name,head,tail,parent in boneinfo:
        b=arm.edit_bones.new(name);b.head=head;b.tail=tail
        if parent:b.parent=arm.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    mod=body.modifiers.new('AnatomicalRig','ARMATURE');mod.object=rig;body.parent=rig
    bpy.ops.object.select_all(action='DESELECT');body.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.fbx(filepath=OUT+'SK_'+kind+'.fbx',use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE')
    rig.location=(index*3,155,0)
    for old in list(rig.users_collection):old.objects.unlink(rig)
    collection('GTA_UNREAL_Characters').objects.link(rig)
    print(kind,len(body.data.vertices),'vertices,',len(rig.data.bones),'bones')
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'UnrealGTA.blend')
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_distance=3
        area.spaces.active.region_3d.view_location=(0,155,1.0)
        area.spaces.active.region_3d.view_rotation=Quaternion((.66,.56,.32,.38)).normalized()
