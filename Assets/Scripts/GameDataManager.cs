using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.SceneManagement;

[DefaultExecutionOrder(-1000)]
public class GameDataManager : MonoBehaviour
{
	[Serializable]
	public class ResourceEntry
	{
		public string id;
		public int amount;
	}

	[Serializable]
	public class SaveSlotSummary
	{
		public bool saveExists;
		public int slotIndex;
		public string version;
		public string productName;
		public string companyName;
		public string sceneName;
		public string savedAtIsoUtc;
		public long savedAtUnixSeconds;
		public float totalTimeSeconds;
		public bool hasCompletedIntro;
		public Vector3 playerPosition;
	}

	[Serializable]
	private class SerializableVector3
	{
		public float x;
		public float y;
		public float z;

		public SerializableVector3() { }

		public SerializableVector3(Vector3 v)
		{
			x = v.x;
			y = v.y;
			z = v.z;
		}

		public Vector3 ToVector3()
		{
			return new Vector3(x, y, z);
		}
	}

	[Serializable]
	private class SerializableQuaternion
	{
		public float x;
		public float y;
		public float z;
		public float w;

		public SerializableQuaternion() { }

		public SerializableQuaternion(Quaternion q)
		{
			x = q.x;
			y = q.y;
			z = q.z;
			w = q.w;
		}

		public Quaternion ToQuaternion()
		{
			return new Quaternion(x, y, z, w);
		}
	}

	[Serializable]
	private class SaveData
	{
		public List<ResourceEntry> resources = new List<ResourceEntry>();
		public float totalTimeSeconds;
		public SerializableVector3 playerPosition;
		public SerializableQuaternion playerRotation;
		public bool hasCompletedIntro;
		public string sceneName;
		public string version;
		public string productName;
		public string companyName;
		public string savedAtIsoUtc;
		public long savedAtUnixSeconds;
	}

	public static GameDataManager Instance { get; private set; }

	[Header("Save Slot & Flow")]
	[Range(1, 3)]
	public int currentSaveSlot = 1;
	[Tooltip("If true, on play the manager auto-loads the selected slot and enters the correct scene (intro or game).")]
	public bool autoLoadOnStartup = false;
	[Tooltip("If true, spawn the player at the saved position when a scene loads.")]
	public bool spawnFromSavedPositionOnSceneLoad = true;
	[Tooltip("If true, also apply saved rotation to the player when a scene loads.")]
	public bool applySavedRotationOnSceneLoad = false;

	public enum InitialFlowMode { AutoByIntroFlag, ForceIntro, ForceGame }
	[Tooltip("How to decide which scene to load when entering flow.")]
	public InitialFlowMode initialFlowMode = InitialFlowMode.AutoByIntroFlag;

	[Header("Scenes")]
	[Tooltip("Name of the intro/backstory scene.")]
	public string introSceneName = "Intro";
	[Tooltip("Name of the main gameplay scene.")]
	public string gameSceneName = "Game";

	[Header("Player Binding")]
	[Tooltip("Optional direct reference to the player transform. If not set, the manager will try to find a player with PickupInteractor in each scene.")]
	public Transform playerTransform;
	[Tooltip("If true and no player assigned, try to find by tag 'Player'.")]
	public bool findPlayerByTag = true;

	[Header("Resources (Editable in Inspector)")]
	[Tooltip("Add, remove, and reorder resources here. These will be saved & loaded automatically.")]
	public List<ResourceEntry> resources = new List<ResourceEntry>();
	[Tooltip("If true, autosave will be triggered whenever resources change (subject to autosave throttling).")]
	public bool markDirtyOnResourceChange = true;

	[Header("Autosave")]
	public bool enableAutosave = true;
	[Min(1f)] public float autosaveIntervalSeconds = 30f;
	[Tooltip("If true, saving only occurs when data has changed since last save.")]
	public bool autosaveOnlyWhenDirty = true;
	[Tooltip("If true, also save automatically when the active scene changes.")]
	public bool saveOnSceneChange = true;

	[Header("Serialization Options")]
	public bool prettyJson = true;
	public bool writeBackupFile = true;

	[Header("Debug/Logging")]
	public bool logOnSave = false;
	public bool logOnLoad = false;
	public bool logPaths = false;

	public event Action<string, int> OnResourceChanged;
	public event Action OnDataLoaded;
	public event Action<int> OnPlayTimeSecondTick;
	public event Action<int> OnSlotChanged;
	public event Action<int, string> OnSaved; // slot, path

	public float TotalPlayTimeSeconds => _totalPlayTimeSeconds;

	private float _totalPlayTimeSeconds = 0f;
	private bool _hasCompletedIntroInMemory = false;
	private bool _applySavedPlayerPositionWhenAvailable = false;
	private Vector3 _savedPlayerPosition = Vector3.zero;
	private Quaternion _savedPlayerRotation = Quaternion.identity;
	private float _playTimeSecondAccumulator = 0f;
	private float _autosaveTimer = 0f;
	private bool _isDirty = false;
	private string _lastSavePath = string.Empty;

	private void Awake()
	{
		if (Instance != null && Instance != this)
		{
			Destroy(gameObject);
			return;
		}
		Instance = this;
		DontDestroyOnLoad(gameObject);

		SceneManager.sceneLoaded += OnSceneLoaded;

		if (autoLoadOnStartup)
		{
			SelectSlotAndLoad(currentSaveSlot, true);
		}
	}

	private void OnDestroy()
	{
		if (Instance == this)
		{
			SceneManager.sceneLoaded -= OnSceneLoaded;
		}
	}

	private void Update()
	{
		_totalPlayTimeSeconds += Time.unscaledDeltaTime;
		_playTimeSecondAccumulator += Time.unscaledDeltaTime;
		if (_playTimeSecondAccumulator >= 1f)
		{
			_playTimeSecondAccumulator -= 1f;
			OnPlayTimeSecondTick?.Invoke(Mathf.FloorToInt(_totalPlayTimeSeconds));
		}

		if (enableAutosave)
		{
			_autosaveTimer += Time.unscaledDeltaTime;
			if (_autosaveTimer >= Mathf.Max(1f, autosaveIntervalSeconds))
			{
				_autosaveTimer = 0f;
				if (!autosaveOnlyWhenDirty || _isDirty)
				{
					SaveGame();
				}
			}
		}
	}

	private void OnApplicationPause(bool pause)
	{
		if (pause)
		{
			SaveGame();
		}
	}

	private void OnApplicationQuit()
	{
		SaveGame();
	}

	private void OnSceneLoaded(Scene scene, LoadSceneMode loadSceneMode)
	{
		// Re-bind player transform if needed
		if (playerTransform == null)
		{
			var interactor = FindObjectOfType<PickupInteractor>();
			if (interactor != null)
			{
				playerTransform = interactor.transform;
			}
			else if (findPlayerByTag)
			{
				GameObject tagged = GameObject.FindGameObjectWithTag("Player");
				if (tagged != null)
				{
					playerTransform = tagged.transform;
				}
			}
		}

		// Apply saved position/rotation if flagged and player exists
		if (_applySavedPlayerPositionWhenAvailable && playerTransform != null)
		{
			if (spawnFromSavedPositionOnSceneLoad)
			{
				playerTransform.position = _savedPlayerPosition;
			}
			if (applySavedRotationOnSceneLoad)
			{
				playerTransform.rotation = _savedPlayerRotation;
			}
			_applySavedPlayerPositionWhenAvailable = false;
		}

		if (saveOnSceneChange)
		{
			SaveGame();
		}
	}

	// Public API
	public void SetCurrentSaveSlot(int slot)
	{
		currentSaveSlot = Mathf.Clamp(slot, 1, 3);
		OnSlotChanged?.Invoke(currentSaveSlot);
	}

	public void SelectSlotAndLoad(int slot, bool enterSceneFlow)
	{
		SetCurrentSaveSlot(slot);
		LoadGameOrCreateNew();
		if (enterSceneFlow)
		{
			EnterSceneFlowBasedOnIntro();
		}
	}

	public void EnterSceneFlowBasedOnIntro()
	{
		switch (initialFlowMode)
		{
			case InitialFlowMode.ForceIntro:
				if (!string.IsNullOrEmpty(introSceneName)) LoadSceneSafe(introSceneName);
				break;
			case InitialFlowMode.ForceGame:
				if (!string.IsNullOrEmpty(gameSceneName)) LoadSceneSafe(gameSceneName);
				break;
			default:
				if (_hasCompletedIntroInMemory)
				{
					if (!string.IsNullOrEmpty(gameSceneName)) LoadSceneSafe(gameSceneName);
				}
				else
				{
					if (!string.IsNullOrEmpty(introSceneName)) LoadSceneSafe(introSceneName);
				}
				break;
		}
	}

	public void MarkIntroCompleteAndEnterGame()
	{
		_hasCompletedIntroInMemory = true;
		SaveGame();
		if (!string.IsNullOrEmpty(gameSceneName))
		{
			LoadSceneSafe(gameSceneName);
		}
	}

	public int GetResourceAmount(string resourceId)
	{
		if (string.IsNullOrEmpty(resourceId)) return 0;
		for (int i = 0; i < resources.Count; i++)
		{
			if (string.Equals(resources[i].id, resourceId, StringComparison.Ordinal))
			{
				return resources[i].amount;
			}
		}
		return 0;
	}

	public void SetResourceAmount(string resourceId, int newAmount)
	{
		if (string.IsNullOrEmpty(resourceId)) return;
		ResourceEntry entry = FindOrCreateResource(resourceId);
		if (entry.amount != newAmount)
		{
			entry.amount = newAmount;
			OnResourceChanged?.Invoke(resourceId, entry.amount);
			if (markDirtyOnResourceChange) _isDirty = true;
		}
	}

	public void AddResource(string resourceId, int delta)
	{
		if (string.IsNullOrEmpty(resourceId) || delta == 0) return;
		ResourceEntry entry = FindOrCreateResource(resourceId);
		entry.amount += delta;
		OnResourceChanged?.Invoke(resourceId, entry.amount);
		if (markDirtyOnResourceChange) _isDirty = true;
	}

	public void SavePlayerPositionFromCurrent()
	{
		if (playerTransform != null)
		{
			_savedPlayerPosition = playerTransform.position;
			_savedPlayerRotation = playerTransform.rotation;
			_applySavedPlayerPositionWhenAvailable = true; // Ensures next scene load re-applies if needed
			_isDirty = true;
		}
	}

	// Persistence
	public void SaveGame()
	{
		try
		{
			SaveData data = new SaveData();
			// Deep copy resources so we do not store inspector references
			for (int i = 0; i < resources.Count; i++)
			{
				ResourceEntry src = resources[i];
				if (src == null || string.IsNullOrEmpty(src.id)) continue;
				data.resources.Add(new ResourceEntry { id = src.id, amount = src.amount });
			}
			data.totalTimeSeconds = _totalPlayTimeSeconds;
			Vector3 posToSave = playerTransform != null ? playerTransform.position : _savedPlayerPosition;
			data.playerPosition = new SerializableVector3(posToSave);
			Quaternion rotToSave = playerTransform != null ? playerTransform.rotation : _savedPlayerRotation;
			data.playerRotation = new SerializableQuaternion(rotToSave);
			data.hasCompletedIntro = _hasCompletedIntroInMemory;
			data.sceneName = SceneManager.GetActiveScene().name;
			data.version = Application.version;
			data.productName = Application.productName;
			data.companyName = Application.companyName;
			DateTime now = DateTime.UtcNow;
			data.savedAtIsoUtc = now.ToString("o");
			data.savedAtUnixSeconds = (long)(now - new DateTime(1970,1,1,0,0,0,DateTimeKind.Utc)).TotalSeconds;

			string json = JsonUtility.ToJson(data, prettyJson);
			string fullPath = GetSaveFilePath(currentSaveSlot);
			EnsureSavesDirectoryExists();
			if (writeBackupFile && File.Exists(fullPath))
			{
				string backupPath = fullPath + ".bak";
				File.Copy(fullPath, backupPath, true);
			}
			File.WriteAllText(fullPath, json);
			_lastSavePath = fullPath;
			_isDirty = false;
			OnSaved?.Invoke(currentSaveSlot, fullPath);
			if (logOnSave)
			{
				Debug.Log("Saved slot " + currentSaveSlot + " to: " + fullPath);
			}
		}
		catch (Exception e)
		{
			Debug.LogError("Save failed: " + e);
		}
	}

	public void LoadGameOrCreateNew()
	{
		try
		{
			string fullPath = GetSaveFilePath(currentSaveSlot);
			EnsureSavesDirectoryExists();
			if (File.Exists(fullPath))
			{
				string json = File.ReadAllText(fullPath);
				SaveData loaded = JsonUtility.FromJson<SaveData>(json);
				ApplyLoadedData(loaded);
				if (logOnLoad)
				{
					Debug.Log("Loaded slot " + currentSaveSlot + " from: " + fullPath);
				}
			}
			else
			{
				// Create new data using inspector defaults
				SaveData fresh = new SaveData();
				for (int i = 0; i < resources.Count; i++)
				{
					ResourceEntry src = resources[i];
					if (src == null || string.IsNullOrEmpty(src.id)) continue;
					fresh.resources.Add(new ResourceEntry { id = src.id, amount = src.amount });
				}
				fresh.totalTimeSeconds = 0f;
				fresh.playerPosition = new SerializableVector3(_savedPlayerPosition);
				fresh.playerRotation = new SerializableQuaternion(_savedPlayerRotation);
				fresh.hasCompletedIntro = false;
				fresh.sceneName = SceneManager.GetActiveScene().name;
				fresh.version = Application.version;
				fresh.productName = Application.productName;
				fresh.companyName = Application.companyName;
				DateTime now = DateTime.UtcNow;
				fresh.savedAtIsoUtc = now.ToString("o");
				fresh.savedAtUnixSeconds = (long)(now - new DateTime(1970,1,1,0,0,0,DateTimeKind.Utc)).TotalSeconds;
				ApplyLoadedData(fresh);
				SaveGame();
			}
			OnDataLoaded?.Invoke();
		}
		catch (Exception e)
		{
			Debug.LogError("Load failed: " + e);
		}
	}

	private void ApplyLoadedData(SaveData loaded)
	{
		// Merge resources: if present in save, apply; if new in inspector, keep inspector amount
		Dictionary<string, int> savedMap = new Dictionary<string, int>(StringComparer.Ordinal);
		if (loaded.resources != null)
		{
			for (int i = 0; i < loaded.resources.Count; i++)
			{
				ResourceEntry r = loaded.resources[i];
				if (r != null && !string.IsNullOrEmpty(r.id))
				{
					savedMap[r.id] = r.amount;
				}
			}
		}

		// Apply to inspector list first
		for (int i = 0; i < resources.Count; i++)
		{
			ResourceEntry entry = resources[i];
			if (entry == null || string.IsNullOrEmpty(entry.id)) continue;
			if (savedMap.TryGetValue(entry.id, out int amount))
			{
				entry.amount = amount;
			}
		}

		// Add any saved resources that are not present in inspector list
		foreach (KeyValuePair<string, int> kvp in savedMap)
		{
			bool exists = false;
			for (int i = 0; i < resources.Count; i++)
			{
				if (string.Equals(resources[i].id, kvp.Key, StringComparison.Ordinal))
				{
					exists = true;
					break;
				}
			}
			if (!exists)
			{
				resources.Add(new ResourceEntry { id = kvp.Key, amount = kvp.Value });
			}
		}

		_totalPlayTimeSeconds = Mathf.Max(0f, loaded.totalTimeSeconds);
		_hasCompletedIntroInMemory = loaded.hasCompletedIntro;
		_savedPlayerPosition = loaded.playerPosition != null ? loaded.playerPosition.ToVector3() : Vector3.zero;
		_savedPlayerRotation = loaded.playerRotation != null ? loaded.playerRotation.ToQuaternion() : Quaternion.identity;
		_applySavedPlayerPositionWhenAvailable = true;

		// Notify resource listeners
		for (int i = 0; i < resources.Count; i++)
		{
			ResourceEntry entry = resources[i];
			if (entry != null && !string.IsNullOrEmpty(entry.id))
			{
				OnResourceChanged?.Invoke(entry.id, entry.amount);
			}
		}
		_isDirty = false;
	}

	private ResourceEntry FindOrCreateResource(string resourceId)
	{
		for (int i = 0; i < resources.Count; i++)
		{
			if (string.Equals(resources[i].id, resourceId, StringComparison.Ordinal))
			{
				return resources[i];
			}
		}
		ResourceEntry created = new ResourceEntry { id = resourceId, amount = 0 };
		resources.Add(created);
		return created;
	}

	private static string GetSavesDirectory()
	{
		return Path.Combine(Application.persistentDataPath, "Saves");
	}

	private static string GetSaveFilePath(int slot)
	{
		string dir = GetSavesDirectory();
		string fileName = "saveslot" + Mathf.Clamp(slot, 1, 3) + ".json";
		return Path.Combine(dir, fileName);
	}

	private static void EnsureSavesDirectoryExists()
	{
		string dir = GetSavesDirectory();
		if (!Directory.Exists(dir))
		{
			Directory.CreateDirectory(dir);
		}
	}

	private void LoadSceneSafe(string sceneName)
	{
		if (string.IsNullOrEmpty(sceneName)) return;
		if (SceneManager.GetActiveScene().name == sceneName) return;
		try
		{
			SceneManager.LoadScene(sceneName);
		}
		catch (Exception e)
		{
			Debug.LogError("Failed to load scene '" + sceneName + "': " + e);
		}
	}

	// Public helpers and management
	public string GetSavesDirectoryPath() { return GetSavesDirectory(); }
	public string GetCurrentSaveFilePath() { return GetSaveFilePath(currentSaveSlot); }
	public string GetSaveFilePathForSlot(int slot) { return GetSaveFilePath(slot); }

	public SaveSlotSummary GetSlotSummary(int slot)
	{
		SaveSlotSummary summary = new SaveSlotSummary();
		summary.slotIndex = Mathf.Clamp(slot, 1, 3);
		string path = GetSaveFilePath(summary.slotIndex);
		summary.saveExists = File.Exists(path);
		if (summary.saveExists)
		{
			try
			{
				string json = File.ReadAllText(path);
				SaveData d = JsonUtility.FromJson<SaveData>(json);
				summary.version = d.version;
				summary.productName = d.productName;
				summary.companyName = d.companyName;
				summary.sceneName = d.sceneName;
				summary.savedAtIsoUtc = d.savedAtIsoUtc;
				summary.savedAtUnixSeconds = d.savedAtUnixSeconds;
				summary.totalTimeSeconds = d.totalTimeSeconds;
				summary.hasCompletedIntro = d.hasCompletedIntro;
				summary.playerPosition = d.playerPosition != null ? d.playerPosition.ToVector3() : Vector3.zero;
			}
			catch (Exception e)
			{
				Debug.LogWarning("Failed to read summary for slot " + slot + ": " + e);
			}
		}
		else
		{
			summary.version = Application.version;
			summary.productName = Application.productName;
			summary.companyName = Application.companyName;
			summary.sceneName = string.Empty;
			summary.savedAtIsoUtc = string.Empty;
			summary.savedAtUnixSeconds = 0;
			summary.totalTimeSeconds = 0f;
			summary.hasCompletedIntro = false;
			summary.playerPosition = Vector3.zero;
		}
		return summary;
	}

	public void ResetResourcesToDefault()
	{
		for (int i = 0; i < resources.Count; i++)
		{
			ResourceEntry r = resources[i];
			if (r != null) r.amount = 0;
		}
		_isDirty = true;
	}

	public void ClearSlotFile(int slot)
	{
		int clamped = Mathf.Clamp(slot, 1, 3);
		string path = GetSaveFilePath(clamped);
		try
		{
			if (File.Exists(path)) File.Delete(path);
		}
		catch (Exception e)
		{
			Debug.LogError("Failed to delete slot " + clamped + ": " + e);
		}
	}

	public void StartNewGameOnCurrentSlot()
	{
		_hasCompletedIntroInMemory = false;
		_totalPlayTimeSeconds = 0f;
		_savedPlayerPosition = Vector3.zero;
		_savedPlayerRotation = Quaternion.identity;
		// Keep resource definitions, set amounts to zero
		for (int i = 0; i < resources.Count; i++)
		{
			ResourceEntry r = resources[i];
			if (r != null) r.amount = 0;
		}
		_isDirty = true;
		SaveGame();
	}
}

