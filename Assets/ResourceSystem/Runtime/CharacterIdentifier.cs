using System;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace ResourceSystem
{
    [RequireComponent(typeof(Collider))]
    public class CharacterIdentifier : MonoBehaviour
    {
        [Header("Identity")]
        public string characterId = "MainCharacter";

        [Header("Magnet Settings")]
        public float magnetRadius = 4f;
        public float magnetForce = 15f;
        public LayerMask rewardLayer;

        [Header("Runtime")]
        public bool persistTransform = true;
        public bool enableMagnet = true;

        private double sessionPlaytimeSeconds = 0;

        void Awake()
        {
            var col = GetComponent<Collider>();
            col.isTrigger = true;
        }

        void Start()
        {
            TryRestoreTransform();
        }

        void Update()
        {
            sessionPlaytimeSeconds += Time.unscaledDeltaTime;

            if (enableMagnet && magnetRadius > 0f)
            {
                AttractNearbyRewards();
            }

            if (persistTransform && ResourceManager.Instance != null)
            {
                ResourceManager.Instance.RegisterOrUpdateCharacterState(
                    characterId,
                    transform.position,
                    transform.rotation,
                    SceneManager.GetActiveScene().name,
                    Time.unscaledDeltaTime
                );
            }
        }

        private void TryRestoreTransform()
        {
            if (!persistTransform || ResourceManager.Instance == null) return;
            if (ResourceManager.Instance.TryGetCharacterState(characterId, out var state))
            {
                transform.position = state.position;
                transform.rotation = state.rotation;
            }
        }

        private void AttractNearbyRewards()
        {
            var hits = Physics.OverlapSphere(transform.position, magnetRadius, rewardLayer);
            foreach (var hit in hits)
            {
                var rb = hit.attachedRigidbody;
                if (rb != null)
                {
                    var direction = (transform.position - rb.position).normalized;
                    rb.AddForce(direction * magnetForce, ForceMode.Acceleration);
                }
                else
                {
                    hit.transform.position = Vector3.MoveTowards(hit.transform.position, transform.position, magnetForce * Time.deltaTime);
                }
            }
        }

        void OnTriggerEnter(Collider other)
        {
            var reward = other.GetComponent<RewardIdentifier>();
            if (reward != null)
            {
                reward.Collect();
            }
        }
    }
}

