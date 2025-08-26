import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import shutil
import threading
from datetime import datetime
import platform
import subprocess

class FileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows File Manager")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Current directory
        self.current_path = os.path.expanduser("~")
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create address bar
        self.create_address_bar()
        
        # Create main content area
        self.create_content_area()
        
        # Create status bar
        self.create_status_bar()
        
        # Load initial directory
        self.load_directory(self.current_path)
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
    
    def create_toolbar(self):
        """Create the toolbar with common actions"""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Navigation buttons
        ttk.Button(toolbar, text="← Back", command=self.go_back).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="↑ Up", command=self.go_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="⟳ Refresh", command=self.refresh).pack(side=tk.LEFT, padx=2)
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # File operations
        ttk.Button(toolbar, text="📁 New Folder", command=self.create_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📄 New File", command=self.create_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✂️ Cut", command=self.cut_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📋 Copy", command=self.copy_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📌 Paste", command=self.paste_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑️ Delete", command=self.delete_files).pack(side=tk.LEFT, padx=2)
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # View options
        ttk.Button(toolbar, text="🔍 Search", command=self.search_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="⚙️ Properties", command=self.show_properties).pack(side=tk.LEFT, padx=2)
        
        # Clipboard for cut/copy operations
        self.clipboard = []
        self.clipboard_mode = None  # 'cut' or 'copy'
    
    def create_address_bar(self):
        """Create the address bar"""
        address_frame = ttk.Frame(self.main_frame)
        address_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(address_frame, text="Address:").pack(side=tk.LEFT)
        
        self.address_var = tk.StringVar()
        self.address_entry = ttk.Entry(address_frame, textvariable=self.address_var, font=('Consolas', 10))
        self.address_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        ttk.Button(address_frame, text="Go", command=self.navigate_to_address).pack(side=tk.LEFT, padx=(5, 0))
        
        # Bind Enter key to address bar
        self.address_entry.bind('<Return>', lambda e: self.navigate_to_address())
    
    def create_content_area(self):
        """Create the main content area with treeview and details"""
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create paned window for resizable panels
        paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - File tree
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Folders", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Treeview for folders
        self.tree = ttk.Treeview(left_frame, show='tree')
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Scrollbar for tree
        tree_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        # Right panel - File list
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        
        ttk.Label(right_frame, text="Files", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Frame for file list
        file_frame = ttk.Frame(right_frame)
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Treeview for files
        columns = ('Name', 'Size', 'Type', 'Modified')
        self.file_tree = ttk.Treeview(file_frame, columns=columns, show='tree headings')
        
        # Configure columns
        self.file_tree.heading('#0', text='Name')
        self.file_tree.heading('Name', text='Name')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Type', text='Type')
        self.file_tree.heading('Modified', text='Modified')
        
        self.file_tree.column('#0', width=300)
        self.file_tree.column('Name', width=300)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Type', width=100)
        self.file_tree.column('Modified', width=150)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for file list
        file_scroll_y = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        file_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        file_scroll_x = ttk.Scrollbar(file_frame, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        file_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.file_tree.configure(yscrollcommand=file_scroll_y.set, xscrollcommand=file_scroll_x.set)
        
        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.file_tree.bind('<Double-1>', self.on_file_double_click)
        self.file_tree.bind('<Button-3>', self.show_context_menu)
        self.file_tree.bind('<Control-a>', self.select_all)
        self.file_tree.bind('<Control-c>', lambda e: self.copy_files())
        self.file_tree.bind('<Control-x>', lambda e: self.cut_files())
        self.file_tree.bind('<Control-v>', lambda e: self.paste_files())
        self.file_tree.bind('<Delete>', lambda e: self.delete_files())
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Label(self.main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<F5>', lambda e: self.refresh())
        self.root.bind('<Control-r>', lambda e: self.refresh())
        self.root.bind('<Control-l>', lambda e: self.address_entry.focus())
    
    def load_directory(self, path):
        """Load and display the contents of a directory"""
        try:
            self.current_path = os.path.abspath(path)
            self.address_var.set(self.current_path)
            
            # Clear existing items
            self.tree.delete(*self.tree.get_children())
            self.file_tree.delete(*self.file_tree.get_children())
            
            # Load folder tree
            self.load_folder_tree()
            
            # Load files
            self.load_files()
            
            # Update status
            self.update_status()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load directory: {str(e)}")
    
    def load_folder_tree(self):
        """Load the folder tree structure"""
        try:
            # Add drives (Windows)
            if platform.system() == "Windows":
                import win32api
                drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
                for drive in drives:
                    self.tree.insert('', 'end', drive, text=drive, values=(drive,))
            else:
                # For non-Windows systems, start from root
                self.tree.insert('', 'end', '/', text='/', values=('/',))
            
            # Add current path folders
            path_parts = self.current_path.split(os.sep)
            current_path = ""
            
            for part in path_parts:
                if part:
                    current_path = os.path.join(current_path, part) if current_path else part
                    if os.path.exists(current_path):
                        self.tree.insert('', 'end', current_path, text=part, values=(current_path,))
            
        except Exception as e:
            print(f"Error loading folder tree: {e}")
    
    def load_files(self):
        """Load files in the current directory"""
        try:
            items = os.listdir(self.current_path)
            
            # Separate folders and files
            folders = []
            files = []
            
            for item in items:
                item_path = os.path.join(self.current_path, item)
                if os.path.isdir(item_path):
                    folders.append(item)
                else:
                    files.append(item)
            
            # Add folders first
            for folder in sorted(folders):
                folder_path = os.path.join(self.current_path, folder)
                try:
                    stat = os.stat(folder_path)
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                    self.file_tree.insert('', 'end', folder_path, text=folder, 
                                        values=(folder, '<DIR>', 'Folder', modified))
                except:
                    self.file_tree.insert('', 'end', folder_path, text=folder, 
                                        values=(folder, '<DIR>', 'Folder', ''))
            
            # Add files
            for file in sorted(files):
                file_path = os.path.join(self.current_path, file)
                try:
                    stat = os.stat(file_path)
                    size = self.format_size(stat.st_size)
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                    file_type = self.get_file_type(file)
                    self.file_tree.insert('', 'end', file_path, text=file, 
                                        values=(file, size, file_type, modified))
                except:
                    self.file_tree.insert('', 'end', file_path, text=file, 
                                        values=(file, '', 'Unknown', ''))
                    
        except Exception as e:
            messagebox.showerror("Error", f"Could not load files: {str(e)}")
    
    def format_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def get_file_type(self, filename):
        """Get file type based on extension"""
        ext = os.path.splitext(filename)[1].lower()
        type_map = {
            '.txt': 'Text File',
            '.py': 'Python File',
            '.js': 'JavaScript File',
            '.html': 'HTML File',
            '.css': 'CSS File',
            '.json': 'JSON File',
            '.xml': 'XML File',
            '.pdf': 'PDF File',
            '.doc': 'Word Document',
            '.docx': 'Word Document',
            '.xls': 'Excel Spreadsheet',
            '.xlsx': 'Excel Spreadsheet',
            '.ppt': 'PowerPoint Presentation',
            '.pptx': 'PowerPoint Presentation',
            '.jpg': 'JPEG Image',
            '.jpeg': 'JPEG Image',
            '.png': 'PNG Image',
            '.gif': 'GIF Image',
            '.bmp': 'BMP Image',
            '.mp3': 'MP3 Audio',
            '.mp4': 'MP4 Video',
            '.avi': 'AVI Video',
            '.zip': 'ZIP Archive',
            '.rar': 'RAR Archive',
            '.7z': '7-Zip Archive',
            '.exe': 'Executable',
            '.msi': 'Windows Installer',
            '.dll': 'Dynamic Link Library',
            '.sys': 'System File',
            '.ini': 'Configuration File',
            '.log': 'Log File',
            '.tmp': 'Temporary File',
            '.bak': 'Backup File'
        }
        return type_map.get(ext, 'File')
    
    def update_status(self):
        """Update status bar with current directory info"""
        try:
            items = os.listdir(self.current_path)
            folders = sum(1 for item in items if os.path.isdir(os.path.join(self.current_path, item)))
            files = len(items) - folders
            
            status_text = f"Path: {self.current_path} | Folders: {folders} | Files: {files}"
            self.status_bar.config(text=status_text)
        except:
            self.status_bar.config(text=f"Path: {self.current_path}")
    
    def on_tree_select(self, event):
        """Handle tree selection"""
        selection = self.tree.selection()
        if selection:
            selected_path = selection[0]
            if os.path.exists(selected_path):
                self.load_directory(selected_path)
    
    def on_file_double_click(self, event):
        """Handle file double click"""
        selection = self.file_tree.selection()
        if selection:
            item_path = selection[0]
            if os.path.isdir(item_path):
                self.load_directory(item_path)
            else:
                self.open_file(item_path)
    
    def open_file(self, file_path):
        """Open a file with default application"""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def go_back(self):
        """Go back to previous directory"""
        # This would need to maintain a history stack
        # For now, just go up one level
        self.go_up()
    
    def go_up(self):
        """Go up one directory level"""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.load_directory(parent)
    
    def refresh(self):
        """Refresh the current directory"""
        self.load_directory(self.current_path)
    
    def navigate_to_address(self):
        """Navigate to the address in the address bar"""
        path = self.address_var.get().strip()
        if os.path.exists(path):
            self.load_directory(path)
        else:
            messagebox.showerror("Error", "Path does not exist")
    
    def create_folder(self):
        """Create a new folder"""
        name = simpledialog.askstring("New Folder", "Enter folder name:")
        if name:
            try:
                new_folder_path = os.path.join(self.current_path, name)
                os.makedirs(new_folder_path, exist_ok=True)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder: {str(e)}")
    
    def create_file(self):
        """Create a new file"""
        name = simpledialog.askstring("New File", "Enter file name:")
        if name:
            try:
                new_file_path = os.path.join(self.current_path, name)
                with open(new_file_path, 'w') as f:
                    pass  # Create empty file
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create file: {str(e)}")
    
    def cut_files(self):
        """Cut selected files to clipboard"""
        selection = self.file_tree.selection()
        if selection:
            self.clipboard = list(selection)
            self.clipboard_mode = 'cut'
            self.status_bar.config(text=f"Cut {len(selection)} item(s)")
    
    def copy_files(self):
        """Copy selected files to clipboard"""
        selection = self.file_tree.selection()
        if selection:
            self.clipboard = list(selection)
            self.clipboard_mode = 'copy'
            self.status_bar.config(text=f"Copied {len(selection)} item(s)")
    
    def paste_files(self):
        """Paste files from clipboard"""
        if not self.clipboard:
            return
        
        for source_path in self.clipboard:
            try:
                filename = os.path.basename(source_path)
                dest_path = os.path.join(self.current_path, filename)
                
                # Handle duplicate names
                counter = 1
                original_dest = dest_path
                while os.path.exists(dest_path):
                    name, ext = os.path.splitext(filename)
                    dest_path = os.path.join(self.current_path, f"{name} ({counter}){ext}")
                    counter += 1
                
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, dest_path)
                else:
                    shutil.copy2(source_path, dest_path)
                
                if self.clipboard_mode == 'cut':
                    if os.path.isdir(source_path):
                        shutil.rmtree(source_path)
                    else:
                        os.remove(source_path)
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not paste {filename}: {str(e)}")
        
        if self.clipboard_mode == 'cut':
            self.clipboard = []
            self.clipboard_mode = None
        
        self.refresh()
    
    def delete_files(self):
        """Delete selected files"""
        selection = self.file_tree.selection()
        if not selection:
            return
        
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete {len(selection)} item(s)?")
        if result:
            for item_path in selection:
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete {os.path.basename(item_path)}: {str(e)}")
            
            self.refresh()
    
    def search_files(self):
        """Search for files"""
        search_term = simpledialog.askstring("Search Files", "Enter search term:")
        if search_term:
            self.perform_search(search_term)
    
    def perform_search(self, search_term):
        """Perform file search"""
        results = []
        
        def search_recursive(path):
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if search_term.lower() in item.lower():
                        results.append(item_path)
                    
                    if os.path.isdir(item_path):
                        search_recursive(item_path)
            except:
                pass
        
        # Search in current directory and subdirectories
        search_recursive(self.current_path)
        
        if results:
            self.show_search_results(results, search_term)
        else:
            messagebox.showinfo("Search Results", "No files found matching your search term.")
    
    def show_search_results(self, results, search_term):
        """Show search results in a new window"""
        search_window = tk.Toplevel(self.root)
        search_window.title(f"Search Results for '{search_term}'")
        search_window.geometry("800x600")
        
        # Create treeview for results
        columns = ('Path', 'Size', 'Type', 'Modified')
        result_tree = ttk.Treeview(search_window, columns=columns, show='tree headings')
        
        result_tree.heading('#0', text='Name')
        result_tree.heading('Path', text='Path')
        result_tree.heading('Size', text='Size')
        result_tree.heading('Type', text='Type')
        result_tree.heading('Modified', text='Modified')
        
        result_tree.column('#0', width=200)
        result_tree.column('Path', width=400)
        result_tree.column('Size', width=100)
        result_tree.column('Type', width=100)
        result_tree.column('Modified', width=150)
        
        result_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add results
        for result_path in results:
            try:
                filename = os.path.basename(result_path)
                stat = os.stat(result_path)
                size = self.format_size(stat.st_size) if os.path.isfile(result_path) else '<DIR>'
                modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                file_type = 'Folder' if os.path.isdir(result_path) else self.get_file_type(filename)
                
                result_tree.insert('', 'end', result_path, text=filename,
                                 values=(result_path, size, file_type, modified))
            except:
                pass
        
        # Bind double-click to open file/folder
        def on_result_double_click(event):
            selection = result_tree.selection()
            if selection:
                item_path = selection[0]
                if os.path.isdir(item_path):
                    self.load_directory(item_path)
                    search_window.destroy()
                else:
                    self.open_file(item_path)
        
        result_tree.bind('<Double-1>', on_result_double_click)
    
    def show_properties(self):
        """Show properties of selected file"""
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showinfo("Properties", "Please select a file or folder first.")
            return
        
        item_path = selection[0]
        try:
            stat = os.stat(item_path)
            
            properties = f"""
Name: {os.path.basename(item_path)}
Path: {item_path}
Type: {'Folder' if os.path.isdir(item_path) else 'File'}
Size: {self.format_size(stat.st_size) if os.path.isfile(item_path) else 'N/A'}
Created: {datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}
Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
Accessed: {datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')}
Permissions: {oct(stat.st_mode)[-3:]}
            """
            
            messagebox.showinfo("Properties", properties)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not get properties: {str(e)}")
    
    def select_all(self, event=None):
        """Select all files"""
        for item in self.file_tree.get_children():
            self.file_tree.selection_add(item)
    
    def show_context_menu(self, event):
        """Show context menu for right-click"""
        selection = self.file_tree.selection()
        if not selection:
            return
        
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Open", command=lambda: self.open_file(selection[0]))
        context_menu.add_command(label="Open with...", command=lambda: self.open_with(selection[0]))
        context_menu.add_separator()
        context_menu.add_command(label="Cut", command=self.cut_files)
        context_menu.add_command(label="Copy", command=self.copy_files)
        context_menu.add_command(label="Paste", command=self.paste_files)
        context_menu.add_separator()
        context_menu.add_command(label="Delete", command=self.delete_files)
        context_menu.add_command(label="Rename", command=lambda: self.rename_file(selection[0]))
        context_menu.add_separator()
        context_menu.add_command(label="Properties", command=self.show_properties)
        
        context_menu.tk_popup(event.x_root, event.y_root)
    
    def open_with(self, file_path):
        """Open file with specific application"""
        # This would typically show a dialog to select an application
        # For now, just open with default
        self.open_file(file_path)
    
    def rename_file(self, file_path):
        """Rename a file or folder"""
        old_name = os.path.basename(file_path)
        new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
        
        if new_name and new_name != old_name:
            try:
                new_path = os.path.join(os.path.dirname(file_path), new_name)
                os.rename(file_path, new_path)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename: {str(e)}")

def main():
    root = tk.Tk()
    
    # Set application icon (optional)
    try:
        root.iconbitmap('file_manager.ico')
    except:
        pass
    
    # Create and run file manager
    app = FileManager(root)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()