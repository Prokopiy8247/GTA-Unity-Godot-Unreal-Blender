using System;
using UnityEngine;
namespace Meridian {
[CreateAssetMenu(menuName="Meridian/Catalog")]
public class GameCatalog : ScriptableObject {
 public string[] names; public GameObject[] models; public Material asphalt, concrete, grass, sand, water, marking, particle;
 public GameObject Get(string n) { int i=Array.IndexOf(names,n);return i<0?null:models[i]; }
}
public enum VehicleKind { Car, Motorcycle, Bicycle, Boat, Helicopter, Plane }
[Serializable] public class VehicleSpec {
 public string id,label; public VehicleKind kind; public float maxSpeed,power,mass,length;
 public VehicleSpec(string i,string l,VehicleKind k,float s,float p,float m,float len) {id=i;label=l;kind=k;maxSpeed=s;power=p;mass=m;length=len;}
}
public static class Roster {
 public static readonly VehicleSpec[] Vehicles={
 new("Aster_Sedan","Aster / sedan",VehicleKind.Car,48,1600,1450,4.7f),
 new("Mica_Compact","Mica / compact",VehicleKind.Car,38,1250,1050,3.65f),
 new("Vela_Sport","Vela / sport",VehicleKind.Car,72,2400,1300,4.35f),
 new("Bison_Muscle","Bison / muscle",VehicleKind.Car,60,2600,1750,4.9f),
 new("Atlas_SUV","Atlas / SUV",VehicleKind.Car,43,2200,2200,4.95f),
 new("Ranger_Pickup","Ranger / pickup",VehicleKind.Car,44,2300,2250,5.45f),
 new("Courier_Van","Courier / van",VehicleKind.Car,35,2200,2450,5.2f),
 new("Sentinel_Police","Sentinel / police",VehicleKind.Car,58,2300,1750,4.95f),
 new("Metro_Taxi","Metro / taxi",VehicleKind.Car,45,1700,1550,4.75f),
 new("Arrow_Motorcycle","Arrow / motorcycle",VehicleKind.Motorcycle,65,850,240,1.9f),
 new("Comet_Bicycle","Comet / bicycle",VehicleKind.Bicycle,15,130,95,1.9f),
 new("Kestrel_Boat","Kestrel / motorboat",VehicleKind.Boat,35,16,950,5.4f),
 new("Heron_Helicopter","Heron / helicopter",VehicleKind.Helicopter,65,14,2100,6),
 new("Watch_PoliceHeli","Watch / police helicopter",VehicleKind.Helicopter,70,15,2300,6),
 new("Swift_Plane","Swift / propeller plane",VehicleKind.Plane,100,14,1250,7.2f)};
 public static string[] Districts={"Central Exchange","Westhaven Homes","Foundry District","Breakwater Port","Sable Beach","Meridian Airport","Greenridge Farms","Northwatch Hills","Coastal Highway"};
 public static Vector3[] Locations={new(9,1,20),new(-520,1,260),new(390,1,-520),new(930,1,-500),new(1040,1,360),new(-1140,1,-1250),new(-1250,1,920),new(-200,1,1700),new(880,1,900)};
}
}
