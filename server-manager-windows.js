#!/usr/bin/env node

const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn, exec } = require('child_process');
const readline = require('readline');
const os = require('os');

class WindowsServerManager {
    constructor() {
        this.servers = new Map();
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        this.availablePorts = new Set();
        this.initializePorts();
        this.isWindows = os.platform() === 'win32';
    }

    initializePorts() {
        // Reserve ports 3000-3009 for our servers
        for (let i = 3000; i <= 3009; i++) {
            this.availablePorts.add(i);
        }
    }

    getNextAvailablePort() {
        for (const port of this.availablePorts) {
            if (!this.servers.has(port)) {
                return port;
            }
        }
        return null;
    }

    async startNodeServer(name, port, directory) {
        return new Promise((resolve, reject) => {
            const serverPath = path.join(directory, 'server.js');
            
            // Create a simple Node.js server if none exists
            if (!fs.existsSync(serverPath)) {
                this.createNodeServerTemplate(serverPath, port);
            }

            const server = spawn('node', [serverPath], {
                cwd: directory,
                stdio: ['pipe', 'pipe', 'pipe'],
                shell: this.isWindows
            });

            server.stdout.on('data', (data) => {
                console.log(`[${name}:${port}] ${data.toString().trim()}`);
            });

            server.stderr.on('data', (data) => {
                console.error(`[${name}:${port}] ERROR: ${data.toString().trim()}`);
            });

            server.on('close', (code) => {
                console.log(`[${name}:${port}] Server stopped with code ${code}`);
                this.servers.delete(port);
                this.availablePorts.add(port);
            });

            this.servers.set(port, {
                name,
                type: 'node',
                process: server,
                directory,
                startTime: new Date()
            });

            // Wait a moment for server to start
            setTimeout(() => {
                resolve(port);
            }, 1000);
        });
    }

    async startPHPServer(name, port, directory) {
        return new Promise((resolve, reject) => {
            const phpPath = this.isWindows ? 
                path.join(process.cwd(), 'bin', 'php', 'php.exe') : 
                'php';
            
            const server = spawn(phpPath, ['-S', `localhost:${port}`, '-t', directory], {
                stdio: ['pipe', 'pipe', 'pipe'],
                shell: this.isWindows
            });

            server.stdout.on('data', (data) => {
                console.log(`[${name}:${port}] ${data.toString().trim()}`);
            });

            server.stderr.on('data', (data) => {
                console.error(`[${name}:${port}] ERROR: ${data.toString().trim()}`);
            });

            server.on('close', (code) => {
                console.log(`[${name}:${port}] Server stopped with code ${code}`);
                this.servers.delete(port);
                this.availablePorts.add(port);
            });

            this.servers.set(port, {
                name,
                type: 'php',
                process: server,
                directory,
                startTime: new Date()
            });

            // Wait a moment for server to start
            setTimeout(() => {
                resolve(port);
            }, 1000);
        });
    }

    createNodeServerTemplate(serverPath, port) {
        const template = `const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || ${port};

const server = http.createServer((req, res) => {
    let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : req.url);
    
    // Security: prevent directory traversal
    filePath = path.resolve(filePath);
    if (!filePath.startsWith(__dirname)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
    }
    
    fs.readFile(filePath, (err, data) => {
        if (err) {
            if (err.code === 'ENOENT') {
                res.writeHead(404);
                res.end('File not found');
            } else {
                res.writeHead(500);
                res.end('Server error');
            }
        } else {
            const ext = path.extname(filePath);
            const contentType = {
                '.html': 'text/html',
                '.js': 'text/javascript',
                '.css': 'text/css',
                '.json': 'application/json',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml'
            }[ext] || 'text/plain';
            
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(data);
        }
    });
});

server.listen(PORT, () => {
    console.log(\`Node.js server running on http://localhost:\${PORT}\`);
});`;
        
        fs.writeFileSync(serverPath, template);
    }

    createPHPTemplate(directory) {
        const indexPath = path.join(directory, 'index.php');
        if (!fs.existsSync(indexPath)) {
            const template = `<?php
echo "<h1>PHP Server Running</h1>";
echo "<p>Server started at: " . date('Y-m-d H:i:s') . "</p>";
echo "<p>PHP Version: " . phpversion() . "</p>";
echo "<p>Document Root: " . __DIR__ . "</p>";
echo "<p>Request URI: " . $_SERVER['REQUEST_URI'] . "</p>";
?>`;
            fs.writeFileSync(indexPath, template);
        }
    }

    stopServer(port) {
        const server = this.servers.get(port);
        if (server) {
            if (this.isWindows) {
                // On Windows, use taskkill
                exec(`taskkill /PID ${server.process.pid} /F`, (error) => {
                    if (error) {
                        console.log(`Could not kill process ${server.process.pid}: ${error.message}`);
                    }
                });
            } else {
                server.process.kill();
            }
            this.servers.delete(port);
            this.availablePorts.add(port);
            console.log(`Server on port ${port} stopped.`);
        } else {
            console.log(`No server found on port ${port}.`);
        }
    }

    listServers() {
        console.log('\n=== Running Servers ===');
        if (this.servers.size === 0) {
            console.log('No servers running.');
        } else {
            this.servers.forEach((server, port) => {
                const uptime = Math.floor((new Date() - server.startTime) / 1000);
                console.log(`Port ${port}: ${server.name} (${server.type}) - Uptime: ${uptime}s - ${server.directory}`);
            });
        }
        console.log('======================\n');
    }

    async startServer() {
        console.log('\n=== Start New Server ===');
        console.log('1. Node.js Server');
        console.log('2. PHP Server');
        
        const choice = await this.question('Choose server type (1-2): ');
        const name = await this.question('Enter server name: ');
        const directory = await this.question('Enter directory path: ');
        
        if (!fs.existsSync(directory)) {
            console.log('Directory does not exist. Creating...');
            fs.mkdirSync(directory, { recursive: true });
        }

        const port = this.getNextAvailablePort();
        if (!port) {
            console.log('No available ports. Maximum of 10 servers allowed.');
            return;
        }

        try {
            if (choice === '1') {
                await this.startNodeServer(name, port, directory);
                console.log(`Node.js server "${name}" started on port ${port}`);
            } else if (choice === '2') {
                this.createPHPTemplate(directory);
                await this.startPHPServer(name, port, directory);
                console.log(`PHP server "${name}" started on port ${port}`);
            } else {
                console.log('Invalid choice.');
            }
        } catch (error) {
            console.error('Error starting server:', error.message);
        }
    }

    question(prompt) {
        return new Promise((resolve) => {
            this.rl.question(prompt, resolve);
        });
    }

    async showMenu() {
        console.log('\n=== Professional Server Manager ===');
        console.log('1. Start new server');
        console.log('2. Stop server');
        console.log('3. List running servers');
        console.log('4. Stop all servers');
        console.log('5. Open web interface');
        console.log('6. Exit');
        
        const choice = await this.question('Choose option (1-6): ');
        
        switch (choice) {
            case '1':
                await this.startServer();
                break;
            case '2':
                const port = await this.question('Enter port number to stop: ');
                this.stopServer(parseInt(port));
                break;
            case '3':
                this.listServers();
                break;
            case '4':
                this.servers.forEach((server, port) => {
                    this.stopServer(port);
                });
                console.log('All servers stopped.');
                break;
            case '5':
                this.openWebInterface();
                break;
            case '6':
                console.log('Stopping all servers...');
                this.servers.forEach((server) => {
                    this.stopServer(server.port);
                });
                this.rl.close();
                process.exit(0);
                break;
            default:
                console.log('Invalid choice.');
        }
        
        if (choice !== '6') {
            await this.showMenu();
        }
    }

    openWebInterface() {
        const indexPath = path.join(__dirname, 'index.html');
        if (fs.existsSync(indexPath)) {
            if (this.isWindows) {
                exec(`start ${indexPath}`);
            } else {
                exec(`xdg-open ${indexPath}`);
            }
            console.log('Web interface opened in your default browser.');
        } else {
            console.log('Web interface not found. Please ensure index.html exists.');
        }
    }

    async run() {
        console.log('🚀 Professional Server Manager for Windows');
        console.log('Manage up to 10 local servers simultaneously');
        console.log('Supports Node.js and PHP servers');
        console.log(`Platform: ${os.platform()} ${os.arch()}`);
        
        // Handle process termination
        process.on('SIGINT', () => {
            console.log('\nShutting down all servers...');
            this.servers.forEach((server) => {
                this.stopServer(server.port);
            });
            this.rl.close();
            process.exit(0);
        });

        await this.showMenu();
    }
}

// Run the server manager
const manager = new WindowsServerManager();
manager.run().catch(console.error);