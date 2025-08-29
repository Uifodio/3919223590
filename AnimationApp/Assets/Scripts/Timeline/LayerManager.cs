using UnityEngine;
using System.Collections.Generic;

namespace AnimationApp.Timeline
{
    public class LayerManager : MonoBehaviour
    {
        [Header("Layer Settings")]
        public List<LayerData> layers = new List<LayerData>();
        public int selectedLayerIndex = 0;
        
        public System.Action<LayerData> OnLayerAdded;
        public System.Action<LayerData> OnLayerRemoved;
        public System.Action<LayerData> OnLayerVisibilityChanged;
        public System.Action<LayerData> OnLayerSelected;
        
        public void Initialize()
        {
            // Create default layer
            AddLayer("Background", LayerType.Bitmap);
        }
        
        public LayerData AddLayer(string name, LayerType type)
        {
            LayerData newLayer = new LayerData
            {
                id = System.Guid.NewGuid().ToString(),
                name = name,
                type = type,
                visible = true,
                locked = false,
                opacity = 1f,
                blendingMode = BlendingMode.Normal,
                order = layers.Count
            };
            
            layers.Add(newLayer);
            OnLayerAdded?.Invoke(newLayer);
            
            return newLayer;
        }
        
        public void RemoveLayer(int index)
        {
            if (index >= 0 && index < layers.Count)
            {
                LayerData layer = layers[index];
                layers.RemoveAt(index);
                
                // Update order of remaining layers
                for (int i = index; i < layers.Count; i++)
                {
                    layers[i].order = i;
                }
                
                OnLayerRemoved?.Invoke(layer);
                
                // Adjust selected layer index
                if (selectedLayerIndex >= layers.Count)
                {
                    selectedLayerIndex = layers.Count - 1;
                }
            }
        }
        
        public void MoveLayer(int fromIndex, int toIndex)
        {
            if (fromIndex >= 0 && fromIndex < layers.Count && 
                toIndex >= 0 && toIndex < layers.Count)
            {
                LayerData layer = layers[fromIndex];
                layers.RemoveAt(fromIndex);
                layers.Insert(toIndex, layer);
                
                // Update order
                for (int i = 0; i < layers.Count; i++)
                {
                    layers[i].order = i;
                }
            }
        }
        
        public void SetLayerVisibility(int index, bool visible)
        {
            if (index >= 0 && index < layers.Count)
            {
                layers[index].visible = visible;
                OnLayerVisibilityChanged?.Invoke(layers[index]);
            }
        }
        
        public void SetLayerLocked(int index, bool locked)
        {
            if (index >= 0 && index < layers.Count)
            {
                layers[index].locked = locked;
            }
        }
        
        public void SetLayerOpacity(int index, float opacity)
        {
            if (index >= 0 && index < layers.Count)
            {
                layers[index].opacity = Mathf.Clamp01(opacity);
            }
        }
        
        public void SetLayerBlendingMode(int index, BlendingMode mode)
        {
            if (index >= 0 && index < layers.Count)
            {
                layers[index].blendingMode = mode;
            }
        }
        
        public void SelectLayer(int index)
        {
            if (index >= 0 && index < layers.Count)
            {
                selectedLayerIndex = index;
                OnLayerSelected?.Invoke(layers[index]);
            }
        }
        
        public LayerData GetSelectedLayer()
        {
            if (selectedLayerIndex >= 0 && selectedLayerIndex < layers.Count)
            {
                return layers[selectedLayerIndex];
            }
            return null;
        }
        
        public LayerData GetLayer(int index)
        {
            if (index >= 0 && index < layers.Count)
            {
                return layers[index];
            }
            return null;
        }
        
        public LayerData GetLayerById(string id)
        {
            return layers.Find(layer => layer.id == id);
        }
        
        public LayerData[] GetVisibleLayers()
        {
            return layers.FindAll(layer => layer.visible).ToArray();
        }
        
        public LayerData[] GetUnlockedLayers()
        {
            return layers.FindAll(layer => !layer.locked).ToArray();
        }
        
        public LayerData GetTimelineData()
        {
            return new LayerData
            {
                layers = layers.ToArray(),
                selectedLayerIndex = selectedLayerIndex
            };
        }
        
        public void LoadLayerData(LayerData data)
        {
            layers.Clear();
            layers.AddRange(data.layers);
            selectedLayerIndex = data.selectedLayerIndex;
        }
    }
    
    [System.Serializable]
    public class LayerData
    {
        public string id;
        public string name;
        public LayerType type;
        public bool visible = true;
        public bool locked = false;
        public float opacity = 1f;
        public BlendingMode blendingMode = BlendingMode.Normal;
        public int order = 0;
        
        // For serialization
        public LayerData[] layers;
        public int selectedLayerIndex;
    }
    
    public enum LayerType
    {
        Bitmap,
        Vector
    }
    
    public enum BlendingMode
    {
        Normal,
        Multiply,
        Screen,
        Overlay,
        SoftLight,
        HardLight,
        ColorDodge,
        ColorBurn,
        Darken,
        Lighten,
        Difference,
        Exclusion,
        Hue,
        Saturation,
        Color,
        Luminosity
    }
}
