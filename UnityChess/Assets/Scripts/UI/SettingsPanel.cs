using UnityEngine;
using UnityEngine.UI;

namespace Chess
{
	public class SettingsPanel : MonoBehaviour
	{
		[SerializeField] private GameManager gameManager;
		[SerializeField] private GameObject panel;
		[SerializeField] private Toggle humanWhiteToggle;
		[SerializeField] private Toggle humanBlackToggle;
		[SerializeField] private Slider aiDepthSlider;
		[SerializeField] private Text aiDepthLabel;
		[SerializeField] private Button closeButton;

		private void Start()
		{
			panel.SetActive(false);
			humanWhiteToggle.isOn = true;
			humanBlackToggle.isOn = false;
			aiDepthSlider.minValue = 1;
			aiDepthSlider.maxValue = 6;
			aiDepthSlider.wholeNumbers = true;
			aiDepthSlider.value = 3;
			UpdateDepthLabel();
			aiDepthSlider.onValueChanged.AddListener(_ => OnAiDepthChanged());
			closeButton.onClick.AddListener(() => Hide());
		}

		public void Show()
		{
			panel.SetActive(true);
		}

		public void Hide()
		{
			panel.SetActive(false);
		}

		public void Apply()
		{
			// Apply toggles to game by reassigning who is human
			var gmType = typeof(GameManager);
			var whiteField = gmType.GetField("humanPlaysWhite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
			var blackField = gmType.GetField("humanPlaysBlack", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
			var depthField = gmType.GetField("aiDepth", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
			whiteField.SetValue(gameManager, humanWhiteToggle.isOn);
			blackField.SetValue(gameManager, humanBlackToggle.isOn);
			depthField.SetValue(gameManager, (int)aiDepthSlider.value);
			gameManager.Ai.MaxDepth = (int)aiDepthSlider.value;
		}

		private void OnAiDepthChanged()
		{
			UpdateDepthLabel();
		}

		private void UpdateDepthLabel()
		{
			aiDepthLabel.text = $"AI Depth: {(int)aiDepthSlider.value}";
		}
	}
}