using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using UnityEngine.Video;
using TMPro;

[DefaultExecutionOrder(-1000)]
[DisallowMultipleComponent]
[AddComponentMenu("Update System/Update Notification Manager")]
public class UpdateNotificationManager : MonoBehaviour
{
	public static UpdateNotificationManager Instance { get; private set; }

	[Header("Singleton & Lifecycle")]
	[SerializeField] private bool enforceSingleton = true;
	[SerializeField] private bool persistAcrossScenes = true;
	[SerializeField] private bool persistPopupCanvas = true;

	[Header("Remote Config")]
	[Tooltip("Full URL to update.json (e.g., https://raw.githubusercontent.com/<user>/<repo>/<branch>/update.json)")]
	[SerializeField] private string updateJsonUrl = "";
	[Tooltip("Local version/update code stored in the game. If remote updateCode differs, popup will show.")]
	[SerializeField] private string currentUpdateCode = "0";
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

	[Header("Popup UI")]
	[Tooltip("Root object of the Update popup canvas (will be SetActive when update required).")]
	[SerializeField] private GameObject updateCanvasRoot;
	[Tooltip("TextMeshProUGUI field to display the remote updateMessage.")]
	[SerializeField] private TextMeshProUGUI updateMessageText;
	[Tooltip("Button that will open the updateLink when clicked.")]
	[SerializeField] private Button updateButton;
	[Tooltip("Optional: override the link from JSON with this URL.")]
	[SerializeField] private string updateButtonUrlOverride = "";

	[Header("Gameplay Blocking")]
	[Tooltip("Objects to disable while the update popup is visible (add via plus in inspector).")]
	[SerializeField] private List<GameObject> objectsToDisableOnUpdate = new List<GameObject>();
	[Tooltip("Re-enable the disabled objects when the popup is hidden (for optional/dismissable popups).")]
	[SerializeField] private bool reenableObjectsWhenPopupHidden = false;

	[Header("Optional Background (Video/Animation)")]
	[SerializeField] private GameObject backgroundRoot;
	[SerializeField] private VideoPlayer backgroundVideoPlayer;
	[SerializeField] private Animator backgroundAnimator;
	[Tooltip("Animator trigger name used to show the background.")]
	[SerializeField] private string backgroundShowTrigger = "Show";
	[Tooltip("Animator trigger name used to hide the background.")]
	[SerializeField] private string backgroundHideTrigger = "Hide";

	[Header("Toast (Fetch Status)")]
	[Tooltip("CanvasGroup that will be faded in/out for short status messages (e.g., fetch failed).")]
	[SerializeField] private CanvasGroup toastCanvasGroup;
	[SerializeField] private TextMeshProUGUI toastText;
	[SerializeField] private float toastDurationSeconds = 1.0f;
	[SerializeField] private float toastFadeSeconds = 0.25f;

	[Header("Events")]
	public UnityEvent OnUpdateRequired;
	public UnityEvent OnNoUpdate;
	public UnityEvent OnFetchFailed;

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
	private bool isShowingPopup;

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
		}

		ConfigureButton();

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

		if (updateButton != null)
		{
			updateButton.onClick.RemoveListener(HandleUpdateButtonClicked);
		}
	}

	[ContextMenu("Force Check Now")]
	public void ForceCheckNow()
	{
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
		if (string.IsNullOrWhiteSpace(updateJsonUrl))
		{
			Debug.LogWarning("[UpdateNotificationManager] updateJsonUrl is empty; set it in the inspector.");
			yield break;
		}

		using (var request = UnityWebRequest.Get(updateJsonUrl))
		{
			request.timeout = Mathf.Max(1, requestTimeoutSeconds);
			yield return request.SendWebRequest();

#if UNITY_2020_2_OR_NEWER
			bool hasNetworkError = request.result != UnityWebRequest.Result.Success;
#else
			bool hasNetworkError = request.isNetworkError || request.isHttpError;
#endif
			if (hasNetworkError)
			{
				Debug.LogWarning($"[UpdateNotificationManager] Failed to fetch update JSON: {request.error}");
				ShowToast("Couldn't fetch update");
				OnFetchFailed?.Invoke();
				yield break;
			}

			string json = request.downloadHandler.text;
			RemoteUpdateInfo remote = null;
			try
			{
				remote = JsonUtility.FromJson<RemoteUpdateInfo>(json);
			}
			catch (Exception ex)
			{
				Debug.LogWarning($"[UpdateNotificationManager] JSON parse error: {ex.Message}");
				ShowToast("Couldn't fetch update");
				OnFetchFailed?.Invoke();
				yield break;
			}

			latestRemote = remote;

			if (remote == null || string.IsNullOrEmpty(remote.updateCode))
			{
				Debug.LogWarning("[UpdateNotificationManager] JSON missing updateCode.");
				ShowToast("Couldn't fetch update");
				OnFetchFailed?.Invoke();
				yield break;
			}

			bool needsUpdate = !string.Equals(remote.updateCode, currentUpdateCode, StringComparison.Ordinal);

			if (needsUpdate)
			{
				ShowUpdatePopup(remote);
				OnUpdateRequired?.Invoke();
			}
			else
			{
				HideUpdatePopup();
				OnNoUpdate?.Invoke();
			}
		}
	}

	private void ShowUpdatePopup(RemoteUpdateInfo remote)
	{
		isShowingPopup = true;

		if (updateCanvasRoot != null)
		{
			updateCanvasRoot.SetActive(true);
		}

		if (updateMessageText != null)
		{
			string message = !string.IsNullOrEmpty(remote.updateMessage) ? remote.updateMessage : "An update is available.";
			if (!string.IsNullOrEmpty(remote.latestVersion))
			{
				message = message + "\n\nLatest version: " + remote.latestVersion;
			}
			updateMessageText.text = message;
		}

		ConfigureButton();

		for (int i = 0; i < objectsToDisableOnUpdate.Count; i++)
		{
			var target = objectsToDisableOnUpdate[i];
			if (target != null)
			{
				target.SetActive(false);
			}
		}

		if (backgroundRoot != null)
		{
			backgroundRoot.SetActive(true);
		}

		if (backgroundVideoPlayer != null)
		{
			try { backgroundVideoPlayer.Play(); } catch { }
		}

		if (backgroundAnimator != null && !string.IsNullOrEmpty(backgroundShowTrigger))
		{
			backgroundAnimator.ResetTrigger(backgroundHideTrigger);
			backgroundAnimator.SetTrigger(backgroundShowTrigger);
		}
	}

	private void HideUpdatePopup()
	{
		isShowingPopup = false;

		if (updateCanvasRoot != null)
		{
			updateCanvasRoot.SetActive(false);
		}

		if (reenableObjectsWhenPopupHidden)
		{
			for (int i = 0; i < objectsToDisableOnUpdate.Count; i++)
			{
				var target = objectsToDisableOnUpdate[i];
				if (target != null)
				{
					target.SetActive(true);
				}
			}
		}

		if (backgroundAnimator != null && !string.IsNullOrEmpty(backgroundHideTrigger))
		{
			backgroundAnimator.ResetTrigger(backgroundShowTrigger);
			backgroundAnimator.SetTrigger(backgroundHideTrigger);
		}

		if (backgroundVideoPlayer != null)
		{
			try { backgroundVideoPlayer.Stop(); } catch { }
		}

		if (backgroundRoot != null)
		{
			backgroundRoot.SetActive(false);
		}
	}

	private void ConfigureButton()
	{
		if (updateButton == null)
		{
			return;
		}

		updateButton.onClick.RemoveListener(HandleUpdateButtonClicked);
		updateButton.onClick.AddListener(HandleUpdateButtonClicked);
	}

	private void HandleUpdateButtonClicked()
	{
		string url = !string.IsNullOrWhiteSpace(updateButtonUrlOverride)
			? updateButtonUrlOverride
			: (latestRemote != null ? latestRemote.updateLink : string.Empty);

		if (string.IsNullOrWhiteSpace(url))
		{
			Debug.LogWarning("[UpdateNotificationManager] No update link configured (override and JSON empty).");
			ShowToast("No update link set");
			return;
		}

		Application.OpenURL(url);
	}

	private void ShowToast(string message)
	{
		if (toastText == null || toastCanvasGroup == null)
		{
			Debug.Log(message);
			return;
		}

		toastText.text = message;
		StartCoroutine(ToastRoutine());
	}

	private IEnumerator ToastRoutine()
	{
		toastCanvasGroup.gameObject.SetActive(true);
		yield return FadeCanvasGroup(toastCanvasGroup, 0f, 1f, toastFadeSeconds);
		yield return new WaitForSecondsRealtime(Mathf.Max(0f, toastDurationSeconds));
		yield return FadeCanvasGroup(toastCanvasGroup, 1f, 0f, toastFadeSeconds);
		toastCanvasGroup.gameObject.SetActive(false);
	}

	private IEnumerator FadeCanvasGroup(CanvasGroup cg, float from, float to, float duration)
	{
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
}