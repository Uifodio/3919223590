using UnityEditor;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace UltimateFloatingJoystick.Editor
{
    public static class FloatingJoystickMenu
    {
        [MenuItem("GameObject/UI/Ultimate Floating Joystick", false, 2000)]
        public static void CreateFloatingJoystick()
        {
            Canvas canvas = Object.FindObjectOfType<Canvas>();
            if (canvas == null)
            {
                GameObject canvasGo = new GameObject("Canvas", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
                canvas = canvasGo.GetComponent<Canvas>();
                canvas.renderMode = RenderMode.ScreenSpaceOverlay;
                CanvasScaler scaler = canvasGo.GetComponent<CanvasScaler>();
                scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
                scaler.referenceResolution = new Vector2(1920, 1080);
                scaler.matchWidthOrHeight = 0.5f;
                Undo.RegisterCreatedObjectUndo(canvasGo, "Create Canvas");
            }

            EventSystem es = Object.FindObjectOfType<EventSystem>();
            if (es == null)
            {
                GameObject esGo = new GameObject("EventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
                Undo.RegisterCreatedObjectUndo(esGo, "Create EventSystem");
            }

            GameObject root = new GameObject("FloatingJoystick", typeof(RectTransform), typeof(Image), typeof(UltimateFloatingJoystick.FloatingJoystick));
            Undo.RegisterCreatedObjectUndo(root, "Create FloatingJoystick");
            GameObjectUtility.SetParentAndAlign(root, canvas.gameObject);

            RectTransform rootRect = root.GetComponent<RectTransform>();
            rootRect.anchorMin = Vector2.zero;
            rootRect.anchorMax = Vector2.one;
            rootRect.sizeDelta = Vector2.zero;
            rootRect.anchoredPosition = Vector2.zero;

            Image areaImage = root.GetComponent<Image>();
            areaImage.color = new Color(0f, 0f, 0f, 0f); // Invisible but raycast target by default
            areaImage.raycastTarget = true;

            // Joystick container
            GameObject container = new GameObject("JoystickContainer", typeof(RectTransform), typeof(CanvasGroup));
            Undo.RegisterCreatedObjectUndo(container, "Create JoystickContainer");
            GameObjectUtility.SetParentAndAlign(container, root);
            RectTransform containerRect = container.GetComponent<RectTransform>();
            containerRect.anchorMin = new Vector2(0.5f, 0.5f);
            containerRect.anchorMax = new Vector2(0.5f, 0.5f);
            containerRect.sizeDelta = new Vector2(160, 160);
            containerRect.anchoredPosition = new Vector2(220, 220);
            CanvasGroup containerCg = container.GetComponent<CanvasGroup>();
            containerCg.alpha = 0f; // Respect default runtime behavior

            // Background
            GameObject bg = new GameObject("Background", typeof(RectTransform), typeof(Image));
            Undo.RegisterCreatedObjectUndo(bg, "Create Background");
            GameObjectUtility.SetParentAndAlign(bg, container);
            RectTransform bgRect = bg.GetComponent<RectTransform>();
            bgRect.anchorMin = new Vector2(0.5f, 0.5f);
            bgRect.anchorMax = new Vector2(0.5f, 0.5f);
            bgRect.sizeDelta = new Vector2(160, 160);
            bgRect.anchoredPosition = Vector2.zero;
            Image bgImage = bg.GetComponent<Image>();
            var uiSprite = AssetDatabase.GetBuiltinExtraResource<Sprite>("UI/Skin/UISprite.psd");
            bgImage.sprite = uiSprite;
            bgImage.type = Image.Type.Sliced;
            bgImage.color = new Color(1f, 1f, 1f, 0.45f);
            bgImage.raycastTarget = false;

            // Handle
            GameObject handle = new GameObject("Handle", typeof(RectTransform), typeof(Image));
            Undo.RegisterCreatedObjectUndo(handle, "Create Handle");
            GameObjectUtility.SetParentAndAlign(handle, container);
            RectTransform handleRect = handle.GetComponent<RectTransform>();
            handleRect.anchorMin = new Vector2(0.5f, 0.5f);
            handleRect.anchorMax = new Vector2(0.5f, 0.5f);
            handleRect.sizeDelta = new Vector2(72, 72);
            handleRect.anchoredPosition = Vector2.zero;
            Image handleImage = handle.GetComponent<Image>();
            var knob = AssetDatabase.GetBuiltinExtraResource<Sprite>("UI/Skin/Knob.psd");
            handleImage.sprite = knob;
            handleImage.type = Image.Type.Simple;
            handleImage.color = Color.white;
            handleImage.raycastTarget = false;

            // Placeholder
            GameObject placeholder = new GameObject("Placeholder", typeof(RectTransform), typeof(CanvasGroup));
            Undo.RegisterCreatedObjectUndo(placeholder, "Create Placeholder");
            GameObjectUtility.SetParentAndAlign(placeholder, root);
            RectTransform phRect = placeholder.GetComponent<RectTransform>();
            phRect.anchorMin = new Vector2(0.5f, 0.5f);
            phRect.anchorMax = new Vector2(0.5f, 0.5f);
            phRect.sizeDelta = new Vector2(200, 60);
            phRect.anchoredPosition = containerRect.anchoredPosition;
            CanvasGroup phCg = placeholder.GetComponent<CanvasGroup>();
            phCg.alpha = 1f; // Default placeholder visible when joystick hidden

            // Placeholder background (subtle circle)
            GameObject phBg = new GameObject("Circle", typeof(RectTransform), typeof(Image));
            GameObjectUtility.SetParentAndAlign(phBg, placeholder);
            RectTransform phBgRect = phBg.GetComponent<RectTransform>();
            phBgRect.anchorMin = new Vector2(0.5f, 0.5f);
            phBgRect.anchorMax = new Vector2(0.5f, 0.5f);
            phBgRect.sizeDelta = new Vector2(140, 140);
            phBgRect.anchoredPosition = Vector2.zero;
            Image phBgImage = phBg.GetComponent<Image>();
            phBgImage.color = new Color(1f, 1f, 1f, 0.08f);

            // Placeholder text (prefers TMP if available)
            GameObject phTextGo = new GameObject("Text", typeof(RectTransform));
            GameObjectUtility.SetParentAndAlign(phTextGo, placeholder);
            RectTransform phTextRect = phTextGo.GetComponent<RectTransform>();
            phTextRect.anchorMin = new Vector2(0.5f, 0.5f);
            phTextRect.anchorMax = new Vector2(0.5f, 0.5f);
            phTextRect.sizeDelta = new Vector2(200, 60);
            phTextRect.anchoredPosition = Vector2.zero;

            System.Type tmpType = null;
            foreach (var asm in System.AppDomain.CurrentDomain.GetAssemblies())
            {
                tmpType = asm.GetType("TMPro.TextMeshProUGUI");
                if (tmpType != null) break;
            }
            if (tmpType != null)
            {
                var tmp = phTextGo.AddComponent(tmpType);
                // tmp.text = "Touch to Move";
                tmpType.GetProperty("text")?.SetValue(tmp, "Touch to Move");
                // tmp.alignment = TextAlignmentOptions.Center;
                var alignProp = tmpType.GetProperty("alignment");
                var alignEnum = alignProp?.PropertyType;
                if (alignProp != null && alignEnum != null)
                {
                    var centerValue = System.Enum.Parse(alignEnum, "Center");
                    alignProp.SetValue(tmp, centerValue);
                }
                // tmp.color
                var colorProp = tmpType.GetProperty("color");
                if (colorProp != null)
                {
                    colorProp.SetValue(tmp, new Color(1f, 1f, 1f, 0.8f));
                }
                // tmp.raycastTarget = false
                var rgProp = tmpType.BaseType?.BaseType?.GetProperty("raycastTarget");
                rgProp?.SetValue(tmp, false);
            }
            else
            {
                var phText = phTextGo.AddComponent<Text>();
                phText.text = "Touch to Move";
                phText.alignment = TextAnchor.MiddleCenter;
                phText.color = new Color(1f, 1f, 1f, 0.6f);
                // Fix for Unity 6: Arial.ttf is deprecated. Use LegacyRuntime.ttf if available.
                Font fallbackFont = null;
                try
                {
                    fallbackFont = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
                }
                catch {}
                if (fallbackFont == null)
                {
                    // Last resort: default to system font via new Font("Arial") which Unity resolves if present
                    fallbackFont = new Font("Arial");
                }
                phText.font = fallbackFont;
                phText.raycastTarget = false;
            }

            // Wire up component
            var joystick = root.GetComponent<UltimateFloatingJoystick.FloatingJoystick>();
            joystick.GetType().GetField("activationArea", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(joystick, root.GetComponent<RectTransform>());
            joystick.GetType().GetField("joystickContainer", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(joystick, containerRect);
            joystick.GetType().GetField("joystickCanvasGroup", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(joystick, container.GetComponent<CanvasGroup>());
            joystick.GetType().GetField("backgroundImage", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(joystick, bgImage);
            joystick.GetType().GetField("handleImage", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(joystick, handleImage);
            joystick.GetType().GetField("placeholder", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(joystick, phRect);
            joystick.GetType().GetField("placeholderCanvasGroup", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(joystick, phCg);

            // Respect inspector preview; do not force preview on creation

            // Try to add compatibility Joystick component if available and not already present
            System.Type compatJoystickType = null;
            foreach (var asm in System.AppDomain.CurrentDomain.GetAssemblies())
            {
                var t = asm.GetType("Joystick");
                if (t != null && t != typeof(UltimateFloatingJoystick.FloatingJoystick))
                {
                    compatJoystickType = t;
                    break;
                }
            }
            if (compatJoystickType != null && root.GetComponent(compatJoystickType) == null)
            {
                root.AddComponent(compatJoystickType);
            }

            Selection.activeGameObject = root;
        }
    }
}

