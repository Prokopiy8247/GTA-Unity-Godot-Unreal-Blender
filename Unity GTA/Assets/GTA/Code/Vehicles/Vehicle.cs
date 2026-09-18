using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
namespace Meridian {
public class Vehicle:MonoBehaviour {
 public bool passengerService;public int index;public VehicleSpec spec;public Rigidbody body;public PlayerMotor driver;public GameObject visual;public bool trafficControlled,policeControlled,destroyed,engineOn,lightsOn=true,siren;
 public float health=100,engineUpgrade=1,brakeUpgrade=1,armorUpgrade=1,throttle,steer;public int routeX,routeZ,heading;public float aiSpeed=12;public Vector3 aiTarget;
 public List<WheelCollider> wheels=new();List<Transform> wheelMeshes=new();List<Light> headlights=new();List<Light> beacons=new();AudioSource engine,sirenAudio;
 float spin,smokeAt,fireTimer,stuckTimer,nextHit,hornAt;Vector3 lastPos;float airThrottle=.25f;GameObject driverVisual;Material paint;
 public bool IsAir=>spec.kind==VehicleKind.Helicopter||spec.kind==VehicleKind.Plane;
 public bool IsLand=>spec.kind==VehicleKind.Car||spec.kind==VehicleKind.Motorcycle||spec.kind==VehicleKind.Bicycle;
 public float Speed=>body?body.linearVelocity.magnitude:0;
 public void Initialize(){
  spec=Roster.Vehicles[index];gameObject.layer=9;visual=Game.I.Model(spec.id,transform);PlayerMotor.SetLayer(visual,9);
  body=gameObject.AddComponent<Rigidbody>();body.mass=spec.mass;body.interpolation=RigidbodyInterpolation.Interpolate;body.collisionDetectionMode=CollisionDetectionMode.ContinuousDynamic;body.linearDamping=.08f;body.angularDamping=2;body.centerOfMass=new(0,.4f,0);body.maxAngularVelocity=4;
  var collider=gameObject.AddComponent<BoxCollider>();collider.center=new(0,IsAir?1.1f:.72f,0);collider.size=spec.kind switch {VehicleKind.Motorcycle or VehicleKind.Bicycle=>new(.55f,.8f,1.65f),VehicleKind.Boat=>new(1.8f,.8f,4.6f),VehicleKind.Helicopter=>new(1.7f,1.6f,4),VehicleKind.Plane=>new(1.15f,1.05f,6.3f),_=>new(1.78f,.9f,spec.length*.92f)};
  if(IsLand){
   foreach(var t in visual.GetComponentsInChildren<Transform>())if(t.name.StartsWith("Wheel_")){
    var o=new GameObject("Suspension "+t.name);o.transform.SetParent(transform);Vector3 p=transform.InverseTransformPoint(t.position);o.transform.localPosition=p+Vector3.up*.15f;
    var wc=o.AddComponent<WheelCollider>();wc.radius=spec.kind==VehicleKind.Car?(index==4? 0.4f:.35f):.35f;wc.mass=spec.kind==VehicleKind.Car?28:10;wc.suspensionDistance=.24f;
    var spring=wc.suspensionSpring;spring.spring=spec.mass*25;spring.damper=spec.mass*3;spring.targetPosition=.5f;wc.suspensionSpring=spring;
    var forward=wc.forwardFriction;forward.stiffness=1.35f;wc.forwardFriction=forward;var side=wc.sidewaysFriction;side.stiffness=1.5f;wc.sidewaysFriction=side;
    wheels.Add(wc);wheelMeshes.Add(t);
   }
   if(spec.kind!=VehicleKind.Car){body.constraints=RigidbodyConstraints.FreezeRotationX|RigidbodyConstraints.FreezeRotationZ;body.centerOfMass=new(0,.25f,0);}
  }
  if(spec.kind==VehicleKind.Plane){var wing=gameObject.AddComponent<BoxCollider>();wing.center=new(0,1,0);wing.size=new(9,.16f,1.1f);}
  for(int i=-1;i<=1;i+=2){var go=new GameObject("Headlamp");go.transform.SetParent(transform);go.transform.localPosition=new(i*.65f,.75f,spec.length*.48f);var l=go.AddComponent<Light>();l.type=LightType.Spot;l.range=42;l.spotAngle=55;l.intensity=2.6f;l.color=new(.9f,.92f,.8f);l.shadows=LightShadows.None;headlights.Add(l);}
  if(index==7||index==13)for(int i=-1;i<=1;i+=2){var go=new GameObject("Police beacon");go.transform.SetParent(transform);go.transform.localPosition=new(i*.5f,1.85f,0);var l=go.AddComponent<Light>();l.type=LightType.Point;l.range=12;l.intensity=3;l.color=i<0?Color.red:Color.blue;beacons.Add(l);}
  engine=Game.I.sound.Loop(IsAir?"rotor":"engine",transform,.16f,1);
  sirenAudio=Game.I.sound.Loop("siren",transform,0,1);lastPos=transform.position;
 }
 void Update(){
  if(!Game.I.ready)return;
  if(driver&&!Game.I.paused){if(InputHub.Down(Key.L))lightsOn=!lightsOn;if(InputHub.Down(Key.H)&&Time.time>hornAt){Game.I.sound.Play("horn",transform.position,.7f);hornAt=Time.time+.5f;}if(InputHub.Down(Key.J))siren=!siren;if(InputHub.Down(Key.N))Game.I.sound.CycleRadio();}
  bool night=Game.I.atmosphere.hour<6||Game.I.atmosphere.hour>18;foreach(var l in headlights)l.enabled=lightsOn&&(night||driver)&&!destroyed;
  for(int i=0;i<beacons.Count;i++)beacons[i].enabled=siren&&!destroyed&&((int)(Time.time*9)+i)%2==0;
  if(engine){engine.volume=engineOn&&!destroyed?(driver? 0.3f:.12f):.015f;engine.pitch=Mathf.Clamp(.6f+Speed*.025f+Mathf.Abs(throttle)*.2f,.55f,2.2f);}
  if(sirenAudio)sirenAudio.volume=siren&&!destroyed? 0.24f:0;
  if(health<32&&!destroyed&&Time.time>smokeAt){smokeAt=Time.time+.18f;Effects.Burst(transform.position+Vector3.up*1.3f,health<12?new Color(.9f,.3f,.05f):new Color(.15f,.15f,.16f),8,health<12?2:1,2.5f);if(health<12){fireTimer+=.18f;if(fireTimer>8)Damage(200);}}
  spin+=Speed*Time.deltaTime*150;
  for(int i=0;i<wheelMeshes.Count;i++){
   var t=wheelMeshes[i];if(trafficControlled){t.localRotation=Quaternion.Euler(spin,0,0);continue;}
   wheels[i].GetWorldPose(out var p,out var r);t.SetPositionAndRotation(p,r);
  }
  foreach(var t in visual.GetComponentsInChildren<Transform>())if(t.name.StartsWith("Rotor")){if(t.name.Contains("Main"))t.Rotate(Vector3.up,engineOn?Time.deltaTime*1800:0,Space.Self);else t.Rotate(Vector3.forward,engineOn?Time.deltaTime*2300:0,Space.Self);}
  if(!driver&&!policeControlled&&!trafficControlled&&transform.position.y<-35)DestroyVehicle();
 }
 void FixedUpdate(){
  if(destroyed||!Game.I.ready||Game.I.paused||passengerService)return;
  if(trafficControlled){TrafficStep();return;}
  throttle=driver?InputHub.Move.y:0;steer=driver?InputHub.Move.x:0;
  if(policeControlled&&!driver)PoliceDrive();
  if(IsLand)LandPhysics();
  else if(spec.kind==VehicleKind.Boat)BoatPhysics();
  else if(spec.kind==VehicleKind.Helicopter)HelicopterPhysics();
  else PlanePhysics();
 }
 void LandPhysics(){
  float forwardSpeed=Vector3.Dot(body.linearVelocity,transform.forward);float max=spec.maxSpeed*engineUpgrade;float motor=throttle*spec.power*engineUpgrade*Mathf.Lerp(.42f,1,health/100)/Mathf.Max(2,wheels.Count);
  bool brake=(driver&&(InputHub.Held(Key.Space)||InputHub.simulatedBrake))||(!driver&&!policeControlled);float wet=Game.I.atmosphere.weather>=2? 0.73f:1;
  for(int i=0;i<wheels.Count;i++){
   var w=wheels[i];bool front=w.transform.localPosition.z>0;w.steerAngle=front?steer*Mathf.Lerp(31,11,Mathf.Abs(forwardSpeed)/45):0;
   w.motorTorque=Mathf.Abs(forwardSpeed)<max?motor:0;w.brakeTorque=brake?spec.mass*1.8f*brakeUpgrade:(throttle*forwardSpeed<-1?spec.mass*.75f*brakeUpgrade:0);
   var f=w.sidewaysFriction;f.stiffness=(brake&&!front? 0.45f:1.55f)*wet;w.sidewaysFriction=f;
  }
  if(spec.kind==VehicleKind.Car){body.AddForce(-transform.up*Speed*4,ForceMode.Force);body.AddTorque(Vector3.Cross(transform.up,Vector3.up)*Mathf.Max(0,Vector3.Dot(transform.up,Vector3.up))*spec.mass*1.5f,ForceMode.Force);}
  if(driver){Game.I.Skill(4,Speed*Time.fixedDeltaTime*.0005f);if(spec.kind==VehicleKind.Bicycle)Game.I.Skill(0,Time.fixedDeltaTime*.012f);}
  if(driver&&Mathf.Abs(steer)>.65f&&Speed>15&&InputHub.Held(Key.Space)&&Time.frameCount%8==0){Effects.Burst(transform.position-transform.forward,Color.gray,5,1);Game.I.sound.Play("skid",transform.position,.2f);}
 }
 void BoatPhysics(){
  bool water=transform.position.x>1100;
  if(water){
   float desired=.05f+Mathf.Sin(Time.time*1.4f+transform.position.x*.02f)*.12f;
   body.AddForce(Vector3.up*(9.81f+(desired-transform.position.y)*8-body.linearVelocity.y*3),ForceMode.Acceleration);
   body.AddTorque(Vector3.Cross(transform.up,Vector3.up)*8-body.angularVelocity*2,ForceMode.Acceleration);
   body.AddForce(-transform.right*Vector3.Dot(body.linearVelocity,transform.right)*1.3f,ForceMode.Acceleration);
   if(Speed<spec.maxSpeed)body.AddForce(transform.forward*throttle*spec.power,ForceMode.Acceleration);body.AddTorque(Vector3.up*steer*Mathf.Clamp(Speed*.1f,.2f,1.5f),ForceMode.Acceleration);
   if(driver&&Speed>5&&Time.frameCount%8==0)Effects.Burst(transform.position-transform.forward*2, new Color(.6f,.8f,.85f),8,2);
  }
 }
 void HelicopterPhysics(){
  if(!engineOn&&!policeControlled)return;
  float lift=driver?InputHub.Lift:policeControlled?Mathf.Clamp((aiTarget.y-transform.position.y)*.3f,-1,1):0;
  var desired=Quaternion.Euler(throttle*13,transform.eulerAngles.y+steer*40*Time.fixedDeltaTime,-steer*8);
  body.MoveRotation(Quaternion.Slerp(body.rotation,desired,Time.fixedDeltaTime*2));
  body.AddForce(Vector3.up*(9.81f+lift*8-body.linearVelocity.y*.9f),ForceMode.Acceleration);
  body.AddForce(transform.forward*throttle*10-body.linearVelocity*.16f,ForceMode.Acceleration);
  if(driver)Game.I.Skill(5,Time.fixedDeltaTime*.009f);
  if(transform.position.y>550)body.AddForce(Vector3.down*12,ForceMode.Acceleration);
 }
 void PlanePhysics(){
  if(driver){airThrottle=Mathf.Clamp01(airThrottle+InputHub.Move.y*Time.fixedDeltaTime*.22f);float pitch=(InputHub.Held(Key.DownArrow)?-1:0)+(InputHub.Held(Key.UpArrow)?1:0)-InputHub.Lift;float yaw=(InputHub.Held(Key.E)?1:0)-(InputHub.Held(Key.Q)?1:0);
   body.AddRelativeTorque(new Vector3(pitch*2.3f,yaw*1.1f,-steer*2),ForceMode.Acceleration);Game.I.Skill(5,Time.fixedDeltaTime*.009f);}
  if(engineOn){body.AddForce(transform.forward*airThrottle*14,ForceMode.Acceleration);float airspeed=Mathf.Max(0,Vector3.Dot(body.linearVelocity,transform.forward));float lift=Mathf.Clamp(airspeed*airspeed*.015f,0,14);body.AddForce(transform.up*lift,ForceMode.Acceleration);body.AddForce(-body.linearVelocity*.05f,ForceMode.Acceleration);}
 }
 public void BeginTraffic(int x,int z,int dir) {
  routeX=x;routeZ=z;heading=dir;trafficControlled=true;engineOn=true;body.isKinematic=true;NextTarget(false);
  driverVisual=Game.I.Model("Pedestrian_M",visual.transform);driverVisual.transform.localPosition=new(-.4f,-.05f,-.15f);driverVisual.transform.localScale=Vector3.one*.86f;PlayerMotor.SetLayer(driverVisual,9);
 }
 public static Vector3 Direction(int h)=>h switch {0=>Vector3.forward,1=>Vector3.right,2=>Vector3.back,_=>Vector3.left};
 void NextTarget(bool advance=true) {
  var d=Direction(heading);if(advance){routeX+=(int)d.x;routeZ+=(int)d.z;}
  routeX=Mathf.Clamp(routeX,-7,7);routeZ=Mathf.Clamp(routeZ,-7,7);
  Vector3 right=Quaternion.Euler(0,90,0)*d;aiTarget=new Vector3(routeX*128,0,routeZ*128)+right*4.1f;
 }
 void TrafficStep(){
  Vector3 to=aiTarget-transform.position;to.y=0;
  if(to.magnitude<5){
   int turn=Random.value<.22f?(Random.value<.5f?-1:1):0;heading=(heading+turn+4)%4;
   if((routeX>=7&&heading==1)||(routeX<=-7&&heading==3)||(routeZ>=7&&heading==0)||(routeZ<=-7&&heading==2))heading=(heading+2)%4;
   NextTarget();to=aiTarget-transform.position;to.y=0;
  }
  bool red=((int)(Time.time/9)%2==0)!=(heading%2==0);float distance=to.magnitude;float targetSpeed=red&&distance<17&&distance>6?0:aiSpeed;
  Vector3 origin=transform.position+transform.forward*(spec.length*.5f+.3f)+Vector3.up*.6f;
  if(Physics.SphereCast(origin,.65f,transform.forward,out var hit,Mathf.Max(5,aiSpeed*.65f),(1<<9)|(1<<8),QueryTriggerInteraction.Ignore)&&hit.transform.root!=transform)targetSpeed=0;
  float current=Vector3.Distance(transform.position,lastPos)/Time.fixedDeltaTime;float speed=Mathf.MoveTowards(current,targetSpeed,Time.fixedDeltaTime*5);lastPos=transform.position;
  if(to.sqrMagnitude>.1f)body.MoveRotation(Quaternion.RotateTowards(body.rotation,Quaternion.LookRotation(to),Time.fixedDeltaTime*75));
  body.MovePosition(transform.position+transform.forward*speed*Time.fixedDeltaTime);
  if(targetSpeed==0)stuckTimer+=Time.fixedDeltaTime;else stuckTimer=0;if(stuckTimer>30){stuckTimer=0;NextTarget();}
  if(!trafficControlled&&driverVisual)Destroy(driverVisual);
 }
 void PoliceDrive(){
  if(!Game.I.player)return;var p=Game.I.player.transform.position;Vector3 target=Game.I.wanted.visible?p:Game.I.wanted.lastKnown;
  if(IsAir){aiTarget=target+Vector3.up*45;Vector3 d=target-transform.position;d.y=0;steer=Mathf.Clamp(Vector3.SignedAngle(transform.forward,d,Vector3.up)/40,-1,1);throttle=d.magnitude>25? 0.75f:0;return;}
  Vector3 direct=target-transform.position;float dist=direct.magnitude;
  // Pursue via road intersections when far away, then intercept locally.
  if(dist>45){float nx=Mathf.Round(transform.position.x/128)*128,nz=Mathf.Round(transform.position.z/128)*128;float tx=Mathf.Round(target.x/128)*128,tz=Mathf.Round(target.z/128)*128;
   if(Mathf.Abs(transform.position.x-nx)>14)target=new(nx,0,nz);else if(Mathf.Abs(tx-nx)>20)target=new(nx+Mathf.Sign(tx-nx)*128,0,nz+4);else target=new(nx+4,0,nz+Mathf.Sign(tz-nz)*128);}
  Vector3 local=transform.InverseTransformPoint(target);steer=Mathf.Clamp(Mathf.Atan2(local.x,local.z)*1.6f,-1,1);throttle=dist>9?1:0;
  if(Physics.Raycast(transform.position+Vector3.up*.7f+transform.forward*2.7f,transform.forward,6,1<<0)){steer=1;throttle=.3f;stuckTimer+=Time.fixedDeltaTime;}else stuckTimer=0;
  if(stuckTimer>3){throttle=-1;steer=-1;}if(stuckTimer>6)stuckTimer=0;
  if(dist<22&&Speed<6&&Time.time>nextHit){nextHit=Time.time+7;var a=Game.I.SpawnActor(transform.position+transform.right*2,true,Game.I.wanted.level>=4);a.Panic(p);}
 }
 public void Damage(float amount){if(destroyed)return;health-=amount/armorUpgrade;if(health<=0){destroyed=true;engineOn=false;siren=false;health=0;Effects.Explosion(transform.position,8,65,this);if(driver)driver.Damage(85);foreach(var r in visual.GetComponentsInChildren<Renderer>()){var mp=new MaterialPropertyBlock();mp.SetColor("_BaseColor",new Color(.06f,.055f,.05f));r.SetPropertyBlock(mp);}body.isKinematic=false;body.AddForce(Vector3.up*3,ForceMode.VelocityChange);}}
 void OnCollisionEnter(Collision c){if(c.relativeVelocity.magnitude>5){Damage((c.relativeVelocity.magnitude-4)*2.3f);Game.I.sound.Play("impact",transform.position,.6f);if(driver){driver.Damage(Mathf.Max(0,c.relativeVelocity.magnitude-12)*1.5f);if(c.collider.GetComponentInParent<Vehicle>())Game.I.wanted.Crime(transform.position,8,30);}}var a=c.collider.GetComponentInParent<Actor>();if(a&&c.relativeVelocity.magnitude>4)a.Damage(c.relativeVelocity.magnitude*8,transform.forward*8,driver!=null);}
 public void RemoveDriverModel(){if(driverVisual)Destroy(driverVisual);}
 public void Repair(){health=100;destroyed=false;fireTimer=0;foreach(var r in visual.GetComponentsInChildren<Renderer>())r.SetPropertyBlock(null);Game.I.Notify("VEHICLE REPAIRED");}
 public void Repaint(Color color){foreach(var r in visual.GetComponentsInChildren<Renderer>()){var mats=r.materials;foreach(var m in mats)if(m.name.Contains("Paint")||m.name.Contains("Pearl")||m.name.Contains("Gold"))m.color=color;}Game.I.storedPaint=color;}
 public void DestroyVehicle(){Game.I.vehicles.Remove(this);Destroy(gameObject);}
 void OnDestroy(){if(Game.I)Game.I.vehicles.Remove(this);}
}
}
