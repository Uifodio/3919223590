#!/usr/bin/env python3
"""
Professional Web Server Manager - Main Application
Full deployment server network with multiple servers and proper controls
"""

import sys
import os
import time
import json
from pathlib import Path
from server_manager import ServerManager

class ProfessionalWebServerApp:
    """Professional web server management application"""
    
    def __init__(self):
        self.manager = ServerManager()
        self.running = True
    
    def print_banner(self):
        """Print application banner"""
        print("=" * 60)
        print("🚀 PROFESSIONAL WEB SERVER MANAGER")
        print("   Full Deployment Server Network")
        print("=" * 60)
        print()
    
    def print_menu(self):
        """Print main menu"""
        print("📋 MAIN MENU:")
        print("1. Create New Server")
        print("2. Start Server")
        print("3. Stop Server")
        print("4. List All Servers")
        print("5. Show Server Status")
        print("6. Open Server in Browser")
        print("7. View Server Logs")
        print("8. Save Configuration")
        print("9. Load Configuration")
        print("0. Exit")
        print()
    
    def create_server(self):
        """Create a new server"""
        print("\n🔧 CREATE NEW SERVER")
        print("-" * 30)
        
        try:
            port = int(input("Enter port number: "))
            directory = input("Enter directory path: ").strip()
            
            if not directory:
                directory = str(Path.home())
            
            # Expand user path
            directory = os.path.expanduser(directory)
            
            if not os.path.exists(directory):
                create = input(f"Directory {directory} doesn't exist. Create it? (y/n): ").lower()
                if create == 'y':
                    os.makedirs(directory, exist_ok=True)
                    print(f"✅ Created directory: {directory}")
                else:
                    print("❌ Server creation cancelled")
                    return
            
            server_id = self.manager.create_server(port, directory)
            print(f"✅ Server {server_id} created successfully!")
            print(f"   Port: {port}")
            print(f"   Directory: {directory}")
            
        except ValueError:
            print("❌ Invalid port number")
        except Exception as e:
            print(f"❌ Error creating server: {e}")
    
    def start_server(self):
        """Start a server"""
        print("\n▶️  START SERVER")
        print("-" * 20)
        
        servers = self.manager.list_servers()
        if not servers:
            print("❌ No servers available")
            return
        
        print("Available servers:")
        for server_id in servers:
            status = self.manager.get_server_status(server_id)
            print(f"  {server_id}: Port {status['port']} - {status['directory']} ({'Running' if status['is_running'] else 'Stopped'})")
        
        try:
            server_id = int(input("\nEnter server ID to start: "))
            if self.manager.start_server(server_id):
                print(f"✅ Server {server_id} started successfully!")
                print(f"🌐 Access at: http://localhost:{self.manager.servers[server_id].port}")
            else:
                print(f"❌ Failed to start server {server_id}")
        except ValueError:
            print("❌ Invalid server ID")
        except Exception as e:
            print(f"❌ Error starting server: {e}")
    
    def stop_server(self):
        """Stop a server"""
        print("\n⏹️  STOP SERVER")
        print("-" * 20)
        
        servers = self.manager.list_servers()
        if not servers:
            print("❌ No servers available")
            return
        
        running_servers = [s for s in servers if self.manager.get_server_status(s)['is_running']]
        if not running_servers:
            print("❌ No running servers")
            return
        
        print("Running servers:")
        for server_id in running_servers:
            status = self.manager.get_server_status(server_id)
            print(f"  {server_id}: Port {status['port']} - {status['directory']}")
        
        try:
            server_id = int(input("\nEnter server ID to stop: "))
            if self.manager.stop_server(server_id):
                print(f"✅ Server {server_id} stopped successfully!")
            else:
                print(f"❌ Failed to stop server {server_id}")
        except ValueError:
            print("❌ Invalid server ID")
        except Exception as e:
            print(f"❌ Error stopping server: {e}")
    
    def list_servers(self):
        """List all servers"""
        print("\n📋 ALL SERVERS")
        print("-" * 20)
        
        servers = self.manager.get_all_servers_status()
        if not servers:
            print("❌ No servers created")
            return
        
        print(f"{'ID':<4} {'Port':<6} {'Status':<8} {'Directory':<30} {'Uptime':<10}")
        print("-" * 70)
        
        for server_id, status in servers.items():
            uptime_str = f"{status['uptime']:.1f}s" if status['uptime'] > 0 else "N/A"
            status_str = "Running" if status['is_running'] else "Stopped"
            directory = os.path.basename(status['directory'])
            
            print(f"{server_id:<4} {status['port']:<6} {status_str:<8} {directory:<30} {uptime_str:<10}")
    
    def show_server_status(self):
        """Show detailed server status"""
        print("\n📊 SERVER STATUS")
        print("-" * 20)
        
        servers = self.manager.list_servers()
        if not servers:
            print("❌ No servers available")
            return
        
        print("Available servers:")
        for server_id in servers:
            status = self.manager.get_server_status(server_id)
            print(f"  {server_id}: Port {status['port']} - {status['directory']}")
        
        try:
            server_id = int(input("\nEnter server ID for details: "))
            status = self.manager.get_server_status(server_id)
            if status:
                print(f"\n📊 Server {server_id} Details:")
                print(f"   Port: {status['port']}")
                print(f"   Directory: {status['directory']}")
                print(f"   Status: {'Running' if status['is_running'] else 'Stopped'}")
                print(f"   Uptime: {status['uptime']:.1f} seconds")
                print(f"   Start Time: {time.ctime(status['start_time']) if status['start_time'] else 'N/A'}")
            else:
                print("❌ Server not found")
        except ValueError:
            print("❌ Invalid server ID")
    
    def open_server_in_browser(self):
        """Open server in browser"""
        print("\n🌐 OPEN IN BROWSER")
        print("-" * 20)
        
        servers = self.manager.list_servers()
        if not servers:
            print("❌ No servers available")
            return
        
        running_servers = [s for s in servers if self.manager.get_server_status(s)['is_running']]
        if not running_servers:
            print("❌ No running servers")
            return
        
        print("Running servers:")
        for server_id in running_servers:
            status = self.manager.get_server_status(server_id)
            print(f"  {server_id}: Port {status['port']} - {status['directory']}")
        
        try:
            server_id = int(input("\nEnter server ID to open: "))
            if self.manager.open_server_in_browser(server_id):
                print(f"✅ Opening server {server_id} in browser...")
            else:
                print(f"❌ Failed to open server {server_id}")
        except ValueError:
            print("❌ Invalid server ID")
    
    def view_server_logs(self):
        """View server logs"""
        print("\n📄 SERVER LOGS")
        print("-" * 20)
        
        servers = self.manager.list_servers()
        if not servers:
            print("❌ No servers available")
            return
        
        print("Available servers:")
        for server_id in servers:
            status = self.manager.get_server_status(server_id)
            print(f"  {server_id}: Port {status['port']} - {status['directory']}")
        
        try:
            server_id = int(input("\nEnter server ID for logs: "))
            log_file = Path("logs") / f"server_{server_id}.log"
            
            if log_file.exists():
                print(f"\n📄 Logs for Server {server_id}:")
                print("-" * 40)
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    # Show last 20 lines
                    for line in lines[-20:]:
                        print(line.rstrip())
            else:
                print(f"❌ No log file found for server {server_id}")
        except ValueError:
            print("❌ Invalid server ID")
        except Exception as e:
            print(f"❌ Error reading logs: {e}")
    
    def save_configuration(self):
        """Save server configuration"""
        print("\n💾 SAVE CONFIGURATION")
        print("-" * 25)
        
        config = {
            'servers': {},
            'next_server_id': self.manager.next_server_id
        }
        
        for server_id, server in self.manager.servers.items():
            config['servers'][str(server_id)] = {
                'port': server.port,
                'directory': server.directory,
                'server_id': server.server_id
            }
        
        config_file = Path("server_config.json")
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Configuration saved to {config_file}")
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
    
    def load_configuration(self):
        """Load server configuration"""
        print("\n📂 LOAD CONFIGURATION")
        print("-" * 25)
        
        config_file = Path("server_config.json")
        if not config_file.exists():
            print("❌ No configuration file found")
            return
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Clear existing servers
            self.manager.servers.clear()
            self.manager.next_server_id = config.get('next_server_id', 1)
            
            # Load servers
            for server_id_str, server_config in config.get('servers', {}).items():
                server_id = int(server_id_str)
                port = server_config['port']
                directory = server_config['directory']
                
                server = self.manager.servers[server_id] = self.manager.manager.WebServer(
                    server_id, port, directory, self.manager
                )
            
            print(f"✅ Configuration loaded from {config_file}")
            print(f"   Loaded {len(self.manager.servers)} servers")
            
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
    
    def run(self):
        """Run the main application loop"""
        self.print_banner()
        
        while self.running:
            try:
                self.print_menu()
                choice = input("Enter your choice (0-9): ").strip()
                
                if choice == '0':
                    print("\n👋 Shutting down all servers...")
                    for server_id in list(self.manager.servers.keys()):
                        self.manager.stop_server(server_id)
                    print("✅ All servers stopped. Goodbye!")
                    self.running = False
                
                elif choice == '1':
                    self.create_server()
                
                elif choice == '2':
                    self.start_server()
                
                elif choice == '3':
                    self.stop_server()
                
                elif choice == '4':
                    self.list_servers()
                
                elif choice == '5':
                    self.show_server_status()
                
                elif choice == '6':
                    self.open_server_in_browser()
                
                elif choice == '7':
                    self.view_server_logs()
                
                elif choice == '8':
                    self.save_configuration()
                
                elif choice == '9':
                    self.load_configuration()
                
                else:
                    print("❌ Invalid choice. Please try again.")
                
                if self.running:
                    input("\nPress Enter to continue...")
                    print("\n" + "="*60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Shutting down all servers...")
                for server_id in list(self.manager.servers.keys()):
                    self.manager.stop_server(server_id)
                print("✅ All servers stopped. Goodbye!")
                self.running = False
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                input("Press Enter to continue...")

def main():
    """Main function"""
    try:
        app = ProfessionalWebServerApp()
        app.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()