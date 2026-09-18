extends SceneTree
const H=preload("res://gta/code/helpers.gd")
var game
func _initialize():call_deferred("run")
func run():
	game=load("res://gta/scenes/main.tscn").instantiate()
	root.add_child(game);current_scene=game
	game.invulnerable=true
	for i in range(240):await process_frame
	var samples=[]
	var phases=[]
	for index in range(3):
		var label=["day_traffic","storm_pursuit","harbor_air"][index]
		if index==1:
			game.set_wanted(5);game.weather="Storm";game.hour=23;game.weather_timer=0
		elif index==2:
			game.set_wanted(0);game.teleport("Harbor");game.weather="Clear";game.hour=14;game.weather_timer=0
			var heli=game.spawn_vehicle("helicopter")
			game.player.position=heli.position+Vector3(2,0,0)
			game.enter_exit()
			Input.action_press("jump")
		var began=Time.get_ticks_usec()
		var previous=began
		var durations=[]
		while Time.get_ticks_usec()-began<20000000:
			await process_frame
			var now=Time.get_ticks_usec()
			durations.append((now-previous)/1000.0);previous=now
		Input.action_release("jump")
		durations.sort()
		var sum=0.0
		for value in durations:sum+=value
		var item={"scenario":label,"frames":durations.size(),"seconds":sum/1000.0,
			"mean_fps":1000.0/(sum/durations.size()),"p95_frame_ms":durations[int(durations.size()*.95)],
			"max_frame_ms":durations.back(),"sectors":game.world.sectors.size(),
			"nodes":get_node_count(),"static_memory_mb":OS.get_static_memory_usage()/1048576.0,
			"draw_calls":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME)}
		phases.append(item);print("SOAK ",JSON.stringify(item))
	var file=FileAccess.open("res://.astra-run/performance-results.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"gpu":RenderingServer.get_video_adapter_name(),"phases":phases}, "\t"));file.close()
	if is_instance_valid(game.player.vehicle):game.exit_vehicle()
	game.queue_free()
	for i in range(4):await process_frame
	H.cache.clear()
	quit()
