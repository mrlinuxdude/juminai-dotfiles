#!/usr/bin/env python
# juminai @ github

import json
import os
import sys
import subprocess
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk

cache_file = os.path.expandvars("$XDG_CACHE_HOME/eww/apps.json")

DOCK_LIST = [
    "spotify",
    "discord",
    "foot",
    "kotatogram desktop",
    "code - oss",
    "thunar file manager",
    "brave",
    "transmission"
]


def installed_apps():
    app_info = Gio.AppInfo
    app_infos = app_info.get_all()

    app_list = []
    
    for app_info in app_infos:
        get_icon = app_info.get_icon()
        
        if get_icon:
            if get_icon.get_names():
                icon_name = get_icon.get_names()[0]
                icon_location = get_themed_icon(icon_name)
            else:
                None
        else:
            icon_location = None
        
        if app_info.should_show():
            app_dict = {
                "name": app_info.get_display_name(),
                "icon": icon_location,
                "description": app_info.get_description(),
                "desktop": app_info.get_id()
            }
            
            app_list.append(app_dict)
    return app_list


def get_themed_icon(icon_name):
    theme = Gtk.IconTheme.get_default()
    icon_info = theme.lookup_icon(icon_name, 128, 0)

    if icon_info is not None:
        return icon_info.get_filename()


def list_dock_apps():
    app_list = installed_apps()
    dock_apps_list = []

    for app in app_list:
        if app["name"].lower() in DOCK_LIST:
            dock_apps_list.append(app)
    return dock_apps_list


def get_cache():
    if os.path.exists(cache_file):
        with open(cache_file, "r") as file:
            return json.load(file)
    else:
        full_list = {
            "apps": installed_apps(), 
            "dock_apps": list_dock_apps()
        }
        
        with open(cache_file, "w") as file:
            json.dump(full_list, file, indent=2)
        return full_list


def filter_entries(entries, query):
    filtered_data = [
        entry for entry in entries["apps"]
        if query.lower() in entry["name"].lower()
        or (entry["description"] and query.lower() in entry["description"].lower())
    ]
    return filtered_data


def update_eww(entries):
    subprocess.run(["eww", "update", "apps={}".format(json.dumps(entries))])


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--query":
        query = sys.argv[2]
    else:
        query = None

    entries = get_cache()
    
    if query is not None:
        update_eww({
            "apps":filter_entries(entries, query), 
            "dock_apps": entries["dock_apps"]
        })
    else:
        update_eww(entries)