"""Record a measured session cutoff, without inventing unreported token categories."""
import json, pathlib, datetime, re, argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("session", type=pathlib.Path, help="Local session JSONL (never committed or uploaded)")
args = parser.parse_args()
ROOT=pathlib.Path(__file__).resolve().parent.parent
SESSION=args.session
events=[]; contexts=[]
for line in SESSION.open(encoding='utf-8'):
    try: d=json.loads(line)
    except json.JSONDecodeError: continue
    if d.get('type')=='turn_context': contexts.append(d['payload'])
    if d.get('type')=='event_msg' and d.get('payload',{}).get('type')=='token_count' and d['payload'].get('info'): events.append(d)
end=datetime.datetime.now().astimezone()
stamp=(ROOT/'.astra-run/start_time.txt').read_text(encoding='utf-8-sig').strip()
stamp=re.sub(r'(\.\d{6})\d+(?=[+-]|Z|$)',r'\1',stamp)
start=datetime.datetime.fromisoformat(stamp)
elapsed=(end-start).total_seconds()
last=events[-1]; usage=last['payload']['info']['total_token_usage']
uncached=usage['input_tokens']-usage['cached_input_tokens']-usage.get('cache_write_input_tokens',0)
cost=(uncached*10+usage['cached_input_tokens']+usage.get('cache_write_input_tokens',0)*12.5+usage['output_tokens']*50)/1_000_000
max_input=max(e['payload']['info']['last_token_usage']['input_tokens'] for e in events)
if max_input>272000: raise RuntimeError('Recompute per-request long-context pricing; aggregate rates would be insufficient.')
source='https://developers.openai.com/api/docs/models/gpt-6-astra'
data={'start':start.isoformat(),'end':end.isoformat(),'elapsed_seconds':elapsed,'model':contexts[-1].get('model'),'reasoning_effort':contexts[-1].get('effort'),'usage_snapshot_utc':last['timestamp'],'token_usage':usage,'uncached_input_tokens':uncached,'max_observed_request_input_tokens':max_input,'cost_usd_standard_token_only':cost,'rates_per_million':{'uncached_input':10,'cached_input':1,'cache_write':12.5,'output':50},'pricing_source':source,'long_context_adjustment':'None: every observed request below 272K input tokens','data_source':'Local session usage snapshot (private path omitted)','scope':'Cumulative task usage snapshot; later bookkeeping and final response excluded. Reasoning tokens are included in output. This is not an invoice.'}
(ROOT/'.astra-run/end_time.txt').write_text(end.isoformat()+'\n',encoding='utf-8')
(ROOT/'.astra-run/session_metrics.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
hours=int(elapsed//3600);minutes=int(elapsed%3600//60);seconds=int(elapsed%60)
block=f"""
## Astra Session Metrics

Start: {start.isoformat()}
End: {end.isoformat()}
Elapsed: {hours:02d}:{minutes:02d}:{seconds:02d}
Elapsed minutes: {elapsed/60:.2f}
Elapsed hours: {elapsed/3600:.4f}
Model: {data['model']}
Reasoning effort (if available): {data['reasoning_effort']}
Input tokens: {usage['input_tokens']:,} total, including cache; {uncached:,} uncached
Cached input tokens: {usage['cached_input_tokens']:,}
Cache-write tokens: {usage.get('cache_write_input_tokens',0):,}
Output tokens: {usage['output_tokens']:,}, including reasoning
Reasoning tokens (if separately available): {usage.get('reasoning_output_tokens','unreported'):,}; already included in output, not added again
Total tokens: {usage['total_tokens']:,}
GPT-6 Astra token-only API-equivalent cost: US${cost:.4f} (Standard-rate estimate from measured usage)
Pricing rates/source used: US$10 / US$1 / US$12.50 / US$50 per million uncached input / cached input / cache writes / output; [official model pricing]({source}), checked 2026-09-18
Long-context adjustment: None; largest observed request input {max_input:,}, below the 272,000 threshold
External tool/API fees included: No
Confidence / data source: Actual cumulative total_token_usage from this task's Codex JSONL; snapshot {last['timestamp']}. Duplicate cumulative snapshots were not summed. Subsequent bookkeeping/final-response tokens are excluded. This is an API-equivalent calculation, not a charged invoice.
Blender MCP server used: blender_unreal
Blender port: 9878
Blender master file: UnrealGTA.blend
Approximate number of major Blender assets created: 54 major models; 70 exported meshes including accessories and helper geometry

Cost formula: ({uncached:,} × 10 + {usage['cached_input_tokens']:,} × 1 + {usage.get('cache_write_input_tokens',0):,} × 12.5 + {usage['output_tokens']:,} × 50) / 1,000,000.
"""
# Markdown hard breaks keep the requested one-metric-per-line structure readable.
block='\n'.join(line+'  ' if ': ' in line and not line.startswith('Cost formula') else line for line in block.splitlines())+'\n'
report=ROOT/'ASTRA_FINAL_REPORT.md'
report.write_text(report.read_text(encoding='utf-8').split('## Astra Session Metrics')[0].rstrip()+'\n'+block,encoding='utf-8')
print(json.dumps(data,indent=2))
