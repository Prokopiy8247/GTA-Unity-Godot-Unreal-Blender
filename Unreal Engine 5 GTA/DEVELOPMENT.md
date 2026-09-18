# Port Meridian вЂ” development
Original missionless single-player sandbox in the existing Unreal_GTA project.

## Environment and baseline
- Start: 2026-09-18 06:07:21 +02:00 / 04:07:21 UTC.
- Unreal Engine 5.8.2, CL 56702186.
- Blender 5.2.2 LTS. All important 3D models authored through blender_unreal, port 9878, in this project's UnrealGTA.blend.
- Existing project initially contained only a blank native module; Content was empty. The private local baseline is not part of the public history.
- All 2802 lines of the supplied benchmark specification were read before implementation.
- No downloaded models, textures, asset packs or copyrighted game content.

## Run
Double-click Launch_PortMeridian.cmd to use the cooked Windows build. Alternatively, open Unreal_GTA.uproject and press Play.
The project opens /Game/GTA/Maps/PortMeridian and uses native PMGameMode.
No manual Blueprint wiring, importing, actor placement or property assignment is needed.

## Controls
Control | Action
--- | ---
WASD / mouse | Movement / camera; drive and steer in a vehicle
Shift | Sprint
Space | Jump/vault; handbrake in land vehicles; climb in aircraft
Ctrl | Descend aircraft / dive in water
F | Enter/exit nearby vehicle
E | Storefront supplies, repair garage or safehouse save
LMB / RMB | Fire or melee / aim
R | Reload
1вЂ“9 / mouse wheel | Weapon selection
Tab + wheel | Slow-motion equipment selection
Q / C | Contextual cover / crouch
V | First-person camera toggle on foot
H / L | Horn/emergency siren / vehicle headlights
P | Deploy parachute while falling
F1 | Sandbox services menu
M | Full map; click to set a waypoint
F5 / F9 | Save / load
Escape | Menu; resumes if paused

Aircraft use W/S for forward power, A/D for heading, Space/Ctrl for climb/descent. The airplane needs forward airspeed to climb. Boats belong in Meridian Bay.

## World
272 saved spatial sectors, each 250 Г— 250 m, cover 4 Г— 4.25 km (17 kmВІ including sea). The world uses World Partition, a native spatial hash with 250 m cells and 850 m loading radius, plus HISM batches, Nanite environment assets and distance culling.

Districts: Meridian Downtown, Willow Gardens, Foundry District, Eastport Docks, Solace Coast, Meridian Airfield, North County, Cedar Highlands, West Boulevard. The port has a crane and pier; the coast has a lighthouse; the hills use authored terrain meshes. COVE HOUSE is a small accessible interior near the starting district. This is a generated world, with repeated architecture and a regular road grid.

## Native systems
- PMCharacter.cpp: character/camera, procedural skeletal posing, combat, cover, crouch, swimming, diving/breath, parachute, shops, save/load.
- PMVehicle.cpp: authored vehicle meshes, separate wheels, Chaos rigid-body hulls with four ray suspension forces, ground grip, traffic steering, water/air movement, damage, repairs and simple modifications.
- PMWorld.cpp: spawn/despawn rings, pedestrians, police, witnesses, 0вЂ“5 wanted escalation, LOS pursuit/search, weather/day cycle, generated sound, effects, smoke tests and automatic screenshots.
- PMContent.cpp: vehicle/weapon definitions and sector generation.
- PMUI.cpp: Enhanced Input, native UMG menu and HUD/radar/map.
- PMEditorLibrary.cpp: explicit Skeleton/PhysicsAsset generation and World Partition configuration.

Visible characters use Blender-authored Skeletal Meshes and procedural bone transforms. The small Physics Assets provide a simplified physical death reaction. Blueprint children are available for inspection/composition; runtime does not depend on hand-built graphs.

## Content pipeline
1. Tools/blender_*.py record the asset-generation scripts that were actually run through Blender MCP.
2. SourceAssets/BlenderExports contains engine-ready FBX exports.
3. SourceAssets/manifest.json records the actual materials, dimensions and vertex counts.
4. Tools/generate_audio.py creates original WAV files.
5. Tools/import_assets.py imports content and assigns shared PBR material instances.
6. Tools/build_world.py creates the saved map, sectors, lighting, signs and Blueprint children.
7. Tools/repair_content.py explicitly creates/saves Skeleton and Physics Assets, verifies materials, enables volumetric fog and configures streaming.
8. Tools/update_art.py imports the visual QA revisions without discarding Skeleton/PhysicsAsset references.

Use forward slashes in paths passed to -ExecutePythonScript; Unreal's Python command parser can interpret Windows backslash sequences.

## Build and validation
Editor target builds with the installed engine's Build.bat / UnrealBuildTool.
First runtime crash (missing Skeleton) was diagnosed and corrected by explicit creation/saving of Skeleton and Physics Assets.
The subsequent headless gameplay run confirmed mesh loading, 13 vehicle meshes, walking (1,233 cm), enter/drive/exit (11,066 cm driven), damage/death, save/load and police ground/air response. Extended tests also exercise helicopter/boat controls, underwater breath, parachute, search decay, shops, garage repair and airplane takeoff. See QA_RESULTS.md for final results and their limits.

Current detailed logs live in .astra-run. Logs, shader caches, binaries and Saved are not committed.

## Practical limits
Both Editor and Game targets have compiled successfully. Packaging status and final runtime evidence are recorded in ASTRA_FINAL_REPORT.md.

This remains a procedurally authored prototype rather than AAA production content. Character anatomy/animation, vehicle interiors, environment variation, traffic decisions and combat AI are simplified. See FEATURE_MATRIX.md for exact implemented/partial/missing systems. No missions, quest markers, campaign or story progression exist.

## Rendering and enabled plugins
DirectX 12 / SM6, software Lumen GI/reflections, Virtual Shadow Maps, Substrate, Nanite environments, Sky Atmosphere, volumetric clouds/fog. Hardware ray tracing is disabled. Runtime defaults to quality level 2 and a 90 FPS cap; F1 offers quality and volume controls.

Explicit plugins: ModelingToolsEditorMode (Editor), PythonScriptPlugin, EditorScriptingUtilities, EnhancedInput, Niagara, ProceduralMeshComponent. Niagara is available but current effects use native mesh particles.

## Visual QA fixes
Missing skeletal Skeleton references, missing skeletal material assignments, shared-material skeletal/instancing usage flags, native UMG tree construction, physical sunlight/exposure levels and teleport screenshot timing were diagnosed in actual runs and corrected. Trees were rebuilt through Blender MCP with individual leaf geometry.

Tools/polish_world.py, fix_character_materials.py, update_trees.py and polish_extras.py reproduce the later lighting/material/tree/water/attachment revisions after the base content pipeline. They must run in that order after import/build/repair/update_art when rebuilding from FBX. The delivered .uasset/.umap files already contain these changes.

## Final validation
The Editor game and packaged Windows executable each passed all 31 smoke checks. The final content cook completed with zero errors and zero warnings. Nine final packaged-game screenshots are in QA/Screenshots. Frame-loop measurements were taken with a hidden window and must not be interpreted as interactive GPU FPS.
