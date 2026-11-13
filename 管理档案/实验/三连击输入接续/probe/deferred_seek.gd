extends SceneTree
func _initialize():
    call_deferred("run")
func run():
    for immediate in [false, true]:
        for update_only in [false, true]:
            var target = Node.new()
            target.set_script(load("res://target.gd"))
            root.add_child(target)
            var p = AnimationPlayer.new()
            target.add_child(p)
            p.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
            p.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE
            p.speed_scale = 1.0
            var a = Animation.new()
            a.length = 1.0
            var idx = a.add_track(Animation.TYPE_METHOD)
            a.track_set_path(idx, NodePath("."))
            for t in [0.2, 0.4, 0.6]:
                a.track_insert_key(idx, t, {"method":"marker","args":[str(t)]})
            var lib = AnimationLibrary.new()
            lib.add_animation("hit", a)
            p.add_animation_library("", lib)
            p.play("hit")
            p.advance(0)
            var setup = target.hits.duplicate()
            p.seek(0.5, immediate, update_only)
            var after_seek = target.hits.duplicate()
            var seek_position = p.current_animation_position
            p.advance(0.15)
            print(JSON.stringify({"update":immediate,"update_only":update_only,"setup":setup,"after_seek":after_seek,"seek_position":seek_position,"after_advance":target.hits,"final_position":p.current_animation_position}))
            target.free()
    quit()
