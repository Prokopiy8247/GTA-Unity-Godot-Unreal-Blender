extends CharacterBody3D
const H=preload("res://gta/code/helpers.gd")
var game
var police=false
var tactical=false
var model_id="mc_civilian_a"
var visual:Node3D
var skeleton:Skeleton3D
var health= 70
var target=Vector3.ZERO
var panic=0.0
var think=0.0
var fire_timer=0.0
var anim=0.0
var dead=false
var report_delay=-1.0
var report_value=0.0
var last_threat=Vector3.ZERO
var life=0.0
var rounds=12
func _ready():
	collision_layer=2
	collision_mask=5
	add_to_group("police" if police else "civilian")
	var c=CollisionShape3D.new()
	var shape=CapsuleShape3D.new()
	shape.radius=.28;shape.height=1.76
	c.shape=shape;c.position.y=.88;add_child(c)
	visual=H.model("mc_tactical" if tactical else ("mc_officer" if police else model_id))
	add_child(visual)
	skeleton=H.skeletal(visual)
	if police:
		var gun=H.model("mc_carbine" if tactical else "mc_pistol")
		add_child(gun)
		gun.position=Vector3(.27,1.24,-.46)
		health=140 if tactical else  90
	new_destination()
func new_destination():
	var p=global_position
	var along_z=randf()<.5
	if along_z:
		target=Vector3(roundf(p.x/128)*128+12,0,roundf(p.z/128)*128+(128 if randf()<.5 else -128)+12)
	else:
		target=Vector3(roundf(p.x/128)*128+(128 if randf()<.5 else -128)+12,0,roundf(p.z/128)*128+12)
	target.y=game.world.height_at(target.x,target.z)
func sees_player() -> bool:
	var p=game.focus()+Vector3.UP
	var distance=global_position.distance_to(p)
	var limit=90.0 if police else  60
	if game.player.crouched:limit*=.6
	if distance>limit:return false
	var look=-global_basis.z
	if not police and look.dot((p-global_position).normalized())<-.1:return false
	var hit=H.ray(self,global_position+Vector3.UP*1.6,p,[get_rid()],7)
	return hit.is_empty() or hit.get("collider")==game.player or hit.get("collider")==game.player.vehicle
func witness(value:float, source:Vector3):
	panic= 12
	last_threat=source
	if police:
		game.raise_wanted(value)
	elif report_delay<0:
		report_delay=3.5
		report_value=value
func _physics_process(dt):
	if dead:return
	life+=dt
	var distance=global_position.distance_to(game.focus())
	if distance>300:
		queue_free();return
	think-=dt;fire_timer-=dt
	panic=maxf(0,panic-dt)
	if report_delay>=0:
		report_delay-=dt
		if report_delay<=0:
			if global_position.distance_to(last_threat)<130:game.raise_wanted(report_value)
			report_delay=-1
	if distance>150 and int(life*10)%3!=0:return
	var visible_target=false
	if police and game.wanted>0:
		visible_target=sees_player()
		target=game.focus() if visible_target else game.last_known
		if visible_target:game.police_saw_player()
		if visible_target and distance< 40 and game.wanted>=2:
			if fire_timer<=0:
				fire_timer= .32 if tactical else .85
				rounds-=1
				if rounds<=0:rounds=12;fire_timer=2.4
				var from=global_position+Vector3.UP*1.35-global_basis.z*.55
				game.tracer(from,game.focus()+Vector3.UP,Color(1,.68,.25))
				game.sound("shot",from,.5)
				if randf()<(.48 if tactical else .24):game.player.take_damage(11 if tactical else 8)
		if distance<2.5 and game.weapon_index==0 and game.wanted<=2:
			game.arrest_progress+=dt
			if game.arrest_progress>2.0:game.respawn_player("BUSTED")
	elif panic>0:
		target=global_position+(global_position-last_threat).normalized()* 15
	elif think<=0:
		think=3+randf()*4
		if global_position.distance_to(target)<4:new_destination()
	var direction=target-global_position
	direction.y=0
	var speed=4.2 if police or panic>0 else 1.35
	if visible_target and distance< 20:speed=0.5
	if direction.length()<1:speed=0
	direction=direction.normalized()
	var obstacle=H.ray(self,global_position+Vector3.UP*.7,global_position+Vector3.UP*.7+direction*1.2,[get_rid()],1)
	if not obstacle.is_empty():
		direction=direction.slide(obstacle.normal).normalized()
		if direction.length()<.1:direction=obstacle.normal.cross(Vector3.UP)
	velocity.x=direction.x*speed
	velocity.z=direction.z*speed
	velocity.y-= 20*dt
	move_and_slide()
	if direction.length()>.1:rotation.y=lerp_angle(rotation.y,atan2(-direction.x,-direction.z),dt*8)
	anim+=dt*speed*2
	H.animate(skeleton,anim,speed,police and visible_target)
	if global_position.x>900:queue_free()
func take_damage(amount:float, by_player:bool=true):
	if dead:return
	health-=amount
	panic= 15
	last_threat=game.focus()
	if by_player:
		if not police:game.crime(.7,global_position,60)
		else:game.raise_wanted(.7)
	if health<=0:
		dead=true
		collision_layer=0
		collision_mask=0
		if by_player:
			game.cash+=randi_range(15,90)
			game.add_skill("Shooting",.4)
		game.effect(global_position+Vector3.UP,Color(.28,.06,.04),8,.35,1.2)
		var rag=RigidBody3D.new()
		game.add_child(rag)
		rag.global_transform=global_transform
		rag.mass= 70
		rag.collision_layer=0;rag.collision_mask=1
		H.collider(rag,Vector3(.4,1.5,.3),Vector3(0,.8,0))
		remove_child(visual);rag.add_child(visual)
		rag.apply_impulse(-global_basis.z*80+Vector3.UP*30,Vector3.UP)
		var t=game.get_tree().create_timer( 18)
		t.timeout.connect(func():if is_instance_valid(rag):rag.queue_free())
		queue_free()
