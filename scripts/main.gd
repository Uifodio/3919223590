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
	"editor_line": Color(0.15, 0.15, 0.17),
	"tree_bg": Color(0.14, 0.14, 0.16),
	"tree_selection": Color(0.20, 0.40, 0.70),
	"progress_bg": Color(0.20, 0.20, 0.22),
	"progress_fill": Color(0.00, 0.60, 1.00)
}

# File type icons
const FILE_ICONS = {
	"folder": "📁",
	"file": "📄",
	"image": "🖼️",
	"video": "🎥",
	"audio": "🎵",
	"archive": "📦",
	"code": "💻",
	"document": "📋",
	"spreadsheet": "📊",
	"presentation": "📽️",
	"pdf": "📕",
	"unity": "🎮"
}

# UI References
@onready var toolbar = $MainLayout/Toolbar
@onready var address_bar = $MainLayout/AddressBar
@onready var file_tree = $MainLayout/ContentArea/FileTree
@onready var file_list = $MainLayout/ContentArea/FileList
@onready var editor_area = $MainLayout/ContentArea/EditorArea
@onready var status_bar = $MainLayout/StatusBar
@onready var search_bar = $MainLayout/SearchBar
@onready var progress_bar = $MainLayout/ProgressBar

# Navigation
var current_path: String = ""
var history: Array[String] = []
var history_index: int = -1
var clipboard: Array[String] = []
var recent_folders: Array[String] = []

# File operations
var selected_files: Array[String] = []
var current_editor_file: String = ""
var show_hidden_files: bool = false
var multi_select_mode: bool = false

# Search
var search_query: String = ""
var search_results: Array[String] = []

# Progress tracking
var current_operation: String = ""
var operation_progress: float = 0.0
var operation_total: int = 0
var operation_current: int = 0

# Settings
var settings: Dictionary = {
	"theme": "dark",
	"font_size": 12,
	"show_hidden": false,
	"auto_save": true,
	"backup_on_edit": true,
	"line_numbers": true,
	"syntax_highlighting": true
}

func _ready():
	# Set up the UI
	setup_ui()
	
	# Initialize with user's home directory
	current_path = OS.get_user_data_dir()
	if current_path.is_empty():
		current_path = "C:/"
	
	# Set up signals
	setup_signals()
	
	# Build file tree
	build_file_tree()
	
	# Load initial directory
	load_directory(current_path)
	
	# Set up Unity integration
	setup_unity_integration()

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
	toolbar.get_node("CutButton").pressed.connect(cut_selected_files)
	toolbar.get_node("PasteButton").pressed.connect(paste_files)
	toolbar.get_node("DeleteButton").pressed.connect(delete_selected_files)
	toolbar.get_node("RenameButton").pressed.connect(rename_selected_file)
	toolbar.get_node("DuplicateButton").pressed.connect(duplicate_selected_file)
	toolbar.get_node("NewWindowButton").pressed.connect(open_new_window)
	toolbar.get_node("SettingsButton").pressed.connect(open_settings)
	
	# Connect address bar
	address_bar.get_node("GoButton").pressed.connect(navigate_to_path)
	address_bar.get_node("RefreshButton").pressed.connect(refresh_current_directory)
	
	# Connect search bar
	search_bar.get_node("SearchButton").pressed.connect(perform_search)
	search_bar.get_node("ShowHiddenButton").pressed.connect(toggle_hidden_files)
	search_bar.get_node("SearchInput").text_changed.connect(on_search_text_changed)
	
	# Connect file tree
	file_tree.item_selected.connect(on_tree_item_selected)
	
	# Connect file list
	file_list.item_selected.connect(on_file_selected)
	file_list.item_activated.connect(on_file_activated)
	
	# Connect editor buttons
	editor_area.get_node("EditorToolbar/SaveButton").pressed.connect(_on_save_button_pressed)
	editor_area.get_node("EditorToolbar/CloseEditorButton").pressed.connect(_on_close_editor_button_pressed)
	
	# Connect keyboard shortcuts
	setup_keyboard_shortcuts()

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
	
	# Initialize arrays
	var folders = []
	var files = []
	
	# Get directory contents
	var dir = DirAccess.open(current_path)
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		
		while file_name != "":
			if not file_name.begins_with(".") or show_hidden_files:
				var full_path = current_path.path_join(file_name)
				if dir.current_is_dir():
					folders.append(file_name)
				else:
					files.append(file_name)
			file_name = dir.get_next()
		
		# Sort and add folders first
		folders.sort()
		for folder in folders:
			var icon = get_file_icon(current_path.path_join(folder))
			file_list.add_item(icon + " " + folder, null, false)
		
		# Then add files with proper icons
		files.sort()
		for file in files:
			var icon = get_file_icon(current_path.path_join(file))
			file_list.add_item(icon + " " + file, null, false)
	
	# Update status
	var total_items = folders.size() + files.size()
	update_status("📁 " + current_path + " (" + str(total_items) + " items)")

func update_status(message: String):
	status_bar.get_node("StatusLabel").text = message

func on_file_selected(index: int):
	var item_text = file_list.get_item_text(index)
	var item_name = item_text.substr(2)  # Remove emoji
	
	if item_name == "..":
		selected_files.clear()
	else:
		var full_path = current_path.path_join(item_name)
		
		# Handle multi-selection with Ctrl/Cmd key
		if Input.is_key_pressed(KEY_CTRL) or Input.is_key_pressed(KEY_META):
			if selected_files.has(full_path):
				selected_files.erase(full_path)
			else:
				selected_files.append(full_path)
		# Handle range selection with Shift key
		elif Input.is_key_pressed(KEY_SHIFT) and selected_files.size() > 0:
			var last_selected = selected_files[-1]
			var last_index = get_file_index_from_path(last_selected)
			var current_index = index
			
			# Clear selection and add range
			selected_files.clear()
			var start_index = min(last_index, current_index)
			var end_index = max(last_index, current_index)
			
			for i in range(start_index, end_index + 1):
				var path_item = file_list.get_item_text(i)
				var path_name = path_item.substr(2)  # Remove emoji
				if path_name != "..":
					selected_files.append(current_path.path_join(path_name))
		else:
			# Single selection
			selected_files = [full_path]
	
	update_selection_display()
	update_status("Selected: " + str(selected_files.size()) + " items")

func get_file_index_from_path(file_path: String) -> int:
	var file_name = file_path.get_file()
	for i in range(file_list.get_item_count()):
		var item_text = file_list.get_item_text(i)
		var item_name = item_text.substr(2)  # Remove emoji
		if item_name == file_name:
			return i
	return -1

func update_selection_display():
	# Update visual selection in file list
	for i in range(file_list.get_item_count()):
		var item_text = file_list.get_item_text(i)
		var item_name = item_text.substr(2)  # Remove emoji
		if item_name != "..":
			var full_path = current_path.path_join(item_name)
			if selected_files.has(full_path):
				file_list.select(i)
			else:
				file_list.deselect(i)

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
	var ext = file_path.get_extension().to_lower()
	
	# Check if it's a Unity asset
	if ext in ["unity", "prefab", "mat", "asset"]:
		handle_unity_asset(file_path)
		open_in_editor(file_path)
		return
	
	# Check if it's an image file
	var image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"]
	if ext in image_extensions:
		open_image_viewer(file_path)
		return
	
	# Check if it's a text/code file
	var text_extensions = [".txt", ".py", ".js", ".html", ".css", ".json", ".xml", ".md", ".c", ".cpp", ".h", ".java", ".cs", ".php", ".rb", ".pl", ".sh", ".bat", ".ps1", ".sql", ".log", ".ini", ".cfg", ".conf", ".yaml", ".yml", ".toml", ".lua", ".r", ".scala", ".kt", ".swift", ".go", ".rs", ".dart", ".ts", ".jsx", ".tsx", ".vue", ".svelte"]
	if ext in text_extensions or is_text_file(file_path):
		open_in_editor(file_path)
		return
	
	# Check if it's a ZIP archive
	if ext in ["zip", "rar", "7z", "tar", "gz"]:
		open_archive(file_path)
		return
	
	# Try to open with default application
	OS.shell_open(file_path)
	update_status("🚀 Opened with default app: " + file_path.get_file())

func open_image_viewer(file_path: String):
	# Simple image viewer - could be enhanced with a proper image viewer
	var dialog = AcceptDialog.new()
	dialog.title = "Image Viewer"
	dialog.dialog_text = "Image: " + file_path.get_file() + "\n\nImage viewer will be implemented here."
	dialog.dialog_autowrap = true
	add_child(dialog)
	dialog.popup_centered()

func open_archive(file_path: String):
	# Handle ZIP archives - could be enhanced to browse contents
	var dialog = AcceptDialog.new()
	dialog.title = "Archive Viewer"
	dialog.dialog_text = "Archive: " + file_path.get_file() + "\n\nArchive browser will be implemented here."
	dialog.dialog_autowrap = true
	add_child(dialog)
	dialog.popup_centered()

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
		
		var text_edit = editor_area.get_node("TextEdit")
		text_edit.text = content
		
		# Set up syntax highlighting
		setup_syntax_highlighting(file_path)
		
		# Update file label with path
		var file_label = editor_area.get_node("EditorToolbar/FileLabel")
		file_label.text = "📝 " + file_path.get_file() + " - " + file_path
		
		# Add to recent files
		add_to_recent_files(file_path)
		
		update_status("📝 Opened in editor: " + file_path.get_file())

func setup_syntax_highlighting(file_path: String):
	var text_edit = editor_area.get_node("TextEdit")
	var ext = file_path.get_extension().to_lower()
	
	# Basic syntax highlighting setup
	text_edit.syntax_highlighter = CodeHighlighter.new()
	
	# Set up different colors for different file types
	match ext:
		"py":
			setup_python_highlighting(text_edit)
		"js", "jsx":
			setup_javascript_highlighting(text_edit)
		"html":
			setup_html_highlighting(text_edit)
		"css":
			setup_css_highlighting(text_edit)
		"cs":
			setup_csharp_highlighting(text_edit)
		_:
			setup_generic_highlighting(text_edit)

func setup_python_highlighting(text_edit: TextEdit):
	var highlighter = text_edit.syntax_highlighter
	highlighter.add_color_region("#", "", Color(0.5, 0.5, 0.5), true)  # Comments
	highlighter.add_color_region('"', '"', Color(0.8, 0.8, 0.2))  # Strings
	highlighter.add_color_region("'", "'", Color(0.8, 0.8, 0.2))  # Strings

func setup_javascript_highlighting(text_edit: TextEdit):
	var highlighter = text_edit.syntax_highlighter
	highlighter.add_color_region("//", "", Color(0.5, 0.5, 0.5), true)  # Comments
	highlighter.add_color_region('"', '"', Color(0.8, 0.8, 0.2))  # Strings
	highlighter.add_color_region("'", "'", Color(0.8, 0.8, 0.2))  # Strings

func setup_html_highlighting(text_edit: TextEdit):
	var highlighter = text_edit.syntax_highlighter
	highlighter.add_color_region("<!--", "-->", Color(0.5, 0.5, 0.5), true)  # Comments
	highlighter.add_color_region('"', '"', Color(0.8, 0.8, 0.2))  # Strings

func setup_css_highlighting(text_edit: TextEdit):
	var highlighter = text_edit.syntax_highlighter
	highlighter.add_color_region("/*", "*/", Color(0.5, 0.5, 0.5), true)  # Comments
	highlighter.add_color_region('"', '"', Color(0.8, 0.8, 0.2))  # Strings

func setup_csharp_highlighting(text_edit: TextEdit):
	var highlighter = text_edit.syntax_highlighter
	highlighter.add_color_region("//", "", Color(0.5, 0.5, 0.5), true)  # Comments
	highlighter.add_color_region('"', '"', Color(0.8, 0.8, 0.2))  # Strings

func setup_generic_highlighting(text_edit: TextEdit):
	var highlighter = text_edit.syntax_highlighter
	highlighter.add_color_region('"', '"', Color(0.8, 0.8, 0.2))  # Strings

func add_to_recent_files(file_path: String):
	if not recent_folders.has(file_path):
		recent_folders.append(file_path)
		# Keep only last 10 files
		if recent_folders.size() > 10:
			recent_folders.pop_front()

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
		
		# Create backup if enabled
		if settings.backup_on_edit:
			create_backup(current_editor_file)
		
		# Save the file
		var file = FileAccess.open(current_editor_file, FileAccess.WRITE)
		if file:
			file.store_string(content)
			file.close()
			update_status("💾 Saved: " + current_editor_file.get_file())
		else:
			show_error("Error saving file: " + current_editor_file.get_file())

func create_backup(file_path: String):
	var backup_path = file_path + ".bak"
	var file = FileAccess.open(file_path, FileAccess.READ)
	if file:
		var content = file.get_as_text()
		file.close()
		
		var backup_file = FileAccess.open(backup_path, FileAccess.WRITE)
		if backup_file:
			backup_file.store_string(content)
			backup_file.close()
			update_status("💾 Backup created: " + file_path.get_file() + ".bak")

func _on_close_editor_button_pressed():
	editor_area.visible = false
	file_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	current_editor_file = ""
	update_status("Editor closed")

# ===== PROFESSIONAL FEATURES =====

func setup_keyboard_shortcuts():
	# Set up input map for keyboard shortcuts
	pass

func build_file_tree():
	file_tree.clear()
	var root = file_tree.create_item()
	root.set_text(0, "📁 Computer")
	root.set_icon(0, null)
	
	# Add drives
	var drives = get_available_drives()
	for drive in drives:
		var drive_item = file_tree.create_item(root)
		drive_item.set_text(0, "💾 " + drive)
		drive_item.set_icon(0, null)
		drive_item.set_metadata(0, drive)

func get_available_drives() -> Array[String]:
	var drives: Array[String] = []
	
	# Windows drives
	for i in range(65, 91):  # A-Z
		var drive = char(i) + ":\\"
		if DirAccess.dir_exists_absolute(drive):
			drives.append(drive)
	
	return drives

func on_tree_item_selected():
	var selected_item = file_tree.get_selected()
	if selected_item and selected_item.has_metadata(0):
		var path = selected_item.get_metadata(0)
		load_directory(path)

func toggle_hidden_files():
	show_hidden_files = !show_hidden_files
	update_file_list()
	update_status("Hidden files: " + ("Shown" if show_hidden_files else "Hidden"))

func on_search_text_changed(new_text: String):
	search_query = new_text
	if search_query.length() > 2:
		perform_search()
	elif search_query.is_empty():
		update_file_list()

func perform_search():
	if search_query.is_empty():
		return
	
	search_results.clear()
	search_in_directory(current_path, search_query)
	display_search_results()

func search_in_directory(dir_path: String, query: String):
	var dir = DirAccess.open(dir_path)
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		
		while file_name != "":
			if not file_name.begins_with(".") or show_hidden_files:
				var full_path = dir_path.path_join(file_name)
				
				# Search in filename
				if query.to_lower() in file_name.to_lower():
					search_results.append(full_path)
				
				# Search in file content (for text files)
				elif dir.current_is_dir():
					search_in_directory(full_path, query)
				else:
					search_in_file_content(full_path, query)
			
			file_name = dir.get_next()

func search_in_file_content(file_path: String, query: String):
	var text_extensions = [".txt", ".py", ".js", ".html", ".css", ".json", ".xml", ".md", ".c", ".cpp", ".h", ".java", ".cs", ".php", ".rb", ".pl", ".sh", ".bat", ".ps1", ".sql", ".log", ".ini", ".cfg", ".conf"]
	var ext = file_path.get_extension().to_lower()
	
	if ext in text_extensions:
		var file = FileAccess.open(file_path, FileAccess.READ)
		if file:
			var content = file.get_as_text()
			file.close()
			if query.to_lower() in content.to_lower():
				search_results.append(file_path)

func display_search_results():
	file_list.clear()
	
	if search_results.is_empty():
		file_list.add_item("No results found for: " + search_query, null, false)
	else:
		for result in search_results:
			var file_name = result.get_file()
			var icon = get_file_icon(result)
			file_list.add_item(icon + " " + file_name, null, false)

func get_file_icon(file_path: String) -> String:
	if DirAccess.dir_exists_absolute(file_path):
		return FILE_ICONS.folder
	
	var ext = file_path.get_extension().to_lower()
	
	match ext:
		"jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp":
			return FILE_ICONS.image
		"mp4", "avi", "mov", "wmv", "flv", "webm":
			return FILE_ICONS.video
		"mp3", "wav", "flac", "ogg", "aac":
			return FILE_ICONS.audio
		"zip", "rar", "7z", "tar", "gz":
			return FILE_ICONS.archive
		"py", "js", "html", "css", "json", "xml", "md", "c", "cpp", "h", "java", "cs", "php", "rb", "pl", "sh", "bat", "ps1", "sql":
			return FILE_ICONS.code
		"doc", "docx", "rtf":
			return FILE_ICONS.document
		"xls", "xlsx", "csv":
			return FILE_ICONS.spreadsheet
		"ppt", "pptx":
			return FILE_ICONS.presentation
		"pdf":
			return FILE_ICONS.pdf
		"unity", "prefab", "mat", "asset":
			return FILE_ICONS.unity
		_:
			return FILE_ICONS.file

func cut_selected_files():
	if selected_files.size() > 0:
		clipboard = selected_files.duplicate()
		clipboard.append("CUT")  # Mark as cut operation
		update_status("✂️ Cut " + str(selected_files.size()) + " items to clipboard")
	else:
		update_status("⚠️ No files selected")

func paste_files():
	if clipboard.is_empty():
		update_status("⚠️ Clipboard is empty")
		return
	
	var is_cut = clipboard.has("CUT")
	clipboard.erase("CUT")
	
	start_file_operation("Pasting files...", clipboard.size())
	
	for i in range(clipboard.size()):
		var source_path = clipboard[i]
		var file_name = source_path.get_file()
		var dest_path = current_path.path_join(file_name)
		
		# Handle duplicate names
		var counter = 1
		while FileAccess.file_exists(dest_path):
			var name_without_ext = file_name.get_basename()
			var ext = file_name.get_extension()
			dest_path = current_path.path_join(name_without_ext + " (" + str(counter) + ")." + ext)
			counter += 1
		
		# Copy file
		var dir = DirAccess.open(current_path)
		if dir:
			var error = dir.copy(source_path, dest_path)
			if error == OK and is_cut:
				# Delete original if it was a cut operation
				DirAccess.remove_absolute(source_path)
		
		update_operation_progress(i + 1)
	
	clipboard.clear()
	refresh_current_directory()
	update_status("✅ Pasted " + str(clipboard.size()) + " items")

func rename_selected_file():
	if selected_files.size() != 1:
		update_status("⚠️ Please select exactly one file to rename")
		return
	
	var old_path = selected_files[0]
	var old_name = old_path.get_file()
	
	var dialog = AcceptDialog.new()
	dialog.title = "Rename File"
	dialog.dialog_text = "Enter new name:"
	
	var input = LineEdit.new()
	input.text = old_name
	input.select_all()
	dialog.add_child(input)
	
	dialog.confirmed.connect(func():
		var new_name = input.text.strip_edges()
		if new_name and new_name != old_name:
			var new_path = current_path.path_join(new_name)
			var dir = DirAccess.open(current_path)
			if dir:
				var error = dir.rename(old_name, new_name)
				if error == OK:
					refresh_current_directory()
					update_status("✅ Renamed: " + old_name + " → " + new_name)
				else:
					show_error("Error renaming file: " + old_name)
		dialog.queue_free()
	)
	
	add_child(dialog)
	dialog.popup_centered()

func duplicate_selected_file():
	if selected_files.size() != 1:
		update_status("⚠️ Please select exactly one file to duplicate")
		return
	
	var source_path = selected_files[0]
	var file_name = source_path.get_file()
	var name_without_ext = file_name.get_basename()
	var ext = file_name.get_extension()
	
	# Find next available name
	var counter = 1
	var dest_path = current_path.path_join(name_without_ext + " - Copy." + ext)
	while FileAccess.file_exists(dest_path):
		dest_path = current_path.path_join(name_without_ext + " - Copy (" + str(counter) + ")." + ext)
		counter += 1
	
	# Copy file
	var dir = DirAccess.open(current_path)
	if dir:
		var error = dir.copy(file_name, dest_path.get_file())
		if error == OK:
			refresh_current_directory()
			update_status("✅ Duplicated: " + file_name)
		else:
			show_error("Error duplicating file: " + file_name)

func open_new_window():
	# Launch a new instance of the application
	var executable = OS.get_executable_path()
	OS.execute(executable, ["--path", current_path], [])

func open_settings():
	var dialog = AcceptDialog.new()
	dialog.title = "Settings"
	dialog.dialog_text = "Settings dialog will be implemented here"
	dialog.dialog_autowrap = true
	add_child(dialog)
	dialog.popup_centered()

func start_file_operation(operation_name: String, total_items: int):
	current_operation = operation_name
	operation_total = total_items
	operation_current = 0
	operation_progress = 0.0
	
	progress_bar.visible = true
	progress_bar.max_value = total_items
	progress_bar.value = 0
	update_status("🔄 " + operation_name)

func update_operation_progress(current: int):
	operation_current = current
	operation_progress = float(current) / float(operation_total)
	progress_bar.value = current
	
	if current >= operation_total:
		progress_bar.visible = false
		update_status("✅ " + current_operation + " completed")

func open_file_in_new_window(file_path: String):
	# Open file in a new editor window
	var executable = OS.get_executable_path()
	OS.execute(executable, ["--path", file_path, "--edit"], [])

# ===== UNITY INTEGRATION =====

func setup_unity_integration():
	# Set up Unity-specific features
	pass

func is_unity_project(path: String) -> bool:
	return FileAccess.file_exists(path.path_join("ProjectSettings/ProjectVersion.txt"))

func handle_unity_asset(file_path: String):
	# Special handling for Unity assets
	if file_path.get_extension() in ["unity", "prefab", "mat", "asset"]:
		update_status("🎮 Unity asset detected: " + file_path.get_file())

# ===== DRAG AND DROP =====

func _get_drag_data(position: Vector2):
	if selected_files.is_empty():
		return null
	
	var preview = Label.new()
	preview.text = str(selected_files.size()) + " items"
	
	set_drag_preview(preview)
	
	# Return drag data
	return {
		"type": "files",
		"files": selected_files
	}

func _can_drop_data(position: Vector2, data) -> bool:
	return data is Dictionary and data.has("type") and data.type == "files"

func _drop_data(position: Vector2, data):
	var files = data.files
	# Handle drop operation
	update_status("📥 Dropped " + str(files.size()) + " items")