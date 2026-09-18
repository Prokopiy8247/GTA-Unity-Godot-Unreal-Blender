using System.Collections.Generic;
using UnityEngine;
namespace Meridian {
public class Population:MonoBehaviour {
 float next;List<Wildlife> fauna=new();int serial;public int maxTraffic=22,maxPedestrians=32;
 public void Initialize(){next=0;}
 void Update(){
  if(!Game.I.ready||Time.time<next)return;next=Time.time+.65f;var p=Game.I.player.transform.position;
  int trafficCount=0,pedCount=0;
  foreach(var v in new List<Vehicle>(Game.I.vehicles))if(v&&v.trafficControlled){
   trafficCount++;float d=Vector3.Distance(v.transform.position,p);if(d>420||!Game.I.traffic){v.DestroyVehicle();trafficCount--;}
  }
  foreach(var a in new List<Actor>(Game.I.actors))if(a&&!a.police&&!a.dead){pedCount++;if(Vector3.Distance(a.transform.position,p)>350||!Game.I.pedestrians){Game.I.actors.Remove(a);Destroy(a.gameObject);pedCount--;}}
  bool city=Mathf.Abs(p.x)<1050&&Mathf.Abs(p.z)<1030;
  for(int i=0;i<3&&Game.I.traffic&&city&&trafficCount<maxTraffic;i++,trafficCount++)SpawnTraffic(p);
  for(int i=0;i<4&&Game.I.pedestrians&&city&&pedCount<maxPedestrians;i++,pedCount++)SpawnPed(p);
  if(Game.I.wildlife&&p.z>1000&&fauna.Count<10){var pos=p+new Vector3(Random.Range(-100,100),0,Random.Range(-100,100));pos.y=World.Height(pos.x,pos.z);var go=Game.I.Model("Deer");go.transform.position=pos;fauna.Add(go.AddComponent<Wildlife>());}
  for(int i=fauna.Count-1;i>=0;i--)if(!fauna[i])fauna.RemoveAt(i);else if(!Game.I.wildlife||Vector3.Distance(fauna[i].transform.position,p)>350){Destroy(fauna[i].gameObject);fauna.RemoveAt(i);}
 }
 void SpawnTraffic(Vector3 player){
  int x=Mathf.Clamp(Mathf.RoundToInt(player.x/128)+Random.Range(-2,3),-6,6),z=Mathf.Clamp(Mathf.RoundToInt(player.z/128)+Random.Range(-2,3),-6,6),h=serial++%4;Vector3 dir=Vehicle.Direction(h),right=Quaternion.Euler(0,90,0)*dir;
  Vector3 pos=new Vector3(x*128,.32f,z*128)+right*4.1f-dir*Random.Range(25,65);
  if(Vector3.Distance(pos,player)<35||Physics.CheckBox(pos+Vector3.up, new Vector3(1.2f,1,3),Quaternion.LookRotation(dir),1<<9))return;
  var v=Game.I.SpawnVehicle(Random.Range(0,9),pos,Quaternion.LookRotation(dir));v.aiSpeed=Random.Range(8,15);v.BeginTraffic(x,z,h);
 }
 void SpawnPed(Vector3 player){int x=Mathf.Clamp(Mathf.FloorToInt(player.x/128)+Random.Range(-1,2),-7,6),z=Mathf.Clamp(Mathf.FloorToInt(player.z/128)+Random.Range(-1,2),-7,6);var pos=new Vector3(x*128+(Random.value<.5f?13:115),.4f,z*128+Random.Range(15,112));if(Vector3.Distance(pos,player)<12)return;Game.I.SpawnActor(pos);}
 public void Panic(Vector3 pos,float radius){foreach(var a in Game.I.actors)if(a&&!a.dead&&Vector3.Distance(a.transform.position,pos)<radius)a.Panic(pos);}
}
public class Wildlife:MonoBehaviour {
 Vector3 direction;float next;void Update(){var p=Game.I.player.transform.position;bool flee=Vector3.Distance(transform.position,p)<22;if(Time.time>next){next=Time.time+Random.Range(2,5);direction=flee?(transform.position-p).normalized:new Vector3(Random.Range(-1f,1),0,Random.Range(-1f,1)).normalized;}direction.y=0;transform.position+=direction*Time.deltaTime*(flee?7:.7f);var pos=transform.position;pos.y=World.Height(pos.x,pos.z);transform.position=pos;if(direction.sqrMagnitude>.1f)transform.rotation=Quaternion.Slerp(transform.rotation,Quaternion.LookRotation(direction),Time.deltaTime*2);}
}
}
