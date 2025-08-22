<?php
declare(strict_types=1);
session_start();

// Nightplay - app.php (App detail + Downloads)

// ---------- Configuration ----------
const SITE_NAME = 'Nightplay';
$ROOT_DIR = __DIR__;
$DB_FILE = $ROOT_DIR . '/nightplay.sqlite';
$UPLOAD_DIR = $ROOT_DIR . '/uploads';

// ---------- Database Helpers ----------
function db(): PDO {
  static $pdo = null;
  if ($pdo !== null) return $pdo;
  $pdo = new PDO('sqlite:' . $GLOBALS['DB_FILE']);
  $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
  $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
  $pdo->exec('PRAGMA foreign_keys = ON');
  $pdo->exec('PRAGMA journal_mode = WAL');
  $pdo->exec('PRAGMA synchronous = NORMAL');
  ensure_schema($pdo);
  return $pdo;
}

function ensure_schema(PDO $pdo): void {
  $pdo->exec('CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
  )');
  $pdo->exec('CREATE TABLE IF NOT EXISTS apps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    developer TEXT NOT NULL,
    category TEXT DEFAULT "",
    short_desc TEXT DEFAULT "",
    long_desc TEXT DEFAULT "",
    icon_path TEXT DEFAULT "",
    banner_path TEXT DEFAULT "",
    is_published INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
  )');
  $pdo->exec('CREATE TABLE IF NOT EXISTS app_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id INTEGER NOT NULL,
    version_name TEXT NOT NULL,
    version_code INTEGER NOT NULL,
    changelog TEXT DEFAULT "",
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    is_published INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE
  )');
  $pdo->exec('CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id INTEGER NOT NULL,
    version_id INTEGER NOT NULL,
    downloaded_at TEXT NOT NULL,
    ip TEXT DEFAULT "",
    user_agent TEXT DEFAULT "",
    bytes INTEGER DEFAULT 0,
    FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
    FOREIGN KEY (version_id) REFERENCES app_versions(id) ON DELETE CASCADE
  )');
}

// ---------- Utilities ----------
function h(string $s): string { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function now(): string { return (new DateTimeImmutable('now'))->format('c'); }

function latest_version_for_app(PDO $pdo, int $appId): ?array {
  $stmt = $pdo->prepare('SELECT * FROM app_versions WHERE app_id = :id AND is_published = 1 ORDER BY created_at DESC, id DESC LIMIT 1');
  $stmt->execute([':id' => $appId]);
  $row = $stmt->fetch();
  return $row ?: null;
}

// ---------- Download streaming (Range support) ----------
function stream_file(string $absolutePath, string $asFilename, string $mime, bool $cacheLong = false): void {
  if (!is_file($absolutePath) || !is_readable($absolutePath)) {
    http_response_code(404);
    echo 'File not found';
    exit;
  }

  @set_time_limit(0);
  @ini_set('output_buffering', 'off');
  @ini_set('zlib.output_compression', '0');
  @ini_set('implicit_flush', '1');
  while (ob_get_level()) { ob_end_clean(); }

  $size = filesize($absolutePath);
  $start = 0;
  $end = $size - 1;
  $length = $size;

  header('Content-Type: ' . $mime);
  header('X-Content-Type-Options: nosniff');
  header('Accept-Ranges: bytes');
  if ($cacheLong) {
    header('Cache-Control: public, max-age=31536000, immutable');
  } else {
    header('Cache-Control: no-cache, no-store, must-revalidate');
    header('Pragma: no-cache');
    header('Expires: 0');
  }
  header('Content-Disposition: attachment; filename="' . rawurlencode($asFilename) . '"');

  if (isset($_SERVER['HTTP_RANGE'])) {
    if (preg_match('/bytes=([0-9]*)-([0-9]*)/i', (string)$_SERVER['HTTP_RANGE'], $matches)) {
      if ($matches[1] !== '') $start = (int)$matches[1];
      if ($matches[2] !== '') $end = (int)$matches[2];
      if ($end > $size - 1) $end = $size - 1;
      if ($start > $end || $start >= $size) { http_response_code(416); header('Content-Range: bytes */' . $size); exit; }
      $length = $end - $start + 1;
      http_response_code(206);
      header("Content-Range: bytes $start-$end/$size");
      header('Content-Length: ' . $length);
    }
  } else {
    header('Content-Length: ' . $size);
  }

  $chunkSize = 8 * 1024 * 1024; // 8MB
  $fp = fopen($absolutePath, 'rb');
  if ($fp === false) { http_response_code(500); echo 'Unable to open file'; exit; }
  if ($start > 0) fseek($fp, $start);

  $bytesSent = 0;
  while (!feof($fp) && $bytesSent < $length) {
    $bytesToRead = (int)min($chunkSize, $length - $bytesSent);
    $buffer = fread($fp, $bytesToRead);
    if ($buffer === false) break;
    echo $buffer;
    $bytesSent += strlen($buffer);
    flush();
    if (connection_aborted()) break;
  }
  fclose($fp);
}

// ---------- Fetch app ----------
$pdo = db();
$slug = trim((string)($_GET['slug'] ?? ''));
if ($slug === '') { header('Location: /index.php'); exit; }

$stmt = $pdo->prepare('SELECT * FROM apps WHERE slug = :slug AND is_published = 1');
$stmt->execute([':slug' => $slug]);
$app = $stmt->fetch();
if (!$app) { http_response_code(404); echo 'App not found'; exit; }

// ---------- Download routes ----------
$download = $_GET['download'] ?? '';
if ($download !== '') {
  $v = null;
  if ($download === 'latest') {
    $v = latest_version_for_app($pdo, (int)$app['id']);
  } else if (ctype_digit((string)$download)) {
    $stmt = $pdo->prepare('SELECT * FROM app_versions WHERE id = :id AND app_id = :app AND is_published = 1');
    $stmt->execute([':id' => (int)$download, ':app' => (int)$app['id']]);
    $v = $stmt->fetch() ?: null;
  }
  if (!$v) { http_response_code(404); echo 'No available version'; exit; }

  $abs = $GLOBALS['ROOT_DIR'] . '/' . $v['file_path'];
  $fname = $app['slug'] . '-v' . $v['version_name'] . '.' . pathinfo($abs, PATHINFO_EXTENSION);

  // Log download (best-effort)
  $pdo->prepare('INSERT INTO downloads (app_id, version_id, downloaded_at, ip, user_agent, bytes) VALUES (:a,:v,:d,:ip,:ua,:b)')->execute([
    ':a' => (int)$app['id'], ':v' => (int)$v['id'], ':d' => now(), ':ip' => $_SERVER['REMOTE_ADDR'] ?? '', ':ua' => $_SERVER['HTTP_USER_AGENT'] ?? '', ':b' => (int)$v['file_size']
  ]);

  $cacheLong = ($download !== 'latest');
  stream_file($abs, $fname, $v['mime_type'], $cacheLong);
  exit;
}

// Optional specific version view
$versionId = isset($_GET['version']) && ctype_digit((string)$_GET['version']) ? (int)$_GET['version'] : 0;
$version = null;
if ($versionId > 0) {
  $stmt = $pdo->prepare('SELECT * FROM app_versions WHERE id = :id AND app_id = :app AND is_published = 1');
  $stmt->execute([':id'=>$versionId, ':app'=>(int)$app['id']]);
  $version = $stmt->fetch() ?: null;
}
$latest = latest_version_for_app($pdo, (int)$app['id']);

// ---------- Render ----------
function render_header(string $title, array $app): void {
  echo '<!doctype html><html lang="en"><head><meta charset="utf-8">';
  echo '<meta name="viewport" content="width=device-width, initial-scale=1">';
  echo '<meta name="color-scheme" content="dark">';
  echo '<title>' . h($title) . '</title>';
  echo '<meta name="theme-color" content="#0b0f17">';
  echo '<meta property="og:title" content="' . h($app['name']) . ' on Nightplay" />';
  $desc = $app['short_desc'] ?: 'Download ' . $app['name'] . ' by ' . $app['developer'];
  echo '<meta property="og:description" content="' . h($desc) . '" />';
  if (!empty($app['icon_path'])) { echo '<meta property="og:image" content="/' . h($app['icon_path']) . '" />'; }
  echo '<style>';
  ?>
  :root { --bg:#0b0f17;--surface:#111827;--surface-2:#0f1623;--text:#e5e7eb;--muted:#9ca3af;--primary:#22d3ee;--accent:#a78bfa;--border:#1f2937; }
  html,body{margin:0;padding:0;background:var(--bg);color:var(--text);font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,Helvetica Neue,Arial}
  a{color:inherit;text-decoration:none}
  .topbar{position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:12px;padding:12px 16px;background:linear-gradient(180deg,rgba(7,10,16,.95),rgba(7,10,16,.75));backdrop-filter:blur(12px);border-bottom:1px solid var(--border)}
  .brand{display:flex;align-items:center;gap:10px;font-weight:700}
  .brand-badge{width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,var(--primary),var(--accent));box-shadow:0 4px 16px rgba(34,211,238,.35)}
  .wrap{max-width:1100px;margin:0 auto;padding:18px}
  .hero{display:grid;grid-template-columns:96px 1fr;gap:16px}
  @media(max-width:700px){.hero{grid-template-columns:64px 1fr}}
  .icon{width:96px;height:96px;border-radius:20px;border:1px solid var(--border);background:var(--surface-2);overflow:hidden;display:grid;place-items:center}
  .icon img{width:100%;height:100%;object-fit:cover}
  .title{font-size:24px;font-weight:800;margin:0}
  .dev{color:var(--muted);margin-top:4px}
  .actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
  .btn{display:inline-block;padding:12px 16px;border-radius:12px;border:0;background:var(--primary);color:#001217;font-weight:800;cursor:pointer}
  .btn.secondary{background:var(--surface-2);color:var(--text);border:1px solid var(--border)}
  .section{margin-top:18px;background:linear-gradient(180deg,var(--surface),var(--surface-2));border:1px solid var(--border);border-radius:16px;padding:16px}
  .versions table{width:100%;border-collapse:collapse}
  .versions th,.versions td{border-bottom:1px solid var(--border);padding:10px 8px;text-align:left}
  .muted{color:var(--muted)}
  </style>
  </head><body>
  <header class="topbar">
    <a class="brand" href="/index.php"><span class="brand-badge"></span><span>Nightplay</span></a>
  </header>
  <div class="wrap">
  <?php
}
function render_footer(): void { echo '</div></body></html>'; }

render_header($app['name'] . ' – Nightplay', $app);
?>
  <section class="hero">
    <div class="icon">
      <?php if (!empty($app['icon_path']) && file_exists($ROOT_DIR . '/' . $app['icon_path'])): ?>
        <img src="/<?php echo h($app['icon_path']); ?>" alt="<?php echo h($app['name']); ?> icon">
      <?php else: ?>
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 6a3 3 0 013-3h7l5 5v10a3 3 0 01-3 3H6a3 3 0 01-3-3V6z" stroke="#4b5563" stroke-width="1.5"/><path d="M13 3v5h5" stroke="#4b5563" stroke-width="1.5"/></svg>
      <?php endif; ?>
    </div>
    <div>
      <h1 class="title"><?php echo h($app['name']); ?></h1>
      <div class="dev">by <?php echo h($app['developer']); ?><?php if ($app['category']): ?> • <?php echo h($app['category']); ?><?php endif; ?></div>
      <div class="actions">
        <?php if ($latest): ?>
          <a class="btn" href="/app.php?slug=<?php echo h($app['slug']); ?>&download=latest">Download</a>
          <a class="btn secondary" href="#" onclick="navigator.clipboard.writeText(location.origin + '/app.php?slug=<?php echo h($app['slug']); ?>&download=latest'); return false;">Copy stable link</a>
          <span class="muted" style="align-self:center;font-size:13px;">v<?php echo h($latest['version_name']); ?> • <?php echo number_format((int)$latest['file_size']/1048576, 2); ?> MB</span>
        <?php else: ?>
          <span class="muted">No release available</span>
        <?php endif; ?>
      </div>
    </div>
  </section>

  <?php if (!empty($app['banner_path']) && file_exists($ROOT_DIR . '/' . $app['banner_path'])): ?>
    <section class="section" style="overflow:hidden;padding:0;margin-top:18px;">
      <img src="/<?php echo h($app['banner_path']); ?>" alt style="width:100%;height:auto;display:block;max-height:320px;object-fit:cover;">
    </section>
  <?php endif; ?>

  <section class="section">
    <h3 style="margin:0 0 8px;">About this app</h3>
    <p class="muted" style="margin:0 0 8px;">Updated: <?php echo h(date('Y-m-d', strtotime($app['updated_at']))); ?></p>
    <p style="white-space:pre-wrap;line-height:1.6;"><?php echo nl2br(h($app['long_desc'] ?: $app['short_desc'])); ?></p>
  </section>

  <?php $versions = $pdo->prepare('SELECT * FROM app_versions WHERE app_id = :id AND is_published = 1 ORDER BY created_at DESC'); $versions->execute([':id'=>(int)$app['id']]); $versions = $versions->fetchAll(); ?>
  <?php if ($versions): ?>
    <section class="section versions">
      <h3 style="margin:0 0 8px;">All versions</h3>
      <table>
        <thead><tr><th>Version</th><th>Uploaded</th><th>Size</th><th>Download</th></tr></thead>
        <tbody>
          <?php foreach ($versions as $v): ?>
            <tr>
              <td>v<?php echo h($v['version_name']); ?> <span class="muted">(<?php echo (int)$v['version_code']; ?>)</span></td>
              <td class="muted"><?php echo h(date('Y-m-d', strtotime($v['created_at']))); ?></td>
              <td><?php echo number_format((int)$v['file_size']/1048576, 2); ?> MB</td>
              <td><a class="btn secondary" href="/app.php?slug=<?php echo h($app['slug']); ?>&download=<?php echo (int)$v['id']; ?>">Download</a> <a class="btn secondary" href="/app.php?slug=<?php echo h($app['slug']); ?>&version=<?php echo (int)$v['id']; ?>">Details</a></td>
            </tr>
          <?php endforeach; ?>
        </tbody>
      </table>
    </section>
  <?php endif; ?>

<?php
render_footer();
?>