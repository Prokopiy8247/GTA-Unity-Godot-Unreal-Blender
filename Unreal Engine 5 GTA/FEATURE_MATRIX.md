# Port Meridian — feature matrix

Status describes the delivered implementation, not the full GTA/AAA benchmark aspiration. WORKING means a usable implemented path; PARTIAL identifies concrete gaps. Core runtime checks and visual captures are recorded in QA_RESULTS.md.

Feature | Status | Notes
--- | --- | ---
Existing Unreal project | WORKING | Existing Unreal_GTA.uproject, UE 5.8.2; no nested replacement project
Correct Blender MCP / master | WORKING | blender_unreal, port 9878, UnrealGTA.blend; 70 exported project-owned meshes
Automated content pipeline | WORKING | FBX, materials, skeletons, Physics Assets, map and Blueprint children generated and saved automatically
Original asset provenance | WORKING | No downloaded models/packs; original Blender geometry and synthesized WAV audio
Realistic asset-quality target | PARTIAL | Recognizable detailed vehicle/weapon silhouettes, but simplified humans, architecture and animations; not photorealistic
Large open world | PARTIAL | 17 km² including sea, 272 sectors, nine travel destinations; repeated regular grid, sparse rural detail
City / suburbs / industry / port / coast / airport / hills | WORKING | Saved district geometry, piers, crane, hangars, lighthouse, roads and trees
Detailed road network / bridges / tunnels | PARTIAL | Marked grid roads and crossings; no bridges, tunnels or highway junction system
Landscape / terrain / nature | PARTIAL | Blender terrain meshes, rocks and three trees with individual leaves; no UE Landscape sculpt or dense ecological simulation
World Partition | WORKING | Streaming enabled, spatial hash: 250 m cells, 850 m loading range; travel exercised in runtime
Nanite / HISM / culling | WORKING | Environment Nanite, per-sector HISM and distance culling
HLOD / production LOD pipeline | NOT IMPLEMENTED | No baked HLOD actors or character/vehicle LOD chains
Lumen / shadows / sky | WORKING | Software Lumen, Virtual Shadow Maps, Sky Atmosphere, movable sunlight, volumetric clouds and fog
Materials / textures | PARTIAL | Shared procedural PBR materials, weather wetness, animated water normals; no baked production texture sets
Player / Enhanced Input | WORKING | Movement, sprint, stamina, jump, camera, aim, tested through simulated key input
Character anatomy / rig | PARTIAL | Four authored 17-bone Blender rigs; imported skeleton has 18 bones; simplified segmented clothing/body
Character animation | PARTIAL | Procedural skeletal posing for walking/aiming/drivers; no authored animation clips, AnimBP or montages
First / third person cameras | WORKING | Spring-arm collision, shoulder aim, zoom scopes and first-person toggle
Cover | PARTIAL | Surface detection, crouched attachment and lateral movement; no corner transitions or separate leaning animation
Stealth | PARTIAL | Crouching, quiet footsteps, reduced police detection radius and melee bonus; no complete suspicion system
Traversal | PARTIAL | Jump, low-obstacle vault and fall damage; no ladders or ledge climbing
Melee | PARTIAL | Unarmed/knife/bat collision damage; no combos, blocking or paired takedowns
Pedestrians | PARTIAL | Walking, obstacle deflection, panic, witnesses and damage; no NavMesh schedules, conversations or animation variety
Traffic | PARTIAL | Lane targets, intersections, obstacle braking, spawn/despawn; rudimentary turns and congestion recovery
Civilian drivers / carjacking | PARTIAL | Seated pose, displaced driver flees and theft can trigger witnesses; no door/ejection animation
Land vehicles | WORKING | Eight car bodies plus motorcycle; Chaos hulls, ray suspension, steering, braking and collisions
Vehicle fidelity | PARTIAL | Distinct specifications, wheels, lights, interiors; simplified drivetrain and motorcycle balance
Boat | WORKING | Driven water vehicle, steering and wave motion tested; arcade buoyancy
Helicopter | WORKING | Civilian/police variants, rotors, forward flight, climb/descent; flight tested
Airplane | WORKING | Throttle, heading, takeoff threshold, climb/descent and stall descent; flight tested
Aircraft realism | PARTIAL | Arcade swept movement; no aerodynamic simulator or articulated flight controls
Drive-by combat | PARTIAL | Small arms from a driven vehicle; no passengers or window/arm animation
Vehicle lights / horn / siren / engines | WORKING | Runtime light/audio controls and speed-dependent pitch
Vehicle damage / fire / explosion | PARTIAL | Health, collision damage, smoke, chain explosions, repair; no body deformation, broken glass or detachable panels
Garage customization | PARTIAL | Repair, paint, finish, performance multiplier, spoiler; no complete tuning/bodykit catalogue
Personal garage | PARTIAL | Stores/retrieves model identifiers; individual paint/condition/tuning is not retained
Weapons / inventory | WORKING | 12 weapons plus unarmed, ownership, reserve/magazine ammunition, selection, reload, rates and spread
Hitscan / damage / explosives | WORKING | Collision traces, head multiplier, shotgun pellets, bouncing grenades, rockets and radial damage
Combat presentation | PARTIAL | Recoil, zoom, flashes, impacts and simple effects; no polished reload/aim animation or penetration system
Weapon customization | PARTIAL | Suppressor, foregrip and extended magazine meshes with gameplay switches; flashlight; no attachment socket catalogue
Wanted 0–5 | WORKING | Crime heat, star display, witnesses, police escalation and escape path
Witnesses / pursuit / search | WORKING | Delayed living-witness reports, LOS tests, last-known position, decay while unseen
Appearance changes / busted | PARTIAL | Unseen paint/outfit changes accelerate search decay; one-star unarmed arrest proximity; simplified identity matching
Police ground / air response | WORKING | Pursuit cars, officers, tactical variant at high stars and helicopter from level 3
Police tactics / combat AI | PARTIAL | LOS shooting, chase, additional interceptors and dismount; no coordinated cover, sophisticated roadblocks or police boats
Physics / ragdolls | PARTIAL | Chaos hull impacts and simplified two-body character Physics Assets; no full articulated ragdoll tuning
Health / armor / death / recovery | WORKING | Armor absorption, damage, respawn, hospital/arrest cash fees and invulnerability option
Economy / supply store | PARTIAL | Paid supply bundle, repair fee and combat cash; no complete shop stock/pricing ecosystem
Safehouse | PARTIAL | Accessible simple COVE HOUSE interior, heal/save and wardrobe access; no property market
Clothing / appearance | PARTIAL | Whole-character outfit/appearance cycling; no modular garments, barber or face editor
Phone / personal services | NOT IMPLEMENTED | F1 sandbox service panel is not an in-world smartphone
Day / night | WORKING | Continuous clock, sun movement, night lighting and manual time selection
Weather | PARTIAL | Clear/cloud lighting, rain streaks/audio/wetness and fog; no storms, lightning or weather forecasting
Swimming / diving / breath | WORKING | Water detection, vertical swimming, oxygen consumption, drowning and scuba switch; tested
Underwater world | PARTIAL | Underwater color treatment; no authored seabed attractions or underwater fauna
Parachute | WORKING | Authored canopy/lines, limited descent speed, directional air control and landing reset; tested
Taxi passenger service | NOT IMPLEMENTED | No hired passenger route
Train / public transit / bicycle | NOT IMPLEMENTED | Bus-stop scenery only; no functional train/bus service or bicycle
Wildlife | NOT IMPLEMENTED | No ambient birds, fish or animals
HUD / minimap / full map | WORKING | Health, armor, ammo, money, stars, pursuit/search, speed and map markers
GPS navigation | PARTIAL | Click waypoint and routes to services; approximate grid polyline, not a road-graph route solver
Weapon wheel | WORKING | Slow-motion selection through Tab and scroll
Sandbox / benchmark menu | WORKING | Visible UMG buttons: travel, weather/time, vehicles, equipment, wanted, player and settings
Graphics / sound settings | PARTIAL | Quality cycling, volume, FPS display and save persistence; no full resolution/rebinding panel
Audio / ambience | PARTIAL | 12 synthesized sounds, gunshots, reload, impacts, engines, rotors, horn, siren, rain and city; no recorded dialogue
Radio / emergency dispatch | NOT IMPLEMENTED | No radio stations, ambulance/fire response or dispatch dialogue
VFX / Niagara | PARTIAL | Native mesh effects for sparks, flashes, smoke/explosion and rain; Niagara plugin enabled, no authored Niagara systems
Save / load | PARTIAL | Player state, inventory/magazines, outfit, attachments, skills, time/weather, garage models and preferences; no complete persistent population/damage world state
Skills | PARTIAL | Use-based values for several actions and lung-capacity effect; most stats lack balanced gameplay influence
Shooting range / stunt scoring / hobbies | NOT IMPLEMENTED | Free roam combat/driving possible; no dedicated scoring activities
Missionless scope | WORKING | No quests, campaign, mission markers or compulsory objectives
AI simulation tiers | PARTIAL | Distance-based despawn, population caps and slower thinking at distance; no Mass/StateTree simulation
Performance target | PARTIAL | Recorded sample windows on this machine; no guarantee of 60 FPS across hardware or all scenarios
