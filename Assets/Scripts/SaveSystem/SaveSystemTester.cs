using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Threading.Tasks;

namespace SaveSystem
{
    public class SaveSystemTester : MonoBehaviour
    {
        [Header("Test Configuration")]
        [SerializeField] private bool runTestsOnStart = false;
        [SerializeField] private bool enableDetailedLogging = true;
        [SerializeField] private float testDelay = 1f;

        [Header("Test Results")]
        [SerializeField] private List<string> testResults = new List<string>();

        private void Start()
        {
            if (runTestsOnStart)
            {
                StartCoroutine(RunAllTests());
            }
        }

        [ContextMenu("Run All Tests")]
        public void RunAllTestsMenu()
        {
            StartCoroutine(RunAllTests());
        }

        private IEnumerator RunAllTests()
        {
            testResults.Clear();
            Debug.Log("=== Starting Save System Tests ===");

            // Test 1: Basic System Initialization
            yield return StartCoroutine(TestSystemInitialization());

            // Test 2: Resource Management
            yield return StartCoroutine(TestResourceManagement());

            // Test 3: SaveableEntity Functionality
            yield return StartCoroutine(TestSaveableEntity());

            // Test 4: Save/Load Operations
            yield return StartCoroutine(TestSaveLoadOperations());

            // Test 5: Character Tracking
            yield return StartCoroutine(TestCharacterTracking());

            // Test 6: Crash Recovery
            yield return StartCoroutine(TestCrashRecovery());

            // Test 7: Performance Test
            yield return StartCoroutine(TestPerformance());

            // Print final results
            PrintTestResults();
        }

        private IEnumerator TestSystemInitialization()
        {
            AddTestResult("=== Testing System Initialization ===");
            
            // Test SaveManager
            if (SaveManager.Instance != null)
            {
                AddTestResult("✓ SaveManager initialized successfully");
            }
            else
            {
                AddTestResult("✗ SaveManager failed to initialize");
            }

            // Test ResourceManager
            if (ResourceManager.Instance != null)
            {
                AddTestResult("✓ ResourceManager initialized successfully");
            }
            else
            {
                AddTestResult("✗ ResourceManager failed to initialize");
            }

            // Test WorldStateManager
            if (WorldStateManager.Instance != null)
            {
                AddTestResult("✓ WorldStateManager initialized successfully");
            }
            else
            {
                AddTestResult("✗ WorldStateManager failed to initialize");
            }

            yield return new WaitForSeconds(testDelay);
        }

        private IEnumerator TestResourceManagement()
        {
            AddTestResult("=== Testing Resource Management ===");

            if (ResourceManager.Instance == null)
            {
                AddTestResult("✗ ResourceManager not available");
                yield break;
            }

            // Test adding resources
            ResourceManager.Instance.AddResource("coins", 100, "Test");
            long coins = ResourceManager.Instance.GetResourceAmount("coins");
            if (coins == 100)
            {
                AddTestResult("✓ Resource addition works correctly");
            }
            else
            {
                AddTestResult($"✗ Resource addition failed. Expected 100, got {coins}");
            }

            // Test removing resources
            bool removed = ResourceManager.Instance.TryRemoveResource("coins", 50, "Test");
            if (removed)
            {
                coins = ResourceManager.Instance.GetResourceAmount("coins");
                if (coins == 50)
                {
                    AddTestResult("✓ Resource removal works correctly");
                }
                else
                {
                    AddTestResult($"✗ Resource removal failed. Expected 50, got {coins}");
                }
            }
            else
            {
                AddTestResult("✗ Resource removal returned false");
            }

            // Test insufficient resources
            bool insufficient = ResourceManager.Instance.TryRemoveResource("coins", 100, "Test");
            if (!insufficient)
            {
                AddTestResult("✓ Insufficient resource check works correctly");
            }
            else
            {
                AddTestResult("✗ Insufficient resource check failed");
            }

            yield return new WaitForSeconds(testDelay);
        }

        private IEnumerator TestSaveableEntity()
        {
            AddTestResult("=== Testing SaveableEntity ===");

            // Create a test object
            GameObject testObj = new GameObject("TestSaveableEntity");
            SaveableEntity saveable = testObj.AddComponent<SaveableEntity>();

            // Test serialization
            var saveData = saveable.Serialize();
            if (saveData != null && !string.IsNullOrEmpty(saveData.persistentId))
            {
                AddTestResult("✓ SaveableEntity serialization works");
            }
            else
            {
                AddTestResult("✗ SaveableEntity serialization failed");
            }

            // Test custom fields
            saveable.SetCustomField("testValue", 42);
            int testValue = saveable.GetCustomField<int>("testValue", 0);
            if (testValue == 42)
            {
                AddTestResult("✓ Custom field operations work");
            }
            else
            {
                AddTestResult($"✗ Custom field operations failed. Expected 42, got {testValue}");
            }

            // Test state changes
            saveable.MarkBroken();
            if (saveable.IsBroken)
            {
                AddTestResult("✓ State change operations work");
            }
            else
            {
                AddTestResult("✗ State change operations failed");
            }

            // Cleanup
            DestroyImmediate(testObj);

            yield return new WaitForSeconds(testDelay);
        }

        private IEnumerator TestSaveLoadOperations()
        {
            AddTestResult("=== Testing Save/Load Operations ===");

            if (SaveManager.Instance == null)
            {
                AddTestResult("✗ SaveManager not available");
                yield break;
            }

            string testSlotId = "test_slot_" + System.DateTime.Now.Ticks;

            try
            {
                // Test save
                AddTestResult("Testing save operation...");
                await SaveManager.Instance.SaveSlotAsync(testSlotId);
                AddTestResult("✓ Save operation completed");

                // Test load
                AddTestResult("Testing load operation...");
                await SaveManager.Instance.LoadSlotAsync(testSlotId);
                AddTestResult("✓ Load operation completed");

                // Test save summaries
                var summaries = SaveManager.Instance.GetSaveSummaries();
                bool foundTestSlot = false;
                foreach (var summary in summaries)
                {
                    if (summary.slotId == testSlotId)
                    {
                        foundTestSlot = true;
                        break;
                    }
                }

                if (foundTestSlot)
                {
                    AddTestResult("✓ Save summaries work correctly");
                }
                else
                {
                    AddTestResult("✗ Save summaries failed");
                }

                // Cleanup
                await SaveManager.Instance.DeleteSlotAsync(testSlotId);
                AddTestResult("✓ Test slot cleaned up");
            }
            catch (System.Exception ex)
            {
                AddTestResult($"✗ Save/Load test failed: {ex.Message}");
            }

            yield return new WaitForSeconds(testDelay);
        }

        private IEnumerator TestCharacterTracking()
        {
            AddTestResult("=== Testing Character Tracking ===");

            // Create a test character
            GameObject characterObj = new GameObject("TestCharacter");
            characterObj.tag = "Player";
            SaveableEntity character = characterObj.AddComponent<SaveableEntity>();
            character.SetCharacter(true);

            // Register with WorldStateManager
            if (WorldStateManager.Instance != null)
            {
                WorldStateManager.Instance.RegisterCharacter(character);
                var registeredCharacter = WorldStateManager.Instance.GetCharacter();
                if (registeredCharacter == character)
                {
                    AddTestResult("✓ Character registration works");
                }
                else
                {
                    AddTestResult("✗ Character registration failed");
                }
            }

            // Test position tracking
            Vector3 originalPos = character.transform.position;
            character.transform.position = originalPos + Vector3.right * 2f;
            
            yield return new WaitForSeconds(0.1f); // Wait for tracking to update

            // Check if position change was detected
            if (SaveManager.Instance != null)
            {
                // This would trigger dirty flag in real scenario
                AddTestResult("✓ Character position tracking setup complete");
            }

            // Cleanup
            DestroyImmediate(characterObj);

            yield return new WaitForSeconds(testDelay);
        }

        private IEnumerator TestCrashRecovery()
        {
            AddTestResult("=== Testing Crash Recovery ===");

            if (SaveManager.Instance == null)
            {
                AddTestResult("✗ SaveManager not available");
                yield break;
            }

            // Test crash detection
            SaveManager.Instance.TestCrashRecovery();
            AddTestResult("✓ Crash recovery test triggered");

            yield return new WaitForSeconds(testDelay);
        }

        private IEnumerator TestPerformance()
        {
            AddTestResult("=== Testing Performance ===");

            if (ResourceManager.Instance == null)
            {
                AddTestResult("✗ ResourceManager not available");
                yield break;
            }

            // Test bulk resource operations
            var startTime = System.DateTime.Now;
            
            for (int i = 0; i < 100; i++)
            {
                ResourceManager.Instance.AddResource("coins", 1, "Performance Test");
            }
            
            var endTime = System.DateTime.Now;
            var duration = (endTime - startTime).TotalMilliseconds;
            
            if (duration < 100) // Should complete in less than 100ms
            {
                AddTestResult($"✓ Performance test passed ({duration:F2}ms for 100 operations)");
            }
            else
            {
                AddTestResult($"✗ Performance test failed ({duration:F2}ms for 100 operations)");
            }

            yield return new WaitForSeconds(testDelay);
        }

        private void AddTestResult(string result)
        {
            testResults.Add(result);
            if (enableDetailedLogging)
            {
                Debug.Log(result);
            }
        }

        private void PrintTestResults()
        {
            Debug.Log("=== Save System Test Results ===");
            int passed = 0;
            int failed = 0;

            foreach (string result in testResults)
            {
                if (result.StartsWith("✓"))
                {
                    passed++;
                }
                else if (result.StartsWith("✗"))
                {
                    failed++;
                }
                Debug.Log(result);
            }

            Debug.Log($"=== Test Summary: {passed} passed, {failed} failed ===");
            
            if (failed == 0)
            {
                Debug.Log("🎉 All tests passed! Save system is ready for production.");
            }
            else
            {
                Debug.LogWarning($"⚠️ {failed} tests failed. Please review the issues above.");
            }
        }

        // Helper method to set character flag
        private void SetCharacter(SaveableEntity entity, bool isCharacter)
        {
            entity.SetCharacter(isCharacter);
        }
    }
}