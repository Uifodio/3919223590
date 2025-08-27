using UnityEngine;
using System.Collections;
using System.Collections.Generic;

/// <summary>
/// Sample Unity C# script to demonstrate Anora Editor syntax highlighting
/// </summary>
public class SamplePlayerController : MonoBehaviour
{
    [Header("Player Settings")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpForce = 10f;
    [SerializeField] private LayerMask groundLayer = 1;
    
    [Header("References")]
    [SerializeField] private Transform groundCheck;
    [SerializeField] private Rigidbody2D rb;
    [SerializeField] private Animator animator;
    
    // Private variables
    private bool isGrounded;
    private float horizontalInput;
    private const float GROUND_CHECK_RADIUS = 0.2f;
    
    /// <summary>
    /// Called when the script instance is being loaded
    /// </summary>
    private void Awake()
    {
        // Validate required components
        if (rb == null)
            rb = GetComponent<Rigidbody2D>();
            
        if (animator == null)
            animator = GetComponent<Animator>();
    }
    
    /// <summary>
    /// Called every frame
    /// </summary>
    private void Update()
    {
        // Get input
        horizontalInput = Input.GetAxisRaw("Horizontal");
        
        // Check if grounded
        isGrounded = Physics2D.OverlapCircle(groundCheck.position, GROUND_CHECK_RADIUS, groundLayer);
        
        // Handle jump input
        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            Jump();
        }
        
        // Update animations
        UpdateAnimations();
    }
    
    /// <summary>
    /// Called every fixed frame-rate frame
    /// </summary>
    private void FixedUpdate()
    {
        // Move the player
        Move();
    }
    
    /// <summary>
    /// Moves the player horizontally
    /// </summary>
    private void Move()
    {
        Vector2 velocity = rb.velocity;
        velocity.x = horizontalInput * moveSpeed;
        rb.velocity = velocity;
        
        // Flip sprite based on direction
        if (horizontalInput != 0)
        {
            transform.localScale = new Vector3(Mathf.Sign(horizontalInput), 1f, 1f);
        }
    }
    
    /// <summary>
    /// Makes the player jump
    /// </summary>
    private void Jump()
    {
        rb.AddForce(Vector2.up * jumpForce, ForceMode2D.Impulse);
        
        // Play jump sound
        AudioManager.Instance?.PlaySound("jump");
    }
    
    /// <summary>
    /// Updates the animator parameters
    /// </summary>
    private void UpdateAnimations()
    {
        if (animator != null)
        {
            animator.SetBool("IsGrounded", isGrounded);
            animator.SetFloat("Speed", Mathf.Abs(horizontalInput));
        }
    }
    
    /// <summary>
    /// Called when this collider/rigidbody has begun touching another rigidbody/collider
    /// </summary>
    private void OnCollisionEnter2D(Collision2D collision)
    {
        // Check if we landed on an enemy
        if (collision.gameObject.CompareTag("Enemy"))
        {
            // Bounce off enemy
            rb.AddForce(Vector2.up * jumpForce * 0.5f, ForceMode2D.Impulse);
            
            // Damage enemy
            Enemy enemy = collision.gameObject.GetComponent<Enemy>();
            enemy?.TakeDamage();
        }
    }
    
    /// <summary>
    /// Called when the player takes damage
    /// </summary>
    public void TakeDamage()
    {
        // Implement damage logic here
        Debug.Log("Player took damage!");
        
        // Play damage animation
        animator?.SetTrigger("TakeDamage");
        
        // Play damage sound
        AudioManager.Instance?.PlaySound("damage");
    }
    
    /// <summary>
    /// Called when the player collects a power-up
    /// </summary>
    /// <param name="powerUpType">The type of power-up collected</param>
    public void CollectPowerUp(PowerUpType powerUpType)
    {
        switch (powerUpType)
        {
            case PowerUpType.SpeedBoost:
                StartCoroutine(SpeedBoostCoroutine());
                break;
            case PowerUpType.DoubleJump:
                EnableDoubleJump();
                break;
            case PowerUpType.Shield:
                ActivateShield();
                break;
        }
    }
    
    /// <summary>
    /// Coroutine for speed boost power-up
    /// </summary>
    private IEnumerator SpeedBoostCoroutine()
    {
        float originalSpeed = moveSpeed;
        moveSpeed *= 2f;
        
        yield return new WaitForSeconds(10f);
        
        moveSpeed = originalSpeed;
    }
    
    /// <summary>
    /// Enables double jump ability
    /// </summary>
    private void EnableDoubleJump()
    {
        // Implementation for double jump
        Debug.Log("Double jump enabled!");
    }
    
    /// <summary>
    /// Activates shield power-up
    /// </summary>
    private void ActivateShield()
    {
        // Implementation for shield
        Debug.Log("Shield activated!");
    }
}

/// <summary>
/// Enum for different power-up types
/// </summary>
public enum PowerUpType
{
    SpeedBoost,
    DoubleJump,
    Shield
}