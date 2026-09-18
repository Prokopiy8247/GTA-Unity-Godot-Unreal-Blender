"""Original assets, executed inside UnityGTA.blend via blender_unity MCP."""
import bpy, math, json, random
from mathutils import Vector
ROOT=bpy.path.abspath('//').replace(chr(92),'/').rstrip('/')
assert bpy.data.filepath.replace(chr(92),'/').endswith('/UnityGTA.blend')
OUT=ROOT+'/Assets/GTA/Generated/Models'
random.seed(2841);M={};asset_names=[]
def mat(n,c,metal=0,rough=.55,emission=0):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1)
 p=next(x for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED')
 for k,v in [('Base Color',(*c,1)),('Metallic',metal),('Roughness',rough),('Emission Color',(*c,1)),('Emission Strength',emission)]:p.inputs[k].default_value=v
 M[n]=m
for a in [('Paint',(.055,.17,.22),.72,.24),('Pearl',(.65,.7,.72),.5,.28),('RedPaint',(.36,.025,.02),.65,.26),('Rubber',(.015,.019,.022),0,.82),('Chrome',(.55,.61,.66),.92,.18),('Metal',(.15,.19,.22),.78,.42),('Glass',(.035,.105,.14),.62,.13),('Interior',(.028,.034,.041),0,.85),('Lamp',(.84,.89,.82),.1,.2,3),('Tail',(.5,.012,.007),.25,.2,2),('BlueLight',(.01,.14,.9),.1,.2,4),('Amber',(.95,.36,.035),0,.4,.5),('Concrete',(.47,.46,.42),0,.9),('Plaster',(.69,.65,.56),0,.82),('Brick',(.32,.16,.105),0,.91),('Facade',(.23,.27,.29),.25,.6),('Window',(.11,.22,.28),.68,.18),('WarmWindow',(.62,.47,.24),.3,.3,.45),('Wood',(.23,.14,.075),0,.85),('Foliage',(.075,.18,.075),0,.92),('Trunk',(.18,.12,.07),0,1),('Skin',(.52,.31,.19),0,.68),('SkinLight',(.69,.46,.32),0,.68),('SkinDark',(.27,.135,.082),0,.72),('Jacket',(.085,.11,.14),0,.88),('Shirt',(.39,.43,.42),0,.92),('Denim',(.09,.14,.19),0,.94),('Hair',(.035,.024,.018),0,.86),('PoliceCloth',(.025,.045,.095),0,.83),('White',(.78,.78,.73),0,.7),('Gunmetal',(.07,.085,.093),.8,.33),('Grip',(.025,.028,.027),0,.93),('Sand',(.61,.53,.38),0,.98),('Rock',(.3,.32,.29),0,.94),('Canvas',(.64,.14,.055),0,.8),('Gold',(.7,.5,.15),.7,.32)]:mat(*a)
master=bpy.data.collections.get('GTA_UNITY')
if master:
 for o in list(master.all_objects):bpy.data.objects.remove(o,do_unlink=True)
 for c in list(master.children):bpy.data.collections.remove(c)
else:
 master=bpy.data.collections.new('GTA_UNITY');bpy.context.scene.collection.children.link(master)
groups={}
for n in ['Vehicles','Characters','Weapons','Buildings','StreetProps','Nature','Interiors']:
 c=bpy.data.collections.new(n);master.children.link(c);groups[n]=c
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
def bike(n,bicycle=False):
 begin(n,'Vehicles')
 for y in [-.75,.78]:wheel(0,y,.35,.35,.055 if bicycle else .18,'Wheel_'+('F' if y>0 else 'R'))
 for a,b in [((0,-.75,.35),(0,-.1,.85)),((0,-.1,.85),(0,.6,.9)),((0,.6,.9),(0,.78,.35)),((0,-.1,.85),(0,.22,.36)),((0,.22,.36),(0,-.75,.35))]:cyl('Frame',a,b,.025 if bicycle else .065,'Chrome' if bicycle else 'Metal')
 box('Saddle',(0,-.22,1),(.24,.42,.12),'Interior',.05);cyl('Handlebar',(-.36,.55,1.14),(.36,.55,1.14),.025,'Metal')
 if not bicycle:ell('Tank',(0,.15,.88),(.23,.4,.22),'RedPaint');box('Engine',(0,-.03,.5),(.36,.4,.35),'Metal');cyl('Headlamp',(0,.74,.94),(0,.84,.94),.12,'Lamp',24);cyl('Exhaust',(.25,-.65,.38),(.25,.1,.4),.055,'Chrome')
 finish(n)
def boat():
 n='Kestrel_Boat';begin(n,'Vehicles');loft('Deep V hull',[(-2.6,.86,.15,.62,.92),(-1.8,1.1,-.2,.64,1),(.4,1,-.15,.64,1.04),(1.8,.6,.2,.7,1.13),(2.7,.025,.72,.98,1.17)],'Pearl');box('Deck',(0,-.1,.98),(1.55,3.6,.1),'Wood',.08);loft('Windshield',[(-.1,.76,1.02,1.2,1.52),(.6,.7,1.01,1.15,1.3)],'Glass')
 for x in [-.46,.46]:box('Seat',(x,-.95,1.12),(.5,.62,.25),'Interior',.1)
 box('Motor',(0,-2.7,.59),(.5,.55,.82),'Metal',.1);finish(n)
def aircraft(n,heli=True,police=False):
 begin(n,'Vehicles')
 if heli:
  ell('Fuselage',(0,0,1.5),(1,2.05,.96),'Pearl' if police else 'Paint',32,20);ell('Cockpit',(0,1.18,1.68),(.91,1,.68),'Glass',32,16);cyl('Tail boom',(0,-1.5,1.65),(0,-6,2),.36,'Metal',16,.10);box('Tail fin',(0,-5.7,2.6),(.1,.8,1.5),'Paint');cyl('Mast',(0,0,2.1),(0,0,3.1),.1,'Metal');rot=[]
  for a in [0,math.pi/2]:o=box('Blade',(0,0,3.08),(.22,9.6,.055),'Metal');o.rotation_euler.z=a;rot.append(o)
  join(rot,'Rotor_Main',(0,0,3.08));box('Rotor_Tail',(.16,-5.8,2.45),(.055,.14,1.75),'Metal')
  for x in [-1,1]:
   cyl('Landing skid',(x,-1.6,.2),(x,1.6,.2),.065,'Metal')
   for y in [-.7,.7]:cyl('Skid strut',(x,y,.2),(x*.65,y,1.1),.048,'Metal')
  if police:ell('Searchlight',(0,1.4,.85),(.2,.2,.18),'Lamp')
 else:
  loft('Fuselage',[(-4,.1,.9,1.1,1.2),(-2,.4,.5,1.1,1.4),(0,.64,.45,1.3,1.65),(2.4,.48,.64,1.2,1.5),(3.1,.17,.94,1.1,1.22)],'Pearl');ell('Cockpit',(0,.5,1.52),(.53,1,.34),'Glass')
  mesh('Wings',[(-5.2,-.6,1.08),(5.2,-.6,1.08),(5.2,.15,1.13),(.6,1,1.22),(-.6,1,1.22),(-5.2,.15,1.13),(-5.2,-.6,1),(5.2,-.6,1),(5.2,.15,1.05),(.6,1,1.12),(-.6,1,1.12),(-5.2,.15,1.05)],[(0,1,2,3,4,5),(11,10,9,8,7,6),(0,6,7,1),(1,7,8,2),(2,8,9,3),(3,9,10,4),(4,10,11,5),(5,11,6,0)],'Pearl',.025)
  box('Tailplane',(0,-3.25,1.12),(3.5,.65,.08),'Pearl');box('Tail fin',(0,-3.1,1.85),(.09,.9,1.55),'RedPaint');box('Rotor_Prop',(0,3.18,1.13),(.14,.075,2.3),'Metal')
  for x,y in [(-1.2,0),(1.2,0),(0,2.1)]:cyl('Gear',(x,y,.28),(x*.6,y,.92),.04,'Metal');wheel(x,y,.25,.23,.11,'Wheel_'+str(x))
 finish(n)
def character(n,female=False,police=False,dark=False):
 begin(n,'Characters');skin='SkinDark' if dark else 'SkinLight';cloth='PoliceCloth' if police else 'Jacket'
 loft('Torso',[(-.14,.17,.93,1.2,1.46),(0,.22,.94,1.24,1.48),(.16,.18,.94,1.23,1.43)],cloth);ell('Hips',(0,0,.93),(.19,.14,.19),'Denim');cyl('Neck',(0,0,1.44),(0,0,1.58),.062,skin)
 for z in [1.1,1.2,1.3,1.4]:ell('Button',(0,.165,z),(.009,.007,.009),'Metal',8,6)
 box('Belt',(0,0,1.015),(.36,.295,.045),'Interior',.012);box('Buckle',(0,.151,1.015),(.055,.015,.04),'Chrome',.003)
 for side in [-1,1]:
  x=.22*side;before=set(state['current'].objects);cyl('Sleeve',(x,0,1.4),(x+side*.04,.01,1.13),.085,cloth,16,.061);cyl('Forearm',(x+side*.04,.01,1.15),(x+side*.04,.035,.94),.06,skin,16,.042);ell('Hand',(x+side*.04,.035,.89),(.045,.034,.078),skin)
  for k in range(4):cyl('Finger',(x+side*.04+(k-1.5)*.018,.043,.87),(x+side*.04+(k-1.5)*.018,.052,.803+abs(k-1.5)*.01),.009,skin,8,.006)
  join(list(set(state['current'].objects)-before),'Arm_'+('L' if side<0 else 'R'),(x,0,1.4));before=set(state['current'].objects);x=side*.104
  cyl('Thigh',(x,0,.94),(x,.015,.53),.102,'Denim',16,.076);cyl('Calf',(x,.015,.55),(x,0,.13),.077,'Denim',16,.052);ell('Shoe',(x,.065,.077),(.075,.16,.067),'Interior');box('Sole',(x,.069,.035),(.146,.28,.028),'Rubber',.013);join(list(set(state['current'].objects)-before),'Leg_'+('L' if side<0 else 'R'),(x,0,.94))
 before=set(state['current'].objects);ell('Skull',(0,.004,1.668),(.086,.089,.119),skin,24,18);ell('Jaw',(0,.026,1.603),(.069,.072,.065),skin);ell('Nose',(0,.094,1.661),(.019,.034,.037),skin)
 for s in [-1,1]:
  ell('Ear',(s*.087,0,1.659),(.017,.023,.034),skin);ell('Eye',(s*.033,.084,1.69),(.017,.008,.009),'White');ell('Iris',(s*.033,.091,1.69),(.007,.003,.007),'Hair');box('Brow',(s*.033,.086,1.708),(.036,.01,.007),'Hair',.003)
 box('Mouth',(0,.09,1.616),(.042,.007,.005),'SkinDark',.002);ell('Hair',(0,-.016,1.732),(.091,.087,.075),'Hair')
 if female:ell('Hair back',(0,-.078,1.64),(.093,.035,.17),'Hair')
 if police:cyl('Cap',(0,0,1.765),(0,0,1.82),.098,'PoliceCloth',24);box('Visor',(0,.075,1.768),(.18,.14,.012),'Interior',.025)
 join(list(set(state['current'].objects)-before),'Head',(0,0,1.52))
 if police:box('Vest',(0,.145,1.27),(.32,.05,.31),'Interior');box('Badge',(-.075,.18,1.38),(.035,.009,.042),'Gold',.004);box('Radio',(.15,.13,1.35),(.06,.06,.1),'Metal')
 finish(n)
def weapon(n,k):
 begin(n,'Weapons')
 if k=='knife':
  box('Grip',(0,-.12,0),(.045,.19,.045),'Grip');mesh('Blade',[(-.025,0,-.005),(.025,0,-.005),(.015,.22,0),(0,.3,0),(-.025,0,.005),(.025,0,.005)],[(0,1,2,3),(4,3,2,5),(0,4,5,1),(1,5,2),(0,3,4)],'Chrome')
 elif k=='bat':cyl('Bat',(0,-.2,0),(0,.65,0),.022,'Wood',20,.046)
 elif k=='grenade':ell('Grenade',(0,0,0),(.06,.07,.09),'Metal');box('Lever',(.025,0,.07),(.04,.1,.015),'Chrome')
 else:
  pistol=k in ['pistol','heavy'];long=k in ['rifle','carbine','marksman','sniper','shotgun','rocket'];length=.3 if pistol else .54 if k=='smg' else .92
  box('Receiver',(0,.14,.08),(.07,length*.43,.09),'Gunmetal',.01);o=box('Grip',(0,.01,-.025),(.059,.11,.17),'Grip',.012);o.rotation_euler.x=-.24;cyl('Barrel',(0,.18,.103),(0,length,.103),.021 if k!='rocket' else .1,'Gunmetal',24)
  if long:
   box('Stock',(0,-.24,.04),(.065,.35,.15),'Grip',.025);box('Handguard',(0,.43,.078),(.095,.28,.1),'Grip',.012)
   for y in [.32,.37,.42,.47,.52]:box('Rail',(0,y,.14),(.08,.018,.018),'Metal',.003)
  if k not in ['shotgun','rocket','heavy']:box('Magazine',(0,.19,-.08),(.046,.077,.2),'Metal',.009)
  if k in ['sniper','marksman']:cyl('Scope',(0,-.02,.23),(0,.37,.23),.044,'Metal',24);cyl('Lens',(0,.373,.23),(0,.379,.23),.035,'Glass',20)
  box('Sight',(0,length*.73,.166),(.015,.018,.042),'Metal',.002)
  for x in [-.024,.024]:cyl('Trigger guard',(x,-.065,-.015),(x,.1,-.09),.007,'Metal',8)
 finish(n)
def building(n,style,w,d,h):
 begin(n,'Buildings');box('Structure',(0,0,h/2),(w,d,h),'Facade' if style=='office' else 'Brick' if style=='apartment' else 'Plaster' if style=='house' else 'Concrete',.08)
 if style=='house':
  mesh('Pitched roof',[(-w*.56,-d*.55,h),(w*.56,-d*.55,h),(0,-d*.55,h+2),(-w*.56,d*.55,h),(w*.56,d*.55,h),(0,d*.55,h+2)],[(0,1,2),(5,4,3),(0,2,5,3),(2,1,4,5),(0,3,4,1)],'Brick');box('Chimney',(w*.26,0,h+1.2),(.7,.7,2),'Brick')
 else:
  box('Cornice',(0,0,h),(w+.6,d+.6,.4),'Concrete')
  for x in [-w*.26,w*.26]:box('Rooftop HVAC',(x,0,h+.55),(2.3,2.4,1.1),'Metal')
 floors=max(1,int(h/3.3));cols=max(2,int(w/3))
 for side in [-1,1]:
  for level in range(floors):
   z=level*3.3+1.9
   if z>h-.3:continue
   for col in range(cols):
    x=(col-(cols-1)*.5)*(w/(cols+.3));mw=w/(cols+.3)*.72;box('Window',(x,side*(d/2+.04),z),(mw,.08,1.72),'WarmWindow' if random.random()<.18 else 'Window',.02);box('Sill',(x,side*(d/2+.13),z-.91),(mw+.15,.29,.12),'Concrete',.015);box('Mullion',(x,side*(d/2+.1),z),(.05,.07,1.72),'Metal',.003)
    if style=='apartment':box('Balcony',(x,side*(d/2+.53),z-.97),(mw+.3,1.15,.15),'Concrete');box('Balcony rail',(x,side*(d/2+1.04),z-.45),(mw+.3,.07,.84),'Glass')
   if style!='house':box('Band',(0,side*(d/2+.07),level*3.3+.3),(w+.2,.16,.17),'Concrete')
  if style in ['office','apartment']:
   for level in range(floors):
    for y in [-d*.3,0,d*.3]:box('Side window',(side*(w/2+.04),y,level*3.3+1.9),(.08,d*.21,1.75),'Window',.015)
 box('Entry',(0,d/2+.16,1.6),(2.3,.3,3.2),'Metal');box('Door glass',(0,d/2+.33,1.5),(1.9,.035,2.85),'Glass');box('Canopy',(0,d/2+1.1,3.1),(4.6,2.5,.15),'Metal')
 if style=='warehouse':
  for x in [-w*.28,w*.28]:
   box('Shutter',(x,d/2+.12,2.5),(w*.3,.12,5),'Metal')
   for z in [i*.35 for i in range(1,14)]:box('Shutter seam',(x,d/2+.19,z),(w*.3,.035,.025),'Chrome',.001)
 finish(n)
def props():
 begin('Streetlamp','StreetProps');cyl('Post',(0,0,0),(0,0,7),.09,'Metal');cyl('Arm',(0,0,6.8),(0,1.7,7.1),.055,'Metal');box('Luminaire',(0,1.6,7.06),(.4,.95,.12),'Metal');box('Light',(0,1.65,6.99),(.3,.7,.025),'Lamp');finish('Streetlamp')
 begin('TrafficSignal','StreetProps');cyl('Post',(0,0,0),(0,0,4.2),.07,'Metal');box('Housing',(0,.09,3.5),(.36,.24,1.02),'Metal')
 for z,m in [(3.82,'Tail'),(3.5,'Amber'),(3.18,'Foliage')]:cyl('Lens',(0,.21,z),(0,.24,z),.105,m,20)
 finish('TrafficSignal');begin('Bench','StreetProps')
 for y in [-.22,-.07,.08,.23]:box('Seat plank',(0,y,.5),(1.8,.12,.07),'Wood')
 for z in [.72,.86,1]:box('Back plank',(0,-.26,z),(1.8,.07,.11),'Wood')
 for x in [-.65,.65]:box('Leg',(x,0,.25),(.07,.46,.5),'Metal')
 finish('Bench');begin('Hydrant','StreetProps');cyl('Body',(0,0,.08),(0,0,.75),.13,'RedPaint',20);ell('Cap',(0,0,.75),(.16,.16,.1),'RedPaint');cyl('Outlet',(-.22,0,.54),(.22,0,.54),.08,'Metal');finish('Hydrant')
 begin('Bin','StreetProps');box('Bin',(0,0,.51),(.57,.56,1.02),'Metal',.07);box('Lid',(0,0,1.05),(.62,.6,.06),'Rubber');finish('Bin')
 begin('Barrier','StreetProps');loft('Barrier',[(-1.5,.4,0,.3,.85),(1.5,.4,0,.3,.85)],'Concrete');finish('Barrier')
 begin('Container','StreetProps');box('Container',(0,0,1.3),(2.45,6,2.6),'RedPaint')
 for x in [-1.235,1.235]:
  for y in [i*.28-2.8 for i in range(21)]:box('Corrugation',(x,y,1.3),(.06,.085,2.5),'RedPaint',.012)
 for x in [-.65,.65]:cyl('Door bar',(x,3.05,.15),(x,3.05,2.4),.025,'Chrome')
 finish('Container');begin('PortCrane','StreetProps')
 for x in [-4,4]:
  for y in [-4,4]:cyl('Leg',(x,y,0),(x*.7,y*.7,24),.36,'Metal')
 box('Gantry',(0,0,24),(9,9,1.2),'Amber');box('Boom',(0,8,27),(1.2,35,1.4),'Amber')
 for y in range(-8,25,3):cyl('Truss',(-.5,y,26.6),(.5,y+3,27.6),.1,'Metal')
 cyl('Cable',(0,19,27),(0,19,5),.055,'Metal');finish('PortCrane')
 begin('Parachute','StreetProps');ell('Canopy',(0,0,5.6),(3.1,1.8,.65),'Canvas',32,16)
 for x in [-2.8,-1.4,1.4,2.8]:
  for y in [-1.1,1.1]:cyl('Cord',(x,y,5.5),(x*.06,y*.1,1.35),.009,'White',6)
 finish('Parachute');begin('Target','StreetProps');box('Stand',(0,0,.65),(.08,.12,1.3),'Metal');cyl('Target board',(0,-.04,1.6),(0,.04,1.6),.42,'White',32);cyl('Bullseye',(0,.046,1.6),(0,.049,1.6),.12,'Tail',32);finish('Target')
def nature():
 for n,palm in [('Oak',False),('Palm',True)]:
  begin(n,'Nature');h=8 if palm else 6;cyl('Trunk',(0,0,0),(.25,0,h),.3 if palm else .4,'Trunk',16,.13)
  if palm:
   for i in range(12):
    a=i*math.tau/12;vs=[]
    for j in range(7):
     r=j*.65;z=h+.7*math.sin(j/6*math.pi)-j*.12;p=Vector((math.cos(a)*r,math.sin(a)*r,z));side=Vector((-math.sin(a),math.cos(a),0))*.3*math.sin((j+.5)/7*math.pi);vs.extend([tuple(p-side),tuple(p+side)])
    mesh('Frond',vs,[(j*2,j*2+1,j*2+3,j*2+2) for j in range(6)],'Foliage')
  else:
   for i in range(11):
    a=i*2.4;r=1.7 if i>0 else 0;z=h+random.uniform(-1.3,1.4);end=(math.cos(a)*r,math.sin(a)*r,z);cyl('Branch',(0,0,h-2),end,.13,'Trunk',10,.04);ell('Crown',end,(1.7,1.6,1.65),'Foliage',12,8)
  finish(n)
 begin('Rock','Nature');o=ell('Boulder',(0,0,.65),(1.2,.9,.95),'Rock',12,8)
 for v in o.data.vertices:v.co*=random.uniform(.83,1.15)
 finish('Rock');begin('Deer','Nature');ell('Body',(0,0,.92),(.28,.66,.37),'Wood');ell('Neck',(0,.52,1.27),(.17,.24,.42),'Wood');ell('Head',(0,.7,1.57),(.15,.29,.17),'Wood')
 for x in [-.19,.19]:
  for y in [-.43,.4]:cyl('Leg',(x,y,.85),(x,y,.07),.055,'Wood',10,.035)
 for x in [-.13,.13]:ell('Ear',(x,.58,1.8),(.08,.055,.14),'Wood')
 finish('Deer')
def build_all():
 for a in [('Aster_Sedan','sedan',4.7,1.86,1.48,'Paint'),('Mica_Compact','compact',3.65,1.73,1.49,'Pearl'),('Vela_Sport','sport',4.35,1.93,1.22,'RedPaint'),('Bison_Muscle','sport',4.9,1.98,1.36,'Paint'),('Atlas_SUV','suv',4.95,2.02,1.85,'Pearl'),('Ranger_Pickup','pickup',5.45,2.02,1.76,'RedPaint'),('Courier_Van','van',5.2,2.06,2.2,'Pearl'),('Sentinel_Police','police',4.95,1.94,1.53,'Paint'),('Metro_Taxi','sedan',4.75,1.9,1.55,'Gold')]:car(*a)
 bike('Arrow_Motorcycle');bike('Comet_Bicycle',True);boat();aircraft('Heron_Helicopter');aircraft('Watch_PoliceHeli',True,True);aircraft('Swift_Plane',False)
 character('Player');character('Pedestrian_M',dark=True);character('Pedestrian_F',female=True);character('Officer',police=True);character('Tactical',police=True,dark=True)
 for n,k in [('Knife','knife'),('Baton','bat'),('Pistol','pistol'),('HeavyPistol','heavy'),('SMG','smg'),('Shotgun','shotgun'),('Rifle','rifle'),('Carbine','carbine'),('Marksman','marksman'),('Sniper','sniper'),('Grenade','grenade'),('Launcher','rocket')]:weapon(n,k)
 for a in [('OfficeTower','office',24,22,66),('OfficeMid','office',19,18,29),('Apartment','apartment',20,15,19),('House','house',10,9,3.1),('Warehouse','warehouse',32,25,8),('Hangar','warehouse',42,36,12),('Storefront','warehouse',14,10,4.5),('Parking','office',27,24,9.7)]:building(*a)
 props();nature()
 bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/UnityGTA.blend');print('MERIDIAN_ASSETS',len(asset_names))
build_all()


