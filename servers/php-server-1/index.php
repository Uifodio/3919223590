<?php
$serverInfo = [
    'type' => 'PHP Built-in Server',
    'version' => phpversion(),
    'status' => 'Running',
    'started' => date('Y-m-d H:i:s'),
    'document_root' => __DIR__,
    'request_uri' => $_SERVER['REQUEST_URI'] ?? '/',
    'server_software' => $_SERVER['SERVER_SOFTWARE'] ?? 'PHP Built-in Server',
    'memory_limit' => ini_get('memory_limit'),
    'max_execution_time' => ini_get('max_execution_time'),
    'upload_max_filesize' => ini_get('upload_max_filesize'),
    'post_max_size' => ini_get('post_max_size')
];

$extensions = get_loaded_extensions();
$importantExtensions = ['curl', 'gd', 'mbstring', 'mysql', 'xml', 'zip', 'json', 'bcmath', 'intl'];
$loadedImportant = array_intersect($importantExtensions, $extensions);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PHP Server 1 - Professional Server Manager</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        h1 {
            font-size: 3rem;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            font-size: 1.2rem;
            margin-bottom: 30px;
            opacity: 0.9;
        }
        
        .status {
            display: inline-block;
            padding: 8px 16px;
            background: rgba(34, 197, 94, 0.2);
            border: 1px solid rgba(34, 197, 94, 0.5);
            border-radius: 20px;
            font-weight: 600;
            margin: 20px 0;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .info-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: left;
        }
        
        .info-card h3 {
            margin-bottom: 10px;
            color: #fff;
            font-size: 1.1rem;
        }
        
        .info-card p {
            opacity: 0.8;
            font-size: 0.9rem;
        }
        
        .extensions {
            background: rgba(0, 0, 0, 0.2);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            text-align: left;
        }
        
        .extensions h3 {
            margin-bottom: 15px;
            text-align: center;
        }
        
        .extension-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }
        
        .extension {
            background: rgba(255, 255, 255, 0.1);
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.9rem;
            text-align: center;
        }
        
        .time {
            font-size: 0.9rem;
            opacity: 0.7;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐘 PHP Server 1</h1>
        <p class="subtitle">Professional Server Manager - PHP Development Environment</p>
        
        <div class="status">🟢 RUNNING</div>
        
        <div class="info-grid">
            <?php foreach($serverInfo as $key => $value): ?>
                <div class="info-card">
                    <h3><?= ucfirst(str_replace('_', ' ', $key)) ?></h3>
                    <p><?= htmlspecialchars($value) ?></p>
                </div>
            <?php endforeach; ?>
        </div>
        
        <div class="extensions">
            <h3>Loaded Extensions (<?= count($extensions) ?> total)</h3>
            <div class="extension-list">
                <?php foreach($extensions as $ext): ?>
                    <div class="extension"><?= $ext ?></div>
                <?php endforeach; ?>
            </div>
        </div>
        
        <div class="extensions">
            <h3>Important Extensions Status</h3>
            <div class="extension-list">
                <?php foreach($importantExtensions as $ext): ?>
                    <div class="extension" style="background: <?= in_array($ext, $loadedImportant) ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)' ?>;">
                        <?= $ext ?> <?= in_array($ext, $loadedImportant) ? '✓' : '✗' ?>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
        
        <div class="time">
            Server started at: <?= date('Y-m-d H:i:s') ?>
        </div>
    </div>
</body>
</html>