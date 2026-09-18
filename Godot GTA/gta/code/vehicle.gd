extends RigidBody3D
const H=preload("res://gta/code/helpers.gd")
const D=preload("res://gta/code/data.gd")
var game
var id="sedan"
var data={}
var kind="car"
var model:Node3D
var health=100.0
var speed=0.0
var driver=false
var ai=false
var police=false
var target=Vector3.ZERO
var route_dir=Vector3.FORWARD
var home_line=0.0
var spawn_age=0.0
var wheels=[]
var rotors=[]
var headlamps=[]
var engine:AudioStreamPlayer3D
var siren:AudioStreamPlayer3D
var lights_on=false
var siren_on=false
var tune=1.0
var brake_tune=1.0
var paint=Color(.08,.25,.29)
var destroyed=false
var player_caused_damage=false
var throttle=0.0
var steer=0.0
var flying_throttle=.0
var smoke_timer=0.0
var collision_cooldown=0.0
var door_time=0.0
var owned=false
var support_count=0
var last_junction=Vector2i(999,999)
var taxi_route=[]
var taxi_place=""
func _ready():
	data=D.VEHICLES[id]
	kind=data.kind
	mass=data.mass
	collision_layer=4
	collision_mask=7
	contact_monitor=true
	max_contacts_reported=6
	body_entered.connect(_impact)
	angular_damp=4.0
	linear_damp=.05
	axis_lock_angular_x=true
	axis_lock_angular_z=true
	if kind in ["heli","plane"]:axis_lock_angular_x=false;axis_lock_angular_z=false
	var size=Vector3(1.78,.85,4.3)
	var center=Vector3(0,.77,0)
	if kind=="bike":size=Vector3(.58,.8,2.0)
	if kind=="boat":size=Vector3(2,1.0,5.0)
	if kind=="heli":size=Vector3(1.8,1.8,4.3);center.y=1.65
	if kind=="plane":size=Vector3(1.2,1.0,6.5);center.y=1.2
	H.collider(self,size,center)
	model=H.model(data.model)
	add_child(model)
	for m in H.find_meshes(model):
		if "Wheel_" in m.name:wheels.append(m)
		if "Rotor" in m.name or "Propeller" in m.name:rotors.append(m)
	for s in [-1,1]:
		var lamp=SpotLight3D.new()
		lamp.position=Vector3(s*.63,.72,-2.25)
		lamp.spot_range= 40
		lamp.spot_angle= 30
		lamp.light_energy=2.5
		lamp.light_color=Color(1,.86,.65)
		lamp.shadow_enabled=false
		add_child(lamp)
		headlamps.append(lamp)
	engine=AudioStreamPlayer3D.new()
	engine.stream=load("res://gta/generated/audio/engine.wav")
	engine.max_distance=60
	engine.volume_db=-18
	add_child(engine)
	if DisplayServer.get_name()!="headless":engine.play()
	siren=AudioStreamPlayer3D.new()
	siren.stream=load("res://gta/generated/audio/siren.wav")
	siren.max_distance=160
	siren.volume_db=-12
	add_child(siren)
	if police:
		siren_on=true
		if DisplayServer.get_name()!="headless":siren.play()
func _physics_process(dt):
	spawn_age+=dt
	collision_cooldown=maxf(0,collision_cooldown-dt)
	if destroyed:return
	var forward=-global_basis.z
	speed=linear_velocity.dot(forward)
	throttle=0.0;steer=0.0
	if driver and not game.menu_open:
		throttle=Input.get_axis("back","forward")
		steer=Input.get_axis("right","left")
		if Input.is_action_just_pressed("lights"):lights_on=not lights_on
		if Input.is_action_just_pressed("horn"):game.sound("horn",global_position,1.0)
		if Input.is_action_just_pressed("siren") and id in ["police","police_helicopter"]:
			siren_on=not siren_on
			if siren_on:siren.play()
			else:siren.stop()
		game.add_skill("Flying" if kind in ["heli","plane"] else "Driving",dt*abs(speed)*.001)
	elif ai:
		ai_control(dt)
	var wet=.68 if game.weather in ["Rain","Storm"] else 1.0
	if kind in ["car","bike"]:ground_drive(dt,forward,wet)
	elif kind=="boat":boat_drive(dt,forward)
	elif kind=="heli":helicopter_drive(dt,forward)
	elif kind=="plane":plane_drive(dt,forward)
	for w in wheels:w.rotate_x(speed*dt/ .37)
	for rotor in rotors:
		if "TailRotor" in rotor.name:rotor.rotate_x(dt*28)
		elif "Propeller" in rotor.name:rotor.rotate_z(dt*40)
		else:rotor.rotate_y(dt*28)
	for l in headlamps:l.visible=lights_on or game.hour<6 or game.hour>19
	engine.pitch_scale=clampf(.65+abs(speed)*.036+abs(throttle)*.18,.55,3)
	engine.volume_db= -15 if driver else -25
	if siren_on:
		var flash=sin(Time.get_ticks_msec()*.014)>0
		if not has_node("PoliceLight"):
			var light=OmniLight3D.new()
			light.name="PoliceLight"
			light.position.y=2.2
			light.omni_range= 12
			add_child(light)
		$PoliceLight.light_color=Color(.1,.25,1) if flash else Color(1,.04,.03)
		$PoliceLight.light_energy=3
	elif has_node("PoliceLight"):$PoliceLight.light_energy=0
	if health<40:
		smoke_timer-=dt
		if smoke_timer<=0:
			smoke_timer=.4
			game.effect(global_position+Vector3.UP*1.4,Color(.13,.13,.13,.8),8,1.6,2.0)
		if health<12:take_damage(dt*1.8,false)
	if global_position.y< - 30:queue_free()
func ground_drive(dt:float, forward:Vector3, wet:float):
	support_count=0
	var spread=.76 if kind=="car" else .16
	for x in [-spread,spread]:
		for z in [-1.35,1.35]:
			if kind=="bike":z*=.62
			var local=Vector3(x,.85,z)
			var start=global_transform*local
			var hit=H.ray(self,start,start-Vector3.UP*1.15,[get_rid()],1)
			if not hit.is_empty():
				var compression=1.0-start.distance_to(hit.position)
				if compression>0:
					var wheelvel=linear_velocity+angular_velocity.cross(global_basis*local)
					var force=clampf(compression*mass*9.5-wheelvel.y*mass*.8,0,mass*14)
					apply_force(Vector3.UP*force,global_basis*local)
					support_count+=1
	if support_count>0:
		var limit=data.speed*tune
		var force=data.power*tune*(.45+health*.0055)
		if abs(speed)<limit or sign(throttle)!=sign(speed):apply_central_force(forward*throttle*force)
		var lateral=global_basis.x*linear_velocity.dot(global_basis.x)
		var grip=(2.0 if driver and Input.is_action_pressed("jump") else 9.0)*wet
		apply_central_force(-lateral*mass*grip)
		apply_central_force(-forward*speed*mass*.055)
		var desired_yaw=steer*clampf(abs(speed)*.09,0,1.3)*sign(speed if abs(speed)>.2 else 1)
		angular_velocity.y=lerpf(angular_velocity.y,desired_yaw,dt*(4.0+game.skills.Driving*.015))
		if driver and Input.is_action_pressed("jump"):
			apply_central_force(-linear_velocity*mass*2.0*brake_tune)
	else:angular_velocity.y*=.98
func boat_drive(dt:float,forward:Vector3):
	if global_position.x>905:
		var water_y= -.55+sin(spawn_age*1.4)*.09
		var buoyancy=mass*(9.8+(water_y-global_position.y)*14-linear_velocity.y*4)
		apply_central_force(Vector3.UP*clampf(buoyancy,-mass*8,mass*28))
		apply_central_force(forward*throttle*data.power)
		apply_central_force(-linear_velocity*mass*.45)
		angular_velocity.y=lerpf(angular_velocity.y,steer*.65,dt*3)
	else:linear_velocity*=.99
func helicopter_drive(dt:float,forward:Vector3):
	var lift=0.0
	if driver and not game.menu_open:
		lift=Input.get_axis("crouch_hold","jump")
		flying_throttle=move_toward(flying_throttle,1.0,dt*.5)
	elif police and ai:
		lift=clampf((game.focus().y+ 30-global_position.y)*.12,-1,1)
		flying_throttle=1
	if flying_throttle>0:
		apply_central_force(Vector3.UP*mass*(9.8+lift*5-linear_velocity.y*.8))
		apply_central_force(forward*throttle*mass*8)
		apply_central_force(-Vector3(linear_velocity.x,0,linear_velocity.z)*mass*.25)
		angular_velocity.y=steer*.9
		angular_velocity.x=clampf(-rotation.x*3-throttle*.25,-1,1)
		angular_velocity.z=clampf(-rotation.z*3-steer*.25,-1,1)
func plane_drive(dt:float,forward:Vector3):
	if driver and not game.menu_open:
		flying_throttle=clampf(flying_throttle+Input.get_axis("back","forward")*dt*.3,0,1)
		var pitch_input=Input.get_axis("pitch_down","pitch_up")
		angular_velocity.x=lerpf(angular_velocity.x,pitch_input*.65,dt*2)
		angular_velocity.z=lerpf(angular_velocity.z,steer*.8,dt*2)
		angular_velocity.y=steer*clampf(abs(speed)*.004,.04,.3)
	apply_central_force(forward*flying_throttle*data.power)
	var airspeed=maxf(0,speed)
	var lift=clampf(airspeed*airspeed*.014,0,14)*mass
	apply_central_force(global_basis.y*lift)
	apply_central_force(-linear_velocity*mass*.065)
	if airspeed< 18:angular_velocity.x+=dt*.05
	# Fixed landing gear suspension enables rollout before lift develops.
	if global_position.y<1.2:
		var hit=H.ray(self,global_position+Vector3.UP,global_position-Vector3.UP,[get_rid()],1)
		if not hit.is_empty():apply_central_force(Vector3.UP*maxf(0,mass*(9.8+(hit.position.y-global_position.y+.12)*18-linear_velocity.y*5)))
func ai_control(dt):
	var desired=route_dir
	if not taxi_route.is_empty():
		var goal=taxi_route[0]
		goal.y=global_position.y
		if global_position.distance_to(goal)<8:
			taxi_route.pop_front()
			if taxi_route.is_empty():
				ai=false
				if game.player.vehicle==self:game.exit_vehicle();game.notify("Taxi arrived · "+taxi_place)
				return
			goal=taxi_route[0];goal.y=global_position.y
		desired=(goal-global_position).normalized()
		throttle=.55 if speed<12 else -.1
		steer=clampf(global_basis.z.signed_angle_to(-desired,Vector3.UP)*2,-1,1)
		return
	if police:
		var goal=game.last_known if game.pursuit=="SEARCH" else game.focus()
		if kind=="heli":goal.y=global_position.y
		desired=(goal-global_position).normalized()
		throttle=.9 if global_position.distance_to(goal)>10 else .1
	else:
		throttle=.48 if speed<11 else .05
		# Connected grid lane: gently correct lateral drift.
		var lane_error=home_line-(global_position.x if abs(route_dir.z)>.5 else global_position.z)
		desired=(route_dir+(Vector3.RIGHT if abs(route_dir.z)>.5 else Vector3.BACK)*clampf(lane_error*.1,-.4,.4)).normalized()
		var along=global_position.z if abs(route_dir.z)>.5 else global_position.x
		var junction=absf(fposmod(along+64,128)-64)
		var cell=Vector2i(roundi(global_position.x/128),roundi(global_position.z/128))
		if junction<2.5 and cell!=last_junction:
			last_junction=cell
			if randf()<.22:
				route_dir=route_dir.rotated(Vector3.UP,PI/2 if randf()<.5 else -PI/2).round()
				home_line=cell.x*128+(5 if route_dir.z<0 else -5) if abs(route_dir.z)>.5 else cell.y*128+(5 if route_dir.x>0 else -5)
		var red=(int(game.sim_time/9)%2==0)==(abs(route_dir.z)>.5)
		if junction< 19 and junction>9 and red:throttle=-.4 if speed>1 else 0
		var obstacle=H.ray(self,global_position+Vector3.UP*.8,global_position+Vector3.UP*.8-global_basis.z* 9,[get_rid()],6)
		if not obstacle.is_empty():throttle=-.7 if speed>1 else 0
	var angle=global_basis.z.signed_angle_to(-desired,Vector3.UP)
	steer=clampf(angle*2,-1,1)
	if kind in ["car","bike"] and speed<.5 and throttle<0:throttle=0
func _impact(body:Node):
	if collision_cooldown>0:return
	var impact=linear_velocity.length()
	if impact>5:
		collision_cooldown=.65
		take_damage((impact-4)*1.1,false)
		game.sound("impact",global_position,.9)
		if body.has_method("take_damage") and body!=game.player:
			body.take_damage(impact*4,driver)
		if driver and impact>10:
			game.player.take_damage(impact*.3)
			if body.is_in_group("civilian") or (body.get("police")==true):game.crime(1.0,global_position,80)
func take_damage(amount:float, by_player:bool=true):
	if destroyed:return
	player_caused_damage=player_caused_damage or by_player or driver
	health=maxf(0,health-amount)
	if health<=0:
		destroyed=true
		engine.stop();siren.stop()
		var was_driver=driver
		if was_driver:game.exit_vehicle();game.player.take_damage( 80)
		game.explosion(global_position,7.0,100.0,self,player_caused_damage)
		ai=false
		for m in H.find_meshes(model):m.material_override=H.material(Color(.055,.05,.045),.95)
func repair():
	health=100
	destroyed=false
	for m in H.find_meshes(model):m.material_override=null
	if DisplayServer.get_name()!="headless":engine.play()
func repaint(color:Color):
	paint=color
	for m in H.find_meshes(model):
		for i in range(m.mesh.get_surface_count()):
			var mat=m.mesh.surface_get_material(i)
			if mat and ("paint" in mat.resource_name or "red"==mat.resource_name or "white"==mat.resource_name):
				var copy=mat.duplicate()
				copy.albedo_color=color
				m.set_surface_override_material(i,copy)

func _exit_tree():
	if is_instance_valid(engine):engine.stop();engine.stream=null
	if is_instance_valid(siren):siren.stop();siren.stream=null
