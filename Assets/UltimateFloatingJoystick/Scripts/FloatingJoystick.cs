using System.Collections;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace UltimateFloatingJoystick
{
    /// <summary>
    /// Professional floating joystick that appears where the user first touches,
    /// supports half/full-screen activation, dead zone, smooth handle motion,
    /// glow/fade visuals, and an instructional placeholder.
    /// </summary>
    [DisallowMultipleComponent]
    public class FloatingJoystick : MonoBehaviour, IPointerDownHandler, IPointerUpHandler, IDragHandler
    {
        public enum ActivationRestriction
        {
            FullScreen = 0,
            LeftHalf = 1,
            RightHalf = 2
        }

        [Header("Hierarchy References")]
        [Tooltip("The RectTransform that receives pointer events. Typically this is a full-screen transparent Image.")]
        [SerializeField] private RectTransform activationArea;
        [Tooltip("Container for joystick visuals (background + handle). This group fades in/out.")]
        [SerializeField] private RectTransform joystickContainer;
        [SerializeField] private CanvasGroup joystickCanvasGroup;
        [Tooltip("Joystick background Image.")]
        [SerializeField] private Image backgroundImage;
        [Tooltip("Joystick handle Image.")]
        [SerializeField] private Image handleImage;

        [Header("Input & Motion")]
        [Tooltip("Maximum distance in pixels the handle can move from the center.")]
        [Min(1f)]
        [SerializeField] private float handleRange = 120f;
        [Tooltip("Radius in pixels where small touches are ignored.")]
        [Min(0f)]
        [SerializeField] private float deadZoneRadius = 12f;
        [Tooltip("If true, values beyond the dead zone are rescaled to [0..1].")]
        [SerializeField] private bool renormalizeAfterDeadZone = true;
        [Tooltip("Smooth time (seconds) for handle to follow target. Use 0 for no smoothing.")]
        [Min(0f)]
        [SerializeField] private float handleSmoothTime = 0.06f;

        [Header("Behavior")]
        [Tooltip("If true, joystick visuals fade out when the finger is lifted.")]
        [SerializeField] private bool hideOnRelease = true;
        [Tooltip("Speed the joystick fades in/out (alpha per second). Higher = faster.")]
        [Min(0.1f)]
        [SerializeField] private float joystickFadeSpeed = 10f;
        [Tooltip("Where touches are allowed to start the joystick.")]
        [SerializeField] private ActivationRestriction activationRestriction = ActivationRestriction.FullScreen;

        [Header("Glow Visuals")]
        [Tooltip("If true, handle and background glow when active with smooth fade.")]
        [SerializeField] private bool useGlow = true;
        [Tooltip("How strong the glow is when pressed (0..1).")]
        [Range(0f, 1f)]
        [SerializeField] private float glowIntensity = 0.2f;
        [Tooltip("Speed the glow color fades (per second). Higher = faster.")]
        [Min(0.1f)]
        [SerializeField] private float glowFadeSpeed = 12f;

        [Header("Placeholder / Instructional")]
        [Tooltip("Optional placeholder that appears at the original position when the joystick is hidden.")]
        [SerializeField] private RectTransform placeholder;
        [SerializeField] private CanvasGroup placeholderCanvasGroup;
        [Tooltip("If true, placeholder shows when hidden.")]
        [SerializeField] private bool placeholderEnabled = true;
        [Tooltip("If true, the placeholder is only shown for a limited duration then fades out.")]
        [SerializeField] private bool placeholderTimedVisibility = false;
        [Tooltip("How long the placeholder stays visible (seconds) when timed visibility is enabled.")]
        [Min(0f)]
        [SerializeField] private float placeholderDuration = 2.0f;
        [Tooltip("Speed the placeholder fades in/out (alpha per second). Higher = faster.")]
        [Min(0.1f)]
        [SerializeField] private float placeholderFadeSpeed = 8f;
        [Tooltip("If true, show the placeholder again after releasing the joystick.")]
        [SerializeField] private bool placeholderReappearOnRelease = true;

        // Runtime state
        private Canvas _canvas;
        private Camera _eventCamera;
        private RectTransform _joystickContainerRect;
        private RectTransform _handleRect;
        private RectTransform _backgroundRect;

        private Vector2 _containerInitialAnchoredPos;
        private Vector2 _handleTargetLocalPos;
        private Vector2 _handleSmoothVelocity;
        private Vector2 _currentInput;
        private Vector2 _pressLocalPoint;

        private Color _initialBackgroundColor;
        private Color _initialHandleColor;

        private float _targetJoystickAlpha;
        private float _targetPlaceholderAlpha;

        private int _activePointerId = -1;
        private bool _isPressed;
        private Coroutine _placeholderTimerRoutine;

        public float Horizontal => _currentInput.x;
        public float Vertical => _currentInput.y;
        public Vector2 Direction => _currentInput;
        public bool IsPressed => _isPressed;

        private void Awake()
        {
            _canvas = GetComponentInParent<Canvas>();
            if (_canvas == null)
            {
                Debug.LogError("FloatingJoystick must be a child of a Canvas.", this);
            }

            _eventCamera = _canvas != null && _canvas.renderMode != RenderMode.ScreenSpaceOverlay
                ? _canvas.worldCamera
                : null;

            if (activationArea == null)
            {
                activationArea = GetComponent<RectTransform>();
            }

            _joystickContainerRect = joystickContainer;
            _handleRect = handleImage != null ? handleImage.rectTransform : null;
            _backgroundRect = backgroundImage != null ? backgroundImage.rectTransform : null;

            if (_joystickContainerRect == null)
            {
                Debug.LogError("Joystick Container is required.", this);
            }
            if (_handleRect == null || _backgroundRect == null)
            {
                Debug.LogError("Assign Background and Handle Images.", this);
            }
            if (joystickCanvasGroup == null && joystickContainer != null)
            {
                joystickCanvasGroup = joystickContainer.GetComponent<CanvasGroup>();
                if (joystickCanvasGroup == null)
                {
                    joystickCanvasGroup = joystickContainer.gameObject.AddComponent<CanvasGroup>();
                }
            }

            _initialBackgroundColor = backgroundImage != null ? backgroundImage.color : Color.white;
            _initialHandleColor = handleImage != null ? handleImage.color : Color.white;

            _containerInitialAnchoredPos = _joystickContainerRect != null ? _joystickContainerRect.anchoredPosition : Vector2.zero;

            if (placeholder != null && placeholderCanvasGroup == null)
            {
                placeholderCanvasGroup = placeholder.GetComponent<CanvasGroup>();
                if (placeholderCanvasGroup == null)
                {
                    placeholderCanvasGroup = placeholder.gameObject.AddComponent<CanvasGroup>();
                }
            }

            // Start hidden until first press, unless hideOnRelease is false (then we can start visible if desired)
            _targetJoystickAlpha = hideOnRelease ? 0f : 1f;
            if (joystickCanvasGroup != null)
            {
                joystickCanvasGroup.alpha = _targetJoystickAlpha;
                joystickCanvasGroup.interactable = true;
                joystickCanvasGroup.blocksRaycasts = false; // do not block screen touches
            }

            if (_handleRect != null)
            {
                _handleRect.anchoredPosition = Vector2.zero;
            }

            // Placeholder initial state
            if (placeholder != null)
            {
                placeholder.anchoredPosition = _containerInitialAnchoredPos;
            }
        }

        private void OnEnable()
        {
            _isPressed = false;
            _activePointerId = -1;
            _currentInput = Vector2.zero;
            _handleTargetLocalPos = Vector2.zero;
            _handleSmoothVelocity = Vector2.zero;

            if (hideOnRelease)
            {
                // Show placeholder on enable if configured
                SetPlaceholderVisible(placeholderEnabled, immediate: true);
                if (placeholderEnabled && placeholderTimedVisibility)
                {
                    StartPlaceholderTimer();
                }
            }
            else
            {
                // If not hiding on release, joystick starts visible and placeholder hidden
                SetPlaceholderVisible(false, immediate: true);
                SetJoystickVisible(true, immediate: true);
            }
        }

        private void OnDisable()
        {
            ResetInputAndHandle();
            _activePointerId = -1;
            _isPressed = false;
            StopPlaceholderTimer();
        }

        private void Update()
        {
            // Smooth handle movement
            if (_handleRect != null)
            {
                if (handleSmoothTime > 0f)
                {
                    _handleRect.anchoredPosition = Vector2.SmoothDamp(
                        _handleRect.anchoredPosition,
                        _handleTargetLocalPos,
                        ref _handleSmoothVelocity,
                        handleSmoothTime);
                }
                else
                {
                    _handleRect.anchoredPosition = _handleTargetLocalPos;
                }
            }

            // Fade joystick
            if (joystickCanvasGroup != null)
            {
                float step = joystickFadeSpeed * Time.unscaledDeltaTime;
                joystickCanvasGroup.alpha = Mathf.MoveTowards(joystickCanvasGroup.alpha, _targetJoystickAlpha, step);
            }

            // Glow
            if (useGlow)
            {
                float t = Mathf.Clamp01(glowFadeSpeed * Time.unscaledDeltaTime);
                if (backgroundImage != null)
                {
                    Color bgTarget = GetGlowTarget(_initialBackgroundColor, _isPressed ? glowIntensity : 0f);
                    backgroundImage.color = Color.Lerp(backgroundImage.color, bgTarget, t);
                }
                if (handleImage != null)
                {
                    Color handleTarget = GetGlowTarget(_initialHandleColor, _isPressed ? glowIntensity : 0f);
                    handleImage.color = Color.Lerp(handleImage.color, handleTarget, t);
                }
            }

            // Fade placeholder
            if (placeholderCanvasGroup != null)
            {
                float step = placeholderFadeSpeed * Time.unscaledDeltaTime;
                placeholderCanvasGroup.alpha = Mathf.MoveTowards(placeholderCanvasGroup.alpha, _targetPlaceholderAlpha, step);
                if (Mathf.Approximately(placeholderCanvasGroup.alpha, 0f))
                {
                    if (placeholderCanvasGroup.gameObject.activeSelf)
                    {
                        placeholderCanvasGroup.gameObject.SetActive(false);
                    }
                }
                else
                {
                    if (!placeholderCanvasGroup.gameObject.activeSelf)
                    {
                        placeholderCanvasGroup.gameObject.SetActive(true);
                    }
                }
            }
        }

        public void OnPointerDown(PointerEventData eventData)
        {
            if (_activePointerId != -1)
            {
                return; // already tracking a touch
            }

            if (!IsAllowedStartPosition(eventData.position))
            {
                return;
            }

            _activePointerId = eventData.pointerId;
            _isPressed = true;

            Vector2 localPoint;
            if (!RectTransformUtility.ScreenPointToLocalPointInRectangle(
                    activationArea, eventData.position, _eventCamera, out localPoint))
            {
                return;
            }

            // Position joystick container at first touch, reset handle
            if (_joystickContainerRect != null)
            {
                _joystickContainerRect.anchoredPosition = localPoint;
                _handleTargetLocalPos = Vector2.zero;
                if (_handleRect != null)
                {
                    _handleRect.anchoredPosition = Vector2.zero;
                }
            }

            _pressLocalPoint = localPoint;
            _currentInput = Vector2.zero;

            // Visuals
            SetJoystickVisible(true, immediate: false);
            SetPlaceholderVisible(false, immediate: false);
        }

        public void OnDrag(PointerEventData eventData)
        {
            if (eventData.pointerId != _activePointerId || !_isPressed)
            {
                return;
            }

            Vector2 localPoint;
            if (!RectTransformUtility.ScreenPointToLocalPointInRectangle(
                    activationArea, eventData.position, _eventCamera, out localPoint))
            {
                return;
            }

            Vector2 delta = localPoint - _joystickContainerRect.anchoredPosition;

            // Clamp to handle range
            float magnitude = delta.magnitude;
            Vector2 clamped = magnitude > Mathf.Epsilon
                ? Vector2.ClampMagnitude(delta, handleRange)
                : Vector2.zero;

            _handleTargetLocalPos = clamped;

            // Compute input with dead zone handling
            Vector2 input = Vector2.zero;
            if (magnitude > deadZoneRadius)
            {
                Vector2 dir = delta.normalized;
                float effective = handleRange;
                float scaledMag = magnitude;
                if (renormalizeAfterDeadZone)
                {
                    float denom = Mathf.Max(effective - deadZoneRadius, 0.0001f);
                    float t = Mathf.Clamp01((magnitude - deadZoneRadius) / denom);
                    scaledMag = t * effective;
                }
                input = dir * Mathf.Clamp01(scaledMag / Mathf.Max(effective, 0.0001f));
            }
            else
            {
                input = Vector2.zero;
            }

            _currentInput = input;
        }

        public void OnPointerUp(PointerEventData eventData)
        {
            if (eventData.pointerId != _activePointerId)
            {
                return;
            }

            _activePointerId = -1;
            _isPressed = false;

            ResetInputAndHandle();

            if (hideOnRelease)
            {
                SetJoystickVisible(false, immediate: false);
                if (placeholderEnabled && placeholderReappearOnRelease)
                {
                    // Return placeholder to its original position
                    if (placeholder != null)
                    {
                        placeholder.anchoredPosition = _containerInitialAnchoredPos;
                    }
                    SetPlaceholderVisible(true, immediate: false);
                    if (placeholderTimedVisibility)
                    {
                        StartPlaceholderTimer();
                    }
                }
            }
        }

        private void ResetInputAndHandle()
        {
            _currentInput = Vector2.zero;
            _handleTargetLocalPos = Vector2.zero;
        }

        private void SetJoystickVisible(bool visible, bool immediate)
        {
            _targetJoystickAlpha = visible ? 1f : 0f;
            if (immediate && joystickCanvasGroup != null)
            {
                joystickCanvasGroup.alpha = _targetJoystickAlpha;
            }
        }

        private void SetPlaceholderVisible(bool visible, bool immediate)
        {
            if (placeholderCanvasGroup == null)
            {
                return;
            }
            _targetPlaceholderAlpha = visible ? 1f : 0f;
            if (immediate)
            {
                placeholderCanvasGroup.alpha = _targetPlaceholderAlpha;
                placeholderCanvasGroup.gameObject.SetActive(visible);
            }
        }

        private void StartPlaceholderTimer()
        {
            StopPlaceholderTimer();
            if (!placeholderTimedVisibility || placeholderCanvasGroup == null)
            {
                return;
            }
            _placeholderTimerRoutine = StartCoroutine(PlaceholderTimerCoroutine());
        }

        private void StopPlaceholderTimer()
        {
            if (_placeholderTimerRoutine != null)
            {
                StopCoroutine(_placeholderTimerRoutine);
                _placeholderTimerRoutine = null;
            }
        }

        private IEnumerator PlaceholderTimerCoroutine()
        {
            float elapsed = 0f;
            while (elapsed < placeholderDuration)
            {
                if (_isPressed)
                {
                    yield break; // user interacted
                }
                elapsed += Time.unscaledDeltaTime;
                yield return null;
            }
            SetPlaceholderVisible(false, immediate: false);
            _placeholderTimerRoutine = null;
        }

        private bool IsAllowedStartPosition(Vector2 screenPosition)
        {
            switch (activationRestriction)
            {
                case ActivationRestriction.LeftHalf:
                    return screenPosition.x <= (Screen.width * 0.5f);
                case ActivationRestriction.RightHalf:
                    return screenPosition.x >= (Screen.width * 0.5f);
                default:
                    return true;
            }
        }

        private static Color GetGlowTarget(Color baseColor, float intensity)
        {
            // Lerp toward white to simulate glow; preserve base alpha
            Color target = Color.Lerp(baseColor, Color.white, Mathf.Clamp01(intensity));
            target.a = baseColor.a;
            return target;
        }

        // Public API for configuration at runtime
        public void SetSprites(Sprite background, Sprite handle)
        {
            if (backgroundImage != null) backgroundImage.sprite = background;
            if (handleImage != null) handleImage.sprite = handle;
        }

        public void SetRange(float rangePixels)
        {
            handleRange = Mathf.Max(1f, rangePixels);
        }

        public void SetDeadZone(float deadZonePixels)
        {
            deadZoneRadius = Mathf.Max(0f, deadZonePixels);
        }

        public void SetHideOnRelease(bool hidden)
        {
            hideOnRelease = hidden;
        }
    }
}

