extends SceneTree
const H=preload("res://gta/code/helpers.gd")
var game
var results=[]
func _initialize():call_deferred("run")
func frames(n:int):
	for i in range(n):await physics_frame
func check(name:String,ok:bool,detail:String=""):
	results.append({"name":name,"pass":ok,"detail":detail})
	print("EXTRA ",name," ", "PASS" if ok else "FAIL"," ",detail)
func run():
	game=load("res://gta/scenes/main.tscn").instantiate()
	root.add_child(game);current_scene=game
	game.invulnerable=true
	await frames(180)
	var traffic=game.vehicles.filter(func(v):return v.ai and not v.police)
	var v=traffic[0];var start=v.position
	await frames(90)
	check("traffic_drives",v.position.distance_to(start)>2,str(v.position.distance_to(start)))
	var nodes_before=game.get_child_count()
	for district in ["Harbor","Airport","Downtown","Highlands","Downtown"]:
		game.teleport(district);await frames(90)
	check("stream_bound",game.world.sectors.size()==25)
	check("forest_multimesh",game.world.get_children().any(func(n):return n is MultiMeshInstance3D))
	game.teleport("Countryside");game.populate();await frames(60)
	check("deer_population",game.animals.any(func(a):return is_instance_valid(a) and a.species=="deer"))
	game.teleport("Harbor");await frames(60);game.populate();await frames(60)
	check("gull_population",game.animals.any(func(a):return is_instance_valid(a) and a.species=="gull"))
	game.teleport("Downtown");await frames(60)
	for a in game.actors:
		if is_instance_valid(a):a.queue_free()
	game.actors.clear()
	game.traffic_enabled=false;game.pedestrians_enabled=false
	game.set_wanted(0)
	var civilian=game.spawn_actor(game.player.position+Vector3(0,0,-9),false)
	civilian.take_damage(10,false)
	await frames(260)
	check("unrelated_npc_damage_not_crime",game.wanted==0)
	civilian.witness(1,game.player.position)
	await frames(120)
	check("witness_delay",game.wanted==0)
	await frames(150)
	check("witness_report",game.wanted>0)
	game.set_wanted(0)
	for i in range(6):
		game.set_wanted(i)
		check("wanted_level_"+str(i),game.wanted==i)
		game.set_wanted(0)
		await frames(2)
	game.cash=5000
	game.owned.erase(5)
	game.buy_weapon(5)
	check("weapon_shop",game.owned.has(5) and game.cash==3800)
	game.cash=0
	var balance=game.cash
	game.buy_weapon(9)
	check("shop_insufficient_funds",not game.owned.has(9) and game.cash==balance)
	game.cash=12500
	game.select_weapon(3)
	game.attachments.suppressor=true;game.attachments.optic=true;game.attachments.flashlight=true;game.attachments.extended=true
	game.player.equip("pistol")
	check("attachment_models",game.player.gun.get_child_count()>=4)
	check("extended_magazine",game.capacity()>15)
	Input.action_press("aim");await frames(10);Input.action_release("aim")
	check("weapon_flashlight",game.player.flashlight.visible)
	game.weather="Rain";game.weather_timer=0;game.update_environment(1)
	check("rain_particles",game.rain.emitting)
	check("wet_road",game.world.roadmat.get_shader_parameter("wet")==1)
	game.weather="Fog";game.weather_timer=0;game.update_environment(1)
	check("fog",game.env.fog_density>.004)
	game.hour=23;await frames(40)
	check("night_lamps",game.world.street_lights.any(func(l):return is_instance_valid(l) and l.visible))
	game.teleport("Downtown")
	game.player.position=Vector3(5,.1, 90)
	game.call_taxi("Old Quarter")
	await frames(5)
	var taxi=game.player.vehicle
	check("taxi_passenger",is_instance_valid(taxi) and not taxi.driver and taxi.ai)
	var initial=taxi.position
	await frames(360)
	check("taxi_ride",taxi.position.distance_to(initial)>10,str(taxi.position.distance_to(initial)))
	game.skip_taxi()
	check("taxi_skip",game.player.vehicle==null and game.player.position.distance_to(game.D.PLACES["Old Quarter"])<6)
	game.teleport("Downtown")
	var car=game.spawn_vehicle("sedan",Vector3(5,.4, 60))
	await frames(60)
	game.player.position=car.position+Vector3(2,.2,0);game.enter_exit()
	game.select_weapon(3);var ammunition=game.magazines["3"]
	game.shoot_timer=0;game.fire_weapon()
	check("drive_by",game.magazines["3"]==ammunition-1)
	game.exit_vehicle()
	game.set_outfit(Color(.4,.2,.1));game.saved_vehicles=[{"id":"sedan","paint":"ffcc88","tune":1.25,"brakes":1.3}]
	game.save_game(false);game.saved_vehicles=[];game.set_outfit(Color.BLACK);game.load_game()
	check("garage_persistence",game.saved_vehicles.size()==1)
	check("clothing_persistence",game.outfit.r>.39)
	game.teleport("Downtown")
	var repair_car=game.spawn_vehicle("sedan",Vector3(70,.4,-14))
	await frames(70)
	game.player.position=repair_car.position+Vector3(2,.2,0);game.enter_exit()
	Input.action_press("forward");await frames(130);Input.action_release("forward")
	check("garage_entry",repair_car.position.z < -26,str(repair_car.position))
	game.exit_vehicle()
	game.start_range()
	game.range_hit(game.range_targets[0])
	check("shooting_range_score",game.range_score==1 and game.range_active)
	# A grenade and rocket run their full timers/collision paths.
	for grenade in [true,false]:
		game.launch_projectile(game.player.position+Vector3(0,2,-3),Vector3.FORWARD,grenade)
	await frames(300)
	check("projectile_cleanup",game.effects_count<48)
	check("no_mission_nodes",not game.has_node("MissionManager"))
	var file=FileAccess.open("res://.astra-run/extra-qa-results.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(results,"\t"));file.close()
	var failed=results.filter(func(r):return not r.pass)
	print("EXTRA_RESULT ",results.size()-failed.size(),"/",results.size()," PASS")
	game.queue_free()
	await process_frame
	await process_frame
	H.cache.clear()
	quit(0 if failed.is_empty() else 2)
