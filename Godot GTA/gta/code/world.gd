extends Node3D
const H=preload("res://gta/code/helpers.gd")
var game
var sectors={}
var pending=[]
var timer=0.0
var roadmat
var walkmat
var landmat
var sandmat
var stripe
var water:MeshInstance3D
var buildings=0
var street_lights=[]
var sector_radius=2
var seed_value=817
func _ready():
	roadmat=surface(Color(.115,.125,.13),48.0,.87)
	walkmat=surface(Color(.40,.39,.35),22.0,.9)
	landmat=surface(Color(.22,.255,.15),.8,.96)
	sandmat=surface(Color(.55,.48,.34),8.0,.96)
	stripe=H.material(Color(.78,.73,.49),.8)
	make_terrain()
	make_water()
	make_landmarks()
	scatter_nature()
	update_sectors(true)
func surface(color:Color, scale_value:float, rough:float) -> ShaderMaterial:
	var m=ShaderMaterial.new()
	var s=Shader.new()
	s.code="""shader_type spatial;
uniform vec4 tint: source_color;
uniform float grain=20.0;
uniform float wet=0.0;
varying vec3 wp;
float noise(vec2 p){return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453);}
void vertex(){wp=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){float n=noise(floor(wp.xz*grain));ALBEDO=tint.rgb*(.86+n*.22)*(1.0-wet*.33);ROUGHNESS=mix(.9,.19,wet);NORMAL_MAP=vec3(.5+(n-.5)*.1,.5+(n-.5)*.1,1.0);}
"""
	m.shader=s
	m.set_shader_parameter("tint",color)
	m.set_shader_parameter("grain",scale_value)
	return m
func height_at(x:float,z:float) -> float:
	if x>930:return -18.0
	if x>870:return lerpf(0.0,-18.0,(x-870.0)/60.0)
	if x < -650 and z < -350:
		var h=maxf(0.0,(-x-650.0)/7.5)
		return h*(.65+.35*sin(z*.004)*sin(x*.004))
	if x < -750:return sin(x*.009)*sin(z*.009)*4.0
	return 0.0
func make_terrain():
	var st=SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var step=32
	for x in range(-1664,1664,step):
		for z in range(-1664,1664,step):
			var a=Vector3(x,height_at(x,z)-.09,z)
			var b=Vector3(x+step,height_at(x+step,z)-.09,z)
			var c=Vector3(x,height_at(x,z+step)-.09,z+step)
			var d=Vector3(x+step,height_at(x+step,z+step)-.09,z+step)
			for v in [a,b,c,b,d,c]:st.add_vertex(v)
	st.generate_normals()
	var mesh=MeshInstance3D.new()
	mesh.mesh=st.commit()
	mesh.material_override=landmat
	add_child(mesh)
	mesh.create_trimesh_collision()
	# Coast promenade and sandy transition are authored as terrain surfaces.
	H.box(self,Vector3(874,-.25,0),Vector3(84,.42,3200),sandmat,true)
func make_water():
	water=MeshInstance3D.new()
	var plane=PlaneMesh.new()
	plane.size=Vector2(3000,4000)
	plane.subdivide_width=60
	plane.subdivide_depth=80
	water.mesh=plane
	var m=ShaderMaterial.new()
	var s=Shader.new()
	s.code="""shader_type spatial;
render_mode cull_disabled;
varying vec3 wp;
void vertex(){wp=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;VERTEX.y+=sin(wp.x*.085+TIME*1.2)*.14+sin(wp.z*.12+TIME*.9)*.1;}
void fragment(){float w=sin(wp.x*.7+TIME*1.4)*sin(wp.z*.5+TIME);ALBEDO=mix(vec3(.015,.11,.13),vec3(.06,.24,.25),w*.5+.5);METALLIC=.42;ROUGHNESS=.17;NORMAL_MAP=vec3(.5+w*.06,.5+cos(wp.z*.8+TIME)*.05,1.0);}
"""
	m.shader=s
	water.material_override=m
	add_child(water)
	water.position=Vector3(2400,-.35,0)
func district(p:Vector3) -> String:
	if p.x>740 and p.z>250:return "HARBOR / EAST DOCKS"
	if p.x>780:return "COAST / TERN BEACH"
	if p.z>770 and p.x < -250:return "PETREL AIRFIELD"
	if p.x < -650 and p.z < -350:return "CINDER HIGHLANDS"
	if p.x < -740:return "WESTERN COUNTRYSIDE"
	if p.x>270 and p.z>270:return "IRONWORKS DISTRICT"
	if p.x < -250 and p.z>200:return "GARDEN SUBURBS"
	if p.x < -250:return "OLD QUARTER"
	return "MERIDIAN / DOWNTOWN"
func _process(dt):
	timer-=dt
	if timer<=0:
		street_lights=street_lights.filter(func(l):return is_instance_valid(l))
		for light in street_lights:light.visible=(game.hour>18.4 or game.hour<6.8) and light.global_position.distance_to(game.focus())<140
		timer=.5
		update_sectors(false)
	if not pending.is_empty():
		var key=pending.pop_front()
		if not sectors.has(key):build_sector(key)
func update_sectors(immediate:bool):
	if not is_instance_valid(game.player):return
	var p=game.focus()
	var center=Vector2i(floori(p.x/128.0),floori(p.z/128.0))
	var desired={}
	for x in range(-sector_radius,sector_radius+1):
		for z in range(-sector_radius,sector_radius+1):
			var key=center+Vector2i(x,z)
			if abs(key.x)>12 or abs(key.y)>12:continue
			desired[key]=true
			if not sectors.has(key) and not pending.has(key):pending.append(key)
	for key in sectors.keys():
		if not desired.has(key):
			sectors[key].queue_free()
			sectors.erase(key)
	pending=pending.filter(func(k):return desired.has(k))
	pending.sort_custom(func(a,b):return (a-center).length_squared()<(b-center).length_squared())
	if immediate:
		for i in range(mini(9,pending.size())):build_sector(pending.pop_front())
func add_model(id:String, parent:Node, p:Vector3, rot:float=0.0, solid_size:Vector3=Vector3.ZERO):
	var model=H.model(id)
	parent.add_child(model)
	model.position=p
	model.rotation.y=rot
	if id=="mc_lamp":
		var light=SpotLight3D.new()
		model.add_child(light)
		light.position=Vector3(0,7.9,-2)
		light.rotation.x=-PI/2
		light.spot_range=18
		light.spot_angle=68
		light.light_color=Color(1,.76,.43)
		light.light_energy=3
		light.shadow_enabled=false
		street_lights.append(light)
	for m in H.find_meshes(model):
		m.visibility_range_end=420.0 if id.contains("tower") else 260.0
		m.visibility_range_end_margin=30
	if solid_size!=Vector3.ZERO:
		var b=StaticBody3D.new()
		model.add_child(b)
		H.collider(b,solid_size,Vector3(0,solid_size.y/2,0))
	return model
func build_sector(key:Vector2i):
	var sector=Node3D.new()
	sector.name="Sector_%s_%s" % [key.x,key.y]
	add_child(sector)
	sector.position=Vector3(key.x*128,0,key.y*128)
	sectors[key]=sector
	var x=key.x*128.0
	var z=key.y*128.0
	if x>=896:return
	var rural=x < -750 or z < -770 or z>768
	if rural:
		if z>640 and z<1408 and x>-700 and x<-200:return
		for i in range(5):
			var px=x+18+i*23
			var pz=z+35+sin(i*3.1)* 20
			add_model("mc_tree",sector,Vector3(px-x,height_at(px,pz),pz-z))
		return
	if not (x < -256 and z>128):
		H.box(sector,Vector3(64,-.015,64),Vector3(99,.09,99),walkmat)
		H.box(sector,Vector3(64,.04,64),Vector3(18,.035,96),roadmat)
		for bay in range(24,116,7):
			H.box(sector,Vector3(60,.065,bay),Vector3(7,.012,.09),stripe)
	# Roads on the grid; centerline lanes connect deterministically across sectors.
	H.box(sector,Vector3(64,.015,0),Vector3(128,.04, 20),roadmat)
	H.box(sector,Vector3(0,.018,64),Vector3( 20,.04,128),roadmat)
	for i in range(4,124,12):
		H.box(sector,Vector3(i,.042,0),Vector3(5,.008,.14),stripe)
		H.box(sector,Vector3(0,.045,i),Vector3(.14,.008,5),stripe)
	for s in [-1,1]:
		H.box(sector,Vector3(64,.12,s*12),Vector3(128,.22,3.4),walkmat,true)
		H.box(sector,Vector3(s*12,.12,64),Vector3(3.4,.22,128),walkmat,true)
	for i in range(6):
		H.box(sector,Vector3(-6+i*2.3,.05,15),Vector3(1.25,.015,3.7),H.material(Color(.65,.65,.59)))
		H.box(sector,Vector3(15,.05,-6+i*2.3),Vector3(3.7,.015,1.25),H.material(Color(.65,.65,.59)))
	var rng=RandomNumberGenerator.new()
	rng.seed=abs(key.x*947+key.y*13757+seed_value)
	for bx in [38, 90]:
		for bz in [38, 90]:
			if key==Vector2i.ZERO and bx==38 and bz==38:continue
			if key==Vector2i(0,-1) and bx==90 and bz==90:continue
			if key==Vector2i(-2,2) and bx==38 and bz==38:continue
			if key==Vector2i(1,-1) and bx==38 and bz==38:continue
			var id="mc_tower"
			var size=Vector3(26,72,24)
			var scale_y=rng.randf_range(.55,1.45)
			if x < -256 and z>128:
				id="mc_house";size=Vector3(14,7,13);scale_y=1.0
			elif x>256 and z>256:
				id="mc_warehouse";size=Vector3(34,12,27);scale_y=1.0
			elif x < -128 or rng.randf() < .38:
				id="mc_apartment";size=Vector3(23,22,20);scale_y=rng.randf_range(.9,1.4)
			var model=add_model(id,sector,Vector3(bx,0,bz),0,size)
			model.scale.y=scale_y
			buildings+=1
			if id=="mc_house":add_model("mc_tree",sector,Vector3(bx+16,0,bz+9))
	for p in [Vector3(12,0, 30),Vector3( 90,0,12)]:
		add_model("mc_lamp",sector,p)
	add_model("mc_signal",sector,Vector3(12,0,14))
	add_model("mc_bench",sector,Vector3( 30,.24,12),PI/2)
	var bin=preload("res://gta/code/prop.gd").new()
	bin.game=game;sector.add_child(bin);bin.position=Vector3(34,.24,12)
	add_model("mc_hydrant",sector,Vector3(18,.24,12))
	if rng.randf()<.55:add_model("mc_tree",sector,Vector3( 70,0,20))
func make_landmarks():
	add_model("mc_shop",self,Vector3(38,0,38),0,Vector3(24,7,18))
	H.text3(self,"MERIDIAN SUPPLY\nWeapons • ammunition • armor",Vector3(38,8,27),.022)
	var garage=add_model("mc_garage",self,Vector3(70,0,-35),PI)
	for wall in [[Vector3(-13.7,4.5,0),Vector3(.6,9,22)],[Vector3(13.7,4.5,0),Vector3(.6,9,22)],[Vector3(0,4.5,10.7),Vector3(28,9,.6)]]:
		var body=StaticBody3D.new();garage.add_child(body);H.collider(body,wall[1],wall[0])
	H.text3(self,"COASTLINE MOTORWORKS\nRepair • paint • performance",Vector3( 70,9,-21),.022)
	add_model("mc_house",self,Vector3(-218,0,294),0,Vector3(14,7,13))
	H.text3(self,"HARBOR HOUSE\nWardrobe • sleep • save",Vector3(-218,8,284),.024)
	add_model("mc_hospital",self,Vector3(166,0,- 90),PI,Vector3(32,28,24))
	# Long runway, taxiway and aprons with actual takeoff space.
	H.box(self,Vector3(-520,.018,1000),Vector3( 40,.08,650),roadmat)
	H.box(self,Vector3(-430,.02,1000),Vector3(14,.08,650),roadmat)
	for z in range(700,1310, 40):
		H.box(self,Vector3(-520,.07,z),Vector3(1.3,.02, 18),stripe)
	for x in [-532,-526,-514,-508]:
		H.box(self,Vector3(x,.08, 70+630),Vector3(2,.02,35),stripe)
	for z in [850,1050,1250]:
		add_model("mc_hangar",self,Vector3(-370,0,z),PI/2,Vector3(44, 18,36))
	H.box(self,Vector3(-435,.015,970),Vector3(150,.1,480),roadmat)
	# Highway from countryside to docks, with coast bridge.
	H.box(self,Vector3(0,.09,650),Vector3(2300,.18,32),roadmat,true)
	for x in range(-1100,1150,20):
		for z in [644,656]:H.box(self,Vector3(x,.19,z),Vector3(9,.012,.16),stripe)
	for z in [634,666]:H.box(self,Vector3(0,.7,z),Vector3(2300,.9,.45),walkmat,true)
	for z in [450,520,590]:
		H.box(self,Vector3(930,.05,z),Vector3(140,1.0, 14),walkmat,true)
		add_model("mc_crane",self,Vector3(840,0,z),0)
		for i in range(3):add_model("mc_container",self,Vector3(820-i*4,0,z+ 20))
	# Rural link to highland viewpoint follows terrain.
	for i in range(40):
		var a=Vector3(-650-i*14+sin(i*.3)*45,0,-350-i*18)
		var b=Vector3(-650-(i+1)*14+sin((i+1)*.3)*45,0,-350-(i+1)*18)
		a.y=height_at(a.x,a.z)+.08;b.y=height_at(b.x,b.z)+.08
		var road=H.box(self,(a+b)/2,Vector3(11,.22,(a-b).length()+1),roadmat,true)
		road.look_at_from_position((a+b)/2,b,Vector3.UP)
	for i in range(16):
		var p=Vector3(-1000+sin(i)*170,0,-900+cos(i)*170)
		p.y=height_at(p.x,p.z)
		add_model("mc_rock",self,p)

func scatter_nature():
	var sample=H.model("mc_tree")
	var tree_mesh=H.find_meshes(sample)[0]
	var mesh=tree_mesh.mesh
	var origin=tree_mesh.transform
	var mm=MultiMesh.new()
	mm.transform_format=MultiMesh.TRANSFORM_3D
	mm.mesh=mesh
	mm.instance_count=260
	var rng=RandomNumberGenerator.new();rng.seed=9817
	for i in range(mm.instance_count):
		var p=Vector3(rng.randf_range(-1500,-780),0,rng.randf_range(-1500,650))
		p.y=height_at(p.x,p.z)
		var scale_value=rng.randf_range(.65,1.5)
		var transform=Transform3D(Basis(Vector3.UP,rng.randf()*TAU).scaled(Vector3.ONE*scale_value),p)
		mm.set_instance_transform(i,transform*origin)
	var trees=MultiMeshInstance3D.new();trees.multimesh=mm;add_child(trees)
	sample.free()
	for p in [Vector3(-1040,0,128),Vector3(-1260,0,350),Vector3(-920,0,-200)]:
		p.y=height_at(p.x,p.z)
		add_model("mc_house",self,p,0,Vector3(14,7,13))
		add_model("mc_warehouse",self,p+Vector3(40,0,0),0,Vector3(34,12,27))
