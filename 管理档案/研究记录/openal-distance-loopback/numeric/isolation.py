"""Five selected writable runtime locations; not a sandbox or process launcher."""
from pathlib import Path

KEYS = ('HOME', 'XDG_CACHE_HOME', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'TMPDIR')


def _root(owned_root):
    root = Path(owned_root)
    if not root.is_absolute() or '..' in root.parts:
        raise ValueError('owned root must be absolute without parent traversal')
    if root == Path(root.anchor):
        raise ValueError('filesystem anchor cannot be an invocation root')
    # Inspect components before resolve: resolving first would hide symlinks.
    for path in (root, *root.parents):
        if path.is_symlink():
            raise ValueError('symlink root component rejected')
    if not root.is_dir():
        raise ValueError('owned root must already be a directory')
    return root


def prepare_environment(base_env, owned_root):
    """Return (copied env, five-key receipt map). Caller owns directory cleanup.

    A caller-created, exclusively owned fresh root is a precondition, not an
    ownership/security fact established by this function. Failure may leave
    partially created children. No whole-environment logging is performed.
    """
    root = _root(owned_root)
    env = dict(base_env)
    paths = {key: root / key for key in KEYS}
    for path in paths.values():
        if path.exists() or path.is_symlink():
            raise ValueError('reserved runtime path already exists')
    for path in paths.values():
        path.mkdir(exist_ok=False)
    manifest = {key: str(path) for key, path in paths.items()}
    env.update(manifest)
    validate_environment(env, root)
    return env, dict(manifest)


def validate_environment(env, owned_root):
    """Check this instant's exact paths; caller can still mutate them afterward."""
    root = _root(owned_root)
    for key in KEYS:
        path = root / key
        if env.get(key) != str(path):
            raise ValueError('missing or redirected runtime key: ' + key)
        if path.is_symlink() or not path.is_dir():
            raise ValueError('runtime directory missing or symlink: ' + key)
    return {key: str(root / key) for key in KEYS}
