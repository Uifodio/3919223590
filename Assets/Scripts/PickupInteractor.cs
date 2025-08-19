using UnityEngine;

[RequireComponent(typeof(SphereCollider))]
public class PickupInteractor : MonoBehaviour
{
	[Header("Interactor Radius")]
	public float radius = 2.0f;
	[Tooltip("Whether to show the interactor radius in the editor scene view for tuning.")]
	public bool showGizmo = true;
	public Color gizmoColor = new Color(0.2f, 0.9f, 0.4f, 0.25f);

	private SphereCollider _collider;

	private void Reset()
	{
		SetupCollider();
	}

	private void Awake()
	{
		SetupCollider();
	}

	private void SetupCollider()
	{
		_collider = GetComponent<SphereCollider>();
		_collider.isTrigger = true;
		_collider.radius = radius;
	}

	private void OnValidate()
	{
		if (_collider == null)
		{
			_collider = GetComponent<SphereCollider>();
		}
		if (_collider != null)
		{
			_collider.isTrigger = true;
			_collider.radius = Mathf.Max(0.01f, radius);
		}
	}

	private void OnTriggerEnter(Collider other)
	{
		var collectible = other.attachedRigidbody != null
			? other.attachedRigidbody.GetComponent<Collectible>()
			: other.GetComponent<Collectible>();
		if (collectible != null)
		{
			collectible.BeginMagnetNow();
		}
	}

	private void OnDrawGizmosSelected()
	{
		if (!showGizmo) return;
		Gizmos.color = gizmoColor;
		Gizmos.DrawSphere(transform.position, Mathf.Max(0.01f, radius));
	}
}

