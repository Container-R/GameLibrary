extends SceneTree
func _initialize():
    call_deferred("run")
func run():
    for mode in ["advance", "seek_no_update", "seek_update", "seek_update_only"]:
        var target = Node.new()
        target.set_script(load("res://target.gd"))
        root.add_child(target)
        var p = AnimationPlayer.new()
        target.add_child(p)
        p.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
        p.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE
        var a = Animation.new()
        a.length = 1.0
        var idx = a.add_track(Animation.TYPE_METHOD)
        a.track_set_path(idx, NodePath("."))
        a.track_insert_key(idx, 0.1, {"method":"marker","args":["early"]})
        a.track_insert_key(idx, 0.2, {"method":"marker","args":["late"]})
        var lib = AnimationLibrary.new()
        lib.add_animation("hit", a)
        p.add_animation_library("", lib)
        p.play("hit")
        p.advance(0)
        var setup = target.hits.duplicate()
        if mode == "advance":
            p.advance(0.3)
        else:
            p.seek(0.3, mode != "seek_no_update", mode == "seek_update_only")
        print(JSON.stringify({"case":mode,"setup":setup,"native_markers":target.hits,"application_window_accept":0.3 >= 0.2 and 0.3 < 0.4,"time":p.current_animation_position}))
        target.free()
    quit()
