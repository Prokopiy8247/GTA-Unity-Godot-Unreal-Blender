import bpy,math,json,random,bmesh
from mathutils import Vector
OUT=bpy.path.abspath('//Assets/GTA/Generated/Models').replace(chr(92),'/')
M={m.name:m for m in bpy.data.materials};groups={'Vehicles':bpy.data.collections['Vehicles']};asset_names=[]
for o in bpy.context.scene.objects:o.hide_set(False);o.select_set(False)
state={'current':None}
def begin(n,g):
 state['current']=bpy.data.collections.new(n);groups[g].children.link(state['current'])
def reg(o,n,m):
 o.name=n
 for c in list(o.users_collection):c.objects.unlink(o)
 state['current'].objects.link(o);o.data.materials.append(M[m]);return o
def mesh(n,vs,fs,m,b=0):
 me=bpy.data.meshes.new(n+'_mesh');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);state['current'].objects.link(o);me.materials.append(M[m])
 if b:mod=o.modifiers.new('Edge bevel','BEVEL');mod.width=b;mod.segments=2
 return o
def box(n,p,s,m,b=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=reg(bpy.context.object,n,m);o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:mod=o.modifiers.new('Edge bevel','BEVEL');mod.width=b;mod.segments=2
 return o
def ell(n,p,s,m,seg=20,rings=12):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,radius=1,location=p);o=reg(bpy.context.object,n,m);o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for f in o.data.polygons:f.use_smooth=True
 return o
def cyl(n,a,b,r,m,verts=16,r2=None):
 d=Vector(b)-Vector(a);p=(Vector(a)+Vector(b))*.5
 bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r,radius2=r if r2 is None else r2,depth=d.length,location=p);o=reg(bpy.context.object,n,m);o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return o
def loft(n,sections,m):
 vs=[]
 for y,w,b,s,t in sections:vs.extend([(-w*.86,y,b),(w*.86,y,b),(w,y,s),(w*.91,y,t-.05),(w*.66,y,t),(-w*.66,y,t),(-w*.91,y,t-.05),(-w,y,s)])
 fs=[tuple(range(7,-1,-1))]
 for i in range(len(sections)-1):
  for k in range(8):a=i*8+k;b=i*8+(k+1)%8;fs.append((a,b,b+8,a+8))
 fs.append(tuple(range((len(sections)-1)*8,len(sections)*8)));return mesh(n,vs,fs,m,.025)
def join(items,n,p=(0,0,0)):
 bpy.ops.object.select_all(action='DESELECT')
 for o in items:
  o.select_set(True);bpy.context.view_layer.objects.active=o
  for m in list(o.modifiers):
   try:bpy.ops.object.modifier_apply(modifier=m.name)
   except Exception:pass
 bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object;o.name=n;bpy.context.scene.cursor.location=p;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
def finish(n):
 obs=list(state['current'].objects);fixed=[o for o in obs if not o.name.startswith(('Wheel_','Rotor','Arm_','Leg_','Head'))]
 if fixed:join(fixed,'Body')
 obs=list(state['current'].objects);bpy.ops.object.select_all(action='DESELECT')
 for o in obs:
  o.select_set(True)
  if not o.data.uv_layers:o.data.uv_layers.new(name='SurfaceUV')
  for f in o.data.polygons:
   for li in f.loop_indices:
    v=o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers[0].data[li].uv=(v.x+v.y*.23,v.z+v.y*.23)
 bpy.context.view_layer.objects.active=obs[0]
 for o in obs:
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 bpy.ops.object.shade_smooth_by_angle(angle=.5,keep_sharp_edges=False)
 bpy.ops.export_scene.fbx(filepath=OUT+'/'+n+'.fbx',use_selection=True,axis_forward='-Z',axis_up='Y',apply_scale_options='FBX_SCALE_ALL',bake_anim=False,add_leaf_bones=False)
 asset_names.append(n);i=len(asset_names)-1
 for o in state['current'].objects:o.location+=Vector(((i%9)*35,(i//9)*42,0))
 print('EXPORTED',n)
def wheel(x,y,z,r=.35,w=.23,n='Wheel'):
 before=set(state['current'].objects);cyl('Tire',(x-w*.5,y,z),(x+w*.5,y,z),r,'Rubber',32)
 for side in [-1,1]:
  sx=x+side*w*.51;cyl('Rim',(sx-.012,y,z),(sx+.012,y,z),r*.69,'Chrome',24);cyl('Hub',(sx-.018,y,z),(sx+.018,y,z),r*.22,'Metal',20)
  for i in range(7):
   a=i*math.tau/7;cyl('Spoke',(sx,y+math.cos(a)*r*.21,z+math.sin(a)*r*.21),(sx,y+math.cos(a)*r*.64,z+math.sin(a)*r*.64),.022,'Metal',6)
 join(list(set(state['current'].objects)-before),n,(x,y,z))
def car(n,style,length,width,h,paint):
 begin(n,'Vehicles');L=length/2;w=width/2
 loft('Sculpted body',[(-L,w*.85,.42,.63,.85),(-L*.86,w,.38,.78,1),(-L*.45,w,.42,.86,1.04),(0,w,.43,.88,1.01),(L*.64,w*.94,.4,.76,.96),(L,w*.79,.44,.64,.79)],paint)
 rear=-L*.55 if style not in ['pickup','van'] else -L*.18;front=L*.35
 if style in ['suv','van']:rear=-L*.8;front=L*.5
 if style=='sport':rear=-L*.48;front=L*.43
 loft('Cabin',[(rear,w*.84,.94,1.06,1.12),(rear+.38,w*.77,1,h-.1,h),(front-.36,w*.72,1,h-.1,h),(front,w*.82,.95,1.04,1.12)],'Glass')
 box('Roof',(0,(rear+front)*.5,h+.007),(width*.71,max(.2,front-rear-.65),.06),paint,.04)
 for s in [-1,1]:
  cyl('A pillar',(s*w*.8,front,1),(s*w*.7,front-.37,h),.045,paint);cyl('C pillar',(s*w*.82,rear,1.01),(s*w*.73,rear+.4,h),.065,paint);cyl('B pillar',(s*w*.86,-.12,1),(s*w*.74,-.12,h),.033,'Metal')
  box('Belt trim',(s*w*.96,0,.98),(.025,length*.67,.025),'Chrome',.008);box('Handle',(s*w*1.01,-.35,.88),(.035,.17,.035),'Chrome',.012);box('Mirror',(s*(w+.09),front-.08,1.06),(.23,.23,.115),paint,.04);box('Sill',(s*w,0,.4),(.065,length*.64,.09),'Metal')
  for y in [-L*.59,L*.61]:wheel(s*w*.95,y,.41 if style=='suv' else .36,.4 if style=='suv' else .35,.24,'Wheel_'+('L' if s<0 else 'R')+('F' if y>0 else 'R'))
  box('Headlight',(s*w*.64,L*.94,.71),(width*.24,.09,.13),'Lamp');box('Taillight',(s*w*.68,-L*.96,.75),(width*.21,.08,.15),'Tail');box('Seat',(s*.43,-.22,.87),(.43,.52,.17),'Interior',.07);box('Seat back',(s*.43,-.48,1.05),(.42,.13,.57),'Interior',.05)
 box('Front intake',(0,L*.985,.54),(width*.57,.055,.16),'Rubber',.02)
 for x in [-.45,-.22,0,.22,.45]:box('Grille',(x,L*1.004,.54),(.015,.03,.125),'Chrome',.003)
 box('Rear bumper',(0,-L,.48),(width*.86,.08,.1),'Metal');box('Plate',(0,-L-.047,.7),(.42,.025,.105),'White',.008);box('Dashboard',(0,front-.03,1.02),(width*.75,.23,.16),'Interior');cyl('Steering',(-.43,front-.2,1.13),(-.43,front-.24,1.13),.16,'Rubber',24)
 if style=='pickup':
  box('Bed',(0,-L*.61,.89),(width*.82,L*.62,.08),'Rubber')
  for s in [-1,1]:box('Bed rail',(s*w*.9,-L*.61,1.1),(.1,L*.69,.4),paint)
 if style=='sport':
  box('Spoiler',(0,-L*.78,1.18),(width*.92,.24,.05),'Metal')
  for s in [-1,1]:box('Support',(s*.5,-L*.78,1.07),(.045,.1,.25),'Metal')
 if style=='police':
  box('Lightbar',(0,-.1,h+.1),(1.15,.27,.1),'Metal')
  for s in [-1,1]:box('Beacon',(s*.35,-.1,h+.18),(.48,.23,.1),'Tail' if s<0 else 'BlueLight');box('White door',(s*(w+.016),-.1,.73),(.025,1.05,.34),'White')
  box('Push bar',(0,L+.07,.55),(width*.73,.13,.17),'Metal')
 finish(n)

for args in [('Aster_Sedan','sedan',4.7,1.86,1.48,'Paint'),('Mica_Compact','compact',3.65,1.73,1.49,'Pearl'),('Vela_Sport','sport',4.35,1.93,1.22,'RedPaint'),('Bison_Muscle','sport',4.9,1.98,1.36,'Paint'),('Atlas_SUV','suv',4.95,2.02,1.85,'Pearl'),('Ranger_Pickup','pickup',5.45,2.02,1.76,'RedPaint'),('Courier_Van','van',5.2,2.06,2.2,'Pearl'),('Sentinel_Police','police',4.95,1.94,1.53,'Paint'),('Metro_Taxi','sedan',4.75,1.9,1.55,'Gold')]:
 coll=bpy.data.collections.get(args[0])
 if coll:
  for o in list(coll.objects):bpy.data.objects.remove(o,do_unlink=True)
  bpy.data.collections.remove(coll)
 for o in bpy.context.scene.objects:o.select_set(False)
 car(*args)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Rebuilt complete shells with consistent outward normals; all glazing and roofs preserved.')

