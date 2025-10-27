using UnityEngine;
using UnityEngine.UI;

namespace AnimationApp.UI.Panels
{
    public class MainMenuBar : MonoBehaviour
    {
        [Header("Menu Items")]
        public Button fileMenuButton;
        public Button editMenuButton;
        public Button viewMenuButton;
        public Button layerMenuButton;
        public Button timelineMenuButton;
        public Button windowMenuButton;
        public Button helpMenuButton;
        
        [Header("Dropdown Menus")]
        public GameObject fileDropdown;
        public GameObject editDropdown;
        public GameObject viewDropdown;
        public GameObject layerDropdown;
        public GameObject timelineDropdown;
        public GameObject windowDropdown;
        public GameObject helpDropdown;
        
        public void Initialize()
        {
            SetupMenuButtons();
            SetupDropdownMenus();
        }
        
        private void SetupMenuButtons()
        {
            if (fileMenuButton != null)
                fileMenuButton.onClick.AddListener(() => ToggleDropdown(fileDropdown));
            
            if (editMenuButton != null)
                editMenuButton.onClick.AddListener(() => ToggleDropdown(editDropdown));
            
            if (viewMenuButton != null)
                viewMenuButton.onClick.AddListener(() => ToggleDropdown(viewDropdown));
            
            if (layerMenuButton != null)
                layerMenuButton.onClick.AddListener(() => ToggleDropdown(layerDropdown));
            
            if (timelineMenuButton != null)
                timelineMenuButton.onClick.AddListener(() => ToggleDropdown(timelineDropdown));
            
            if (windowMenuButton != null)
                windowMenuButton.onClick.AddListener(() => ToggleDropdown(windowDropdown));
            
            if (helpMenuButton != null)
                helpMenuButton.onClick.AddListener(() => ToggleDropdown(helpDropdown));
        }
        
        private void SetupDropdownMenus()
        {
            // Set up file menu items
            SetupFileMenu();
            
            // Set up edit menu items
            SetupEditMenu();
            
            // Set up view menu items
            SetupViewMenu();
            
            // Set up layer menu items
            SetupLayerMenu();
            
            // Set up timeline menu items
            SetupTimelineMenu();
            
            // Set up window menu items
            SetupWindowMenu();
            
            // Set up help menu items
            SetupHelpMenu();
        }
        
        private void SetupFileMenu()
        {
            // New Project, Open, Save, Save As, Export, Import Audio, Exit
        }
        
        private void SetupEditMenu()
        {
            // Undo, Redo, Cut, Copy, Paste, Select All, Clear
        }
        
        private void SetupViewMenu()
        {
            // Zoom In, Zoom Out, Fit to Screen, Show Grid, Show Rulers, Onion Skin
        }
        
        private void SetupLayerMenu()
        {
            // New Layer, Delete Layer, Duplicate Layer, Merge Layers
        }
        
        private void SetupTimelineMenu()
        {
            // Insert Frame, Delete Frame, Duplicate Frame, Extend Exposure
        }
        
        private void SetupWindowMenu()
        {
            // Brush Settings, Export, Preferences, Timeline, Properties
        }
        
        private void SetupHelpMenu()
        {
            // About, Help, Keyboard Shortcuts
        }
        
        private void ToggleDropdown(GameObject dropdown)
        {
            if (dropdown != null)
            {
                dropdown.SetActive(!dropdown.activeSelf);
            }
        }
        
        public void HideAllDropdowns()
        {
            if (fileDropdown != null) fileDropdown.SetActive(false);
            if (editDropdown != null) editDropdown.SetActive(false);
            if (viewDropdown != null) viewDropdown.SetActive(false);
            if (layerDropdown != null) layerDropdown.SetActive(false);
            if (timelineDropdown != null) timelineDropdown.SetActive(false);
            if (windowDropdown != null) windowDropdown.SetActive(false);
            if (helpDropdown != null) helpDropdown.SetActive(false);
        }
    }
}
