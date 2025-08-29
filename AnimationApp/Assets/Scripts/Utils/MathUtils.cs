using UnityEngine;

namespace AnimationApp.Utils
{
    public static class MathUtils
    {
        public static Vector2 ClampToCanvas(Vector2 position, Rect canvasRect)
        {
            return new Vector2(
                Mathf.Clamp(position.x, canvasRect.xMin, canvasRect.xMax),
                Mathf.Clamp(position.y, canvasRect.yMin, canvasRect.yMax)
            );
        }
        
        public static float DistanceToLine(Vector2 point, Vector2 lineStart, Vector2 lineEnd)
        {
            Vector2 line = lineEnd - lineStart;
            Vector2 pointToStart = point - lineStart;
            
            float lineLength = line.magnitude;
            if (lineLength == 0)
                return pointToStart.magnitude;
            
            float t = Vector2.Dot(pointToStart, line) / (lineLength * lineLength);
            t = Mathf.Clamp01(t);
            
            Vector2 projection = lineStart + t * line;
            return Vector2.Distance(point, projection);
        }
        
        public static bool PointInRect(Vector2 point, Rect rect)
        {
            return point.x >= rect.xMin && point.x <= rect.xMax &&
                   point.y >= rect.yMin && point.y <= rect.yMax;
        }
        
        public static Rect GetBoundingRect(Vector2[] points)
        {
            if (points.Length == 0)
                return Rect.zero;
            
            float minX = points[0].x;
            float maxX = points[0].x;
            float minY = points[0].y;
            float maxY = points[0].y;
            
            for (int i = 1; i < points.Length; i++)
            {
                minX = Mathf.Min(minX, points[i].x);
                maxX = Mathf.Max(maxX, points[i].x);
                minY = Mathf.Min(minY, points[i].y);
                maxY = Mathf.Max(maxY, points[i].y);
            }
            
            return new Rect(minX, minY, maxX - minX, maxY - minY);
        }
        
        public static float SmoothStep(float edge0, float edge1, float x)
        {
            x = Mathf.Clamp01((x - edge0) / (edge1 - edge0));
            return x * x * (3 - 2 * x);
        }
        
        public static Vector2 RotatePoint(Vector2 point, Vector2 center, float angle)
        {
            float cos = Mathf.Cos(angle * Mathf.Deg2Rad);
            float sin = Mathf.Sin(angle * Mathf.Deg2Rad);
            
            Vector2 rotated = point - center;
            Vector2 result = new Vector2(
                rotated.x * cos - rotated.y * sin,
                rotated.x * sin + rotated.y * cos
            );
            
            return result + center;
        }
        
        public static float GetAngle(Vector2 from, Vector2 to)
        {
            Vector2 direction = to - from;
            return Mathf.Atan2(direction.y, direction.x) * Mathf.Rad2Deg;
        }
        
        public static float LerpAngle(float a, float b, float t)
        {
            float delta = Mathf.Repeat(b - a, 360);
            if (delta > 180)
                delta -= 360;
            return a + delta * t;
        }
    }
}
