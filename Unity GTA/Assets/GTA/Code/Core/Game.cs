using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.InputSystem;
namespace Meridian {
public class Game : MonoBehaviour {
 public static Game I;
 public GameCatalog catalog;
 public World world; public PlayerMotor player; public FollowCamera cameraRig; public Population population; public WantedSystem wanted; public Atmosphere atmosphere; public GameUI ui; public SoundBank sound;
 public List<Vehicle> vehicles=new(); public List<Actor> actors=new();
 public float cash=25000; public float[] skills=new float[7]; public bool god,traffic=true,pedestrians=true,wildlife=true,paused,ready; public string toast="WELCOME TO MERIDIAN COAST"; public float toastUntil=8;
 public string savePath; public Vehicle storedVehicle; public int storedIndex; public Color storedPaint=Color.white; public float storedEngine=1;
 public bool automated; public string evidenceDir;
 void Awake() {
  I=this;Application.targetFrameRate=60;QualitySettings.vSyncCount=0;Physics.defaultSolverIterations=10;Time.fixedDeltaTime=.02f;
  savePath=Path.Combine(Application.persistentDataPath,"meridian-save.json");
  automated=Array.Exists(Environment.GetCommandLineArgs(),a=>a=="-meridianQA");evidenceDir=automated?Path.Combine(Directory.GetCurrentDirectory(),".astra-run"):Path.Combine(Application.persistentDataPath,"Photos");Directory.CreateDirectory(evidenceDir);
  sound=gameObject.AddComponent<SoundBank>();world=gameObject.AddComponent<World>();wanted=gameObject.AddComponent<WantedSystem>();population=gameObject.AddComponent<Population>();atmosphere=gameObject.AddComponent<Atmosphere>();ui=gameObject.AddComponent<GameUI>();
 }
 IEnumerator Start() {
  world.Build();
  var go=new GameObject("Player");go.transform.position=new Vector3(9,1,20);player=go.AddComponent<PlayerMotor>();player.Initialize();
  var cam=new GameObject("Gameplay Camera");cam.tag="MainCamera";cam.AddComponent<Camera>();cam.AddComponent<AudioListener>();cameraRig=cam.AddComponent<FollowCamera>();
  atmosphere.Initialize();population.Initialize();SpawnVehicle(0,new Vector3(5,1,25),Quaternion.identity);
  SpawnVehicle(2,new Vector3(-5,1,33),Quaternion.identity);SpawnVehicle(7,new Vector3(7,1,78),Quaternion.identity);
  SpawnVehicle(12,new Vector3(-1110,1,-1220),Quaternion.identity);SpawnVehicle(14,new Vector3(-1135,1,-1290),Quaternion.identity);SpawnVehicle(11,new Vector3(1200,.2f,-510),Quaternion.Euler(0,90,0));
  if(!automated)Load(false);
  yield return null;ready=true;world.UpdateSectors(true);CursorState();
  if(automated)gameObject.AddComponent<RuntimeQA>();
 }
 void Update() {
  if(!ready)return;
  if(InputHub.Down(Key.F11))Screen.fullScreen=!Screen.fullScreen;
  if(InputHub.Down(Key.Escape)){ui.panel=ui.panel==""?"pause":"";Pause(ui.panel=="pause");}
  if(InputHub.Down(Key.F1)){ui.panel=ui.panel=="admin"?"":"admin";Pause(ui.panel!="");}
  if(InputHub.Down(Key.M)){ui.panel=ui.panel=="map"?"":"map";Pause(ui.panel!="");}
  if(InputHub.Down(Key.P)){ui.panel=ui.panel=="phone"?"":"phone";Pause(ui.panel!="");}
  if(InputHub.Down(Key.F5))Save();
  if(InputHub.Down(Key.F9))Load();
  if(InputHub.Down(Key.F12)){ScreenCapture.CaptureScreenshot(Path.Combine(evidenceDir,"photo-"+DateTime.Now.ToString("HHmmss")+".png"));Notify("PHOTO SAVED");}
 }
 public void Pause(bool p){paused=p;Time.timeScale=p?0:1;CursorState();}
 public void CursorState(){bool free=paused||ui.panel!="";Cursor.lockState=free?CursorLockMode.None:CursorLockMode.Locked;Cursor.visible=free;}
 public void Notify(string s){toast=s;toastUntil=Time.unscaledTime+4;sound?.Play("ui",player?player.transform.position:Vector3.zero,.35f);}
 public GameObject Model(string n,Transform parent=null){var src=catalog.Get(n);if(!src)throw new Exception("Missing Blender asset: "+n);var o=Instantiate(src,parent);o.name=n;return o;}
 public Vehicle SpawnVehicle(int index,Vector3 p,Quaternion r) {
  if(vehicles.Count>=70){var old=vehicles.Find(v=>v&&v.driver==null&&!v.policeControlled);if(old)old.DestroyVehicle();}
  index=Mathf.Clamp(index,0,Roster.Vehicles.Length-1);var spec=Roster.Vehicles[index];var go=new GameObject(spec.label);go.transform.SetPositionAndRotation(p,r);
  var v=go.AddComponent<Vehicle>();v.index=index;v.Initialize();vehicles.Add(v);return v;
 }
 public Actor SpawnActor(Vector3 p,bool police=false,bool tactical=false) {
  if(actors.Count>=110){var old=actors.Find(a=>a&&a.dead);if(old){actors.Remove(old);Destroy(old.gameObject);}}
  var go=new GameObject(police?"Police officer":"Citizen");go.transform.position=p;var a=go.AddComponent<Actor>();a.police=police;a.tactical=tactical;a.Initialize();actors.Add(a);return a;
 }
 public void Teleport(int index){player.ExitVehicle(true);Vector3 p=Roster.Locations[index];p.y=World.Height(p.x,p.z)+1;player.Teleport(p);world.UpdateSectors(true);Notify(Roster.Districts[index]);}
 public Vehicle SpawnForPlayer(int index) {
  var spec=Roster.Vehicles[index];Vector3 p=player.transform.position+player.transform.forward*7;
  if(spec.kind==VehicleKind.Boat){p=new Vector3(1210,.3f,-510);player.Teleport(p+new Vector3(-3,1,0));}
  if(spec.kind==VehicleKind.Plane){p=new Vector3(-1135,1,-1290);player.Teleport(p+new Vector3(3,0,0));}
  p.y=spec.kind==VehicleKind.Boat? 0.3f:World.Height(p.x,p.z)+1;
  var v=SpawnVehicle(index,p,Quaternion.identity);Notify("DELIVERED  "+spec.label);return v;
 }
 public void Skill(int i,float amount){skills[i]=Mathf.Min(100,skills[i]+amount);}
 public bool Pay(float cost){if(cash<cost){Notify("INSUFFICIENT CASH");return false;}cash-=cost;return true;}
 public void CallTaxi(int district) {
  float fare=50+Vector3.Distance(player.transform.position,Roster.Locations[district])*.04f;if(!Pay(fare))return;player.ExitVehicle(true);float x=Mathf.Clamp(Mathf.Round(player.transform.position.x/128)*128+4,-892,900);var start=new Vector3(x,.3f,Mathf.Clamp(player.transform.position.z,-890,890));var taxi=SpawnVehicle(8,start,Quaternion.identity);player.EnterVehicle(taxi,true);taxi.BeginTraffic(Mathf.RoundToInt(x/128),Mathf.RoundToInt(start.z/128),0);taxi.gameObject.AddComponent<TaxiRide>().Initialize(taxi,district);
 }
 public void Respawn(bool arrest=false){StartCoroutine(RespawnRoutine(arrest));}
 IEnumerator RespawnRoutine(bool arrest) {
  player.dead=true;ui.death=arrest?"DETAINED":"CRITICAL INJURY";wanted.SetLevel(0);yield return new WaitForSecondsRealtime(2);
  player.ExitVehicle(true);player.Teleport(new Vector3(24,1,148));player.health=100;player.armor=0;cash=Mathf.Max(0,cash-(arrest?400:250));player.dead=false;ui.death="";Notify(arrest?"Released from Central Station":"Discharged from Meridian Clinic");
 }
 [Serializable] public class SaveData {public int version=1;public Vector3 position;public float health,armor,cash,hour;public int weapon,weather,storedIndex;public float storedEngine;public Color storedPaint;public float[] skills;public int[] ammo,reserve;public bool[] owned;public bool suppressor,extended,grip,scuba;public int outfit;}
 public void Save() {
  if(!ready)return;
  var w=player.weapons;var s=new SaveData{position=player.transform.position,health=player.health,armor=player.armor,cash=cash,hour=atmosphere.hour,weather=atmosphere.weather,weapon=w.selected,skills=skills,ammo=w.ammo,reserve=w.reserve,owned=w.owned,suppressor=w.suppressor,extended=w.extended,grip=w.grip,scuba=player.scuba,outfit=player.outfit,storedIndex=storedIndex,storedEngine=storedEngine,storedPaint=storedPaint};
  try {File.WriteAllText(savePath+".tmp",JsonUtility.ToJson(s,true));File.Copy(savePath+".tmp",savePath,true);File.Delete(savePath+".tmp");Notify("FREE ROAM SAVED");}catch(Exception e){Debug.LogWarning(e);Notify("Save failed: "+e.Message);}
 }
 public bool Load(bool notify=true) {
  if(!File.Exists(savePath)){if(notify)Notify("NO SAVE FOUND");return false;}
  try {var s=JsonUtility.FromJson<SaveData>(File.ReadAllText(savePath));if(s==null||s.version!=1||s.owned==null||s.owned.Length!=Weapons.Defs.Length||s.ammo==null||s.ammo.Length!=Weapons.Defs.Length||s.reserve==null||s.reserve.Length!=Weapons.Defs.Length||float.IsNaN(s.position.x)||float.IsInfinity(s.position.y))throw new Exception("Unsupported save");
   player.ExitVehicle(true);player.Teleport(s.position);player.health=Mathf.Clamp(s.health,1,100);player.armor=Mathf.Clamp(s.armor,0,100);cash=Mathf.Max(0,s.cash);atmosphere.hour=s.hour;atmosphere.SetWeather(s.weather);skills=s.skills?.Length==7?s.skills:new float[7];
   player.weapons.ammo=s.ammo;player.weapons.reserve=s.reserve;player.weapons.owned=s.owned;player.weapons.suppressor=s.suppressor;player.weapons.extended=s.extended;player.weapons.grip=s.grip;player.weapons.Equip(s.weapon);player.scuba=s.scuba;player.SetOutfit(s.outfit);storedIndex=s.storedIndex;storedEngine=s.storedEngine;storedPaint=s.storedPaint;wanted.SetLevel(0);if(notify)Notify("FREE ROAM LOADED");return true;
  }catch(Exception e){Debug.LogWarning("Save ignored: "+e.Message);if(notify)Notify("Save unreadable; world preserved");return false;}
 }
 void OnApplicationQuit(){if(ready&&!automated)Save();}
}
}
