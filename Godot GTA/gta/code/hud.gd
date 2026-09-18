extends Control
var game
var ui
var font=ThemeDB.fallback_font
var ink=Color(.90,.92,.88)
var muted=Color(.57,.64,.65)
var accent=Color(.9,.68,.34)
func _ready():
	mouse_filter=Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
func _process(_dt):queue_redraw()
func txt(p:Vector2, text:String, size_value:int=18, color:Color=ink):
	draw_string(font,p,text,HORIZONTAL_ALIGNMENT_LEFT,-1,size_value,color)
func panel(rect:Rect2):
	draw_style_box(ui.panel_style,rect)
func _draw():
	if not is_instance_valid(game.player):return
	var s=get_viewport_rect().size
	var player=game.player
	if ui.map_open:
		draw_rect(Rect2(Vector2.ZERO,s),Color(.025,.04,.047,.97))
		var area=Rect2(70,100,s.x-140,s.y-180)
		draw_map(area,Vector3.ZERO,1600,true)
		txt(Vector2(70, 50),"MERIDIAN COAST", 30)
		txt(Vector2(70, 80),"Click to place a waypoint   /   M or Esc to close", 16,muted)
		return
	if game.menu_open:return
	txt(Vector2(32, 40),"MERIDIAN COAST", 20,ink)
	draw_line(Vector2(32,54),Vector2(85,54),accent,3)
	txt(Vector2(32, 80),game.world.district(game.focus()), 14,muted)
	var status="%02d:%02d  /  %s" % [int(game.hour),int(fmod(game.hour,1)*60),game.weather.to_upper()]
	txt(Vector2(32,105),status,14,muted)
	txt(Vector2(s.x-220, 40),"$ %s" % game.cash,26,ink)
	for i in range(5):
		var color=Color(.22,.27,.29)
		if i<game.wanted:
			color=accent
			if game.pursuit=="SEARCH" and sin(Time.get_ticks_msec()*.006)<0:color=accent*.45
		star(Vector2(s.x- 50-i*33, 70), 12,color)
	if game.wanted>0:txt(Vector2(s.x-220,108),game.pursuit+"  /  "+str(game.wanted),14,accent)
	var map_area=Rect2(28,s.y-260,250,195)
	panel(Rect2(22,s.y-288,262,264))
	draw_map(map_area,game.focus(),155,false)
	txt(Vector2(35,s.y-268),"LOCAL RADAR", 12,muted)
	var health=clampf(player.health/100,0,1)
	var armor=clampf(player.armor/100,0,1)
	draw_rect(Rect2(35,s.y- 50,112,5),Color(.14,.2,.2))
	draw_rect(Rect2(35,s.y- 50,112*health,5),Color(.57,.74,.57))
	draw_rect(Rect2(154,s.y- 50,112,5),Color(.14,.2,.2))
	draw_rect(Rect2(154,s.y- 50,112*armor,5),Color(.46,.64,.75))
	txt(Vector2(35,s.y- 30),"HEALTH %03d" % player.health, 11,muted)
	txt(Vector2(154,s.y- 30),"ARMOR %03d" % player.armor, 11,muted)
	var weapon=game.D.WEAPONS[game.weapon_index]
	panel(Rect2(s.x-268,s.y-130,240,100))
	txt(Vector2(s.x-250,s.y-100),weapon.name.to_upper(),16,ink)
	var ammo="—" if weapon.mag==0 else "%02d  /  %03d" % [int(game.magazines[str(game.weapon_index)]),int(game.reserve[str(game.weapon_index)])]
	if game.reload_timer>0:ammo="RELOADING"
	txt(Vector2(s.x-250,s.y- 60),ammo,28,accent)
	if is_instance_valid(player.vehicle):
		var v=player.vehicle
		txt(Vector2(s.x-260,s.y-170),"%03d" % int(abs(v.speed)*3.6), 40,ink)
		txt(Vector2(s.x-158,s.y-170),"KM/H",14,muted)
		txt(Vector2(s.x-260,s.y-150),v.data.name+"  /  "+str(int(v.health))+"%",14,muted)
		if v.kind in ["heli","plane"]:txt(Vector2(s.x-260,s.y-205),"ALT  %04d M" % v.global_position.y,16,ink)
	else:
		var center=s*.5
		if player.aiming:
			if game.weapon_index==9:
				draw_circle(center,150,Color(.02,.025,.03,.35))
				draw_line(center-Vector2(210,0),center+Vector2(210,0),ink*.8,1)
				draw_line(center-Vector2(0,180),center+Vector2(0,180),ink*.8,1)
			for d in [Vector2.LEFT,Vector2.RIGHT,Vector2.UP,Vector2.DOWN]:
				draw_line(center+d*5,center+d* 12,Color(1,1,.94,.8),1)
		else:draw_circle(center,1.5,Color(.95,.93,.84,.7))
	if player.swimming:
		txt(Vector2(s.x*.5-80,s.y- 80),"OXYGEN  %03d%%" % player.breath,16,accent)
	elif player.stamina< 90:
		draw_rect(Rect2(s.x*.5-80,s.y- 70,160*player.stamina/100,3),accent)
	if game.nearest_service:
		txt(Vector2(s.x*.5-200,s.y-150),"[ E ]  "+game.nearest_service.name, 20,ink)
	else:
		var near=false
		for v in game.vehicles:
			if is_instance_valid(v) and not v.destroyed and v.global_position.distance_to(player.global_position)<4.2:near=true;break
		if near and player.vehicle==null:txt(Vector2(s.x*.5-110,s.y-150),"[ F ]  Enter vehicle", 18,ink)
	if game.notification_time>0:
		var w=minf(820,s.x- 60)
		panel(Rect2((s.x-w)/2,128,w,42))
		txt(Vector2((s.x-w)/2+ 16,156),game.notification,16,ink)
	txt(Vector2(310,s.y- 30),"F1  SANDBOX     TAB  WEAPONS     M  MAP     E  INTERACT",12,muted)
	txt(Vector2(s.x-250,145),"%d FPS  /  %d SECTORS" % [Engine.get_frames_per_second(),game.world.sectors.size()],12,muted)
	if game.range_active:txt(Vector2(s.x*.5-130,210),"RANGE  %02ds  /  %s HITS" % [game.range_time,game.range_score],20,accent)
	if game.waypoint!=Vector3.INF:
		txt(Vector2(32,132),"WAYPOINT  %d M" % game.focus().distance_to(game.waypoint),14,accent)
	if game.hurt_flash>0:draw_rect(Rect2(Vector2.ZERO,s),Color(.5,.02,.01,game.hurt_flash*.5))
	if not ui.death_text.is_empty():
		draw_rect(Rect2(Vector2.ZERO,s),Color(.02,.025,.03,.55))
		txt(s*.5-Vector2(130,0),ui.death_text,54,accent)
func star(center:Vector2,radius:float,color:Color):
	var points=PackedVector2Array()
	for i in range(10):
		var a=-PI/2+i*PI/5
		points.append(center+Vector2(cos(a),sin(a))*radius*(1.0 if i%2==0 else .45))
	draw_colored_polygon(points,color)
func draw_map(rect:Rect2, focus_pos:Vector3, radius:float, full:bool):
	draw_rect(rect,Color(.065,.095,.106))
	var scale_factor=rect.size.x/(radius*2)
	var origin=rect.get_center()
	var to_map=func(p):return origin+Vector2(p.x-focus_pos.x,p.z-focus_pos.z)*scale_factor
	var coast=to_map.call(Vector3(900,0,0)).x
	if coast<rect.end.x:draw_rect(Rect2(maxf(coast,rect.position.x),rect.position.y,rect.end.x-maxf(coast,rect.position.x),rect.size.y),Color(.055,.16,.19))
	for axis in range(-12,13):
		var n=axis*128
		var x=origin.x+(n-focus_pos.x)*scale_factor
		var y=origin.y+(n-focus_pos.z)*scale_factor
		if x>rect.position.x and x<minf(rect.end.x,coast):
			draw_line(Vector2(x,rect.position.y),Vector2(x,rect.end.y),Color(.22,.27,.28),2 if full else 7)
		if y>rect.position.y and y<rect.end.y:
			draw_line(Vector2(rect.position.x,y),Vector2(minf(rect.end.x,coast),y),Color(.22,.27,.28),2 if full else 7)
	for place in game.D.PLACES:
		var p=to_map.call(game.D.PLACES[place])
		if rect.has_point(p):
			draw_circle(p,3,accent)
			if full:txt(p+Vector2(6,-6),place, 14,ink)
	for a in game.actors:
		if is_instance_valid(a) and a.police:
			var p=to_map.call(a.global_position)
			if rect.has_point(p):draw_circle(p,3,Color(.36,.57,1))
	for v in game.vehicles:
		if is_instance_valid(v):
			var p=to_map.call(v.global_position)
			if rect.has_point(p):draw_rect(Rect2(p-Vector2(2,2),Vector2(4,4)),Color(.3,.5,.95) if v.police else Color(.48,.52,.48))
	var p=to_map.call(game.focus())
	if rect.has_point(p):
		var heading=game.player.yaw
		var pts=PackedVector2Array()
		for v in [Vector2(0,-7),Vector2(-4,5),Vector2(4,5)]:pts.append(p+v.rotated(-heading))
		draw_colored_polygon(pts,ink)
	if game.waypoint!=Vector3.INF:
		var wp=to_map.call(game.waypoint)
		if rect.has_point(wp):
			draw_line(p,wp,accent,2)
			draw_arc(wp,7,0,TAU,24,accent,2)
func _input(event):
	if ui.map_open and event is InputEventMouseButton and event.pressed and event.button_index==MOUSE_BUTTON_LEFT:
		var s=get_viewport_rect().size
		var area=Rect2(70,100,s.x-140,s.y-180)
		if area.has_point(event.position):
			var delta=(event.position-area.get_center())/(area.size.x/3200)
			game.waypoint=Vector3(delta.x,0,delta.y)
