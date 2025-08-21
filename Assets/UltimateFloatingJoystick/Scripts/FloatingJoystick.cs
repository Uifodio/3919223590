using System.Collections;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.Events;
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
            RightHalf = 2,
            TopHalf = 3,
            BottomHalf = 4
        }

        public enum AxisOptions
        {
            Both = 0,
            HorizontalOnly = 1,
            VerticalOnly = 2
        }

        public enum SnapMode
        {
            None = 0,
            Four = 4,
            Eight = 8
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

        [Header("Axes & Snapping")]
        [Tooltip("Restrict axes for input output.")]
        [SerializeField] private AxisOptions axisOptions = AxisOptions.Both;
        [Tooltip("Optional angular snapping: None, 4-way, or 8-way.")]
        [SerializeField] private SnapMode snapMode = SnapMode.None;

        [Header("Behavior")]
        [Tooltip("If true, joystick visuals fade out when the finger is lifted.")]
        [SerializeField] private bool hideOnRelease = true;
        [Tooltip("Speed the joystick fades in/out (alpha per second). Higher = faster.")]
        [Min(0.1f)]
        [SerializeField] private float joystickFadeSpeed = 10f;
        [Tooltip("Where touches are allowed to start the joystick.")]
        [SerializeField] private ActivationRestriction activationRestriction = ActivationRestriction.FullScreen;

        [Header("Output Smoothing & Events")]
        [Tooltip("Additional smoothing for the output Direction values. 0 to disable.")]
        [Min(0f)]
        [SerializeField] private float outputSmoothTime = 0f;
        [Tooltip("Enable keyboard/controller fallback when not touching (useful for desktop/editor). Uses Horizontal/Vertical axes.")]
        [SerializeField] private bool editorKeyboardFallback = true;
        [Space]
        [SerializeField] private UnityEvent onPress = new UnityEvent();
        [SerializeField] private UnityEvent onRelease = new UnityEvent();
        [System.Serializable]
        public class Vector2Event : UnityEvent<Vector2> {}
        [SerializeField] private Vector2Event onValueChanged = new Vector2Event();

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
        private Vector2 _currentInput; // output (optionally smoothed)
        private Vector2 _rawInput; // raw (pre-smoothing) from pointer/keyboard
        private Vector2 _outputSmoothVelocity;
        private Vector2 _lastSentInput;
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
        public float Magnitude => _currentInput.magnitude;
        public float AngleDegrees => Mathf.Atan2(_currentInput.y, _currentInput.x) * Mathf.Rad2Deg;
        public static FloatingJoystick ActiveInstance { get; private set; }
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
            if (ActiveInstance == null) ActiveInstance = this;
            _isPressed = false;
            _activePointerId = -1;
            _currentInput = Vector2.zero;
            _rawInput = Vector2.zero;
            _handleTargetLocalPos = Vector2.zero;
            _handleSmoothVelocity = Vector2.zero;
            _outputSmoothVelocity = Vector2.zero;
            _lastSentInput = Vector2.zero;

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
            if (ActiveInstance == this) ActiveInstance = null;
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

            // Output smoothing (and keyboard fallback when not pressed)
            if (!_isPressed && editorKeyboardFallback)
            {
                Vector2 kbd = new Vector2(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical"));
                if (kbd.sqrMagnitude > 1f) kbd.Normalize();
                _rawInput = ApplyAxisAndSnapping(kbd);
            }

            if (outputSmoothTime > 0f)
            {
                _currentInput = Vector2.SmoothDamp(_currentInput, _rawInput, ref _outputSmoothVelocity, outputSmoothTime);
            }
            else
            {
                _currentInput = _rawInput;
            }

            // Send change event if value updated
            if ((_currentInput - _lastSentInput).sqrMagnitude > 0.000001f)
            {
                onValueChanged?.Invoke(_currentInput);
                _lastSentInput = _currentInput;
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
            onPress?.Invoke();

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
            _rawInput = Vector2.zero;

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

            input = ApplyAxisAndSnapping(input);
            _rawInput = input;
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
            onRelease?.Invoke();
        }

        private void ResetInputAndHandle()
        {
            _currentInput = Vector2.zero;
            _rawInput = Vector2.zero;
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
                case ActivationRestriction.TopHalf:
                    return screenPosition.y >= (Screen.height * 0.5f);
                case ActivationRestriction.BottomHalf:
                    return screenPosition.y <= (Screen.height * 0.5f);
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

        public void SetAxisOptions(AxisOptions options)
        {
            axisOptions = options;
        }

        public void SetActivationRestriction(ActivationRestriction restriction)
        {
            activationRestriction = restriction;
        }

        private Vector2 ApplyAxisAndSnapping(Vector2 input)
        {
            switch (axisOptions)
            {
                case AxisOptions.HorizontalOnly:
                    input.y = 0f;
                    break;
                case AxisOptions.VerticalOnly:
                    input.x = 0f;
                    break;
            }

            if (snapMode != SnapMode.None && input.sqrMagnitude > 0f)
            {
                float angle = Mathf.Atan2(input.y, input.x) * Mathf.Rad2Deg;
                int slices = (int)snapMode; // 4 or 8
                float step = 360f / slices;
                float snappedAngle = Mathf.Round(angle / step) * step;
                float mag = input.magnitude;
                float rad = snappedAngle * Mathf.Deg2Rad;
                input = new Vector2(Mathf.Cos(rad), Mathf.Sin(rad)) * mag;
            }
            return input;
        }
    }
}

