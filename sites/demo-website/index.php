<?php
// Professional Server Admin - PHP Demo
$server_info = [
    'php_version' => phpversion(),
    'server_software' => $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown',
    'document_root' => $_SERVER['DOCUMENT_ROOT'] ?? 'Unknown',
    'request_time' => date('Y-m-d H:i:s', $_SERVER['REQUEST_TIME']),
    'memory_usage' => memory_get_usage(true),
    'memory_peak' => memory_get_peak_usage(true),
    'loaded_extensions' => get_loaded_extensions()
];

function formatBytes($bytes, $precision = 2) {
    $units = array('B', 'KB', 'MB', 'GB', 'TB');
    for ($i = 0; $bytes > 1024 && $i < count($units) - 1; $i++) {
        $bytes /= 1024;
    }
    return round($bytes, $precision) . ' ' . $units[$i];
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PHP Demo - Professional Server Admin</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            color: #f0f6fc;
            min-height: 100vh;
            padding: 2rem;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .logo {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(45deg, #238636, #2f81f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            color: #8b949e;
            font-size: 1.1rem;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .info-card {
            background: rgba(33, 38, 45, 0.5);
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 1.5rem;
        }
        
        .info-card h3 {
            color: #2f81f7;
            margin-bottom: 1rem;
            font-size: 1.25rem;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #21262d;
        }
        
        .info-item:last-child {
            border-bottom: none;
        }
        
        .info-label {
            color: #8b949e;
            font-weight: 500;
        }
        
        .info-value {
            color: #f0f6fc;
            font-family: 'Monaco', 'Menlo', monospace;
        }
        
        .extensions {
            background: rgba(33, 38, 45, 0.5);
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .extensions h3 {
            color: #2f81f7;
            margin-bottom: 1rem;
            font-size: 1.25rem;
        }
        
        .extension-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 0.5rem;
        }
        
        .extension {
            background: rgba(47, 129, 247, 0.1);
            border: 1px solid rgba(47, 129, 247, 0.2);
            border-radius: 6px;
            padding: 0.5rem;
            text-align: center;
            font-size: 0.9rem;
            color: #58a6ff;
        }
        
        .actions {
            text-align: center;
        }
        
        .btn {
            display: inline-block;
            background: linear-gradient(45deg, #238636, #2f81f7);
            color: white;
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            margin: 0 0.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(47, 129, 247, 0.3);
        }
        
        .status {
            background: rgba(35, 134, 54, 0.1);
            border: 1px solid rgba(35, 134, 54, 0.2);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            color: #238636;
            margin-top: 2rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🐘</div>
            <h1>PHP Server Demo</h1>
            <p class="subtitle">Professional Server Admin - PHP Integration Working</p>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>Server Information</h3>
                <div class="info-item">
                    <span class="info-label">PHP Version:</span>
                    <span class="info-value"><?php echo $server_info['php_version']; ?></span>
                </div>
                <div class="info-item">
                    <span class="info-label">Server Software:</span>
                    <span class="info-value"><?php echo $server_info['server_software']; ?></span>
                </div>
                <div class="info-item">
                    <span class="info-label">Document Root:</span>
                    <span class="info-value"><?php echo $server_info['document_root']; ?></span>
                </div>
                <div class="info-item">
                    <span class="info-label">Request Time:</span>
                    <span class="info-value"><?php echo $server_info['request_time']; ?></span>
                </div>
            </div>
            
            <div class="info-card">
                <h3>Memory Usage</h3>
                <div class="info-item">
                    <span class="info-label">Current Usage:</span>
                    <span class="info-value"><?php echo formatBytes($server_info['memory_usage']); ?></span>
                </div>
                <div class="info-item">
                    <span class="info-label">Peak Usage:</span>
                    <span class="info-value"><?php echo formatBytes($server_info['memory_peak']); ?></span>
                </div>
                <div class="info-item">
                    <span class="info-label">Memory Limit:</span>
                    <span class="info-value"><?php echo ini_get('memory_limit'); ?></span>
                </div>
                <div class="info-item">
                    <span class="info-label">Max Execution Time:</span>
                    <span class="info-value"><?php echo ini_get('max_execution_time'); ?>s</span>
                </div>
            </div>
        </div>
        
        <div class="extensions">
            <h3>Loaded PHP Extensions (<?php echo count($server_info['loaded_extensions']); ?>)</h3>
            <div class="extension-list">
                <?php foreach (array_slice($server_info['loaded_extensions'], 0, 20) as $ext): ?>
                    <div class="extension"><?php echo $ext; ?></div>
                <?php endforeach; ?>
                <?php if (count($server_info['loaded_extensions']) > 20): ?>
                    <div class="extension">... and <?php echo count($server_info['loaded_extensions']) - 20; ?> more</div>
                <?php endif; ?>
            </div>
        </div>
        
        <div class="actions">
            <a href="/" class="btn">Back to Dashboard</a>
            <a href="index.html" class="btn">View HTML Demo</a>
        </div>
        
        <div class="status">
            ✅ PHP server is running successfully! This demonstrates the PHP integration capabilities.
        </div>
    </div>
</body>
</html>