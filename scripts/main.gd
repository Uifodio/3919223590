extends Control

# Professional color scheme
const COLORS = {
	"dark_bg": Color(0.12, 0.12, 0.14),
	"darker_bg": Color(0.08, 0.08, 0.10),
	"panel_bg": Color(0.16, 0.16, 0.18),
	"accent": Color(0.00, 0.47, 0.84),
	"accent_hover": Color(0.00, 0.55, 0.95),
	"success": Color(0.13, 0.59, 0.13),
	"warning": Color(0.85, 0.65, 0.13),
	"error": Color(0.80, 0.20, 0.20),
	"text_primary": Color(0.90, 0.90, 0.90),
	"text_secondary": Color(0.70, 0.70, 0.70),
	"text_muted": Color(0.50, 0.50, 0.50),
	"border": Color(0.25, 0.25, 0.27),
	"selection": Color(0.26, 0.47, 0.78),
	"editor_bg": Color(0.10, 0.10, 0.12),
	"editor_line": Color(0.15, 0.15, 0.17)
}

# UI References
@onready var toolbar = $MainLayout/Toolbar
@onready var address_bar = $MainLayout/AddressBar
@onready var file_list = $MainLayout/ContentArea/FileList
@onready var editor_area = $MainLayout/ContentArea/EditorArea
@onready var status_bar = $MainLayout/StatusBar

# Navigation
var current_path: String = ""
var history: Array[String] = []
var history_index: int = -1
var clipboard: Array[String] = []

# File operations
var selected_files: Array[String] = []
var current_editor_file: String = ""

func _ready():
	# Set up the UI
	setup_ui()
	
	# Initialize with user's home directory
	current_path = OS.get_user_data_dir()
	if current_path.is_empty():
		current_path = "C:/"
	
	# Load initial directory
	load_directory(current_path)
	
	# Set up signals
	setup_signals()

func setup_ui():
	# Set background color
	var style_box = StyleBoxFlat.new()
	style_box.bg_color = COLORS.dark_bg
	add_theme_stylebox_override("panel", style_box)
	
	# Apply professional styling to all UI elements
	apply_professional_styling()

func apply_professional_styling():
	# Apply dark theme to all buttons
	var button_style = StyleBoxFlat.new()
	button_style.bg_color = COLORS.accent
	button_style.corner_radius_top_left = 4
	button_style.corner_radius_top_right = 4
	button_style.corner_radius_bottom_left = 4
	button_style.corner_radius_bottom_right = 4
	
	# Apply to all buttons in toolbar
	for child in toolbar.get_children():
		if child is Button:
			child.add_theme_stylebox_override("normal", button_style)
			child.add_theme_color_override("font_color", COLORS.text_primary)

func setup_signals():
	# Connect toolbar buttons
	toolbar.get_node("BackButton").pressed.connect(go_back)
	toolbar.get_node("ForwardButton").pressed.connect(go_forward)
	toolbar.get_node("UpButton").pressed.connect(go_up)
	toolbar.get_node("NewFolderButton").pressed.connect(create_new_folder)
	toolbar.get_node("NewFileButton").pressed.connect(create_new_file)
	toolbar.get_node("CopyButton").pressed.connect(copy_selected_files)
	toolbar.get_node("DeleteButton").pressed.connect(delete_selected_files)
	
	# Connect address bar
	address_bar.get_node("GoButton").pressed.connect(navigate_to_path)
	address_bar.get_node("RefreshButton").pressed.connect(refresh_current_directory)
	
	# Connect file list
	file_list.item_selected.connect(on_file_selected)
	file_list.item_activated.connect(on_file_activated)
	
	# Connect editor buttons
	editor_area.get_node("EditorToolbar/SaveButton").pressed.connect(_on_save_button_pressed)
	editor_area.get_node("EditorToolbar/CloseEditorButton").pressed.connect(_on_close_editor_button_pressed)

func load_directory(path: String):
	if not DirAccess.dir_exists_absolute(path):
		show_error("Directory does not exist: " + path)
		return
	
	current_path = path
	update_address_bar()
	update_file_list()
	update_status("📁 Loaded directory: " + path)

func update_address_bar():
	address_bar.get_node("PathInput").text = current_path

func update_file_list():
	file_list.clear()
	
	# Add parent directory option
	if current_path != current_path.get_base_dir():
		file_list.add_item("📂 ..", null, false)
	
	# Get directory contents
	var dir = DirAccess.open(current_path)
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		
		var folders = []
		var files = []
		
		while file_name != "":
			if not file_name.begins_with("."):
				var full_path = current_path.path_join(file_name)
				if dir.current_is_dir():
					folders.append(file_name)
				else:
					files.append(file_name)
			file_name = dir.get_next()
		
		# Sort and add folders first
		folders.sort()
		for folder in folders:
			file_list.add_item("📁 " + folder, null, false)
		
		# Then add files
		files.sort()
		for file in files:
			file_list.add_item("📄 " + file, null, false)

func update_status(message: String):
	status_bar.get_node("StatusLabel").text = message

func on_file_selected(index: int):
	var item_text = file_list.get_item_text(index)
	var item_name = item_text.substr(2)  # Remove emoji
	
	if item_name == "..":
		selected_files.clear()
	else:
		selected_files = [current_path.path_join(item_name)]
	
	update_status("Selected: " + str(selected_files.size()) + " items")

func on_file_activated(index: int):
	var item_text = file_list.get_item_text(index)
	var item_name = item_text.substr(2)  # Remove emoji
	
	if item_name == "..":
		go_up()
	else:
		var full_path = current_path.path_join(item_name)
		if DirAccess.dir_exists_absolute(full_path):
			load_directory(full_path)
		else:
			open_file(full_path)

func open_file(file_path: String):
	# Check if it's a text file
	var text_extensions = [".txt", ".py", ".js", ".html", ".css", ".json", ".xml", ".md", ".c", ".cpp", ".h", ".java", ".cs", ".php", ".rb", ".pl", ".sh", ".bat", ".ps1", ".sql", ".log", ".ini", ".cfg", ".conf"]
	var ext = file_path.get_extension().to_lower()
	
	if ext in text_extensions or is_text_file(file_path):
		open_in_editor(file_path)
	else:
		# Try to open with default application
		OS.shell_open(file_path)
		update_status("🚀 Opened with default app: " + file_path.get_file())

func is_text_file(file_path: String) -> bool:
	var file = FileAccess.open(file_path, FileAccess.READ)
	if file:
		var content = file.get_as_text()
		file.close()
		return content.is_valid_utf8()
	return false

func open_in_editor(file_path: String):
	current_editor_file = file_path
	
	# Show editor area
	editor_area.visible = true
	editor_area.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	file_list.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	
	# Load file content
	var file = FileAccess.open(file_path, FileAccess.READ)
	if file:
		var content = file.get_as_text()
		file.close()
		
		editor_area.get_node("TextEdit").text = content
		editor_area.get_node("FileLabel").text = "📝 " + file_path.get_file()
		
		update_status("📝 Opened in editor: " + file_path.get_file())

func go_back():
	if history_index > 0:
		history_index -= 1
		load_directory(history[history_index])

func go_forward():
	if history_index < history.size() - 1:
		history_index += 1
		load_directory(history[history_index])

func go_up():
	var parent = current_path.get_base_dir()
	if parent != current_path:
		load_directory(parent)

func navigate_to_path():
	var path = address_bar.get_node("PathInput").text.strip_edges()
	if DirAccess.dir_exists_absolute(path):
		load_directory(path)
	else:
		show_error("Path does not exist: " + path)

func refresh_current_directory():
	load_directory(current_path)

func create_new_folder():
	var dialog = AcceptDialog.new()
	dialog.title = "New Folder"
	dialog.dialog_text = "Enter folder name:"
	
	var input = LineEdit.new()
	input.placeholder_text = "Folder name"
	dialog.add_child(input)
	
	dialog.confirmed.connect(func():
		var folder_name = input.text.strip_edges()
		if folder_name:
			var folder_path = current_path.path_join(folder_name)
			var dir = DirAccess.open(current_path)
			if dir:
				var error = dir.make_dir(folder_name)
				if error == OK:
					refresh_current_directory()
					update_status("✅ Created folder: " + folder_name)
				else:
					show_error("Error creating folder: " + folder_name)
		dialog.queue_free()
	)
	
	add_child(dialog)
	dialog.popup_centered()

func create_new_file():
	var dialog = AcceptDialog.new()
	dialog.title = "New File"
	dialog.dialog_text = "Enter file name:"
	
	var input = LineEdit.new()
	input.placeholder_text = "File name"
	dialog.add_child(input)
	
	dialog.confirmed.connect(func():
		var file_name = input.text.strip_edges()
		if file_name:
			var file_path = current_path.path_join(file_name)
			var file = FileAccess.open(file_path, FileAccess.WRITE)
			if file:
				file.close()
				refresh_current_directory()
				update_status("✅ Created file: " + file_name)
			else:
				show_error("Error creating file: " + file_name)
		dialog.queue_free()
	)
	
	add_child(dialog)
	dialog.popup_centered()

func copy_selected_files():
	if selected_files.size() > 0:
		clipboard = selected_files.duplicate()
		update_status("📋 Copied " + str(clipboard.size()) + " items to clipboard")
	else:
		update_status("⚠️ No files selected")

func delete_selected_files():
	if selected_files.size() == 0:
		update_status("⚠️ No files selected")
		return
	
	var dialog = ConfirmationDialog.new()
	dialog.title = "Confirm Delete"
	dialog.dialog_text = "Are you sure you want to delete " + str(selected_files.size()) + " items?"
	
	dialog.confirmed.connect(func():
		for file_path in selected_files:
			var dir = DirAccess.open(current_path)
			if dir:
				if DirAccess.dir_exists_absolute(file_path):
					dir.remove(file_path)
				else:
					dir.remove(file_path.get_file())
		
		refresh_current_directory()
		update_status("🗑️ Deleted " + str(selected_files.size()) + " items")
		selected_files.clear()
		dialog.queue_free()
	)
	
	dialog.canceled.connect(func():
		dialog.queue_free()
	)
	
	add_child(dialog)
	dialog.popup_centered()

func show_error(message: String):
	var dialog = AcceptDialog.new()
	dialog.title = "Error"
	dialog.dialog_text = message
	add_child(dialog)
	dialog.popup_centered()

func _on_save_button_pressed():
	if current_editor_file:
		var content = editor_area.get_node("TextEdit").text
		var file = FileAccess.open(current_editor_file, FileAccess.WRITE)
		if file:
			file.store_string(content)
			file.close()
			update_status("💾 Saved: " + current_editor_file.get_file())

func _on_close_editor_button_pressed():
	editor_area.visible = false
	file_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	current_editor_file = ""
	update_status("Editor closed")