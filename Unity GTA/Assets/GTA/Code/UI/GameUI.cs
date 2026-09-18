using UnityEngine;
using UnityEngine.InputSystem;
namespace Meridian {
public class GameUI:MonoBehaviour {
 public string panel="",death="";public float hurt,hitMarker,rangeTime;public int rangeHits,rangeShots;public bool showFPS=true;public float fps;public Vector3 waypoint;public bool hasWaypoint;
 int tab;Vector2 scroll;ServicePoint service;float smoothedDelta=.016f;GUIStyle large,medium,small,tiny,button;Texture2D white;Color ink=new(.035f,.055f,.075f,.94f),accent=new(.40f,.82f,.82f),muted=new(.65f,.73f,.77f);
 void Update(){
  smoothedDelta=Mathf.Lerp(smoothedDelta,Time.unscaledDeltaTime,.035f);fps=1/Mathf.Max(.0001f,smoothedDelta);hurt=Mathf.Max(0,hurt-Time.unscaledDeltaTime);hitMarker=Mathf.Max(0,hitMarker-Time.unscaledDeltaTime);
  if(rangeTime>0){rangeTime-=Time.deltaTime;if(rangeTime<=0)Game.I.Notify("RANGE COMPLETE  /  "+rangeHits+" HITS  /  "+(rangeShots==0?0:Mathf.RoundToInt(100f*rangeHits/rangeShots))+"% ACCURACY");}
 }
 void Styles(){
  if(white)return;white=Texture2D.whiteTexture;
  large=new GUIStyle(GUI.skin.label){fontSize=30,fontStyle=FontStyle.Bold,normal={textColor=Color.white}};
  medium=new GUIStyle(GUI.skin.label){fontSize=18,normal={textColor=Color.white}};
  small=new GUIStyle(GUI.skin.label){fontSize=14,normal={textColor=muted}};
  tiny=new GUIStyle(GUI.skin.label){fontSize=11,normal={textColor=muted}};
  button=new GUIStyle(GUI.skin.button){fontSize=15,alignment=TextAnchor.MiddleLeft,padding=new RectOffset(14,8,5,5),normal={textColor=Color.white,background=Texture2D.grayTexture},hover={textColor=Color.white,background=Texture2D.whiteTexture}};
 }
 void Rect(float x,float y,float w,float h,Color c){GUI.color=c;GUI.DrawTexture(new Rect(x,y,w,h),white);GUI.color=Color.white;}
 void Text(string s,float x,float y,GUIStyle style=null){GUI.Label(new Rect(x,y,1000,50),s,style??small);}
 bool Button(string s,float x,float y,float w=240,float h=38){GUI.backgroundColor=new Color(.12f,.22f,.26f);bool b=GUI.Button(new Rect(x,y,w,h),s,button);GUI.backgroundColor=Color.white;return b;}
 public void OpenService(ServicePoint s){service=s;panel=s.kind.ToString().ToLower();Game.I.Pause(true);scroll=Vector2.zero;}
 void Close(){panel="";Game.I.Pause(false);}
 void OnGUI(){
  if(!Game.I.ready)return;Styles();GUI.matrix=Matrix4x4.TRS(Vector3.zero,Quaternion.identity,new Vector3(Screen.width/1600f,Screen.height/900f,1));var g=Game.I;var p=g.player;var w=p.weapons;
  Rect(27,24,310,60,ink);Rect(27,24,3,60,accent);Text("MERIDIAN  /  COAST",43,30,medium);Text(g.world.District(p.transform.position)+"   "+FormatTime(g.atmosphere.hour),44,59,tiny);
  string stars="";for(int i=0;i<5;i++)stars+=i<g.wanted.level?"★ ":"☆ ";
  GUI.color=g.wanted.state=="SEARCH"&&Time.unscaledTime%1<.5f?new Color(.4f,.6f,.7f):Color.white;Text(stars,1320,24,large);GUI.color=Color.white;Text(g.wanted.state,1440,62,tiny);Text("$ "+Mathf.RoundToInt(g.cash).ToString("N0"),1350,93,medium);
  DrawMap(new Rect(28,644,236,194),false);
  Bar(28,850,236,6,p.health/100,new Color(.40f,.79f,.65f));Bar(28,860,236,4,p.armor/100,new Color(.46f,.68f,.9f));Bar(28,868,236,3,p.stamina/100,new Color(.94f,.76f,.40f));
  if(p.swimming)Bar(28,879,236,4,p.breath/100,new Color(.4f,.9f,1));
  Rect(1290,789,282,86,ink);Text(Weapons.Defs[w.selected].name.ToUpperInvariant(),1307,798,small);Text(w.selected<3?"MELEE":w.ammo[w.selected].ToString("00")+"  /  "+w.reserve[w.selected],1306,822,large);
  if(w.reloading)Text("RELOADING",1445,852,tiny);
  if(p.vehicle){Text(Mathf.RoundToInt(p.vehicle.Speed*3.6f).ToString("000")+" KM/H",1297,728,large);Text(p.vehicle.spec.label.ToUpperInvariant(),1300,762,tiny);Bar(1295,782,272,3,p.vehicle.health/100,accent);}
  if(!p.vehicle&&panel==""){
   foreach(var v in g.vehicles)if(v&&!v.destroyed&&Vector3.Distance(v.transform.position,p.transform.position)<4.5f){Hint("[F] ENTER  "+v.spec.label);break;}
   foreach(var s in g.world.services)if(Vector3.Distance(s.transform.position,p.transform.position)<10){Hint("[E] "+s.title);break;}
  }
  if(panel==""&&InputHub.Aim){Rect(795,449,10,1,Color.white);Rect(799,445,1,10,Color.white);}
  if(hitMarker>0){Text("×",791,431,large);}
  if(p.weapons.selected==10&&InputHub.Aim&&panel==""){Rect(0,0,350,900,new Color(0,0,0,.93f));Rect(1250,0,350,900,new Color(0,0,0,.93f));Rect(350,449,900,1,new Color(0,0,0,.8f));Rect(799,0,1,900,new Color(0,0,0,.8f));}
  if(p.vehicle&&p.vehicle.passengerService)Text("METRO TAXI / T SKIP JOURNEY",630,667,small);
  if(p.cover)Text("COVER  /  Q RELEASE",720,667,small);
  if(p.parachute)Text("ALT  "+Mathf.RoundToInt(p.transform.position.y-World.Height(p.transform.position.x,p.transform.position.z))+" M   /   SHIFT FLARE",660,700,medium);
  if(showFPS)Text(Mathf.RoundToInt(fps)+" FPS  /  "+g.world.activeSectors+" SECTORS  /  "+g.actors.Count+" PEOPLE",28,96,tiny);
  if(Time.unscaledTime<g.toastUntil){Rect(490,104,620,46,ink);Text(g.toast,510,115,small);}
  Text("F1  SANDBOX     M  MAP     P  PHONE     TAB  WEAPONS     ESC  PAUSE",474,872,tiny);
  if(rangeTime>0)Text("RANGE  "+Mathf.CeilToInt(rangeTime)+"s  |  HITS "+rangeHits,665,165,medium);
  if(hurt>0)Rect(0,0,1600,900,new Color(.65f,.04f,.03f,hurt*.11f));
  if(InputHub.Held(Key.Tab)&&panel=="")WeaponWheel();
  if(panel!="")Panel();
  if(death!=""){Rect(0,0,1600,900,new Color(.04f,.06f,.07f,.84f));Text(death,620,400,large);Text("MERIDIAN EMERGENCY SERVICES",620,450,small);}
 }
 void Hint(string text){Rect(520,776,560,42,ink);Text(text,543,787,small);}
 void Bar(float x,float y,float w,float h,float f,Color c){Rect(x,y,w,h,new Color(.07f,.09f,.1f,.8f));Rect(x,y,w*Mathf.Clamp01(f),h,c);}
 string FormatTime(float hour)=>Mathf.FloorToInt(hour).ToString("00")+":"+Mathf.FloorToInt((hour%1)*60).ToString("00");
 void WeaponWheel(){
  var w=Game.I.player.weapons;Rect(445,202,710,470,new Color(.025f,.04f,.05f,.9f));Text("LOADOUT  /  SCROLL TO SELECT",475,220,medium);
  for(int i=0;i<Weapons.Defs.Length;i++){float a=i*Mathf.PI*2/Weapons.Defs.Length-Mathf.PI/2;Vector2 pos=new(800+Mathf.Cos(a)*245,435+Mathf.Sin(a)*167);if(i==w.selected)Rect(pos.x-83,pos.y-7,172,43,new Color(.15f,.39f,.42f));Text((w.owned[i]?"":"LOCKED  ")+Weapons.Defs[i].name,pos.x-80,pos.y,tiny);}
 }
 Vector2 MapPoint(Vector3 p,Rect rect,bool full){if(full)return new(rect.x+(p.x+2200)/3800*rect.width,rect.y+rect.height-(p.z+2200)/4800*rect.height);Vector3 d=p-Game.I.player.transform.position;return new(rect.center.x+d.x*.47f,rect.center.y-d.z*.47f);}
 void MapDot(Vector3 p,Rect r,bool full,Color c,int size){var pos=MapPoint(p,r,full);if(r.Contains(pos))Rect(pos.x-size/2,pos.y-size/2,size,size,c);}
 void DrawMap(Rect r,bool full){
  Rect(r.x,r.y,r.width,r.height,new Color(.045f,.095f,.12f,.96f));GUI.BeginGroup(r);var local=new Rect(0,0,r.width,r.height);
  for(int i=-7;i<=7;i++){var a=MapPoint(new(i*128,0,-896),r,full)-r.position;var b=MapPoint(new(i*128,0,1024),r,full)-r.position;Rect(a.x,b.y,full?2:4,a.y-b.y,new Color(.27f,.34f,.36f));a=MapPoint(new(-896,0,i*128),r,full)-r.position;b=MapPoint(new(1024,0,i*128),r,full)-r.position;Rect(a.x,a.y,b.x-a.x,full?2:4,new Color(.27f,.34f,.36f));}
  GUI.EndGroup();
  foreach(var s in Game.I.world.services)MapDot(s.transform.position,r,full,accent,6);
  foreach(var v in Game.I.vehicles)if(v&&v.policeControlled)MapDot(v.transform.position,r,full,new Color(.35f,.62f,1),6);
  if(Game.I.wanted.level>0)MapDot(Game.I.wanted.lastKnown,r,full,new Color(1,.4f,.3f),9);
  if(hasWaypoint)MapDot(waypoint,r,full,new Color(.95f,.71f,.33f),9);
  MapDot(Game.I.player.transform.position,r,full,Color.white,8);
  var q=MapPoint(Game.I.player.transform.position,r,full);Vector3 f=Game.I.player.transform.forward;Line(q,q+new Vector2(f.x,-f.z)*13,Color.white,2);
  Text("N",r.x+r.width-17,r.y+4,tiny);
 }
 void Line(Vector2 a,Vector2 b,Color color,float thickness){var saved=GUI.matrix;float angle=Mathf.Atan2(b.y-a.y,b.x-a.x)*Mathf.Rad2Deg;GUIUtility.RotateAroundPivot(angle,a);Rect(a.x,a.y,(b-a).magnitude,thickness,color);GUI.matrix=saved;}
 void Panel(){
  Rect(0,0,1600,900,new Color(.015f,.025f,.035f,.72f));Rect(220,120,1160,650,ink);Rect(220,120,1160,3,accent);
  string title=panel=="admin"?"SANDBOX CONTROL":panel=="pause"?"FREE ROAM / PAUSED":panel=="map"?"MERIDIAN COAST / MAP":panel=="phone"?"RELAY / PERSONAL SERVICES":panel=="taxi"?"METRO TAXI / DESTINATION":service?service.title:panel.ToUpper();
  Text(title,250,141,large);if(Button("CLOSE  ×",1207,143,144,35))Close();
  if(panel=="admin")Admin();else if(panel=="map")MapPanel();else if(panel=="pause")PausePanel();else if(panel=="phone")Phone();else if(panel=="taxi")Taxi();else if(panel=="weapons")Shop();else if(panel=="garage")Garage();else if(panel=="clinic")Clinic();else if(panel=="home")Home();else if(panel=="range")Range();
 }
 void Admin(){
  string[] tabs={"WORLD","VEHICLES","LOADOUT","PLAYER","PURSUIT","SETTINGS"};for(int i=0;i<tabs.Length;i++)if(Button(tabs[i],250+i*181,205,170,36)){tab=i;scroll=Vector2.zero;}
  var g=Game.I;var p=g.player;
  if(tab==0){
   Text("TRAVEL",250,270,medium);for(int i=0;i<Roster.Districts.Length;i++)if(Button(Roster.Districts[i],250+(i%3)*350,310+(i/3)*52,335)){g.Teleport(i);Close();}
   Text("ATMOSPHERE",250,490,medium);for(int i=0;i<5;i++)if(Button(Atmosphere.WeatherNames[i],250+i*211,534,198))g.atmosphere.SetWeather(i);
   Text("LOCAL TIME  "+FormatTime(g.atmosphere.hour),250,600,small);g.atmosphere.hour=GUI.HorizontalSlider(new Rect(450,610,610,20),g.atmosphere.hour,0,23.99f);
  } else if(tab==1){
   for(int i=0;i<Roster.Vehicles.Length;i++)if(Button(Roster.Vehicles[i].label,250+(i%3)*350,280+(i/3)*66,332,51)){var v=g.SpawnForPlayer(i);p.EnterVehicle(v,true);Close();}
  } else if(tab==2){
   if(Button("GIVE ALL + REFILL",250,264,320)){p.weapons.GiveAll();}
   for(int i=0;i<Weapons.Defs.Length;i++)if(Button(Weapons.Defs[i].name,250+(i%3)*350,320+(i/3)*61,332,47)){p.weapons.owned[i]=true;p.weapons.ammo[i]=p.weapons.Capacity(i);p.weapons.reserve[i]=p.weapons.Capacity(i)*10;p.weapons.Equip(i);}
  } else if(tab==3){
   if(Button("Health + armor",250,280,330)){p.health=p.armor=100;}
   if(Button(g.god?"Invulnerability: ON":"Invulnerability: OFF",610,280,330))g.god=!g.god;
   if(Button("+ $50,000",970,280,330))g.cash+=50000;
   if(Button("Parachute / high jump",250,340,330)){p.ExitVehicle(true);p.Teleport(p.transform.position+Vector3.up*200);Close();}
   if(Button(p.scuba?"Scuba: ON":"Scuba: OFF",610,340,330)){p.scuba=!p.scuba;p.breath=100;}
   if(Button("Max all skills",970,340,330))for(int i=0;i<7;i++)g.skills[i]=100;
   Skills(250,420);
   if(Button("Reset skills",970,630,330))for(int i=0;i<7;i++)g.skills[i]=0;
  } else if(tab==4){
   Text("WANTED LEVEL / REAL LINE OF SIGHT SEARCH",250,280,medium);for(int i=0;i<=5;i++)if(Button(i==0?"CLEAR":i+" STARS",250+i*178,335,165,48))g.wanted.SetLevel(i);
   if(Button("Dispatch reinforcement",250,420,340)){if(g.wanted.level==0)g.wanted.SetLevel(2);g.wanted.Dispatch();}
   Text("State: "+g.wanted.state+"    Unseen: "+g.wanted.unseen.ToString("F1")+"s",250,490,medium);
   Text("Hide behind buildings or leave the search area. Reacquisition resets escape progress.",250,535,small);
  }else{
   if(Button(g.traffic?"Traffic: ON":"Traffic: OFF",250,285,330))g.traffic=!g.traffic;
   if(Button(g.pedestrians?"Pedestrians: ON":"Pedestrians: OFF",610,285,330))g.pedestrians=!g.pedestrians;
   if(Button(g.wildlife?"Wildlife: ON":"Wildlife: OFF",970,285,330))g.wildlife=!g.wildlife;
   if(Button(showFPS?"Diagnostics: ON":"Diagnostics: OFF",250,350,330))showFPS=!showFPS;
   if(Button("Save free roam",610,350,330))g.Save();
   if(Button("Load free roam",970,350,330))g.Load();
   Text("Position "+p.transform.position.ToString("F1"),250,440,medium);Text("F12 saves a photograph. The world has no story or mission system.",250,490,small);
   if(Button("Open vehicle workshop",250,550,330))panel="garage";
  }
 }
 void MapPanel(){
  DrawMap(new Rect(252,207,640,510),true);for(int i=0;i<Roster.Districts.Length;i++)if(Button(Roster.Districts[i],940,211+i*51,395,39)){waypoint=Roster.Locations[i];hasWaypoint=true;Game.I.Notify("WAYPOINT  "+Roster.Districts[i]);}
  Text("Select a destination to place a navigation marker. Teleports are in F1.",255,726,tiny);
 }
 void PausePanel(){
  Text("A city with no instructions. Make your own way.",250,220,medium);
  string[] lines={"WASD  MOVE / STEER     MOUSE  LOOK     SHIFT  SPRINT","SPACE  JUMP / HANDBRAKE / AIRCRAFT LIFT     CTRL  DESCEND / DIVE","F  ENTER / EXIT     E  SERVICE     C  CROUCH     Q  COVER","LMB  FIRE     RMB  AIM     R  RELOAD     SCROLL / TAB  WEAPONS","V  FIRST PERSON     L  HEADLIGHTS     H  HORN     J  SIREN     N  RADIO","PLANE: W/S THROTTLE  A/D ROLL  ARROWS PITCH  Q/E YAW","F5  SAVE     F9  LOAD     F12  PHOTO     F1  SANDBOX MENU"};
  for(int i=0;i<lines.Length;i++)Text(lines[i],250,277+i*39,small);
  if(Button("Resume",250,640,260))Close();if(Button("Save",535,640,260))Game.I.Save();if(Button("Quit game",1100,640,220))Application.Quit();
 }
 void Phone(){
  Text("RELAY",250,220,large);Text("PERSONAL UTILITY / CONNECTED",250,262,small);
  if(Button("Quick save",250,327,470))Game.I.Save();if(Button("Garage delivery",250,388,470)){Game.I.SpawnForPlayer(Game.I.storedIndex);Close();}
  if(Button("Photo / hide interface",250,450,470)){Close();Game.I.Notify("Press F12 to capture");}
  if(Button("Map & destinations",250,510,470))panel="map";
  if(Button("Call Metro Taxi",250,570,470))panel="taxi";
  Text("PERSONAL VEHICLE",795,328,medium);Text(Roster.Vehicles[Mathf.Clamp(Game.I.storedIndex,0,14)].label,795,372,small);
  Text("Emergency dispatch listens to reported incidents.",795,450,small);Text("Use TORQUE to store and upgrade your vehicle.",795,483,small);
 }
 void Taxi(){Text("CHOOSE DESTINATION / $50 + DISTANCE FARE",250,220,medium);for(int i=0;i<Roster.Districts.Length;i++)if(Button(Roster.Districts[i],250+(i%3)*350,280+(i/3)*62,330,47)){Game.I.CallTaxi(i);Close();}Text("Ride as a passenger. Press T after three seconds to skip the journey.",250,535,small);}
 void Shop(){
  var p=Game.I.player;for(int i=1;i<Weapons.Defs.Length;i++){int price=250+i*180;if(Button((p.weapons.owned[i]?"EQUIP  ":"$"+price+"  ")+Weapons.Defs[i].name,250+((i-1)%3)*350,225+((i-1)/3)*57,333,44)){if(p.weapons.owned[i]||Game.I.Pay(price)){p.weapons.owned[i]=true;p.weapons.Equip(i);}}}
  if(Button("Ammo refill  /  $180",250,485,330)&&Game.I.Pay(180)){for(int i=3;i<Weapons.Defs.Length;i++)p.weapons.reserve[i]+=p.weapons.Capacity(i)*3;}
  if(Button("Suppressor  /  $450",610,485,330)&&Game.I.Pay(450))p.weapons.suppressor=true;
  if(Button("Extended magazines  /  $600",970,485,330)&&Game.I.Pay(600))p.weapons.extended=true;
  if(Button("Stability grip  /  $350",250,545,330)&&Game.I.Pay(350))p.weapons.grip=true;
  if(Button("Body armor  /  $250",610,545,330)&&Game.I.Pay(250))p.armor=100;
  Text("SUPPRESSOR "+p.weapons.suppressor+"   EXTENDED "+p.weapons.extended+"   GRIP "+p.weapons.grip,250,623,small);
 }
 Vehicle GarageVehicle(){if(Game.I.player.vehicle)return Game.I.player.vehicle;Vehicle best=null;float range=20;foreach(var v in Game.I.vehicles)if(v){float d=Vector3.Distance(v.transform.position,Game.I.player.transform.position);if(d<range){range=d;best=v;}}return best;}
 void Garage(){
  var v=GarageVehicle();if(!v){Text("Park a vehicle nearby or request your stored vehicle.",250,260,medium);if(Button("Retrieve personal vehicle",250,335,480)){var car=Game.I.SpawnForPlayer(Game.I.storedIndex);car.engineUpgrade=Mathf.Max(1,Game.I.storedEngine);car.Repaint(Game.I.storedPaint);}return;}
  Text(v.spec.label.ToUpperInvariant()+"  /  CONDITION "+Mathf.RoundToInt(v.health)+"%",250,228,medium);
  if(Button("Repair  /  $250",250,286,330)&&Game.I.Pay(250))v.Repair();
  if(Button("Engine +25%  /  $1,200",610,286,330)&&Game.I.Pay(1200))v.engineUpgrade=Mathf.Min(1.75f,v.engineUpgrade+.25f);
  if(Button("Brakes +25%  /  $600",970,286,330)&&Game.I.Pay(600))v.brakeUpgrade=Mathf.Min(2,v.brakeUpgrade+.25f);
  if(Button("Armor +30%  /  $800",250,350,330)&&Game.I.Pay(800))v.armorUpgrade=Mathf.Min(2.5f,v.armorUpgrade+.3f);
  if(Button("Store personal vehicle",610,350,330)){Game.I.storedIndex=v.index;Game.I.storedEngine=v.engineUpgrade;Game.I.Save();}
  Text("PRIMARY FINISH  /  $150",250,425,medium);
  Color[] colors={new(.035f,.11f,.17f),new(.52f,.04f,.025f),new(.65f,.67f,.65f),new(.025f,.03f,.035f),new(.6f,.38f,.07f),new(.07f,.22f,.11f)};
  for(int i=0;i<colors.Length;i++){GUI.backgroundColor=colors[i];if(GUI.Button(new Rect(250+i*175,478,152,80),"")&&Game.I.Pay(150))v.Repaint(colors[i]);GUI.backgroundColor=Color.white;}
  Text("ENGINE "+v.engineUpgrade.ToString("F2")+"×    BRAKES "+v.brakeUpgrade.ToString("F2")+"×    ARMOR "+v.armorUpgrade.ToString("F2")+"×",250,603,small);
 }
 void Clinic(){Text("Walk-in treatment. No appointments required.",250,250,medium);if(Button("Treatment  /  $100",250,335,440)&&Game.I.Pay(100)){Game.I.player.health=100;Game.I.Notify("HEALTH RESTORED");}if(Button("Armor  /  $250",750,335,440)&&Game.I.Pay(250))Game.I.player.armor=100;}
 void Home(){if(Button("Save",250,240,330))Game.I.Save();if(Button("Rest until morning",610,240,330)){Game.I.atmosphere.hour=8;Game.I.player.health=100;}if(Button("Request stored vehicle",970,240,330)){Game.I.SpawnForPlayer(Game.I.storedIndex);Close();}
  Text("WARDROBE",250,320,medium);for(int i=0;i<4;i++)if(Button("Outfit "+(i+1),250+i*260,370,242))Game.I.player.SetOutfit(i);Skills(250,447);}
 void Skills(float x,float y){string[] names={"Stamina","Shooting","Strength","Stealth","Driving","Flying","Lung capacity"};for(int i=0;i<7;i++){Text(names[i],x,y+i*30,small);Bar(x+160,y+10+i*30,380,5,Game.I.skills[i]/100,accent);Text(Mathf.FloorToInt(Game.I.skills[i]).ToString(),x+555,y+i*30,tiny);}}
 void Range(){Text("45 seconds. Shoot the targets. $10 per hit.",250,260,medium);if(Button("Start practice",250,337,450)){rangeTime=45;rangeHits=rangeShots=0;Game.I.player.weapons.GiveAll();Game.I.player.weapons.Equip(3);Close();}}
}
}
