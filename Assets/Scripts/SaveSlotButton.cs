using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Button))]
public class SaveSlotButton : MonoBehaviour
{
	[Range(1,3)]
	public int slotIndex = 1;
	[Tooltip("If true, clicking will immediately enter intro/game scene flow. If false, it only sets slot and loads data.")]
	public bool enterSceneFlowOnClick = true;

	private Button _button;

	private void Awake()
	{
		_button = GetComponent<Button>();
		_button.onClick.AddListener(HandleClick);
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
		GameDataManager.Instance.SelectSlotAndLoad(slotIndex, enterSceneFlowOnClick);
	}
}

