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
	private class SaveData
	{
		public List<ResourceEntry> resources = new List<ResourceEntry>();
		public float totalTimeSeconds;
		public SerializableVector3 playerPosition;
		public bool hasCompletedIntro;
	}

	public static GameDataManager Instance { get; private set; }

	[Header("Save Slot & Flow")]
	[Range(1, 3)]
	public int currentSaveSlot = 1;
	[Tooltip("If true, on play the manager auto-loads the selected slot and enters the correct scene (intro or game).")]
	public bool autoLoadOnStartup = false;

	[Header("Scenes")]
	[Tooltip("Name of the intro/backstory scene.")]
	public string introSceneName = "Intro";
	[Tooltip("Name of the main gameplay scene.")]
	public string gameSceneName = "Game";

	[Header("Player Binding")]
	[Tooltip("Optional direct reference to the player transform. If not set, the manager will try to find a player with PickupInteractor in each scene.")]
	public Transform playerTransform;

	[Header("Resources (Editable in Inspector)")]
	[Tooltip("Add, remove, and reorder resources here. These will be saved & loaded automatically.")]
	public List<ResourceEntry> resources = new List<ResourceEntry>();

	public event Action<string, int> OnResourceChanged;
	public event Action OnDataLoaded;
	public event Action<int> OnPlayTimeSecondTick;

	public float TotalPlayTimeSeconds => _totalPlayTimeSeconds;

	private float _totalPlayTimeSeconds = 0f;
	private bool _hasCompletedIntroInMemory = false;
	private bool _applySavedPlayerPositionWhenAvailable = false;
	private Vector3 _savedPlayerPosition = Vector3.zero;
	private float _playTimeSecondAccumulator = 0f;

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
		}

		// Apply saved position if flagged and player exists
		if (_applySavedPlayerPositionWhenAvailable && playerTransform != null)
		{
			playerTransform.position = _savedPlayerPosition;
			_applySavedPlayerPositionWhenAvailable = false;
		}
	}

	// Public API
	public void SetCurrentSaveSlot(int slot)
	{
		currentSaveSlot = Mathf.Clamp(slot, 1, 3);
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
		if (_hasCompletedIntroInMemory)
		{
			if (!string.IsNullOrEmpty(gameSceneName))
			{
				LoadSceneSafe(gameSceneName);
			}
		}
		else
		{
			if (!string.IsNullOrEmpty(introSceneName))
			{
				LoadSceneSafe(introSceneName);
			}
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
		}
	}

	public void AddResource(string resourceId, int delta)
	{
		if (string.IsNullOrEmpty(resourceId) || delta == 0) return;
		ResourceEntry entry = FindOrCreateResource(resourceId);
		entry.amount += delta;
		OnResourceChanged?.Invoke(resourceId, entry.amount);
	}

	public void SavePlayerPositionFromCurrent()
	{
		if (playerTransform != null)
		{
			_savedPlayerPosition = playerTransform.position;
			_applySavedPlayerPositionWhenAvailable = true; // Ensures next scene load re-applies if needed
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
			data.hasCompletedIntro = _hasCompletedIntroInMemory;

			string json = JsonUtility.ToJson(data, true);
			string fullPath = GetSaveFilePath(currentSaveSlot);
			EnsureSavesDirectoryExists();
			File.WriteAllText(fullPath, json);
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
				fresh.hasCompletedIntro = false;
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
}

