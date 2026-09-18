extends RefCounted
const VEHICLES = {
"sedan":{"name":"Aster Executive","model":"mc_sedan","kind":"car","speed":48.0,"power":11000.0,"mass":1450.0},
"compact":{"name":"Finch City","model":"mc_compact","kind":"car","speed":38.0,"power":8000.0,"mass":1100.0},
"sport":{"name":"Vela GT","model":"mc_sport","kind":"car","speed": 70.0,"power":18000.0,"mass":1300.0},
"muscle":{"name":"Bison 440","model":"mc_muscle","kind":"car","speed":55.0,"power":15500.0,"mass":1600.0},
"suv":{"name":"Ridge SUV","model":"mc_suv","kind":"car","speed":44.0,"power":12500.0,"mass":1900.0},
"pickup":{"name":"Cairn Utility","model":"mc_pickup","kind":"car","speed":42.0,"power":13000.0,"mass":2000.0},
"van":{"name":"Porter Van","model":"mc_van","kind":"car","speed":35.0,"power":10500.0,"mass":2200.0},
"police":{"name":"MCPD Interceptor","model":"mc_police","kind":"car","speed":53.0,"power":15500.0,"mass":1550.0},
"taxi":{"name":"Meridian Cab","model":"mc_taxi","kind":"car","speed":45.0,"power":11000.0,"mass":1450.0},
"motorcycle":{"name":"Kestrel 900","model":"mc_motorcycle","kind":"bike","speed":58.0,"power":4400.0,"mass":340.0},
"boat":{"name":"Tern 22","model":"mc_boat","kind":"boat","speed": 30,"power":14000.0,"mass":1600.0},
"helicopter":{"name":"Osprey H4","model":"mc_helicopter","kind":"heli","speed": 60.0,"power":14000.0,"mass":1800.0},
"police_helicopter":{"name":"MCPD Osprey","model":"mc_police_helicopter","kind":"heli","speed":60.0,"power":14500.0,"mass":1800.0},
"plane":{"name":"Petrel P6","model":"mc_plane","kind":"plane","speed":95.0,"power":18000.0,"mass":1300.0}
}
const WEAPONS = [
{"id":"fists","name":"Unarmed","damage":18.0,"mag":0,"rate":.55,"range":2.3,"price":0},
{"id":"knife","name":"Utility knife","damage": 40.0,"mag":0,"rate":.45,"range":2.5,"price":150},
{"id":"bat","name":"Hardwood bat","damage":48.0,"mag":0,"rate":.8,"range":2.8,"price":90},
{"id":"pistol","name":"M9 Sidearm","damage": 30,"mag":15,"rate":.23,"range":130.0,"price":350},
{"id":"heavy","name":"Sentinel .45","damage": 50.0,"mag":8,"rate":.38,"range":170.0,"price":650},
{"id":"smg","name":"Wasp Compact","damage":21.0,"mag": 30,"rate":.08,"range":160.0,"price":1200},
{"id":"shotgun","name":"Breaker 12","damage": 16.0,"mag":8,"rate":.85,"range": 60.0,"price":1100},
{"id":"rifle","name":"Morrow R5","damage": 30,"mag":30,"rate":.11,"range":250.0,"price":1800},
{"id":"carbine","name":"Morrow C4","damage":27.0,"mag":30,"rate":.09,"range":230.0,"price":2100},
{"id":"sniper","name":"Horizon DMR","damage":110.0,"mag":5,"rate":1.15,"range":600.0,"price":3200},
{"id":"grenade","name":"Fragment grenade","damage":160.0,"mag":1,"rate":1.1,"range": 40.0,"price":250},
{"id":"rocket","name":"Atlas launcher","damage":260.0,"mag":1,"rate":1.6,"range":300.0,"price":4000}
]
const PLACES = {
"Downtown":Vector3(6,2,24),
"Old Quarter":Vector3(-378,2,20),
"Garden Suburbs":Vector3(-510,2,390),
"Industrial":Vector3(390,2,390),
"Harbor":Vector3(774,2,510),
"Coast":Vector3(898,2,-260),
"Airport":Vector3(-520,2,1010),
"Countryside":Vector3(-900,2,260),
"Highlands":Vector3(-1024,90,-850),
"Hospital":Vector3(134,2,-115),
"Safehouse":Vector3(-246,2,262)
}
