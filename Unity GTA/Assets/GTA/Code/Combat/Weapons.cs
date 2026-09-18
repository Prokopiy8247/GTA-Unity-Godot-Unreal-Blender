using System;
using System.Collections;
using UnityEngine;
using UnityEngine.InputSystem;
namespace Meridian {
[Serializable] public class WeaponDef {
 public string name,model;public int capacity;public float damage,rate,range,spread;public int pellets;
 public WeaponDef(string n,string m,int c,float d,float r,float reach,float sp,int p=1){name=n;model=m;capacity=c;damage=d;rate=r;range=reach;spread=sp;pellets=p;}
}
public class Weapons:MonoBehaviour {
 public static WeaponDef[] Defs={
 new("Unarmed","",1,18,.55f,2,.01f),new("Field knife","Knife",1,42,.5f,2,.01f),new("Hardwood baton","Baton",1,36,.7f,2.3f,.02f),
 new("P9 service pistol","Pistol",12,26,.22f,160,.012f),new("H45 heavy pistol","HeavyPistol",7,46,.35f,180,.018f),
 new("S9 compact","SMG",28,20,.085f,150,.026f),new("P12 pump","Shotgun",8,13,.8f,60,.075f,8),
 new("AR36 rifle","Rifle",30,30,.105f,320,.015f),new("C20 carbine","Carbine",24,34,.13f,300,.012f),
 new("M7 marksman","Marksman",12,66,.45f,600,.004f),new("L90 precision","Sniper",5,120,1.1f,900,.001f),
 new("Fragment grenade","Grenade",6,95,1.2f,70,.01f),new("R80 launcher","Launcher",1,160,1.5f,500,.005f)};
 public int selected=3;public int[] ammo,reserve;public bool[] owned;public bool suppressor,extended,grip,flashlight;public bool firing,reloading;public int shotsFired,hits;GameObject model;float nextShot,reloadUntil,firingUntil;
 public void Initialize(){ammo=new int[Defs.Length];reserve=new int[Defs.Length];owned=new bool[Defs.Length];for(int i=0;i<Defs.Length;i++){ammo[i]=Defs[i].capacity;reserve[i]=Defs[i].capacity*6;owned[i]=i<4;}Equip(3);}
 public void Equip(int i){
  if(i<0||i>=Defs.Length||!owned[i])return;selected=i;reloading=false;
  if(model)Destroy(model);if(Defs[i].model!=""){model=Game.I.Model(Defs[i].model,transform);model.transform.localPosition=new(.23f,1.13f,.33f);PlayerMotor.SetLayer(model,8);}
 }
 public void HideModel(){if(model)model.SetActive(false);}
 public void GiveAll(){for(int i=0;i<Defs.Length;i++){owned[i]=true;ammo[i]=Capacity(i);reserve[i]=Capacity(i)*10;}Game.I.Notify("ALL WEAPONS / AMMO");}
 public int Capacity(int i)=>Defs[i].capacity*(extended&&i>2&&i<11?2:1);
 void Update(){
  if(!Game.I.ready||Game.I.player.dead)return;firing=Time.time<firingUntil;
  if(reloading&&Time.time>=reloadUntil){int n=Mathf.Min(Capacity(selected)-ammo[selected],reserve[selected]);ammo[selected]+=n;reserve[selected]-=n;reloading=false;}
  if(Game.I.paused)return;
  if(InputHub.Scroll!=0){int dir=InputHub.Scroll>0?1:-1;for(int k=1;k<=Defs.Length;k++){int i=(selected+dir*k+Defs.Length*2)%Defs.Length;if(owned[i]){Equip(i);break;}}}
  Key[] keys={Key.Digit1,Key.Digit2,Key.Digit3,Key.Digit4,Key.Digit5,Key.Digit6,Key.Digit7,Key.Digit8,Key.Digit9};
  for(int i=0;i<keys.Length;i++)if(InputHub.Down(keys[i]))Equip(i);
  if(InputHub.Down(Key.R))Reload();
  bool restricted=Game.I.player.vehicle&&selected!=3&&selected!=4&&selected!=5&&selected!=11;
  if(InputHub.Fire&&!restricted)TryFire();
  if(model){model.SetActive(!Game.I.player.vehicle);if(!Game.I.player.vehicle)model.transform.localRotation=Quaternion.Euler(InputHub.Aim?-Game.I.cameraRig.pitch:0,0,reloading?Mathf.Sin(Time.time*8)*25:0);}
 }
 public void Reload(){if(reloading||ammo[selected]>=Capacity(selected)||reserve[selected]<=0||selected<3)return;reloading=true;reloadUntil=Time.time+1.65f-Game.I.skills[1]*.004f;Game.I.sound.Play("reload",transform.position,.5f);}
 public bool TryFire(){
  var p=Game.I.player;if(Time.time<nextShot||reloading||p.dead)return false;var def=Defs[selected];
  if(selected>2&&ammo[selected]<=0){Reload();return false;}
  nextShot=Time.time+def.rate;firingUntil=Time.time+.16f;if(selected>2)ammo[selected]--;shotsFired++;Game.I.ui.rangeShots+=Game.I.ui.rangeTime>0?1:0;Game.I.Skill(selected<3?2:1,.018f);
  Vector3 origin=p.vehicle?p.vehicle.transform.position+Vector3.up*1.35f+Game.I.cameraRig.transform.right*1.15f:transform.position+Vector3.up*1.35f+transform.forward*.45f;
  Vector3 aim=(Game.I.cameraRig.aimPoint-origin).normalized;
  if(selected<3){origin=transform.position+Vector3.up;aim=transform.forward;var colliders=Physics.OverlapSphere(origin+aim*1.1f,.9f,(1<<10)|(1<<9));foreach(var c in colliders){var a=c.GetComponentInParent<Actor>();if(a){float damage=def.damage;if(p.crouch&&Vector3.Dot(a.transform.forward,transform.forward)>.5f)damage=150;a.Damage(damage,aim*6,true);break;}}Game.I.sound.Play("impact",origin,.35f);return true;}
  float noise=suppressor?20:140;if(Game.I.ui.rangeTime<=0)Game.I.wanted.Crime(origin,selected>=11?28:6,noise);Game.I.population.Panic(origin,noise);
  Game.I.sound.Play(selected>=11?"launch":"gun",origin,suppressor? 0.2f:.7f,selected==6? 0.65f:1);
  Game.I.cameraRig.shake=selected==6? 0.75f:.22f;Effects.Burst(origin,new Color(1,.66f,.2f),suppressor?3:8,2,.08f);
  if(selected>=11){var o=Game.I.Model(def.model);o.transform.position=origin+aim*.6f;o.transform.rotation=Quaternion.LookRotation(aim);o.AddComponent<SphereCollider>().radius=.08f;var rb=o.AddComponent<Rigidbody>();rb.mass=.4f;rb.useGravity=selected==11;rb.collisionDetectionMode=CollisionDetectionMode.ContinuousDynamic;rb.linearVelocity=aim*(selected==11?22:70)+(selected==11?Vector3.up*5:Vector3.zero);var proj=o.AddComponent<ExplosiveProjectile>();proj.fuse=selected==11?2.8f:6;proj.damage=def.damage;proj.rocket=selected==12;return true;}
  for(int i=0;i<def.pellets;i++){
   float spread=def.spread*(InputHub.Aim? 0.45f:1)*(grip? 0.7f:1)*(p.vehicle?2:1);
   Vector3 dir=(aim+UnityEngine.Random.insideUnitSphere*spread).normalized;
   var all=Physics.RaycastAll(origin,dir,def.range,~(1<<8),QueryTriggerInteraction.Ignore);Array.Sort(all,(a,b)=>a.distance.CompareTo(b.distance));Vector3 end=origin+dir*def.range;
   foreach(var hit in all){
    if(p.vehicle&&hit.collider.GetComponentInParent<Vehicle>()==p.vehicle)continue;
    end=hit.point;var actor=hit.collider.GetComponentInParent<Actor>();var car=hit.collider.GetComponentInParent<Vehicle>();var target=hit.collider.GetComponentInParent<RangeTarget>();
    if(actor){bool headshot=hit.point.y-actor.transform.position.y>1.45f;actor.Damage(def.damage*(headshot?2.5f:1),dir*4,true);hits++;Game.I.ui.hitMarker=.25f;}
    if(car){car.Damage(def.damage*.65f);hits++;Game.I.ui.hitMarker=.25f;}
    if(target){target.Hit();hits++;Game.I.ui.hitMarker=.25f;}
    Effects.Burst(hit.point+hit.normal*.025f,car?new Color(1,.64f,.25f):new Color(.65f,.6f,.5f),7,car?3:1.2f,.3f);
    if(hit.rigidbody&&!hit.rigidbody.isKinematic)hit.rigidbody.AddForceAtPosition(dir*120,hit.point);
    break;
   }
   Effects.Tracer(origin,end);
  }return true;
 }
}
public class ExplosiveProjectile:MonoBehaviour {
 public float fuse=3,damage=100;public bool rocket;bool exploded;
 void Update(){fuse-=Time.deltaTime;if(fuse<=0)Boom();if(rocket&&Time.frameCount%4==0)Effects.Burst(transform.position,Color.gray,2,.4f,.8f);}
 void OnCollisionEnter(Collision c){if(rocket)Boom();}
 void Boom(){if(exploded)return;exploded=true;Effects.Explosion(transform.position,selectedRadius(),damage);Destroy(gameObject);}
 float selectedRadius()=>rocket?11:8;
}
}
