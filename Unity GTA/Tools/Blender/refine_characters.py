import bpy,math
from mathutils import Vector,Quaternion
BASE=bpy.path.abspath('//').replace(chr(92),'/')
state={'collection':None,'parts':[]}
def skin_surface(name,rings,material):
 vs=[];fs=[];N=24
 for z,x,rx,front,back in rings:
  for j in range(N):
   a=j*math.tau/N;s=math.sin(a);vs.append((x+math.cos(a)*rx,s*(front if s>=0 else back),z))
 for k in range(len(rings)-1):
  for j in range(N):fs.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
 fs.extend([tuple(range(N-1,-1,-1)),tuple(range((len(rings)-1)*N,len(rings)*N))])
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();me.materials.append(bpy.data.materials[material]);o=bpy.data.objects.new(name,me);state['collection'].objects.link(o)
 for f in me.polygons:f.use_smooth=True
 uv=me.uv_layers.new(name='TailoredUV')
 for f in me.polygons:
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x*3+v.y,v.z*3)
 state['parts'].append(o);return o
def oval(name,loc,size,material):
 for o in bpy.context.scene.objects:o.select_set(False)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1,location=loc)
 o=bpy.context.object;o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 state['collection'].objects.link(o);o.data.materials.append(bpy.data.materials[material])
 for f in o.data.polygons:f.use_smooth=True
 state['parts'].append(o);return o
def detail(name,loc,size,material,bevel=.008):
 for o in bpy.context.scene.objects:o.select_set(False)
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 state['collection'].objects.link(o);o.data.materials.append(bpy.data.materials[material]);mod=o.modifiers.new('Tailoring edge','BEVEL');mod.width=bevel;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);state['parts'].append(o);return o
def assemble(name,pivot,offset):
 for o in bpy.context.scene.objects:o.select_set(False)
 for o in state['parts']:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=state['parts'][0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=pivot;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');o.location+=offset;state['parts']=[]
for name in ['Player','Pedestrian_M','Pedestrian_F','Officer','Tactical']:
 coll=bpy.data.collections[name];state['collection']=coll
 body=next(o for o in coll.objects if o.name.startswith('Body'));offset=body.location.copy();female=name=='Pedestrian_F';police=name in ['Officer','Tactical'];skin='SkinDark' if name in ['Pedestrian_M','Tactical'] else 'SkinLight';cloth='PoliceCloth' if police else 'Jacket'
 for o in list(coll.objects):
  if o!=body:bpy.data.objects.remove(o,do_unlink=True)
 if female:
  for v in body.data.vertices:
   if v.co.z>1.07:v.co.x*=.88
 for side in [-1,1]:
  x=side*(.205 if female else .225)
  skin_surface('Tailored sleeve',[(1.14,x+side*.035,.057,.061,.057),(1.22,x+side*.03,.067,.071,.067),(1.32,x+side*.015,.078,.078,.074),(1.40,x,.076,.087,.072),(1.445,x-side*.025,.03,.042,.032)],cloth)
  skin_surface('Forearm',[(.935,x+side*.045,.032,.038,.03),(1.00,x+side*.047,.043,.046,.039),(1.08,x+side*.04,.052,.052,.044),(1.15,x+side*.035,.051,.049,.043)],skin)
  oval('Palm',(x+side*.045,.006,.896),(.035,.025,.05),skin)
  for j in range(4):oval('Finger',(x+side*.045+(j-1.5)*.015,.014,.842+abs(j-1.5)*.009),(.008,.01,.035),skin)
  oval('Thumb',(x+side*.008,.017,.89),(.014,.014,.032),skin)
  assemble('Arm_'+('L' if side<0 else 'R'),(x,0,1.40),offset)
  x=side*.102
  skin_surface('Tailored trousers',[(.14,x,.051,.062,.049),(.24,x,.06,.066,.053),(.39,x,.069,.078,.062),(.53,x,.066,.071,.064),(.63,x,.076,.091,.08),(.78,x,.088,.103,.085),(.94,x,.088,.104,.095)],'Denim')
  detail('Leather shoe',(x,.04,.079),(.14,.257,.10),'Interior',.036)
  detail('Rubber sole',(x,.04,.029),(.142,.262,.025),'Rubber',.012)
  for y in [.055,.084,.108]:detail('Laces',(x,y,.128),(.065,.005,.003),'Shirt',.001)
  assemble('Leg_'+('L' if side<0 else 'R'),(x,0,.94),offset)
 skin_surface('Continuous head',[(1.535,0,.033,.031,.032),(1.557,0,.054,.047,.053),(1.59,0,.07,.058,.069),(1.63,0,.081,.064,.081),(1.68,0,.082,.062,.086),(1.724,0,.075,.064,.082),(1.76,0,.059,.045,.065),(1.784,0,.027,.016,.029),(1.79,0,.006,.008,.01)],skin)
 # A restrained nose bridge, small eyes and integrated jaw replace spherical facial placeholders.
 oval('Nose bridge',(0,.066,1.663),(.011,.012,.032),skin)
 oval('Nose tip',(0,.082,1.645),(.014,.018,.012),skin)
 for s in [-1,1]:
  oval('Ear',(s*.083,-.008,1.652),(.012,.018,.029),skin)
  oval('Eye white',(s*.030,.0585,1.688),(.012,.006,.005),'White')
  oval('Iris',(s*.030,.0635,1.688),(.004,.002,.004),'Hair')
  detail('Eyebrow',(s*.029,.063,1.701),(.029,.004,.004),'Hair',.001)
 detail('Lips',(0,.059,1.602),(.035,.006,.004),'SkinDark',.001)
 skin_surface('Hair crown',[(1.718,0,.076,.066,.084),(1.744,0,.071,.057,.078),(1.775,0,.048,.032,.049),(1.798,0,.005,.004,.005)],'Hair')
 if female:
  oval('Tied hair',(0,-.082,1.70),(.065,.062,.095),'Hair');oval('Bun',(0,-.135,1.74),(.045,.04,.045),'Hair')
 if name=='Player':detail('Facial hair',(0,.059,1.581),(.041,.004,.013),'Hair',.005)
 if police:
  if name=='Tactical':oval('Protective helmet',(0,-.013,1.773),(.098,.101,.077),'Interior')
  else:detail('Patrol cap',(0,-.008,1.781),(.175,.172,.037),'PoliceCloth',.021)
  detail('Cap brim',(0,.085,1.773),(.157,.12,.01),'Interior',.018)
 assemble('Head',(0,0,1.51),offset)
 for o in bpy.context.scene.objects:o.select_set(False)
 for o in coll.objects:o.hide_set(False);o.location-=offset;o.select_set(True)
 bpy.ops.export_scene.fbx(filepath=BASE+'Assets/GTA/Generated/Models/'+name+'.fbx',use_selection=True,axis_forward='-Z',axis_up='Y',apply_scale_options='FBX_SCALE_ALL',bake_anim=False,add_leaf_bones=False)
 for o in coll.objects:o.location+=offset;o.select_set(False)
bpy.ops.wm.save_as_mainfile(filepath=BASE+'UnityGTA.blend')
print('Five human assets rebuilt with continuous anatomical faces, shaped arms, trousers, shoes and distinct headwear.')
