using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
namespace Meridian {
public class RuntimeQA:MonoBehaviour {
 readonly List<string> results=new();readonly List<string> errors=new();Game g;float start;float frameSum;int frames;float worst;public static bool Completed;
 void OnEnable(){Application.logMessageReceived+=Log;}
 void OnDisable(){Application.logMessageReceived-=Log;}
 void Log(string m,string stack,LogType type){if(type==LogType.Error||type==LogType.Exception||type==LogType.Assert)errors.Add(m+"\n"+stack);}
 void Update(){if(g&&g.ready&&!g.paused){frameSum+=Time.unscaledDeltaTime;frames++;worst=Mathf.Max(worst,Time.unscaledDeltaTime);}}
 void Check(string name,bool pass,string detail=""){results.Add((pass?"PASS":"FAIL")+" | "+name+" | "+detail);Debug.Log("QA "+results[^1]);File.WriteAllLines(Path.Combine(g.evidenceDir,"runtime-qa.txt"),results);}
 IEnumerator Picture(string name){if(Array.Exists(Environment.GetCommandLineArgs(),a=>a=="-meridianHeadlessQA")){results.Add("SKIP | Rendered frame "+name+" | Headless runner; graphics require separate visual verification");yield break;}yield return new WaitForEndOfFrame();var texture=ScreenCapture.CaptureScreenshotAsTexture();if(texture){var pixels=texture.GetPixels32();var colors=new HashSet<int>();for(int i=0;i<pixels.Length;i+=241){var c=pixels[i];colors.Add(c.r*65536+c.g*256+c.b);}Check("Rendered frame "+name,colors.Count>80,colors.Count+" sampled colors; "+g.ui.fps.ToString("F1")+" FPS");File.WriteAllBytes(Path.Combine(g.evidenceDir,name+".png"),texture.EncodeToPNG());Destroy(texture);}else Check("Capture "+name,false);}
 IEnumerator Start(){
  g=Game.I;start=Time.realtimeSinceStartup;g.god=true;InputHub.scripted=true;g.savePath=Path.Combine(g.evidenceDir,"qa-save.json");g.cameraRig.yaw=10;g.cameraRig.pitch=12;
  yield return new WaitForSeconds(4);
  Check("54 Blender assets integrated",g.catalog.names.Length>=54,g.catalog.names.Length.ToString());Check("Free roam bootstrap",g.ready&&g.player&&g.cameraRig);Check("World sectors",g.world.sectors.Count==225);
  yield return Picture("01-downtown");
  var p=g.player;var old=p.transform.position;InputHub.simulatedMove=new(0,1);yield return new WaitForSeconds(2);InputHub.simulatedMove=Vector2.zero;Check("Player moves",Vector3.Distance(old,p.transform.position)>4);
  Check("Traffic population",g.vehicles.Exists(v=>v&&v.trafficControlled));Check("Pedestrian population",g.actors.Exists(a=>a&&!a.police));
  var traffic=g.vehicles.Find(v=>v&&v.trafficControlled);if(traffic){old=traffic.transform.position;yield return new WaitForSeconds(1);Check("Traffic follows lanes",Vector3.Distance(old,traffic.transform.position)>.2f);}
  // Every offered land vehicle must actually accelerate, not merely appear in the menu.
  for(int i=0;i<=10;i++){
   p.ExitVehicle(true);Vector3 location=new(-1370,1,-1810+i*42);p.Teleport(location+Vector3.right*3);var v=g.SpawnVehicle(i,location,Quaternion.identity);yield return new WaitForSeconds(.6f);p.EnterVehicle(v,true);old=v.transform.position;InputHub.simulatedMove=new(0,1);yield return new WaitForSeconds(2.5f);InputHub.simulatedMove=Vector2.zero;
   Check("Drive "+v.spec.id,Vector3.Distance(old,v.transform.position)>2,v.Speed.ToString("F2")+" m/s");InputHub.simulatedBrake=true;yield return new WaitForSeconds(.4f);InputHub.simulatedBrake=false;p.ExitVehicle(true);Check("Exit "+i,p.controller.enabled&&!p.vehicle);v.Damage(45);Check("Damage "+i,v.health<100);v.Repair();Check("Repair "+i,Mathf.Approximately(v.health,100));
  }
  g.wanted.SetLevel(0);g.Teleport(0);g.cameraRig.yaw=200;yield return new WaitForSeconds(1);yield return Picture("05-street-vehicles");
  p.Teleport(new(-1100,1,-1100));p.transform.rotation=Quaternion.identity;var target=g.SpawnActor(p.transform.position+Vector3.forward*9);yield return new WaitForSeconds(.2f);p.weapons.GiveAll();p.weapons.Equip(7);float hp=target.health;g.cameraRig.aimPoint=target.transform.position+Vector3.up;p.weapons.TryFire();Check("Raycast combat damages NPC",target.health<hp);p.weapons.ammo[7]=0;p.weapons.Reload();yield return new WaitForSeconds(2);Check("Magazine reload",p.weapons.ammo[7]>0);
  target.Damage(200,Vector3.forward*5,true);yield return new WaitForSeconds(.2f);Check("Articulated ragdoll",target.dead&&target.GetComponentsInChildren<CharacterJoint>().Length>=3);
  g.wanted.SetLevel(0);p.Teleport(new(-2100,1,-2300));g.wanted.Crime(p.transform.position,25,30);yield return new WaitForSeconds(3);Check("Unwitnessed crime stays unknown",g.wanted.level==0);
  var witness=g.SpawnActor(p.transform.position+Vector3.forward*4);g.wanted.Crime(p.transform.position,25,45);yield return new WaitForSeconds(3);Check("Delayed witness report",g.wanted.level>0);
  g.wanted.SetLevel(5);g.wanted.Dispatch();Check("Five-star response",g.wanted.level==5&&g.vehicles.Exists(v=>v&&v.policeControlled));g.wanted.SetLevel(2);
  var officer=g.SpawnActor(p.transform.position+Vector3.forward*8,true);yield return new WaitForSeconds(.5f);Check("Police line of sight",g.wanted.visible);
  p.Teleport(new(-2100,1,300));yield return new WaitForSeconds(.6f);Check("Real search after LOS loss",!g.wanted.visible&&g.wanted.state=="SEARCH");
  g.wanted.unseen=25.8f;yield return new WaitForSeconds(.5f);Check("Unseen wanted decay",g.wanted.level==1);g.wanted.SetLevel(0);
  float cash=g.cash;g.Save();g.cash=0;Check("Save/load restores cash",g.Load(false)&&Mathf.Abs(g.cash-cash)<.1f);
  string good=File.ReadAllText(g.savePath);File.WriteAllText(g.savePath,"{}");Check("Malformed save rejected",!g.Load(false));File.WriteAllText(g.savePath,good);
  for(int i=0;i<9;i++){g.Teleport(i);yield return new WaitForSeconds(.3f);Check("District accessible "+i,p.transform.position.y>-20,Roster.Districts[i]);}
  g.Teleport(5);g.cameraRig.yaw=225;yield return new WaitForSeconds(1);yield return Picture("02-airport");
  for(int i=12;i<=13;i++){var h=g.SpawnVehicle(i,new(-1130+(i-12)*30,1,-1260),Quaternion.identity);p.EnterVehicle(h,true);InputHub.simulatedLift=1;yield return new WaitForSeconds(3);InputHub.simulatedLift=0;Check("Helicopter "+i+" lift",h.transform.position.y>7,h.transform.position.y.ToString("F1"));p.ExitVehicle(true);}
  var plane=g.SpawnVehicle(14,new(-1370,1,-1930),Quaternion.identity);p.EnterVehicle(plane,true);InputHub.simulatedMove=new(0,1);yield return new WaitForSeconds(17);InputHub.simulatedMove=Vector2.zero;Check("Airplane powered flight",plane.Speed>22&&plane.transform.position.y>4,plane.Speed.ToString("F1")+" m/s; altitude "+plane.transform.position.y.ToString("F1"));yield return Picture("06-flight");p.ExitVehicle(true);
  var boat=g.SpawnVehicle(11,new(1240,.1f,-510),Quaternion.identity);p.Teleport(new(1243,1,-510));p.EnterVehicle(boat,true);old=boat.transform.position;InputHub.simulatedMove=new(0,1);yield return new WaitForSeconds(4);InputHub.simulatedMove=Vector2.zero;Check("Boat buoyancy and propulsion",Vector3.Distance(old,boat.transform.position)>5&&boat.transform.position.y>-1);yield return Picture("07-coast");p.ExitVehicle(true);yield return new WaitForSeconds(.5f);Check("Swimming",p.swimming);
  InputHub.simulatedLift=-1;yield return new WaitForSeconds(2);InputHub.simulatedLift=0;Check("Diving breath",p.transform.position.y<-.7f&&p.breath<100);
  g.atmosphere.hour=21;g.atmosphere.SetWeather(2);g.Teleport(0);g.cameraRig.yaw=25;g.cameraRig.pitch=8;yield return new WaitForSeconds(2);yield return Picture("03-rain-night");Check("Weather state",g.atmosphere.weather==2);
  g.atmosphere.hour=16.4f;g.atmosphere.SetWeather(0);g.ui.panel="admin";g.Pause(true);yield return new WaitForSecondsRealtime(.5f);yield return Picture("04-sandbox-menu");g.ui.panel="";g.Pause(false);
  g.CallTaxi(1);var ride=p.vehicle?p.vehicle.GetComponent<TaxiRide>():null;Check("Taxi passenger boarding",ride&&p.vehicle.passengerService);yield return new WaitForSeconds(4);if(ride)ride.Skip();yield return new WaitForSeconds(.2f);Check("Taxi arrival",!p.vehicle&&Vector3.Distance(p.transform.position,Roster.Locations[1])<120);
  Check("No runtime exceptions",errors.Count==0,errors.Count.ToString());results.Add("PERFORMANCE average FPS "+(frames/Mathf.Max(.001f,frameSum)).ToString("F1")+"; worst frame ms "+(worst*1000).ToString("F1"));results.Add("WALL SECONDS "+(Time.realtimeSinceStartup-start).ToString("F1"));File.WriteAllLines(Path.Combine(g.evidenceDir,"runtime-qa.txt"),results);File.WriteAllLines(Path.Combine(g.evidenceDir,"runtime-errors.txt"),errors);Completed=true;Debug.Log("MERIDIAN_QA_COMPLETE");yield return new WaitForSeconds(1);Application.Quit(errors.Count>0||results.Exists(r=>r.StartsWith("FAIL"))?2:0);
 }
}
}
