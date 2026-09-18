extends Node3D
const H=preload("res://gta/code/helpers.gd")
const D=preload("res://gta/code/data.gd")
const PlayerScript=preload("res://gta/code/player.gd")
const VehicleScript=preload("res://gta/code/vehicle.gd")
const ActorScript=preload("res://gta/code/actor.gd")
const WorldScript=preload("res://gta/code/world.gd")
const UIScript=preload("res://gta/code/ui.gd")
var player
var world
var ui
var env:Environment
var sun:DirectionalLight3D
var underwater_overlay:ColorRect
var vehicles=[]
var actors=[]
var menu_open=false
var sim_time=0.0
var hour=15.0
var weather="Clear"
var wanted=0
var pressure=0.0
var pursuit="CLEAR"
var last_known=Vector3.ZERO
var unseen=0.0
var last_seen_time=-100.0
var arrest_progress=0.0
var cash=12500
var skills={"Stamina":10.0,"Shooting":10.0,"Strength":10.0,"Stealth":10.0,"Driving":10.0,"Flying":10.0,"Lung Capacity":10.0}
var weapon_index=3
var owned=[0,1,2,3]
var magazines={}
var reserve={}
var attachments={"suppressor":false,"extended":false,"grip":false,"optic":false,"flashlight":false}
var shoot_timer=0.0
var reload_timer=0.0
var pop_timer=0.0
var police_timer=0.0
var weather_timer=0.0
var notification="Welcome to Meridian Coast · F1 opens the sandbox controls"
var notification_time=9.0
var invulnerable=false
var scuba=false
var traffic_enabled=true
var pedestrians_enabled=true
var sensitivity=1.0
var master_volume=.8
var hurt_flash=0.0
var rain:CPUParticles3D
var rain_audio:AudioStreamPlayer
var ambient:AudioStreamPlayer
var sound_cache={}
var smoke_test=false
var screenshot_mode=false
var test_done=false
var saved_vehicles=[]
var outfit=Color(.075,.1,.115)
var street_traffic_turns=true
var wildlife_enabled=true
var animals=[]
var waypoint=Vector3.INF
var range_active=false
var range_time=0.0
var range_score=0
var range_shots=0
var range_targets=[]
var effects_count=0
var service_points=[
{"name":"Meridian Supply","kind":"shop","pos":Vector3(38,0,25)},
{"name":"Coastline Motorworks","kind":"garage","pos":Vector3(70,0,-28)},
{"name":"Harbor House","kind":"home","pos":Vector3(-218,0,283)},
{"name":"Meridian Medical","kind":"hospital","pos":Vector3(166,0,-105)},
{"name":"Portside Range","kind":"range","pos":Vector3(265,0,264)}
]
var nearest_service=null
var radio:AudioStreamPlayer
var radio_on=false
var autosave_timer=120.0
var save_path="user://meridian_save.json"
func _ready():
	process_mode=Node.PROCESS_MODE_ALWAYS
	smoke_test="--smoke-test" in OS.get_cmdline_user_args()
	screenshot_mode="--capture" in OS.get_cmdline_user_args()
	if smoke_test or "--qa" in OS.get_cmdline_user_args():save_path="user://meridian_qa_save.json"
	seed(817)
	setup_input()
	for i in range(D.WEAPONS.size()):
		magazines[str(i)]=D.WEAPONS[i].mag
		reserve[str(i)]=90 if i<10 else 8
	player=PlayerScript.new()
	player.game=self
	player.name="Player"
	player.process_mode=Node.PROCESS_MODE_PAUSABLE
	add_child(player)
	player.position=Vector3(6,2,24)
	world=WorldScript.new()
	world.game=self
	world.name="StreamedWorld"
	world.process_mode=Node.PROCESS_MODE_PAUSABLE
	add_child(world)
	setup_environment()
	ui=UIScript.new()
	ui.game=self
	add_child(ui)
	underwater_overlay=ui.underwater
	player.equip("pistol")
	spawn_vehicle("sedan",Vector3(5,.3,12))
	spawn_vehicle("sport",Vector3(-5,.3,24))
	spawn_vehicle("motorcycle",Vector3(8,.3, 30))
	spawn_vehicle("helicopter",Vector3(-432,.5,980))
	spawn_vehicle("plane",Vector3(-520,.5,1200))
	spawn_vehicle("boat",Vector3(1020,-.5,480))
	setup_range()
	if not smoke_test and not screenshot_mode and not "--qa" in OS.get_cmdline_user_args():load_game()
	Input.mouse_mode=Input.MOUSE_MODE_CAPTURED
	populate()
	print("MERIDIAN_READY | Godot ",Engine.get_version_info().string," | models=",H.cache.size()," | no missions")
func setup_input():
	var keys={"forward":KEY_W,"back":KEY_S,"left":KEY_A,"right":KEY_D,"sprint":KEY_SHIFT,"jump":KEY_SPACE,"crouch":KEY_C,"crouch_hold":KEY_CTRL,"enter_vehicle":KEY_F,"interact":KEY_E,"reload":KEY_R,"camera":KEY_V,"horn":KEY_H,"lights":KEY_L,"siren":KEY_J,"cover":KEY_Q,"parachute":KEY_P,"pitch_up":KEY_DOWN,"pitch_down":KEY_UP,"admin":KEY_F1,"map":KEY_M,"weapon_wheel":KEY_TAB,"quick_save":KEY_F5,"quick_load":KEY_F9,"phone":KEY_UP,"radio":KEY_T}
	for action in keys:
		if not InputMap.has_action(action):InputMap.add_action(action)
		var e=InputEventKey.new();e.physical_keycode=keys[action];InputMap.action_add_event(action,e)
	for a in ["fire","aim"]:
		if not InputMap.has_action(a):InputMap.add_action(a)
		var e=InputEventMouseButton.new();e.button_index=MOUSE_BUTTON_LEFT if a=="fire" else MOUSE_BUTTON_RIGHT
		InputMap.action_add_event(a,e)
func _unhandled_input(event):
	if event.is_action_pressed("admin") or event.is_action_pressed("ui_cancel"):
		ui.toggle_menu("Sandbox")
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("weapon_wheel"):
		ui.toggle_menu("Armory")
	elif event.is_action_pressed("map"):ui.toggle_map()
	elif event.is_action_pressed("quick_save"):save_game()
	elif event.is_action_pressed("quick_load"):load_game()
	elif not menu_open:
		if event.is_action_pressed("enter_vehicle"):enter_exit()
		if event.is_action_pressed("interact"):interact()
		if event.is_action_pressed("reload"):reload_weapon()
		if event.is_action_pressed("phone") and player.vehicle==null:ui.open_menu("Services")
		if event.is_action_pressed("radio"):
			radio_on=not radio_on
			radio.play() if radio_on else radio.stop()
			notify("Radio · Coastline ambient" if radio_on else "Radio off")
		if event is InputEventKey and event.pressed and not event.echo:
			if event.physical_keycode>=KEY_1 and event.physical_keycode<=KEY_9:select_weapon(event.physical_keycode-KEY_1)
		if event is InputEventMouseButton and event.pressed:
			if event.button_index==MOUSE_BUTTON_WHEEL_UP:cycle_weapon(1)
			elif event.button_index==MOUSE_BUTTON_WHEEL_DOWN:cycle_weapon(-1)
func focus() -> Vector3:
	if is_instance_valid(player.vehicle):return player.vehicle.global_position
	return player.global_position
func _process(dt):
	notification_time=maxf(0,notification_time-dt)
	hurt_flash=maxf(0,hurt_flash-dt)
	if menu_open:return
	sim_time+=dt
	hour=fposmod(hour+dt/ 80,24.0)
	player.update_camera(dt)
	update_environment(dt)
	nearest_service=null
	for service in service_points:
		if focus().distance_to(service.pos)< 9:nearest_service=service
	if range_active:
		range_time-=dt
		if range_time<=0:
			range_active=false
			cash+=range_score*15
			notify("Range complete · %s hits / %s shots · $%s" % [range_score,range_shots,range_score*15])
	autosave_timer-=dt
	if autosave_timer<=0:
		autosave_timer=120
		save_game(false)
	if screenshot_mode and sim_time>5 and not test_done:
		test_done=true
		capture_screenshot("free_roam")
	if smoke_test and sim_time>3 and not test_done:
		test_done=true
		run_smoke_tests()
func _physics_process(dt):
	if menu_open:return
	shoot_timer=maxf(0,shoot_timer-dt)
	if reload_timer>0:
		reload_timer-=dt
		if reload_timer<=0:
			var key=str(weapon_index)
			var amount=mini(capacity()-int(magazines[key]),int(reserve[key]))
			magazines[key]+=amount;reserve[key]-=amount
			notify("Reloaded")
	if Input.is_action_pressed("fire") and not player.dead:fire_weapon()
	pop_timer-=dt;police_timer-=dt
	if pop_timer<=0:
		pop_timer=3.0
		populate()
	if wanted>0:
		if sim_time-last_seen_time>1.1:
			pursuit="SEARCH"
			unseen+=dt
			var delay=9.0+wanted*5.0
			if player.crouched:delay*=.8
			if unseen>delay:
				wanted-=1
				pressure=float(wanted)
				unseen=0
				if wanted==0:
					pursuit="CLEAR"
					notify("Search called off · You lost the police")
		else:unseen=0;pursuit="PURSUIT"
		if police_timer<=0:
			police_timer=9.0
			reinforcements()
	else:
		pursuit="CLEAR"
	arrest_progress=maxf(0,arrest_progress-dt*.3)
func populate():
	vehicles=vehicles.filter(func(v):return is_instance_valid(v))
	actors=actors.filter(func(a):return is_instance_valid(a))
	var p=focus()
	populate_wildlife(p)
	for v in vehicles:
		if v.ai and not v.driver and v.global_position.distance_to(p)>380:v.queue_free()
	var civilians=actors.filter(func(a):return not a.police)
	if pedestrians_enabled:
		for i in range(maxi(0, 20-civilians.size())):
			var offset=Vector3(randf_range(-170,170),0,randf_range(-170,170))
			if offset.length()< 20:offset.x+= 40
			var point=p+offset
			point.x=roundf(point.x/128)*128+12
			point.y=world.height_at(point.x,point.z)+.5
			if point.x>820 or absf(point.z)>760 or point.x < -750:continue
			spawn_actor(point,false)
	if traffic_enabled and absf(p.z)<800 and p.x <820 and p.x > -750:
		var traffic=vehicles.filter(func(v):return v.ai and not v.police)
		for i in range(maxi(0,14-traffic.size())):
			var point=p+Vector3(randf_range(-210,210),0,randf_range(-210,210))
			var direction=Vector3.FORWARD if randf()<.5 else Vector3.BACK
			point.x=roundf(point.x/128)*128+(5 if direction.z<0 else -5)
			point.y=.4
			if point.distance_to(p)< 30:point.z+=80
			if point.x>800 or point.x < -700:continue
			var types=["sedan","compact","suv","van","taxi","pickup","muscle"]
			var v=spawn_vehicle(types.pick_random(),point)
			v.rotation.y=0 if direction.z<0 else PI
			v.ai=true;v.route_dir=direction;v.home_line=point.x
func spawn_vehicle(id:String, pos:Vector3=Vector3.INF):
	if not D.VEHICLES.has(id):return null
	vehicles=vehicles.filter(func(v):return is_instance_valid(v))
	if vehicles.size()>= 60:
		for v in vehicles:
			if not v.driver and not v.owned:v.queue_free();break
	if pos==Vector3.INF:
		pos=focus()-player.global_basis.z*8+Vector3.UP*.6
		if D.VEHICLES[id].kind=="boat":pos=Vector3(1020,-.4,480)
		if D.VEHICLES[id].kind=="plane":pos=Vector3(-532,.5,1270)
		if D.VEHICLES[id].kind=="heli":pos.y+=1.0
	var vehicle=VehicleScript.new()
	vehicle.game=self;vehicle.id=id;vehicle.police=id=="police" or id=="police_helicopter"
	vehicle.process_mode=Node.PROCESS_MODE_PAUSABLE
	add_child(vehicle)
	vehicle.global_position=pos
	vehicles.append(vehicle)
	return vehicle
func spawn_actor(p:Vector3, is_police:bool, tactical:bool=false):
	var a=ActorScript.new()
	a.game=self;a.police=is_police;a.tactical=tactical
	a.model_id=["mc_civilian_a","mc_civilian_b","mc_civilian_c"].pick_random()
	a.position=p
	a.process_mode=Node.PROCESS_MODE_PAUSABLE
	add_child(a)
	actors.append(a)
	return a
func enter_exit():
	if is_instance_valid(player.vehicle):exit_vehicle();return
	var closest=null
	var distance=4.2
	for v in vehicles:
		if is_instance_valid(v) and not v.destroyed:
			var d=v.global_position.distance_to(player.global_position)
			if d<distance:closest=v;distance=d
	if closest:
		if closest.ai:
			var civilian=spawn_actor(closest.global_position+closest.global_basis.x*2,false)
			civilian.panic=12
			civilian.last_threat=player.global_position
			crime(1.0,closest.global_position,70)
		if closest.police:raise_wanted(2)
		if pursuit=="SEARCH":unseen+=2
		closest.ai=false;closest.driver=true
		closest.door_time=1
		player.vehicle=closest
		player.cover_normal=Vector3.ZERO
		player.parachuting=false;player.parachute.visible=false
		player.yaw=closest.rotation.y
		sound("door",closest.global_position,.7)
		notify("Driving "+closest.data.name+" · F exit · H horn · L lights")
	else:notify("Move closer to a vehicle to enter")
func exit_vehicle():
	if not is_instance_valid(player.vehicle):player.vehicle=null;return
	var v=player.vehicle
	var candidate=v.global_position+v.global_basis.x*2.4+Vector3.UP*.8
	var hit=H.ray(player,v.global_position+Vector3.UP,candidate,[v.get_rid(),player.get_rid()],1)
	if not hit.is_empty():candidate=v.global_position-v.global_basis.x*2.4+Vector3.UP*.8
	v.driver=false
	player.vehicle=null
	player.global_position=candidate
	player.velocity=v.linear_velocity*.25
	player.collision_layer=2;player.collision_mask=5
	if v.kind in ["heli","plane"] and v.global_position.y>8:notify("Press P to deploy parachute")
	sound("door",v.global_position,.7)
func teleport(place:String):
	if not D.PLACES.has(place):return
	if is_instance_valid(player.vehicle):exit_vehicle()
	var p=D.PLACES[place]
	p.y=world.height_at(p.x,p.z)+2
	player.global_position=p
	player.velocity=Vector3.ZERO
	player.parachuting=false;player.parachute.visible=false
	world.update_sectors(true)
	populate()
	notify(place)
func select_weapon(index:int):
	if index<0 or index>=D.WEAPONS.size() or not owned.has(index):return
	if is_instance_valid(player.vehicle) and index not in [0,3,4,5,10]:notify("Use a sidearm, compact SMG or grenade in a vehicle");return
	weapon_index=index;reload_timer=0
	player.equip(D.WEAPONS[index].id)
	sound("ui",focus(),.3)
func cycle_weapon(delta:int):
	var available=owned.duplicate()
	available.sort()
	var n=available.find(weapon_index)
	select_weapon(available[posmod(n+delta,available.size())])
func capacity() -> int:
	return int(D.WEAPONS[weapon_index].mag*(1.5 if attachments.extended else 1.0))
func reload_weapon():
	if reload_timer>0 or capacity()==0:return
	if int(reserve[str(weapon_index)])<=0:notify("No reserve ammunition");return
	reload_timer=1.65-skills.Shooting*.005
	sound("reload",focus(),.7)
func fire_weapon():
	if shoot_timer>0 or reload_timer>0:return
	if is_instance_valid(player.vehicle) and weapon_index not in [0,3,4,5,10]:return
	var w=D.WEAPONS[weapon_index]
	shoot_timer=w.rate
	var origin=player.camera.global_position
	var direction=-player.camera.global_basis.z
	if weapon_index<3:
		var victim=null
		for a in actors:
			if is_instance_valid(a) and a.global_position.distance_to(player.global_position)<w.range:
				if direction.dot((a.global_position-player.global_position).normalized())>.2:victim=a;break
		if victim:
			var damage=w.damage*(1+skills.Strength*.004)
			if player.crouched and (-victim.global_basis.z).dot((player.global_position-victim.global_position).normalized())<-.4:damage*=5
			elif player.aiming:damage*=1.5
			victim.take_damage(damage)
			add_skill("Strength",.6)
			sound("impact",victim.global_position,.6)
		player.recoil=.07
		return
	var key=str(weapon_index)
	if magazines[key]<=0:reload_weapon();return
	magazines[key]-=1
	range_shots+=1 if range_active else 0
	var source=player.global_position+Vector3.UP*1.3-player.global_basis.z*.6
	var excluded=[player.get_rid()]
	if is_instance_valid(player.vehicle):excluded.append(player.vehicle.get_rid())
	if weapon_index in [10,11]:
		launch_projectile(source,direction,weapon_index==10)
	else:
		for pellet in range(8 if weapon_index==6 else 1):
			var spread=.003 if player.aiming else .025
			if weapon_index==6:spread=.06
			if attachments.grip:spread*=.7
			if is_instance_valid(player.vehicle):spread*=2
			var aim=(direction+player.camera.global_basis.x*randf_range(-spread,spread)+player.camera.global_basis.y*randf_range(-spread,spread)).normalized()
			var hit=H.ray(player,origin,origin+aim*w.range,excluded,7)
			var end=origin+aim*w.range
			if not hit.is_empty():
				end=hit.position
				var body=hit.collider
				if body.has_method("take_damage"):
					var headshot=(body is CharacterBody3D and end.y-body.global_position.y>1.48)
					body.take_damage(w.damage*(2.0 if headshot else 1.0))
				elif body.is_in_group("range_target"):
					range_hit(body)
				effect(end,Color(.71,.61,.37),6,.25,2)
			tracer(source,end,Color(1,.79,.37))
		sound("shot",source,.4 if attachments.suppressor else .9)
	effect(source,Color(1,.7,.17),5,.075,.5)
	player.recoil+= (.022 if attachments.grip else .045)*(1-skills.Shooting*.003)
	add_skill("Shooting",.08)
	crime(.24,source,20 if attachments.suppressor else 100)
func launch_projectile(pos:Vector3, direction:Vector3, grenade:bool):
	var b=RigidBody3D.new()
	add_child(b);b.global_position=pos
	b.mass=.4;b.collision_layer=0;b.collision_mask=5
	H.collider(b,Vector3(.12,.12,.2))
	var visual=H.model("mc_grenade" if grenade else "mc_rocket")
	b.add_child(visual)
	if not grenade:visual.scale=Vector3.ONE*.4
	b.linear_velocity=direction*( 18 if grenade else  70)+Vector3.UP*(4 if grenade else 0)
	b.gravity_scale=1 if grenade else 0
	b.contact_monitor=true;b.max_contacts_reported=2
	var state={"exploded":false}
	var projectile_ref=weakref(b)
	var detonate=func():
		var projectile=projectile_ref.get_ref()
		if not is_instance_valid(projectile) or state.exploded:return
		state.exploded=true
		explosion(projectile.global_position,10,180,projectile)
		projectile.queue_free()
	if not grenade:b.body_entered.connect(func(_body):detonate.call())
	get_tree().create_timer(2.5 if grenade else 4.0).timeout.connect(detonate)
func explosion(pos:Vector3, radius:float, damage:float, excluded:Node=null, blame_player:bool=true):
	effect(pos,Color(1,.29,.045), 60,.85,12)
	effect(pos+Vector3.UP,Color(.16,.14,.12,.8), 30,3.2,5)
	sound("explosion",pos,1)
	var light=OmniLight3D.new();add_child(light);light.position=pos+Vector3.UP
	light.omni_range= 20;light.light_energy=12;light.light_color=Color(1,.28,.06)
	var tween=create_tween();tween.tween_property(light,"light_energy",0,.6);tween.tween_callback(light.queue_free)
	for entity in vehicles+actors+[player]:
		if is_instance_valid(entity) and entity!=excluded:
			var distance=entity.global_position.distance_to(pos)
			if distance<radius:
				if entity==player:entity.take_damage(damage*(1-distance/radius))
				else:entity.take_damage(damage*(1-distance/radius),blame_player)
				if entity is RigidBody3D:entity.apply_central_impulse((entity.global_position-pos).normalized()*entity.mass*8)
	if blame_player:crime(1.3,pos,180)
func crime(value:float, pos:Vector3, radius:float):
	for a in actors:
		if is_instance_valid(a) and not a.dead and a.global_position.distance_to(pos)<radius:
			var hit=H.ray(player,a.global_position+Vector3.UP*1.5,pos+Vector3.UP*.3,[a.get_rid(),player.get_rid()],1)
			if hit.is_empty() or radius> 80:
				a.witness(value,pos)
func raise_wanted(amount:float):
	pressure=clampf(pressure+amount,0,5)
	wanted=clampi(ceili(pressure),0,5)
	if wanted>0:
		last_known=focus()
		unseen=0;police_timer=minf(police_timer,1)
		pursuit="SEARCH"
func set_wanted(level:int):
	wanted=clampi(level,0,5);pressure=wanted;unseen=0;last_known=focus()
	if level==0:
		for a in actors:
			if is_instance_valid(a) and a.police:a.queue_free()
		for v in vehicles:
			if is_instance_valid(v) and v.police and v.ai:v.queue_free()
		pursuit="CLEAR"
	else:reinforcements()
func police_saw_player():
	last_seen_time=sim_time
	last_known=focus()
	pursuit="PURSUIT"
	unseen=0
func reinforcements():
	var count=actors.filter(func(a):return is_instance_valid(a) and a.police).size()
	var cap=2+wanted*2
	if count>=cap:return
	var behind=player.camera.global_basis.z
	var p=focus()+behind*randf_range(70,110)+player.camera.global_basis.x*randf_range(- 30, 30)
	p.x=roundf(p.x/128)*128+5;p.y=world.height_at(p.x,p.z)+.4
	if p.x>880:p.x=780
	var v=spawn_vehicle("police",p)
	v.ai=true;v.police=true
	for i in range(mini(2,cap-count)):
		spawn_actor(p+Vector3(3+i,0,2),true,wanted>=4)
	if wanted>=3 and not vehicles.any(func(car):return is_instance_valid(car) and car.id=="police_helicopter" and car.ai):
		var heli=spawn_vehicle("police_helicopter",focus()+Vector3( 60, 40, 60))
		heli.ai=true;heli.police=true
	if wanted>=3:
		var block=spawn_vehicle("police",focus()-player.global_basis.z*80+Vector3.UP)
		block.rotation.y=PI/2
func respawn_player(reason:String):
	if player.dead and reason=="BUSTED":return
	player.dead=true
	notify(reason+" · Recovering at Meridian Medical",4)
	ui.death_text=reason
	await get_tree().create_timer(3).timeout
	if is_instance_valid(player.vehicle):exit_vehicle()
	player.global_position=Vector3(134,2,-115)
	player.velocity=Vector3.ZERO
	player.health=100;player.armor=0;player.breath=100
	player.dead=false
	cash=maxi(0,cash-250)
	set_wanted(0);arrest_progress=0
	ui.death_text=""
func interact():
	if nearest_service:
		var kind=nearest_service.kind
		if kind=="range":start_range()
		elif kind=="hospital":
			if spend(100):player.health=100;notify("Medical treatment complete")
		else:ui.open_service(kind)
func spend(amount:int) -> bool:
	if cash<amount:notify("Insufficient funds");return false
	cash-=amount;sound("ui",focus(),.6)
	return true
func buy_weapon(index:int):
	if owned.has(index):notify("Already owned");return
	if spend(D.WEAPONS[index].price):
		owned.append(index)
		select_weapon(index)
		notify("Purchased "+D.WEAPONS[index].name)
func add_skill(key:String, amount:float):
	skills[key]=minf(100,skills[key]+amount)
func notify(text:String, duration:float=4.0):
	notification=text;notification_time=duration
func effect(pos:Vector3, color:Color, count:int, lifetime:float, velocity:float):
	if effects_count>=48:return
	effects_count+=1
	var p=CPUParticles3D.new()
	p.amount=count;p.lifetime=lifetime;p.one_shot=true;p.explosiveness=.95
	p.direction=Vector3.UP;p.spread=180;p.initial_velocity_min=velocity*.25;p.initial_velocity_max=velocity
	p.gravity=Vector3(0,-3,0)
	p.scale_amount_min=.03 if lifetime<1 else .2
	p.scale_amount_max=.11 if lifetime<1 else .8
	var mesh=SphereMesh.new();mesh.radial_segments=6;mesh.rings=3;mesh.radius=.15;mesh.height=.3
	p.mesh=mesh
	var mat=H.material(color,.9)
	if color.r>.8:mat.emission_enabled=true;mat.emission=color;mat.emission_energy_multiplier=2
	p.material_override=mat
	add_child(p);p.global_position=pos;p.emitting=true
	get_tree().create_timer(lifetime+.2).timeout.connect(func():
		if is_instance_valid(p):p.queue_free()
		effects_count-=1)
func tracer(from:Vector3,to:Vector3,color:Color):
	if effects_count>=45:return
	var mesh=ImmediateMesh.new()
	mesh.surface_begin(Mesh.PRIMITIVE_LINES)
	mesh.surface_add_vertex(from);mesh.surface_add_vertex(to);mesh.surface_end()
	var n=MeshInstance3D.new();n.mesh=mesh
	var mat=H.material(color)
	mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	n.material_override=mat;add_child(n)
	get_tree().create_timer(.045).timeout.connect(n.queue_free)
func sound(id:String,pos:Vector3,volume:float=1):
	if DisplayServer.get_name()=="headless":return
	if not sound_cache.has(id):
		var path="res://gta/generated/audio/"+id+".wav"
		if not ResourceLoader.exists(path):return
		sound_cache[id]=load(path)
	var p=AudioStreamPlayer3D.new();p.stream=sound_cache[id]
	p.volume_db=linear_to_db(volume*master_volume);p.max_distance=140
	add_child(p);p.global_position=pos;p.play();p.finished.connect(p.queue_free)
func setup_environment():
	var we=WorldEnvironment.new()
	env=Environment.new()
	env.background_mode=Environment.BG_SKY
	var sky=Sky.new()
	var skymat=ProceduralSkyMaterial.new()
	skymat.sky_top_color=Color(.12,.29,.43)
	skymat.sky_horizon_color=Color(.63,.7,.72)
	skymat.ground_bottom_color=Color(.16,.19,.18)
	skymat.ground_horizon_color=Color(.58,.64,.64)
	sky.sky_material=skymat
	env.sky=sky
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color=Color(.56,.65,.78)
	env.ambient_light_energy=.65
	env.tonemap_mode=Environment.TONE_MAPPER_FILMIC
	env.tonemap_exposure=1.3
	env.fog_enabled=true;env.fog_density=.0007
	env.fog_light_color=Color(.55,.65,.69)
	env.ssao_enabled=true
	env.ssao_radius=1.3;env.ssao_intensity=1.1
	env.glow_enabled=true;env.glow_intensity=.45
	env.volumetric_fog_enabled=false
	we.environment=env;add_child(we)
	sun=DirectionalLight3D.new()
	add_child(sun);sun.shadow_enabled=true
	sun.directional_shadow_max_distance=180
	sun.directional_shadow_mode=DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
	sun.rotation_degrees=Vector3(- 40,-35,0)
	rain=CPUParticles3D.new()
	rain.amount=1400;rain.lifetime=1.1
	rain.emission_shape=CPUParticles3D.EMISSION_SHAPE_BOX
	rain.emission_box_extents=Vector3( 20,.5, 20)
	rain.direction=Vector3(.12,-1,.03);rain.spread=8
	rain.initial_velocity_min= 20;rain.initial_velocity_max= 20+5
	rain.gravity=Vector3(0,-7,0)
	var mesh=BoxMesh.new();mesh.size=Vector3(.016,.45,.016)
	rain.mesh=mesh;rain.material_override=H.material(Color(.62,.7,.73),.2)
	add_child(rain);rain.emitting=false
	rain_audio=AudioStreamPlayer.new();rain_audio.stream=load("res://gta/generated/audio/rain.wav");rain_audio.volume_db=-19;add_child(rain_audio)
	ambient=AudioStreamPlayer.new();ambient.stream=load("res://gta/generated/audio/ambient.wav");ambient.volume_db=-25;add_child(ambient)
	if DisplayServer.get_name()!="headless":ambient.play()
	radio=AudioStreamPlayer.new();radio.stream=load("res://gta/generated/audio/radio.wav");radio.volume_db=-22;add_child(radio)
func update_environment(dt):
	weather_timer-=dt
	rain.global_position=focus()+Vector3.UP*12
	if weather_timer>0:return
	weather_timer=.2
	var daylight=clampf(sin((hour-6)/ 12*PI),0,1)
	sun.rotation_degrees.x= -(hour-6)*15
	sun.light_energy=daylight*2.2+.12
	sun.light_color=Color(1,.72+daylight*.22,.5+daylight*.42)
	var wet=weather in ["Rain","Storm"]
	var cloudy=weather in ["Cloudy","Rain","Storm"]
	var sky=env.sky.sky_material
	sky.sky_top_color=Color(.12,.29,.43).lerp(Color(.055,.065,.085),.7 if cloudy else 0)*(.15+daylight*.85)
	sky.sky_horizon_color=Color(.63,.7,.72)*(.13+daylight*.87)
	env.ambient_light_energy=.27+daylight*.48
	env.fog_density=.0045 if weather=="Fog" else (.0028 if wet else .00065)
	env.fog_light_color=Color(.52,.59,.63)*(.2+daylight*.8)
	rain.emitting=wet
	world.roadmat.set_shader_parameter("wet",1 if wet else 0)
	if wet and not rain_audio.playing and DisplayServer.get_name()!="headless":rain_audio.play()
	elif not wet:rain_audio.stop()
	if weather=="Storm" and randf()<.015:
		sun.light_energy=8
		sound("explosion",focus()+Vector3.UP*40,.25)
func setup_range():
	for i in range(5):
		var b=StaticBody3D.new()
		b.add_to_group("range_target")
		add_child(b);b.position=Vector3(244+i*6,1.7, 30+256)
		H.collider(b,Vector3(1.1,1.6,.18))
		var m=H.box(b,Vector3.ZERO,Vector3(1.1,1.6,.18),H.material(Color(.65,.61,.5)))
		H.text3(b,"◎",Vector3(0,.2,-.12),.014)
		range_targets.append(b)
	H.text3(self,"PORTSIDE RANGE\nE · 45 second practice",Vector3(265,3,264),.018)
func start_range():
	range_active=true;range_time=45;range_score=0;range_shots=0
	notify("Range active · Hit the five targets · No mission or progression requirements")
func range_hit(body:Node):
	if not range_active:return
	range_score+=1
	add_skill("Shooting",.5)
	body.position.y=randf_range(1,2.5)
	sound("ui",body.global_position,.7)
func save_game(show_notice:bool=true):
	var p=player.global_position
	var data={"version":1,"position":[p.x,p.y,p.z],"health":player.health,"armor":player.armor,"cash":cash,"owned":owned,"magazines":magazines,"reserve":reserve,"weapon":weapon_index,"hour":hour,"weather":weather,"skills":skills,"attachments":attachments,"garage":saved_vehicles,"sensitivity":sensitivity,"volume":master_volume,"outfit":outfit.to_html()}
	var file=FileAccess.open(save_path+".tmp",FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(data,"\t"));file.close()
		DirAccess.rename_absolute(save_path+".tmp",save_path)
		if show_notice:notify("Progress saved")
func load_game():
	if not FileAccess.file_exists(save_path):return
	var parsed=JSON.parse_string(FileAccess.get_file_as_string(save_path))
	if not parsed is Dictionary or parsed.get("version",0)!=1:notify("Save could not be loaded safely");return
	if is_instance_valid(player.vehicle):exit_vehicle()
	var p=parsed.get("position",[6,2,24])
	if p is Array and p.size()==3:
		player.position=Vector3(clampf(float(p[0]),-1550,1550),maxf(float(p[1]),- 15),clampf(float(p[2]),-1550,1550))+Vector3.UP*.5
	player.velocity=Vector3.ZERO
	player.health=clampf(float(parsed.get("health",100)),1,100)
	player.armor=clampf(float(parsed.get("armor",0)),0,100)
	cash=maxi(0,int(parsed.get("cash",12500)))
	owned=[]
	for i in parsed.get("owned",[0,3]):
		if int(i)>=0 and int(i)<D.WEAPONS.size():owned.append(int(i))
	if not owned.has(0):owned.append(0)
	magazines.merge(parsed.get("magazines",{}),true);reserve.merge(parsed.get("reserve",{}),true)
	for key in skills:skills[key]=clampf(float(parsed.get("skills",{}).get(key,10)),0,100)
	hour=fposmod(float(parsed.get("hour",16.4)),24)
	weather=parsed.get("weather","Clear")
	attachments.merge(parsed.get("attachments",{}),true)
	saved_vehicles=parsed.get("garage",[])
	sensitivity=clampf(float(parsed.get("sensitivity",1)),.2,3)
	master_volume=clampf(float(parsed.get("volume",.8)),0,1)
	set_outfit(Color(parsed.get("outfit",outfit.to_html())))
	select_weapon(int(parsed.get("weapon",3)))
	set_wanted(0);world.update_sectors(true)
	notify("Progress restored")
func capture_screenshot(label:String):
	if DisplayServer.get_name()=="headless":return
	await RenderingServer.frame_post_draw
	var image=get_viewport().get_texture().get_image()
	DirAccess.make_dir_recursive_absolute("user://screenshots")
	var path="user://screenshots/"+label+".png"
	var result=image.save_png(path)
	notify("Photo saved to your user data screenshots folder" if result==OK else "Could not save photo")
	print("CAPTURE ",path)
func run_smoke_tests():
	print("SMOKE starting integration checks")
	var assertions=[]
	assertions.append(["player_grounded",player.is_on_floor()])
	assertions.append(["world_sectors",world.sectors.size()>=9 and world.sectors.size()<=25])
	assertions.append(["traffic_population",vehicles.size()>=10])
	assertions.append(["pedestrian_population",actors.size()>5])
	assertions.append(["rig_import",player.skeleton!=null and player.skeleton.get_bone_count()>=10])
	var v=vehicles[0]
	player.position=v.position+Vector3(2,0,0)
	enter_exit()
	assertions.append(["enter_vehicle",player.vehicle==v and v.driver])
	exit_vehicle()
	assertions.append(["exit_vehicle",player.vehicle==null and not v.driver])
	var old_cash=cash
	cash=12345
	save_game(false)
	cash=0
	load_game()
	assertions.append(["save_load",cash==12345])
	cash=old_cash
	set_wanted(3)
	assertions.append(["wanted_response",wanted==3 and actors.any(func(a):return is_instance_valid(a) and a.police)])
	set_wanted(0)
	assertions.append(["wanted_clear",wanted==0])
	var original_health=player.health
	player.armor=0;player.take_damage(5)
	assertions.append(["player_damage",player.health<original_health])
	player.health=100
	for id in D.VEHICLES:
		var test=spawn_vehicle(id,Vector3(0,5,- 80))
		assertions.append(["vehicle_"+id,is_instance_valid(test) and test.model!=null])
		test.queue_free()
	for i in range(D.WEAPONS.size()):
		if not owned.has(i):owned.append(i)
		select_weapon(i)
		assertions.append(["weapon_"+str(i),i==0 or is_instance_valid(player.gun)])
	var success=true
	for check in assertions:
		print("CHECK ",check[0]," ", "PASS" if check[1] else "FAIL")
		if not check[1]:success=false
	print("SMOKE_RESULT ", "PASS" if success else "FAIL")
	await get_tree().process_frame
	await get_tree().process_frame
	get_tree().quit(0 if success else 2)

func set_outfit(color:Color):
	outfit=color
	for mesh in H.find_meshes(player.visual):
		for i in range(mesh.mesh.get_surface_count()):
			var mat=mesh.mesh.surface_get_material(i)
			if mat and mat.resource_name=="cloth":
				var copy=mat.duplicate();copy.albedo_color=color;mesh.set_surface_override_material(i,copy)

func populate_wildlife(p:Vector3):
	animals=animals.filter(func(a):return is_instance_valid(a))
	if not wildlife_enabled:return
	var species="deer" if p.x < -700 else ("gull" if p.x>740 else "")
	if species.is_empty():return
	for i in range(maxi(0,7-animals.size())):
		var a=preload("res://gta/code/wildlife.gd").new()
		a.game=self;a.species="fish" if p.x>900 and i%2==0 else species
		a.position=p+Vector3(randf_range(-60,60),0,randf_range(-60,60))
		a.position.y=world.height_at(a.position.x,a.position.z)+.3
		if a.species=="gull":a.position.y=14+randf()*12
		if a.species=="fish":a.position.x=maxf(a.position.x,940);a.position.y=-3-randf()*4
		add_child(a);animals.append(a)

func call_taxi(place:String):
	if not spend(75):return
	if is_instance_valid(player.vehicle):exit_vehicle()
	var start=focus()+Vector3(0,.5,5)
	start.x=roundf(start.x/128)*128+5
	start.y=world.height_at(start.x,start.z)+.4
	var dest=D.PLACES[place]
	var v=spawn_vehicle("taxi",start)
	v.ai=true
	v.taxi_place=place
	var junction_z=roundf(dest.z/128)*128+5
	v.taxi_route=[Vector3(start.x,0,junction_z),Vector3(roundf(dest.x/128)*128+5,0,junction_z),Vector3(roundf(dest.x/128)*128+5,0,dest.z)]
	player.vehicle=v
	player.yaw=v.rotation.y
	notify("Taxi passenger · F to leave · Services menu to skip the trip")

func skip_taxi():
	if is_instance_valid(player.vehicle) and not player.vehicle.taxi_place.is_empty():
		var place=player.vehicle.taxi_place
		exit_vehicle();teleport(place)
		notify("Taxi arrived · "+place)

func _exit_tree():
	for audio in [ambient,rain_audio,radio]:
		if is_instance_valid(audio):audio.stop();audio.stream=null
	sound_cache.clear()
