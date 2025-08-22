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

		[Header("Check Triggers")]
		[SerializeField] private bool checkOnStart = true;
		[SerializeField] private bool checkOnSceneLoaded = true;
		[SerializeField] private bool checkOnInterval = true;
		[Min(0.1f)]
		[SerializeField] private float checkIntervalMinutes = 10f;

		[Header("Behavior")]
		[Tooltip("If true, pause Time.timeScale when showing the update panel")]
		[SerializeField] private bool pauseTimeWhenShowing = true;
		[SerializeField] private bool autoReloadPageOnMismatch = false;
		[SerializeField] private bool showPanelOnMismatch = true;
		[SerializeField] private bool allowDismiss = true;
		[SerializeField] private bool allowDismissEvenIfForceUpdate = false;
		[Min(1)]
		[SerializeField] private int defaultDismissMinutes = 5;

		[Header("UI - Update Panel")]
		[Tooltip("Prefab or scene object to show when an update is available. This will be moved under the manager and persist.")]
		[SerializeField] private GameObject updatePanelPrefab;
		[SerializeField] private GameObject updatePanelInstance;
		[SerializeField] private CanvasGroup updatePanelCanvasGroup;
		[SerializeField] private TMP_Text updateMessageText;
		[SerializeField] private Button openUpdateLinkButton;
		[SerializeField] private Button dismissForMinutesButton;
		[SerializeField] private Button reloadPageButton;

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
		private float _timeScaleBeforePause = 1f;

		#if UNITY_WEBGL && !UNITY_EDITOR
		[DllImport("__Internal")] private static extern void ReloadPage();
		#endif

		private void Awake()
		{
			if (Instance != null && Instance != this)
			{
				if (keepFirstInstance)
				{
					Destroy(gameObject);
					return;
				}
				else
				{
					Destroy(Instance.gameObject);
				}
			}

			Instance = this;
			if (makePersistent)
			{
				DontDestroyOnLoad(gameObject);
			}

			PrepareUpdatePanel();
		}

		private void OnEnable()
		{
			if (checkOnSceneLoaded)
			{
				SceneManager.sceneLoaded += OnSceneLoaded;
			}
		}

		private void OnDisable()
		{
			if (checkOnSceneLoaded)
			{
				SceneManager.sceneLoaded -= OnSceneLoaded;
			}
		}

		private IEnumerator Start()
		{
			if (checkOnInterval)
			{
				_intervalRoutine = StartCoroutine(IntervalChecker());
			}

			if (checkOnStart)
			{
				yield return CheckForUpdatesRoutine(false);
			}
		}

		[ContextMenu("Force Check Now")]
		public void ForceCheckNow()
		{
			if (!_isChecking)
			{
				StartCoroutine(CheckForUpdatesRoutine(true));
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
					StartCoroutine(CheckForUpdatesRoutine(false));
				}
			}
		}

		private void OnSceneLoaded(Scene scene, LoadSceneMode mode)
		{
			if (checkOnSceneLoaded && !_isChecking)
			{
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
					return resolved.ToString();
				}
				catch { /* ignored */ }
			}

			if (!string.IsNullOrEmpty(remoteJsonAbsoluteUrl))
			{
				return remoteJsonAbsoluteUrl;
			}

			// As a development fallback, allow local StreamingAssets copy
			var localPath = System.IO.Path.Combine(Application.streamingAssetsPath, relativeJsonFilename);
			return localPath;
		}

		private IEnumerator CheckForUpdatesRoutine(bool isForced)
		{
			_isChecking = true;

			string url = ResolveJsonUrl();
			using (var req = UnityWebRequest.Get(url))
			{
				// strongly discourage caches
				req.SetRequestHeader("Cache-Control", "no-cache, no-store, must-revalidate");
				req.SetRequestHeader("Pragma", "no-cache");
				req.SetRequestHeader("Expires", "0");

				yield return req.SendWebRequest();

				if (req.result != UnityWebRequest.Result.Success)
				{
					ShowToast(toastFetchFailedMessage);
					onFetchFailed?.Invoke();
					_isChecking = false;
					yield break;
				}

				var json = req.downloadHandler.text;
				UpdatePayload payload = null;
				try
				{
					payload = JsonUtility.FromJson<UpdatePayload>(json);
				}
				catch (Exception)
				{
					ShowToast("Invalid update payload");
					_isChecking = false;
					yield break;
				}

				_lastPayload = payload;

				bool mismatch = IsUpdateMismatch(payload);
				bool isDismissed = IsDismissedNow(payload);

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
						AttemptReloadPage();
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
					return true;
				}
			}

			if (alsoCompareSemanticVersion && !string.IsNullOrEmpty(payload.latestVersion))
			{
				try
				{
					if (IsNewerVersion(payload.latestVersion, localVersion))
					{
						return true;
					}
				}
				catch { /* ignored */ }
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
			if (!allowDismiss) return;
			if (_lastPayload != null && _lastPayload.forceUpdate && !allowDismissEvenIfForceUpdate) return;

			int minutes = defaultDismissMinutes;
			if (_lastPayload != null && _lastPayload.dismissMinutesOverride > 0)
			{
				minutes = _lastPayload.dismissMinutesOverride;
			}

			double untilUnix = DateTimeOffset.UtcNow.ToUnixTimeSeconds() + (minutes * 60);
			PlayerPrefs.SetString(PlayerPrefsDismissKey, untilUnix.ToString());
			PlayerPrefs.Save();

			HideUpdatePanel();
		}

		private void ShowUpdatePanel(UpdatePayload payload)
		{
			PrepareUpdatePanel();

			if (updateMessageText != null)
			{
				updateMessageText.text = string.IsNullOrEmpty(payload.updateMessage) ? "Update available" : payload.updateMessage;
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
			SetPanelVisible(true);
		}

		private void HideUpdatePanel()
		{
			SetPanelVisible(false);
			SetGameplayDisabled(false);
		}

		private void SetPanelVisible(bool visible)
		{
			_isPanelVisible = visible;

			if (updatePanelInstance != null)
			{
				updatePanelInstance.SetActive(visible);
			}

			if (updatePanelCanvasGroup != null)
			{
				updatePanelCanvasGroup.alpha = visible ? 1f : 0f;
				updatePanelCanvasGroup.blocksRaycasts = visible;
				updatePanelCanvasGroup.interactable = visible;
			}

			if (pauseTimeWhenShowing)
			{
				if (visible)
				{
					_timeScaleBeforePause = Time.timeScale;
					Time.timeScale = 0f;
				}
				else
				{
					Time.timeScale = _timeScaleBeforePause;
				}
			}
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
		}

		private void PrepareUpdatePanel()
		{
			// If we don't have an instance in the scene yet, instantiate from prefab
			if (updatePanelInstance == null && updatePanelPrefab != null)
			{
				updatePanelInstance = Instantiate(updatePanelPrefab, transform);
			}

			if (updatePanelInstance != null)
			{
				if (makePersistent)
				{
					DontDestroyOnLoad(updatePanelInstance);
				}

				// Try to auto-wire references if not set
				if (updatePanelCanvasGroup == null)
				{
					updatePanelCanvasGroup = updatePanelInstance.GetComponentInChildren<CanvasGroup>(true);
				}
				if (updateMessageText == null)
				{
					updateMessageText = updatePanelInstance.GetComponentInChildren<TMP_Text>(true);
				}
				if (openUpdateLinkButton == null || dismissForMinutesButton == null || reloadPageButton == null)
				{
					var buttons = updatePanelInstance.GetComponentsInChildren<Button>(true);
					foreach (var b in buttons)
					{
						// Heuristic: name-based auto-binding if empty
						if (openUpdateLinkButton == null && b.name.ToLower().Contains("update")) openUpdateLinkButton = b;
						if (dismissForMinutesButton == null && b.name.ToLower().Contains("dismiss")) dismissForMinutesButton = b;
						if (reloadPageButton == null && (b.name.ToLower().Contains("reload") || b.name.ToLower().Contains("refresh"))) reloadPageButton = b;
					}
				}

				// Ensure hidden at start
				SetPanelVisible(false);
			}
		}

		private void OpenUpdateLink()
		{
			var link = _lastPayload != null ? _lastPayload.updateLink : string.Empty;
			if (string.IsNullOrEmpty(link)) return;
			Application.OpenURL(link);
		}

		public void AttemptReloadPage()
		{
			#if UNITY_WEBGL && !UNITY_EDITOR
			try { ReloadPage(); } catch { /* ignored */ }
			#else
			// Non-WebGL fallback: reopen current URL if available
			if (!string.IsNullOrEmpty(Application.absoluteURL))
			{
				Application.OpenURL(Application.absoluteURL);
			}
			#endif
		}

		private void ShowToast(string message)
		{
			if (toastText == null || toastCanvasGroup == null)
			{
				// No toast UI provided; silently ignore but keep console info
				Debug.LogWarning(message);
				return;
			}

			StopCoroutineSafe("ToastRoutine");
			StartCoroutine(ToastRoutine(message));
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
	}
}