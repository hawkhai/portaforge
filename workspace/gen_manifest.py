#encoding=utf8
import hashlib
import json
import os
import re
import time

from pythonx.pelib import getPeType


def _md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _format_time(path):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))


def _manifest_name(app):
    return os.path.basename(os.path.normpath(app))


def _entry_exe(app_dir, entry=""):
    if entry:
        name = entry if entry.lower().endswith(".exe") else entry + ".exe"
        path = os.path.join(app_dir, name)
        if not os.path.exists(path):
            raise AssertionError("entry exe not found: {}".format(path))
        return name

    exes = [name for name in os.listdir(app_dir) if name.lower().endswith(".exe")]
    if len(exes) != 1:
        raise AssertionError(
            "entry exe is ambiguous, specify via --entry (found: {})".format(exes)
        )
    return exes[0]


def _keyname(relpath, used):
    parts = re.findall("[0-9a-zA-Z_]+", relpath)
    key = "_".join(parts).upper()
    while key in used:
        parts.append(str(len(used)))
        key = "_".join(parts).upper()
    used.add(key)
    return key


def update_manifest(app, entry=""):
    app_dir = os.path.abspath(app)
    if not os.path.isdir(app_dir):
        raise AssertionError("app directory not found: {}".format(app_dir))

    name = _manifest_name(app)
    current_json = os.path.abspath(os.path.join("backup", name + ".json"))
    current_rc = os.path.abspath(os.path.join("backup", name + ".rc"))

    entry_name = _entry_exe(app_dir, entry=entry)
    files = {}
    used_keys = set()
    for root, dirs, names in os.walk(app_dir):
        dirs.sort()
        names.sort()
        for filename in names:
            full = os.path.join(root, filename)
            rel = os.path.relpath(full, app_dir).replace("/", "\\").lower()
            key = _keyname(rel, used_keys)
            files[rel] = {
                "md5": _md5_file(full),
                "keyname": key,
                "runfile": os.path.join(name, rel),
                "fmtime": _format_time(full),
                "fsize": os.path.getsize(full),
                "petype": getPeType(full),
            }

    manifest = {
        "zloader": os.path.join(name, entry_name.lower()),
        "files": files,
        "version": "nsis",
        "sysversion": "",
        "genrestime": round(time.time()),
        "petype": getPeType(os.path.join(app_dir, entry_name)),
    }

    current_dir = os.path.dirname(current_json)
    if current_dir and not os.path.isdir(current_dir):
        os.makedirs(current_dir)
    with open(current_json, "wb") as fp:
        fp.write(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8"))

    rc_lines = ['ZLOADER_ROOT_JSON RCDATA "{}"'.format(
        os.path.join("backup", name + ".json").replace("\\", "\\\\"))]
    for rel in sorted(files.keys()):
        rc_lines.append('{} RCDATA "{}"'.format(
            files[rel]["keyname"], os.path.join(app, rel).replace("\\", "\\\\")))
    with open(current_rc, "wb") as fp:
        fp.write(("\r\n".join(rc_lines) + "\r\n").encode("utf-8"))

    return current_json, current_rc
