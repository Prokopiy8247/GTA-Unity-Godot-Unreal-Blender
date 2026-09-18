using System.Collections.Generic;
using UnityEngine;
namespace Meridian {
public class SoundBank:MonoBehaviour {
 Dictionary<string,AudioClip> clips=new();AudioSource ambience,rain,ocean,radio;int station;
 void Awake(){foreach(var n in new[]{"step","gun","reload","impact","explosion","engine","horn","siren","rotor","skid","launch","ui","wind","rain","ocean","radio"})clips[n]=Synthesize(n);ambience=Loop("wind",transform,.07f,1);rain=Loop("rain",transform,0,1);ocean=Loop("ocean",transform,0,1);radio=Loop("radio",transform,0,1);}
 AudioClip Synthesize(string name){
  const int hz=22050;float duration=name switch{"engine"=>2,"rotor"=>2,"siren"=>4,"horn"=>.6f,"wind"=>4,"rain"=>4,"ocean"=>5,"radio"=>12,"explosion"=>2,"gun"=>.24f,"step"=>.15f,"ui"=>.12f,_=>.55f};
  var data=new float[(int)(hz*duration)];var rng=new System.Random(name.GetHashCode());float low=0;
  for(int i=0;i<data.Length;i++){
   float t=(float)i/hz,n=(float)rng.NextDouble()*2-1;low=Mathf.Lerp(low,n,.06f);float env=Mathf.Exp(-t*10);
   float sample=name switch{
    "engine"=>(Mathf.Sin(t*92*Mathf.PI*2)*.28f+Mathf.Sin(t*184*Mathf.PI*2)*.12f+low*.55f)*(.83f+.17f*Mathf.Sin(t*30)),
    "rotor"=>(low*.7f+Mathf.Sin(t*56)*.15f)*Mathf.Pow(.5f+.5f*Mathf.Sin(t*38),3),
    "siren"=>Mathf.Sin(t*2*Mathf.PI*(630+240*Mathf.Sin(t*Mathf.PI)))*.32f,
    "horn"=>(Mathf.Sin(t*420*2*Mathf.PI)+Mathf.Sin(t*510*2*Mathf.PI))*.2f*Mathf.Clamp01((duration-t)*8),
    "gun"=>(n*.7f+Mathf.Sin(t*92*2*Mathf.PI)*.5f)*Mathf.Exp(-t*24),
    "explosion"=>(low*1.4f+n*.3f+Mathf.Sin(t*43*2*Mathf.PI)*.3f)*Mathf.Exp(-t*2.6f),
    "step"=>(low+n*.2f)*env,
    "impact"=>(low+Mathf.Sin(t*180*Mathf.PI)*.4f)*Mathf.Exp(-t*14),
    "reload"=>n*.3f*Mathf.Exp(-((t-.07f)*(t-.07f))*1800)+n*.35f*Mathf.Exp(-((t-.28f)*(t-.28f))*1900),
    "ui"=>Mathf.Sin(t*760*2*Mathf.PI)*env*.25f,
    "rain"=>low*.65f+n*.04f,
    "wind"=>low*.32f*(.65f+.35f*Mathf.Sin(t*1.5f)),
    "ocean"=>low*(.65f+.3f*Mathf.Sin(t*1.2566f)),
    "radio"=>(Mathf.Sin(t*110*2*Mathf.PI)*.12f+Mathf.Sin(t*165*2*Mathf.PI)*.08f+Mathf.Sin(t*220*2*Mathf.PI)*.04f)*(.5f+.5f*Mathf.Sin(t*Mathf.PI/3)),
    _=>n*.3f*Mathf.Exp(-t*6)};
   data[i]=Mathf.Clamp(sample,-.98f,.98f)*Mathf.Min(1,t*500);
  }
  var clip=AudioClip.Create("Meridian original "+name,data.Length,1,hz,false);clip.SetData(data,0);return clip;
 }
 public void Play(string n,Vector3 p,float volume=1,float pitch=1){if(!clips.TryGetValue(n,out var c))return;var o=new GameObject("Audio "+n);o.transform.position=p;var a=o.AddComponent<AudioSource>();a.clip=c;a.volume=volume;a.pitch=pitch;a.spatialBlend=n=="ui"?0:1;a.minDistance=6;a.maxDistance=150;a.rolloffMode=AudioRolloffMode.Linear;a.Play();Destroy(o,c.length/Mathf.Max(.1f,pitch)+.1f);}
 public AudioSource Loop(string n,Transform parent,float volume,float pitch){var o=new GameObject("Loop "+n);o.transform.SetParent(parent);o.transform.localPosition=Vector3.zero;var a=o.AddComponent<AudioSource>();a.clip=clips[n];a.loop=true;a.volume=volume;a.pitch=pitch;a.spatialBlend=parent==transform?0:1;a.minDistance=5;a.maxDistance=100;a.rolloffMode=AudioRolloffMode.Linear;a.Play();return a;}
 public void CycleRadio(){station=(station+1)%3;radio.pitch=station==1?1:.75f;Game.I.Notify(station==0?"RADIO OFF":station==1?"RADIO / NIGHT CURRENT":"RADIO / LOW TIDE");}
 void Update(){if(!Game.I.ready)return;rain.volume=Game.I.atmosphere.weather>=2&&Game.I.atmosphere.weather!=3? 0.18f:0;ocean.volume=Game.I.player.transform.position.x>1000? 0.15f:0;radio.volume=Game.I.player.vehicle&&station>0? 0.13f:0;}
}
}
