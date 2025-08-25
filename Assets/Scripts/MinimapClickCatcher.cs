using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

/// <summary>
/// Captures pointer clicks within the minimap UI area and forwards them to the MinimapSystem.
/// Ensures a raycastable Graphic exists even if visually transparent.
/// </summary>
public class MinimapClickCatcher : MonoBehaviour, IPointerClickHandler, IPointerDownHandler, IPointerUpHandler, IDragHandler
{
    [Tooltip("Reference to the MinimapSystem that owns this click catcher. If null, it will search in parents.")]
    public MinimapSystem minimapSystem;
    [Tooltip("If true, this catcher belongs to the expanded map overlay.")]
    public bool forExpanded = false;

    private RectTransform rectTransform;
    private Image raycastImage;

    private void Awake()
    {
        rectTransform = GetComponent<RectTransform>();
        if (minimapSystem == null)
        {
            minimapSystem = GetComponentInParent<MinimapSystem>();
        }

        raycastImage = GetComponent<Image>();
        if (raycastImage == null)
        {
            raycastImage = gameObject.AddComponent<Image>();
        }

        // Make sure it receives raycasts while staying visually invisible.
        raycastImage.raycastTarget = true;
        var c = raycastImage.color;
        if (c.a < 0.001f)
        {
            c.a = 0.001f;
            raycastImage.color = c;
        }
    }

    public void OnPointerClick(PointerEventData eventData)
    {
        if (minimapSystem == null || rectTransform == null) return;
        if (RectTransformUtility.ScreenPointToLocalPointInRectangle(rectTransform, eventData.position, eventData.pressEventCamera, out var local))
        {
            minimapSystem.HandleMinimapPointer(local, eventData);
        }
    }

    public void OnPointerDown(PointerEventData eventData)
    {
        // Optional: support press-and-hold behavior in the future.
    }

    public void OnPointerUp(PointerEventData eventData)
    {
        // Optional: support press-and-hold behavior in the future.
    }

    public void OnDrag(PointerEventData eventData)
    {
        // Optional: allow dragging to move a waypoint preview.
    }
}

