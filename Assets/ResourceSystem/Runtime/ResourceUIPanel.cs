using TMPro;
using UnityEngine;

namespace ResourceSystem
{
    [RequireComponent(typeof(TMP_Text))]
    public class ResourceUIPanel : MonoBehaviour
    {
        [Header("Binding")]
        public string resourceId = "money";
        public string format = "{0}";
        public int decimals = 0;

        private TMP_Text text;

        void Awake()
        {
            text = GetComponent<TMP_Text>();
        }

        void OnEnable()
        {
            if (ResourceManager.Instance != null)
            {
                ResourceManager.Instance.OnResourceChanged += HandleResourceChanged;
            }
            Refresh();
        }

        void OnDisable()
        {
            if (ResourceManager.Instance != null)
            {
                ResourceManager.Instance.OnResourceChanged -= HandleResourceChanged;
            }
        }

        private void HandleResourceChanged(string changedId, double newValue)
        {
            if (!string.Equals(changedId, resourceId, System.StringComparison.OrdinalIgnoreCase)) return;
            UpdateText(newValue);
        }

        public void Refresh()
        {
            if (ResourceManager.Instance == null) return;
            var value = ResourceManager.Instance.GetResourceAmount(resourceId);
            UpdateText(value);
        }

        private void UpdateText(double value)
        {
            if (text == null) return;
            var rounded = System.Math.Round(value, decimals);
            text.text = string.Format(format, rounded);
        }
    }
}

