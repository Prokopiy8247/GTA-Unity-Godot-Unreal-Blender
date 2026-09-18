
def tailored(name,sections,mat):
    verts=[];faces=[];count=24
    for row,(z,rx,ry,cx,cy) in enumerate(sections):
        for j in range(count):
            a=j*math.tau/count
            wrinkle=1+(.012*math.sin(j*3+row*2) if row not in [0,len(sections)-1] else 0)
            verts.append((cx+math.cos(a)*rx*wrinkle,cy+math.sin(a)*ry*wrinkle,z))
    for row in range(len(sections)-1):
        for j in range(count):faces.append((row*count+j,row*count+(j+1)%count,(row+1)*count+(j+1)%count,(row+1)*count+j))
    faces.append(tuple(range(count-1,-1,-1)))
    faces.append(tuple(range((len(sections)-1)*count,len(sections)*count)))
    return mesh(name,verts,faces,mat,True)

def human(name,skin,coat,pants='denim',female=False,police=False):
    begin(name,'Characters')
    parts={}
    def tag(o,b):parts.setdefault(b,[]).append(o);return o
    tag(tailored('Waistband',[(.83,.178,.127,0,0),(.91,.184,.138,0,0),(1.01,.163,.12,0,0)],pants),'Hips')
    tag(tailored('TailoredJacket',[(.99,.166,.124,0,0),(1.06,.171,.13,0,0),(1.15,.173,.13,0,0),(1.27,.203,.146,0,.005),(1.38,.228,.14,0,0),(1.435,.223,.11,0,0),(1.48,.082,.084,0,0)],coat),'Spine')
    for side in [-1,1]:
        tag(beam('Collar',(side*.075,.09,1.48),(side*.1,.145,1.37),.027,coat),'Spine')
    tag(cyl('Neck',(0,0,1.54),.068,.13,skin),'Head')
    tag(tailored('HeadSculpt',[(1.55,.051,.07,0,.01),(1.585,.068,.089,0,.026),(1.63,.092,.102,0,.015),(1.69,.103,.104,0,.005),(1.745,.102,.1,0,0),(1.79,.085,.083,0,-.004),(1.819,.04,.05,0,-.007),(1.829,.01,.012,0,-.009)],skin),'Head')
    tag(ell('Chin',(0,.082,1.607),(.048,.032,.022),skin),'Head')
    tag(ell('Nose',(0,.115,1.686),(.024,.036,.037),skin),'Head')
    tag(ell('Hair',(0,-.005,1.788),(.108,.105,.058),'hair'),'Head')
    for s in [-1,1]:
        tag(ell('Ear',(s*.107,.005,1.686),(.022,.014,.041),skin),'Head')
        tag(ell('EyeWhite',(s*.041,.106,1.712),(.025,.012,.013),'white'),'Head')
        tag(ell('Iris',(s*.041,.117,1.712),(.01,.004,.01),'hair'),'Head')
        tag(beam('Brow',(s*.022,.111,1.738),(s*.064,.103,1.736),.008,'hair'),'Head')
    tag(beam('Mouth',(-.032,.11,1.632),(.032,.11,1.632),.005,'brick'),'Head')
    tag(box('Belt',(0,.007,1.),(.36,.257,.028),'black',.009),'Hips')
    tag(box('Buckle',(0,.144,1.),(.052,.011,.04),'chrome',.006),'Hips')
    tag(beam('JacketZip',(0,.135,1.05),(0,.13,1.47),.007,'chrome'),'Spine')
    for s,side in [(-1,'L'),(1,'R')]:
        tag(tailored('TrouserThigh',[(.46,.073,.077,s*.1,0),(.51,.077,.084,s*.1,.009),(.56,.085,.093,s*.1,0),(.66,.093,.1,s*.1,0),(.78,.1,.109,s*.1,0),(.91,.099,.115,s*.1,0)],pants),'Thigh'+side)
        tag(tailored('TrouserCalf',[(.105,.062,.065,s*.1,0),(.14,.073,.073,s*.1,.006),(.2,.064,.067,s*.1,0),(.29,.069,.077,s*.1,-.01),(.38,.077,.082,s*.1,-.004),(.49,.075,.08,s*.1,0)],pants),'Shin'+side)
        tag(box('Boot',(s*.1,.071,.085),(.145,.31,.16),'black',.055),'Shin'+side)
        tag(box('Sole',(s*.1,.07,.03),(.153,.32,.04),'rubber',.015),'Shin'+side)
        tag(tailored('JacketSleeveUpper',[(1.1,.061,.065,s*.305,0),(1.17,.067,.074,s*.297,0),(1.29,.075,.083,s*.281,0),(1.39,.081,.086,s*.263,0),(1.44,.061,.07,s*.239,0)],coat),'Arm'+side)
        tag(tailored('JacketSleeveLower',[(.867,.047,.048,s*.307,.03),(.89,.052,.058,s*.307,.03),(.94,.048,.056,s*.307,.026),(1.02,.057,.065,s*.307,.01),(1.105,.062,.066,s*.305,0),(1.15,.06,.063,s*.305,0)],coat),'Forearm'+side)
        tag(ell('Hand',(s*.307,.031,.837),(.052,.037,.08),skin),'Forearm'+side)
        for f in range(4):
            tag(ell('Finger',(s*(.28+f*.017),.044,.785),(.011,.018,.036),skin,12,8),'Forearm'+side)
        tag(ell('Thumb',(s*.26,.06,.843),(.016,.021,.04),skin,12,8),'Forearm'+side)
        tag(box('Pocket',(s*.1,.122,1.275),(.115,.026,.117),coat,.012),'Spine')
    if female:tag(ell('Ponytail',(0,-.125,1.69),(.065,.08,.17),'hair'),'Head')
    if police:
        tag(box('Vest',(0,.117,1.26),(.35,.045,.35),'uniform',.03),'Spine')
        tag(ell('Cap',(0,.01,1.816),(.113,.11,.041),'uniform'),'Head')
        tag(box('CapVisor',(0,.123,1.8),(.18,.14,.018),'uniform',.02),'Head')
        tag(box('Badge',(-.085,.164,1.36),(.04,.009,.054),'gold',.009),'Spine')
    armdata=bpy.data.armatures.new(name+'_Skeleton'); rig=bpy.data.objects.new(name+'_Rig',armdata)
    asset[1].objects.link(rig);rig.parent=asset[2]
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
    bpy.ops.object.mode_set(mode='EDIT')
    specs=[('Hips',(0,0,.89),(0,0,1.02),None),('Spine',(0,0,1.02),(0,0,1.48),'Hips'),('Head',(0,0,1.48),(0,0,1.84),'Spine')]
    for s,side in [(-1,'L'),(1,'R')]:
        specs += [('Thigh'+side,(s*.1,0,.9),(s*.1,0,.48),'Hips'),('Shin'+side,(s*.1,0,.48),(s*.1,0,.07),'Thigh'+side),('Arm'+side,(s*.245,0,1.45),(s*.305,0,1.13),'Spine'),('Forearm'+side,(s*.305,0,1.13),(s*.307,.03,.83),'Arm'+side)]
    for n,h,t,p in specs:
        b=armdata.edit_bones.new(n);b.head=h;b.tail=t
        if p:b.parent=armdata.edit_bones[p]
    bpy.ops.object.mode_set(mode='OBJECT')
    for bn,objects in parts.items():
        for o in objects:
            vg=o.vertex_groups.new(name=bn);vg.add(list(range(len(o.data.vertices))),1.,'REPLACE')
            mod=o.modifiers.new('Character skin','ARMATURE');mod.object=rig
    # Consolidate skin to one mesh with shared material slots, keep the actual rig.
    bpy.ops.object.select_all(action='DESELECT')
    objs=[o for o in asset[1].objects if o.type=='MESH']
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join()
    objs[0].name=name+'__Skin'
    objs[0].parent=rig
    finish(False)

def weapon(name,kind):
    begin(name,'Weapons')
    if kind in ['knife','bat']:
        if kind=='knife':
            box('Grip',(0,0,0),(.038,.13,.04),'black',.01)
            mesh('Blade',[(-.025,.06,-.009),(.025,.06,-.009),(.024,.23,0),(0,.34,0),(-.024,.23,0)],[(0,1,2,3,4)],'chrome')
        else:
            cyl('Handle',(0,0,0),.018,.3,'wood','Y')
            ell('Barrel',(0,.3,0),(.048,.27,.048),'wood')
        finish(True);return
    if kind=='grenade':
        ell('Body',(0,0,0),(.045,.045,.066),'leaf',16,12)
        box('Lever',(0,0,.066),(.016,.065,.015),'steel',.003);finish(True);return
    length={'pistol':.2,'heavy':.25,'smg':.38,'shotgun':.91,'rifle':.8,'carbine':.65,'sniper':1.15,'rocket':1.15}.get(kind,.8)
    if kind=='rocket':
        cyl('Launcher',(0,.21,.055),.085,length,'leaf','Y');cyl('Muzzle',(0,.79,.055),.098,.035,'steel','Y')
        box('Grip',(0,0,-.07),(.05,.1,.2),'black',.014);finish(True);return
    box('Receiver',(0,length*.18,0),(.07,length*.48,.095),'steel',.012)
    grip=box('Grip',(0,-.035,-.1),(.058,.087,.17),'black',.013);grip.rotation_euler.x=-.2
    cyl('Barrel',(0,length*.56,.012),.017,length*.5,'steel','Y')
    cyl('Muzzle',(0,length*.815,.012),.019,.035,'black','Y')
    box('TriggerGuard',(0,.045,-.069),(.018,.103,.02),'steel',.006)
    beam('Trigger',(0,.042,-.025),(0,.033,-.061),.006,'steel')
    if kind not in ['pistol','heavy']:
        box('Magazine',(0,.11,-.126),(.051,.105,.17),'black',.012)
        box('Foregrip',(0,length*.46,-.031),(.09,length*.24,.08),'black',.014)
        box('Stock',(0,-.19,-.015),(.055,.27,.12),'black',.016)
        for y in range(6):box('Rail',(0,.03+y*.04,.062),(.083,.013,.019),'black',.004)
    else:
        for y in range(5):box('SlideSerration',(.036,-.04+y*.013,.022),(.005,.005,.066),'black',.001)
    if kind=='sniper':
        cyl('Scope',(0,.14,.12),.033,.3,'black','Y');cyl('ScopeLens',(0,.299,.12),.029,.004,'glass','Y')
        for y in [.04,.23]:box('ScopeMount',(0,y,.075),(.037,.028,.065),'steel',.004)
    box('FrontSight',(0,length*.67,.068),(.014,.019,.03),'black',.002)
    if kind not in ['pistol','heavy','grenade','rocket','knife','bat']:
        for y in [length*.35+i*.028 for i in range(6)]:
            for side in [-1,1]:box('CoolingPort',(side*.047,y,-.013),(.009,.016,.026),'rubber',.004)
        for j in range(3):box('MagazineRib',(.029,.11,-.09-j*.032),(.005,.086,.009),'steel',.002)
        ell('ButtPad',(0,-.329,-.02),(.048,.018,.089),'rubber')
        cyl('Selector',(.043,.08,.016),.013,.012,'chrome','X',16)
        beam('ChargingHandle',(-.074,.13,.01),(.069,.13,.01),.008,'steel')
    finish(True)

def building(name,kind):
    begin(name,'Buildings')
    w,d,h={'tower':(26,24,72),'apartment':(23,20,22),'house':(14,13,7),'warehouse':(34,27,12),'shop':(24,18,7),'hangar':(44,36,18),'garage':(28,22,9),'hospital':(32,24,28)}[kind]
    facade='brick' if kind=='apartment' else 'plaster'
    box('Foundation',(0,0,.3),(w+.6,d+.6,.6),'concrete',.08)
    if kind in ['hangar','garage']:
        box('RearWall',(0,-d/2+.3,h/2),(w,.6,h),facade,.06)
        for side in [-1,1]:box('SideWall',(side*(w/2-.3),0,h/2),(.6,d,h),facade,.06)
        box('Lintel',(0,d/2-.3,h-1),(w,.6,2),facade,.06)
        box('Floor',(0,0,.15),(w,d,.3),'concrete',.03)
        for side in [-1,1]:
            box('Workbench',(side*(w/2-2),0,.9),(2,5,.15),'steel',.04)
            for yy in [-1.8,1.8]:beam('BenchLeg',(side*(w/2-2),yy,0),(side*(w/2-2),yy,.9),.05,'steel')
    else:box('Mass',(0,0,h/2),(w,d,h),facade,.13)
    if kind in ['tower','hospital']:
        box('CurtainWall',(0,d/2+.03,h/2),(w-.7,.09,h-.6),'glass',.02)
        box('CurtainWall',(0,-d/2-.03,h/2),(w-.7,.09,h-.6),'glass',.02)
        for x in range(-int(w/2)+1,int(w/2),3):
            for s in [-1,1]:box('Mullion',(x,s*(d/2+.1),h/2),(.13,.15,h),'chrome')
        for z in range(3,int(h),3):
            for s in [-1,1]:box('Spandrel',(0,s*(d/2+.13),z),(w,.18,.3),'steel')
        for s in [-1,1]:
            box('SideGlazing',(s*(w/2+.02),0,h/2),(.08,d-1,h-1),'glass')
            for z in range(3,int(h),3):box('SideSpandrel',(s*(w/2+.1),0,z),(.16,d,.3),'steel')
    elif kind not in ['warehouse','hangar','garage']:
        for z in range(2,int(h),3):
            for x in range(-int(w/2)+2,int(w/2)-1,4):
                for s in [-1,1]:
                    box('WindowFrame',(x,s*(d/2+.07),z),(2.05,.2,1.8),'white',.035)
                    box('Window',(x,s*(d/2+.19),z),(1.8,.04,1.56),'glass' if random.random()<.75 else 'window_lit',.02)
                    box('WindowSill',(x,s*(d/2+.26),z-.9),(2.3,.55,.13),'concrete',.03)
                    if kind=='apartment':
                        box('Balcony',(x,s*(d/2+.8),z-1.1),(2.8,1.7,.16),'concrete')
                        beam('Railing',(x-1.3,s*(d/2+1.5),z-.2),(x+1.3,s*(d/2+1.5),z-.2),.032,'steel')
    else:
        for x in range(-int(w/2)+1,int(w/2),2):box('Corrugation',(x,-d/2-.04,h/2),(.09,.09,h),'steel')
        if kind=='warehouse':box('DoorRoller',(0,d/2+.08,h*.32),(w*.65,.14,h*.59),'steel',.04)
        for z in range(1,int(h*.58)) if kind=='warehouse' else []:box('DoorSlat',(0,d/2+.17,z),(w*.65,.035,.035),'chrome')
        box('Clerestory',(0,-d/2-.06,h-1.4),(w-2,.1,1.6),'glass')
    box('Cornice',(0,0,h+.12),(w+.6,d+.6,.24),'concrete',.05)
    for x in [-w*.25,w*.25]:
        box('HVAC',(x,-d*.15,h+.65),(2.2,3,1.1),'steel',.08)
        for y in [-.8,-.4,0,.4,.8]:box('HVACLouvre',(x,-d*.15+y,h+1.23),(1.9,.06,.02),'chrome')
    if kind=='house':
        mesh('Roof',[(-8,-7,h),(8,-7,h),(-8,7,h),(8,7,h),(0,-7,h+3.2),(0,7,h+3.2)],[(0,4,5,2),(1,3,5,4),(0,1,4),(2,5,3)],'brick')
        box('FrontDoor',(0,d/2+.12,1.2),(1.25,.18,2.4),'wood',.04)
    if kind in ['shop','garage','hospital']:
        box('Signboard',(0,d/2+.3,h-1.15),(w-2,.25,1.4),'paint',.06)
        label({'shop':'MERIDIAN  SUPPLY','garage':'COASTLINE  MOTORWORKS','hospital':'MERIDIAN  MEDICAL'}[kind],(0,d/2+.45,h-1.55),.65,rot=(math.pi/2,0,math.pi))
    finish(True)

def props():
    begin('mc_lamp','StreetProps')
    cyl('Base',(0,0,.18),.21,.36,'steel')
    cyl('Post',(0,0,4),.08,8,'steel')
    beam('Arm',(0,0,7.9),(0,2,8.15),.066,'steel')
    box('Housing',(0,2,8.1),(.42,1.05,.17),'steel',.09)
    box('LED',(0,2,8.001),(.32,.83,.025),'headlight',.03);finish(True)
    begin('mc_signal','StreetProps')
    cyl('Post',(0,0,2.5),.075,5,'steel')
    box('Housing',(0,0,4.5),(.42,.3,1.2),'black',.07)
    for z,m in [(4.12,'leaf'),(4.5,'gold'),(4.88,'taillight')]:cyl('Lens',(0,.175,z),.13,.04,m,'Y')
    finish(True)
    begin('mc_bench','StreetProps')
    for x in [-.7,.7]:
        for y in [-.24,.24]:beam('Leg',(x,y,0),(x,y,.48),.034,'steel')
    for y in [-.24,-.08,.08,.24]:box('SeatSlat',(0,y,.49),(1.85,.12,.05),'wood',.015)
    for z in [.66,.84]:box('BackSlat',(0,-.29,z),(1.85,.06,.15),'wood',.015)
    finish(True)
    begin('mc_bin','StreetProps');cyl('Bin',(0,0,.46),.29,.92,'steel',verts=16);cyl('Lid',(0,0,.94),.32,.06,'black');finish(True)
    begin('mc_barrier','StreetProps')
    loft('Jersey',[(-1.6,.4,0,.18,.25),(1.6,.4,0,.18,.25)],'concrete')
    box('Spine',(0,0,.63),(.26,3.2,.75),'concrete',.06)
    for y in [-1,0,1]:box('Reflector',(0.141,y,.78),(.02,.17,.1),'gold')
    finish(True)
    begin('mc_container','StreetProps')
    box('Cargo',(0,0,1.3),(2.5,6,2.6),'red',.07)
    for y in range(-14,15):box('Rib',(-1.26,y*.2,1.3),(.04,.07,2.46),'steel')
    for s in [-1,1]:beam('DoorLock',(s*.58,3.07,.2),(s*.58,3.07,2.42),.025,'chrome')
    finish(True)
    begin('mc_crane','Buildings')
    for x in [-5,5]:
        for y in [-4,4]:beam('TowerLeg',(x,y,0),(x*.5,y*.5,25),.28,'gold')
    beam('MainBoom',(-18,0,25),(22,0,25),.3,'gold')
    for x in range(-18,22,4):beam('Truss',(x,0,25),(x+4,0,28),.14,'steel')
    beam('TopChord',(-18,0,28),(22,0,28),.2,'gold')
    beam('Cable',(17,0,25),(17,0,6),.035,'steel')
    box('Cab',(1,1.6,24),(3,2.7,2.7),'glass',.1);finish(True)
    begin('mc_tree','Nature')
    cyl('Trunk',(0,0,2.7),.2,5.4,'wood',verts=12)
    for i in range(9):
        angle=i*2.399;v=Vector((math.sin(angle)*1.8,math.cos(angle)*1.8,4.6+i*.22))
        beam('Branch',(0,0,3.6),v,.077,'wood')
        # Individual leaf clusters create irregular, porous silhouettes.
        for j in range(15):
            p=v+Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-.5,.8)))
            ell('Foliage',p,(random.uniform(.35,.7),random.uniform(.4,.7),.3),'leaf' if j%3 else 'leaf2',8,6)
    finish(True)
    begin('mc_rock','Nature');o=ell('Rock',(0,0,.5),(1.5,1.1,.8),'concrete',12,8)
    for v in o.data.vertices:v.co*=random.uniform(.8,1.2)
    finish(True)
    begin('mc_parachute','Equipment')
    vs=[];fs=[]
    for i in range(17):
        a=-1.25+i*2.5/16
        for y in [-1.1,1.1]:vs.append((math.sin(a)*3,y,3+math.cos(a)*1.5))
    for i in range(16):fs.append((i*2,i*2+1,i*2+3,i*2+2))
    mesh('Canopy',vs,fs,'red',True)
    for x in [-2.6,-1.4,1.4,2.6]:
        for y in [-1,1]:beam('Line',(x,y,3.7),(x*.08,y*.1,0),.009,'white')
    finish(True)
