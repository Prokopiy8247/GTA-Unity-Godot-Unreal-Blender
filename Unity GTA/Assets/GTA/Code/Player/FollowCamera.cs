using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.Rendering.Universal;
namespace Meridian {
public class FollowCamera:MonoBehaviour {
 public float yaw=10,pitch=12,shake;public bool firstPerson;Camera cam;Vector3 vel;public Vector3 aimPoint;
 void Awake(){cam=GetComponent<Camera>();cam.nearClipPlane=.08f;cam.farClipPlane=3600;cam.fieldOfView=64;var data=cam.GetUniversalAdditionalCameraData();data.renderPostProcessing=true;data.antialiasing=AntialiasingMode.FastApproximateAntialiasing;}
 void LateUpdate(){
  var g=Game.I;if(!g.player)return;var p=g.player;
  if(!g.paused){var look=InputHub.Look;yaw+=look.x*.13f;pitch=Mathf.Clamp(pitch-look.y*.10f,-55,72);if(InputHub.Down(Key.V))firstPerson=!firstPerson;}
  Vector3 target=p.transform.position+Vector3.up*(p.crouch?1.05f:1.5f);float distance=firstPerson?0:InputHub.Aim?2.15f:4.8f;
  if(p.vehicle){target=p.vehicle.transform.position+Vector3.up*(p.vehicle.IsAir?2:1.35f);distance=firstPerson?0:p.vehicle.IsAir?13:7.3f;if(!InputHub.Aim&&InputHub.Look.sqrMagnitude<.01f&&p.vehicle.Speed>3&&!InputHub.scripted)yaw=Mathf.LerpAngle(yaw,p.vehicle.transform.eulerAngles.y,Time.deltaTime*.6f);}
  var rotation=Quaternion.Euler(pitch,yaw,0);Vector3 shoulder=rotation*Vector3.right*(InputHub.Aim? 0.6f:.35f);
  Vector3 desired=target+shoulder-rotation*Vector3.forward*distance;
  if(distance>0&&Physics.SphereCast(target,.22f,(desired-target).normalized,out var hit,distance,1<<0,QueryTriggerInteraction.Ignore))desired=target+(desired-target).normalized*Mathf.Max(.45f,hit.distance-.2f);
  transform.position=Vector3.SmoothDamp(transform.position,desired,ref vel,.055f);transform.rotation=rotation;
  if(firstPerson){transform.position=target+rotation*Vector3.forward*.18f;transform.position+=Vector3.up*.08f;}
  foreach(var r in p.visual.GetComponentsInChildren<Renderer>())r.enabled=!firstPerson;
  shake=Mathf.MoveTowards(shake,0,Time.deltaTime*1.6f);if(shake>0)transform.position+=Random.insideUnitSphere*shake*.1f;
  float fov=InputHub.Aim?(p.weapons.selected==10?22:48):64+(p.vehicle?Mathf.Min(12,p.vehicle.Speed*.2f):0);cam.fieldOfView=Mathf.Lerp(cam.fieldOfView,fov,Time.deltaTime*8);
  var ray=new Ray(transform.position,transform.forward);aimPoint=Physics.Raycast(ray,out var aim,800,~(1<<8),QueryTriggerInteraction.Ignore)?aim.point:ray.GetPoint(800);
 }
}
}
