extends SceneTree

const MARGIN := 18.0
const SIZE := Vector2i(640, 720)

func _initialize() -> void:
	run.call_deferred()

func camera() -> Camera3D:
	var viewport := SubViewport.new()
	viewport.size = SIZE
	root.add_child(viewport)
	var cam := Camera3D.new()
	cam.keep_aspect = Camera3D.KEEP_HEIGHT
	cam.fov = 90
	cam.near = 0.1
	cam.far = 100
	viewport.add_child(cam)
	cam.make_current()
	return cam

func arrow(cam: Camera3D, p: Vector3) -> Variant:
	var local := cam.to_local(p) # for this unit-scale camera, forward is -Z
	var c := Vector2(SIZE) * 0.5
	var half := c - Vector2(MARGIN, MARGIN)
	var dir := Vector2(local.x, -local.y) * c.y # square pixels and 90-deg vertical FOV
	if dir.length() < 1e-6:
		return null
	var tx := INF if absf(dir.x) < 1e-6 else half.x / absf(dir.x)
	var ty := INF if absf(dir.y) < 1e-6 else half.y / absf(dir.y)
	return c + dir * minf(tx, ty)

func fmt(p: Vector2) -> String:
	return "(%.3f,%.3f)" % [p.x,p.y]

func run() -> void:
	var left := camera()
	var right := camera()
	var offset := Vector2(640,0)
	var a := Vector3(1,0.5,-5)
	var b := Vector3(1,0.5,5)
	var c := Vector3(1,0.5,-0.05)
	var d := Vector3(0,0,5)
	print("kind behind_flag local_projection edge_anchor_on_right")
	for row in [["front",a],["behind",b],["before_near",c],["rear_axis",d]]:
		var p: Vector3 = row[1]
		var proj := right.unproject_position(p)
		var edge = arrow(right,p)
		var s := "none" if edge==null else fmt(edge+offset)
		print("%s %s %s %s" % [row[0],right.is_position_behind(p),fmt(proj),s])
	var r: Vector2 = arrow(right,b)
	var l: Vector2 = arrow(left,b)
	var back_wrong := right.unproject_position(b)+offset
	var front := right.unproject_position(a)+offset
	print("front_screen=%s back_naive_screen=%s fixed_left=%s fixed_right=%s" % [fmt(front),fmt(back_wrong),fmt(l),fmt(r+offset)])
	var ok := front.is_equal_approx(Vector2(1032,324)) and back_wrong.is_equal_approx(Vector2(888,396)) and r.is_equal_approx(Vector2(622,209)) and l.is_equal_approx(r)
	ok = ok and right.is_position_behind(b) and right.is_position_behind(c) and not right.is_position_behind(a) and arrow(right,d)==null
	quit(0 if ok else 1)
