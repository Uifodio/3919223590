#!/usr/bin/env python3
import os
import sys
import json
import time
from pathlib import Path

import dearpygui.dearpygui as dpg

APP_NAME = "Aegis Editor"
STATE = {
    "tabs": {},        # tab_id -> {path, dirty}
    "current_tab": None,
    "search": {"text": "", "replace": ""},
    "always_on_top": False,
    "fullscreen": False,
}

# -------------- Helpers --------------

def set_status(text: str) -> None:
    if dpg.does_item_exist("status_text"):
        dpg.set_value("status_text", text)


def get_editor_for_tab(tab_id: str):
    editor_id = f"editor::{tab_id}"
    return editor_id if dpg.does_item_exist(editor_id) else None


def new_tab(title: str = "Untitled", path: str | None = None, content: str = "") -> str:
    tab_id = f"tab::{int(time.time() * 1000)}"
    with dpg.tab(label=title, parent="tabbar", tag=tab_id, closable=True):
        editor_id = f"editor::{tab_id}"
        dpg.add_input_text(tag=editor_id, default_value=content, multiline=True, tab_input=True,
                           callback=lambda s,a,u=tab_id: mark_dirty(u),
                           width=-1, height=-1)
    STATE["tabs"][tab_id] = {"path": path, "dirty": False}
    STATE["current_tab"] = tab_id
    dpg.configure_item("tabbar", selected=tab_id)
    update_title()
    return tab_id


def mark_dirty(tab_id: str):
    t = STATE["tabs"].get(tab_id)
    if t and not t["dirty"]:
        t["dirty"] = True
        label = dpg.get_item_label(tab_id)
        if not label.endswith(" *"):
            dpg.configure_item(tab_id, label=f"{label} *")
        update_title()


def update_title():
    tab_id = STATE.get("current_tab")
    if not tab_id:
        dpg.set_viewport_title(APP_NAME)
        return
    t = STATE["tabs"][tab_id]
    base = os.path.basename(t["path"]) if t["path"] else dpg.get_item_label(tab_id)
    if t["dirty"]:
        base += " *"
    dpg.set_viewport_title(f"{APP_NAME} - {base}")


def open_file(paths: list[str]):
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            new_tab(os.path.basename(p), p, content)
            set_status(f"Opened: {p}")
        except Exception as e:
            set_status(f"Open failed: {p}: {e}")


def save_current(save_as: bool = False):
    tab_id = STATE.get("current_tab")
    if not tab_id:
        return
    t = STATE["tabs"][tab_id]
    editor_id = get_editor_for_tab(tab_id)
    text = dpg.get_value(editor_id)
    path = t["path"]
    if save_as or not path:
        # invoke save dialog
        def _save(sender, app_data):
            if app_data and "file_path_name" in app_data:
                _do_save(tab_id, editor_id, app_data["file_path_name"], text)
        dpg.show_item("file_save_dialog")
        dpg.set_value("save_default_name", os.path.basename(path) if path else "Untitled.txt")
        dpg.set_item_user_data("file_save_dialog", {"tab_id": tab_id, "editor_id": editor_id, "text": text})
        return
    _do_save(tab_id, editor_id, path, text)


def _do_save(tab_id: str, editor_id, path: str, text: str):
    try:
        with open(path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(text)
        STATE["tabs"][tab_id]["path"] = path
        STATE["tabs"][tab_id]["dirty"] = False
        dpg.configure_item(tab_id, label=os.path.basename(path))
        set_status(f"Saved: {path}")
        update_title()
    except Exception as e:
        set_status(f"Save failed: {e}")


def on_tab_changed(sender, app_data):
    STATE["current_tab"] = app_data
    update_title()


def on_tab_closed(sender, app_data):
    tab_id = app_data
    t = STATE["tabs"].get(tab_id)
    if t and t["dirty"] and t.get("path"):
        set_status("Tab closed with unsaved changes")
    STATE["tabs"].pop(tab_id, None)
    if STATE["current_tab"] == tab_id:
        STATE["current_tab"] = None
        update_title()


def find_next(reverse: bool = False):
    tab_id = STATE.get("current_tab")
    if not tab_id:
        return
    editor_id = get_editor_for_tab(tab_id)
    text = dpg.get_value(editor_id)
    needle = STATE["search"]["text"]
    if not needle:
        return
    cursor = dpg.get_item_state(editor_id)["cursor_pos"] or 0
    if reverse:
        idx = text.rfind(needle, 0, cursor)
    else:
        idx = text.find(needle, cursor + 1)
    if idx == -1:
        # wrap
        idx = text.find(needle) if not reverse else text.rfind(needle)
    if idx != -1:
        # Dear PyGui input_text lacks native selection; set cursor near match
        dpg.set_item_state(editor_id, cursor_pos=idx)
        set_status(f"Found at {idx}")
    else:
        set_status("Not found")


def replace_one():
    tab_id = STATE.get("current_tab")
    if not tab_id:
        return
    editor_id = get_editor_for_tab(tab_id)
    text = dpg.get_value(editor_id)
    needle = STATE["search"]["text"]
    repl = STATE["search"]["replace"]
    cursor = dpg.get_item_state(editor_id)["cursor_pos"] or 0
    idx = text.find(needle, cursor)
    if idx == -1:
        idx = text.find(needle)
    if idx != -1 and needle:
        new_text = text[:idx] + repl + text[idx+len(needle):]
        dpg.set_value(editor_id, new_text)
        mark_dirty(tab_id)
        dpg.set_item_state(editor_id, cursor_pos=idx + len(repl))
        set_status("Replaced")


def replace_all():
    tab_id = STATE.get("current_tab")
    if not tab_id:
        return
    editor_id = get_editor_for_tab(tab_id)
    text = dpg.get_value(editor_id)
    needle = STATE["search"]["text"]
    repl = STATE["search"]["replace"]
    if needle:
        new_text = text.replace(needle, repl)
        if new_text != text:
            dpg.set_value(editor_id, new_text)
            mark_dirty(tab_id)
            set_status("Replaced all")


def set_always_on_top(v: bool):
    STATE["always_on_top"] = v
    dpg.set_viewport_always_top(v)


def toggle_fullscreen():
    STATE["fullscreen"] = not STATE["fullscreen"]
    dpg.toggle_viewport_fullscreen()


def on_drop(sender, app_data):
    paths = [p for p in app_data if os.path.isfile(p)]
    if paths:
        open_file(paths)

# -------------- UI --------------

def build_ui():
    with dpg.viewport_menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="New", shortcut="Ctrl+N", callback=lambda: new_tab())
            dpg.add_menu_item(label="Open...", shortcut="Ctrl+O", callback=lambda: dpg.show_item("file_open_dialog"))
            dpg.add_menu_item(label="Save", shortcut="Ctrl+S", callback=lambda: save_current(False))
            dpg.add_menu_item(label="Save As...", shortcut="Ctrl+Shift+S", callback=lambda: save_current(True))
            dpg.add_separator()
            dpg.add_menu_item(label="Exit", callback=lambda: dpg.stop_dearpygui())
        with dpg.menu(label="Edit"):
            dpg.add_menu_item(label="Undo", shortcut="Ctrl+Z", callback=lambda: None)
            dpg.add_menu_item(label="Redo", shortcut="Ctrl+Y", callback=lambda: None)
        with dpg.menu(label="Search"):
            dpg.add_menu_item(label="Find", shortcut="Ctrl+F", callback=lambda: dpg.show_item("search_panel"))
            dpg.add_menu_item(label="Replace", shortcut="Ctrl+H", callback=lambda: dpg.show_item("search_panel"))
            dpg.add_menu_item(label="Find Next", shortcut="F3", callback=lambda: find_next(False))
            dpg.add_menu_item(label="Find Prev", shortcut="Shift+F3", callback=lambda: find_next(True))
        with dpg.menu(label="View"):
            dpg.add_menu_item(label="Fullscreen", shortcut="F11", callback=toggle_fullscreen)
            dpg.add_menu_item(label="Always on Top", callback=lambda s,a: set_always_on_top(True))
            dpg.add_menu_item(label="Not on Top", callback=lambda s,a: set_always_on_top(False))

    with dpg.window(label="Search", tag="search_panel", pos=(10, 50), width=450, height=120, show=False, no_resize=False, no_collapse=True):
        dpg.add_input_text(label="Find", tag="find_text", callback=lambda s,a: STATE["search"].update(text=a))
        dpg.add_input_text(label="Replace", tag="replace_text", callback=lambda s,a: STATE["search"].update(replace=a))
        with dpg.group(horizontal=True):
            dpg.add_button(label="Find Next", callback=lambda: find_next(False))
            dpg.add_button(label="Find Prev", callback=lambda: find_next(True))
            dpg.add_button(label="Replace", callback=replace_one)
            dpg.add_button(label="Replace All", callback=replace_all)
            dpg.add_button(label="Close", callback=lambda: dpg.hide_item("search_panel"))

    with dpg.window(label="Aegis Editor", tag="main_window", width=1200, height=800):
        with dpg.tab_bar(tag="tabbar"):
            pass
        dpg.add_spacer(height=6)
        with dpg.group(horizontal=True):
            dpg.add_text("Ready", tag="status_text")

    # File dialogs
    with dpg.file_dialog(tag="file_open_dialog", directory_selector=False, show=False, callback=lambda s,a: open_file(a.get("selections", {}).values())):
        dpg.add_file_extension(".*", color=(200,200,200,255))
    with dpg.file_dialog(tag="file_save_dialog", directory_selector=False, show=False, callback=lambda s,a: _do_save(STATE["current_tab"], get_editor_for_tab(STATE["current_tab"]), a.get("file_path_name", ""), dpg.get_value(get_editor_for_tab(STATE["current_tab"])) )):
        dpg.add_file_extension(".*", color=(200,200,200,255))
        dpg.add_input_text(tag="save_default_name")

# -------------- Main --------------

def main():
    dpg.create_context()
    dpg.create_viewport(title=APP_NAME, width=1200, height=800)

    with dpg.theme() as dark_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30,30,30,255))
            dpg.add_theme_color(dpg.mvThemeCol_Text, (220,220,220,255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (45,45,45,255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, (50,50,50,255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (60,60,60,255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (70,70,70,255))
    dpg.bind_theme(dark_theme)

    build_ui()
    new_tab()

    dpg.setup_dearpygui()

    # Drag & drop files onto viewport
    dpg.enable_docking(dock_space=True)
    dpg.set_viewport_vsync(True)
    dpg.set_viewport_large_icon("")
    dpg.set_viewport_small_icon("")
    dpg.set_viewport_title(APP_NAME)
    dpg.set_viewport_pos((100, 60))

    dpg.set_file_drop_callback(on_drop)

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()