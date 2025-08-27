const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const os = require('os');

console.log('🔍 Unity Code Editor - System Diagnostic');
console.log('==========================================\n');

const diagnostic = {
    system: {},
    dependencies: {},
    permissions: {},
    errors: [],
    warnings: []
};

// Check system information
function checkSystem() {
    console.log('📋 Checking System Information...');
    
    diagnostic.system = {
        platform: os.platform(),
        arch: os.arch(),
        version: os.release(),
        totalMemory: Math.round(os.totalmem() / (1024 * 1024 * 1024)),
        freeMemory: Math.round(os.freemem() / (1024 * 1024 * 1024)),
        cpus: os.cpus().length,
        hostname: os.hostname(),
        userInfo: os.userInfo()
    };
    
    console.log(`✅ Platform: ${diagnostic.system.platform}`);
    console.log(`✅ Architecture: ${diagnostic.system.arch}`);
    console.log(`✅ Windows Version: ${diagnostic.system.version}`);
    console.log(`✅ Total RAM: ${diagnostic.system.totalMemory}GB`);
    console.log(`✅ Available RAM: ${diagnostic.system.freeMemory}GB`);
    console.log(`✅ CPU Cores: ${diagnostic.system.cpus}`);
    
    // Check if it's Windows 11
    if (diagnostic.system.platform === 'win32') {
        const version = diagnostic.system.version;
        if (version.includes('10.0.2') || parseInt(version.split('.')[2]) >= 22000) {
            console.log('✅ Windows 11 detected');
        } else {
            diagnostic.warnings.push('Windows 10 detected - Windows 11 recommended for best performance');
        }
    } else {
        diagnostic.errors.push('This app is designed for Windows. Current platform: ' + diagnostic.system.platform);
    }
}

// Check Node.js
function checkNodeJS() {
    console.log('\n📋 Checking Node.js...');
    
    try {
        const nodeVersion = execSync('node --version', { encoding: 'utf8' }).trim();
        const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
        
        diagnostic.dependencies.nodejs = {
            version: nodeVersion,
            npmVersion: npmVersion,
            installed: true
        };
        
        console.log(`✅ Node.js: ${nodeVersion}`);
        console.log(`✅ npm: ${npmVersion}`);
        
        // Check if version is recent enough
        const majorVersion = parseInt(nodeVersion.replace('v', '').split('.')[0]);
        if (majorVersion < 16) {
            diagnostic.warnings.push('Node.js version should be 16 or higher for best compatibility');
        }
        
    } catch (error) {
        diagnostic.dependencies.nodejs = { installed: false };
        diagnostic.errors.push('Node.js not found or not accessible');
        console.log('❌ Node.js not found');
    }
}

// Check Git
function checkGit() {
    console.log('\n📋 Checking Git...');
    
    try {
        const gitVersion = execSync('git --version', { encoding: 'utf8' }).trim();
        diagnostic.dependencies.git = {
            version: gitVersion,
            installed: true
        };
        
        console.log(`✅ Git: ${gitVersion}`);
        
    } catch (error) {
        diagnostic.dependencies.git = { installed: false };
        diagnostic.warnings.push('Git not found - some features may be limited');
        console.log('⚠️ Git not found (optional)');
    }
}

// Check Python
function checkPython() {
    console.log('\n📋 Checking Python...');
    
    try {
        const pythonVersion = execSync('python --version', { encoding: 'utf8' }).trim();
        diagnostic.dependencies.python = {
            version: pythonVersion,
            installed: true
        };
        
        console.log(`✅ Python: ${pythonVersion}`);
        
    } catch (error) {
        try {
            const pythonVersion = execSync('python3 --version', { encoding: 'utf8' }).trim();
            diagnostic.dependencies.python = {
                version: pythonVersion,
                installed: true
            };
            console.log(`✅ Python: ${pythonVersion}`);
        } catch (error2) {
            diagnostic.dependencies.python = { installed: false };
            console.log('⚠️ Python not found (optional)');
        }
    }
}

// Check .NET
function checkDotNet() {
    console.log('\n📋 Checking .NET...');
    
    try {
        const dotnetVersion = execSync('dotnet --version', { encoding: 'utf8' }).trim();
        diagnostic.dependencies.dotnet = {
            version: dotnetVersion,
            installed: true
        };
        
        console.log(`✅ .NET: ${dotnetVersion}`);
        
    } catch (error) {
        diagnostic.dependencies.dotnet = { installed: false };
        console.log('⚠️ .NET not found (optional for Unity integration)');
    }
}

// Check file permissions
function checkPermissions() {
    console.log('\n📋 Checking File Permissions...');
    
    const testDir = path.join(process.cwd(), 'test-permissions');
    
    try {
        // Test directory creation
        if (!fs.existsSync(testDir)) {
            fs.mkdirSync(testDir);
        }
        
        // Test file creation
        const testFile = path.join(testDir, 'test.txt');
        fs.writeFileSync(testFile, 'test');
        
        // Test file reading
        const content = fs.readFileSync(testFile, 'utf8');
        
        // Test file deletion
        fs.unlinkSync(testFile);
        fs.rmdirSync(testDir);
        
        diagnostic.permissions = {
            canCreateDirectories: true,
            canCreateFiles: true,
            canReadFiles: true,
            canDeleteFiles: true,
            canDeleteDirectories: true
        };
        
        console.log('✅ All file permissions working correctly');
        
    } catch (error) {
        diagnostic.permissions = {
            canCreateDirectories: false,
            canCreateFiles: false,
            canReadFiles: false,
            canDeleteFiles: false,
            canDeleteDirectories: false
        };
        diagnostic.errors.push('File permission issues detected: ' + error.message);
        console.log('❌ File permission issues detected');
    }
}

// Check available disk space
function checkDiskSpace() {
    console.log('\n📋 Checking Disk Space...');
    
    try {
        const stats = fs.statfsSync(process.cwd());
        const freeSpaceGB = Math.round((stats.bavail * stats.bsize) / (1024 * 1024 * 1024));
        
        diagnostic.system.freeDiskSpace = freeSpaceGB;
        
        console.log(`✅ Available disk space: ${freeSpaceGB}GB`);
        
        if (freeSpaceGB < 1) {
            diagnostic.warnings.push('Low disk space - at least 1GB recommended');
        }
        
    } catch (error) {
        console.log('⚠️ Could not check disk space');
    }
}

// Generate report
function generateReport() {
    console.log('\n📊 Diagnostic Report');
    console.log('===================');
    
    if (diagnostic.errors.length > 0) {
        console.log('\n❌ ERRORS:');
        diagnostic.errors.forEach(error => console.log(`  - ${error}`));
    }
    
    if (diagnostic.warnings.length > 0) {
        console.log('\n⚠️ WARNINGS:');
        diagnostic.warnings.forEach(warning => console.log(`  - ${warning}`));
    }
    
    console.log('\n✅ SYSTEM READY FOR DEVELOPMENT');
    console.log('===============================');
    
    // Save diagnostic report
    const reportPath = path.join(process.cwd(), 'diagnostic-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(diagnostic, null, 2));
    console.log(`\n📄 Diagnostic report saved to: ${reportPath}`);
    
    return diagnostic.errors.length === 0;
}

// Main diagnostic function
function runDiagnostic() {
    try {
        checkSystem();
        checkNodeJS();
        checkGit();
        checkPython();
        checkDotNet();
        checkPermissions();
        checkDiskSpace();
        
        const isReady = generateReport();
        
        if (isReady) {
            console.log('\n🎉 Your system is ready! You can now build the Unity Code Editor.');
            console.log('\nNext steps:');
            console.log('1. Run: npm install');
            console.log('2. Run: npm start (to test the app)');
            console.log('3. Run: npm run build-win (to create the .exe)');
        } else {
            console.log('\n❌ Please fix the errors above before proceeding.');
        }
        
    } catch (error) {
        console.error('\n💥 Diagnostic failed:', error.message);
        process.exit(1);
    }
}

// Run the diagnostic
runDiagnostic();