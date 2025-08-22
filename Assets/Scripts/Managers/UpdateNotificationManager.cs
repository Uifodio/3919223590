using System;
using System.Collections;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using TMPro;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace Game.Managers
{
	/// <summary>
	/// UpdateNotificationManager
	/// - Persistent singleton that periodically checks a remote JSON for update info
	/// - Fully inspector-configurable behavior (intervals, scene checks, UI references, gameplay disabling, time pause, etc.)
	/// - Shows an update panel with message and buttons (open link, optional reload, optional dismiss for N minutes)
	/// - Gracefully handles connectivity errors with a small fading toast message
	/// - Designed for WebGL (optional page reload) and other platforms
	/// </summary>
	public sealed class UpdateNotificationManager : MonoBehaviour
	{
		[Serializable]
		private sealed class UpdatePayload
		{
			public string updateCode;
			public string latestVersion;
			public string updateMessage;
			public string updateLink;

			// Optional, if you decide to add these in your JSON later. Defaults handled safely.
			public bool forceUpdate;
			public bool requireReload;
			public int dismissMinutesOverride;
		}

		public static UpdateNotificationManager Instance { get; private set; }

		[Header("Logging")]
		[SerializeField] private bool enableLogging = true;
		[SerializeField] private bool verboseLogging = true;

		[Header("Singleton")]
		[SerializeField] private bool keepFirstInstance = true;
		[SerializeField] private bool makePersistent = true;

		[Header("Local Version Settings")]
		[Tooltip("Local update code to compare against remote JSON's updateCode")] 
		[SerializeField] private string localUpdateCode = "335678";
		[Tooltip("Optionally also compare semantic version strings if enabled")] 
		[SerializeField] private bool alsoCompareSemanticVersion = false;
		[SerializeField] private string localVersion = "1.0.0";

		[Header("Remote JSON Source")]
		[Tooltip("If true, uses the folder of the currently loaded index.html (WebGL) and fetches 'relativeJsonFilename'.")]
		[SerializeField] private bool useRelativeToIndexHtml = true;
		[SerializeField] private string relativeJsonFilename = "update.json";
		[Tooltip("Absolute URL fallback (or primary) to the JSON (e.g., https://example.com/update.json)")]
		[SerializeField] private string remoteJsonAbsoluteUrl = string.Empty;
		[SerializeField] private bool addNoCacheQueryParam = true;

		[Header("Check Triggers")]
		[SerializeField] private bool checkOnStart = true;
		[SerializeField] private bool checkOnSceneLoaded = true;
		[SerializeField] private bool checkOnInterval = true;
		[Min(0.1f)]
		[SerializeField] private float checkIntervalMinutes = 10f;

		[Header("Behavior")]
		[Tooltip("If true, pause Time.timeScale when showing the update panel")]
		[SerializeField] private bool pauseTimeWhenShowing = true;
		[SerializeField] private bool autoReloadPageOnMismatch = true; // default: ON per request
		[SerializeField] private bool showPanelOnMismatch = true;
		[SerializeField] private bool allowDismiss = true;
		[SerializeField] private bool allowDismissEvenIfForceUpdate = false;
		[Min(1)]
		[SerializeField] private int defaultDismissMinutes = 5;

		[Header("Reload Safety")]
		[SerializeField] private bool onlyReloadOncePerSession = true;
		[Min(0f)] [SerializeField] private float reloadDelaySeconds = 0.15f;
		[Min(0f)] [SerializeField] private float reloadCooldownSeconds = 5f;
		private static bool _reloadedThisSession = false;
		private static double _lastReloadUnix = 0;

		[Header("Testing / Overrides")]
		[SerializeField] private bool testingForceMismatch = false;
		[SerializeField] private bool testingForcePanelOnStart = false;
		[SerializeField] private bool testingBypassDismiss = false;

		[Header("UI - Update Panel")]
		[Tooltip("Prefab or scene object to show when an update is available. This will be moved under the manager and persist.")]
		[SerializeField] private GameObject updatePanelPrefab;
		[SerializeField] private GameObject updatePanelInstance;
		[SerializeField] private CanvasGroup updatePanelCanvasGroup;
		[SerializeField] private TMP_Text updateMessageText;
		[SerializeField] private Button openUpdateLinkButton;
		[SerializeField] private Button dismissForMinutesButton;
		[SerializeField] private Button reloadPageButton;

		[Header("Auto UI Fallbacks")]
		[SerializeField] private bool autoCreateDefaultPanelIfMissing = true;
		[SerializeField] private bool autoCreateToastIfMissing = true;

		[Header("Panel Fade")]
		[SerializeField] private bool usePanelFade = true;
		[Min(0f)] [SerializeField] private float panelFadeInDuration = 0.35f;
		[Min(0f)] [SerializeField] private float panelFadeOutDuration = 0.25f;
		[SerializeField] private AnimationCurve panelFadeInCurve = AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);
		[SerializeField] private AnimationCurve panelFadeOutCurve = AnimationCurve.EaseInOut(0f, 1f, 1f, 0f);

		[Header("Gameplay Lockdown")]
		[Tooltip("Objects to disable while the update panel is shown (canvases, managers, gameplay objects).")]
		[SerializeField] private List<GameObject> objectsToDisableOnUpdate = new List<GameObject>();

		[Header("Toast (Fetch Errors)")]
		[SerializeField] private TMP_Text toastText;
		[SerializeField] private CanvasGroup toastCanvasGroup;
		[Min(0.1f)]
		[SerializeField] private float toastDisplaySeconds = 1.0f;
		[Min(0.05f)]
		[SerializeField] private float toastFadeDuration = 0.4f;
		[SerializeField] private string toastFetchFailedMessage = "Couldn't fetch update";

		[Header("Events")]
		public UnityEvent onUpdateAvailable;
		public UnityEvent onUpToDate;
		public UnityEvent onFetchFailed;

		private const string PlayerPrefsDismissKey = "UpdateManager.DismissUntilUtc";
		private const string PlayerPrefsLastRemoteCodeKey = "UpdateManager.LastRemoteCode";

		private UpdatePayload _lastPayload;
		private bool _isPanelVisible;
		private bool _isChecking;
		private Coroutine _intervalRoutine;
		private Coroutine _panelFadeRoutine;
		private float _timeScaleBeforePause = 1f;
		private string _lastResolvedUrl = string.Empty;

		#if UNITY_WEBGL && !UNITY_EDITOR
		[DllImport("__Internal")] private static extern void ReloadPage();
		#endif

		private void Awake()
		{
			if (Instance != null && Instance != this)
			{
				if (keepFirstInstance)
				{
					LogWarn("Another instance detected, destroying this one to keep the first.");
					Destroy(gameObject);
					return;
				}
				else
				{
					LogWarn("Another instance detected, replacing the existing instance with this one.");
					Destroy(Instance.gameObject);
				}
			}

			Instance = this;
			if (makePersistent)
			{
				if (transform.parent != null)
				{
					LogVerbose("Detaching manager from parent to satisfy DontDestroyOnLoad root requirement.");
					transform.SetParent(null, false);
				}
				LogVerbose("Marking manager as DontDestroyOnLoad.");
				DontDestroyOnLoad(gameObject);
			}

			PrepareUpdatePanel();
		}

		private void OnEnable()
		{
			if (checkOnSceneLoaded)
			{
				SceneManager.sceneLoaded += OnSceneLoaded;
				LogVerbose("Subscribed to SceneManager.sceneLoaded");
			}
		}

		private void OnDisable()
		{
			if (checkOnSceneLoaded)
			{
				SceneManager.sceneLoaded -= OnSceneLoaded;
				LogVerbose("Unsubscribed from SceneManager.sceneLoaded");
			}
		}

		private IEnumerator Start()
		{
			LogInfo("UpdateNotificationManager started.");
			if (checkOnInterval)
			{
				_intervalRoutine = StartCoroutine(IntervalChecker());
				LogVerbose($"Interval checker started: every {checkIntervalMinutes} minutes");
			}

			if (checkOnStart)
			{
				LogVerbose("Initial check triggered on Start().");
				yield return CheckForUpdatesRoutine(false);
			}

			if (testingForcePanelOnStart)
			{
				LogWarn("Testing: forcing panel to show on start.");
				_lastPayload = new UpdatePayload { updateMessage = "Testing: Forced panel", updateLink = Application.absoluteURL };
				ShowUpdatePanel(_lastPayload);
			}
		}

		[ContextMenu("Force Check Now")]
		public void ForceCheckNow()
		{
			if (!_isChecking)
			{
				LogInfo("ForceCheckNow invoked.");
				StartCoroutine(CheckForUpdatesRoutine(true));
			}
			else
			{
				LogVerbose("ForceCheckNow ignored because a check is already running.");
			}
		}

		private IEnumerator IntervalChecker()
		{
			var wait = new WaitForSecondsRealtime(Mathf.Max(0.1f, checkIntervalMinutes * 60f));
			while (true)
			{
				yield return wait;
				if (!_isChecking)
				{
					LogVerbose("Interval tick: starting update check.");
					StartCoroutine(CheckForUpdatesRoutine(false));
				}
			}
		}

		private void OnSceneLoaded(Scene scene, LoadSceneMode mode)
		{
			if (checkOnSceneLoaded && !_isChecking)
			{
				LogInfo($"Scene loaded: {scene.name}. Triggering update check.");
				StartCoroutine(CheckForUpdatesRoutine(false));
			}
		}

		private string ResolveJsonUrl()
		{
			if (useRelativeToIndexHtml && !string.IsNullOrEmpty(Application.absoluteURL))
			{
				try
				{
					var baseUri = new Uri(Application.absoluteURL);
					var resolved = new Uri(baseUri, relativeJsonFilename);
					var url = resolved.ToString();
					if (addNoCacheQueryParam) url = AppendNoCacheQuery(url);
					LogVerbose($"Resolved JSON via index.html base: {url}");
					return url;
				}
				catch (Exception ex)
				{
					LogWarn($"Failed to resolve relative JSON URL: {ex.Message}");
				}
			}

			if (!string.IsNullOrEmpty(remoteJsonAbsoluteUrl))
			{
				var url = remoteJsonAbsoluteUrl;
				if (addNoCacheQueryParam) url = AppendNoCacheQuery(url);
				LogVerbose($"Using absolute JSON URL: {url}");
				return url;
			}

			// As a development fallback, allow local StreamingAssets copy
			var localPath = System.IO.Path.Combine(Application.streamingAssetsPath, relativeJsonFilename);
			LogVerbose($"Using StreamingAssets fallback path: {localPath}");
			return localPath;
		}

		private string AppendNoCacheQuery(string url)
		{
			try
			{
				var sep = url.Contains("?") ? "&" : "?";
				return url + sep + "__ts=" + DateTimeOffset.UtcNow.ToUnixTimeSeconds();
			}
			catch { return url; }
		}

		private IEnumerator CheckForUpdatesRoutine(bool isForced)
		{
			_isChecking = true;
			_lastResolvedUrl = ResolveJsonUrl();
			LogInfo($"Starting update check (forced={isForced}) at {_lastResolvedUrl}");

			using (var req = UnityWebRequest.Get(_lastResolvedUrl))
			{
				// strongly discourage caches
				req.SetRequestHeader("Cache-Control", "no-cache, no-store, must-revalidate");
				req.SetRequestHeader("Pragma", "no-cache");
				req.SetRequestHeader("Expires", "0");

				yield return req.SendWebRequest();

				if (req.result != UnityWebRequest.Result.Success)
				{
					LogError($"Fetch failed: {req.error}");
					ShowToast(toastFetchFailedMessage);
					onFetchFailed?.Invoke();
					_isChecking = false;
					yield break;
				}

				var json = req.downloadHandler.text;
				LogVerbose($"Fetched JSON: {json}");
				UpdatePayload payload = null;
				try
				{
					payload = JsonUtility.FromJson<UpdatePayload>(json);
				}
				catch (Exception ex)
				{
					LogError($"Invalid update payload: {ex.Message}");
					ShowToast("Invalid update payload");
					_isChecking = false;
					yield break;
				}

				_lastPayload = payload;
				LogInfo($"Remote updateCode='{payload.updateCode}', latestVersion='{payload.latestVersion}', forceUpdate={payload.forceUpdate}, requireReload={payload.requireReload}");

				bool mismatch = testingForceMismatch || IsUpdateMismatch(payload);
				bool isDismissed = testingBypassDismiss ? false : IsDismissedNow(payload);
				LogInfo($"Mismatch={mismatch}, DismissedNow={isDismissed}");

				if (mismatch && !isDismissed)
				{
					PlayerPrefs.SetString(PlayerPrefsLastRemoteCodeKey, payload.updateCode ?? string.Empty);

					if (showPanelOnMismatch)
					{
						ShowUpdatePanel(payload);
					}

					onUpdateAvailable?.Invoke();

					if (autoReloadPageOnMismatch || (payload != null && payload.requireReload))
					{
						LogInfo("Auto-reload enabled. Attempting to reload page now.");
						AttemptReloadPageWithCooldown();
					}
				}
				else
				{
					HideUpdatePanel();
					onUpToDate?.Invoke();
				}
			}

			_isChecking = false;
		}

		private bool IsUpdateMismatch(UpdatePayload payload)
		{
			if (payload == null) return false;

			if (!string.IsNullOrEmpty(payload.updateCode))
			{
				if (!string.Equals(payload.updateCode, localUpdateCode, StringComparison.Ordinal))
				{
					LogVerbose($"Update code mismatch: remote='{payload.updateCode}', local='{localUpdateCode}'");
					return true;
				}
			}

			if (alsoCompareSemanticVersion && !string.IsNullOrEmpty(payload.latestVersion))
			{
				try
				{
					if (IsNewerVersion(payload.latestVersion, localVersion))
					{
						LogVerbose($"Version mismatch: remote='{payload.latestVersion}' > local='{localVersion}'");
						return true;
					}
				}
				catch (Exception ex)
				{
					LogWarn($"Version compare failed: {ex.Message}");
				}
			}

			return false;
		}

		private static bool IsNewerVersion(string remote, string local)
		{
			System.Version r = new System.Version(remote);
			System.Version l = new System.Version(local);
			return r > l;
		}

		private bool IsDismissedNow(UpdatePayload payload)
		{
			if (!allowDismiss) return false;
			if (payload != null && payload.forceUpdate && !allowDismissEvenIfForceUpdate) return false;

			var stored = PlayerPrefs.GetString(PlayerPrefsDismissKey, string.Empty);
			if (string.IsNullOrEmpty(stored)) return false;
			if (!double.TryParse(stored, out var untilUnix)) return false;

			double nowUnix = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
			return nowUnix < untilUnix;
		}

		private void DismissForMinutes()
		{
			if (!allowDismiss) { LogVerbose("Dismiss ignored: dismiss disabled in settings."); return; }
			if (_lastPayload != null && _lastPayload.forceUpdate && !allowDismissEvenIfForceUpdate) { LogVerbose("Dismiss ignored: forceUpdate active and dismiss not allowed."); return; }

			int minutes = defaultDismissMinutes;
			if (_lastPayload != null && _lastPayload.dismissMinutesOverride > 0)
			{
				minutes = _lastPayload.dismissMinutesOverride;
			}

			double untilUnix = DateTimeOffset.UtcNow.ToUnixTimeSeconds() + (minutes * 60);
			PlayerPrefs.SetString(PlayerPrefsDismissKey, untilUnix.ToString());
			PlayerPrefs.Save();
			LogInfo($"Dismissed update for {minutes} minute(s). Hiding panel.");

			HideUpdatePanel();
		}

		private void ShowUpdatePanel(UpdatePayload payload)
		{
			PrepareUpdatePanel();

			// Wire content
			if (updateMessageText == null)
			{
				updateMessageText = TryAutoFindMessageText(updatePanelInstance);
			}
			if (updateMessageText != null)
			{
				updateMessageText.text = string.IsNullOrEmpty(payload.updateMessage) ? "Update available" : payload.updateMessage;
				LogVerbose($"Set update message text: '{updateMessageText.text}'");
			}
			else
			{
				LogWarn("No TMP_Text assigned/found for update message.");
			}

			if (openUpdateLinkButton == null || dismissForMinutesButton == null || reloadPageButton == null)
			{
				AutoWireButtons(updatePanelInstance);
			}

			if (openUpdateLinkButton != null)
			{
				openUpdateLinkButton.onClick.RemoveListener(OpenUpdateLink);
				openUpdateLinkButton.onClick.AddListener(OpenUpdateLink);
			}

			if (dismissForMinutesButton != null)
			{
				dismissForMinutesButton.onClick.RemoveListener(DismissForMinutes);
				dismissForMinutesButton.onClick.AddListener(DismissForMinutes);
				dismissForMinutesButton.gameObject.SetActive(allowDismiss && (!(_lastPayload?.forceUpdate ?? false) || allowDismissEvenIfForceUpdate));
			}

			if (reloadPageButton != null)
			{
				reloadPageButton.onClick.RemoveAllListeners();
				reloadPageButton.onClick.AddListener(AttemptReloadPage);
				reloadPageButton.gameObject.SetActive(true);
			}

			SetGameplayDisabled(true);
			ShowPanel();
		}

		private void HideUpdatePanel()
		{
			HidePanel();
			SetGameplayDisabled(false);
		}

		private void ShowPanel()
		{
			if (updatePanelInstance == null) return;

			EnsureCanvasGroup();
			updatePanelInstance.SetActive(true);
			_isPanelVisible = true;

			if (pauseTimeWhenShowing)
			{
				_timeScaleBeforePause = Time.timeScale;
				Time.timeScale = 0f;
				LogVerbose("Time paused (Time.timeScale = 0) while showing panel.");
			}

			StartPanelFade(targetAlpha: 1f, duration: panelFadeInDuration, curve: panelFadeInCurve);
		}

		private void HidePanel()
		{
			if (updatePanelInstance == null) return;
			EnsureCanvasGroup();
			_isPanelVisible = false;
			StartPanelFade(targetAlpha: 0f, duration: panelFadeOutDuration, curve: panelFadeOutCurve, onComplete: () =>
			{
				updatePanelInstance.SetActive(false);
				if (pauseTimeWhenShowing)
				{
					Time.timeScale = _timeScaleBeforePause;
					LogVerbose($"Time resumed (Time.timeScale = {_timeScaleBeforePause}).");
				}
			});
		}

		private void StartPanelFade(float targetAlpha, float duration, AnimationCurve curve, Action onComplete = null)
		{
			if (!usePanelFade || updatePanelCanvasGroup == null || duration <= 0f)
			{
				updatePanelCanvasGroup.alpha = targetAlpha;
				updatePanelCanvasGroup.blocksRaycasts = targetAlpha > 0.99f;
				updatePanelCanvasGroup.interactable = targetAlpha > 0.99f;
				onComplete?.Invoke();
				return;
			}

			if (_panelFadeRoutine != null)
			{
				StopCoroutine(_panelFadeRoutine);
			}
			_panelFadeRoutine = StartCoroutine(PanelFadeRoutine(targetAlpha, duration, curve, onComplete));
		}

		private IEnumerator PanelFadeRoutine(float targetAlpha, float duration, AnimationCurve curve, Action onComplete)
		{
			float startAlpha = updatePanelCanvasGroup.alpha;
			float t = 0f;
			while (t < duration)
			{
				t += Time.unscaledDeltaTime;
				float a = Mathf.Lerp(startAlpha, targetAlpha, curve.Evaluate(Mathf.Clamp01(t / duration)));
				updatePanelCanvasGroup.alpha = a;
				yield return null;
			}
			updatePanelCanvasGroup.alpha = targetAlpha;
			updatePanelCanvasGroup.blocksRaycasts = targetAlpha > 0.99f;
			updatePanelCanvasGroup.interactable = targetAlpha > 0.99f;
			onComplete?.Invoke();
		}

		private void SetGameplayDisabled(bool disabled)
		{
			if (objectsToDisableOnUpdate == null) return;
			for (int i = 0; i < objectsToDisableOnUpdate.Count; i++)
			{
				var obj = objectsToDisableOnUpdate[i];
				if (obj == null) continue;
				obj.SetActive(!disabled);
			}
			LogVerbose($"Gameplay objects {(disabled ? "disabled" : "enabled")}.");
		}

		private void PrepareUpdatePanel()
		{
			// If we don't have an instance in the scene yet, instantiate from prefab
			if (updatePanelInstance == null && updatePanelPrefab != null)
			{
				updatePanelInstance = Instantiate(updatePanelPrefab);
				LogVerbose("Instantiated update panel prefab.");
			}

			// Auto-create a simple default panel if still missing
			if (updatePanelInstance == null && autoCreateDefaultPanelIfMissing)
			{
				LogWarn("No update panel assigned. Auto-creating a default panel.");
				CreateDefaultUpdatePanel();
			}

			if (updatePanelInstance != null)
			{
				if (makePersistent)
				{
					// Must be root before DontDestroyOnLoad
					if (updatePanelInstance.transform.parent != null)
					{
						updatePanelInstance.transform.SetParent(null, false);
						LogVerbose("Detached update panel to root for persistence.");
					}
					DontDestroyOnLoad(updatePanelInstance);
					LogVerbose("Marked update panel as DontDestroyOnLoad.");
				}

				EnsureCanvasGroup();

				// Try to auto-wire message text if not set
				if (updateMessageText == null)
				{
					updateMessageText = TryAutoFindMessageText(updatePanelInstance);
				}

				// Try to auto-wire buttons if not set
				if (openUpdateLinkButton == null || dismissForMinutesButton == null || reloadPageButton == null)
				{
					AutoWireButtons(updatePanelInstance);
				}

				// Ensure hidden at start
				updatePanelCanvasGroup.alpha = 0f;
				updatePanelCanvasGroup.blocksRaycasts = false;
				updatePanelCanvasGroup.interactable = false;
				updatePanelInstance.SetActive(false);
			}
		}

		private void CreateDefaultUpdatePanel()
		{
			// Canvas root
			var canvasGO = new GameObject("UpdatePanelCanvas");
			var canvas = canvasGO.AddComponent<Canvas>();
			canvas.renderMode = RenderMode.ScreenSpaceOverlay;
			canvas.sortingOrder = 5000;
			canvas.pixelPerfect = false;
			canvasGO.AddComponent<CanvasScaler>();
			canvasGO.AddComponent<GraphicRaycaster>();
			var cg = canvasGO.AddComponent<CanvasGroup>();
			cg.alpha = 0f;
			cg.blocksRaycasts = false;
			cg.interactable = false;

			// Background dimmer
			var bg = new GameObject("Dimmer");
			bg.transform.SetParent(canvasGO.transform, false);
			var bgRect = bg.AddComponent<RectTransform>();
			bgRect.anchorMin = Vector2.zero; bgRect.anchorMax = Vector2.one; bgRect.offsetMin = Vector2.zero; bgRect.offsetMax = Vector2.zero;
			var bgImg = bg.AddComponent<Image>();
			bgImg.color = new Color(0f, 0f, 0f, 0.5f);

			// Window
			var win = new GameObject("Window");
			win.transform.SetParent(canvasGO.transform, false);
			var winRect = win.AddComponent<RectTransform>();
			winRect.sizeDelta = new Vector2(640, 360);
			winRect.anchorMin = new Vector2(0.5f, 0.5f); winRect.anchorMax = new Vector2(0.5f, 0.5f);
			winRect.anchoredPosition = Vector2.zero;
			var winImg = win.AddComponent<Image>();
			winImg.color = new Color(0.13f, 0.13f, 0.13f, 0.96f);

			// Message
			var msgGO = new GameObject("MessageText");
			msgGO.transform.SetParent(win.transform, false);
			var msgRect = msgGO.AddComponent<RectTransform>();
			msgRect.anchorMin = new Vector2(0.1f, 0.55f); msgRect.anchorMax = new Vector2(0.9f, 0.9f);
			msgRect.offsetMin = Vector2.zero; msgRect.offsetMax = Vector2.zero;
			var msgTMP = msgGO.AddComponent<TextMeshProUGUI>();
			msgTMP.fontSize = 28f;
			msgTMP.alignment = TextAlignmentOptions.Center;
			msgTMP.color = Color.white;
			msgTMP.text = "Update available";

			// Buttons row
			var btnY = -110f;
			openUpdateLinkButton = CreateButton(win.transform, new Vector2(-160f, btnY), new Vector2(200f, 60f), "Open");
			dismissForMinutesButton = CreateButton(win.transform, new Vector2(0f, btnY), new Vector2(200f, 60f), "Dismiss");
			reloadPageButton = CreateButton(win.transform, new Vector2(160f, btnY), new Vector2(200f, 60f), "Reload");

			updatePanelInstance = canvasGO;
			updatePanelCanvasGroup = cg;
			updateMessageText = msgTMP;
		}

		private Button CreateButton(Transform parent, Vector2 anchoredPos, Vector2 size, string label)
		{
			var go = new GameObject(label + "Button");
			go.transform.SetParent(parent, false);
			var rect = go.AddComponent<RectTransform>();
			rect.sizeDelta = size;
			rect.anchorMin = rect.anchorMax = new Vector2(0.5f, 0.5f);
			rect.anchoredPosition = anchoredPos;
			var img = go.AddComponent<Image>();
			img.color = new Color(0.22f, 0.22f, 0.22f, 1f);
			var btn = go.AddComponent<Button>();
			var txtGO = new GameObject("Label");
			txtGO.transform.SetParent(go.transform, false);
			var txtRect = txtGO.AddComponent<RectTransform>();
			txtRect.anchorMin = new Vector2(0.1f, 0.1f); txtRect.anchorMax = new Vector2(0.9f, 0.9f);
			var tmp = txtGO.AddComponent<TextMeshProUGUI>();
			tmp.text = label;
			tmp.alignment = TextAlignmentOptions.Center;
			tmp.color = Color.white;
			return btn;
		}

		private void EnsureCanvasGroup()
		{
			if (updatePanelInstance == null) return;
			if (updatePanelCanvasGroup == null)
			{
				updatePanelCanvasGroup = updatePanelInstance.GetComponentInChildren<CanvasGroup>(true);
				if (updatePanelCanvasGroup == null)
				{
					updatePanelCanvasGroup = updatePanelInstance.AddComponent<CanvasGroup>();
					LogVerbose("Added CanvasGroup to update panel instance.");
				}
			}
		}

		private TMP_Text TryAutoFindMessageText(GameObject root)
		{
			if (root == null) return null;
			var texts = root.GetComponentsInChildren<TMP_Text>(true);
			foreach (var t in texts)
			{
				var n = t.gameObject.name.ToLower();
				if (n.Contains("message") || n.Contains("update")) return t;
			}
			return texts.Length > 0 ? texts[0] : null;
		}

		private void AutoWireButtons(GameObject root)
		{
			if (root == null) return;
			var buttons = root.GetComponentsInChildren<Button>(true);
			foreach (var b in buttons)
			{
				var n = b.name.ToLower();
				if (openUpdateLinkButton == null && (n.Contains("update") || n.Contains("link") || n.Contains("store") || ContainsLabel(b, "update") || ContainsLabel(b, "open"))) openUpdateLinkButton = b;
				if (dismissForMinutesButton == null && (n.Contains("dismiss") || n.Contains("later") || n.Contains("close") || ContainsLabel(b, "dismiss") || ContainsLabel(b, "later") || ContainsLabel(b, "close"))) dismissForMinutesButton = b;
				if (reloadPageButton == null && (n.Contains("reload") || n.Contains("refresh") || n.Contains("restart") || ContainsLabel(b, "reload") || ContainsLabel(b, "refresh"))) reloadPageButton = b;
			}
		}

		private bool ContainsLabel(Button b, string keyword)
		{
			if (b == null) return false;
			var texts = b.GetComponentsInChildren<TMP_Text>(true);
			for (int i = 0; i < texts.Length; i++)
			{
				if (!string.IsNullOrEmpty(texts[i].text) && texts[i].text.ToLower().Contains(keyword)) return true;
			}
			return false;
		}

		private void OpenUpdateLink()
		{
			var link = _lastPayload != null ? _lastPayload.updateLink : string.Empty;
			if (string.IsNullOrEmpty(link)) { LogWarn("OpenUpdateLink ignored: link is empty."); return; }
			LogInfo($"Opening update link: {link}");
			Application.OpenURL(link);
		}

		private void AttemptReloadPageWithCooldown()
		{
			double now = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
			if (onlyReloadOncePerSession && _reloadedThisSession)
			{
				LogWarn("Reload suppressed: already reloaded this session.");
				return;
			}
			if (now - _lastReloadUnix < reloadCooldownSeconds)
			{
				LogWarn("Reload suppressed: cooldown active.");
				return;
			}
			_lastReloadUnix = now;
			StartCoroutine(ReloadAfterDelay());
		}

		private IEnumerator ReloadAfterDelay()
		{
			if (reloadDelaySeconds > 0f)
			{
				LogVerbose($"Waiting {reloadDelaySeconds} seconds before reload...");
				yield return new WaitForSecondsRealtime(reloadDelaySeconds);
			}
			_reloadedThisSession = true;
			AttemptReloadPage();
		}

		public void AttemptReloadPage()
		{
			#if UNITY_WEBGL && !UNITY_EDITOR
			try { LogInfo("Reloading WebGL page via JS"); ReloadPage(); } catch (Exception ex) { LogWarn($"ReloadPage JS call failed: {ex.Message}"); }
			#else
			// Non-WebGL fallback: reopen current URL if available
			if (!string.IsNullOrEmpty(Application.absoluteURL))
			{
				LogInfo($"Reopening URL: {Application.absoluteURL}");
				Application.OpenURL(Application.absoluteURL);
			}
			else
			{
				LogWarn("Cannot reload page: Application.absoluteURL is empty.");
			}
			#endif
		}

		private void ShowToast(string message)
		{
			if ((toastText == null || toastCanvasGroup == null) && autoCreateToastIfMissing)
			{
				LogWarn("Toast UI missing. Auto-creating a default toast.");
				CreateDefaultToastUI();
			}
			if (toastText == null || toastCanvasGroup == null)
			{
				LogWarn($"Toast requested but toast UI not wired. Message: {message}");
				return;
			}

			StopCoroutineSafe("ToastRoutine");
			StartCoroutine(ToastRoutine(message));
		}

		private void CreateDefaultToastUI()
		{
			var canvasGO = new GameObject("UpdateToastCanvas");
			var canvas = canvasGO.AddComponent<Canvas>();
			canvas.renderMode = RenderMode.ScreenSpaceOverlay;
			canvas.sortingOrder = 6000;
			canvasGO.AddComponent<CanvasScaler>();
			canvasGO.AddComponent<GraphicRaycaster>();
			var cg = canvasGO.AddComponent<CanvasGroup>();
			cg.alpha = 0f;
			cg.blocksRaycasts = false;
			cg.interactable = false;

			var txtGO = new GameObject("ToastText");
			txtGO.transform.SetParent(canvasGO.transform, false);
			var rt = txtGO.AddComponent<RectTransform>();
			rt.anchorMin = new Vector2(0.5f, 1f); rt.anchorMax = new Vector2(0.5f, 1f);
			rt.anchoredPosition = new Vector2(0f, -40f);
			rt.sizeDelta = new Vector2(900f, 80f);
			var tmp = txtGO.AddComponent<TextMeshProUGUI>();
			tmp.alignment = TextAlignmentOptions.Center;
			tmp.fontSize = 24f;
			tmp.color = Color.white;
			var bg = txtGO.AddComponent<Image>();
			bg.color = new Color(0f, 0f, 0f, 0.7f);

			toastCanvasGroup = cg;
			toastText = tmp;

			if (makePersistent)
			{
				if (canvasGO.transform.parent != null) canvasGO.transform.SetParent(null, false);
				DontDestroyOnLoad(canvasGO);
			}
		}

		private IEnumerator ToastRoutine(string message)
		{
			toastText.text = message;
			toastCanvasGroup.alpha = 0f;
			toastCanvasGroup.gameObject.SetActive(true);

			float t = 0f;
			while (t < toastFadeDuration)
			{
				t += Time.unscaledDeltaTime;
				toastCanvasGroup.alpha = Mathf.Lerp(0f, 1f, t / toastFadeDuration);
				yield return null;
			}
			toastCanvasGroup.alpha = 1f;

			yield return new WaitForSecondsRealtime(toastDisplaySeconds);

			t = 0f;
			while (t < toastFadeDuration)
			{
				t += Time.unscaledDeltaTime;
				toastCanvasGroup.alpha = Mathf.Lerp(1f, 0f, t / toastFadeDuration);
				yield return null;
			}

			toastCanvasGroup.alpha = 0f;
			toastCanvasGroup.gameObject.SetActive(false);
		}

		private void StopCoroutineSafe(string methodName)
		{
			try { StopCoroutine(methodName); } catch { /* ignored */ }
		}

		private void LogInfo(string message) { if (enableLogging) Debug.Log($"[UpdateManager] {message}", this); }
		private void LogWarn(string message) { if (enableLogging) Debug.LogWarning($"[UpdateManager] {message}", this); }
		private void LogError(string message) { if (enableLogging) Debug.LogError($"[UpdateManager] {message}", this); }
		private void LogVerbose(string message) { if (enableLogging && verboseLogging) Debug.Log($"[UpdateManager][Verbose] {message}", this); }
	}
}