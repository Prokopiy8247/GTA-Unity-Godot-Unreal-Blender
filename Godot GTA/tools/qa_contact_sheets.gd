extends SceneTree
func _initialize():
	var groups={
"game_contact":["final_downtown","city_overview","night_rain","harbor","airport","highlands","vehicle_menu","world_map"],
"godot_assets":["godot_mc_sedan","godot_mc_player","godot_mc_officer","godot_mc_pistol","godot_mc_rifle","godot_mc_boat","godot_mc_helicopter","godot_mc_plane"]}
	for group in groups:
		var out=Image.create(1600,450,false,Image.FORMAT_RGB8)
		out.fill(Color(.06,.06,.07))
		var i=0
		for name in groups[group]:
			var path="res://.astra-run/screenshots/"+name+".jpg"
			if FileAccess.file_exists(path):
				var im=Image.load_from_file(path)
				im.resize(400,225,Image.INTERPOLATE_LANCZOS)
				im.convert(Image.FORMAT_RGB8)
				out.blit_rect(im,Rect2i(0,0,400,225),Vector2i((i%4)*400,(i/4)*225))
			i+=1
		out.save_jpg("res://.astra-run/screenshots/"+group+".jpg")
	quit()
