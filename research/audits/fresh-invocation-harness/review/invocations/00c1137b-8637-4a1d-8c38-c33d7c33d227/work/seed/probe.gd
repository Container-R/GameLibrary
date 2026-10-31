extends Node
func _ready() -> void:
    var config := ConfigFile.new()
    var error: int = config.load("res://asset.svg.import")
    if error != OK:
        push_error("Cannot read import metadata")
        get_tree().quit(2)
        return
    var direct: Texture2D = ResourceLoader.load("res://asset.svg")
    var scene_texture: Texture2D = $Icon.texture
    if direct == null or scene_texture == null:
        push_error("Missing actual imported texture")
        get_tree().quit(2)
        return
    var uid_text: String = config.get_value("remap", "uid")
    var uid: int = ResourceUID.text_to_id(uid_text)
    var uid_known: bool = ResourceUID.has_id(uid)
    print("RESULT_JSON=" + JSON.stringify({"version": Engine.get_version_info(),
        "display_server": DisplayServer.get_name(), "scale": config.get_value("params", "svg/scale"),
        "uid": uid_text, "uid_known": uid_known,
        "uid_path": ResourceUID.get_id_path(uid) if uid_known else "",
        "direct_type": direct.get_class(), "scene_type": scene_texture.get_class(),
        "direct_path": direct.resource_path, "scene_path": scene_texture.resource_path,
        "direct_size": [direct.get_width(), direct.get_height()],
        "scene_size": [scene_texture.get_width(), scene_texture.get_height()],
        "same_resource": direct == scene_texture,
        "scene_dependencies": ResourceLoader.get_dependencies("res://main.tscn")}))
    get_tree().quit(0)
