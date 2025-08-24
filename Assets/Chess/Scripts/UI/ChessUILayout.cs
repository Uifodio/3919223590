using UnityEngine;

namespace Chess.UI
{
	public class ChessUILayout : MonoBehaviour
	{
		public RectTransform boardRoot;
		public RectTransform sidebarRoot;
		public RectTransform turnLabelRoot;
		public RectTransform statusLabelRoot;
		public RectTransform undoButtonRoot;
		public RectTransform newGameButtonRoot;
		public RectTransform depthDropdownRoot;
		public RectTransform drawButtonRoot;
		public RectTransform economyLabelRoot;

		private void Awake()
		{
			AutoAssignIfNull(ref boardRoot, "BoardRoot");
			AutoAssignIfNull(ref sidebarRoot, "SidebarRoot");
			AutoAssignIfNull(ref turnLabelRoot, "TurnLabelRoot");
			AutoAssignIfNull(ref statusLabelRoot, "StatusLabelRoot");
			AutoAssignIfNull(ref undoButtonRoot, "UndoButtonRoot");
			AutoAssignIfNull(ref newGameButtonRoot, "NewGameButtonRoot");
			AutoAssignIfNull(ref depthDropdownRoot, "DepthDropdownRoot");
			AutoAssignIfNull(ref drawButtonRoot, "DrawButtonRoot");
			AutoAssignIfNull(ref economyLabelRoot, "EconomyLabelRoot");
		}

		private void AutoAssignIfNull(ref RectTransform field, string childName)
		{
			if (field != null) return;
			var t = transform.Find(childName) as RectTransform;
			if (t != null) field = t;
		}
	}
}