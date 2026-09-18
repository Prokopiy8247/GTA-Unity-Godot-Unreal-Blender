extends CanvasLayer
const D=preload("res://gta/code/data.gd")
const H=preload("res://gta/code/helpers.gd")
var game
var hud
var root:Control
var menu:PanelContainer
var tabs:TabContainer
var underwater:ColorRect
var panel_style:StyleBoxFlat
var map_open=false
var death_text=""
var service_mode=""
var stats_label:Label
func _ready():
	layer=10
	root=Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter=Control.MOUSE_FILTER_IGNORE
	add_child(root)
	panel_style=StyleBoxFlat.new()
	panel_style.bg_color=Color(.025,.045,.055,.9)
	panel_style.border_color=Color(.22,.28,.29,.6)
	panel_style.set_border_width_all(1)
	panel_style.set_corner_radius_all(7)
	underwater=ColorRect.new()
	underwater.color=Color(.015,.22,.26,.45)
	underwater.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	underwater.mouse_filter=Control.MOUSE_FILTER_IGNORE
	root.add_child(underwater);underwater.visible=false
	hud=preload("res://gta/code/hud.gd").new()
	hud.game=game;hud.ui=self;root.add_child(hud)
	create_menu()
func create_menu():
	menu=PanelContainer.new()
	root.add_child(menu)
	menu.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	menu.offset_left=70;menu.offset_top=45;menu.offset_right=-70;menu.offset_bottom=-45
	menu.add_theme_stylebox_override("panel",panel_style)
	var margin=MarginContainer.new()
	for edge in ["left","right","top","bottom"]:margin.add_theme_constant_override("margin_"+edge,22)
	menu.add_child(margin)
	var column=VBoxContainer.new();column.add_theme_constant_override("separation",14);margin.add_child(column)
	var title=Label.new();title.text="MERIDIAN  /  FREE ROAM";title.add_theme_font_size_override("font_size", 30);column.add_child(title)
	var subtitle=Label.new();subtitle.text="A city without objectives. Choose your own direction.     F1 / ESC to resume";subtitle.modulate=Color(.61,.69,.7);column.add_child(subtitle)
	tabs=TabContainer.new();tabs.size_flags_vertical=Control.SIZE_EXPAND_FILL;column.add_child(tabs)
	var theme=Theme.new()
	theme.default_font_size= 18
	var btn=panel_style.duplicate()
	btn.bg_color=Color(.09,.14,.16)
	btn.content_margin_left= 16;btn.content_margin_right= 16;btn.content_margin_top= 11;btn.content_margin_bottom= 11
	theme.set_stylebox("normal","Button",btn)
	var hover=btn.duplicate();hover.bg_color=Color(.19,.26,.27);hover.border_color=Color(.76,.58,.3)
	theme.set_stylebox("hover","Button",hover)
	theme.set_stylebox("pressed","Button",hover)
	menu.theme=theme
	build_pages()
	menu.visible=false
func page(name:String) -> VBoxContainer:
	var scroll=ScrollContainer.new();scroll.name=name
	tabs.add_child(scroll)
	scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED
	var box=VBoxContainer.new();box.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	box.add_theme_constant_override("separation",8);scroll.add_child(box)
	return box
func heading(box:Node,text:String):
	var l=Label.new();l.text=text;l.add_theme_font_size_override("font_size", 20);l.modulate=Color(.91,.7,.4)
	box.add_child(l)
func button(box:Node,text:String, action:Callable):
	var b=Button.new();b.text=text;b.alignment=HORIZONTAL_ALIGNMENT_LEFT
	b.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	box.add_child(b);b.pressed.connect(action)
	return b
func build_pages():
	for c in tabs.get_children():c.queue_free();tabs.remove_child(c)
	var sandbox=page("Sandbox")
	heading(sandbox,"BENCHMARK / DIRECT ACCESS")
	var grid=GridContainer.new();grid.columns=3;sandbox.add_child(grid)
	grid.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	for place in D.PLACES:
		button(grid,place,func():game.teleport(place);close_menu())
	heading(sandbox,"POLICE RESPONSE")
	var stars=HBoxContainer.new();sandbox.add_child(stars)
	for i in range(6):button(stars,str(i)+" stars",func():game.set_wanted(i);close_menu())
	button(sandbox,"Restore health, armor and ammunition",func():game.player.health=100;game.player.armor=100;refill();game.notify("Restored"))
	button(sandbox,"Invulnerability: toggle",func():game.invulnerable=not game.invulnerable;game.notify("Invulnerability "+str(game.invulnerable)))
	button(sandbox,"Add $25,000",func():game.cash+=25000;game.notify("$25,000 added"))
	button(sandbox,"Unlock every implemented weapon",func():
		game.owned=range(D.WEAPONS.size())
		refill()
		game.notify("Armory unlocked"))
	button(sandbox,"Traffic: toggle",func():
		game.traffic_enabled=not game.traffic_enabled
		if not game.traffic_enabled:
			for v in game.vehicles:
				if is_instance_valid(v) and v.ai and not v.police:v.queue_free()
		game.notify("Traffic "+str(game.traffic_enabled)))
	button(sandbox,"Pedestrians: toggle",func():
		game.pedestrians_enabled=not game.pedestrians_enabled
		if not game.pedestrians_enabled:
			for a in game.actors:
				if is_instance_valid(a) and not a.police:a.queue_free()
		game.notify("Pedestrians "+str(game.pedestrians_enabled)))
	button(sandbox,"Wildlife: toggle",func():game.wildlife_enabled=not game.wildlife_enabled;game.notify("Wildlife "+str(game.wildlife_enabled)))
	button(sandbox,"Scuba / unlimited breath: toggle",func():game.scuba=not game.scuba;game.notify("Scuba "+str(game.scuba)))
	button(sandbox,"Parachute jump above the coast",func():
		game.teleport("Coast");game.player.position.y=350;close_menu();game.notify("Press P to deploy · Space to flare"))
	var fleet=page("Vehicles")
	heading(fleet,"SPAWN / ALL VEHICLES ARE DRIVABLE")
	var vg=GridContainer.new();vg.columns=2;fleet.add_child(vg)
	for id in D.VEHICLES:
		var d=D.VEHICLES[id]
		button(vg,d.name+"  ·  "+d.kind,func():
			if is_instance_valid(game.player.vehicle):game.exit_vehicle()
			var v=game.spawn_vehicle(id)
			game.player.position=v.position+Vector3(2.8,.8,0)
			game.world.update_sectors(true)
			close_menu()
			game.notify("Vehicle delivered · F to enter"))
	var armory=page("Armory")
	heading(armory,"INVENTORY / SELECT OR PURCHASE")
	var ag=GridContainer.new();ag.columns=2;armory.add_child(ag)
	for i in range(D.WEAPONS.size()):
		var w=D.WEAPONS[i]
		button(ag,w.name+"  ·  $"+str(w.price),func():
			if game.owned.has(i):game.select_weapon(i);close_menu()
			else:game.buy_weapon(i))
	button(armory,"Ammunition refill  ·  $200",func():if game.spend(200):refill();game.notify("Ammunition replenished"))
	button(armory,"Body armor  ·  $500",func():if game.spend(500):game.player.armor=100;game.notify("Armor equipped"))
	heading(armory,"WEAPON WORKBENCH")
	for part in ["suppressor","extended","grip","optic","flashlight"]:
		button(armory,part.capitalize()+"  ·  $350",func():
			if game.attachments[part]:game.notify("Already installed")
			elif game.spend(350):game.attachments[part]=true;game.player.equip(D.WEAPONS[game.weapon_index].id);game.notify(part.capitalize()+" installed"))
	var garage=page("Garage")
	heading(garage,"COASTLINE MOTORWORKS / NEARBY VEHICLE")
	button(garage,"Repair vehicle  ·  $250",func():
		var v=near_vehicle()
		if v and game.spend(250):v.repair();game.notify("Vehicle repaired"))
	var colors=HBoxContainer.new();garage.add_child(colors)
	for pair in [["Lagoon",Color(.035,.23,.25)],["Oxide",Color(.48,.045,.027)],["Pearl",Color(.75,.77,.72)],["Onyx",Color(.025,.03,.037)],["Bronze",Color(.4,.22,.07)]]:
		button(colors,pair[0]+"  $150",func():
			var v=near_vehicle()
			if v and game.spend(150):v.repaint(pair[1]);game.notify("Paint applied"))
	button(garage,"Engine upgrade: +25% thrust and top speed  ·  $1,200",func():
		var v=near_vehicle()
		if v and game.spend(1200):v.tune=minf(v.tune+.25,1.75);game.notify("Engine tuned"))
	button(garage,"Brake upgrade: +30% braking force  ·  $600",func():
		var v=near_vehicle()
		if v and game.spend(600):v.brake_tune=minf(v.brake_tune+.3,1.9);game.notify("Brakes upgraded"))
	button(garage,"Store nearby vehicle in personal garage",func():
		var v=near_vehicle()
		if v:
			if game.saved_vehicles.size()>=5:game.saved_vehicles.pop_front()
			game.saved_vehicles.append({"id":v.id,"paint":v.paint.to_html(),"tune":v.tune,"brakes":v.brake_tune})
			v.owned=true
			game.save_game(false)
			game.notify("Vehicle stored · "+str(game.saved_vehicles.size())+" / 5"))
	button(garage,"Retrieve last stored vehicle",func():
		if game.saved_vehicles.is_empty():game.notify("Garage is empty");return
		var data=game.saved_vehicles.back()
		var v=game.spawn_vehicle(data.id)
		v.repaint(Color(data.paint));v.tune=data.tune;v.brake_tune=data.brakes
		v.owned=true;close_menu())
	var world_page=page("World")
	heading(world_page,"TIME / WEATHER")
	var times=HBoxContainer.new();world_page.add_child(times)
	for t in [6.5,12.0,16.4,19.2,23.0]:button(times,str(t)+" h",func():game.hour=t;game.weather_timer=0;close_menu())
	var weathers=HBoxContainer.new();world_page.add_child(weathers)
	for w in ["Clear","Cloudy","Rain","Fog","Storm"]:button(weathers,w,func():game.weather=w;game.weather_timer=0;close_menu())
	button(world_page,"Save progress  ·  F5",func():game.save_game())
	button(world_page,"Load progress  ·  F9",func():game.load_game();close_menu())
	button(world_page,"Photo: save current game view",func():close_menu();game.capture_screenshot("photo_"+str(Time.get_unix_time_from_system())))
	var home=page("Services")
	heading(home,"HARBOR HOUSE / PERSONAL SERVICES")
	button(home,"Sleep until morning",func():game.hour=7;game.player.health=100;game.save_game();close_menu())
	for pair in [["Slate",Color(.075,.1,.115)],["Sand",Color(.4,.32,.19)],["Burgundy",Color(.3,.025,.04)]]:
		button(home,"Jacket · "+pair[0]+"  $120",func():
			if game.spend(120):
				game.set_outfit(pair[1])
				game.notify("Wardrobe updated"))
	heading(home,"TAXI / PASSENGER SERVICE")
	button(home,"Skip the current taxi trip",func():game.skip_taxi();close_menu())
	for place in ["Downtown","Airport","Harbor","Safehouse","Coast"]:
		button(home,"Cab to "+place+"  ·  $75",func():
			game.call_taxi(place);close_menu())
	var status=page("Status")
	stats_label=Label.new();status.add_child(stats_label)
	button(status,"Max all skills (benchmark)",func():
		for skill in game.skills:game.skills[skill]=100
		update_stats())
	button(status,"Reset all skills",func():
		for skill in game.skills:game.skills[skill]=0
		update_stats())
	heading(status,"CONTROLS")
	var controls=Label.new()
	controls.text="WASD · Move / drive     Mouse · Look     Shift · Sprint / dive\nSpace · Jump / handbrake / helicopter climb / parachute flare\nF · Enter / exit     E · Interact     C · Crouch     Q · Cover\nLMB · Fire / melee     RMB · Aim     R · Reload     Wheel / 1–9 · Weapon\nTab · Armory     V · Camera     P · Parachute     M · Map\nH · Horn     J · Siren     L · Lights     T · Original ambient radio\nHelicopter: WASD flight / Space climb / Ctrl descend\nAirplane: W/S throttle / A/D bank / arrows up-down pitch\nF1 / Esc · Sandbox & pause     F5 / F9 · Save / load"
	status.add_child(controls)
	button(status,"Return to free roam",close_menu)
	button(status,"Quit game",func():game.save_game(false);get_tree().quit())
func update_stats():
	if not stats_label:return
	var text="CHARACTER / USE-BASED SKILLS\n\n"
	for skill in game.skills:text+="%s   %0.1f / 100\n" % [skill,game.skills[skill]]
	text+="\nCash  $%s\nCoordinates  %s\nActive sectors  %s\n" % [game.cash,game.focus().round(),game.world.sectors.size()]
	stats_label.text=text
func toggle_menu(tab_name:String):
	if game.menu_open:close_menu()
	else:open_menu(tab_name)
func open_menu(tab_name:String):
	map_open=false
	game.menu_open=true
	get_tree().paused=true
	menu.visible=true
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
	for i in range(tabs.get_tab_count()):
		if tabs.get_tab_title(i)==tab_name:tabs.current_tab=i
	update_stats()
func close_menu():
	menu.visible=false;map_open=false;game.menu_open=false
	get_tree().paused=false
	Input.mouse_mode=Input.MOUSE_MODE_CAPTURED
func open_service(kind:String):
	service_mode=kind
	open_menu({"shop":"Armory","garage":"Garage","home":"Services"}.get(kind,"Services"))
func toggle_map():
	if map_open:close_menu();return
	menu.visible=false;map_open=true;game.menu_open=true
	get_tree().paused=true
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
func refill():
	for i in range(D.WEAPONS.size()):
		game.magazines[str(i)]=D.WEAPONS[i].mag
		game.reserve[str(i)]=300 if i<10 else 20
func near_vehicle():
	if is_instance_valid(game.player.vehicle):return game.player.vehicle
	var closest=null
	var dist= 15
	for v in game.vehicles:
		if is_instance_valid(v) and v.global_position.distance_to(game.focus())<dist:
			closest=v;dist=v.global_position.distance_to(game.focus())
	if not closest:game.notify("Bring a vehicle within 15 metres")
	return closest
