using UnityEngine;

namespace UltimateFloatingJoystick
{
    public interface IJoystick
    {
        float Horizontal { get; }
        float Vertical { get; }
        Vector2 Direction { get; }
        float Magnitude { get; }
        float AngleDegrees { get; }
        bool IsPressed { get; }
    }
}

