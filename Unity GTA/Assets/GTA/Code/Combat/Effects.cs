using System.Collections.Generic;
using UnityEngine;
namespace Meridian {
public class EffectLifetime:MonoBehaviour {public float life;void Update(){life-=Time.deltaTime;if(life<=0)Destroy(gameObject);}}
public static class Effects {
 static int active;public static void Burst(Vector3 p,Color color,int count,float speed,float life=.5f){
  if(active>110)return;
  var o=new GameObject("Particle effect");o.transform.position=p;var ps=o.AddComponent<ParticleSystem>();ps.Stop(true,ParticleSystemStopBehavior.StopEmittingAndClear);var main=ps.main;main.duration=life;main.loop=false;main.startLifetime=life;main.startSpeed=speed;main.startSize=life>1? 0.6f:.08f;main.startColor=color;main.gravityModifier=life>1?-.08f:.25f;main.maxParticles=50;main.simulationSpace=ParticleSystemSimulationSpace.World;
  var em=ps.emission;em.enabled=false;var sh=ps.shape;sh.shapeType=ParticleSystemShapeType.Sphere;sh.radius=.08f;
  var col=ps.colorOverLifetime;col.enabled=true;var g=new Gradient();g.SetKeys(new[]{new GradientColorKey(color,0),new GradientColorKey(color,1)},new[]{new GradientAlphaKey(1,0),new GradientAlphaKey(0,1)});col.color=g;
  ps.GetComponent<ParticleSystemRenderer>().sharedMaterial=Game.I.catalog.particle;ps.Play();ps.Emit(count);var ttl=o.AddComponent<EffectLifetime>();ttl.life=life+.2f;active++;o.AddComponent<EffectCounter>();
 }
 public static void Released(){active=Mathf.Max(0,active-1);}
 public static void Tracer(Vector3 a,Vector3 b){var o=new GameObject("Tracer");var lr=o.AddComponent<LineRenderer>();lr.sharedMaterial=Game.I.catalog.particle;lr.positionCount=2;lr.SetPosition(0,a);lr.SetPosition(1,b);lr.startWidth=.018f;lr.endWidth=.007f;lr.startColor=new(1,.84f,.5f,.65f);lr.endColor=new(1,.84f,.5f,0);o.AddComponent<EffectLifetime>().life=.055f;}
 public static void Explosion(Vector3 p,float radius,float damage,Vehicle source=null){
  Burst(p,new Color(1,.35f,.04f),45,9,1.2f);Burst(p,Color.gray,30,4,3);Game.I.sound.Play("explosion",p,1);Game.I.cameraRig.shake=1;Game.I.population.Panic(p,160);Game.I.wanted.Crime(p,25,240);
  var seen=new HashSet<Object>();
  foreach(var c in Physics.OverlapSphere(p,radius)){
   if(c.attachedRigidbody&&!c.attachedRigidbody.isKinematic)c.attachedRigidbody.AddExplosionForce(damage*50,p,radius,2);
   var a=c.GetComponentInParent<Actor>();if(a&&seen.Add(a))a.Damage(damage*(1-Vector3.Distance(a.transform.position,p)/radius),(a.transform.position-p).normalized*8,true);
   var v=c.GetComponentInParent<Vehicle>();if(v&&v!=source&&seen.Add(v))v.Damage(damage*.6f*(1-Vector3.Distance(v.transform.position,p)/radius));
  }
  var player=Game.I.player;if(Vector3.Distance(player.transform.position,p)<radius)player.Damage(damage*(1-Vector3.Distance(player.transform.position,p)/radius));
 }
}
public class EffectCounter:MonoBehaviour {void OnDestroy(){Effects.Released();}}
}
