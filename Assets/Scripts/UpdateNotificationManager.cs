using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using TMPro;

[DefaultExecutionOrder(-1000)]
[DisallowMultipleComponent]
[AddComponentMenu("Update System/Update Notification Manager")]
public class UpdateNotificationManager : MonoBehaviour
{
	public static UpdateNotificationManager Instance { get; private set; }

	public enum UpdateDecisionMode
	{
		UpdateCodeMismatch,
		SemVerGreater,
		Either,
		Both
	}

	public enum UpdateRequirement
	{
		Optional,
		Forced
	}

	[Header("Singleton & Lifecycle")]
	[SerializeField] private bool enforceSingleton = true;
	[SerializeField] private bool persistAcrossScenes = true;
	[SerializeField] private bool persistPopupCanvas = true;

	[Header("Remote Config")]
	[Tooltip("URL to update.json. GitHub blob links are auto-normalized to RAW.")]
	[SerializeField] private string updateJsonUrl = "";
	[Tooltip("Local update code. If remote updateCode differs, update may be required depending on Decision Mode.")]
	[SerializeField] private string currentUpdateCode = "0";
	[Tooltip("Local app version (SemVer). Used only when Decision Mode includes SemVer.")]
	[SerializeField] private string localVersion = "1.0.0";
	[SerializeField] private UpdateDecisionMode decisionMode = UpdateDecisionMode.UpdateCodeMismatch;
	[SerializeField] private UpdateRequirement updateRequirement = UpdateRequirement.Forced;
	[Tooltip("Run a check immediately on Start().")]
	[SerializeField] private bool checkOnStart = true;
	[Tooltip("Run a check whenever a new scene is loaded.")]
	[SerializeField] private bool checkOnSceneLoaded = true;
	[Tooltip("Run periodic checks at a configurable interval.")]
	[SerializeField] private bool enablePeriodicChecks = true;
	[Tooltip("Interval in minutes between periodic checks.")]
	[SerializeField] private float checkIntervalMinutes = 10f;
	[Tooltip("Network request timeout in seconds.")]
	[SerializeField] private int requestTimeoutSeconds = 10;
	[Tooltip("Max retry attempts on failure.")]
	[SerializeField] private int maxRetryCount = 2;
	[Tooltip("Base seconds for exponential backoff between retries.")]
	[SerializeField] private float retryBackoffBaseSeconds = 1.5f;
	[Tooltip("Detect and auto-use RAW URL for GitHub blob links.")]
	[SerializeField] private bool autoNormalizeGitHubUrl = true;
	[Tooltip("If the first attempt fails or returns HTML, try normalized RAW URL.")]
	[SerializeField] private bool fallbackToNormalizedUrlOnError = true;
	[Tooltip("Enable extra debug logs.")]
	[SerializeField] private bool enableDetailedLogs = false;

	[Header("Popup UI")]
	[SerializeField] private GameObject updateCanvasRoot;
	[SerializeField] private TextMeshProUGUI updateMessageText;
	[SerializeField] private Button updateButton;
	[SerializeField] private string updateButtonUrlOverride = "";
	[Tooltip("Optional: Display a custom title above the message.")]
	[SerializeField] private TextMeshProUGUI updateTitleText;
	[SerializeField] private string forcedUpdateTitle = "Update required";
	[SerializeField] private string optionalUpdateTitle = "Update available";
	[Tooltip("Optional CanvasGroup used for popup fade in/out. If null, one will be added at runtime.")]
	[SerializeField] private CanvasGroup popupCanvasGroup;
	[SerializeField] private float popupFadeSeconds = 0.25f;

	[Header("Gameplay Blocking")]
	[SerializeField] private List<GameObject> objectsToDisableOnUpdate = new List<GameObject>();
	[SerializeField] private bool reenableObjectsWhenPopupHidden = false;
	[SerializeField] private bool pauseTimeOnPopup = true;

	[Header("Persistence")]
	[SerializeField] private bool rememberDismissedUpdateCode = true;
	[SerializeField] private string playerPrefsDismissKey = "UpdateManager.LastDismissedCode";

	[Serializable]
	private class RemoteUpdateInfo
	{
		public string updateCode;
		public string latestVersion;
		public string updateMessage;
		public string updateLink;
	}

	private RemoteUpdateInfo latestRemote;
	private Coroutine periodicRoutine;
	private Coroutine popupFadeRoutine;
	private bool isShowingPopup;
	private bool isRequestInFlight;
	private float previousTimeScale = 1f;

	private void Awake()
	{
		if (Instance != null && Instance != this)
		{
			if (enforceSingleton)
			{
				Destroy(gameObject);
				return;
			}
		}

		Instance = this;

		if (persistAcrossScenes)
		{
			DontDestroyOnLoad(gameObject);
		}

		if (persistPopupCanvas && updateCanvasRoot != null)
		{
			DontDestroyOnLoad(updateCanvasRoot);
		}

		if (updateCanvasRoot != null)
		{
			updateCanvasRoot.SetActive(false);
			EnsurePopupCanvasGroup();
			if (popupCanvasGroup != null) popupCanvasGroup.alpha = 0f;
		}

		WireUpButtons();

		if (checkOnSceneLoaded)
		{
			SceneManager.sceneLoaded += HandleSceneLoaded;
		}
	}

	private void Start()
	{
		if (checkOnStart)
		{
			ForceCheckNow();
		}

		if (enablePeriodicChecks && checkIntervalMinutes > 0f)
		{
			periodicRoutine = StartCoroutine(PeriodicCheck());
		}
	}

	private void OnDestroy()
	{
		if (Instance == this)
		{
			Instance = null;
		}

		SceneManager.sceneLoaded -= HandleSceneLoaded;

		UnwireButtons();
	}

	[ContextMenu("Force Check Now")]
	public void ForceCheckNow()
	{
		if (!gameObject.activeInHierarchy)
		{
			return;
		}
		StartCoroutine(CheckForUpdates());
	}

	private void HandleSceneLoaded(Scene scene, LoadSceneMode mode)
	{
		if (checkOnSceneLoaded)
		{
			ForceCheckNow();
		}
	}

	private IEnumerator PeriodicCheck()
	{
		var wait = new WaitForSeconds(Mathf.Max(1f, checkIntervalMinutes * 60f));
		while (true)
		{
			yield return wait;
			ForceCheckNow();
		}
	}

	private IEnumerator CheckForUpdates()
	{
		if (isRequestInFlight)
		{
			if (enableDetailedLogs) Debug.Log("[UpdateNotificationManager] Request already in flight, skipping.");
			yield break;
		}

		if (Application.internetReachability == NetworkReachability.NotReachable)
		{
			if (enableDetailedLogs) Debug.Log("[UpdateNotificationManager] No internet connection");
			yield break;
		}

		if (string.IsNullOrWhiteSpace(updateJsonUrl))
		{
			Debug.LogWarning("[UpdateNotificationManager] updateJsonUrl is empty; set it in the inspector.");
			yield break;
		}

		isRequestInFlight = true;
		string primaryUrl = updateJsonUrl.Trim();
		string normalizedUrl = autoNormalizeGitHubUrl ? NormalizeGitHubRawUrl(primaryUrl) : primaryUrl;

		RemoteUpdateInfo remote = null;
		string lastError = null;
		string usedUrl = primaryUrl;

		for (int attempt = 0; attempt <= Mathf.Max(0, maxRetryCount); attempt++)
		{
			string tryUrl = (attempt == 0) ? primaryUrl : normalizedUrl;
			if (fallbackToNormalizedUrlOnError && !string.Equals(primaryUrl, normalizedUrl, StringComparison.Ordinal))
			{
				tryUrl = (attempt % 2 == 0) ? primaryUrl : normalizedUrl; // alternate
			}
			else
			{
				tryUrl = (attempt == 0) ? primaryUrl : primaryUrl; // keep primary if no fallback
			}

			if (enableDetailedLogs) Debug.Log($"[UpdateNotificationManager] Fetch attempt {attempt + 1} URL: {tryUrl}");

			using (var request = UnityWebRequest.Get(tryUrl))
			{
				request.timeout = Mathf.Max(1, requestTimeoutSeconds);
				yield return request.SendWebRequest();

#if UNITY_2020_2_OR_NEWER
				bool hasNetworkError = request.result != UnityWebRequest.Result.Success;
#else
				bool hasNetworkError = request.isNetworkError || request.isHttpError;
#endif
				string text = request.downloadHandler != null ? request.downloadHandler.text : null;
				bool looksLikeHtml = !string.IsNullOrEmpty(text) && LooksLikeHtml(text);

				if (hasNetworkError || looksLikeHtml)
				{
					lastError = hasNetworkError ? request.error : "Received HTML instead of JSON";
					if (enableDetailedLogs) Debug.LogWarning($"[UpdateNotificationManager] Attempt {attempt + 1} failed: {lastError}");
				}
				else
				{
					try
					{
						remote = JsonUtility.FromJson<RemoteUpdateInfo>(text);
					}
					catch (Exception ex)
					{
						lastError = "JSON parse error: " + ex.Message;
						remote = null;
					}

					if (remote != null && !string.IsNullOrEmpty(remote.updateCode))
					{
						usedUrl = tryUrl;
						break;
					}
					else
					{
						lastError = string.IsNullOrEmpty(lastError) ? "Invalid or missing updateCode" : lastError;
					}
				}
			}

			if (remote == null)
			{
				float delay = Mathf.Pow(2f, attempt) * retryBackoffBaseSeconds;
				if (attempt < Mathf.Max(0, maxRetryCount))
				{
					if (enableDetailedLogs) Debug.Log($"[UpdateNotificationManager] Retrying in {delay:0.00}s...");
					yield return new WaitForSecondsRealtime(delay);
				}
			}
		}

		isRequestInFlight = false;

		if (remote == null)
		{
			Debug.LogWarning($"[UpdateNotificationManager] Failed to fetch/parse update JSON. Last error: {lastError}");
			yield break;
		}

		latestRemote = remote;

		// Dismissed cache check (optional)
		if (rememberDismissedUpdateCode)
		{
			string lastDismissed = PlayerPrefs.GetString(playerPrefsDismissKey, string.Empty);
			if (!string.IsNullOrEmpty(lastDismissed) && string.Equals(lastDismissed, remote.updateCode, StringComparison.Ordinal))
			{
				if (enableDetailedLogs) Debug.Log("[UpdateNotificationManager] Remote update previously dismissed. Skipping popup.");
				yield break;
			}
		}

		bool needsUpdate = ShouldRequireUpdate(remote);
		if (enableDetailedLogs) Debug.Log($"[UpdateNotificationManager] Decision: needsUpdate={needsUpdate} via {decisionMode}. Used URL: {usedUrl}");

		if (needsUpdate)
		{
			ShowUpdatePopup(remote);
		}
		else
		{
			HideUpdatePopup();
		}
	}

	private bool ShouldRequireUpdate(RemoteUpdateInfo remote)
	{
		bool codeMismatch = !string.Equals(remote.updateCode, currentUpdateCode, StringComparison.Ordinal);
		bool semverGreater = false;

		if (decisionMode != UpdateDecisionMode.UpdateCodeMismatch)
		{
			semverGreater = CompareSemVer(remote.latestVersion, localVersion) > 0;
		}

		switch (decisionMode)
		{
			case UpdateDecisionMode.UpdateCodeMismatch: return codeMismatch;
			case UpdateDecisionMode.SemVerGreater: return semverGreater;
			case UpdateDecisionMode.Either: return codeMismatch || semverGreater;
			case UpdateDecisionMode.Both: return codeMismatch && semverGreater;
			default: return codeMismatch;
		}
	}

	private static int CompareSemVer(string a, string b)
	{
		if (string.IsNullOrEmpty(a) && string.IsNullOrEmpty(b)) return 0;
		if (string.IsNullOrEmpty(a)) return -1;
		if (string.IsNullOrEmpty(b)) return 1;
		try
		{
			string[] pa = a.Split('.');
			string[] pb = b.Split('.');
			int len = Mathf.Max(pa.Length, pb.Length);
			for (int i = 0; i < len; i++)
			{
				int ai = i < pa.Length ? ParseIntSafe(pa[i]) : 0;
				int bi = i < pb.Length ? ParseIntSafe(pb[i]) : 0;
				if (ai != bi) return ai.CompareTo(bi);
			}
			return 0;
		}
		catch { return string.Compare(a, b, StringComparison.Ordinal); }
	}

	private static int ParseIntSafe(string s)
	{
		int v; return int.TryParse(s, out v) ? v : 0;
	}

	private void ShowUpdatePopup(RemoteUpdateInfo remote)
	{
		isShowingPopup = true;

		if (pauseTimeOnPopup)
		{
			previousTimeScale = Time.timeScale;
			Time.timeScale = 0f;
		}

		if (updateCanvasRoot != null)
		{
			EnsurePopupCanvasGroup();
			updateCanvasRoot.SetActive(true);
			if (popupFadeRoutine != null) StopCoroutine(popupFadeRoutine);
			if (popupCanvasGroup != null) popupCanvasGroup.alpha = 0f;
			popupFadeRoutine = StartCoroutine(FadeCanvasGroup(popupCanvasGroup, 0f, 1f, popupFadeSeconds));
		}

		if (updateTitleText != null)
		{
			updateTitleText.text = (updateRequirement == UpdateRequirement.Forced) ? forcedUpdateTitle : optionalUpdateTitle;
		}

		if (updateMessageText != null)
		{
			var sb = new StringBuilder();
			string message = !string.IsNullOrEmpty(remote.updateMessage) ? remote.updateMessage : "An update is available.";
			sb.Append(message);
			if (!string.IsNullOrEmpty(remote.latestVersion))
			{
				sb.Append("\n\nLatest version: ").Append(remote.latestVersion);
			}
			updateMessageText.text = sb.ToString();
		}

		WireUpButtons();

		for (int i = 0; i < objectsToDisableOnUpdate.Count; i++)
		{
			var target = objectsToDisableOnUpdate[i];
			if (target != null) target.SetActive(false);
		}
	}

	private void HideUpdatePopup()
	{
		isShowingPopup = false;

		if (updateCanvasRoot == null)
		{
			if (pauseTimeOnPopup)
			{
				Time.timeScale = previousTimeScale;
			}
			return;
		}

		EnsurePopupCanvasGroup();
		if (popupFadeRoutine != null) StopCoroutine(popupFadeRoutine);
		StartCoroutine(HidePopupRoutine());
	}

	private IEnumerator HidePopupRoutine()
	{
		if (popupCanvasGroup != null)
		{
			yield return FadeCanvasGroup(popupCanvasGroup, popupCanvasGroup.alpha, 0f, popupFadeSeconds);
		}
		if (updateCanvasRoot != null) updateCanvasRoot.SetActive(false);

		if (reenableObjectsWhenPopupHidden)
		{
			for (int i = 0; i < objectsToDisableOnUpdate.Count; i++)
			{
				var target = objectsToDisableOnUpdate[i];
				if (target != null) target.SetActive(true);
			}
		}

		if (pauseTimeOnPopup)
		{
			Time.timeScale = previousTimeScale;
		}
	}

	private void WireUpButtons()
	{
		if (updateButton != null)
		{
			updateButton.onClick.RemoveListener(HandleUpdateButtonClicked);
			updateButton.onClick.AddListener(HandleUpdateButtonClicked);
		}
	}

	private void UnwireButtons()
	{
		if (updateButton != null) updateButton.onClick.RemoveListener(HandleUpdateButtonClicked);
	}

	private void HandleUpdateButtonClicked()
	{
		string url = !string.IsNullOrWhiteSpace(updateButtonUrlOverride)
			? updateButtonUrlOverride
			: (latestRemote != null ? latestRemote.updateLink : string.Empty);

		if (string.IsNullOrWhiteSpace(url))
		{
			Debug.LogWarning("[UpdateNotificationManager] No update link configured (override and JSON empty).");
			return;
		}

		Application.OpenURL(url);
	}

	private void EnsurePopupCanvasGroup()
	{
		if (popupCanvasGroup == null && updateCanvasRoot != null)
		{
			popupCanvasGroup = updateCanvasRoot.GetComponent<CanvasGroup>();
			if (popupCanvasGroup == null)
			{
				popupCanvasGroup = updateCanvasRoot.AddComponent<CanvasGroup>();
			}
		}
	}

	private IEnumerator FadeCanvasGroup(CanvasGroup cg, float from, float to, float duration)
	{
		if (cg == null)
		{
			yield break;
		}
		float t = 0f;
		cg.alpha = from;
		if (duration <= 0f)
		{
			cg.alpha = to;
			yield break;
		}
		while (t < duration)
		{
			t += Time.unscaledDeltaTime;
			float p = Mathf.Clamp01(t / duration);
			cg.alpha = Mathf.Lerp(from, to, p);
			yield return null;
		}
		cg.alpha = to;
	}

	private static bool LooksLikeHtml(string text)
	{
		string s = text.TrimStart();
		if (s.StartsWith("<") || s.IndexOf("<!DOCTYPE", StringComparison.OrdinalIgnoreCase) >= 0)
		{
			return true;
		}
		if (s.IndexOf("<html", StringComparison.OrdinalIgnoreCase) >= 0) return true;
		if (s.IndexOf("<head", StringComparison.OrdinalIgnoreCase) >= 0) return true;
		if (s.IndexOf("<body", StringComparison.OrdinalIgnoreCase) >= 0) return true;
		return false;
	}

	public static string NormalizeGitHubRawUrl(string url)
	{
		if (string.IsNullOrEmpty(url)) return url;
		if (!url.Contains("github.com")) return url;
		int blobIndex = url.IndexOf("/blob/", StringComparison.Ordinal);
		if (blobIndex < 0) return url;
		try
		{
			// Example: https://github.com/OWNER/REPO/blob/BRANCH/path/file -> https://raw.githubusercontent.com/OWNER/REPO/BRANCH/path/file
			var prefix = url.Substring(0, blobIndex);
			var suffix = url.Substring(blobIndex + "/blob/".Length);
			var hostStart = prefix.IndexOf("github.com", StringComparison.Ordinal);
			var left = prefix.Substring(0, hostStart);
			var right = prefix.Substring(hostStart + "github.com".Length).TrimEnd('/');
			string normalized = left + "raw.githubusercontent.com" + right + "/" + suffix;
			return normalized;
		}
		catch { return url; }
	}
}