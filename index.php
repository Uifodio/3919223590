<?php
declare(strict_types=1);

// Single-file app: Auth, SQLite, Chat, Uploads, AI proxy, Responsive UI
// NOTE: Ensure the web server has write permissions to `data/` and `uploads/`.

session_start();

// ---------- Configuration ----------
$DB_PATH = __DIR__ . '/data/app.db';
$UPLOAD_DIR = __DIR__ . '/uploads';
$MAX_UPLOAD_BYTES = 25 * 1024 * 1024; // 25 MB
$ALLOWED_MIME_PREFIXES = ['image/', 'video/', 'audio/'];

// Koldbold AI config (user can set in Settings UI)
if (!isset($_SESSION['ai_config'])) {
    $_SESSION['ai_config'] = [
        'base_url' => '', // e.g., http://localhost:11434 or remote
        'api_key' => '',  // optional
        'model' => 'med-chat', // default example
    ];
}

// ---------- Utility ----------
function json_response(int $status, array $payload): void {
    http_response_code($status);
    header('Content-Type: application/json');
    echo json_encode($payload);
    exit;
}

function require_post(): void {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        json_response(405, ['error' => 'Method Not Allowed']);
    }
}

function require_json(): array {
    $raw = file_get_contents('php://input');
    $data = json_decode($raw, true);
    if (!is_array($data)) {
        json_response(400, ['error' => 'Invalid JSON body']);
    }
    return $data;
}

function ensure_dirs(string $dbPath, string $uploadDir): void {
    $dirs = [dirname($dbPath), $uploadDir];
    foreach ($dirs as $d) {
        if (!is_dir($d)) {
            @mkdir($d, 0775, true);
        }
    }
}

function get_db(string $dbPath): PDO {
    static $pdo = null;
    if ($pdo instanceof PDO) return $pdo;
    ensure_dirs($dbPath, __DIR__ . '/uploads');
    $pdo = new PDO('sqlite:' . $dbPath);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    // Pragmas for basic integrity/perf
    $pdo->exec('PRAGMA journal_mode = wal;');
    $pdo->exec('PRAGMA foreign_keys = ON;');
    init_schema($pdo);
    return $pdo;
}

function init_schema(PDO $pdo): void {
    $pdo->exec('CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    )');

    $pdo->exec('CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        recipient_id INTEGER NOT NULL,
        body TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(sender_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(recipient_id) REFERENCES users(id) ON DELETE CASCADE
    )');

    $pdo->exec('CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id INTEGER NOT NULL,
        filepath TEXT NOT NULL,
        mime_type TEXT NOT NULL,
        size_bytes INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(message_id) REFERENCES messages(id) ON DELETE CASCADE
    )');

    // Helpful indexes
    $pdo->exec('CREATE INDEX IF NOT EXISTS idx_messages_pair ON messages(sender_id, recipient_id)');
    $pdo->exec('CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at)');
}

function now_iso(): string {
    return (new DateTimeImmutable('now', new DateTimeZone('UTC')))->format(DateTimeInterface::ATOM);
}

function current_user_id(): ?int {
    return isset($_SESSION['uid']) ? intval($_SESSION['uid']) : null;
}

function ensure_csrf_token(): void {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
}

function validate_csrf_from_post(): void {
    $token = $_POST['csrf_token'] ?? '';
    if (!hash_equals($_SESSION['csrf_token'] ?? '', $token)) {
        json_response(403, ['error' => 'Invalid CSRF token']);
    }
}

function validate_csrf_from_json(array $data): void {
    $token = $data['csrf_token'] ?? '';
    if (!hash_equals($_SESSION['csrf_token'] ?? '', $token)) {
        json_response(403, ['error' => 'Invalid CSRF token']);
    }
}

// ---------- Auth Handlers ----------
function handle_register(PDO $db): void {
    require_post();
    validate_csrf_from_post();
    $username = trim((string)($_POST['username'] ?? ''));
    $password = (string)($_POST['password'] ?? '');
    if ($username === '' || $password === '') {
        json_response(400, ['error' => 'Username and password required']);
    }
    if (!preg_match('/^[A-Za-z0-9_\-\.]{3,32}$/', $username)) {
        json_response(400, ['error' => 'Username must be 3-32 chars [A-Za-z0-9_.-]']);
    }
    $passwordHash = password_hash($password, PASSWORD_DEFAULT);
    try {
        $stmt = $db->prepare('INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)');
        $stmt->execute([$username, $passwordHash, now_iso()]);
        $_SESSION['uid'] = intval($db->lastInsertId());
        $_SESSION['username'] = $username;
        json_response(200, ['ok' => true]);
    } catch (Throwable $e) {
        if (str_contains(strtolower($e->getMessage()), 'unique')) {
            json_response(409, ['error' => 'Username already exists']);
        }
        json_response(500, ['error' => 'Registration failed']);
    }
}

function handle_login(PDO $db): void {
    require_post();
    validate_csrf_from_post();
    $username = trim((string)($_POST['username'] ?? ''));
    $password = (string)($_POST['password'] ?? '');
    $stmt = $db->prepare('SELECT id, password_hash FROM users WHERE username = ?');
    $stmt->execute([$username]);
    $user = $stmt->fetch();
    if (!$user || !password_verify($password, (string)$user['password_hash'])) {
        json_response(401, ['error' => 'Invalid credentials']);
    }
    $_SESSION['uid'] = intval($user['id']);
    $_SESSION['username'] = $username;
    json_response(200, ['ok' => true]);
}

function handle_logout(): void {
    require_post();
    validate_csrf_from_post();
    session_destroy();
    json_response(200, ['ok' => true]);
}

// ---------- Chat Handlers ----------
function list_conversations(PDO $db, int $uid): void {
    // Aggregate pairs where current user is either sender or recipient, order by last message time
    $sql = 'WITH pairs AS (
                SELECT CASE WHEN sender_id = :uid THEN recipient_id ELSE sender_id END AS other_id,
                       MAX(created_at) AS last_time
                FROM messages
                WHERE sender_id = :uid OR recipient_id = :uid
                GROUP BY other_id
            )
            SELECT p.other_id, u.username AS other_username, p.last_time
            FROM pairs p
            LEFT JOIN users u ON u.id = p.other_id
            ORDER BY p.last_time DESC NULLS LAST';
    $stmt = $db->prepare($sql);
    $stmt->execute([':uid' => $uid]);
    $rows = $stmt->fetchAll();
    json_response(200, ['conversations' => $rows]);
}

function fetch_messages(PDO $db, int $uid): void {
    $data = require_json();
    validate_csrf_from_json($data);
    $otherId = intval($data['other_id'] ?? 0);
    $sinceId = isset($data['since_id']) ? intval($data['since_id']) : 0;
    $stmt = $db->prepare('SELECT m.id, m.sender_id, m.recipient_id, m.body, m.created_at,
                                 a.filepath, a.mime_type, a.size_bytes
                          FROM messages m
                          LEFT JOIN attachments a ON a.message_id = m.id
                          WHERE ((m.sender_id = :uid AND m.recipient_id = :other)
                                 OR (m.sender_id = :other AND m.recipient_id = :uid))
                                AND m.id > :since
                          ORDER BY m.id ASC');
    $stmt->execute([':uid' => $uid, ':other' => $otherId, ':since' => $sinceId]);
    $rows = $stmt->fetchAll();
    json_response(200, ['messages' => $rows]);
}

function send_message(PDO $db, int $uid): void {
    $data = require_json();
    validate_csrf_from_json($data);
    $otherId = intval($data['other_id'] ?? 0);
    $body = trim((string)($data['body'] ?? ''));
    if ($otherId <= 0) json_response(400, ['error' => 'other_id required']);
    if ($body === '' && empty($data['attachment'])) json_response(400, ['error' => 'Message empty']);
    // Ensure other user exists (self chat allowed)
    $u = $db->prepare('SELECT id FROM users WHERE id = ?');
    $u->execute([$otherId]);
    if (!$u->fetch()) json_response(404, ['error' => 'Recipient not found']);

    $db->beginTransaction();
    try {
        $stmt = $db->prepare('INSERT INTO messages (sender_id, recipient_id, body, created_at) VALUES (?, ?, ?, ?)');
        $stmt->execute([$uid, $otherId, $body !== '' ? $body : null, now_iso()]);
        $mid = intval($db->lastInsertId());

        if (!empty($data['attachment'])) {
            // attachment is not handled in this route; uploads use multipart form to /?action=upload
        }

        $db->commit();
        json_response(200, ['ok' => true, 'message_id' => $mid]);
    } catch (Throwable $e) {
        $db->rollBack();
        json_response(500, ['error' => 'Failed to send message']);
    }
}

function upload_attachment(PDO $db, int $uid): void {
    // Multipart POST: fields -> csrf_token, other_id, attach_for_message(optional)
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        json_response(405, ['error' => 'Method Not Allowed']);
    }
    validate_csrf_from_post();
    $otherId = intval($_POST['other_id'] ?? 0);
    if ($otherId <= 0) json_response(400, ['error' => 'other_id required']);

    if (!isset($_FILES['file'])) {
        json_response(400, ['error' => 'No file']);
    }
    $file = $_FILES['file'];
    if (($file['error'] ?? UPLOAD_ERR_OK) !== UPLOAD_ERR_OK) {
        json_response(400, ['error' => 'Upload error']);
    }
    if (($file['size'] ?? 0) > $GLOBALS['MAX_UPLOAD_BYTES']) {
        json_response(413, ['error' => 'File too large']);
    }

    $finfo = new finfo(FILEINFO_MIME_TYPE);
    $mime = $finfo->file($file['tmp_name']);
    $allowed = false;
    foreach ($GLOBALS['ALLOWED_MIME_PREFIXES'] as $prefix) {
        if (str_starts_with((string)$mime, $prefix)) { $allowed = true; break; }
    }
    if (!$allowed) {
        json_response(415, ['error' => 'Unsupported media type']);
    }

    // Create message first (empty body with attachment)
    $stmt = $db->prepare('INSERT INTO messages (sender_id, recipient_id, body, created_at) VALUES (?, ?, NULL, ?)');
    $stmt->execute([$uid, $otherId, now_iso()]);
    $mid = intval($db->lastInsertId());

    // Persist file
    $ext = pathinfo((string)$file['name'], PATHINFO_EXTENSION);
    $safeBase = bin2hex(random_bytes(8));
    $destRel = $safeBase . ($ext ? ('.' . preg_replace('/[^A-Za-z0-9]/', '', $ext)) : '');
    $destAbs = rtrim($GLOBALS['UPLOAD_DIR'], '/\\') . DIRECTORY_SEPARATOR . $destRel;
    if (!move_uploaded_file($file['tmp_name'], $destAbs)) {
        json_response(500, ['error' => 'Failed to save file']);
    }

    $stmtA = $db->prepare('INSERT INTO attachments (message_id, filepath, mime_type, size_bytes, created_at) VALUES (?, ?, ?, ?, ?)');
    $stmtA->execute([$mid, 'uploads/' . $destRel, (string)$mime, intval($file['size']), now_iso()]);

    json_response(200, ['ok' => true, 'message_id' => $mid]);
}

// ---------- AI Proxy (Stub) ----------
function ai_proxy(): void {
    $data = require_json();
    validate_csrf_from_json($data);
    $prompt = trim((string)($data['prompt'] ?? ''));
    $config = $_SESSION['ai_config'] ?? [];
    $base = (string)($config['base_url'] ?? '');
    $model = (string)($config['model'] ?? 'med-chat');
    $key = (string)($config['api_key'] ?? '');

    if ($base === '') {
        // Local fallback stub
        json_response(200, ['ok' => true, 'model' => $model, 'answer' => 'AI (stub): ' . ($prompt !== '' ? $prompt : 'Hello! Configure base URL to use Koldbold.')]);
    }

    // Example proxy call (simple sync). Adjust path to Koldbold API.
    $url = rtrim($base, '/');
    $endpoint = $url . '/v1/chat/completions';
    $ch = curl_init($endpoint);
    $payload = json_encode([
        'model' => $model,
        'messages' => [
            ['role' => 'user', 'content' => $prompt],
        ],
        'stream' => false,
    ]);
    $headers = ['Content-Type: application/json'];
    if ($key !== '') { $headers[] = 'Authorization: Bearer ' . $key; }
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_TIMEOUT => 30,
    ]);
    $resp = curl_exec($ch);
    $err = curl_error($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    if ($resp === false) {
        json_response(502, ['error' => 'AI proxy error: ' . $err]);
    }
    $body = json_decode((string)$resp, true);
    if (!is_array($body) || $code >= 400) {
        json_response(502, ['error' => 'AI proxy bad response', 'status' => $code]);
    }
    $answer = $body['choices'][0]['message']['content'] ?? 'No response';
    json_response(200, ['ok' => true, 'model' => $model, 'answer' => $answer]);
}

// ---------- Settings ----------
function save_settings(): void {
    $data = require_json();
    validate_csrf_from_json($data);
    $base = trim((string)($data['base_url'] ?? ''));
    $key = trim((string)($data['api_key'] ?? ''));
    $model = trim((string)($data['model'] ?? 'med-chat'));
    $_SESSION['ai_config'] = [
        'base_url' => $base,
        'api_key' => $key,
        'model' => $model !== '' ? $model : 'med-chat',
    ];
    json_response(200, ['ok' => true]);
}

// ---------- Router for JSON/API actions ----------
ensure_dirs($DB_PATH, $UPLOAD_DIR);
ensure_csrf_token();
$db = get_db($DB_PATH);
$action = $_GET['action'] ?? '';

if ($action !== '') {
    $uid = current_user_id();
    switch ($action) {
        case 'register': handle_register($db); break;
        case 'login': handle_login($db); break;
        case 'logout': handle_logout(); break;
        case 'list_conversations': if ($uid) { list_conversations($db, $uid); } else { json_response(401, ['error' => 'auth']); } break;
        case 'fetch_messages': if ($uid) { fetch_messages($db, $uid); } else { json_response(401, ['error' => 'auth']); } break;
        case 'send_message': if ($uid) { send_message($db, $uid); } else { json_response(401, ['error' => 'auth']); } break;
        case 'upload': if ($uid) { upload_attachment($db, $uid); } else { json_response(401, ['error' => 'auth']); } break;
        case 'ai_proxy': if ($uid) { ai_proxy(); } else { json_response(401, ['error' => 'auth']); } break;
        case 'save_settings': if ($uid) { save_settings(); } else { json_response(401, ['error' => 'auth']); } break;
        default: json_response(404, ['error' => 'Unknown action']);
    }
}

// ---------- HTML UI ----------
$uid = current_user_id();
$username = $_SESSION['username'] ?? '';
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>HyperLink – Professional Self-Comm and Team Chat</title>
    <style>
        :root {
            --bg: #0f1521;
            --card: #151c2c;
            --elev: #1b2438;
            --text: #e7ecf4;
            --muted: #aeb7c7;
            --accent: #6aa2ff;
            --accent-2: #7ef0d1;
            --danger: #ff6a6a;
            --ok: #79e08f;
            --shadow: 0 10px 30px rgba(0,0,0,0.4);
        }
        * { box-sizing: border-box; }
        html, body { height: 100%; }
        body {
            margin: 0; background: linear-gradient(180deg, #0d1220 0%, #0b0f19 100%);
            color: var(--text); font: 15px/1.5 system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
        }
        a { color: var(--accent); text-decoration: none; }
        button, input, select, textarea { font: inherit; }
        .app {
            display: grid; height: 100vh; width: 100vw; overflow: hidden;
            grid-template-columns: 320px 1fr; grid-template-rows: 64px 1fr 64px;
            grid-template-areas:
                "sidebar header"
                "sidebar main"
                "sidebar composer";
        }
        .header {
            grid-area: header; display: flex; align-items: center; justify-content: space-between;
            padding: 0 16px; background: var(--card); border-bottom: 1px solid #24304a; box-shadow: var(--shadow);
        }
        .brand { display: flex; align-items: center; gap: 12px; font-weight: 700; letter-spacing: 0.3px; }
        .brand .logo { width: 28px; height: 28px; background: linear-gradient(135deg, var(--accent), var(--accent-2)); border-radius: 8px; box-shadow: 0 6px 16px rgba(122, 175, 255, 0.35); }
        .header .actions { display: flex; align-items: center; gap: 8px; }
        .btn { background: var(--elev); color: var(--text); border: 1px solid #2a3858; padding: 8px 12px; border-radius: 10px; cursor: pointer; }
        .btn.primary { background: linear-gradient(135deg, #4b7dff, #6aa2ff); border-color: transparent; }
        .btn.ghost { background: transparent; border-color: #2a3858; }
        .btn.danger { background: transparent; border-color: #5b2630; color: #ff9aa8; }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }

        .sidebar {
            grid-area: sidebar; display: flex; flex-direction: column; background: var(--card); border-right: 1px solid #24304a; min-width: 260px;
        }
        .sidebar .me { padding: 16px; border-bottom: 1px solid #24304a; display: flex; align-items: center; gap: 12px; }
        .avatar { width: 36px; height: 36px; border-radius: 10px; background: #24304a; display: inline-flex; align-items: center; justify-content: center; color: var(--muted); font-weight: 700; }
        .sidebar .search { padding: 12px 16px; }
        .input { width: 100%; padding: 10px 12px; border-radius: 10px; border: 1px solid #2a3858; background: #0f1521; color: var(--text); }
        .convos { overflow: auto; padding: 8px; }
        .convo { display: grid; grid-template-columns: 44px 1fr auto; gap: 10px; align-items: center; padding: 10px; border-radius: 12px; cursor: pointer; }
        .convo:hover { background: #121a2b; }
        .convo.active { background: #111a30; border: 1px solid #2a3858; }
        .convo .name { font-weight: 600; }
        .convo .time { color: var(--muted); font-size: 12px; }

        .main { grid-area: main; display: grid; grid-template-rows: auto 1fr; }
        .thread-header { padding: 12px 16px; border-bottom: 1px solid #24304a; background: var(--card); display: flex; gap: 12px; align-items: center; }
        .messages { overflow: auto; padding: 16px; display: flex; flex-direction: column; gap: 10px; background: radial-gradient(1200px 800px at 80% 10%, #10172a, transparent), linear-gradient(180deg,#0b1222 0%,#0a101a 100%); }
        .msg { max-width: 70%; padding: 10px 12px; border-radius: 12px; background: #10182a; border: 1px solid #223152; box-shadow: var(--shadow); }
        .msg.me { margin-left: auto; background: linear-gradient(135deg, #17305f, #1b2f57); border-color: #2a4477; }
        .msg .meta { color: var(--muted); font-size: 12px; margin-bottom: 6px; }
        .msg .body { white-space: pre-wrap; word-break: break-word; }
        .msg img, .msg video, .msg audio { max-width: 100%; border-radius: 10px; margin-top: 6px; }

        .composer { grid-area: composer; display: grid; grid-template-columns: auto 1fr auto auto; gap: 8px; align-items: center; padding: 10px; border-top: 1px solid #24304a; background: var(--card); }
        .composer .file { display: none; }

        .auth { max-width: 440px; margin: 8vh auto; padding: 24px; border-radius: 16px; background: var(--card); border: 1px solid #24304a; box-shadow: var(--shadow); }
        .auth h1 { margin: 0 0 12px; }
        .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .muted { color: var(--muted); }

        .settings-panel { padding: 12px 16px; border-top: 1px solid #24304a; }

        /* Responsive: phones get toggleable sidebar */
        @media (max-width: 980px) {
            .app { grid-template-columns: 1fr; grid-template-areas:
                    "header"
                    "main"
                    "composer"; }
            .sidebar { position: fixed; left: 0; top: 0; bottom: 0; width: 86%; max-width: 380px; transform: translateX(-105%); transition: transform .2s ease; z-index: 10; box-shadow: var(--shadow); }
            .sidebar.open { transform: translateX(0); }
        }
    </style>
</head>
<body>
<?php if (!$uid): ?>
    <div class="auth">
        <h1>HyperLink</h1>
        <p class="muted">Professional self-communication and team chat. Register or log in.</p>
        <form id="form-register" method="post" action="?action=register" style="margin-top:12px; display:grid; gap:8px;">
            <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($_SESSION['csrf_token']); ?>" />
            <input class="input" type="text" name="username" placeholder="Username" minlength="3" maxlength="32" required />
            <input class="input" type="password" name="password" placeholder="Password" required />
            <button class="btn primary" type="submit">Create account</button>
        </form>
        <div style="height:10px"></div>
        <form id="form-login" method="post" action="?action=login" style="display:grid; gap:8px;">
            <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($_SESSION['csrf_token']); ?>" />
            <input class="input" type="text" name="username" placeholder="Username" required />
            <input class="input" type="password" name="password" placeholder="Password" required />
            <button class="btn" type="submit">Log in</button>
        </form>
        <p id="auth-error" class="muted"></p>
    </div>
    <script>
    const authForms = ['form-register','form-login'];
    authForms.forEach(id => {
        const f = document.getElementById(id);
        f?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fd = new FormData(f);
            const res = await fetch(f.action, { method: 'POST', body: fd });
            const txt = await res.text();
            try { const j = JSON.parse(txt); if (j.ok) location.reload(); else document.getElementById('auth-error').textContent = j.error || 'Error'; } catch { document.getElementById('auth-error').textContent = 'Error'; }
        });
    });
    </script>
<?php else: ?>
    <div class="app">
        <div class="header">
            <div class="brand">
                <div class="logo"></div>
                <div>HyperLink</div>
            </div>
            <div class="actions">
                <button id="btn-sidebar" class="btn ghost">Menu</button>
                <button id="btn-ai" class="btn">AI</button>
                <form id="form-logout" method="post" action="?action=logout" style="display:inline;">
                    <input type="hidden" name="csrf_token" value="<?php echo htmlspecialchars($_SESSION['csrf_token']); ?>" />
                    <button class="btn danger">Logout</button>
                </form>
            </div>
        </div>
        <aside class="sidebar" id="sidebar">
            <div class="me">
                <div class="avatar"><?php echo strtoupper(substr($username,0,1)); ?></div>
                <div>
                    <div style="font-weight:700;">@<?php echo htmlspecialchars($username); ?></div>
                    <div class="muted" style="font-size:12px;">Online</div>
                </div>
            </div>
            <div class="search"><input id="search" class="input" placeholder="Search or start a self chat" /></div>
            <div class="convos" id="convos"></div>
            <div class="settings-panel">
                <div style="font-weight:700; margin-bottom:6px;">Settings</div>
                <div class="muted" style="font-size:12px; margin-bottom:8px;">Koldbold AI</div>
                <div style="display:grid; gap:6px;">
                    <input id="ai-base" class="input" placeholder="Base URL (e.g., http://localhost:11434)" value="<?php echo htmlspecialchars($_SESSION['ai_config']['base_url'] ?? ''); ?>" />
                    <input id="ai-model" class="input" placeholder="Model (e.g., med-chat)" value="<?php echo htmlspecialchars($_SESSION['ai_config']['model'] ?? 'med-chat'); ?>" />
                    <input id="ai-key" class="input" placeholder="API Key (optional)" value="<?php echo htmlspecialchars($_SESSION['ai_config']['api_key'] ?? ''); ?>" />
                    <button id="btn-save-settings" class="btn">Save Settings</button>
                </div>
                <div style="height:8px"></div>
                <div class="muted" style="font-size:12px;">Tip: For self-chat, just select your own username.</div>
            </div>
        </aside>
        <main class="main">
            <div class="thread-header">
                <div class="avatar" id="thread-avatar">Y</div>
                <div>
                    <div id="thread-title" style="font-weight:700;">Select a conversation</div>
                    <div id="thread-sub" class="muted" style="font-size:12px;">Self, teammates, and AI assistance</div>
                </div>
            </div>
            <div class="messages" id="messages"></div>
        </main>
        <div class="composer">
            <input id="csrf-token" type="hidden" value="<?php echo htmlspecialchars($_SESSION['csrf_token']); ?>" />
            <input id="other-id" type="hidden" />
            <button id="btn-attach" class="btn">Attach</button>
            <input id="file" class="file" type="file" accept="image/*,video/*,audio/*" />
            <input id="input" class="input" placeholder="Type a message..." />
            <button id="btn-send" class="btn primary">Send</button>
            <button id="btn-self" class="btn ghost" title="Chat with yourself">Self</button>
        </div>
    </div>
    <script>
    const csrf = document.getElementById('csrf-token').value;
    const convosEl = document.getElementById('convos');
    const messagesEl = document.getElementById('messages');
    const otherIdEl = document.getElementById('other-id');
    const inputEl = document.getElementById('input');
    const fileEl = document.getElementById('file');
    const btnAttach = document.getElementById('btn-attach');
    const btnSend = document.getElementById('btn-send');
    const btnSelf = document.getElementById('btn-self');
    const btnSidebar = document.getElementById('btn-sidebar');
    const sidebar = document.getElementById('sidebar');
    const btnAI = document.getElementById('btn-ai');
    const searchEl = document.getElementById('search');

    document.getElementById('form-logout')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        const res = await fetch('?action=logout', { method: 'POST', body: fd });
        const j = await res.json().catch(()=>({}));
        if (j.ok) location.reload();
    });

    btnSidebar?.addEventListener('click', () => sidebar.classList.toggle('open'));

    async function listConversations() {
        const res = await fetch('?action=list_conversations');
        const j = await res.json();
        convosEl.innerHTML = '';
        const items = j.conversations || [];
        const filtered = searchEl.value?.trim() ? items.filter(c => (c.other_username||'').toLowerCase().includes(searchEl.value.trim().toLowerCase())) : items;
        for (const c of filtered) {
            const el = document.createElement('div');
            el.className = 'convo';
            el.dataset.otherId = c.other_id;
            el.innerHTML = `
                <div class="avatar">${(c.other_username||'?').slice(0,1).toUpperCase()}</div>
                <div>
                    <div class="name">${c.other_username || 'You'}</div>
                    <div class="time">${new Date(c.last_time || Date.now()).toLocaleString()}</div>
                </div>
                <div></div>
            `;
            el.addEventListener('click', () => selectConversation(c.other_id, c.other_username || 'You'));
            convosEl.appendChild(el);
        }
    }

    let lastId = 0;
    let pollHandle = null;

    function renderMessage(m, myId) {
        const isMe = m.sender_id == myId;
        const div = document.createElement('div');
        div.className = 'msg' + (isMe ? ' me' : '');
        const meta = document.createElement('div'); meta.className = 'meta';
        meta.textContent = new Date(m.created_at).toLocaleString();
        const body = document.createElement('div'); body.className = 'body'; body.textContent = m.body || '';
        div.appendChild(meta); if (m.body) div.appendChild(body);
        if (m.filepath) {
            if ((m.mime_type||'').startsWith('image/')) {
                const img = document.createElement('img'); img.src = m.filepath; div.appendChild(img);
            } else if ((m.mime_type||'').startsWith('video/')) {
                const v = document.createElement('video'); v.src = m.filepath; v.controls = true; div.appendChild(v);
            } else if ((m.mime_type||'').startsWith('audio/')) {
                const a = document.createElement('audio'); a.src = m.filepath; a.controls = true; div.appendChild(a);
            } else {
                const link = document.createElement('a'); link.href = m.filepath; link.textContent = 'Attachment'; link.target = '_blank'; div.appendChild(link);
            }
        }
        return div;
    }

    async function fetchMessages(otherId) {
        const res = await fetch('?action=fetch_messages', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ csrf_token: csrf, other_id: otherId, since_id: lastId })
        });
        const j = await res.json();
        const msgs = j.messages || [];
        for (const m of msgs) {
            lastId = Math.max(lastId, m.id);
            messagesEl.appendChild(renderMessage(m, <?php echo (int)$uid; ?>));
        }
        if (msgs.length) messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    async function selectConversation(otherId, name) {
        document.querySelectorAll('.convo').forEach(c => c.classList.toggle('active', c.dataset.otherId == otherId));
        otherIdEl.value = otherId;
        lastId = 0;
        document.getElementById('thread-title').textContent = name;
        document.getElementById('thread-avatar').textContent = (name||'?').slice(0,1).toUpperCase();
        messagesEl.innerHTML = '';
        if (sidebar.classList.contains('open')) sidebar.classList.remove('open');
        await fetchMessages(otherId);
        if (pollHandle) clearInterval(pollHandle);
        pollHandle = setInterval(() => fetchMessages(otherId), 2000);
    }

    btnSelf.addEventListener('click', () => selectConversation(<?php echo (int)$uid; ?>, '<?php echo htmlspecialchars($username); ?>'));

    btnSend.addEventListener('click', async () => {
        const otherId = parseInt(otherIdEl.value || '0', 10);
        if (!otherId) { alert('Select a conversation or click Self'); return; }
        const body = inputEl.value.trim();
        if (!body) { inputEl.focus(); return; }
        inputEl.value = '';
        const res = await fetch('?action=send_message', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ csrf_token: csrf, other_id: otherId, body })
        });
        const j = await res.json().catch(()=>({}));
        if (!j.ok) alert(j.error || 'Failed to send');
        else await fetchMessages(otherId);
    });

    btnAttach.addEventListener('click', () => fileEl.click());
    fileEl.addEventListener('change', async () => {
        const otherId = parseInt(otherIdEl.value || '0', 10);
        if (!otherId) { alert('Select a conversation first'); return; }
        const f = fileEl.files[0]; if (!f) return;
        const fd = new FormData();
        fd.append('csrf_token', csrf);
        fd.append('other_id', String(otherId));
        fd.append('file', f);
        const res = await fetch('?action=upload', { method: 'POST', body: fd });
        const j = await res.json().catch(()=>({}));
        if (!j.ok) alert(j.error || 'Upload failed');
        else await fetchMessages(otherId);
        fileEl.value = '';
    });

    btnAI.addEventListener('click', async () => {
        const prompt = prompt('Ask the AI (med-chat):');
        if (!prompt) return;
        const res = await fetch('?action=ai_proxy', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ csrf_token: csrf, prompt })
        });
        const j = await res.json().catch(()=>({}));
        if (!j.ok) { alert(j.error || 'AI error'); return; }
        alert('AI [' + (j.model||'') + ']:\n\n' + (j.answer||''));
    });

    document.getElementById('btn-save-settings').addEventListener('click', async () => {
        const base = document.getElementById('ai-base').value;
        const model = document.getElementById('ai-model').value;
        const key = document.getElementById('ai-key').value;
        const res = await fetch('?action=save_settings', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ csrf_token: csrf, base_url: base, api_key: key, model })
        });
        const j = await res.json().catch(()=>({}));
        if (j.ok) alert('Settings saved'); else alert(j.error || 'Failed to save');
    });

    searchEl.addEventListener('input', () => listConversations());

    await listConversations();
    // Auto-select self chat on first load for convenience
    <?php echo 'selectConversation(' . (int)$uid . ', ' . json_encode($username) . ');'; ?>
    </script>
<?php endif; ?>
</body>
</html>

