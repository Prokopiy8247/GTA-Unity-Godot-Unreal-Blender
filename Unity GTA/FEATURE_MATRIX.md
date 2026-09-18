# Feature matrix

WORKING means a functional in-game path is present; PARTIAL identifies simplified scope or material limitations. See runtime-qa.txt for measured integration checks.

| Feature | Status | Notes |
|---|---|---|
| Existing Unity project and launch | WORKING | Same project, generated default scene, Windows executable |
| Missionless free roam | WORKING | Immediate control; no campaigns, quests or mission markers |
| Blender MCP production | WORKING | blender_unity / 9876 / UnityGTA.blend; 54 models + 11 LOD exports |
| AAA realistic visual target | PARTIAL | Original modeled assets, PBR and lighting; simplified geometry and characters remain |
| HDRP | NOT IMPLEMENTED | Existing URP retained |
| Large map and districts | WORKING | 6 × 6 km extent, 225 city sectors, nine travel destinations |
| Downtown / suburbs / industry | WORKING | Blender buildings, roads, sidewalks, parked and moving vehicles |
| Port / coast / airport / hills / farms | WORKING | Navigable geography and air/water/road access |
| Highway network | PARTIAL | Connected arterial roads; no complex interchanges or tunnels |
| Streaming / memory management | PARTIAL | Sector activation, bounded population; all base geometry remains resident |
| LODs | WORKING | Two mesh levels for 11 environment assets, distance culling elsewhere |
| Third-person movement / camera | WORKING | Walking, sprint, jump, orbit, collision, aim |
| First person | WORKING | Toggle on foot and in vehicles; simplified cockpit placement |
| Crouch / stealth | PARTIAL | Slower movement, reduced noise/visibility; no authored takedown system |
| Cover | PARTIAL | Wall/low-object detection and lateral motion; no robust corner handling |
| Vault / climbing | PARTIAL | Simple low-obstacle vault; no ladders or mantle suite |
| Player animation / rig | PARTIAL | Named articulated limbs with procedural gait; no skinned Humanoid |
| NPC variants and walking | WORKING | Clothing/skin/model variants, sidewalk waypoints, distance tiers |
| NPC reactions / witnesses | WORKING | Panic/flee, delayed report, dead witnesses cannot finish reporting |
| NPC ragdoll | WORKING | Physics bodies and character joints, tested after damage |
| Traffic | PARTIAL | Lane graph, following/stopping, alternating intersection phase; simplified turning |
| Traffic-signal visuals | PARTIAL | Authored signals; no synchronized emissive phase animation |
| Sedan / compact / sports / muscle | WORKING | Each entry accelerated and entered/exited in game |
| SUV / pickup / van / cruiser / taxi | WORKING | Separate exported profiles; tested movement/damage/repair |
| Motorcycle / bicycle | WORKING | Two-wheel physics with stabilization; simplified rider presentation |
| Boat | WORKING | Buoyancy and propulsion tested; coastline entry/exit |
| Civilian / police helicopters | WORKING | Lift, yaw, tilt, chase camera, damage; both tested |
| Propeller airplane | WORKING | Takeoff, powered flight, controls and low-speed lift degradation |
| Jets / heavy trucks / emergency roster | NOT IMPLEMENTED | No decorative menu entries pretending to work |
| Carjacking | PARTIAL | Driver ejection/panic and witnessed crime; abbreviated approach transition |
| Drive-by shooting | WORKING | Handguns, SMG and grenade permitted; aim and spread penalty |
| Vehicle damage / explosions | WORKING | Collision/bullet damage, smoke, fire, explosion and force |
| Vehicle deformation / detachable panels | NOT IMPLEMENTED | No soft-body or panel simulation |
| Vehicle lights / horn / siren / radio | WORKING | Context controls and original synthesized sound |
| Animated doors / convertible roof | NOT IMPLEMENTED | Fixed shells |
| Garage repair / paint / upgrades | WORKING | Money cost, health, visible paint, engine/brake/armor effects |
| Full cosmetic body-kit editor | NOT IMPLEMENTED | No spoilers/rims/bumper customization UI |
| Melee | PARTIAL | Fists, knife and baton damage; no block/finisher animation suite |
| Firearm roster | WORKING | Pistol, heavy pistol, SMG, shotgun, rifle, carbine, marksman, sniper |
| Grenades / launcher | WORKING | Physical projectile, fuse/contact explosion and radial damage |
| Ammo / reload / recoil / scope | WORKING | Inventory and magazine checks; zoom/scoped presentation |
| Weapon modifications | PARTIAL | Suppressor noise, magazine capacity and stability; no full attachment geometry editor |
| Police wanted 0–5 | WORKING | Pressure, witness reports, escalation, visible HUD |
| Pursuit / search / escape | WORKING | Real LOS, last-known position, unseen-only decay; tested |
| Police tactics / tactical units | PARTIAL | Cruisers, officers, barricades and helicopter; basic routing, no PIT/spikes |
| Arrest | WORKING | Close, stationary, unarmed one-star arrest and respawn path |
| Player damage / death / respawn | WORKING | Health/armor, fall, bullets, explosion, drowning; hospital respawn |
| Destructible/movable props | PARTIAL | A bounded set of movable central bins and explosion forces |
| Shops / economy | WORKING | Weapons, ammo, armor, treatment, repair; cash and sandbox grant |
| Safehouse / wardrobe | PARTIAL | Save, rest, outfits and vehicle service in a basic accessible interior |
| Personal garage persistence | PARTIAL | Vehicle model, engine and paint; not the entire dynamic vehicle state |
| Phone / photo | WORKING | Save, garage, map and screenshot utility |
| Taxi passenger service | PARTIAL | Boarding, movement and arrival/skip verified in the final executable; simple routing |
| Train / subway | NOT IMPLEMENTED | No rail transit |
| Swimming / diving | WORKING | Buoyancy movement, breath, underwater fog, drowning/scuba toggle |
| Parachute | WORKING | Deploy, steer, flare and automatic release on landing |
| Underwater exploration content | NOT IMPLEMENTED | No wreck/interior/scuba equipment models |
| Wildlife | PARTIAL | Region-limited deer wander/flee; no diverse ecosystem |
| Day/night | WORKING | Time cycle, sun, atmosphere, street/headlights and window emission |
| Weather | WORKING | Clear, cloud, rain, fog, storm; wet roads and rain grip penalty |
| Audio / ambience | WORKING | Original synthesis, spatial shots/vehicles/sirens, rain/ocean, two radio modes |
| VFX | WORKING | Muzzle, impacts, tracers, smoke/fire, explosions, rain and water spray |
| HUD / radar / full map | WORKING | Health, armor, stamina, breath, ammo, cash, speed, wanted and locations |
| GPS navigation | PARTIAL | Destination marker; no complete route planner |
| Weapon wheel | PARTIAL | Radial display with scroll selection; no time slowing or pointer selection |
| Skill progression | WORKING | Seven use-based stats, status UI and modest effects |
| Shooting range | WORKING | Voluntary timed targets, hit/accuracy score, small cash gain |
| Stunt jumps | PARTIAL | Physical ramps; no scoring/landing detector |
| Other sports / activities | NOT IMPLEMENTED | No racing/golf/tennis/darts suite |
| Emergency medical/fire dispatch | NOT IMPLEMENTED | Police response only |
| Save/load | WORKING | Real file round trip and malformed-save rejection tested |
| Admin / benchmark menu | WORKING | Vehicle/weapon/world/police/player/environment controls |
| Keyboard/mouse | WORKING | Full primary path |
| Controller | NOT IMPLEMENTED | Keyboard/mouse prioritized |

