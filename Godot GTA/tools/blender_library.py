"""Original Meridian Coast assets. Execute inside Blender via blender_godot MCP."""
import bpy, math, random, json
from mathutils import Vector
ROOT = bpy.path.abspath('//').rstrip('/\\')
OUT = ROOT + '/gta/generated/models'

random.seed(817)
assert bpy.data.filepath.endswith('GodotGTA.blend')
M = {}
def material(name, color, metal=0, rough=.5, emission=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    if emission:
        p.inputs['Emission Color'].default_value=(*color,1)
        p.inputs['Emission Strength'].default_value=emission
    m.diffuse_color=(*color,1)
    M[name]=m
    return m
for n,c,me,r,e in [
 ('paint',(0.055,.18,.21),.72,.26,0),('red',(.38,.026,.019),.65,.28,0),
 ('white',(.73,.76,.72),.25,.36,0),('black',(.025,.032,.039),.1,.45,0),
 ('rubber',(.014,.017,.021),0,.86,0),('chrome',(.48,.53,.58),.94,.2,0),
 ('glass',(.06,.135,.18),.5,.16,0),('headlight',(.95,.83,.59),.1,.2,1),
 ('taillight',(.65,.009,.006),.1,.23,2),('blue',(.008,.09,.8),.2,.2,3),
 ('concrete',(.43,.42,.38),0,.89,0),('plaster',(.66,.63,.54),0,.84,0),
 ('brick',(.29,.13,.082),0,.89,0),('steel',(.13,.16,.17),.8,.4,0),
 ('wood',(.22,.105,.037),0,.83,0),('leaf',(.095,.18,.043),0,.95,0),
 ('leaf2',(.16,.26,.055),0,.94,0),('skin',(.48,.285,.17),0,.6,0),
 ('skin2',(.22,.115,.071),0,.63,0),('skin3',(.72,.48,.31),0,.62,0),
 ('hair',(.035,.022,.014),0,.92,0),('cloth',(.075,.1,.115),0,.96,0),
 ('denim',(.042,.085,.135),0,.92,0),('shirt',(.36,.31,.21),0,.95,0),
 ('uniform',(.024,.047,.087),0,.9,0),('gold',(.58,.39,.08),.7,.3,0),
 ('window_lit',(.57,.46,.26),.2,.3,.6)]: material(n,c,me,r,e)

asset=[]
def begin(name, family):
    coll=bpy.data.collections.get(name)
    if coll:
        for o in list(coll.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(coll)
    coll=bpy.data.collections.new(name)
    parent=bpy.data.collections.get(family)
    if not parent:
        parent=bpy.data.collections.new(family); bpy.context.scene.collection.children.link(parent)
    parent.children.link(coll)
    root=bpy.data.objects.new(name,None); coll.objects.link(root)
    asset[:]=[name,coll,root]
    return root
def own(o,name,mat=None):
    o.name=asset[0]+'__'+name
    for c in list(o.users_collection): c.objects.unlink(o)
    asset[1].objects.link(o); o.parent=asset[2]
    if mat: o.data.materials.append(M[mat])
    return o
def box(name,loc,size,mat,bev=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=own(bpy.context.object,name,mat); o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bev:
        mod=o.modifiers.new('Soft manufactured edges','BEVEL'); mod.width=bev; mod.segments=2
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
    return o
def ell(name,loc,size,mat,seg=20,rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,radius=1,location=loc)
    o=own(bpy.context.object,name,mat); o.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for p in o.data.polygons:p.use_smooth=True
    return o
def cyl(name,loc,r,depth,mat,axis='Z',verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc)
    o=own(bpy.context.object,name,mat)
    if axis=='X':o.rotation_euler[1]=math.pi/2
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    for p in o.data.polygons:p.use_smooth=True
    return o
def beam(name,a,b,r,mat):
    a,b=Vector(a),Vector(b); o=cyl(name,(a+b)/2,r,(b-a).length,mat,verts=12)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def mesh(name,verts,faces,mat,smooth=False):
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update()
    o=bpy.data.objects.new(name,m);asset[1].objects.link(o);o.parent=asset[2];o.name=asset[0]+'__'+name
    m.materials.append(M[mat])
    uv=m.uv_layers.new(name='UVMap')
    for p in m.polygons:
        p.use_smooth=smooth
        for li in p.loop_indices:
            v=m.vertices[m.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.2,v.z*.2+v.y*.05)
    return o
def loft(name,sections,mat):
    # y, half-width, bottom, shoulder, top; softened octagonal coachwork section.
    vs=[]
    for y,w,b,s,t in sections:
        vs += [(-w*.8,y,b),(-w,y,b+.09),(-w,y,s),(-w*.77,y,t),(w*.77,y,t),(w,y,s),(w,y,b+.09),(w*.8,y,b)]
    fs=[tuple(range(7,-1,-1))]
    for i in range(len(sections)-1):
        for j in range(8):fs.append((i*8+j,i*8+(j+1)%8,(i+1)*8+(j+1)%8,(i+1)*8+j))
    fs.append(tuple(range((len(sections)-1)*8,len(sections)*8)))
    return mesh(name,vs,fs,mat)
def label(text,loc,size=.4,mat='white',rot=(math.pi/2,0,0)):
    cu=bpy.data.curves.new('Lettering','FONT');cu.body=text;cu.size=size;cu.align_x='CENTER';cu.extrude=.003
    o=bpy.data.objects.new('Lettering',cu);asset[1].objects.link(o);o.parent=asset[2];o.location=loc;o.rotation_euler=rot;cu.materials.append(M[mat])
    bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
    return o
def finish(merge=True):
    name,coll,root=asset
    if merge:
        objects=[o for o in coll.objects if o.type=='MESH' and 'Wheel_' not in o.name and 'Rotor' not in o.name and 'Propeller' not in o.name]
        if objects:
            bpy.ops.object.select_all(action='DESELECT')
            for o in objects:o.select_set(True)
            bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();objects[0].name=name+'__Geometry'
    bpy.ops.object.select_all(action='DESELECT')
    for o in coll.objects:o.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=OUT+'/'+name+'.glb',use_selection=True,export_animations=True,export_apply=True)
    root.location=(len([c for c in bpy.data.collections if c.name.startswith('mc_')])%8*55,len([c for c in bpy.data.collections if c.name.startswith('mc_')])//8*65,0)
    print('EXPORTED',name)

def car(name,kind,color):
    begin(name,'Vehicles')
    L={'compact':3.8,'sports':4.6,'muscle':4.9,'suv':4.8,'pickup':5.3,'van':5.0}.get(kind,4.7)
    w=1.0 if kind in ['suv','pickup','van'] else .9
    hi=1.25 if kind in ['suv','pickup','van'] else 1.02
    if kind=='sports':hi=.82
    body=loft('BodyShell',[(-L/2,.72*w,.32,.64,.69),(-L*.4,w,.27,hi-.12,hi),(-L*.2,w,.27,hi-.04,hi+.05),(L*.25,w,.27,hi-.06,hi),(L*.44,.95*w,.32,.75,.82),(L/2,.79*w,.4,.64,.7)],color)
    for side in [-1,1]:
        for axle in [-L*.31,L*.3]:
            cutter=cyl('WheelArchCutter',(side*w,axle,.37),.405,.65,'rubber','X',32)
            mod=body.modifiers.new('Wheel arch','BOOLEAN')
            mod.object=cutter
            bpy.context.view_layer.objects.active=body
            bpy.ops.object.modifier_apply(modifier=mod.name)
            bpy.data.objects.remove(cutter,do_unlink=True)
    bevel=body.modifiers.new('Coachwork radii','BEVEL');bevel.width=.045;bevel.segments=3
    bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=bevel.name)
    cy=-.25 if kind!='pickup' else .25
    roof=hi+(.51 if kind!='sports' else .4)
    back=-L*.32 if kind not in ['pickup','sports'] else -.5
    front=L*.22
    if kind=='van':back=-L*.4;roof=2.1
    loft('GlassCabin',[(back,w*.82,hi-.04,hi+.04,hi+.06),(back+.5,w*.76,hi,roof-.08,roof),(.45,w*.75,hi,roof-.07,roof),(front,w*.82,hi-.02,hi+.04,hi+.07)],'glass')
    box('Roof',((back+.5+.45)/2,0,0),(1,1,1),color) if False else None
    box('RoofPanel',(0,(back+.5+.45)/2,roof+.008),(w*1.52,max(.25,.45-back-.5),.06),color,.03)
    for s in [-1,1]:
        beam('APillar',(s*w*.82,front,hi),(s*w*.73,.43,roof),.039,color)
        beam('CPillar',(s*w*.82,back,hi),(s*w*.73,back+.5,roof),.055,color)
        beam('BPillar',(s*w*.86,-.15,hi),(s*w*.75,-.15,roof),.036,'black')
        box('BeltTrim',(s*w*.987,-.03,hi-.035),(.025,L*.65,.035),'chrome',.006)
        for y in [-.75,.45]:
            box('DoorHandle',(s*(w+.013),y,hi-.13),(.045,.19,.033),'chrome',.009)
            beam('DoorSeam',(s*w*.994,y-.3,.4),(s*w*.994,y-.3,hi-.055),.006,'black')
        ell('Mirror',(s*(w+.12),.65,hi+.08),(.16,.24,.09),color)
        box('MirrorGlass',(s*(w+.12),.51,hi+.09),(.22,.012,.1),'chrome',.02)
        box('Headlamp',(s*w*.64,L/2-.015,.69),(.47,.035,.115),'headlight',.035)
        box('TailLamp',(s*w*.67,-L/2-.012,.62),(.38,.06,.13),'taillight',.022)
        cyl('Exhaust',(s*.6,-L/2-.04,.31),.058,.25,'chrome','Y')
        for y in [-L*.31,L*.3]:
            wheel=cyl('Wheel_L' if s<0 else 'Wheel_R',(s*w,y,.37),.365,.235,'rubber','X',32)
            hub=cyl('Rim',(s*(w+.125),y,.37),.245,.025,'chrome','X',32)
            cyl('Hub',(s*(w+.143),y,.37),.075,.027,'black','X')
            for a in range(5):
                angle=a*math.tau/5
                beam('Spoke',(s*(w+.145),y,.37),(s*(w+.145),y+math.sin(angle)*.22,.37+math.cos(angle)*.22),.025,'chrome')
        box('Seat',(s*.43,-.12,.82),(.52,.65,.22),'cloth',.08)
        seat=box('SeatBack',(s*.43,-.37,1.07),(.5,.16,.59),'cloth',.06);seat.rotation_euler.x=-.12
    box('Grille',(0,L/2+.006,.5),(1.05,.035,.16),'black',.03)
    for x in range(-5,6):box('GrilleBar',(x*.085,L/2+.028,.5),(.024,.018,.115),'chrome',.005)
    box('FrontPlate',(0,L/2+.035,.37),(.43,.02,.1),'white',.009)
    box('RearPlate',(0,-L/2-.035,.47),(.43,.025,.13),'white',.006)
    box('Dashboard',(0,.64,hi), (1.45,.29,.17),'black',.05)
    bpy.ops.mesh.primitive_torus_add(major_radius=.17,minor_radius=.023,major_segments=24,minor_segments=8,location=(-.43,.4,hi+.15),rotation=(math.pi/3,0,0));own(bpy.context.object,'SteeringWheel','black')
    if kind=='pickup':box('CargoBed',(0,-1.4,1.06),(1.62,1.7,.09),'black',.02)
    if kind=='sports':
        for s in [-1,1]:box('SpoilerMount',(s*.65,-1.76,1.03),(.06,.11,.32),'steel',.02)
        box('Spoiler',(0,-1.78,1.19),(1.85,.31,.06),color,.025)
    if kind=='police':
        box('Lightbar',(0,-.05,roof+.12),(1.1,.24,.08),'black',.02)
        for s in [-1,1]:box('EmergencyLight',(s*.32,-.05,roof+.21),(.44,.2,.15),'blue' if s<0 else 'taillight',.04)
        for s in [-1,1]:box('DoorWhite',(s*(w+.008),-.35,.78),(.014,1.22,.3),'white',.01)
    finish()

def vehicle_roster():
    for name,kind,col in [('mc_sedan','sedan','paint'),('mc_compact','compact','white'),('mc_sport','sports','red'),('mc_muscle','muscle','black'),('mc_suv','suv','white'),('mc_pickup','pickup','paint'),('mc_van','van','white'),('mc_police','police','black'),('mc_taxi','sedan','gold')]:car(name,kind,col)
    begin('mc_motorcycle','Vehicles')
    for y in [-.85,.9]:
        cyl('Wheel',(0,y,.34),.34,.18,'rubber','X',32);cyl('Disc',(.105,y,.34),.23,.025,'chrome','X')
        for s in [-1,1]:beam('Fork',(s*.14,y,.34),(s*.14,y-.2,.85),.035,'chrome')
    beam('Frame',(0,-.7,.4),(0,.65,.87),.1,'steel')
    ell('FuelTank',(0,.2,.97),(.28,.44,.22),'red');box('Saddle',(0,-.37,.87),(.43,.62,.14),'black',.09)
    cyl('Engine',(0,-.08,.54),.22,.43,'steel','X');beam('Handlebar',(-.43,.57,1.12),(.43,.57,1.12),.03,'chrome')
    ell('Headlamp',(0,.88,.9),(.14,.1,.13),'headlight');beam('Exhaust',(.26,-.9,.45),(.26,.15,.43),.057,'chrome');finish()
    begin('mc_boat','Vehicles')
    loft('DeepVHull',[(-2.6,1.05,.12,.85,.95),(-1.6,1.14,-.3,.87,1.0),(.8,.95,-.24,.94,1.12),(2.8,.04,.65,1.03,1.19)],'white')
    box('CockpitFloor',(0,-.4,.91),(1.8,2.6,.08),'wood',.02)
    loft('Windscreen',[(.3,.9,1.0,1.02,1.06),(.0,.8,1.0,1.54,1.59),(-.3,.8,1.,1.54,1.59)],'glass')
    for s in [-1,1]:
        box('Seat',(s*.47,-.7,1.04),(.55,.7,.22),'white',.08);box('SeatBack',(s*.47,-1.,1.3),(.55,.13,.52),'white',.06)
        beam('Rail',(s*.97,-1.5,1.15),(s*.7,1.5,1.34),.022,'chrome')
    box('Outboard',(0,-2.66,.49),(.5,.46,1.),'black',.1);finish()
    for police in [False,True]:
        begin('mc_police_helicopter' if police else 'mc_helicopter','Vehicles')
        ell('Fuselage',(0,0,1.65),(1.02,2.2,1.05),'black' if police else 'white',32,20)
        ell('Cockpit',(0,1.23,1.86),(.91,1.13,.72),'glass',28,16)
        beam('TailBoom',(0,-1.4,1.7),(0,-6.0,2.1),.23,'steel')
        mesh('TailFin',[(-.05,-5.4,2.),(-.05,-6.1,2.),(-.05,-6.3,3.5),(-.05,-5.8,3.3),(.05,-5.4,2.),(.05,-6.1,2.),(.05,-6.3,3.5),(.05,-5.8,3.3)],[(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7)],'white')
        cyl('RotorMast',(0,0,2.97),.14,.7,'steel')
        rotor=box('Rotor',(0,0,3.34),(10.4,.18,.055),'black',.01)
        box('RotorCross',(0,0,3.35),(.18,10.4,.055),'black',.01)
        box('TailRotor',(.3,-5.95,2.45),(.04,.16,1.7),'black',.01)
        for s in [-1,1]:
            beam('Skid',(s*1.12,-1.7,.3),(s*1.12,1.7,.3),.055,'steel')
            for y in [-.9,.9]:beam('Strut',(s*.65,y,1.05),(s*1.12,y,.3),.045,'chrome')
            box('DoorWindow',(s*.985,-.05,1.94),(.025,1.2,.64),'glass',.13)
        finish()
    begin('mc_plane','Vehicles')
    ell('Fuselage',(0,0,1.25),(.63,3.6,.66),'white',32,20)
    ell('Cockpit',(0,.45,1.67),(.58,1.14,.46),'glass')
    mesh('Wings',[(-6,-.5,1.25),(-5.8,.52,1.31),(-.4,1.1,1.35),(.4,1.1,1.35),(5.8,.52,1.31),(6,-.5,1.25),(.4,-.5,1.24),(-.4,-.5,1.24)],[(0,1,2,7),(3,4,5,6),(7,2,3,6)],'white')
    box('Tailplane',(0,-2.9,1.47),(3.5,.73,.095),'red',.05)
    mesh('TailFin',[(0,-3.4,1.3),(0,-3.25,2.8),(0,-2.6,2.6),(0,-2.35,1.4)],[(0,1,2,3)],'red')
    cyl('PropellerHub',(0,3.53,1.25),.15,.2,'chrome','Y');box('Propeller',(0,3.67,1.25),(.11,.055,2.4),'black',.03)
    for x,y in [(-1.2,.3),(1.2,.3),(0,-2.65)]:
        beam('LandingStrut',(x*.5,y,1.1),(x,y,.26),.048,'chrome');cyl('Wheel',(x,y,.24),.24,.18,'rubber','X')
    finish()

def save_master():
    bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/GodotGTA.blend')
