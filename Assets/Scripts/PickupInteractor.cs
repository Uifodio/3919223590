using UnityEngine;

[RequireComponent(typeof(SphereCollider))]
public class PickupInteractor : MonoBehaviour
{
	[Header("Interactor Radius")]
	public float radius = 2.0f;
	[Tooltip("Whether to show the interactor radius in the editor scene view for tuning.")]
	public bool showGizmo = true;
	public Color gizmoColor = new Color(0.2f, 0.9f, 0.4f, 0.25f);

	[Header("Filters/Behavior")]
	[Tooltip("If true, only GameObjects on this layer will be considered as collectibles. Set to -1 to ignore layer filtering.")]
	public int collectibleLayer = -1;
	[Tooltip("If true, also trigger magnet for collectibles already inside the trigger when enabled.")]
	public bool sweepAtStart = true;

	private SphereCollider _collider;

	private void Reset()
	{
		SetupCollider();
	}

	private void Awake()
	{
		SetupCollider();
		if (sweepAtStart)
		{
			SweepForCollectiblesAndTrigger();
		}
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
			if (collectibleLayer >= 0 && other.gameObject.layer != collectibleLayer) return;
			collectible.BeginMagnetNow();
		}
	}

	private void SweepForCollectiblesAndTrigger()
	{
		Collider[] hits = Physics.OverlapSphere(transform.position, Mathf.Max(0.01f, radius));
		for (int i = 0; i < hits.Length; i++)
		{
			Collider c = hits[i];
			var collectible = c.attachedRigidbody != null ? c.attachedRigidbody.GetComponent<Collectible>() : c.GetComponent<Collectible>();
			if (collectible == null) continue;
			if (collectibleLayer >= 0 && c.gameObject.layer != collectibleLayer) continue;
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

