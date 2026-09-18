using System.Collections;
using UnityEngine;
using UnityEngine.InputSystem;
namespace Meridian {
public class PlayerMotor:MonoBehaviour {
 public CharacterController controller;public GameObject visual;public Articulation pose;public Weapons weapons;public Vehicle vehicle;
 public float health=100,armor=50,stamina=100,breath=100;public bool dead,crouch,swimming,parachute,scuba,cover;public int outfit;public Vector3 velocity;public float speed;public bool transitioning;
 GameObject chute;Vector3 coverNormal;float stepTimer,impactVelocity;float vertical;float enterUntil;
 public void Initialize() {
  gameObject.layer=8;controller=gameObject.AddComponent<CharacterController>();controller.height=1.78f;controller.center=new(0,.9f,0);controller.radius=.28f;controller.stepOffset=.32f;controller.slopeLimit=52;
  visual=Game.I.Model("Player",transform);pose=visual.AddComponent<Articulation>();weapons=gameObject.AddComponent<Weapons>();weapons.Initialize();SetLayer(visual,8);
 }
 public static void SetLayer(GameObject o,int layer){o.layer=layer;foreach(Transform t in o.transform)SetLayer(t.gameObject,layer);}
 public void Teleport(Vector3 p){controller.enabled=false;transform.position=p;controller.enabled=true;vertical=0;velocity=Vector3.zero;Game.I.world.UpdateSectors(true);}
 void Update(){
  if(!Game.I.ready||dead)return;
  if(vehicle){transform.position=vehicle.transform.TransformPoint(new Vector3(-.38f,.6f,0));if(!Game.I.paused&&InputHub.Down(Key.F))ExitVehicle();return;}
  if(Game.I.paused||transitioning)return;
  if(InputHub.Down(Key.F)){Vehicle nearest=null;float distance=4.5f;foreach(var v in Game.I.vehicles){if(!v||v.destroyed)continue;float d=Vector3.Distance(v.transform.position,transform.position);if(d<distance){nearest=v;distance=d;}}if(nearest)EnterVehicle(nearest);}
  if(InputHub.Down(Key.E)){foreach(var s in Game.I.world.services)if(Vector3.Distance(s.transform.position,transform.position)<10){Game.I.ui.OpenService(s);break;}}
  if(InputHub.Down(Key.C)){crouch=!crouch;controller.height=crouch?1.2f:1.78f;controller.center=new(0,controller.height*.5f,0);}
  if(InputHub.Down(Key.Q))ToggleCover();
  Vector2 input=InputHub.Move;var yaw=Quaternion.Euler(0,Game.I.cameraRig.yaw,0);Vector3 move=yaw*new Vector3(input.x,0,input.y);move=Vector3.ClampMagnitude(move,1);
  bool sprint=InputHub.Held(Key.LeftShift)&&stamina>1&&!crouch&&!InputHub.Aim;
  float target=crouch?1.7f:sprint?7.5f:InputHub.Aim?2.7f:4.1f;speed=Mathf.Lerp(speed,move.magnitude*target,Time.deltaTime*10);
  if(cover){move=Vector3.ProjectOnPlane(move,coverNormal);if(Vector3.Dot(yaw*new Vector3(input.x,0,input.y),coverNormal)>.65f)cover=false;target=1.9f;}
  swimming=transform.position.x>1100&&transform.position.y<.5f;
  if(swimming){
   float lift=InputHub.Lift;vertical=Mathf.Lerp(vertical,lift*2.8f+(transform.position.y<-.45f&&!InputHub.Held(Key.LeftCtrl)&&lift==0? 0.8f:0),Time.deltaTime*3);move*=2.8f;
   bool submerged=transform.position.y<-1.6f;breath=Mathf.Clamp(breath+(submerged&&!scuba?-Time.deltaTime*(3.5f-Game.I.skills[6]*.015f):Time.deltaTime*12),0,100);if(breath<=0)Damage(Time.deltaTime*14);if(submerged)Game.I.Skill(6,Time.deltaTime*.012f);Game.I.Skill(0,Time.deltaTime*.005f);
  }else{
   breath=Mathf.Min(100,breath+Time.deltaTime*15);move*=target;
   if(controller.isGrounded){
    if(impactVelocity<-13)Damage((-impactVelocity-12)*5);
    impactVelocity=0;vertical=-2;
    if(parachute){parachute=false;if(chute)Destroy(chute);}
    if(InputHub.Down(Key.Space))vertical=6.5f;
   }else {vertical-=20*Time.deltaTime;impactVelocity=Mathf.Min(impactVelocity,vertical);}
   if(InputHub.Down(Key.Space)&&!controller.isGrounded&&vertical<-5&&transform.position.y-World.Height(transform.position.x,transform.position.z)>8){parachute=!parachute;if(parachute)chute=Game.I.Model("Parachute",transform);else if(chute)Destroy(chute);}
   if(parachute){vertical=Mathf.Max(vertical,InputHub.Held(Key.LeftShift)?-2.5f:-5);move=yaw*new Vector3(input.x*4,0,7+input.y*3);}
  }
  if(sprint&&move.sqrMagnitude>1){stamina=Mathf.Max(0,stamina-Time.deltaTime*(9-Game.I.skills[0]*.035f));Game.I.Skill(0,Time.deltaTime*.01f);}else stamina=Mathf.Min(100,stamina+Time.deltaTime*13);
  if(crouch&&move.sqrMagnitude>.1f)Game.I.Skill(3,Time.deltaTime*.005f);
  velocity=new(move.x,vertical,move.z);controller.Move(velocity*Time.deltaTime);
  if(InputHub.Aim)transform.rotation=Quaternion.Slerp(transform.rotation,yaw,Time.deltaTime*15);
  else if(move.sqrMagnitude>.05f)transform.rotation=Quaternion.Slerp(transform.rotation,Quaternion.LookRotation(move),Time.deltaTime*12);
  pose.Animate(speed,InputHub.Aim||weapons.firing,crouch,swimming,parachute);
  if(controller.isGrounded&&speed>1){stepTimer-=Time.deltaTime;if(stepTimer<=0){Game.I.sound.Play("step",transform.position,crouch? 0.08f:.22f,Random.Range(.9f,1.2f));stepTimer=sprint? 0.27f:.4f;}}
  if(transform.position.y<-45||Mathf.Abs(transform.position.x)>2900||Mathf.Abs(transform.position.z)>2900){Teleport(new(9,1,20));Game.I.Notify("Returned to the accessible coast");}
  if(InputHub.Down(Key.G))TryVault();
 }
 void ToggleCover(){
  if(cover){cover=false;return;}
  if(Physics.Raycast(transform.position+Vector3.up*.7f,transform.forward,out var hit,1.5f,~(1<<8))){cover=true;coverNormal=hit.normal;crouch=hit.collider.bounds.size.y<1.6f;Game.I.Notify("COVER  /  Q to leave");}
 }
 void TryVault(){if(Physics.Raycast(transform.position+Vector3.up*.5f,transform.forward,out var hit,1.2f,~(1<<8))&&!Physics.Raycast(transform.position+Vector3.up*1.65f,transform.forward,1.5f,~(1<<8))){controller.Move(Vector3.up*1.1f+transform.forward*1.3f);vertical=2;}}
 public void EnterVehicle(Vehicle v,bool immediate=false) {if(vehicle||transitioning||v.destroyed)return;if(immediate)FinishEnter(v);else StartCoroutine(EnterRoutine(v));}
 IEnumerator EnterRoutine(Vehicle v){transitioning=true;Vector3 a=transform.position,b=v.transform.TransformPoint(new Vector3(-1.35f,0,0));float t=0;while(t<.4f){t+=Time.deltaTime;controller.Move((Vector3.Lerp(a,b,t/.4f)-transform.position));pose.Animate(2,false,false,false,false);yield return null;}FinishEnter(v);transitioning=false;}
 void FinishEnter(Vehicle v){
  if(v.trafficControlled){var a=Game.I.SpawnActor(v.transform.TransformPoint(new Vector3(1.8f,.1f,0)));a.Panic(transform.position);Game.I.wanted.Crime(transform.position,22,25);v.trafficControlled=false;}
  if(v.index==7)Game.I.wanted.Crime(transform.position,40,80,true);
  v.RemoveDriverModel();vehicle=v;v.driver=this;v.body.isKinematic=false;controller.enabled=false;visual.SetActive(false);v.engineOn=true;cover=false;weapons.HideModel();Game.I.Notify(v.spec.label+"  /  F EXIT");
 }
 public void ExitVehicle(bool force=false) {
  if(!vehicle)return;var v=vehicle;if(!force&&v.Speed>24&&!v.IsAir){Game.I.Notify("Slow down to exit");return;}
  Vector3 p=v.transform.TransformPoint(new Vector3(-2.0f,.2f,0));if(Physics.CheckSphere(p+Vector3.up*.8f,.3f,1<<0))p=v.transform.TransformPoint(new Vector3(2.1f,.2f,0));
  v.driver=null;vehicle=null;controller.enabled=true;visual.SetActive(true);Teleport(p);vertical=v.body.linearVelocity.y;weapons.Equip(weapons.selected);
 }
 public void Damage(float amount){if(Game.I.god||dead)return;float absorbed=Mathf.Min(armor,amount*.65f);armor-=absorbed;health-=amount-absorbed;Game.I.ui.hurt=1;if(health<=0){health=0;Game.I.Respawn();}}
 public void SetOutfit(int i){outfit=i;Color[] c={new(.09f,.13f,.18f),new(.45f,.12f,.075f),new(.22f,.29f,.20f),new(.55f,.54f,.47f)};foreach(var r in visual.GetComponentsInChildren<Renderer>()){var mats=r.materials;foreach(var m in mats)if(m.name.Contains("Jacket"))m.color=c[Mathf.Abs(i)%c.Length];}}
}
public class Articulation:MonoBehaviour {
 Transform leftArm,rightArm,leftLeg,rightLeg,head;float phase;
 void Awake(){foreach(var t in GetComponentsInChildren<Transform>()){if(t.name.StartsWith("Arm_L"))leftArm=t;if(t.name.StartsWith("Arm_R"))rightArm=t;if(t.name.StartsWith("Leg_L"))leftLeg=t;if(t.name.StartsWith("Leg_R"))rightLeg=t;if(t.name=="Head"||t.name.StartsWith("Head."))head=t;}}
 public void Animate(float speed,bool aim,bool crouch,bool swim,bool chute){
  phase+=Time.deltaTime*(speed>0.1f?speed*2.3f:1);float swing=Mathf.Sin(phase)*Mathf.Min(32,speed*7);
  Set(leftLeg,swing+(crouch?22:0),0);Set(rightLeg,-swing+(crouch?22:0),0);
  Set(leftArm,aim?-70:swim?-120+Mathf.Sin(phase)*50:chute?-155:-swing*.75f,chute?-18:0);Set(rightArm,aim?-87:swim?-120-Mathf.Sin(phase)*50:chute?-155:swing*.75f,chute?18:0);
  transform.localPosition=new(0,crouch?-.3f:Mathf.Abs(Mathf.Sin(phase))*Mathf.Min(speed*.005f,.025f),0);
 }
 void Set(Transform t,float x,float z){if(t)t.localRotation=Quaternion.Slerp(t.localRotation,Quaternion.Euler(x,0,z),Time.deltaTime*14);}
}
}
