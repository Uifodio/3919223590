using System;
using UnityEngine;
using TMPro;

[RequireComponent(typeof(TMP_Text))]
public class UIDataBridge : MonoBehaviour
{
	public enum DisplayMode
	{
		Resource,
		TotalPlayTime
	}

	[Header("Mode")]
	public DisplayMode mode = DisplayMode.Resource;

	[Header("Resource")]
	public string resourceId = "Wood";
	public string resourceFormat = "{0}: {1}"; // name, amount

	[Header("Time")]
	public string timePrefix = "Time: ";

	private TMP_Text _text;

	private void Awake()
	{
		_text = GetComponent<TMP_Text>();
	}

	private void OnEnable()
	{
		if (GameDataManager.Instance != null)
		{
			GameDataManager.Instance.OnResourceChanged += HandleResourceChanged;
			GameDataManager.Instance.OnPlayTimeSecondTick += HandleTimeTick;
			GameDataManager.Instance.OnDataLoaded += HandleDataLoaded;
		}
		RefreshNow();
	}

	private void OnDisable()
	{
		if (GameDataManager.Instance != null)
		{
			GameDataManager.Instance.OnResourceChanged -= HandleResourceChanged;
			GameDataManager.Instance.OnPlayTimeSecondTick -= HandleTimeTick;
			GameDataManager.Instance.OnDataLoaded -= HandleDataLoaded;
		}
	}

	private void HandleDataLoaded()
	{
		RefreshNow();
	}

	private void HandleTimeTick(int seconds)
	{
		if (mode == DisplayMode.TotalPlayTime)
		{
			_text.text = timePrefix + FormatSeconds(seconds);
		}
	}

	private void HandleResourceChanged(string changedId, int amount)
	{
		if (mode == DisplayMode.Resource)
		{
			if (string.Equals(resourceId, changedId, StringComparison.Ordinal))
			{
				_text.text = string.Format(resourceFormat, resourceId, amount);
			}
		}
	}

	private void RefreshNow()
	{
		if (_text == null) return;
		if (GameDataManager.Instance == null) return;
		switch (mode)
		{
			case DisplayMode.Resource:
				{
					int amount = GameDataManager.Instance.GetResourceAmount(resourceId);
					_text.text = string.Format(resourceFormat, resourceId, amount);
					break;
				}
			case DisplayMode.TotalPlayTime:
				{
					int seconds = Mathf.FloorToInt(GameDataManager.Instance.TotalPlayTimeSeconds);
					_text.text = timePrefix + FormatSeconds(seconds);
					break;
				}
		}
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

