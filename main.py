#!/usr/bin/env python3
"""
Modern Server Administrator GUI
A professional web server management tool with dark theme and modern UI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import subprocess
import os
import json
import webbrowser
from datetime import datetime
import mimetypes
from pathlib import Path
import shutil
import http.server
import socketserver
from urllib.parse import unquote
import queue
import time

class ModernServerAdmin:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Server Administrator")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Server management
        self.servers = {}
        self.server_processes = {}
        self.log_queues = {}
        
        # Configure style
        self.setup_styles()
        
        # Create main interface
        self.create_main_interface()
        
        # Start log monitoring
        self.monitor_logs()
        
    def setup_styles(self):
        """Configure modern dark theme styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       background='#1e1e1e', 
                       foreground='#ffffff', 
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Header.TLabel', 
                       background='#2d2d2d', 
                       foreground='#ffffff', 
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure('Modern.TFrame', 
                       background='#2d2d2d', 
                       relief='flat', 
                       borderwidth=0)
        
        style.configure('Server.TFrame', 
                       background='#3d3d3d', 
                       relief='flat', 
                       borderwidth=1)
        
        style.configure('Modern.TButton', 
                       background='#0078d4', 
                       foreground='#ffffff', 
                       font=('Segoe UI', 10),
                       relief='flat',
                       borderwidth=0)
        
        style.map('Modern.TButton',
                 background=[('active', '#106ebe'),
                           ('pressed', '#005a9e')])
        
        style.configure('Danger.TButton', 
                       background='#d13438', 
                       foreground='#ffffff', 
                       font=('Segoe UI', 10),
                       relief='flat',
                       borderwidth=0)
        
        style.map('Danger.TButton',
                 background=[('active', '#b71c1c'),
                           ('pressed', '#8b0000')])
        
        style.configure('Success.TButton', 
                       background='#107c10', 
                       foreground='#ffffff', 
                       font=('Segoe UI', 10),
                       relief='flat',
                       borderwidth=0)
        
        style.map('Success.TButton',
                 background=[('active', '#0d5d0d'),
                           ('pressed', '#0a4a0a')])
        
        style.configure('Modern.TEntry', 
                       background='#3d3d3d', 
                       foreground='#ffffff', 
                       font=('Segoe UI', 10),
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Modern.TCombobox', 
                       background='#3d3d3d', 
                       foreground='#ffffff', 
                       font=('Segoe UI', 10),
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Modern.Treeview', 
                       background='#2d2d2d', 
                       foreground='#ffffff', 
                       font=('Segoe UI', 10),
                       relief='flat',
                       borderwidth=0)
        
        style.configure('Modern.Treeview.Heading', 
                       background='#3d3d3d', 
                       foreground='#ffffff', 
                       font=('Segoe UI', 10, 'bold'),
                       relief='flat',
                       borderwidth=0)
        
    def create_main_interface(self):
        """Create the main application interface"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(title_frame, 
                               text="🚀 Modern Server Administrator", 
                               style='Title.TLabel')
        title_label.pack(side='left')
        
        # Status indicator
        self.status_label = ttk.Label(title_frame, 
                                     text="● Ready", 
                                     foreground='#4caf50',
                                     font=('Segoe UI', 10, 'bold'))
        self.status_label.pack(side='right')
        
        # Control panel
        self.create_control_panel(main_frame)
        
        # Server list
        self.create_server_list(main_frame)
        
        # File manager
        self.create_file_manager(main_frame)
        
    def create_control_panel(self, parent):
        """Create the control panel for adding new servers"""
        control_frame = ttk.LabelFrame(parent, 
                                      text="Server Control Panel", 
                                      style='Modern.TFrame',
                                      padding=15)
        control_frame.pack(fill='x', pady=(0, 20))
        
        # Server configuration
        config_frame = ttk.Frame(control_frame, style='Modern.TFrame')
        config_frame.pack(fill='x', pady=(0, 10))
        
        # Website folder selection
        folder_frame = ttk.Frame(config_frame, style='Modern.TFrame')
        folder_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(folder_frame, text="Website Folder:", style='Header.TLabel').pack(side='left')
        self.folder_var = tk.StringVar()
        self.folder_entry = ttk.Entry(folder_frame, 
                                     textvariable=self.folder_var, 
                                     style='Modern.TEntry',
                                     width=50)
        self.folder_entry.pack(side='left', padx=(10, 5), fill='x', expand=True)
        
        ttk.Button(folder_frame, 
                  text="Browse", 
                  command=self.browse_folder,
                  style='Modern.TButton').pack(side='right', padx=(5, 0))
        
        # Port configuration
        port_frame = ttk.Frame(config_frame, style='Modern.TFrame')
        port_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(port_frame, text="Port:", style='Header.TLabel').pack(side='left')
        self.port_var = tk.StringVar(value="8000")
        port_entry = ttk.Entry(port_frame, 
                              textvariable=self.port_var, 
                              style='Modern.TEntry',
                              width=10)
        port_entry.pack(side='left', padx=(10, 20))
        
        # Server type
        ttk.Label(port_frame, text="Type:", style='Header.TLabel').pack(side='left')
        self.server_type_var = tk.StringVar(value="HTTP")
        server_type_combo = ttk.Combobox(port_frame, 
                                        textvariable=self.server_type_var,
                                        values=["HTTP", "HTTPS", "PHP", "Node.js"],
                                        style='Modern.TCombobox',
                                        width=15,
                                        state='readonly')
        server_type_combo.pack(side='left', padx=(10, 0))
        
        # Action buttons
        button_frame = ttk.Frame(config_frame, style='Modern.TFrame')
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, 
                  text="➕ Add Server", 
                  command=self.add_server,
                  style='Success.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, 
                  text="🔄 Refresh All", 
                  command=self.refresh_all_servers,
                  style='Modern.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, 
                  text="📊 System Info", 
                  command=self.show_system_info,
                  style='Modern.TButton').pack(side='left')
        
    def create_server_list(self, parent):
        """Create the server list display"""
        server_frame = ttk.LabelFrame(parent, 
                                     text="Active Servers", 
                                     style='Modern.TFrame',
                                     padding=15)
        server_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Server list treeview
        columns = ('Name', 'Port', 'Type', 'Status', 'Folder', 'Actions')
        self.server_tree = ttk.Treeview(server_frame, 
                                       columns=columns, 
                                       show='headings',
                                       style='Modern.Treeview',
                                       height=8)
        
        # Configure columns
        self.server_tree.heading('Name', text='Server Name')
        self.server_tree.heading('Port', text='Port')
        self.server_tree.heading('Type', text='Type')
        self.server_tree.heading('Status', text='Status')
        self.server_tree.heading('Folder', text='Folder')
        self.server_tree.heading('Actions', text='Actions')
        
        self.server_tree.column('Name', width=150)
        self.server_tree.column('Port', width=80)
        self.server_tree.column('Type', width=100)
        self.server_tree.column('Status', width=100)
        self.server_tree.column('Folder', width=200)
        self.server_tree.column('Actions', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(server_frame, orient='vertical', command=self.server_tree.yview)
        self.server_tree.configure(yscrollcommand=scrollbar.set)
        
        self.server_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind double-click for logs
        self.server_tree.bind('<Double-1>', self.show_server_logs)
        
    def create_file_manager(self, parent):
        """Create the file manager interface"""
        file_frame = ttk.LabelFrame(parent, 
                                   text="File Manager", 
                                   style='Modern.TFrame',
                                   padding=15)
        file_frame.pack(fill='both', expand=True)
        
        # File operations toolbar
        toolbar_frame = ttk.Frame(file_frame, style='Modern.TFrame')
        toolbar_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(toolbar_frame, 
                  text="📁 Open Folder", 
                  command=self.open_file_manager,
                  style='Modern.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(toolbar_frame, 
                  text="📤 Upload File", 
                  command=self.upload_file,
                  style='Modern.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(toolbar_frame, 
                  text="🎥 Upload Video", 
                  command=self.upload_video,
                  style='Modern.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(toolbar_frame, 
                  text="🗑️ Delete Selected", 
                  command=self.delete_selected_file,
                  style='Danger.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(toolbar_frame, 
                  text="🔄 Refresh", 
                  command=self.refresh_file_list,
                  style='Modern.TButton').pack(side='left')
        
        # File list
        file_list_frame = ttk.Frame(file_frame, style='Modern.TFrame')
        file_list_frame.pack(fill='both', expand=True)
        
        file_columns = ('Name', 'Size', 'Type', 'Modified', 'Actions')
        self.file_tree = ttk.Treeview(file_list_frame, 
                                     columns=file_columns, 
                                     show='headings',
                                     style='Modern.Treeview')
        
        # Configure file columns
        self.file_tree.heading('Name', text='File Name')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Type', text='Type')
        self.file_tree.heading('Modified', text='Modified')
        self.file_tree.heading('Actions', text='Actions')
        
        self.file_tree.column('Name', width=250)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Type', width=100)
        self.file_tree.column('Modified', width=150)
        self.file_tree.column('Actions', width=100)
        
        # File list scrollbar
        file_scrollbar = ttk.Scrollbar(file_list_frame, orient='vertical', command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=file_scrollbar.set)
        
        self.file_tree.pack(side='left', fill='both', expand=True)
        file_scrollbar.pack(side='right', fill='y')
        
        # Bind file selection
        self.file_tree.bind('<Double-1>', self.open_file)
        self.file_tree.bind('<Button-3>', self.show_file_context_menu)
        
    def browse_folder(self):
        """Browse for website folder"""
        folder = filedialog.askdirectory(title="Select Website Folder")
        if folder:
            self.folder_var.set(folder)
            self.refresh_file_list()
    
    def add_server(self):
        """Add a new server"""
        folder = self.folder_var.get()
        port = self.port_var.get()
        server_type = self.server_type_var.get()
        
        if not folder or not port:
            messagebox.showerror("Error", "Please select a folder and enter a port number")
            return
        
        if not os.path.exists(folder):
            messagebox.showerror("Error", "Selected folder does not exist")
            return
        
        try:
            port = int(port)
        except ValueError:
            messagebox.showerror("Error", "Port must be a valid number")
            return
        
        # Check if port is already in use
        if port in [server['port'] for server in self.servers.values()]:
            messagebox.showerror("Error", f"Port {port} is already in use")
            return
        
        # Generate server name
        server_name = f"Server-{port}"
        counter = 1
        while server_name in self.servers:
            server_name = f"Server-{port}-{counter}"
            counter += 1
        
        # Start server
        if self.start_server(server_name, folder, port, server_type):
            self.servers[server_name] = {
                'name': server_name,
                'folder': folder,
                'port': port,
                'type': server_type,
                'status': 'Running',
                'start_time': datetime.now()
            }
            self.update_server_list()
            self.status_label.config(text="● Server Added", foreground='#4caf50')
        else:
            messagebox.showerror("Error", "Failed to start server")
    
    def start_server(self, name, folder, port, server_type):
        """Start a web server"""
        try:
            if server_type == "HTTP":
                # Use Python's built-in HTTP server
                os.chdir(folder)
                process = subprocess.Popen([
                    'python', '-m', 'http.server', str(port)
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            elif server_type == "PHP":
                # Use PHP built-in server
                process = subprocess.Popen([
                    'php', '-S', f'localhost:{port}', '-t', folder
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            else:
                # Default to HTTP server
                os.chdir(folder)
                process = subprocess.Popen([
                    'python', '-m', 'http.server', str(port)
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.server_processes[name] = process
            self.log_queues[name] = queue.Queue()
            
            # Start log monitoring thread
            log_thread = threading.Thread(target=self.monitor_server_logs, args=(name, process))
            log_thread.daemon = True
            log_thread.start()
            
            return True
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
    
    def monitor_server_logs(self, name, process):
        """Monitor server logs in a separate thread"""
        while process.poll() is None:
            try:
                output = process.stdout.readline()
                if output:
                    self.log_queues[name].put({
                        'timestamp': datetime.now(),
                        'message': output.strip(),
                        'type': 'info'
                    })
            except:
                break
    
    def monitor_logs(self):
        """Monitor all server logs and update UI"""
        for name, log_queue in self.log_queues.items():
            try:
                while not log_queue.empty():
                    log_entry = log_queue.get_nowait()
                    # Update server status if needed
                    if "error" in log_entry['message'].lower():
                        if name in self.servers:
                            self.servers[name]['status'] = 'Error'
            except:
                pass
        
        # Schedule next check
        self.root.after(1000, self.monitor_logs)
    
    def stop_server(self, name):
        """Stop a server"""
        if name in self.server_processes:
            try:
                self.server_processes[name].terminate()
                self.server_processes[name].wait(timeout=5)
            except:
                self.server_processes[name].kill()
            
            del self.server_processes[name]
            if name in self.log_queues:
                del self.log_queues[name]
            
            if name in self.servers:
                self.servers[name]['status'] = 'Stopped'
                self.update_server_list()
    
    def update_server_list(self):
        """Update the server list display"""
        # Clear existing items
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)
        
        # Add servers
        for server in self.servers.values():
            status_color = '#4caf50' if server['status'] == 'Running' else '#f44336'
            
            item = self.server_tree.insert('', 'end', values=(
                server['name'],
                server['port'],
                server['type'],
                server['status'],
                os.path.basename(server['folder']),
                'View Logs | Stop'
            ))
            
            # Color code status
            self.server_tree.set(item, 'Status', server['status'])
    
    def show_server_logs(self, event):
        """Show server logs in a popup window"""
        selection = self.server_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        server_name = self.server_tree.item(item, 'values')[0]
        
        if server_name not in self.servers:
            return
        
        # Create log window
        log_window = tk.Toplevel(self.root)
        log_window.title(f"Logs - {server_name}")
        log_window.geometry("800x600")
        log_window.configure(bg='#1e1e1e')
        
        # Log display
        log_frame = ttk.Frame(log_window, style='Modern.TFrame')
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        log_text = scrolledtext.ScrolledText(log_frame, 
                                           bg='#2d2d2d', 
                                           fg='#ffffff',
                                           font=('Consolas', 10),
                                           wrap='word')
        log_text.pack(fill='both', expand=True)
        
        # Add sample logs (in real implementation, this would show actual logs)
        log_text.insert('end', f"Server: {server_name}\n")
        log_text.insert('end', f"Port: {self.servers[server_name]['port']}\n")
        log_text.insert('end', f"Status: {self.servers[server_name]['status']}\n")
        log_text.insert('end', f"Started: {self.servers[server_name]['start_time']}\n")
        log_text.insert('end', "-" * 50 + "\n")
        log_text.insert('end', "Server started successfully\n")
        log_text.insert('end', f"Serving files from: {self.servers[server_name]['folder']}\n")
        log_text.insert('end', f"Access at: http://localhost:{self.servers[server_name]['port']}\n")
        
        # Control buttons
        button_frame = ttk.Frame(log_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, 
                  text="🔄 Refresh", 
                  command=lambda: self.refresh_logs(log_text, server_name),
                  style='Modern.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, 
                  text="📋 Copy Logs", 
                  command=lambda: self.copy_logs(log_text),
                  style='Modern.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, 
                  text="🌐 Open in Browser", 
                  command=lambda: self.open_in_browser(server_name),
                  style='Modern.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, 
                  text="❌ Stop Server", 
                  command=lambda: self.stop_server_from_logs(log_window, server_name),
                  style='Danger.TButton').pack(side='right')
    
    def refresh_logs(self, log_text, server_name):
        """Refresh log display"""
        # In a real implementation, this would fetch actual logs
        log_text.insert('end', f"[{datetime.now()}] Log refresh requested\n")
        log_text.see('end')
    
    def copy_logs(self, log_text):
        """Copy logs to clipboard"""
        content = log_text.get('1.0', 'end-1c')
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("Success", "Logs copied to clipboard")
    
    def open_in_browser(self, server_name):
        """Open server in browser"""
        if server_name in self.servers:
            port = self.servers[server_name]['port']
            webbrowser.open(f'http://localhost:{port}')
    
    def stop_server_from_logs(self, log_window, server_name):
        """Stop server from log window"""
        self.stop_server(server_name)
        log_window.destroy()
        messagebox.showinfo("Success", f"Server {server_name} stopped")
    
    def refresh_all_servers(self):
        """Refresh all servers"""
        self.update_server_list()
        self.refresh_file_list()
        self.status_label.config(text="● Refreshed", foreground='#4caf50')
    
    def show_system_info(self):
        """Show system information"""
        info_window = tk.Toplevel(self.root)
        info_window.title("System Information")
        info_window.geometry("600x400")
        info_window.configure(bg='#1e1e1e')
        
        info_text = scrolledtext.ScrolledText(info_window, 
                                            bg='#2d2d2d', 
                                            fg='#ffffff',
                                            font=('Consolas', 10))
        info_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # System information
        import platform
        import psutil
        
        info = f"""
System Information
==================
OS: {platform.system()} {platform.release()}
Architecture: {platform.architecture()[0]}
Python Version: {platform.python_version()}
CPU Cores: {psutil.cpu_count()}
Memory: {psutil.virtual_memory().total // (1024**3)} GB
Disk Space: {psutil.disk_usage('/').free // (1024**3)} GB free

Active Servers
==============
"""
        
        for server in self.servers.values():
            info += f"• {server['name']} - Port {server['port']} ({server['status']})\n"
        
        info_text.insert('end', info)
        info_text.config(state='disabled')
    
    def open_file_manager(self):
        """Open file manager for current folder"""
        if self.folder_var.get():
            os.startfile(self.folder_var.get())
        else:
            messagebox.showwarning("Warning", "Please select a folder first")
    
    def upload_file(self):
        """Upload a file to the current folder"""
        if not self.folder_var.get():
            messagebox.showwarning("Warning", "Please select a folder first")
            return
        
        file_path = filedialog.askopenfilename(title="Select file to upload")
        if file_path:
            try:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(self.folder_var.get(), filename)
                shutil.copy2(file_path, dest_path)
                self.refresh_file_list()
                messagebox.showinfo("Success", f"File {filename} uploaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload file: {e}")
    
    def upload_video(self):
        """Upload a video file"""
        if not self.folder_var.get():
            messagebox.showwarning("Warning", "Please select a folder first")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select video file to upload",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm")]
        )
        if file_path:
            try:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(self.folder_var.get(), filename)
                shutil.copy2(file_path, dest_path)
                self.refresh_file_list()
                messagebox.showinfo("Success", f"Video {filename} uploaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload video: {e}")
    
    def delete_selected_file(self):
        """Delete selected file"""
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to delete")
            return
        
        item = selection[0]
        filename = self.file_tree.item(item, 'values')[0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {filename}?"):
            try:
                file_path = os.path.join(self.folder_var.get(), filename)
                os.remove(file_path)
                self.refresh_file_list()
                messagebox.showinfo("Success", f"File {filename} deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete file: {e}")
    
    def refresh_file_list(self):
        """Refresh the file list"""
        if not self.folder_var.get() or not os.path.exists(self.folder_var.get()):
            return
        
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Add files
        try:
            for filename in os.listdir(self.folder_var.get()):
                file_path = os.path.join(self.folder_var.get(), filename)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                    file_type = mimetypes.guess_type(filename)[0] or "Unknown"
                    
                    # Format size
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024**2:
                        size_str = f"{size/1024:.1f} KB"
                    elif size < 1024**3:
                        size_str = f"{size/(1024**2):.1f} MB"
                    else:
                        size_str = f"{size/(1024**3):.1f} GB"
                    
                    self.file_tree.insert('', 'end', values=(
                        filename,
                        size_str,
                        file_type,
                        modified.strftime("%Y-%m-%d %H:%M:%S"),
                        "View | Delete"
                    ))
        except Exception as e:
            print(f"Error refreshing file list: {e}")
    
    def open_file(self, event):
        """Open selected file"""
        selection = self.file_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        filename = self.file_tree.item(item, 'values')[0]
        file_path = os.path.join(self.folder_var.get(), filename)
        
        try:
            os.startfile(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")
    
    def show_file_context_menu(self, event):
        """Show context menu for file"""
        # This would show a right-click context menu
        pass

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = ModernServerAdmin(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()