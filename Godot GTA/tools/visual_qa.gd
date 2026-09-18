extends SceneTree
const H=preload("res://gta/code/helpers.gd")
var game
var frames_times=[]
func _initialize():call_deferred("run")
func wait_frames(n):
	for i in range(n):await process_frame
func capture(name:String, eye:Vector3=Vector3.INF, target:Vector3=Vector3.ZERO):
	if eye!=Vector3.INF:
		game.set_process(false)
		game.player.camera.global_position=eye
		game.player.camera.look_at(target)
	await wait_frames(5)
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_jpg("res://.astra-run/screenshots/"+name+".jpg")
	print("VISUAL_CAPTURE ",name," fps=",Engine.get_frames_per_second()," draw_calls=",RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME))
	game.set_process(true)
func run():
	game=load("res://gta/scenes/main.tscn").instantiate()
	root.add_child(game);current_scene=game
	game.invulnerable=true
	await wait_frames(700)
	await capture("final_downtown")
	await capture("city_overview",Vector3(130, 80,170),Vector3( 30, 15,0))
	game.hour=23
	game.weather="Rain";game.weather_timer=0
	await wait_frames(150)
	await capture("night_rain")
	game.weather="Clear";game.hour= 14;game.weather_timer=0
	game.teleport("Harbor")
	await wait_frames(130)
	await capture("harbor",Vector3(1010, 20,560),Vector3(865,3,490))
	game.teleport("Airport")
	await wait_frames(130)
	await capture("airport",Vector3(-470,25,1255),Vector3(-470,2,1000))
	game.teleport("Highlands")
	await wait_frames(130)
	await capture("highlands",game.player.position+Vector3(45,25,40),game.player.position+Vector3(0,0,- 50))
	game.teleport("Downtown")
	game.player.position=Vector3(16,0,22)
	await wait_frames(100)
	game.ui.open_menu("Vehicles")
	await capture("vehicle_menu")
	game.ui.close_menu()
	game.ui.toggle_map()
	await capture("world_map")
	game.ui.close_menu()
	game.teleport("Downtown")
	await wait_frames(100)
	game.set_process(false)
	for name in ["mc_sedan","mc_player","mc_officer","mc_pistol","mc_rifle","mc_boat","mc_helicopter","mc_plane"]:
		var model=H.model(name)
		game.add_child(model)
		model.position=Vector3(0,400,0)
		var points=[]
		for m in H.find_meshes(model):
			var a=m.get_aabb()
			for i in range(8):points.append(m.global_transform*a.get_endpoint(i))
		var bounds=AABB(points[0],Vector3.ZERO)
		for p in points:bounds=bounds.expand(p)
		var center=bounds.get_center()
		var distance=bounds.size.length()*1.1
		game.player.camera.global_position=center+Vector3(1.15,.55,1.6).normalized()*distance
		game.player.camera.look_at(center)
		game.ui.root.visible=false
		await wait_frames(4)
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_jpg("res://.astra-run/screenshots/godot_"+name+".jpg")
		print("ASSET_VISUAL ",name," bounds=",bounds.size)
		model.queue_free()
	game.ui.root.visible=true
	game.queue_free()
	await wait_frames(3)
	H.cache.clear()
	quit()
