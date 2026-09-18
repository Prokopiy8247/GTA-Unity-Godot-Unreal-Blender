import argparse, json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('--session-log',required=True)
parser.add_argument('--start-utc',required=True)
args=parser.parse_args()
rows=[]
for line in Path(args.session_log).read_text(encoding='utf-8').splitlines():
    try: item=json.loads(line)
    except json.JSONDecodeError: continue
    p=item.get('payload',{})
    if item.get('type')=='event_msg' and p.get('type')=='token_count' and p.get('info'):
        rows.append((item['timestamp'],p['info']))
assert rows, 'No actual token telemetry'
cutoff,info=rows[-1]
total=info['total_token_usage']
fields=['input_tokens','cached_input_tokens','cache_write_input_tokens','output_tokens']
sums={k:sum(r.get('last_token_usage',{}).get(k,0) for _,r in rows) for k in fields}
assert all(sums[k]==total.get(k,0) for k in fields), 'Request and cumulative counters disagree'
pricing=json.loads(Path('.astra-run/pricing.json').read_text(encoding='utf-8-sig'))
rates=pricing['per_million']
cost=Decimal(0);long_requests=0;maximum=0
for _,record in rows:
    u=record['last_token_usage'];input_count=u['input_tokens'];maximum=max(maximum,input_count)
    cached=u.get('cached_input_tokens',0);written=u.get('cache_write_input_tokens',0)
    is_long=input_count>pricing['long_context_threshold'];long_requests+=int(is_long)
    im=Decimal(str(pricing['long_input_multiplier'] if is_long else 1))
    om=Decimal(str(pricing['long_output_multiplier'] if is_long else 1))
    cost+=(Decimal(input_count-cached-written)*Decimal(str(rates['input']))+Decimal(cached)*Decimal(str(rates['cached_input']))+Decimal(written)*Decimal(str(rates['cache_write'])))*im/1000000
    cost+=Decimal(u['output_tokens'])*Decimal(str(rates['output']))*om/1000000
start=datetime.fromisoformat(args.start_utc.replace('Z','+00:00'));end=datetime.now(timezone.utc)
elapsed=(end-start).total_seconds();seconds=round(elapsed);hours,remain=divmod(seconds,3600);minutes,secs=divmod(remain,60)
summary={'start_utc':start.isoformat(),'end_utc':end.isoformat(),'elapsed_seconds':elapsed,'telemetry_cutoff_utc':cutoff,'model':'gpt-6-astra','reasoning_effort':'xhigh','total_token_usage':total,'request_count':len(rows),'maximum_request_input':maximum,'long_context_requests':long_requests,'token_only_api_equivalent_usd':str(cost),'pricing_source':pricing['source'],'token_log':args.session_log,'request_counter_reconciliation':sums}
Path('.astra-run/session-usage-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
Path('.astra-run/end_time.txt').write_text(end.isoformat()+'\n',encoding='utf-8')
section=f'''\n## Astra Session Metrics

Start: {start.isoformat()} (19:22:07 Europe/Warsaw, earliest recorded clock reading)
End: {end.isoformat()} (final report cutoff)
Elapsed: {hours:02}:{minutes:02}:{secs:02}
Elapsed minutes: {elapsed/60:.3f}
Elapsed hours: {elapsed/3600:.5f}

Model: gpt-6-astra
Reasoning effort (if available): xhigh

Input tokens: {total['input_tokens']:,} (includes cached input)
Cached input tokens: {total['cached_input_tokens']:,}
Cache-write tokens: {total.get('cache_write_input_tokens',0):,}
Output tokens: {total['output_tokens']:,} (includes reasoning)
Reasoning tokens (if separately available): {total.get('reasoning_output_tokens',0):,} (subset of output; not added twice)
Total tokens: {total['total_tokens']:,}

GPT-6 Astra token-only API-equivalent cost: USD {cost:.6f} (approximately USD {cost:.2f}; calculated equivalent, not billed cost)
Pricing rates/source used: per 1M tokens — uncached input $10, cached input $1, cache write $12.50, output $50; {pricing['source']} (retrieved 2026-09-17).
Long-context adjustment: {long_requests} requests above 272,000 input tokens; maximum observed request input {maximum:,}. Per-request calculation applies 2x input/cache and 1.5x output above that threshold.
External tool/API fees included: No
Confidence / data source: Exact available cumulative token counters at {cutoff}, reconciled against {len(rows)} per-request input/cache/output records in the current session JSONL. Time is measured wall time through final report generation; start precision is one second. The original OS start file was written 35.746 seconds later and is retained separately. Price is an estimate using published API rates; subscription billing and final-response overhead are excluded. See .astra-run/session-usage-summary.json.

Blender MCP server used: blender_unity
Blender port: 9876
Blender master file: UnityGTA.blend
Approximate number of major Blender assets created: 54 integrated original models, plus 11 LOD exports
'''
p=Path('ASTRA_FINAL_REPORT.md');body=p.read_text(encoding='utf-8-sig').split('\n## Astra Session Metrics')[0];p.write_text(body+section,encoding='utf-8')
print(json.dumps(summary,indent=2))
