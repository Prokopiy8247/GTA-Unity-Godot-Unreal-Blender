using System.Collections;
using UnityEngine;
namespace Meridian {
public class Actor:MonoBehaviour {
 public bool police,tactical,dead,panicked,reporting;public float health=100;public CharacterController controller;public GameObject visual;public Articulation pose;public Vector3 target,threat;
 float rethink,fireAt,panicUntil,reportUntil;int corner,magazine=12;float reload;Vector3 home;public float age;
 public void Initialize(){
  gameObject.layer=10;controller=gameObject.AddComponent<CharacterController>();controller.height=1.76f;controller.center=new(0,.9f,0);controller.radius=.28f;controller.stepOffset=.3f;
  visual=Game.I.Model(police?(tactical?"Tactical":"Officer"):(Random.value<.5f?"Pedestrian_M":"Pedestrian_F"),transform);PlayerMotor.SetLayer(visual,10);pose=visual.AddComponent<Articulation>();
  if(!police){Color clothes=Color.HSVToRGB(Random.value,Random.Range(.15f,.55f),Random.Range(.18f,.55f));foreach(var r in visual.GetComponentsInChildren<Renderer>())foreach(var m in r.materials)if(m.name.Contains("Jacket"))m.color=clothes;}
  if(police){var gun=Game.I.Model(tactical?"Rifle":"Pistol",visual.transform);gun.transform.localPosition=new(.23f,1.12f,.34f);PlayerMotor.SetLayer(gun,10);health=tactical?150:100;}
  home=transform.position;NewSidewalkTarget();
 }
 void NewSidewalkTarget(){int bx=Mathf.FloorToInt(transform.position.x/128),bz=Mathf.FloorToInt(transform.position.z/128);corner=(corner+1)%4;target=new(bx*128+(corner<2?13:115),.2f,bz*128+(corner==0||corner==3?13:115));}
 public void Panic(Vector3 p){if(dead)return;panicked=true;threat=p;panicUntil=Time.time+12;}
 public bool CanSee(Vector3 p,float range=100) {Vector3 eye=transform.position+Vector3.up*1.5f,end=p+Vector3.up;return Vector3.Distance(eye,end)<range&&!Physics.Linecast(eye,end,1<<0,QueryTriggerInteraction.Ignore);}
 void Update(){
  if(!Game.I.ready||dead||Game.I.paused)return;age+=Time.deltaTime;var player=Game.I.player;if(!player)return;float dist=Vector3.Distance(transform.position,player.transform.position);if(dist>330)return;
  bool fighting=police&&Game.I.wanted.level>0;bool aim=false;
  if(Time.time>rethink){rethink=Time.time+(dist>130? 0.8f:.23f);
   if(fighting){Vector3 known=Game.I.wanted.visible?player.transform.position:Game.I.wanted.lastKnown;target=known;
    if(dist<22&&Game.I.wanted.visible)target=transform.position+Vector3.Cross((player.transform.position-transform.position).normalized,Vector3.up)*((Mathf.Abs(Mathf.RoundToInt(home.x))%2)*2-1)*3;
   } else if(panicked&&Time.time<panicUntil){Vector3 away=transform.position-threat;away.y=0;target=transform.position+away.normalized*12;}else{panicked=false;if(Vector3.Distance(transform.position,target)<2)NewSidewalkTarget();}
  }
  Vector3 delta=target-transform.position;delta.y=0;Vector3 direction=delta.normalized;
  bool blocked=Physics.SphereCast(transform.position+Vector3.up*.8f,.25f,direction,out var hit,1.4f,1<<0,QueryTriggerInteraction.Ignore);
  if(blocked){direction=Vector3.ProjectOnPlane(direction,hit.normal).normalized;if(direction.sqrMagnitude<.1f)direction=Vector3.Cross(hit.normal,Vector3.up);}
  float speed=fighting?3.1f:panicked?4.5f:1.25f;if(delta.magnitude<.8f)speed=0;
  if(fighting&&dist<45&&CanSee(player.transform.position,80)){
   aim=true;transform.rotation=Quaternion.Slerp(transform.rotation,Quaternion.LookRotation((player.transform.position-transform.position).normalized),Time.deltaTime*6);
   if(Game.I.wanted.level>=2&&!player.dead&&Time.time>fireAt){
    if(magazine<=0){if(reload==0)reload=Time.time+2.4f;if(Time.time>reload){magazine=12;reload=0;}}
    else{fireAt=Time.time+(tactical? 0.38f:.8f);magazine--;Vector3 origin=transform.position+Vector3.up*1.35f+transform.forward*.4f;Effects.Tracer(origin,player.transform.position+Vector3.up);Effects.Burst(origin,new Color(1,.7f,.3f),4,1,.09f);Game.I.sound.Play("gun",origin,.35f,1.15f);if(Random.value<(dist<15? 0.6f:.23f))player.Damage(tactical?9:6);}
   }
   if(dist<9)speed=0;
  }else if(direction.sqrMagnitude>.01f)transform.rotation=Quaternion.Slerp(transform.rotation,Quaternion.LookRotation(direction),Time.deltaTime*5);
  controller.Move((direction*speed+Vector3.down*5)*Time.deltaTime);pose.Animate(speed,aim,false,false,false);
  if(reporting&&Time.time>reportUntil)reporting=false;
 }
 public void StartReport(){reporting=true;reportUntil=Time.time+3;}
 public void Damage(float amount,Vector3 force,bool playerCrime){
  if(dead)return;health-=amount;Panic(Game.I.player.transform.position);
  if(playerCrime)Game.I.wanted.Crime(transform.position,police?36:18,50,police);
  if(health<=0){dead=true;reporting=false;controller.enabled=false;if(playerCrime){Game.I.cash+=Random.Range(15,80);Game.I.wanted.Crime(transform.position,police?48:26,50,police);}Ragdoll(force);Destroy(gameObject,35);}
 }
 void Ragdoll(Vector3 force){
  Rigidbody central=null;foreach(Transform t in visual.transform){
   var mf=t.GetComponent<MeshFilter>();if(!mf)continue;
   var rb=t.gameObject.AddComponent<Rigidbody>();rb.mass=t.name.StartsWith("Body")?25:7;rb.collisionDetectionMode=CollisionDetectionMode.Continuous;var c=t.gameObject.AddComponent<BoxCollider>();c.center=mf.sharedMesh.bounds.center;c.size=Vector3.Max(mf.sharedMesh.bounds.size*.76f,Vector3.one*.06f);if(t.name.StartsWith("Body"))central=rb;
  }
  if(!central)central=visual.GetComponentInChildren<Rigidbody>();
  foreach(var rb in visual.GetComponentsInChildren<Rigidbody>()){if(rb!=central){var j=rb.gameObject.AddComponent<CharacterJoint>();j.connectedBody=central;j.enablePreprocessing=false;var lim=new SoftJointLimit{limit=40};j.swing1Limit=lim;j.swing2Limit=lim;}rb.AddForce(force,ForceMode.VelocityChange);}
 }
 void OnDestroy(){if(Game.I)Game.I.actors.Remove(this);}
}
}
