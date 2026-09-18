using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
namespace Meridian {
public class World:MonoBehaviour {
 public const float Block=128; public readonly List<GameObject> sectors=new(); public readonly List<Vector3> sectorCenters=new();public readonly List<ServicePoint> services=new();public readonly List<Light> lamps=new();
 public int activeSectors; float next;
 public static float Height(float x,float z) {
  float coast=Mathf.SmoothStep(0,1,Mathf.InverseLerp(1050,1210,x));
  float mountain=Mathf.SmoothStep(0,1,Mathf.InverseLerp(1080,1660,z))*Mathf.SmoothStep(0,1,Mathf.InverseLerp(2300,1450,Mathf.Abs(x)));
  float h=mountain*(70+Mathf.PerlinNoise(x*.0018f+9,z*.0022f)*170);
  if(x>1040)h=0;
  return h-coast*16;
 }
 public void Build() {
  Random.InitState(18451);
  var terrain=new GameObject("Coast terrain");var verts=new List<Vector3>();var uv=new List<Vector2>();var colors=new List<Color>();var tris=new List<int>();const int n=200;const float span=6000;
  for(int z=0;z<=n;z++)for(int x=0;x<=n;x++){float xx=-3000+x*span/n,zz=-3000+z*span/n;verts.Add(new(xx,Height(xx,zz),zz));uv.Add(new(xx*.04f,zz*.04f));colors.Add(Color.white);}
  for(int z=0;z<n;z++)for(int x=0;x<n;x++){int a=z*(n+1)+x;tris.AddRange(new[]{a,a+n+1,a+1,a+1,a+n+1,a+n+2});}
  var me=new Mesh{name="Coastal topography",indexFormat=IndexFormat.UInt32};me.SetVertices(verts);me.SetUVs(0,uv);me.SetTriangles(tris,0);me.RecalculateNormals();terrain.AddComponent<MeshFilter>().sharedMesh=me;terrain.AddComponent<MeshRenderer>().sharedMaterial=Game.I.catalog.grass;terrain.AddComponent<MeshCollider>().sharedMesh=me;
  var sea=Surface("Ocean",new(2350,-.3f,0),new(2650,.15f,6500),Game.I.catalog.water,null,false);sea.AddComponent<WaterSurface>();
  Surface("Beach sand",new(1080,-.09f,0),new(160,.16f,3700),Game.I.catalog.sand,null);
  // A connected orthogonal lane graph, 1.8 km city and a surrounding 6 km landscape.
  for(int x=-7;x<=7;x++)for(int z=-7;z<=7;z++)BuildBlock(x,z);
  Road(new(-1150,.16f,-1900),new(-1150,.16f,980),16,"Airport connector");
  Road(new(-1850,.16f,960),new(1000,.16f,960),17,"Greenridge road");
  Road(new(985,.16f,-1700),new(985,.16f,1050),24,"Coastal expressway");
  Road(new(-1850,.16f,-970),new(990,.16f,-970),26,"Southern highway");
  Surface("Runway",new(-1370,.06f,-1330),new(65,.18f,1350),Game.I.catalog.asphalt,null);
  for(int i=0;i<35;i++)Surface("Runway centerline",new(-1370,.16f,-1970+i*38),new(1.2f,.02f,17),Game.I.catalog.marking,null,false);
  for(int end=-1;end<=1;end+=2)for(int i=-4;i<=4;i++)Surface("Threshold stripe",new(-1370+i*5,.17f,-1330+end*590),new(2,.02f,40),Game.I.catalog.marking,null,false);
  Road(new(-1370,.15f,-1250),new(-1000,.15f,-1250),25,"Taxiway");
  for(int i=0;i<4;i++)Place("Hangar",new(-1065,0,-1550+i*120),270,null,true);
  Label("MERIDIAN AIRFIELD",new(-1100,7,-1190),270,Color.white,1);
  for(int z=-700;z<=-300;z+=100){Surface("Concrete pier",new(1160,.2f,z),new(210,.7f,20),Game.I.catalog.concrete,null);Place("PortCrane",new(1100,.6f,z),0,null,true);}
  for(int i=0;i<24;i++)Place("Container",new(850+(i%4)*12,0,-790+(i/4)*18),90,null,true);
  for(int i=0;i<60;i++){float z=-800+i*29;Place("Palm",new(1035,0,z),Random.Range(0,360),null,true);}
  // Rural compounds and a traversable winding mountain road.
  for(int i=0;i<28;i++){var p=new Vector3(Random.Range(-1900,-1050),0,Random.Range(300,1200));p.y=Height(p.x,p.z);Place("House",p,Random.Range(0,4)*90,null,true);Place("Oak",p+new Vector3(20,0,12),0,null);}
  Vector3 last=new(-500,Height(-500,930)+.1f,930);
  for(int i=1;i<=85;i++){float z=930+i*17;float x=-470+Mathf.Sin(i*.08f)*280;Vector3 p=new(x,Height(x,z)+.15f,z);Road(last,p,10,"Northwatch ascent");last=p;}
  for(int i=0;i<330;i++){float x=Random.Range(-2250,850),z=Random.Range(1000,2600);var p=new Vector3(x,Height(x,z),z);Place(i%5==0?"Rock":"Oak",p,Random.Range(0,360),null,i%5==0);}
  // Original utility locations; no mission markers or objectives.
  Service("AEGIS OUTFITTERS",ServiceKind.Weapons,new(28,.2f,39),"WEAPONS / AMMUNITION");
  Service("TORQUE WORKSHOP",ServiceKind.Garage,new(-28,.2f,49),"REPAIR / TUNING / STORAGE");
  Service("MERIDIAN CLINIC",ServiceKind.Clinic,new(24,.2f,148),"HEALTH / ARMOR");
  Service("HARBOR HOUSE",ServiceKind.Home,new(-28,.2f,167),"SAVE / WARDROBE / REST");
  Service("NORTHSTAR RANGE",ServiceKind.Range,new(-920,.2f,-820),"OPTIONAL SHOOTING RANGE");
  for(int i=0;i<7;i++){var o=Place("Target",new(-936+i*4,.2f,-800),180,null,true);o.AddComponent<RangeTarget>();}
  for(int i=0;i<4;i++){Surface("Stunt ramp",new(820,.4f,-180+i*130),new(5,.6f,10),Game.I.catalog.concrete,null).transform.rotation=Quaternion.Euler(-12,0,0);}
  // A small accessible safehouse interior, assembled from surfaces and authored furniture.
  Surface("Home floor",new(-40,.1f,171),new(14,.2f,12),Game.I.catalog.concrete,null);
  Surface("Home back",new(-40,2,177),new(14,4,.25f),Game.I.catalog.concrete,null);
  Surface("Home side",new(-47,2,171),new(.25f,4,12),Game.I.catalog.concrete,null);
  Surface("Home roof",new(-40,4.1f,171),new(14,.2f,12),Game.I.catalog.concrete,null);
  Place("Bench",new(-41,.2f,173),0,null);Place("Bench",new(-38,.2f,174),90,null);
  Label("MERIDIAN COAST",new(16,5,9),180,new Color(.68f,.89f,.9f),.55f);
  Physics.SyncTransforms();
 }
 void BuildBlock(int x,int z) {
  Vector3 origin=new(x*Block,0,z*Block);var sector=new GameObject("Sector "+x+","+z);sector.transform.position=origin;sectors.Add(sector);sectorCenters.Add(origin+new Vector3(64,0,64));
  Road(origin+new Vector3(0,.12f,0),origin+new Vector3(0,.12f,128),18,"North street",sector.transform);
  Road(origin+new Vector3(0,.13f,0),origin+new Vector3(128,.13f,0),18,"East street",sector.transform);
  Surface("Sidewalk",origin+new Vector3(64,.08f,64),new(108,.18f,108),Game.I.catalog.concrete,sector.transform);
  Surface("Courtyard",origin+new Vector3(64,.18f,64),new(72,.03f,72),Game.I.catalog.grass,sector.transform,false);
  bool downtown=x>=-2&&x<=3&&z>=-2&&z<=3;bool industrial=z<-3&&x>0;
  for(int i=0;i<4;i++){
   Vector3 p=origin+new Vector3(i%2==0?30:98,.19f,i<2?30:98);
   // Keep the central street's services and player spawning spaces accessible.
   if((x==0||x==-1)&&(z==0||z==1)&&i<2)continue;
   string model=downtown?(Random.value<.35f?"OfficeTower":"OfficeMid"):industrial?"Warehouse":x<-2?"House":"Apartment";
   var b=Place(model,p,i<2?180:0,sector.transform,true);
   if(downtown){float f=Random.Range(.8f,1.22f);b.transform.localScale=new Vector3(.8f,f,.85f);}
  }
  for(int i=0;i<3;i++){
   Vector3 p=origin+new Vector3(12,.19f,24+i*40);Place("Streetlamp",p,90,sector.transform);
   if((x+z+i)%4==0) {var l=new GameObject("Street light").AddComponent<Light>();l.transform.SetParent(sector.transform);l.transform.position=p+new Vector3(1.7f,6.9f,0);l.type=LightType.Point;l.range=15;l.intensity=1.5f;l.color=new(1,.78f,.5f);l.enabled=false;lamps.Add(l);}
   Place(i==1?"Bench":"Oak",origin+new Vector3(22,.19f,28+i*35),90,sector.transform);
  }
  Place("TrafficSignal",origin+new Vector3(11,.19f,11),0,sector.transform);
  Place("Hydrant",origin+new Vector3(12,.19f,108),0,sector.transform,true);
  var bin=Place("Bin",origin+new Vector3(17,.19f,52),0,sector.transform,true);if(Mathf.Abs(x)<2&&Mathf.Abs(z)<2){var rb=bin.AddComponent<Rigidbody>();rb.mass=24;rb.interpolation=RigidbodyInterpolation.Interpolate;}
  // Crossing markings on approaches, with clear unmarked junction center.
  for(int i=0;i<6;i++){Surface("Crosswalk",origin+new Vector3(-6+i*2.4f,.15f,13),new(1.1f,.015f,3.4f),Game.I.catalog.marking,sector.transform,false);}
 }
 public static GameObject Surface(string n,Vector3 p,Vector3 s,Material m,Transform parent,bool collider=true) {
  // Civil-engineering surfaces are generated geometry, not placeholder hero objects.
  var o=new GameObject(n);o.transform.SetParent(parent);o.transform.position=p;
  Vector3 h=s*.5f;var v=new[]{new Vector3(-h.x,-h.y,-h.z),new Vector3(h.x,-h.y,-h.z),new Vector3(h.x,h.y,-h.z),new Vector3(-h.x,h.y,-h.z),new Vector3(-h.x,-h.y,h.z),new Vector3(h.x,-h.y,h.z),new Vector3(h.x,h.y,h.z),new Vector3(-h.x,h.y,h.z)};
  int[] t={0,2,1,0,3,2,1,2,6,1,6,5,5,6,7,5,7,4,4,7,3,4,3,0,3,7,6,3,6,2,4,0,1,4,1,5};
  // Duplicate face vertices for crisp edges and world-scaled texture coordinates.
  var vv=new Vector3[36];var uv=new Vector2[36];var tt=new int[36];
  for(int i=0;i<36;i++){vv[i]=v[t[i]];uv[i]=new(vv[i].x*.25f+vv[i].y*.2f,vv[i].z*.25f+vv[i].y*.2f);tt[i]=i;}
  var mesh=new Mesh{name=n};mesh.vertices=vv;mesh.uv=uv;mesh.triangles=tt;mesh.RecalculateNormals();o.AddComponent<MeshFilter>().sharedMesh=mesh;o.AddComponent<MeshRenderer>().sharedMaterial=m;
  if(collider){var c=o.AddComponent<BoxCollider>();c.size=s;}return o;
 }
 public void Road(Vector3 a,Vector3 b,float width,string name,Transform parent=null) {
  var d=b-a;var road=Surface(name,(a+b)*.5f,new(width,.13f,d.magnitude+1),Game.I.catalog.asphalt,parent);road.transform.rotation=Quaternion.LookRotation(d,Vector3.up);
  if(d.magnitude>30){int count=(int)(d.magnitude/14);for(int i=0;i<count;i++){var p=Vector3.Lerp(a,b,(i+.5f)/count)+Vector3.up*.075f;var mark=Surface("Lane divider",p,new(.14f,.012f,5),Game.I.catalog.marking,parent,false);mark.transform.rotation=road.transform.rotation;}}
 }
 public GameObject Place(string n,Vector3 p,float yaw,Transform parent,bool collision=false) {
  var o=Game.I.Model(n,parent);o.transform.SetPositionAndRotation(p,Quaternion.Euler(0,yaw,0));
  if(collision){var renderers=o.GetComponentsInChildren<Renderer>();var bounds=new Bounds(o.transform.position,Vector3.zero);foreach(var r in renderers)bounds.Encapsulate(r.bounds);var c=o.AddComponent<BoxCollider>();c.center=o.transform.InverseTransformPoint(bounds.center);Vector3 size=bounds.size;if(yaw%180!=0)size=new(size.z,size.y,size.x);c.size=size;}
  return o;
 }
 void Service(string n,ServiceKind kind,Vector3 p,string subtitle) {
  var go=new GameObject(n);go.transform.position=p;var s=go.AddComponent<ServicePoint>();s.kind=kind;s.title=n;services.Add(s);
  // Open-front service canopy, accessible directly from the sidewalk.
  Surface("Service pad",p+new Vector3(0,0,2),new(13,.14f,12),Game.I.catalog.concrete,null);
  Surface("Service back",p+new Vector3(0,2,7),new(13,4,.25f),Game.I.catalog.concrete,null);
  Surface("Service canopy",p+new Vector3(0,4,2),new(13,.25f,12),Game.I.catalog.asphalt,null);
  for(int i=-1;i<=1;i+=2)Surface("Pillar",p+new Vector3(i*6,2,2),new(.25f,4,.25f),Game.I.catalog.concrete,null);
  Label(n,p+new Vector3(0,4.4f,-4),180,new Color(.95f,.74f,.37f),.4f);Label(subtitle,p+new Vector3(0,3.5f,-4.1f),180,Color.white,.2f);
  if(kind==ServiceKind.Weapons){Place("Bench",p+new Vector3(0,.15f,4),180,null);Place("Rifle",p+new Vector3(0,1,4),90,null);}
 }
 public static void Label(string text,Vector3 p,float yaw,Color c,float size) {
  var go=new GameObject(text);go.transform.SetPositionAndRotation(p,Quaternion.Euler(0,yaw+180,0));var tm=go.AddComponent<TextMesh>();tm.text=text;tm.anchor=TextAnchor.MiddleCenter;tm.alignment=TextAlignment.Center;tm.characterSize=size*.25f;tm.fontSize=64;tm.color=c;
 }
 void Update(){if(Game.I.ready&&Time.time>next){next=Time.time+.6f;UpdateSectors(false);}}
 public void UpdateSectors(bool force) {
  if(!Game.I.player)return;activeSectors=0;Vector3 p=Game.I.player.transform.position;float range=Game.I.player.vehicle&&Game.I.player.vehicle.IsAir?1500:820;
  for(int i=0;i<sectors.Count;i++){bool a=(new Vector2(p.x,p.z)-new Vector2(sectorCenters[i].x,sectorCenters[i].z)).sqrMagnitude<range*range;if(sectors[i].activeSelf!=a)sectors[i].SetActive(a);if(a)activeSectors++;}
 }
 public string District(Vector3 p){if(p.z>1250)return "NORTHWATCH HILLS";if(p.x>1090)return "BREAKWATER COAST";if(p.x>830&&p.z< -250&&p.z> -900)return "BREAKWATER PORT";if(p.x>940)return "SABLE BEACH";if(p.x<-980&&p.z<-950)return "MERIDIAN AIRFIELD";if(p.x<-950||p.z>880)return "GREENRIDGE FARMS";if(p.z<-400&&p.x>200)return "FOUNDRY DISTRICT";if(p.x<-270)return "WESTHAVEN";return "CENTRAL EXCHANGE";}
}
public class WaterSurface:MonoBehaviour {}
public enum ServiceKind { Weapons,Garage,Clinic,Home,Range }
public class ServicePoint:MonoBehaviour {public ServiceKind kind;public string title;}
public class RangeTarget:MonoBehaviour {
 public void Hit(){if(Game.I.ui.rangeTime>0){Game.I.ui.rangeHits++;Game.I.cash+=10;Game.I.Skill(1,.2f);Effects.Burst(transform.position+Vector3.up*1.6f,Color.cyan,12,2);} }
}
}
