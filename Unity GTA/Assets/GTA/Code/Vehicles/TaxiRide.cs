using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
namespace Meridian {
public class TaxiRide:MonoBehaviour {
 Vehicle car;readonly List<Vector3> points=new();int next;float began;Vector3 destination;public float remaining;
 public void Initialize(Vehicle v,int district){
  car=v;destination=Roster.Locations[district];float x=car.transform.position.x;
  float gx=Mathf.Round(destination.x/128)*128+4,gz=Mathf.Round(destination.z/128)*128-4;
  if(district==5){Add(new(x,0,-970));Add(new(-1150,0,-970));Add(new(-1150,0,-1250));}
  else if(district==6){Add(new(x,0,960));Add(new(-1250,0,960));}
  else if(district==7){Add(new(x,0,896));Add(new(-508,0,896));Add(new(-500,0,930));for(int i=1;i<=46;i++)Add(new(-470+Mathf.Sin(i*.08f)*280,0,930+i*17));}
  else{Add(new(x,0,gz));Add(new(gx,0,gz));}
  destination=points[points.Count-1];car.passengerService=true;car.driver=null;car.trafficControlled=false;car.body.isKinematic=true;car.engineOn=true;began=Time.time;
  Game.I.Notify("METRO TAXI / T SKIP TRIP AFTER 3 SECONDS");
 }
 void Add(Vector3 p){p.y=World.Height(p.x,p.z)+.3f;points.Add(p);}
 void Update(){
  if(!car||Game.I.player.vehicle!=car){Stop();return;}if(Game.I.paused)return;
  remaining=Vector3.Distance(car.transform.position,destination);
  if(Time.time>began+3&&InputHub.Down(Key.T)){Arrive();return;}
  if(next>=points.Count){Arrive();return;}
  Vector3 delta=points[next]-car.transform.position;
  if(delta.magnitude<2){next++;return;}
  car.body.MoveRotation(Quaternion.RotateTowards(car.body.rotation,Quaternion.LookRotation(delta.normalized,Vector3.up),Time.deltaTime*65));
  Vector3 step=Vector3.MoveTowards(car.transform.position,points[next],Time.deltaTime*14);
  bool blocked=Physics.SphereCast(car.transform.position+Vector3.up+car.transform.forward*2.8f,.7f,car.transform.forward,out var hit,4,1<<9)&&hit.transform.root!=car.transform;
  if(!blocked)car.body.MovePosition(step);
 }
 public void Skip(){if(Time.time>began+3)Arrive();}
 void Arrive(){car.body.position=destination;Game.I.player.ExitVehicle(true);Game.I.player.Teleport(destination+Vector3.right*2);Game.I.Notify("METRO TAXI / ARRIVED");Stop();}
 void Stop(){if(car){car.passengerService=false;car.body.isKinematic=false;car.RemoveDriverModel();}Destroy(this);}
}
}
