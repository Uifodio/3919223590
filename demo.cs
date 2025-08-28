using UnityEngine;
using System.Collections;
using System.Collections.Generic;

namespace NexusEditor.Demo
{
    /// <summary>
    /// Demo script to showcase Nexus Editor's C# syntax highlighting
    /// </summary>
    public class DemoScript : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private float speed = 5.0f;
        [SerializeField] private Color playerColor = Color.blue;
        [SerializeField] private bool isActive = true;
        
        // Private fields
        private Transform playerTransform;
        private Vector3 startPosition;
        private int healthPoints = 100;
        private string playerName = "Player";
        
        // Constants
        private const float MAX_SPEED = 10.0f;
        private const string GAME_TAG = "Player";
        
        /// <summary>
        /// Unity's Start method - called once when the script is initialized
        /// </summary>
        void Start()
        {
            InitializePlayer();
            SetupGameObjects();
        }
        
        /// <summary>
        /// Unity's Update method - called every frame
        /// </summary>
        void Update()
        {
            if (!isActive) return;
            
            HandlePlayerMovement();
            CheckGameState();
        }
        
        /// <summary>
        /// Initialize player-related variables and components
        /// </summary>
        private void InitializePlayer()
        {
            playerTransform = transform;
            startPosition = playerTransform.position;
            
            // Set player color
            Renderer renderer = GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material.color = playerColor;
            }
        }
        
        /// <summary>
        /// Setup game objects and find references
        /// </summary>
        private void SetupGameObjects()
        {
            GameObject[] players = GameObject.FindGameObjectsWithTag(GAME_TAG);
            Debug.Log($"Found {players.Length} players in the scene");
            
            // Example of using a List
            List<GameObject> activePlayers = new List<GameObject>();
            foreach (GameObject player in players)
            {
                if (player.activeInHierarchy)
                {
                    activePlayers.Add(player);
                }
            }
        }
        
        /// <summary>
        /// Handle player movement input and physics
        /// </summary>
        private void HandlePlayerMovement()
        {
            float horizontalInput = Input.GetAxis("Horizontal");
            float verticalInput = Input.GetAxis("Vertical");
            
            Vector3 movement = new Vector3(horizontalInput, 0, verticalInput);
            movement = movement.normalized * speed * Time.deltaTime;
            
            // Clamp speed to maximum
            if (movement.magnitude > MAX_SPEED)
            {
                movement = movement.normalized * MAX_SPEED;
            }
            
            playerTransform.Translate(movement);
        }
        
        /// <summary>
        /// Check current game state and handle transitions
        /// </summary>
        private void CheckGameState()
        {
            // Example of switch statement
            switch (healthPoints)
            {
                case 100:
                    Debug.Log("Player is at full health!");
                    break;
                case 0:
                    GameOver();
                    break;
                default:
                    if (healthPoints < 25)
                    {
                        Debug.LogWarning("Player health is low!");
                    }
                    break;
            }
        }
        
        /// <summary>
        /// Handle game over scenario
        /// </summary>
        private void GameOver()
        {
            isActive = false;
            Debug.LogError("Game Over! Player has no health remaining.");
            
            // Reset player position
            playerTransform.position = startPosition;
            healthPoints = 100;
            isActive = true;
        }
        
        /// <summary>
        /// Public method to modify player health
        /// </summary>
        /// <param name="amount">Amount to change health by (positive for healing, negative for damage)</param>
        public void ModifyHealth(int amount)
        {
            healthPoints = Mathf.Clamp(healthPoints + amount, 0, 100);
            Debug.Log($"Health modified by {amount}. Current health: {healthPoints}");
        }
        
        /// <summary>
        /// Coroutine example for delayed actions
        /// </summary>
        /// <param name="delay">Delay in seconds</param>
        /// <returns>IEnumerator for coroutine</returns>
        private IEnumerator DelayedAction(float delay)
        {
            yield return new WaitForSeconds(delay);
            Debug.Log($"Delayed action executed after {delay} seconds");
        }
        
        /// <summary>
        /// Example of using properties
        /// </summary>
        public float CurrentSpeed
        {
            get { return speed; }
            set { speed = Mathf.Clamp(value, 0, MAX_SPEED); }
        }
        
        public string PlayerName
        {
            get { return playerName; }
            set { playerName = value; }
        }
    }
}