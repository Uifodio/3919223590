<?php
declare(strict_types=1);
session_start();

// Nightplay - admin.php (Auth, Uploads, Manage Apps)

// ---------- Configuration ----------
const SITE_NAME = 'Nightplay';
$ROOT_DIR = __DIR__;
$DB_FILE = $ROOT_DIR . '/nightplay.sqlite';
$UPLOAD_DIR = $ROOT_DIR . '/uploads';

if (!is_dir($UPLOAD_DIR)) {
  @mkdir($UPLOAD_DIR, 0775, true);
}

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
function slugify(string $text): string {
  $text = strtolower(trim($text));
  $text = preg_replace('~[^\pL\d]+~u', '-', $text);
  $text = trim($text, '-');
  if ($text === '') { $text = 'app'; }
  return $text;
}
function unique_slug(PDO $pdo, string $base): string {
  $slug = $base;
  $i = 1;
  while (true) {
    $stmt = $pdo->prepare('SELECT 1 FROM apps WHERE slug = :slug LIMIT 1');
    $stmt->execute([':slug' => $slug]);
    if (!$stmt->fetch()) { return $slug; }
    $slug = $base . '-' . $i;
    $i++;
  }
}
function is_logged_in(): bool { return isset($_SESSION['user_id']); }

// ---------- Auth ----------
$pdo = db();

if (($_POST['action'] ?? '') === 'login') {
  $username = trim((string)($_POST['username'] ?? ''));
  $password = (string)($_POST['password'] ?? '');
  $count = (int)$pdo->query('SELECT COUNT(*) FROM users')->fetchColumn();
  if ($count === 0 && $username !== '' && $password !== '') {
    $hash = password_hash($password, PASSWORD_DEFAULT);
    $stmt = $pdo->prepare('INSERT INTO users (username, password_hash, created_at) VALUES (:u, :p, :c)');
    $stmt->execute([':u' => $username, ':p' => $hash, ':c' => now()]);
  }
  $stmt = $pdo->prepare('SELECT * FROM users WHERE username = :u LIMIT 1');
  $stmt->execute([':u' => $username]);
  $user = $stmt->fetch();
  if ($user && password_verify($password, $user['password_hash'])) {
    $_SESSION['user_id'] = (int)$user['id'];
    $_SESSION['username'] = (string)$user['username'];
    header('Location: /admin.php');
    exit;
  } else {
    $login_error = 'Invalid credentials';
  }
}

if (isset($_GET['action']) && $_GET['action'] === 'logout') {
  session_unset();
  session_destroy();
  header('Location: /index.php');
  exit;
}

if (!is_logged_in() && !isset($_POST['action'])) {
  // show login view later in rendering
}

// ---------- Actions (require auth) ----------
function require_auth(): void { if (!is_logged_in()) { http_response_code(403); echo 'Forbidden'; exit; } }

$action = $_POST['action'] ?? '';
if ($action === 'create_app') {
  require_auth();
  $name = trim((string)($_POST['name'] ?? ''));
  $developer = trim((string)($_POST['developer'] ?? ''));
  $category = trim((string)($_POST['category'] ?? ''));
  $short_desc = trim((string)($_POST['short_desc'] ?? ''));
  $long_desc = trim((string)($_POST['long_desc'] ?? ''));
  if ($name === '' || $developer === '') {
    $flash_error = 'Name and Developer are required.';
  } else {
    $base = slugify($name);
    $slug = unique_slug($pdo, $base);
    $now = now();
    $pdo->prepare('INSERT INTO apps (slug, name, developer, category, short_desc, long_desc, created_at, updated_at) VALUES (:slug, :name, :dev, :cat, :short, :long, :c, :u)')
        ->execute([':slug'=>$slug, ':name'=>$name, ':dev'=>$developer, ':cat'=>$category, ':short'=>$short_desc, ':long'=>$long_desc, ':c'=>$now, ':u'=>$now]);
    $app_id = (int)$pdo->lastInsertId();
    // Icon & banner uploads
    $app_dir = $GLOBALS['UPLOAD_DIR'] . '/' . $slug;
    @mkdir($app_dir, 0775, true);
    @mkdir($app_dir . '/assets', 0775, true);
    $icon_rel = '';
    $banner_rel = '';
    if (isset($_FILES['icon']) && is_uploaded_file($_FILES['icon']['tmp_name'])) {
      $ext = pathinfo($_FILES['icon']['name'], PATHINFO_EXTENSION) ?: 'png';
      $dest = $app_dir . '/assets/icon.' . $ext;
      @move_uploaded_file($_FILES['icon']['tmp_name'], $dest);
      $icon_rel = 'uploads/' . $slug . '/assets/' . basename($dest);
    }
    if (isset($_FILES['banner']) && is_uploaded_file($_FILES['banner']['tmp_name'])) {
      $ext = pathinfo($_FILES['banner']['name'], PATHINFO_EXTENSION) ?: 'jpg';
      $dest = $app_dir . '/assets/banner.' . $ext;
      @move_uploaded_file($_FILES['banner']['tmp_name'], $dest);
      $banner_rel = 'uploads/' . $slug . '/assets/' . basename($dest);
    }
    if ($icon_rel !== '' || $banner_rel !== '') {
      $pdo->prepare('UPDATE apps SET icon_path = COALESCE(NULLIF(:icon, ""), icon_path), banner_path = COALESCE(NULLIF(:banner, ""), banner_path), updated_at = :u WHERE id = :id')
          ->execute([':icon'=>$icon_rel, ':banner'=>$banner_rel, ':u'=>now(), ':id'=>$app_id]);
    }
    $flash_success = 'App created successfully';
  }
}

if ($action === 'update_app') {
  require_auth();
  $app_id = (int)($_POST['app_id'] ?? 0);
  $stmt = $pdo->prepare('SELECT * FROM apps WHERE id = :id');
  $stmt->execute([':id'=>$app_id]);
  $app = $stmt->fetch();
  if (!$app) { $flash_error = 'App not found'; }
  else {
    $name = trim((string)($_POST['name'] ?? $app['name']));
    $developer = trim((string)($_POST['developer'] ?? $app['developer']));
    $category = trim((string)($_POST['category'] ?? $app['category']));
    $short_desc = trim((string)($_POST['short_desc'] ?? $app['short_desc']));
    $long_desc = trim((string)($_POST['long_desc'] ?? $app['long_desc']));
    $is_published = isset($_POST['is_published']) ? 1 : 0;

    $pdo->prepare('UPDATE apps SET name=:name, developer=:dev, category=:cat, short_desc=:short, long_desc=:long, is_published=:pub, updated_at=:u WHERE id=:id')
        ->execute([':name'=>$name, ':dev'=>$developer, ':cat'=>$category, ':short'=>$short_desc, ':long'=>$long_desc, ':pub'=>$is_published, ':u'=>now(), ':id'=>$app_id]);

    // Handle icon/banner
    $slug = $app['slug'];
    $app_dir = $GLOBALS['UPLOAD_DIR'] . '/' . $slug;
    @mkdir($app_dir, 0775, true);
    @mkdir($app_dir . '/assets', 0775, true);
    $icon_rel = '';
    $banner_rel = '';
    if (isset($_FILES['icon']) && is_uploaded_file($_FILES['icon']['tmp_name'])) {
      $ext = pathinfo($_FILES['icon']['name'], PATHINFO_EXTENSION) ?: 'png';
      $dest = $app_dir . '/assets/icon.' . $ext;
      @move_uploaded_file($_FILES['icon']['tmp_name'], $dest);
      $icon_rel = 'uploads/' . $slug . '/assets/' . basename($dest);
    }
    if (isset($_FILES['banner']) && is_uploaded_file($_FILES['banner']['tmp_name'])) {
      $ext = pathinfo($_FILES['banner']['name'], PATHINFO_EXTENSION) ?: 'jpg';
      $dest = $app_dir . '/assets/banner.' . $ext;
      @move_uploaded_file($_FILES['banner']['tmp_name'], $dest);
      $banner_rel = 'uploads/' . $slug . '/assets/' . basename($dest);
    }
    if ($icon_rel !== '' || $banner_rel !== '') {
      $pdo->prepare('UPDATE apps SET icon_path = COALESCE(NULLIF(:icon, ""), icon_path), banner_path = COALESCE(NULLIF(:banner, ""), banner_path), updated_at = :u WHERE id = :id')
          ->execute([':icon'=>$icon_rel, ':banner'=>$banner_rel, ':u'=>now(), ':id'=>$app_id]);
    }
    $flash_success = 'App updated';
  }
}

if ($action === 'upload_version') {
  require_auth();
  $app_id = (int)($_POST['app_id'] ?? 0);
  $version_name = trim((string)($_POST['version_name'] ?? ''));
  $version_code = (int)($_POST['version_code'] ?? 0);
  $changelog = trim((string)($_POST['changelog'] ?? ''));

  $stmt = $pdo->prepare('SELECT * FROM apps WHERE id = :id');
  $stmt->execute([':id'=>$app_id]);
  $app = $stmt->fetch();
  if (!$app) { $flash_error = 'App not found'; }
  else if (!isset($_FILES['file']) || !is_uploaded_file($_FILES['file']['tmp_name'])) { $flash_error = 'File upload missing'; }
  else if ($version_name === '' || $version_code <= 0) { $flash_error = 'Version name/code are required'; }
  else {
    $slug = $app['slug'];
    $app_dir = $GLOBALS['UPLOAD_DIR'] . '/' . $slug;
    $ver_dir = $app_dir . '/versions';
    @mkdir($ver_dir, 0775, true);
    $orig = basename((string)$_FILES['file']['name']);
    $san = preg_replace('/[^A-Za-z0-9._-]/', '_', $orig);
    $dest = $ver_dir . '/' . time() . '-' . $san;
    if (!@move_uploaded_file($_FILES['file']['tmp_name'], $dest)) {
      $flash_error = 'Failed to move uploaded file';
    } else {
      $rel = 'uploads/' . $slug . '/versions/' . basename($dest);
      $size = filesize($dest) ?: 0;
      $finfo = finfo_open(FILEINFO_MIME_TYPE);
      $mime = $finfo ? (string)finfo_file($finfo, $dest) : 'application/octet-stream';
      if ($finfo) finfo_close($finfo);
      $pdo->prepare('INSERT INTO app_versions (app_id, version_name, version_code, changelog, file_path, file_size, mime_type, is_published, created_at) VALUES (:app,:vn,:vc,:cl,:fp,:sz,:mt,1,:c)')
          ->execute([':app'=>$app_id, ':vn'=>$version_name, ':vc'=>$version_code, ':cl'=>$changelog, ':fp'=>$rel, ':sz'=>$size, ':mt'=>$mime, ':c'=>now()]);
      $pdo->prepare('UPDATE apps SET updated_at = :u WHERE id = :id')->execute([':u'=>now(), ':id'=>$app_id]);
      $flash_success = 'Version uploaded successfully';
    }
  }
}

if ($action === 'toggle_version') {
  require_auth();
  $version_id = (int)($_POST['version_id'] ?? 0);
  $is_published = isset($_POST['is_published']) ? 1 : 0;
  $pdo->prepare('UPDATE app_versions SET is_published = :p WHERE id = :id')->execute([':p'=>$is_published, ':id'=>$version_id]);
  $flash_success = 'Version visibility updated';
}

// ---------- Fetch data for rendering ----------
function latest_version_for_app(PDO $pdo, int $appId): ?array {
  $stmt = $pdo->prepare('SELECT * FROM app_versions WHERE app_id = :id ORDER BY created_at DESC, id DESC LIMIT 1');
  $stmt->execute([':id' => $appId]);
  $row = $stmt->fetch();
  return $row ?: null;
}

$apps = $pdo->query('SELECT * FROM apps ORDER BY updated_at DESC')->fetchAll();

// ---------- Rendering ----------
function render_header(string $title): void {
  $username = $_SESSION['username'] ?? '';
  echo '<!doctype html><html lang="en"><head><meta charset="utf-8">';
  echo '<meta name="viewport" content="width=device-width, initial-scale=1">';
  echo '<meta name="color-scheme" content="dark">';
  echo '<title>' . h($title) . '</title>';
  echo '<meta name="theme-color" content="#0b0f17">';
  echo '<style>';
  ?>
  :root { --bg:#0b0f17;--surface:#111827;--surface-2:#0f1623;--text:#e5e7eb;--muted:#9ca3af;--primary:#22d3ee;--border:#1f2937;--danger:#ef4444;--success:#10b981; }
  html,body{margin:0;padding:0;background:var(--bg);color:var(--text);font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,Helvetica Neue,Arial;}
  a{color:inherit;text-decoration:none}
  .topbar{position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:12px;padding:12px 16px;background:linear-gradient(180deg,rgba(7,10,16,.95),rgba(7,10,16,.75));backdrop-filter:blur(12px);border-bottom:1px solid var(--border)}
  .brand{display:flex;align-items:center;gap:10px;font-weight:700}
  .brand-badge{width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,var(--primary),#a78bfa);box-shadow:0 4px 16px rgba(34,211,238,.35)}
  .container{max-width:1100px;margin:0 auto;padding:18px}
  .card{background:linear-gradient(180deg,var(--surface),var(--surface-2));border:1px solid var(--border);border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.35);padding:16px}
  .grid{display:grid;grid-template-columns:1fr;gap:18px}
  .row{display:grid;gap:10px}
  .input{padding:10px 12px;background:var(--surface-2);border:1px solid var(--border);border-radius:12px;color:var(--text)}
  .btn{display:inline-block;padding:10px 14px;border-radius:12px;border:0;background:var(--primary);color:#001217;font-weight:800;cursor:pointer}
  .btn.secondary{background:var(--surface-2);color:var(--text);border:1px solid var(--border)}
  .muted{color:var(--muted)}
  .two-col{display:grid;grid-template-columns:1fr 1fr;gap:18px}
  @media(max-width:900px){.two-col{grid-template-columns:1fr}}
  table{width:100%;border-collapse:collapse}
  th,td{border-bottom:1px solid var(--border);padding:10px 8px;text-align:left}
  .badge{display:inline-block;padding:2px 8px;border-radius:999px;border:1px solid rgba(34,211,238,.25);color:var(--primary);font-size:11px}
  </style>
  </head><body>
  <header class="topbar">
    <a class="brand" href="/index.php"><span class="brand-badge"></span><span>Nightplay Admin</span></a>
    <div style="margin-left:auto;display:flex;gap:10px;align-items:center;">
      <?php if ($username): ?>
        <span class="muted">Signed in as <?php echo h($username); ?></span>
        <a class="btn secondary" href="/admin.php?action=logout">Logout</a>
      <?php endif; ?>
    </div>
  </header>
  <div class="container">
  <?php
}

function render_footer(): void {
  echo '</div>'; // container
  echo '</body></html>';
}

// ---------- Views ----------
if (!is_logged_in()) {
  render_header('Nightplay – Admin Login');
  ?>
  <div class="card" style="max-width:520px;margin:30px auto;">
    <h2 style="margin:0 0 8px;">Sign in</h2>
    <p class="muted" style="margin-top:-6px">Manage and upload your apps</p>
    <?php if (!empty($login_error)): ?><div style="color:var(--danger);margin:10px 0;"><?php echo h($login_error); ?></div><?php endif; ?>
    <form method="post" action="/admin.php">
      <input type="hidden" name="action" value="login">
      <div class="row">
        <label>Username</label>
        <input class="input" type="text" name="username" required>
      </div>
      <div class="row">
        <label>Password</label>
        <input class="input" type="password" name="password" required>
      </div>
      <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:8px;">
        <a class="btn secondary" href="/index.php">Cancel</a>
        <button class="btn" type="submit">Sign In</button>
      </div>
      <p class="muted" style="margin-top:10px;font-size:12px;">First run: the credentials you enter will create the admin account.</p>
    </form>
  </div>
  <?php
  render_footer();
  exit;
}

render_header('Nightplay – Dashboard');
?>
  <?php if (!empty($flash_error)): ?><div class="card" style="border-color:var(--danger);color:var(--text);">❌ <?php echo h($flash_error); ?></div><?php endif; ?>
  <?php if (!empty($flash_success)): ?><div class="card" style="border-color:var(--success);color:var(--text);">✅ <?php echo h($flash_success); ?></div><?php endif; ?>

  <div class="two-col">
    <div class="card">
      <h3 style="margin:0 0 10px;">Create new app</h3>
      <form method="post" action="/admin.php" enctype="multipart/form-data">
        <input type="hidden" name="action" value="create_app">
        <div class="grid">
          <div class="row"><label>Name</label><input class="input" type="text" name="name" required></div>
          <div class="row"><label>Developer</label><input class="input" type="text" name="developer" required></div>
          <div class="row"><label>Category</label><input class="input" type="text" name="category" placeholder="Tools, Games, ..."></div>
          <div class="row"><label>Short description</label><input class="input" type="text" name="short_desc" maxlength="160"></div>
          <div class="row"><label>Long description</label><textarea class="input" name="long_desc" rows="5" style="resize:vertical"></textarea></div>
          <div class="row"><label>Icon</label><input class="input" type="file" name="icon" accept="image/*"></div>
          <div class="row"><label>Banner</label><input class="input" type="file" name="banner" accept="image/*"></div>
        </div>
        <div style="display:flex;justify-content:flex-end;margin-top:10px;">
          <button class="btn" type="submit">Create app</button>
        </div>
      </form>
    </div>

    <div class="card">
      <h3 style="margin:0 0 10px;">Your apps</h3>
      <table>
        <thead><tr><th>App</th><th>Updated</th><th>Visibility</th><th>Actions</th></tr></thead>
        <tbody>
          <?php foreach ($apps as $app): $lv = latest_version_for_app($pdo, (int)$app['id']); ?>
            <tr>
              <td>
                <div style="display:flex;align-items:center;gap:10px;">
                  <div style="width:32px;height:32px;border-radius:8px;border:1px solid var(--border);overflow:hidden;background:var(--surface-2);display:grid;place-items:center;">
                    <?php if (!empty($app['icon_path']) && file_exists($ROOT_DIR . '/' . $app['icon_path'])): ?>
                      <img src="/<?php echo h($app['icon_path']); ?>" alt style="width:100%;height:100%;object-fit:cover;">
                    <?php else: ?>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 6a3 3 0 013-3h7l5 5v10a3 3 0 01-3 3H6a3 3 0 01-3-3V6z" stroke="#4b5563" stroke-width="1.5"/><path d="M13 3v5h5" stroke="#4b5563" stroke-width="1.5"/></svg>
                    <?php endif; ?>
                  </div>
                  <div>
                    <div style="font-weight:700;"><?php echo h($app['name']); ?></div>
                    <div class="muted" style="font-size:12px;">by <?php echo h($app['developer']); ?> • <a href="/app.php?slug=<?php echo h($app['slug']); ?>">View</a></div>
                  </div>
                </div>
              </td>
              <td class="muted" style="font-size:12px;"><?php echo h(date('Y-m-d', strtotime($app['updated_at']))); ?></td>
              <td><?php echo $app['is_published'] ? '<span class="badge">Published</span>' : '<span class="badge" style="color:#f59e0b;border-color:rgba(245,158,11,.25)">Hidden</span>'; ?></td>
              <td><details><summary style="cursor:pointer">Manage</summary>
                <div style="padding:10px 0;">
                  <form method="post" action="/admin.php" enctype="multipart/form-data" style="margin-bottom:12px;">
                    <input type="hidden" name="action" value="update_app">
                    <input type="hidden" name="app_id" value="<?php echo (int)$app['id']; ?>">
                    <div class="grid">
                      <div class="row"><label>Name</label><input class="input" type="text" name="name" value="<?php echo h($app['name']); ?>" required></div>
                      <div class="row"><label>Developer</label><input class="input" type="text" name="developer" value="<?php echo h($app['developer']); ?>" required></div>
                      <div class="row"><label>Category</label><input class="input" type="text" name="category" value="<?php echo h($app['category']); ?>"></div>
                      <div class="row"><label>Short description</label><input class="input" type="text" name="short_desc" value="<?php echo h($app['short_desc']); ?>"></div>
                      <div class="row"><label>Long description</label><textarea class="input" name="long_desc" rows="4" style="resize:vertical"><?php echo h($app['long_desc']); ?></textarea></div>
                      <div class="row"><label>Icon</label><input class="input" type="file" name="icon" accept="image/*"></div>
                      <div class="row"><label>Banner</label><input class="input" type="file" name="banner" accept="image/*"></div>
                      <div class="row"><label><input type="checkbox" name="is_published" <?php echo $app['is_published'] ? 'checked' : ''; ?>> Published</label></div>
                    </div>
                    <div style="display:flex;justify-content:flex-end;margin-top:10px;">
                      <button class="btn" type="submit">Save app</button>
                    </div>
                  </form>

                  <div style="border-top:1px solid var(--border);margin:14px 0;"></div>

                  <form method="post" action="/admin.php" enctype="multipart/form-data">
                    <input type="hidden" name="action" value="upload_version">
                    <input type="hidden" name="app_id" value="<?php echo (int)$app['id']; ?>">
                    <h4 style="margin:0 0 6px;">Upload new version</h4>
                    <div class="grid">
                      <div class="row"><label>Version name</label><input class="input" type="text" name="version_name" placeholder="1.0.0" required></div>
                      <div class="row"><label>Version code</label><input class="input" type="number" name="version_code" placeholder="100" required></div>
                      <div class="row"><label>Changelog</label><textarea class="input" name="changelog" rows="3" style="resize:vertical"></textarea></div>
                      <div class="row"><label>File (APK/ZIP/etc.)</label><input class="input" type="file" name="file" required></div>
                    </div>
                    <div style="display:flex;justify-content:flex-end;margin-top:10px;">
                      <button class="btn" type="submit">Upload version</button>
                    </div>
                    <p class="muted" style="font-size:12px;margin-top:8px;">For large files, ensure server upload limits are configured (upload_max_filesize, post_max_size).</p>
                  </form>

                  <?php $versions = $pdo->prepare('SELECT * FROM app_versions WHERE app_id = :id ORDER BY created_at DESC'); $versions->execute([':id'=>(int)$app['id']]); $versions = $versions->fetchAll(); ?>
                  <?php if ($versions): ?>
                    <div style="margin-top:12px;">
                      <h4 style="margin:0 0 6px;">Versions</h4>
                      <table>
                        <thead><tr><th>Version</th><th>Size</th><th>Published</th><th>Download</th><th>Toggle</th></tr></thead>
                        <tbody>
                          <?php foreach ($versions as $v): ?>
                            <tr>
                              <td>v<?php echo h($v['version_name']); ?> <span class="muted">(<?php echo (int)$v['version_code']; ?>)</span></td>
                              <td><?php echo number_format((int)$v['file_size']/1048576, 2); ?> MB</td>
                              <td><?php echo $v['is_published']? 'Yes':'No'; ?></td>
                              <td><a class="btn secondary" href="/app.php?slug=<?php echo h($app['slug']); ?>&version=<?php echo (int)$v['id']; ?>">Page</a> <a class="btn" href="/app.php?slug=<?php echo h($app['slug']); ?>&download=<?php echo (int)$v['id']; ?>">Direct</a></td>
                              <td>
                                <form method="post" action="/admin.php">
                                  <input type="hidden" name="action" value="toggle_version">
                                  <input type="hidden" name="version_id" value="<?php echo (int)$v['id']; ?>">
                                  <label style="display:flex;align-items:center;gap:8px;">
                                    <input type="checkbox" name="is_published" <?php echo $v['is_published']? 'checked':''; ?> onchange="this.form.submit()"> Visible
                                  </label>
                                </form>
                              </td>
                            </tr>
                          <?php endforeach; ?>
                        </tbody>
                      </table>
                    </div>
                  <?php endif; ?>

                  <div style="margin-top:12px;">
                    <span class="muted" style="font-size:12px;">Stable link (always latest):</span>
                    <div class="input" style="white-space:nowrap;overflow:auto;font-size:12px;">https://your-domain/app.php?slug=<?php echo h($app['slug']); ?>&download=latest</div>
                  </div>
                </div>
              </details></td>
            </tr>
          <?php endforeach; ?>
          <?php if (!$apps): ?><tr><td colspan="4" class="muted">No apps yet</td></tr><?php endif; ?>
        </tbody>
      </table>
    </div>
  </div>
<?php
render_footer();