using UnityEngine;

public class GameResourceCollector : MonoBehaviour
{
    [Header("Collection Settings")]
    public string resourceId = "coins";
    public long amount = 1;
    public bool gravityToPlayer = true;
    public float gravityStrength = 5f;
    public float collectRadius = 2f;
    public string playerTag = "Player";
    public bool destroyOnCollect = true;
    
    [Header("Visual Effects")]
    public GameObject collectEffect;
    public AudioClip collectSound;
    
    private Transform playerTransform;
    private bool isCollected = false;
    private AudioSource audioSource;
    
    void Start()
    {
        // Find player
        GameObject player = GameObject.FindGameObjectWithTag(playerTag);
        if (player == null)
        {
            player = GameObject.Find("Player");
        }
        if (player != null)
        {
            playerTransform = player.transform;
        }
        
        // Get audio source
        audioSource = GetComponent<AudioSource>();
        if (audioSource == null)
        {
            audioSource = gameObject.AddComponent<AudioSource>();
        }
    }
    
    void Update()
    {
        if (isCollected || playerTransform == null) return;
        
        float distance = Vector3.Distance(transform.position, playerTransform.position);
        
        if (distance <= collectRadius)
        {
            CollectResource();
        }
        else if (gravityToPlayer && distance <= collectRadius * 2f)
        {
            // Move towards player
            Vector3 direction = (playerTransform.position - transform.position).normalized;
            transform.position += direction * gravityStrength * Time.deltaTime;
        }
    }
    
    void CollectResource()
    {
        if (isCollected) return;
        
        isCollected = true;
        
        // Add resource
        if (GameResourceManager.Instance != null)
        {
            GameResourceManager.Instance.AddResource(resourceId, amount);
        }
        
        // Play effects
        if (collectEffect != null)
        {
            Instantiate(collectEffect, transform.position, Quaternion.identity);
        }
        
        if (collectSound != null && audioSource != null)
        {
            audioSource.PlayOneShot(collectSound);
        }
        
        // Destroy object
        if (destroyOnCollect)
        {
            Destroy(gameObject);
        }
        else
        {
            gameObject.SetActive(false);
        }
        
        Debug.Log("[GameResourceCollector] Collected " + amount + " " + resourceId);
    }
    
    void OnDrawGizmosSelected()
    {
        // Draw collect radius
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, collectRadius);
        
        // Draw gravity radius
        Gizmos.color = Color.blue;
        Gizmos.DrawWireSphere(transform.position, collectRadius * 2f);
    }
    
    // Debug methods
    [ContextMenu("Collect Resource")]
    public void CollectResourceDebug()
    {
        CollectResource();
    }
}