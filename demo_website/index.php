<?php
// Modern Server Administrator - PHP Demo
$page_title = "PHP Server Demo";
$server_info = [
    'php_version' => phpversion(),
    'server_software' => $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown',
    'document_root' => $_SERVER['DOCUMENT_ROOT'] ?? 'Unknown',
    'request_uri' => $_SERVER['REQUEST_URI'] ?? 'Unknown',
    'request_method' => $_SERVER['REQUEST_METHOD'] ?? 'Unknown',
    'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'Unknown',
    'remote_addr' => $_SERVER['REMOTE_ADDR'] ?? 'Unknown',
    'server_time' => date('Y-m-d H:i:s'),
    'timezone' => date_default_timezone_get()
];
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $page_title; ?></title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        
        .container {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid #334155;
            border-radius: 1rem;
            padding: 3rem;
            max-width: 800px;
            width: 100%;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            backdrop-filter: blur(10px);
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(45deg, #6366f1, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
        }
        
        .header p {
            font-size: 1.25rem;
            color: #cbd5e1;
            margin-bottom: 2rem;
        }
        
        .status-badge {
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 0.875rem;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .info-section h3 {
            color: #6366f1;
            margin-bottom: 1rem;
            font-size: 1.25rem;
            font-weight: 600;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid #334155;
        }
        
        .info-item:last-child {
            border-bottom: none;
        }
        
        .info-label {
            color: #94a3b8;
            font-weight: 500;
        }
        
        .info-value {
            color: #f8fafc;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.875rem;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-top: 3rem;
        }
        
        .feature {
            background: rgba(51, 65, 85, 0.5);
            border: 1px solid #475569;
            border-radius: 0.75rem;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .feature:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        
        .feature i {
            font-size: 2rem;
            color: #6366f1;
            margin-bottom: 1rem;
        }
        
        .feature h4 {
            color: #f8fafc;
            margin-bottom: 0.5rem;
            font-size: 1.125rem;
            font-weight: 600;
        }
        
        .feature p {
            color: #cbd5e1;
            font-size: 0.875rem;
        }
        
        .footer {
            text-align: center;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #334155;
            color: #64748b;
        }
    </style>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-server"></i> PHP Server Demo</h1>
            <p>Your PHP server is running successfully!</p>
            <span class="status-badge">Active</span>
        </div>
        
        <div class="info-grid">
            <div class="info-section">
                <h3><i class="fas fa-info-circle"></i> Server Information</h3>
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
                    <span class="info-label">Request URI:</span>
                    <span class="info-value"><?php echo $server_info['request_uri']; ?></span>
                </div>
            </div>
            
            <div class="info-section">
                <h3><i class="fas fa-clock"></i> Request Details</h3>
                <div class="info-item">
                    <span class="info-label">Method:</span>
                    <span class="info-value"><?php echo $server_info['request_method']; ?></span>
                </div>
                <div class="info-item">
                    <span class="info-label">Remote IP:</span>
                    <span class="info-value"><?php echo $server_info['remote_addr']; ?></span>
                </div>
                <div class="info-item">
                    <span class="info-label">Server Time:</span>
                    <span class="info-value"><?php echo $server_info['server_time']; ?></span>
                </div>
                <div class="info-item">
                    <span class="info-label">Timezone:</span>
                    <span class="info-value"><?php echo $server_info['timezone']; ?></span>
                </div>
            </div>
        </div>
        
        <div class="features">
            <div class="feature">
                <i class="fas fa-bolt"></i>
                <h4>Fast Performance</h4>
                <p>Lightning fast PHP server with optimized performance</p>
            </div>
            <div class="feature">
                <i class="fas fa-shield-alt"></i>
                <h4>Secure</h4>
                <p>Built-in security features and error handling</p>
            </div>
            <div class="feature">
                <i class="fas fa-code"></i>
                <h4>Modern PHP</h4>
                <p>Latest PHP features and best practices</p>
            </div>
            <div class="feature">
                <i class="fas fa-tools"></i>
                <h4>Easy Development</h4>
                <p>Perfect for development and testing</p>
            </div>
        </div>
        
        <div class="footer">
            <p>Powered by Modern Server Administrator</p>
        </div>
    </div>
</body>
</html>