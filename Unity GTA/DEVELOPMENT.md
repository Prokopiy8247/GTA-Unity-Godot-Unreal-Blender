# Meridian Coast

Original missionless, single-player open-world sandbox in the existing Unity project.

For ready-to-play Windows and macOS downloads, see README.md and Docs/PLAY_RU.md. Publication/privacy details: PUBLICATION.md.

## Runtime and launch
Unity **6000.6.0f1**, URP **17.6.0**, Input System **1.20.0**, Windows x64 and macOS Universal, PhysX.
URP was retained from the existing project. HDRP migration was evaluated and rejected to preserve the available, tested package configuration. The result uses URP shadows, ACES, bloom, generated surface/normal maps, fog, local lights and a project-owned water shader. It does not reach the requested AAA realism bar.

Run **Builds/Windows/MeridianCoast.exe**, or use **Launch Meridian Coast.ps1**.
In Unity open **Assets/GTA/Scenes/Meridian_FreeRoam.unity** and press Play. The scene's bootstrap creates and connects the world automatically. No manual Inspector or prefab assembly is needed.

To regenerate imported prefabs, materials and the startup scene: **Meridian > Generate complete game**.
To build: **Meridian > Build Windows player**, or **Build Meridian Coast.ps1** with the Editor closed.
The original SampleScene is preserved; the generated scene is the only enabled build scene.

## Architecture
- Game: startup, catalog, bounded entity lists, services, persistence, test mode.
- World: 6 × 6 km terrain extent; connected 1.9 km city grid; 225 sectors with distance activation; airport, port, coastline, farms, hills and connecting roads. Landscape beyond the city is intentionally sparse.
- PlayerMotor / FollowCamera: CharacterController movement, crouch, contextual cover, obstacle vault, swimming, diving, parachute, fall damage, orbit/collision camera and first person.
- Vehicle: reusable Rigidbody/WheelCollider cars and bikes; buoyant boat; assisted helicopter; thrust/lift/stall approximation for aircraft. Traffic uses kinematic lanes; controlled vehicles use physics.
- Population / Actor: bounded civilians and traffic, sidewalk routes, panic, basic obstacle avoidance, clothing variants, armed officers and joint-based NPC ragdolls.
- WantedSystem: delayed witness reports, police line of sight, last-known position, pursuit/search, 0–5 pressure, reinforcements, barricades and helicopter. Search dispatch targets the last known position.
- Weapons / Effects: data roster, hitscan, projectile explosives, magazines, recoil/spread, reload, impact effects and force.
- GameUI: scaled HUD, radar, full map, services, loadout overlay, pause screen, phone and F1 benchmark menu.
- Atmosphere / SoundBank: continuous clock, weather, rain, underwater fog, original synthesized audio and radio.
- RuntimeQA: executable integration checks and genuine rendered screenshots, invoked with -meridianQA.

The world is generated at startup rather than saved as hundreds of hand-authored scenes. Sector switching is distance activation, not asynchronous additive loading. City geometry still exists in memory. Blender LOD exports provide separate lower-detail meshes for 11 building/nature assets; other models use distance culling.

## Controls

| Input | Action |
|---|---|
| WASD / mouse | Movement, steering / camera |
| Shift | Sprint; parachute flare |
| Space | Jump; deploy parachute while falling; vehicle handbrake; helicopter ascend; plane pitch up |
| Left Ctrl | Descend in helicopter; dive while swimming |
| C / Q / G | Crouch / contextual cover / vault low obstruction |
| F / E | Enter or exit vehicle / use nearby service |
| Left / right mouse | Fire or melee / aim |
| R / scroll / 1–9 | Reload / change weapon / direct slots |
| Hold Tab | Loadout overlay; scroll selects |
| V | First person |
| L / H / J / N | Vehicle lights / horn / siren / original radio |
| Plane W/S, A/D, arrows, Q/E | Throttle, roll, pitch, yaw |
| P / T | Phone / skip taxi after three seconds |
| M / Esc / F1 | Map / pause / sandbox controls |
| F11 | Toggle fullscreen (Fn + F11 on some Macs) |
| F5 / F9 / F12 | Save / load / photo |

F1 provides district travel, every implemented vehicle/weapon, health, money, wanted, weather, time, traffic, pedestrians, wildlife, scuba, skill controls and workshop access. Vehicle spawning automatically supplies the appropriate location for boats and planes. On aircraft exit, press Space once falling to deploy the parachute.

## Blender workflow
Mandatory connection used: **blender_unity**, **localhost:9876**. Canonical source: **UnityGTA.blend**.
All 54 main 3D assets were created through that MCP connection, with 11 additional LOD exports. No downloaded model packs or external generation services were used.

Collections under GTA_UNITY separate Vehicles, Characters, Weapons, Buildings, StreetProps and Nature.
The source contains named wheel and articulated limb pivots. Characters use a procedural articulated transform rig, not a skinned Humanoid avatar.
FBX files are under Assets/GTA/Generated/Models and LODs. The Unity builder preserves FBX root transforms, normalizes game-facing orientation and creates reusable prefabs with remapped URP materials.

**Tools/Blender/export_master.py** is the repeatable export of the current, refined master. Send its text to blender_unity; safe mode forbids opening/running external scripts inside Blender.
**build_assets.py** records the initial library generator; rerunning it replaces the generated library and does not preserve later art revisions. Prefer exporting the canonical master.
**refine_vehicles.py** records the final complete-shell/normals rebuild.
**refine_characters.py** records the final anatomical character refinements.

## Persistence
Save: %USERPROFILE%/AppData/LocalLow/Meridian Studio/Meridian Coast/meridian-save.json.
Stored: player position, health, armor, cash, weapons/ammo/modification flags, outfit, skills, weather/time and personal vehicle index/engine/paint. Dynamic traffic, NPCs, destruction and wanted state are not persisted.
F5, phone, home and exit save; F9 loads. Unsupported or malformed saves are rejected without destroying the running world.
Automated checks use a separate .astra-run/qa-save.json.

## Validation
Read .astra-run/runtime-qa.txt for per-feature integration results, .astra-run/runtime-errors.txt for captured errors, and .astra-run/build-result.txt for the build summary.
Screenshots are in .astra-run. A hidden/minimized Windows player produces black screen captures, so visual validation launches an actual visible game window.
The first expanded run verified all 15 vehicle entries (11 land, boat, two helicopters, airplane), genuine flight, NPC damage/ragdoll, witnesses, search/decay, save/load, every district, swimming/diving and rendered day/night frames.

## Limits
This is a substantial functional prototype with simplified original artwork and AI. It is not equivalent to GTA V/RDR2 production content.
Traffic makes abrupt junction turns and can stall in congestion; police tactics are basic. NPC navigation uses local routes and collision probes rather than baked NavMesh.
Cars have shared construction logic with distinct size/cabin/silhouette profiles; there are no separate animated doors, body deformation, punctured tires or full interior seating animation.
Aircraft use assisted physics, not flight simulation. The taxi path is a simple road service with optional skip.
Cover is planar and limited; no corner peeking, ladder system, advanced melee or stealth takedown animation.
Safehouse/shop interiors are small open-front structures. Customization is paint, repair, engine, brakes, armor and simple weapon modifiers, not a full body-kit editor.
Wildlife is limited to deer; no transit trains, ambulance/fire dispatch, full scuba equipment, underwater wrecks, sports suite, NPC voices or authored music recordings.
Sector activation and startup generation can cause brief stalls. No claim is made for stable frame pacing on every machine.

