using System;
using System.Collections.Generic;
using UnityEngine;

namespace ResourceSystem
{
    [Serializable]
    public class RewardEntry
    {
        public string resourceId = "money";
        public double amount = 1;
    }

    public class RewardIdentifier : MonoBehaviour
    {
        [Header("Reward Entries")]
        public List<RewardEntry> rewards = new List<RewardEntry>();

        [Header("Behavior")]
        public bool destroyOnCollect = true;
        public GameObject collectEffectPrefab;

        public void Collect()
        {
            if (ResourceManager.Instance == null)
            {
                Debug.LogWarning("[RewardIdentifier] No ResourceManager in scene.");
                return;
            }

            foreach (var entry in rewards)
            {
                if (entry == null || string.IsNullOrWhiteSpace(entry.resourceId)) continue;
                if (entry.amount >= 0)
                {
                    ResourceManager.Instance.AddResource(entry.resourceId, entry.amount);
                }
                else
                {
                    ResourceManager.Instance.SpendResource(entry.resourceId, -entry.amount);
                }
            }

            if (collectEffectPrefab != null)
            {
                Instantiate(collectEffectPrefab, transform.position, Quaternion.identity);
            }

            if (destroyOnCollect)
            {
                Destroy(gameObject);
            }
        }
    }
}

