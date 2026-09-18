using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
namespace Meridian {
public class Atmosphere:MonoBehaviour {
 public float hour=14.2f;public int weather;public static string[] WeatherNames={"Clear","Overcast","Rain","Fog","Storm"};public Light sun;Light fill;ParticleSystem rain;Material sky;float nextLights,lightningAt;public bool cycle=true;
 public void Initialize(){
  var go=new GameObject("Sun");sun=go.AddComponent<Light>();sun.type=LightType.Directional;sun.shadows=LightShadows.Soft;sun.shadowStrength=.85f;sun.shadowBias=.04f;RenderSettings.sun=sun;var fillObj=new GameObject("Sky fill");fill=fillObj.AddComponent<Light>();fill.type=LightType.Directional;fill.shadows=LightShadows.None;fill.color=new Color(.62f,.73f,.86f);fill.transform.rotation=Quaternion.Euler(45,315,0);
  sky=new Material(Shader.Find("Skybox/Procedural"));sky.SetFloat("_SunSize",.025f);sky.SetFloat("_AtmosphereThickness",1.05f);sky.SetColor("_GroundColor",new Color(.22f,.25f,.27f));RenderSettings.skybox=sky;RenderSettings.ambientMode=AmbientMode.Trilight;
  var v=new GameObject("World grade").AddComponent<Volume>();v.isGlobal=true;v.profile=ScriptableObject.CreateInstance<VolumeProfile>();
  var tone=v.profile.Add<Tonemapping>();tone.mode.Override(TonemappingMode.ACES);
  var bloom=v.profile.Add<Bloom>();bloom.intensity.Override(.18f);bloom.threshold.Override(1.2f);
  var color=v.profile.Add<ColorAdjustments>();color.postExposure.Override(.6f);color.contrast.Override(13);color.saturation.Override(-8);
  var vignette=v.profile.Add<Vignette>();vignette.intensity.Override(.18f);vignette.smoothness.Override(.55f);
  var ro=new GameObject("Local rain");rain=ro.AddComponent<ParticleSystem>();rain.Stop(true,ParticleSystemStopBehavior.StopEmittingAndClear);var main=rain.main;main.loop=true;main.startLifetime=1.4f;main.startSpeed=26;main.startSize=.028f;main.maxParticles=3500;main.simulationSpace=ParticleSystemSimulationSpace.World;main.startColor=new Color(.7f,.8f,.9f,.4f);
  var shape=rain.shape;shape.shapeType=ParticleSystemShapeType.Box;shape.scale=new(45,45,1);var em=rain.emission;em.rateOverTime=1400;
  var rend=rain.GetComponent<ParticleSystemRenderer>();rend.renderMode=ParticleSystemRenderMode.Stretch;rend.lengthScale=8;rend.velocityScale=.04f;rend.sharedMaterial=Game.I.catalog.particle;ro.transform.rotation=Quaternion.Euler(90,0,0);
  SetWeather(0);Apply();
 }
 public void SetWeather(int w){weather=Mathf.Clamp(w,0,4);if(rain){if(weather==2||weather==4)rain.Play();else rain.Stop();}if(Game.I.catalog.asphalt)Game.I.catalog.asphalt.SetFloat("_Smoothness",weather==2||weather==4? 0.72f:.2f);}
 void Update(){if(!sun||!Game.I.ready)return;if(cycle&&!Game.I.paused)hour=Mathf.Repeat(hour+Time.deltaTime*.007f,24);Apply();if(rain)rain.transform.position=Game.I.player.transform.position+Vector3.up*22;if(weather==4&&Time.time>lightningAt){lightningAt=Time.time+Random.Range(9,22);Game.I.sound.Play("explosion",Game.I.player.transform.position+Vector3.up*100,.35f,.55f);sun.intensity=3;}}
 void Apply(){
  bool night=hour<6||hour>19;float daylight=Mathf.Clamp01(Mathf.Sin((hour-6)/12*Mathf.PI));float cloud=weather==0?1:weather==1? 0.72f:weather==3? 0.48f:.4f;
  if(fill)fill.intensity=.08f+daylight*.7f;
  sun.transform.rotation=Quaternion.Euler((hour-6)*15,135,0);sun.intensity=(.07f+daylight*2.1f)*cloud;sun.color=Color.Lerp(new Color(1,.62f,.34f),new Color(1,.96f,.87f),Mathf.Clamp01(daylight*2));
  sky.SetFloat("_Exposure",night? 0.18f:.7f+daylight*.45f);sky.SetColor("_SkyTint",weather==0?new Color(.46f,.54f,.61f):new Color(.45f,.46f,.48f));sky.SetFloat("_AtmosphereThickness",weather==3?2.5f:weather==0?1:1.5f);
  RenderSettings.ambientSkyColor=Color.Lerp(new Color(.045f,.065f,.12f),new Color(.49f,.57f,.64f),daylight*cloud);
  RenderSettings.ambientEquatorColor=Color.Lerp(new Color(.035f,.04f,.07f),new Color(.32f,.36f,.38f),daylight);
  var ambient=new UnityEngine.Rendering.SphericalHarmonicsL2();ambient.AddAmbientLight(Color.Lerp(new Color(.075f,.095f,.14f),new Color(.43f,.48f,.53f),daylight));RenderSettings.ambientProbe=ambient;
  RenderSettings.ambientGroundColor=new Color(.13f,.12f,.11f)*(.2f+daylight*.7f);
  RenderSettings.fog=true;RenderSettings.fogMode=FogMode.ExponentialSquared;RenderSettings.fogDensity=weather==3? 0.006f:weather==4? 0.003f:weather==2? 0.0018f:.00055f;
  RenderSettings.fogColor=Color.Lerp(new Color(.035f,.05f,.08f),weather==0?new Color(.58f,.67f,.72f):new Color(.39f,.44f,.48f),daylight);
  if(Game.I.player&&Game.I.player.transform.position.x>1100&&Game.I.cameraRig&&Game.I.cameraRig.transform.position.y<-.35f){RenderSettings.fogColor=new(.035f,.18f,.2f);RenderSettings.fogDensity=.10f;}
  if(Time.time>nextLights&&Game.I.player){nextLights=Time.time+1;foreach(var l in Game.I.world.lamps)if(l)l.enabled=night&&Vector3.Distance(l.transform.position,Game.I.player.transform.position)<160;}
 }
}
}
