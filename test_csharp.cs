using UnityEngine;

public class TestScript : MonoBehaviour
{
    [SerializeField] private string message = "Hello from Unity!";
    
    void Start()
    {
        Debug.Log(message);
    }
    
    void Update()
    {
        // Update logic here
        if (Input.GetKeyDown(KeyCode.Space))
        {
            Debug.Log("Space pressed!");
        }
    }
}
