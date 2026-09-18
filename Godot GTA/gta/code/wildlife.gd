extends CharacterBody3D
const H=preload("res://gta/code/helpers.gd")
var game
var species="deer"
var home=Vector3.ZERO
var phase=0.0
var visual:Node3D
var health=45.0
func _ready():
	process_mode=Node.PROCESS_MODE_PAUSABLE
	collision_layer=2 if species=="deer" else 0
	collision_mask=1 if species=="deer" else 0
	visual=H.model("mc_"+species);add_child(visual)
	if species=="deer":H.collider(self,Vector3(.45,1.1,1.3),Vector3(0,.65,0))
	home=position;phase=randf()*TAU
func _physics_process(dt):
	if not game.wildlife_enabled or position.distance_to(game.focus())>450:queue_free();return
	phase+=dt*(.24 if species=="deer" else .55)
	var desired=home+Vector3(sin(phase)*20,0,cos(phase*.83)*20)
	if species=="deer":
		var away=position-game.focus()
		var panic=away.length()<25 or game.wanted>0
		var dir=away.normalized() if panic else (desired-position).normalized()
		velocity.x=dir.x*(5.0 if panic else 1.2);velocity.z=dir.z*(5.0 if panic else 1.2)
		velocity.y-=20*dt
		move_and_slide()
		visual.position.y=abs(sin(phase*(22 if panic else 9)))*(.09 if panic else .02)
	else:
		desired.y=home.y+sin(phase*1.5)*(2.0 if species=="gull" else .5)
		velocity=(desired-position)*.7
		position+=velocity*dt
		if species=="gull":visual.rotation.z=sin(phase*4)*.18
	if velocity.length()>.1:rotation.y=atan2(-velocity.x,-velocity.z)
func take_damage(amount:float, _by_player:bool=true):
	health-=amount
	if health<=0:
		game.effect(global_position,Color(.28,.1,.07),5,.3,1)
		queue_free()
