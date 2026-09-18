using System.Collections;
using System.Collections.Generic;
using UnityEngine;
namespace Meridian {
public class WantedSystem:MonoBehaviour {
 public int level;public float pressure,unseen;public bool visible;public Vector3 lastKnown;public string state="CLEAR";float nextScan,nextDispatch,arrest,crimeAt;int pendingReports;public int reportsCompleted;
 static readonly float[] Threshold={0,12,36,75,135,215};
 public void SetLevel(int value){level=Mathf.Clamp(value,0,5);pressure=Threshold[level]+(level>0?1:0);unseen=0;lastKnown=Game.I.player?Game.I.player.transform.position:Vector3.zero;if(level==0){state="CLEAR";visible=false;pendingReports=0;foreach(var v in Game.I.vehicles)if(v&&v.policeControlled){v.policeControlled=false;v.siren=false;}foreach(var a in new List<Actor>(Game.I.actors))if(a&&a.police&&!a.dead){Destroy(a.gameObject);}}else{nextDispatch=0;state="PURSUIT";}}
 public void Crime(Vector3 pos,float severity,float audible,bool immediate=false){
  crimeAt=Time.time;bool policeWitness=immediate;Actor witness=null;
  foreach(var a in Game.I.actors){if(!a||a.dead)continue;float d=Vector3.Distance(a.transform.position,pos);if(a.police&&a.CanSee(pos,110)){policeWitness=true;break;}if(!a.police&&d<audible&&(a.CanSee(pos,audible)||audible>=100)){witness=a;}}
  if(policeWitness){Report(pos,severity);return;}
  if(witness&&pendingReports<4){pendingReports++;witness.StartReport();StartCoroutine(DelayedReport(witness,pos,severity));}
 }
 IEnumerator DelayedReport(Actor witness,Vector3 pos,float severity){yield return new WaitForSeconds(2.6f);pendingReports=Mathf.Max(0,pendingReports-1);if(witness&&!witness.dead){Report(pos,severity);reportsCompleted++;}}
 void Report(Vector3 pos,float severity){pressure=Mathf.Min(320,pressure+severity);lastKnown=pos;int nextLevel=0;for(int i=1;i<Threshold.Length;i++)if(pressure>=Threshold[i])nextLevel=i;if(nextLevel>level){level=nextLevel;nextDispatch=0;Game.I.Notify("POLICE ALERT  /  "+level+" STARS");}unseen=0;}
 void Update(){
  if(!Game.I.ready||level==0)return;var p=Game.I.player;float dt=Time.deltaTime;
  if(Time.time>nextScan){nextScan=Time.time+.25f;visible=false;float visibility=p.crouch?65:110;
   foreach(var a in Game.I.actors)if(a&&a.police&&!a.dead&&a.CanSee(p.transform.position,visibility)){visible=true;break;}
   if(!visible)foreach(var v in Game.I.vehicles)if(v&&v.policeControlled&&!v.destroyed){
    Vector3 eye=v.transform.position+Vector3.up*(v.IsAir?0:1.7f),end=p.transform.position+Vector3.up;float range=v.IsAir?190:140;
    if(Vector3.Distance(eye,end)<range&&!Physics.Linecast(eye,end,1<<0,QueryTriggerInteraction.Ignore)){visible=true;break;}
   }
  }
  if(visible){lastKnown=p.transform.position;unseen=0;state="PURSUIT";}else{unseen+=dt;state="SEARCH";if(unseen>14+level*6){level--;pressure=Threshold[level]+(level>0?1:0);unseen=0;if(level==0){SetLevel(0);Game.I.Notify("SEARCH ENDED  /  CLEAR");}}}
  if(Time.time>nextDispatch){nextDispatch=Time.time+7;Dispatch();}
  if(level==1&&visible&&p.weapons.selected==0&&p.speed<.5f&&!p.vehicle){bool near=false;foreach(var a in Game.I.actors)if(a&&a.police&&!a.dead&&Vector3.Distance(a.transform.position,p.transform.position)<3)near=true;if(near){arrest+=dt;if(arrest>3){Game.I.Respawn(true);arrest=0;}}else arrest=0;}else arrest=0;
 }
 public void Dispatch(){
  if(level==0)return;var p=visible?Game.I.player.transform.position:lastKnown;int count=0;bool heli=false;
  foreach(var v in new List<Vehicle>(Game.I.vehicles))if(v&&v.policeControlled){if(Vector3.Distance(v.transform.position,p)>650){v.DestroyVehicle();continue;}count++;heli|=v.IsAir;}
  if(count<Mathf.Min(8,level+1)){
   Vector3 behind=p-Game.I.cameraRig.transform.forward*(100+Random.Range(20,70));int x=Mathf.Clamp(Mathf.RoundToInt(behind.x/128),-7,7),z=Mathf.Clamp(Mathf.RoundToInt(behind.z/128),-7,7);
   var pos=new Vector3(x*128+4,1,z*128+32);if(Mathf.Abs(p.x)>1050||Mathf.Abs(p.z)>1030)pos=p-Game.I.cameraRig.transform.forward*100;pos.y=World.Height(pos.x,pos.z)+1;
   var v=Game.I.SpawnVehicle(7,pos,Quaternion.LookRotation((new Vector3(p.x,pos.y,p.z)-pos).normalized));v.policeControlled=true;v.engineOn=true;v.siren=true;
  }
  if(level>=3&&!heli){var v=Game.I.SpawnVehicle(13,p+new Vector3(-180,70,-120),Quaternion.identity);v.policeControlled=true;v.engineOn=true;v.siren=true;}
  int cops=0;foreach(var a in Game.I.actors)if(a&&a.police&&!a.dead)cops++;
  if(cops<level*2+2){var pos=p-Game.I.cameraRig.transform.forward*55+Vector3.right*Random.Range(-15,15);pos.y=World.Height(pos.x,pos.z)+.3f;if(!Physics.CheckSphere(pos+Vector3.up,.5f,1<<0))Game.I.SpawnActor(pos,true,level>=4);}
  if(level>=3&&count<3){var pos=new Vector3(Mathf.Round(p.x/128)*128, .2f,Mathf.Round(p.z/128)*128+60);for(int i=-1;i<=1;i+=2){var b=Game.I.world.Place("Barrier",pos+Vector3.right*i*5,90,null,true);Destroy(b,75);}}
 }
}
}
