#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

public class SpriteImportSettings : AssetPostprocessor
{
	void OnPreprocessTexture()
	{
		if (assetPath.Contains("Assets/Chess/Resources/CBurnett") || assetPath.Contains("Assets/Chess/Resources/Board"))
		{
			var importer = (TextureImporter)assetImporter;
			importer.textureType = TextureImporterType.Sprite;
			importer.spriteImportMode = SpriteImportMode.Single;
			importer.mipmapEnabled = false;
			importer.alphaIsTransparency = true;
			importer.filterMode = FilterMode.Bilinear;
			importer.wrapMode = TextureWrapMode.Clamp;
		}
	}
}
#endif