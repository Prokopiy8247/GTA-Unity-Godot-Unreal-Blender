extends RigidBody3D
const H=preload("res://gta/code/helpers.gd")
var game
var health=30.0
func _ready():
	mass=14
	collision_layer=4
	collision_mask=5
	var model=H.model("mc_bin")
	add_child(model)
	H.collider(self,Vector3(.6,.96,.6),Vector3(0,.48,0))
func take_damage(amount:float, _by_player:bool=true):
	health-=amount
	apply_central_impulse(-game.player.camera.global_basis.z*40+Vector3.UP*8)
	game.sound("impact",global_position,.6)
	if health<=0:
		game.effect(global_position+Vector3.UP*.4,Color(.3,.3,.25),10,.5,3)
		queue_free()
