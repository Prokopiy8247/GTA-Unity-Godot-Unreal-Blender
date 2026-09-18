using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
namespace Meridian.Editor {
public static class ProjectBuilder {
 const string Root="Assets/GTA/Generated";static Dictionary<string,Material> mats=new();
 [MenuItem("Meridian/Generate complete game")]
 public static void Generate(){
  Directory.CreateDirectory(".astra-run");
  Directory.CreateDirectory(Root+"/Materials");Directory.CreateDirectory(Root+"/Textures");Directory.CreateDirectory(Root+"/Meshes");Directory.CreateDirectory("Assets/GTA/Prefabs");Directory.CreateDirectory("Assets/GTA/Scenes");
  AssetDatabase.Refresh();mats.Clear();
  var pipeline=AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/Settings/PC_RPAsset.asset");GraphicsSettings.defaultRenderPipeline=pipeline;QualitySettings.renderPipeline=pipeline;
  pipeline.shadowDistance=135;pipeline.msaaSampleCount=2;pipeline.renderScale=1;pipeline.supportsCameraDepthTexture=true;pipeline.supportsCameraOpaqueTexture=true;EditorUtility.SetDirty(pipeline);
  PlayerSettings.companyName="Meridian Studio";PlayerSettings.productName="Meridian Coast";PlayerSettings.defaultScreenWidth=1600;PlayerSettings.defaultScreenHeight=900;PlayerSettings.fullScreenMode=FullScreenMode.FullScreenWindow;PlayerSettings.resizableWindow=true;PlayerSettings.allowFullscreenSwitch=true;PlayerSettings.runInBackground=true;PlayerSettings.colorSpace=ColorSpace.Linear;
  var settings=new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset")[0]);var input=settings.FindProperty("activeInputHandler");if(input!=null)input.intValue=1;settings.ApplyModifiedPropertiesWithoutUndo();
  var files=Directory.GetFiles(Root+"/Models","*.fbx").OrderBy(x=>x).ToArray();var names=new List<string>();var prefabs=new List<GameObject>();var audit=new List<string>();
  foreach(var file in files){
   string path=file.Replace('\\','/');var importer=(ModelImporter)AssetImporter.GetAtPath(path);importer.isReadable=true;importer.importAnimation=false;importer.importCameras=false;importer.importLights=false;importer.materialImportMode=ModelImporterMaterialImportMode.ImportStandard;importer.SaveAndReimport();
   var source=AssetDatabase.LoadAssetAtPath<GameObject>(path);var instance=UnityEngine.Object.Instantiate(source);instance.transform.position=Vector3.zero;string name=Path.GetFileNameWithoutExtension(path);var root=new GameObject(name);
   Quaternion orient=Quaternion.identity;
   var front=instance.GetComponentsInChildren<Transform>().FirstOrDefault(t=>t.name.StartsWith("Wheel_LF"));
   var rear=instance.GetComponentsInChildren<Transform>().FirstOrDefault(t=>t.name.StartsWith("Wheel_LR"));
   if(front&&rear&&front.position.z<rear.position.z)orient=Quaternion.Euler(0,180,0);
   else if(!front)orient=Quaternion.Euler(0,180,0);
   var renderers=new List<Renderer>();
   foreach(var mf in instance.GetComponentsInChildren<MeshFilter>()){
    var mr=mf.GetComponent<MeshRenderer>();if(!mr||!mf.sharedMesh)continue;
    var original=mf.sharedMesh;var mesh=UnityEngine.Object.Instantiate(original);mesh.name=name+"_"+mf.name;
    Vector3 pivot=orient*mf.transform.position;var matrix=mf.transform.localToWorldMatrix;var verts=original.vertices;var norms=original.normals;
    for(int i=0;i<verts.Length;i++)verts[i]=orient*matrix.MultiplyPoint3x4(verts[i])-pivot;
    if(norms.Length==verts.Length)for(int i=0;i<norms.Length;i++)norms[i]=(orient*matrix.MultiplyVector(norms[i])).normalized;
    mesh.vertices=verts;if(norms.Length==verts.Length)mesh.normals=norms;else mesh.RecalculateNormals();mesh.RecalculateBounds();mesh.RecalculateTangents();
    string mp=Root+"/Meshes/"+name+"_"+mf.name.Replace('/','_')+".asset";if(AssetDatabase.LoadAssetAtPath<Mesh>(mp))AssetDatabase.DeleteAsset(mp);AssetDatabase.CreateAsset(mesh,mp);
    var child=new GameObject(mf.name);child.transform.SetParent(root.transform);child.transform.localPosition=pivot;child.AddComponent<MeshFilter>().sharedMesh=mesh;var rend=child.AddComponent<MeshRenderer>();
    rend.sharedMaterials=mr.sharedMaterials.Select(m=>MaterialFor(m?m.name:"Concrete",m)).ToArray();renderers.Add(rend);
   }
   var bounds=new Bounds(Vector3.zero,Vector3.zero);foreach(var r in renderers)bounds.Encapsulate(r.bounds);
   // Generic Blender +Y exports toward Unity -Z; named wheel pivots validate vehicle heading.
   var lowPath=Root+"/LODs/"+name+".fbx";var low=File.Exists(lowPath)?LowerDetail(lowPath,name,root.transform):null;var lod=root.AddComponent<LODGroup>();lod.SetLODs(low!=null?new[]{new LOD(.17f,renderers.ToArray()),new LOD(.008f,low)}:new[]{new LOD(.012f,renderers.ToArray())});lod.RecalculateBounds();
   string pp="Assets/GTA/Prefabs/"+name+".prefab";var prefab=PrefabUtility.SaveAsPrefabAsset(root,pp);names.Add(name);prefabs.Add(prefab);audit.Add(name+" | source rotation "+instance.transform.eulerAngles.ToString("F1")+" | size "+bounds.size.ToString("F3")+" | vertices "+renderers.Sum(r=>r.GetComponent<MeshFilter>().sharedMesh.vertexCount));
   UnityEngine.Object.DestroyImmediate(instance);UnityEngine.Object.DestroyImmediate(root);
  }
  var catalog=AssetDatabase.LoadAssetAtPath<GameCatalog>(Root+"/GameCatalog.asset");if(!catalog){catalog=ScriptableObject.CreateInstance<GameCatalog>();AssetDatabase.CreateAsset(catalog,Root+"/GameCatalog.asset");}
  catalog.names=names.ToArray();catalog.models=prefabs.ToArray();catalog.asphalt=SurfaceMaterial("Asphalt",new Color(.12f,.135f,.14f),.2f,1);catalog.concrete=SurfaceMaterial("Pavement",new Color(.49f,.48f,.45f),.15f,2);catalog.grass=SurfaceMaterial("Grassland",new Color(.20f,.245f,.135f),.05f,3);catalog.sand=SurfaceMaterial("Beach",new Color(.66f,.58f,.43f),.08f,4);catalog.marking=SurfaceMaterial("RoadPaint",new Color(.86f,.85f,.74f),.18f,0);
  catalog.water=SurfaceMaterial("CoastalWater",new Color(.035f,.23f,.28f),.88f,5);catalog.water.shader=Shader.Find("Meridian/CoastWater");catalog.water.color=new Color(.025f,.18f,.23f);
  var particle=AssetDatabase.LoadAssetAtPath<Material>(Root+"/Materials/Particles.mat");if(!particle){particle=new Material(Shader.Find("Universal Render Pipeline/Particles/Unlit"));AssetDatabase.CreateAsset(particle,Root+"/Materials/Particles.mat");}
  particle.SetFloat("_Surface",1);particle.SetFloat("_Blend",0);particle.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);particle.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha);particle.SetFloat("_ZWrite",0);particle.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");particle.renderQueue=3000;catalog.particle=particle;EditorUtility.SetDirty(catalog);
  var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);var bootstrap=new GameObject("Meridian Coast / Free Roam");bootstrap.AddComponent<Game>().catalog=catalog;
  EditorSceneManager.SaveScene(scene,"Assets/GTA/Scenes/Meridian_FreeRoam.unity");EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene("Assets/GTA/Scenes/Meridian_FreeRoam.unity",true)};
  AssetDatabase.SaveAssets();File.WriteAllLines(".astra-run/asset-import-audit.txt",audit);Debug.Log("MERIDIAN_GENERATE_SUCCESS: "+names.Count+" Blender models; launch scene ready.");
 }
 static Renderer[] LowerDetail(string path,string name,Transform parent){
  var importer=(ModelImporter)AssetImporter.GetAtPath(path);if(importer==null)return null;importer.isReadable=true;importer.importAnimation=false;importer.SaveAndReimport();
  var source=UnityEngine.Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(path));source.transform.position=Vector3.zero;var outList=new List<Renderer>();var orient=Quaternion.Euler(0,180,0);
  foreach(var mf in source.GetComponentsInChildren<MeshFilter>()){
   var original=mf.sharedMesh;var mesh=UnityEngine.Object.Instantiate(original);var matrix=mf.transform.localToWorldMatrix;var pivot=orient*mf.transform.position;var vertices=mesh.vertices;var normals=mesh.normals;
   for(int i=0;i<vertices.Length;i++)vertices[i]=orient*matrix.MultiplyPoint3x4(vertices[i])-pivot;
   if(normals.Length==vertices.Length)for(int i=0;i<normals.Length;i++)normals[i]=(orient*matrix.MultiplyVector(normals[i])).normalized;
   mesh.vertices=vertices;mesh.normals=normals;mesh.RecalculateBounds();mesh.RecalculateTangents();
   var p=Root+"/Meshes/"+name+"_LOW_"+mf.name+".asset";if(AssetDatabase.LoadAssetAtPath<Mesh>(p))AssetDatabase.DeleteAsset(p);AssetDatabase.CreateAsset(mesh,p);
   var child=new GameObject("LOD1 "+mf.name);child.transform.SetParent(parent);child.transform.localPosition=pivot;child.AddComponent<MeshFilter>().sharedMesh=mesh;var r=child.AddComponent<MeshRenderer>();r.sharedMaterials=mf.GetComponent<MeshRenderer>().sharedMaterials.Select(m=>MaterialFor(m.name,m)).ToArray();outList.Add(r);
  }
  UnityEngine.Object.DestroyImmediate(source);return outList.ToArray();
 }
 static Material MaterialFor(string name,Material imported){
  name=name.Split('.')[0];if(mats.TryGetValue(name,out var result))return result;
  Color c=imported&&imported.HasProperty("_Color")?imported.color:Color.gray;
  var colors=new Dictionary<string,Color>{
   {"Paint",new(.055f,.17f,.22f)},{"Pearl",new(.65f,.7f,.72f)},{"RedPaint",new(.36f,.025f,.02f)},{"Rubber",new(.015f,.019f,.022f)},{"Chrome",new(.55f,.61f,.66f)},{"Metal",new(.15f,.19f,.22f)},{"Glass",new(.035f,.105f,.14f)},{"Interior",new(.028f,.034f,.041f)},{"Lamp",new(.84f,.89f,.82f)},{"Tail",new(.5f,.012f,.007f)},{"BlueLight",new(.01f,.14f,.9f)},{"Concrete",new(.47f,.46f,.42f)},{"Brick",new(.32f,.16f,.105f)},{"Plaster",new(.69f,.65f,.56f)},{"Facade",new(.23f,.27f,.29f)},{"Window",new(.11f,.22f,.28f)},{"WarmWindow",new(.62f,.47f,.24f)},{"Wood",new(.23f,.14f,.075f)},{"Foliage",new(.075f,.18f,.075f)},{"Trunk",new(.18f,.12f,.07f)},{"SkinLight",new(.69f,.46f,.32f)},{"SkinDark",new(.27f,.135f,.082f)},{"Jacket",new(.085f,.11f,.14f)},{"Denim",new(.09f,.14f,.19f)},{"Hair",new(.035f,.024f,.018f)},{"PoliceCloth",new(.025f,.045f,.095f)},{"Gunmetal",new(.07f,.085f,.093f)},{"Grip",new(.025f,.028f,.027f)}};
  if(colors.TryGetValue(name,out var color))c=color;
  float smooth=name.Contains("Glass")||name.Contains("Window")? 0.83f:name.Contains("Paint")||name=="Pearl"? 0.72f:name=="Chrome"? 0.85f:.25f;
  int texture=name=="Brick"?6:name=="Concrete"||name=="Plaster"?2:name=="Wood"||name=="Trunk"?7:name=="Jacket"||name=="Denim"||name=="PoliceCloth"?8:0;
  result=SurfaceMaterial(name,c,smooth,texture);
  if(name.Contains("Paint")||name=="Pearl"||name=="Metal"||name=="Chrome"||name=="Gunmetal"||name=="Window"||name=="Glass")result.SetFloat("_Metallic",name=="Chrome"? 0.88f:.52f);
  if(name=="Lamp"||name=="Tail"||name=="BlueLight"||name=="WarmWindow"){result.EnableKeyword("_EMISSION");result.SetColor("_EmissionColor",c*(name=="WarmWindow"? 0.4f:2));}
  if(name=="Foliage")result.SetFloat("_Cull",0);
  mats[name]=result;return result;
 }
 static Material SurfaceMaterial(string name,Color color,float smooth,int kind){
  string path=Root+"/Materials/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(m,path);}m.color=color;m.SetFloat("_Smoothness",smooth);m.enableInstancing=true;
  if(kind>0){
   const int n=128;var tex=new Texture2D(n,n,TextureFormat.RGBA32,true);var rng=new System.Random(285+kind);var pixels=new Color[n*n];
   for(int y=0;y<n;y++)for(int x=0;x<n;x++){float noise=(float)rng.NextDouble();float f=.82f+noise*.32f;if(kind==2&&((x%64<2)||(y%64<2)))f=.58f;if(kind==6&&((y%24<2)||((x+(y/24%2)*32)%64<2)))f=.42f;if(kind==7)f=.75f+.25f*Mathf.PerlinNoise(x*.6f,y*.04f);if(kind==8)f=.84f+((x+y)%2)*.2f;if(kind==5)f=.8f+.2f*Mathf.PerlinNoise(x*.08f,y*.13f);pixels[y*n+x]=new Color(f,f,f,1);}
   tex.SetPixels(pixels);tex.Apply();string tp=Root+"/Textures/"+name+".png";File.WriteAllBytes(tp,tex.EncodeToPNG());UnityEngine.Object.DestroyImmediate(tex);AssetDatabase.ImportAsset(tp);var ti=(TextureImporter)AssetImporter.GetAtPath(tp);ti.wrapMode=TextureWrapMode.Repeat;ti.maxTextureSize=128;ti.SaveAndReimport();m.mainTexture=AssetDatabase.LoadAssetAtPath<Texture2D>(tp);
   var normal=new Texture2D(n,n,TextureFormat.RGBA32,true,true);for(int y=0;y<n;y++)for(int x=0;x<n;x++){float dx=pixels[y*n+(x+1)%n].r-pixels[y*n+x].r,dy=pixels[((y+1)%n)*n+x].r-pixels[y*n+x].r;var v=new Vector3(-dx*.5f,-dy*.5f,1).normalized;normal.SetPixel(x,y,new Color(v.x*.5f+.5f,v.y*.5f+.5f,v.z*.5f+.5f,1));}normal.Apply();string np=Root+"/Textures/"+name+"_normal.png";File.WriteAllBytes(np,normal.EncodeToPNG());UnityEngine.Object.DestroyImmediate(normal);AssetDatabase.ImportAsset(np);var ni=(TextureImporter)AssetImporter.GetAtPath(np);ni.textureType=TextureImporterType.NormalMap;ni.SaveAndReimport();m.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(np));m.SetFloat("_BumpScale",.4f);m.EnableKeyword("_NORMALMAP");
  }
  EditorUtility.SetDirty(m);return m;
 }
 [MenuItem("Meridian/Build Windows player")]
 public static void BuildPlayer(){
  Directory.CreateDirectory("Builds/Windows");var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{"Assets/GTA/Scenes/Meridian_FreeRoam.unity"},locationPathName="Builds/Windows/MeridianCoast.exe",target=BuildTarget.StandaloneWindows64,options=BuildOptions.None});
  File.WriteAllText(".astra-run/build-result.txt",report.summary.result+"\nErrors: "+report.summary.totalErrors+"\nWarnings: "+report.summary.totalWarnings+"\nBytes: "+report.summary.totalSize+"\nDuration: "+report.summary.totalTime);
  if(report.summary.result!=BuildResult.Succeeded)throw new Exception("Build failed: "+report.summary.result);Debug.Log("MERIDIAN_BUILD_SUCCESS");
 }
 public static void BuildAll(){Generate();BuildPlayer();}
}
}
