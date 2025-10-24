<?php
// Demo PHP file for Unified Server Administrator
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PHP Demo - Unified Server Admin</title>
    <style>
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            margin: 0;
            padding: 2rem;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 3rem;
            border-radius: 1rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 600px;
        }
        h1 {
            color: #333;
            margin-bottom: 1rem;
        }
        .info {
            background: #e3f2fd;
            color: #1565c0;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #bbdefb;
            margin: 1rem 0;
        }
        .success {
            background: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #c3e6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐘 PHP Demo Site Running!</h1>
        <div class="success">
            <strong>✅ PHP is working!</strong> This site is served via PHP-FPM through nginx!
        </div>
        
        <div class="info">
            <h3>PHP Information:</h3>
            <p><strong>PHP Version:</strong> <?php echo phpversion(); ?></p>
            <p><strong>Server Software:</strong> <?php echo $_SERVER['SERVER_SOFTWARE'] ?? 'Nginx'; ?></p>
            <p><strong>Document Root:</strong> <?php echo $_SERVER['DOCUMENT_ROOT']; ?></p>
            <p><strong>Request Time:</strong> <?php echo date('Y-m-d H:i:s'); ?></p>
        </div>
        
        <p>This demonstrates the PHP processing capability of the unified system with php-fpm integration.</p>
    </div>
</body>
</html>