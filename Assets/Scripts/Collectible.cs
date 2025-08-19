using System.Collections;
using UnityEngine;

public class Collectible : MonoBehaviour
{
	[Header("Visual Motion")]
	public float floatAmplitude = 0.15f;
	public float floatFrequency = 1.5f;
	public Vector3 rotationSpeedEuler = new Vector3(0f, 90f, 0f);

	[Header("Magnet Settings")]
	public float magnetDelay = 0.6f;
	public float magnetAcceleration = 25f;
	public float magnetMaxSpeed = 10f;
	public float collectDistance = 0.75f;

	[Header("Resource Payload")]
	public string resourceId = "Wood";
	public int amount = 1;

	[Header("FX")]
	public AudioClip collectSfx;
	public ParticleSystem collectParticlesPrefab;

	private Vector3 _startPosition;
	private float _sineTime;
	private bool _magnetEnabled;
	private float _currentMagnetSpeed;
	private Transform _targetPlayer;
\tprivate Coroutine _magnetDelayRoutine;

	private void OnEnable()
	{
		_startPosition = transform.position;
		_sineTime = UnityEngine.Random.Range(0f, 100f);
		_currentMagnetSpeed = 0f;
		_magnetEnabled = false;
		_targetPlayer = null;
		_magnetDelayRoutine = StartCoroutine(EnableMagnetAfterDelay());
	}

	private IEnumerator EnableMagnetAfterDelay()
	{
		if (magnetDelay > 0f)
		{
			yield return new WaitForSeconds(magnetDelay);
		}
		_magnetEnabled = true;
	}

	private void Update()
	{
		// Always rotate
		transform.Rotate(rotationSpeedEuler * Time.deltaTime, Space.World);

		if (_magnetEnabled)
		{
			UpdateMagnet();
		}
		else
		{
			AnimateFloat();
		}
	}

	private void AnimateFloat()
	{
		_sineTime += Time.deltaTime * floatFrequency;
		float offset = Mathf.Sin(_sineTime) * floatAmplitude;
		Vector3 pos = _startPosition;
		pos.y += offset;
		transform.position = pos;
	}

	private void UpdateMagnet()
	{
		if (_targetPlayer == null)
		{
			if (GameDataManager.Instance != null)
			{
				_targetPlayer = GameDataManager.Instance.transform;
				Transform bound = GameDataManager.Instance.playerTransform;
				if (bound != null)
				{
					_targetPlayer = bound;
				}
			}
		}
		if (_targetPlayer == null) return;

		_currentMagnetSpeed = Mathf.Min(magnetMaxSpeed, _currentMagnetSpeed + magnetAcceleration * Time.deltaTime);
		Vector3 direction = (_targetPlayer.position - transform.position);
		float distance = direction.magnitude;
		if (distance > 0.0001f)
		{
			Vector3 velocity = direction.normalized * _currentMagnetSpeed;
			transform.position += velocity * Time.deltaTime;
		}

		if (distance <= collectDistance)
		{
			Collect();
		}
	}

	public void BeginMagnetNow()
	{
		if (_magnetEnabled) return;
		_magnetEnabled = true;
		if (_magnetDelayRoutine != null)
		{
			StopCoroutine(_magnetDelayRoutine);
			_magnetDelayRoutine = null;
		}
	}

	private void Collect()
	{
		if (GameDataManager.Instance != null && !string.IsNullOrEmpty(resourceId) && amount != 0)
		{
			GameDataManager.Instance.AddResource(resourceId, amount);
		}

		if (collectParticlesPrefab != null)
		{
			ParticleSystem particles = Instantiate(collectParticlesPrefab, transform.position, Quaternion.identity);
			particles.Play();
			Destroy(particles.gameObject, particles.main.duration + particles.main.startLifetime.constantMax + 0.5f);
		}

		if (collectSfx != null)
		{
			AudioSource.PlayClipAtPoint(collectSfx, transform.position);
		}

		Destroy(gameObject);
	}
}

