using UnityEngine;

// Compatibility adapter so external assets searching for a class named "Joystick"
// can reference this component. It forwards all properties to FloatingJoystick.
// If the project already has a Joystick class, the editor menu will attempt to add it instead.
namespace UltimateFloatingJoystick
{
    [AddComponentMenu("UI/Ultimate Floating Joystick/Joystick (Adapter)")]
    public class Joystick : MonoBehaviour, IJoystick
    {
        [SerializeField] private FloatingJoystick target;

        private void Reset()
        {
            if (target == null)
            {
                target = GetComponent<FloatingJoystick>();
                if (target == null) target = GetComponentInChildren<FloatingJoystick>();
            }
        }

        public float Horizontal => target != null ? target.Horizontal : 0f;
        public float Vertical => target != null ? target.Vertical : 0f;
        public Vector2 Direction => target != null ? target.Direction : Vector2.zero;
        public float Magnitude => target != null ? target.Magnitude : 0f;
        public float AngleDegrees => target != null ? target.AngleDegrees : 0f;
        public bool IsPressed => target != null && target.IsPressed;
    }
}

