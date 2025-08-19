using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Button))]
public class SaveSlotButton : MonoBehaviour
{
	[Range(1,3)]
	public int slotIndex = 1;
	[Tooltip("If true, clicking will immediately enter intro/game scene flow. If false, it only sets slot and loads data.")]
	public bool enterSceneFlowOnClick = true;
	[Tooltip("If true and a save exists, the button will load it; if false and a save exists, will optionally prompt to overwrite (see confirmOverwrite).")]
	public bool continueIfExists = true;
	[Tooltip("If true and continueIfExists is false, clicking will clear the slot first, then start fresh.")]
	public bool confirmOverwrite = false;
	[Tooltip("Optional TMP_Text to show a summary string for the slot.")]
	public TMPro.TMP_Text summaryText;
	[Tooltip("Summary format when a save exists. Placeholders: {0}=time, {1}=scene, {2}=date.")]
	public string summaryFormatExisting = "Time {0} • {1} • {2}";
	[Tooltip("Summary text when the slot is empty.")]
	public string summaryFormatEmpty = "Empty";

	private Button _button;

	private void Awake()
	{
		_button = GetComponent<Button>();
		_button.onClick.AddListener(HandleClick);
		RefreshSummary();
	}

	private void OnDestroy()
	{
		if (_button != null)
		{
			_button.onClick.RemoveListener(HandleClick);
		}
	}

	private void HandleClick()
	{
		if (GameDataManager.Instance == null)
		{
			Debug.LogError("GameDataManager not present in scene. Please add it to a bootstrap scene and mark as Don't Destroy On Load.");
			return;
		}

		var summary = GameDataManager.Instance.GetSlotSummary(slotIndex);
		if (summary.saveExists)
		{
			if (continueIfExists)
			{
				GameDataManager.Instance.SelectSlotAndLoad(slotIndex, enterSceneFlowOnClick);
			}
			else
			{
				bool proceed = true;
				if (confirmOverwrite)
				{
					// Unity runtime has no native confirm dialog in builds; rely on logs/UI. Proceed by default.
					Debug.LogWarning("Overwriting existing save on slot " + slotIndex + ". Implement UI confirm if needed.");
				}
				if (proceed)
				{
					GameDataManager.Instance.SetCurrentSaveSlot(slotIndex);
					GameDataManager.Instance.ClearSlotFile(slotIndex);
					GameDataManager.Instance.StartNewGameOnCurrentSlot();
					if (enterSceneFlowOnClick)
					{
						GameDataManager.Instance.EnterSceneFlowBasedOnIntro();
					}
				}
			}
		}
		else
		{
			GameDataManager.Instance.SelectSlotAndLoad(slotIndex, enterSceneFlowOnClick);
		}
	}

	public void RefreshSummary()
	{
		if (summaryText == null || GameDataManager.Instance == null) return;
		var sum = GameDataManager.Instance.GetSlotSummary(slotIndex);
		if (!sum.saveExists)
		{
			summaryText.text = summaryFormatEmpty;
			return;
		}
		string timeStr = FormatSeconds((int)sum.totalTimeSeconds);
		string dateStr = string.IsNullOrEmpty(sum.savedAtIsoUtc) ? "" : sum.savedAtIsoUtc;
		summaryText.text = string.Format(summaryFormatExisting, timeStr, sum.sceneName, dateStr);
	}

	private static string FormatSeconds(int totalSeconds)
	{
		int hours = totalSeconds / 3600;
		int minutes = (totalSeconds % 3600) / 60;
		int seconds = totalSeconds % 60;
		if (hours > 0)
		{
			return string.Format("{0:D2}:{1:D2}:{2:D2}", hours, minutes, seconds);
		}
		return string.Format("{0:D2}:{1:D2}", minutes, seconds);
	}
}

