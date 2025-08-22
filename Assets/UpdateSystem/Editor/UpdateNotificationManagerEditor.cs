#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

[CustomEditor(typeof(UpdateNotificationManager))]
public class UpdateNotificationManagerEditor : Editor
{
	public override void OnInspectorGUI()
	{
		DrawDefaultInspector();

		var mgr = (UpdateNotificationManager)target;
		EditorGUILayout.Space(8);
		EditorGUILayout.LabelField("Inspector Helpers", EditorStyles.boldLabel);

		EditorGUILayout.BeginHorizontal();
		if (GUILayout.Button("Normalize GitHub URL to RAW"))
		{
			Undo.RecordObject(mgr, "Normalize GitHub URL");
			string before = mgr.GetType().GetField("updateJsonUrl", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).GetValue(mgr) as string;
			string after = UpdateNotificationManager.NormalizeGitHubRawUrl(before);
			mgr.GetType().GetField("updateJsonUrl", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(mgr, after);
			EditorUtility.SetDirty(mgr);
		}
		if (GUILayout.Button("Force Check Now"))
		{
			mgr.ForceCheckNow();
		}
		EditorGUILayout.EndHorizontal();

		EditorGUILayout.HelpBox("If you pasted a GitHub 'blob' link, click Normalize to convert to the RAW content URL.", MessageType.Info);
	}
}
#endif