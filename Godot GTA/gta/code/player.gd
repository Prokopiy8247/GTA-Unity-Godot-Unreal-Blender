extends CharacterBody3D
const H=preload("res://gta/code/helpers.gd")
var game
var visual:Node3D
var skeleton:Skeleton3D
var camera:Camera3D
var yaw=0.0
var pitch=-.18
var first_person=false
var aiming=false
var crouched=false
var swimming=false
var parachuting=false
var parachute:Node3D
var vehicle
var gun:Node3D
var gun_pivot:Node3D
var health=100.0
var armor=50.0
var breath=100.0
var stamina=100.0
var anim_time=0.0
var cover_normal=Vector3.ZERO
var recoil=0.0
var dead=false
var flashlight:SpotLight3D
var step_timer=0.0
var last_fall=0.0
func _ready():
	collision_layer=2
	collision_mask=5
	var shape=CollisionShape3D.new()
	var capsule=CapsuleShape3D.new()
	capsule.radius=.3
	capsule.height=1.78
	shape.shape=capsule
	shape.position.y=.89
	add_child(shape)
	visual=H.model("mc_player")
	add_child(visual)
	skeleton=H.skeletal(visual)
	gun_pivot=Node3D.new()
	add_child(gun_pivot)
	gun_pivot.position=Vector3(.29,1.32,-.4)
	flashlight=SpotLight3D.new();gun_pivot.add_child(flashlight)
	flashlight.spot_range=35;flashlight.spot_angle=28;flashlight.light_energy=3
	flashlight.visible=false
	camera=Camera3D.new()
	game.add_child(camera)
	camera.current=true
	camera.far=2100
	camera.near=.08
	camera.fov= 70
	parachute=H.model("mc_parachute")
	add_child(parachute)
	parachute.visible=false
func equip(id:String):
	if is_instance_valid(gun):gun.queue_free()
	gun=null
	if id=="fists":return
	gun=H.model("mc_"+id)
	gun_pivot.add_child(gun)
	if game.weapon_index>=3 and game.weapon_index<10:
		if game.attachments.suppressor:
			var part=H.model("mc_suppressor");gun.add_child(part);part.position.z= -.16 if game.weapon_index in [3,4] else -.62
		if game.attachments.optic:
			var part=H.model("mc_optic");gun.add_child(part);part.position.y=.08
		if game.attachments.flashlight:
			var part=H.model("mc_flashlight");gun.add_child(part);part.position=Vector3(.07,0,-.12)
func _unhandled_input(event):
	if event is InputEventMouseMotion and Input.mouse_mode==Input.MOUSE_MODE_CAPTURED and not game.menu_open:
		yaw-=event.relative.x*.0023*game.sensitivity
		pitch=clampf(pitch-event.relative.y*.002,-1.3,1.1)
	if event.is_action_pressed("camera"):
		first_person=not first_person
	if event.is_action_pressed("crouch"):
		crouched=not crouched
	if event.is_action_pressed("cover") and vehicle==null:
		if cover_normal!=Vector3.ZERO:cover_normal=Vector3.ZERO
		else:
			var dir=-Basis(Vector3.UP,yaw).z
			var hit=H.ray(self,global_position+Vector3.UP,global_position+Vector3.UP+dir*1.65,[get_rid()],1)
			if not hit.is_empty():
				cover_normal=hit.normal
				global_position=hit.position+hit.normal*.46-Vector3.UP
				game.notify("Cover attached · A/D to move · RMB to peek · Q to leave")
	if event.is_action_pressed("parachute") and not is_on_floor() and vehicle==null and not swimming:
		parachuting=not parachuting
		parachute.visible=parachuting
func _physics_process(dt):
	if dead:return
	aiming=Input.is_action_pressed("aim") and not game.menu_open
	flashlight.visible=aiming and game.attachments.flashlight
	if is_instance_valid(vehicle):
		global_position=vehicle.global_position+Vector3.UP*.7
		velocity=Vector3.ZERO
		collision_layer=0
		collision_mask=0
		visual.visible=false
		gun_pivot.visible=aiming and game.weapon_index in [3,4,5,10]
		rotation.y=yaw if aiming else vehicle.rotation.y
		return
	vehicle=null
	collision_layer=2
	collision_mask=5
	visual.visible=not first_person
	gun_pivot.visible=not dead
	if game.menu_open:return
	var move=Input.get_vector("left","right","forward","back")
	var direction=Basis(Vector3.UP,yaw)*Vector3(move.x,0,move.y)
	swimming=global_position.x>900 and global_position.y<.4
	var speed=5.2
	if crouched:speed=2.1
	if aiming:speed=2.8
	if Input.is_action_pressed("sprint") and stamina>1 and not aiming and not crouched:
		speed=8.4
		stamina=maxf(0,stamina-dt*(7.0-game.skills.Stamina*.025))
		game.add_skill("Stamina",dt*.02)
	else:stamina=minf(100,stamina+dt*12)
	if cover_normal!=Vector3.ZERO:
		var tangent=cover_normal.cross(Vector3.UP)
		direction=tangent*move.x
		speed=2.0
		crouched=true
		if abs(move.y)>.5:cover_normal=Vector3.ZERO
	if swimming:
		parachuting=false
		parachute.visible=false
		speed=3.3
		var dive=Input.is_action_pressed("sprint")
		var vertical=0.0
		if Input.is_action_pressed("jump"):vertical=3
		elif dive:vertical=-2.4
		else:vertical=clampf((-.8-global_position.y)*3,-3,3)
		velocity.y=lerpf(velocity.y,vertical,dt*3)
		if global_position.y< -1.65:
			breath=maxf(0,breath-dt*(3.8-game.skills["Lung Capacity"]*.018)) if not game.scuba else 100
			game.add_skill("Lung Capacity",dt*.035)
			if breath<=0:take_damage(dt*8)
		else:breath=minf(100,breath+dt*24)
	elif parachuting:
		speed=9
		velocity.y=move_toward(velocity.y,-3.2 if Input.is_action_pressed("jump") else -5.5,dt*25)
	else:
		velocity.y-=22*dt
		if is_on_floor():
			if last_fall < - 13:take_damage(abs(last_fall+13)*4)
			if Input.is_action_just_pressed("jump"):
				velocity.y=7.1
				game.sound("step",global_position,.8)
		breath=minf(100,breath+dt*20)
	last_fall=velocity.y
	velocity.x=move_toward(velocity.x,direction.x*speed,dt*22)
	velocity.z=move_toward(velocity.z,direction.z*speed,dt*22)
	if direction.length()>.1 or aiming:
		var target=yaw if aiming else atan2(-direction.x,-direction.z)
		rotation.y=lerp_angle(rotation.y,target,dt*12)
	visual.position.y= -.22 if crouched else 0.0
	if crouched and direction.length()>.1:game.add_skill("Stealth",dt*.025)
	move_and_slide()
	if is_on_floor() and parachuting:
		parachuting=false
		parachute.visible=false
	anim_time+=dt*maxf(2.0,Vector2(velocity.x,velocity.z).length()*2)
	H.animate(skeleton,anim_time,Vector2(velocity.x,velocity.z).length(),aiming,crouched)
	if gun_pivot:gun_pivot.rotation.x= -pitch if aiming else .35
	step_timer-=dt
	if is_on_floor() and direction.length()>.1 and step_timer<=0:
		step_timer=.6 if crouched else .38
		game.sound("step",global_position,.2 if crouched else .45)
	if global_position.y< - 40 or absf(global_position.x)>1700 or absf(global_position.z)>1700:
		game.teleport("Downtown")
func update_camera(dt):
	var base=global_position+Vector3.UP*1.5
	var distance=4.8
	if is_instance_valid(vehicle):
		base=vehicle.global_position+Vector3.UP*(2.0 if vehicle.kind in ["heli","plane"] else 1.2)
		distance=12 if vehicle.kind in ["heli","plane"] else 7.5
		if not aiming and abs(vehicle.speed)>2 and Input.get_last_mouse_velocity().length()<2:
			yaw=lerp_angle(yaw,vehicle.rotation.y,dt*.8)
	if aiming:distance=2.05
	if first_person:distance=0
	var rot=Basis(Vector3.UP,yaw)*Basis(Vector3.RIGHT,pitch+recoil)
	var shoulder=rot.x*(.52 if aiming and not first_person else .12)
	var desired=base+shoulder+rot.z*distance
	var exclude=[get_rid()]
	if is_instance_valid(vehicle):exclude.append(vehicle.get_rid())
	var hit=H.ray(self,base,desired,exclude,1)
	if not hit.is_empty():desired=hit.position+hit.normal*.2
	if camera.global_position.distance_to(desired)>35:camera.global_position=desired
	else:camera.global_position=camera.global_position.lerp(desired,1.0-exp(-12*dt))
	camera.rotation=Vector3(pitch+recoil,yaw,0)
	var fov=70.0
	if aiming:
		fov=24 if game.weapon_index==9 else (38 if game.attachments.optic else 50)
	if is_instance_valid(vehicle):fov+=clampf(abs(vehicle.speed)*.24,0, 14)
	camera.fov=lerpf(camera.fov,fov,dt*9)
	recoil=move_toward(recoil,0,dt*1.5)
	if game.underwater_overlay:
		game.underwater_overlay.visible=swimming and camera.global_position.y<-.4
func take_damage(amount:float):
	if game.invulnerable or dead:return
	amount*=1.0-game.skills.Strength*.0015
	if aiming and game.weapon_index==0:amount*=.5
	var absorbed=minf(armor,amount*.65)
	armor-=absorbed
	health-=amount-absorbed
	game.hurt_flash=.4
	if health<=0:
		health=0
		dead=true
		game.respawn_player("WASTED")
