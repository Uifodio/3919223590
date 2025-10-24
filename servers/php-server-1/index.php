<?php
$serverInfo = [
    'type' => 'PHP Built-in Server',
    'version' => phpversion(),
    'status' => 'Running',
    'started' => date('Y-m-d H:i:s'),
    'document_root' => __DIR__,
    'request_uri' => $_SERVER['REQUEST_URI'] ?? '/',
    'server_software' => $_SERVER['SERVER_SOFTWARE'] ?? 'PHP Built-in Server'
];
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PHP Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        h1 { text-align: center; margin-bottom: 30px; }
        .info { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; margin: 10px 0; }
        .php-info { background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐘 PHP Server Running!</h1>
        <div class="info">
            <h3>Server Information</h3>
            <?php foreach($serverInfo as $key => $value): ?>
                <p><strong><?= ucfirst(str_replace('_', ' ', $key)) ?>:</strong> <?= htmlspecialchars($value) ?></p>
            <?php endforeach; ?>
        </div>
        <div class="php-info">
            <h3>PHP Extensions</h3>
            <p><?= implode(', ', get_loaded_extensions()) ?></p>
        </div>
        <div class="info">
            <h3>Features</h3>
            <ul>
                <li>PHP 8.4+ support</li>
                <li>Built-in development server</li>
                <li>All major extensions loaded</li>
                <li>Error reporting enabled</li>
            </ul>
        </div>
    </div>
</body>
</html>
