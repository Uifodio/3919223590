using UnityEngine;
using System.Collections;
using System.Collections.Generic;

namespace AnoraEditor.Demo
{
    /// <summary>
    /// Demo MonoBehaviour class to showcase Anora Editor's C# syntax highlighting
    /// </summary>
    public class DemoController : MonoBehaviour
    {
        [Header("Demo Settings")]
        [SerializeField] private string playerName = "Player";
        [SerializeField] private int maxHealth = 100;
        [SerializeField] private float moveSpeed = 5.0f;
        [SerializeField] private bool isActive = true;
        
        [Header("References")]
        [SerializeField] private Transform target;
        [SerializeField] private GameObject[] collectibles;
        
        // Private fields
        private float currentHealth;
        private Vector3 startPosition;
        private List<GameObject> activeCollectibles;
        
        // Properties
        public bool IsAlive => currentHealth > 0;
        public float HealthPercentage => currentHealth / maxHealth;
        
        // Events
        public System.Action<float> OnHealthChanged;
        public System.Action OnPlayerDied;
        
        #region Unity Lifecycle
        
        private void Awake()
        {
            InitializeComponents();
        }
        
        private void Start()
        {
            SetupDemo();
        }
        
        private void Update()
        {
            HandleInput();
            UpdateMovement();
        }
        
        private void OnTriggerEnter(Collider other)
        {
            HandleCollision(other);
        }
        
        #endregion
        
        #region Initialization
        
        private void InitializeComponents()
        {
            currentHealth = maxHealth;
            startPosition = transform.position;
            activeCollectibles = new List<GameObject>();
            
            // Validate required components
            if (target == null)
            {
                Debug.LogWarning("Target not assigned to DemoController!");
            }
        }
        
        private void SetupDemo()
        {
            Debug.Log($"Anora Editor Demo initialized for player: {playerName}");
            
            // Spawn collectibles
            if (collectibles != null && collectibles.Length > 0)
            {
                SpawnCollectibles();
            }
        }
        
        #endregion
        
        #region Gameplay Logic
        
        private void HandleInput()
        {
            if (!isActive) return;
            
            // Movement input
            float horizontal = Input.GetAxis("Horizontal");
            float vertical = Input.GetAxis("Vertical");
            
            Vector3 movement = new Vector3(horizontal, 0, vertical) * moveSpeed * Time.deltaTime;
            transform.Translate(movement);
            
            // Action input
            if (Input.GetKeyDown(KeyCode.Space))
            {
                PerformAction();
            }
            
            if (Input.GetKeyDown(KeyCode.R))
            {
                ResetDemo();
            }
        }
        
        private void UpdateMovement()
        {
            if (target != null && isActive)
            {
                // Simple follow behavior
                Vector3 direction = (target.position - transform.position).normalized;
                transform.LookAt(target);
            }
        }
        
        private void HandleCollision(Collider other)
        {
            if (other.CompareTag("Collectible"))
            {
                CollectItem(other.gameObject);
            }
            else if (other.CompareTag("Hazard"))
            {
                TakeDamage(20);
            }
        }
        
        #endregion
        
        #region Actions
        
        private void PerformAction()
        {
            if (!IsAlive) return;
            
            Debug.Log($"{playerName} performed an action!");
            
            // Example action logic
            if (Random.Range(0f, 1f) > 0.5f)
            {
                Heal(10);
            }
        }
        
        private void CollectItem(GameObject item)
        {
            if (activeCollectibles.Contains(item))
            {
                activeCollectibles.Remove(item);
                item.SetActive(false);
                
                Debug.Log($"Collected item! Total: {activeCollectibles.Count}");
                
                // Check win condition
                if (activeCollectibles.Count == 0)
                {
                    OnDemoCompleted();
                }
            }
        }
        
        #endregion
        
        #region Health System
        
        private void TakeDamage(float damage)
        {
            if (!IsAlive) return;
            
            currentHealth = Mathf.Max(0, currentHealth - damage);
            OnHealthChanged?.Invoke(HealthPercentage);
            
            Debug.Log($"{playerName} took {damage} damage! Health: {currentHealth}");
            
            if (!IsAlive)
            {
                OnPlayerDied?.Invoke();
                Debug.Log($"{playerName} has died!");
            }
        }
        
        private void Heal(float amount)
        {
            if (!IsAlive) return;
            
            currentHealth = Mathf.Min(maxHealth, currentHealth + amount);
            OnHealthChanged?.Invoke(HealthPercentage);
            
            Debug.Log($"{playerName} healed {amount} health! Health: {currentHealth}");
        }
        
        #endregion
        
        #region Demo Management
        
        private void SpawnCollectibles()
        {
            for (int i = 0; i < collectibles.Length; i++)
            {
                if (collectibles[i] != null)
                {
                    GameObject spawned = Instantiate(collectibles[i], 
                        startPosition + Random.insideUnitSphere * 5f, 
                        Quaternion.identity);
                    
                    activeCollectibles.Add(spawned);
                }
            }
        }
        
        private void ResetDemo()
        {
            Debug.Log("Resetting demo...");
            
            // Reset health
            currentHealth = maxHealth;
            OnHealthChanged?.Invoke(HealthPercentage);
            
            // Reset position
            transform.position = startPosition;
            
            // Respawn collectibles
            foreach (GameObject item in activeCollectibles)
            {
                if (item != null)
                {
                    Destroy(item);
                }
            }
            activeCollectibles.Clear();
            
            SpawnCollectibles();
        }
        
        private void OnDemoCompleted()
        {
            Debug.Log($"Congratulations! {playerName} completed the demo!");
            isActive = false;
        }
        
        #endregion
        
        #region Utility Methods
        
        public void SetActive(bool active)
        {
            isActive = active;
            Debug.Log($"Demo {playerName} active: {isActive}");
        }
        
        public void SetMoveSpeed(float speed)
        {
            moveSpeed = Mathf.Max(0, speed);
            Debug.Log($"Move speed set to: {moveSpeed}");
        }
        
        #endregion
    }
}