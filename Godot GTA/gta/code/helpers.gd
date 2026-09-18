extends RefCounted
static var cache = {}
static func model(id:String) -> Node3D:
	var path = "res://gta/generated/models/%s.glb" % id
	if not cache.has(path):
		cache[path] = load(path)
	if cache[path] == null:
		push_error("Missing Blender model: "+path)
		return Node3D.new()
	var n = cache[path].instantiate()
	return n
static func material(color:Color, rough:float=.8, metal:float=0.0) -> StandardMaterial3D:
	var m = StandardMaterial3D.new()
	m.albedo_color=color
	m.roughness=rough
	m.metallic=metal
	return m
static func box(parent:Node, p:Vector3, size:Vector3, mat:Material, solid:bool=false) -> MeshInstance3D:
	var n=MeshInstance3D.new()
	var mesh=BoxMesh.new()
	mesh.size=size
	n.mesh=mesh
	n.material_override=mat
	parent.add_child(n)
	n.position=p
	if solid:
		var body=StaticBody3D.new()
		n.add_child(body)
		var c=CollisionShape3D.new()
		var shape=BoxShape3D.new()
		shape.size=size
		c.shape=shape
		body.add_child(c)
	return n
static func collider(parent:Node, size:Vector3, p:Vector3=Vector3.ZERO) -> CollisionShape3D:
	var c=CollisionShape3D.new()
	var sh=BoxShape3D.new()
	sh.size=size
	c.shape=sh
	c.position=p
	parent.add_child(c)
	return c
static func skeletal(root:Node) -> Skeleton3D:
	if root is Skeleton3D:return root
	for c in root.get_children():
		var s=skeletal(c)
		if s:return s
	return null
static func animate(s:Skeleton3D, t:float, speed:float, aiming:bool=false, crouch:bool=false):
	if not s:return
	for side in ["L","R"]:
		var phase=t+(PI if side=="R" else 0.0)
		var stride=sin(phase)*minf(speed*.105,.68)
		for pair in [["Thigh",stride],["Shin",maxf(0,-stride)*1.4],["Arm",-stride*.65],["Forearm",-.12]]:
			var idx=s.find_bone(pair[0]+side)
			if idx>=0:
				var angle=pair[1]
				if aiming and pair[0]=="Arm":angle=-1.3
				if aiming and pair[0]=="Forearm":angle=-.35
				s.set_bone_pose_rotation(idx,s.get_bone_rest(idx).basis.get_rotation_quaternion()*Quaternion(Vector3.RIGHT,angle))
	var spine=s.find_bone("Spine")
	if spine>=0:s.set_bone_pose_rotation(spine,s.get_bone_rest(spine).basis.get_rotation_quaternion()*Quaternion(Vector3.RIGHT,.22 if crouch else .0))
static func ray(node:Node3D, from:Vector3, to:Vector3, exclude:Array=[], mask:int=7) -> Dictionary:
	var q=PhysicsRayQueryParameters3D.create(from,to,mask)
	q.exclude=exclude
	return node.get_world_3d().direct_space_state.intersect_ray(q)
static func find_meshes(node:Node) -> Array:
	var out=[]
	if node is MeshInstance3D:out.append(node)
	for c in node.get_children():out.append_array(find_meshes(c))
	return out
static func text3(parent:Node, text:String, pos:Vector3, size:float=.035) -> Label3D:
	var n=Label3D.new()
	n.text=text
	n.font_size=48
	n.pixel_size=size
	n.modulate=Color(.85,.88,.81)
	n.outline_size=7
	n.billboard=BaseMaterial3D.BILLBOARD_ENABLED
	n.no_depth_test=false
	parent.add_child(n)
	n.position=pos
	n.visibility_range_end=85
	return n
