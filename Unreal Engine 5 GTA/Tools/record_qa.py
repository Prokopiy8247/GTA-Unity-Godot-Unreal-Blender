import pathlib,re,json,shutil
root=pathlib.Path(__file__).resolve().parent.parent
result={}
for label,filename in [('Editor game','.astra-run/runtime-final.log'),('Packaged Windows','.astra-run/packaged-test.log')]:
 text=(root/filename).read_text(encoding='utf-8',errors='replace')
 checks=[{'check':a,'status':b,'detail':c.strip()} for a,b,c in re.findall(r'PM_TEST_(\w+)=(PASS|FAIL)([^\r\n]*)',text)]
 result[label]={'complete':'PM_SMOKE_COMPLETE' in text,'checks':checks}
visual=(root/'.astra-run/packaged-visual-final.log').read_text(encoding='utf-8',errors='replace')
pattern=r'PM_CAPTURE (\S+): mean=([\d.]+)ms p95=([\d.]+)ms averageFPS=([\d.]+) frames=(\d+) people=(\d+) vehicles=(\d+)'
samples=[{'image':n,'mean_ms':float(m),'p95_ms':float(p),'average_fps':float(f),'frames':int(c),'people':int(h),'vehicles':int(v)} for n,m,p,f,c,h,v in re.findall(pattern,visual)]
extra=root/'.astra-run/packaged-ui-final.log'
if extra.exists():
 for n,m,p,f,c,h,v in re.findall(pattern,extra.read_text(encoding='utf-8',errors='replace')):
  samples=[item for item in samples if item['image']!=n]
  samples.append({'image':n,'mean_ms':float(m),'p95_ms':float(p),'average_fps':float(f),'frames':int(c),'people':int(h),'vehicles':int(v)})
result['render_samples']=samples
result['window_conditions']='Automated hidden-window run, 1600x900, r.ScreenPercentage=100, quality level 2, 90 FPS cap; standalone Development build.'
result['hardware']='AMD Ryzen 7 5700X3D / NVIDIA GeForce RTX 5070'
(root/'.astra-run/qa_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
rows=['# Port Meridian — validation evidence','','## Builds','','- Unreal_GTAEditor Win64 Development: succeeded.','- Unreal_GTA Win64 Development: succeeded.','- Windows cook/stage/pak/archive: succeeded. Final cook reports zero errors and zero warnings.','','## Runtime smoke checks','','Check | Editor game | Packaged Windows','--- | --- | ---']
for a,b in zip(result['Editor game']['checks'],result['Packaged Windows']['checks']):
 rows.append(a['check']+' | '+a['status']+' '+a['detail']+' | '+b['status']+' '+b['detail'])
rows+=['','Both runs reached PM_SMOKE_COMPLETE. Tests use actual Enhanced Input for walking/aircraft/boat, real collision traces for shooting, and saved UAssets/cooked content. Vehicle_0..12 checks only confirm mesh load; they are not separate driving tests for every vehicle. UMG validates widget construction, not every mouse interaction. ESCAPE advances search timers after removing police; it is a controlled state test, not a timed pursuit benchmark. Later changes concerned visual materials, HUD readability, spawn/port positions and labels.','','## Rendered capture windows','',result['window_conditions'],result['hardware'],'','Scene | Mean frame ms | P95 frame ms | Mean loop FPS | Frames | NPC / vehicles','--- | ---: | ---: | ---: | ---: | ---:']
for s in samples: rows.append(f"{s['image']} | {s['mean_ms']:.2f} | {s['p95_ms']:.2f} | {s['average_fps']:.1f} | {s['frames']} | {s['people']} / {s['vehicles']}")
rows+=['','Window-state inspection returned Visible=false. These are short instrumented game-loop windows in an automated hidden-window process, including effects of the 90 FPS cap; hidden-window rendering may skip work, so these figures must NOT be presented as interactive rendering FPS. They are not GPU-only timings, a long play session, a 1%-low benchmark or a guarantee for other machines. Teleport streaming may produce brief hitches outside the sampling window. Audio files loaded; no subjective listening test was performed.','','## Visual evidence','','Screenshots are actual rendered game frames from the packaged executable; no image-generation tool or retouching was used.','','## Logs','','Local detailed logs: .astra-run/build.log, package-final-verified.log, package-release.log, runtime-final.log, packaged-test.log and packaged-visual-final.log. They are left on disk, but excluded from Git. Compact machine-readable evidence is committed in .astra-run/qa_results.json.']
source=root/'Packaged/Windows/Unreal_GTA/.astra-run/screenshots'
dest=root/'QA/Screenshots';dest.mkdir(parents=True,exist_ok=True)
for s in samples:
 p=source/s['image']
 if p.exists():
  shutil.copy2(p,dest/p.name)
  rows.append(f"\n![{p.stem}](QA/Screenshots/{p.name})")
(root/'QA_RESULTS.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
print(json.dumps({'checks':{k:len(v['checks']) for k,v in result.items() if isinstance(v,dict) and 'checks' in v},'frames':len(samples)},indent=2))
