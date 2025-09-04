using System.IO;
using UnityEditor;
using UnityEngine;

namespace ResourceSystem.Editor
{
    public static class InstallerAndDebugger
    {
        private const string MenuRoot = "Tools/Resource System";

        [MenuItem(MenuRoot + "/Install Complete System", priority = 0)]
        public static void InstallCompleteSystem()
        {
            EnsureResourceManagerInScene();
            CreateDemoSceneIfMissing();
            EditorUtility.DisplayDialog("Resource System", "Installation complete. A ResourceManager was added and a demo setup is available.", "OK");
        }

        [MenuItem(MenuRoot + "/Uninstall (Remove Manager from Scene)", priority = 1)]
        public static void UninstallFromScene()
        {
            var mgr = Object.FindObjectOfType<ResourceManager>();
            if (mgr != null)
            {
                Object.DestroyImmediate(mgr.gameObject);
            }
            EditorUtility.DisplayDialog("Resource System", "Removed ResourceManager from the scene.", "OK");
        }

        [MenuItem(MenuRoot + "/Open Persistent Data Folder", priority = 50)]
        public static void OpenPersistentDataFolder()
        {
            EditorUtility.RevealInFinder(Application.persistentDataPath);
        }

        [MenuItem(MenuRoot + "/Delete Save File", priority = 51)]
        public static void DeleteSaveFile()
        {
            var tempObj = new GameObject("_temp_rm");
            var rm = tempObj.AddComponent<ResourceManager>();
            rm.DeleteSaveFromDisk();
            Object.DestroyImmediate(tempObj);
            EditorUtility.DisplayDialog("Resource System", "Save file deleted.", "OK");
        }

        [MenuItem(MenuRoot + "/Force Save Now", priority = 52)]
        public static void ForceSaveNow()
        {
            var mgr = Object.FindObjectOfType<ResourceManager>();
            if (mgr == null)
            {
                EnsureResourceManagerInScene();
                mgr = Object.FindObjectOfType<ResourceManager>();
            }
            mgr.SaveToDisk();
            EditorUtility.DisplayDialog("Resource System", "Forced save completed.", "OK");
        }

        private static void EnsureResourceManagerInScene()
        {
            if (Object.FindObjectOfType<ResourceManager>() == null)
            {
                var go = new GameObject("ResourceManager");
                go.AddComponent<ResourceManager>();
            }
        }

        private static void CreateDemoSceneIfMissing()
        {
            // Create a simple demo environment in the current scene: character + a few rewards
            var mgr = Object.FindObjectOfType<ResourceManager>();
            if (mgr == null) return;

            var character = GameObject.Find("DemoCharacter");
            if (character == null)
            {
                character = GameObject.CreatePrimitive(PrimitiveType.Capsule);
                character.name = "DemoCharacter";
                character.transform.position = Vector3.zero;
                var rb = character.AddComponent<Rigidbody>();
                rb.useGravity = true;
                rb.constraints = RigidbodyConstraints.FreezeRotation;
                var id = character.AddComponent<CharacterIdentifier>();
                id.characterId = "MainCharacter";
                id.rewardLayer = LayerMask.GetMask("Default");
            }

            for (int i = 0; i < 5; i++)
            {
                var money = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                money.name = $"Reward_Money_{i}";
                money.transform.position = new Vector3(Random.Range(-5f, 5f), 1.5f, Random.Range(-5f, 5f));
                money.AddComponent<Rigidbody>();
                var r = money.AddComponent<RewardIdentifier>();
                r.rewards.Add(new RewardEntry{ resourceId = "money", amount = Random.Range(1, 5) });
            }

            for (int i = 0; i < 3; i++)
            {
                var wood = GameObject.CreatePrimitive(PrimitiveType.Cube);
                wood.name = $"Reward_Wood_{i}";
                wood.transform.position = new Vector3(Random.Range(-6f, 6f), 1.5f, Random.Range(-6f, 6f));
                wood.AddComponent<Rigidbody>();
                var r = wood.AddComponent<RewardIdentifier>();
                r.rewards.Add(new RewardEntry{ resourceId = "wood", amount = Random.Range(2, 8) });
            }
        }
    }
}

