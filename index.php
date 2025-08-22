<?php
declare(strict_types=1);
session_start();

// Nightplay - index.php (Home, Menu, Login, Search)

// ---------- Configuration ----------
const SITE_NAME = 'Nightplay';
$ROOT_DIR = __DIR__;
$DB_FILE = $ROOT_DIR . '/nightplay.sqlite';
$UPLOAD_DIR = $ROOT_DIR . '/uploads';

// ---------- Bootstrap ----------
if (!is_dir($UPLOAD_DIR)) {
  @mkdir($UPLOAD_DIR, 0775, true);
}

// ---------- Database Helpers ----------
function db(): PDO {
  static $pdo = null;
  if ($pdo !== null) {
    return $pdo;
  }
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

  $pdo->exec('CREATE INDEX IF NOT EXISTS idx_apps_updated ON apps(updated_at DESC)');
  $pdo->exec('CREATE INDEX IF NOT EXISTS idx_versions_app ON app_versions(app_id, created_at DESC)');
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

function ensure_initial_user_if_needed(PDO $pdo): void {
  $count = (int) $pdo->query('SELECT COUNT(*) AS c FROM users')->fetchColumn();
  if ($count === 0 && isset($_POST['action']) && $_POST['action'] === 'login') {
    $username = trim((string)($_POST['username'] ?? 'admin'));
    $password = (string)($_POST['password'] ?? '');
    if ($username !== '' && $password !== '') {
      $hash = password_hash($password, PASSWORD_DEFAULT);
      $stmt = $pdo->prepare('INSERT INTO users (username, password_hash, created_at) VALUES (:u, :p, :c)');
      $stmt->execute([':u' => $username, ':p' => $hash, ':c' => now()]);
    }
  }
}

function latest_version_for_app(PDO $pdo, int $appId): ?array {
  $stmt = $pdo->prepare('SELECT * FROM app_versions WHERE app_id = :id AND is_published = 1 ORDER BY created_at DESC, id DESC LIMIT 1');
  $stmt->execute([':id' => $appId]);
  $row = $stmt->fetch();
  return $row ?: null;
}

// ---------- Auth Handling (Login/Logout on index) ----------
$pdo = db();
ensure_initial_user_if_needed($pdo);

if (($_POST['action'] ?? '') === 'login') {
  $username = trim((string)($_POST['username'] ?? ''));
  $password = (string)($_POST['password'] ?? '');
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

// ---------- AJAX search suggestions ----------
if (isset($_GET['ajax']) && $_GET['ajax'] === '1') {
  $q = trim((string)($_GET['q'] ?? ''));
  $out = [];
  if ($q !== '') {
    $stmt = $pdo->prepare('SELECT slug, name, developer FROM apps WHERE is_published = 1 AND (name LIKE :q OR developer LIKE :q OR short_desc LIKE :q) ORDER BY updated_at DESC LIMIT 10');
    $stmt->execute([':q' => '%' . $q . '%']);
    $out = $stmt->fetchAll();
  }
  header('Content-Type: application/json; charset=UTF-8');
  echo json_encode($out);
  exit;
}

// ---------- Query Apps ----------
$q = trim((string)($_GET['q'] ?? ''));
$apps = [];
if ($q === '') {
  $stmt = $pdo->query('SELECT * FROM apps WHERE is_published = 1 ORDER BY updated_at DESC LIMIT 36');
  $apps = $stmt->fetchAll();
} else {
  $stmt = $pdo->prepare('SELECT * FROM apps WHERE is_published = 1 AND (name LIKE :q OR developer LIKE :q OR short_desc LIKE :q OR category LIKE :q) ORDER BY updated_at DESC LIMIT 48');
  $stmt->execute([':q' => '%' . $q . '%']);
  $apps = $stmt->fetchAll();
}

// ---------- Rendering ----------
function render_header(string $title): void {
  $username = $_SESSION['username'] ?? '';
  $q = h((string)($_GET['q'] ?? ''));
  echo '<!doctype html><html lang="en"><head><meta charset="utf-8">';
  echo '<meta name="viewport" content="width=device-width, initial-scale=1">';
  echo '<meta name="color-scheme" content="dark">';
  echo '<title>' . h($title) . '</title>';
  echo '<meta name="theme-color" content="#0b0f17">';
  echo '<style>';
  ?>
  :root {
    --bg: #0b0f17;
    --surface: #111827;
    --surface-2: #0f1623;
    --text: #e5e7eb;
    --muted: #9ca3af;
    --primary: #22d3ee;
    --primary-2: #0ea5b7;
    --accent: #a78bfa;
    --danger: #ef4444;
    --success: #10b981;
    --warning: #f59e0b;
    --border: #1f2937;
    --card-radius: 16px;
    --shadow: 0 10px 30px rgba(0,0,0,0.35);
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica Neue, Arial, "Apple Color Emoji", "Segoe UI Emoji"; }
  a { color: inherit; text-decoration: none; }
  .topbar { position: sticky; top: 0; z-index: 50; display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: linear-gradient(180deg, rgba(7,10,16,0.95), rgba(7,10,16,0.75)); backdrop-filter: blur(12px); border-bottom: 1px solid var(--border); }
  .brand { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 18px; letter-spacing: 0.5px; }
  .brand-badge { width: 28px; height: 28px; border-radius: 8px; background: linear-gradient(135deg, var(--primary), var(--accent)); box-shadow: 0 4px 16px rgba(34,211,238,0.35); }
  .search { flex: 1; display: flex; align-items: center; background: var(--surface); border: 1px solid var(--border); border-radius: 999px; padding: 8px 14px; gap: 10px; }
  .search input { flex: 1; background: transparent; border: 0; outline: 0; color: var(--text); font-size: 15px; }
  .search button { background: var(--primary); color: #001217; border: 0; padding: 8px 14px; border-radius: 999px; cursor: pointer; font-weight: 700; transition: transform .06s ease; }
  .search button:active { transform: scale(0.98); }
  .nav-actions { display: flex; gap: 10px; align-items: center; }
  .pill { border: 1px solid var(--border); background: var(--surface); padding: 8px 14px; border-radius: 999px; font-weight: 600; }
  .hero { padding: 24px 16px; }
  .hero h1 { font-size: 22px; margin: 0 0 4px; }
  .muted { color: var(--muted); }
  .grid { padding: 8px 16px 40px; display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 18px; }
  @media (max-width: 1200px) { .grid { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
  @media (max-width: 900px) { .grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
  @media (max-width: 640px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .brand span { display:none; } }
  .card { background: linear-gradient(180deg, var(--surface), var(--surface-2)); border: 1px solid var(--border); border-radius: var(--card-radius); overflow: hidden; box-shadow: var(--shadow); transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease; }
  .card:hover { transform: translateY(-2px); border-color: var(--primary-2); box-shadow: 0 14px 36px rgba(14,165,183,0.25); }
  .card-body { display: grid; grid-template-columns: 64px 1fr; gap: 12px; padding: 14px; align-items: center; }
  .icon { width: 64px; height: 64px; border-radius: 14px; background: linear-gradient(135deg, #0f172a, #111827); border: 1px solid var(--border); display: grid; place-items: center; overflow: hidden; }
  .icon img { width: 100%; height: 100%; object-fit: cover; display: block; }
  .title { font-weight: 700; font-size: 16px; margin: 0 0 2px; }
  .dev { font-size: 13px; color: var(--muted); margin-bottom: 6px; }
  .meta { display: flex; gap: 8px; font-size: 12px; color: var(--muted); }
  .badge { background: rgba(34,211,238,0.1); color: var(--primary); border: 1px solid rgba(34,211,238,0.25); padding: 2px 8px; border-radius: 999px; font-weight: 700; font-size: 11px; }
  .login-modal { position: fixed; inset: 0; background: rgba(0,0,0,0.55); display: none; align-items: center; justify-content: center; z-index: 100; }
  .login-card { width: 100%; max-width: 420px; background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 18px; box-shadow: var(--shadow); }
  .login-card h3 { margin: 0 0 12px; }
  .form-row { display: grid; gap: 6px; margin-bottom: 12px; }
  .input { padding: 10px 12px; background: var(--surface-2); border: 1px solid var(--border); border-radius: 12px; color: var(--text); }
  .btn { display: inline-block; padding: 10px 14px; border-radius: 12px; border: 0; background: var(--primary); color: #001217; font-weight: 800; cursor: pointer; }
  .btn.secondary { background: var(--surface-2); color: var(--text); border: 1px solid var(--border); }
  .error { color: var(--danger); font-size: 13px; margin-bottom: 10px; }
  footer { padding: 24px 16px; color: var(--muted); text-align: center; border-top: 1px solid var(--border); background: linear-gradient(180deg, var(--surface-2), transparent); }
  <?php echo '</style>'; ?>
  </head><body>
  <header class="topbar">
    <a class="brand" href="/index.php" aria-label="Nightplay Home">
      <span class="brand-badge"></span>
      <span>Nightplay</span>
    </a>
    <form class="search" role="search" action="/index.php" method="get">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M21 21l-4.3-4.3" stroke="#9ca3af" stroke-width="2" stroke-linecap="round"/><circle cx="11" cy="11" r="7" stroke="#9ca3af" stroke-width="2"/></svg>
      <input type="search" name="q" placeholder="Search apps" value="<?php echo $q; ?>" autocomplete="off" id="q-input" />
      <button type="submit">Search</button>
    </form>
    <div class="nav-actions">
      <a class="pill" href="/admin.php">Dashboard</a>
      <?php if ($username): ?>
        <span class="pill" title="<?php echo h($username); ?>">Signed in</span>
        <a class="pill" href="/index.php?action=logout">Logout</a>
      <?php else: ?>
        <button class="pill" id="open-login" type="button">Login</button>
      <?php endif; ?>
    </div>
  </header>
  <div class="login-modal" id="login-modal">
    <div class="login-card">
      <h3>Sign in to Nightplay</h3>
      <p class="muted" style="margin-top:-6px">Upload and manage your apps</p>
      <?php if (!empty($GLOBALS['login_error'])): ?><div class="error"><?php echo h($GLOBALS['login_error']); ?></div><?php endif; ?>
      <form method="post" action="/index.php">
        <input type="hidden" name="action" value="login">
        <div class="form-row">
          <label>Username</label>
          <input class="input" type="text" name="username" required>
        </div>
        <div class="form-row">
          <label>Password</label>
          <input class="input" type="password" name="password" required>
        </div>
        <div style="display:flex; gap:10px; justify-content:flex-end;">
          <button type="button" class="btn secondary" id="close-login">Cancel</button>
          <button type="submit" class="btn">Sign In</button>
        </div>
      </form>
      <p class="muted" style="margin-top:10px; font-size:12px;">First time? The first credentials you enter will create the admin account.</p>
    </div>
  </div>
  <script>
    (function(){
      const modal = document.getElementById('login-modal');
      const openBtn = document.getElementById('open-login');
      const closeBtn = document.getElementById('close-login');
      if (openBtn) openBtn.addEventListener('click', () => { modal.style.display = 'flex'; });
      if (closeBtn) closeBtn.addEventListener('click', () => { modal.style.display = 'none'; });
      modal && modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });

      // Simple search suggestions
      const input = document.getElementById('q-input');
      let box = null; let lastQ = '';
      function ensureBox(){
        if (!box) {
          box = document.createElement('div');
          box.style.position = 'absolute';
          box.style.top = '54px';
          box.style.left = '16px';
          box.style.right = '16px';
          box.style.zIndex = '40';
          box.style.background = 'var(--surface)';
          box.style.border = '1px solid var(--border)';
          box.style.borderRadius = '12px';
          box.style.overflow = 'hidden';
          document.body.appendChild(box);
        }
        return box;
      }
      function hideBox(){ if (box) { box.style.display = 'none'; } }
      function showBox(){ if (box) { box.style.display = 'block'; } }
      function render(items){
        const b = ensureBox();
        if (!items.length) { hideBox(); return; }
        b.innerHTML = items.map(it => `<a href="/app.php?slug=${encodeURIComponent(it.slug)}" style="display:block;padding:10px 12px;border-bottom:1px solid var(--border);">${it.name} <span class="muted" style="font-size:12px">by ${it.developer}</span></a>`).join('');
        showBox();
      }
      let controller = null;
      input && input.addEventListener('input', async () => {
        const q = input.value.trim();
        if (q === lastQ || q === '') { hideBox(); lastQ = q; return; }
        lastQ = q;
        try {
          if (controller) controller.abort();
          controller = new AbortController();
          const res = await fetch(`/index.php?ajax=1&q=${encodeURIComponent(q)}`, { signal: controller.signal });
          if (!res.ok) return hideBox();
          const data = await res.json();
          render(data);
        } catch(e) { /* ignore */ }
      });
      document.addEventListener('click', (e) => {
        if (!box) return;
        if (!box.contains(e.target) && e.target !== input) hideBox();
      });
    })();
  </script>
  <?php
}

function render_footer(): void {
  echo '<footer>© ' . date('Y') . ' Nightplay. Built for speed and simplicity.</footer>';
  echo '</body></html>';
}

render_header(SITE_NAME . ' – Discover apps');
?>
  <section class="hero">
    <?php if ($q === ''): ?>
      <h1>Welcome to Nightplay</h1>
      <div class="muted">Discover and download apps with a professional, fast experience.</div>
    <?php else: ?>
      <h1>Results for “<?php echo h($q); ?>”</h1>
      <div class="muted"><?php echo count($apps); ?> found</div>
    <?php endif; ?>
  </section>

  <section class="grid">
    <?php foreach ($apps as $app): $lv = latest_version_for_app($pdo, (int)$app['id']); ?>
      <a class="card" href="/app.php?slug=<?php echo h($app['slug']); ?>" aria-label="<?php echo h($app['name']); ?>">
        <div class="card-body">
          <div class="icon">
            <?php if (!empty($app['icon_path']) && file_exists($ROOT_DIR . '/' . $app['icon_path'])): ?>
              <img src="/<?php echo h($app['icon_path']); ?>" alt="<?php echo h($app['name']); ?> icon">
            <?php else: ?>
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 6a3 3 0 013-3h7l5 5v10a3 3 0 01-3 3H6a3 3 0 01-3-3V6z" stroke="#4b5563" stroke-width="1.5"/><path d="M13 3v5h5" stroke="#4b5563" stroke-width="1.5"/></svg>
            <?php endif; ?>
          </div>
          <div>
            <div class="title"><?php echo h($app['name']); ?></div>
            <div class="dev"><?php echo h($app['developer']); ?></div>
            <div class="meta">
              <?php if ($lv): ?>
                <span class="badge">v<?php echo h($lv['version_name']); ?></span>
                <span><?php echo $lv['file_size'] ? number_format((int)$lv['file_size']/1048576, 1) . ' MB' : ''; ?></span>
              <?php else: ?>
                <span class="muted">No release yet</span>
              <?php endif; ?>
            </div>
          </div>
        </div>
      </a>
    <?php endforeach; ?>
    <?php if (!$apps): ?>
      <div class="muted">No apps found.</div>
    <?php endif; ?>
  </section>
<?php render_footer(); ?>