"""Execute synthetic review cases with the official MCP client; print compact facts."""
import asyncio
import json
import sys
from pathlib import Path
from mcp import Client
from mcp.client.streamable_http import streamable_http_client
import httpx2

async def main():
    url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765/mcp'
    root=Path(__file__).resolve().parent
    transcript=[]
    async with httpx2.AsyncClient(trust_env=False) as http_client, Client(streamable_http_client(url,http_client=http_client)) as client:
        tools=await client.list_tools()
        for case_id in ['P1','P2','P3','N1']:
            case=json.loads((root/'review_cases'/f'{case_id}.json').read_text())
            result=await client.call_tool(case['tool'],case['arguments'])
            report=(result.structured_content or {}).get('report')
            row={'case':case_id,'label':case['label'],'tool':case['tool'],'input_format':case['arguments'].get('input_format','json'),'synthetic':True,'is_error':result.is_error}
            if report:
                row.update({'structural_status':report['structural_status'],'event_count':report['counts']['events'],'finding_count':report['counts']['findings'],'finding_codes':sorted(report['finding_code_counts']),'outcome_verification':report['outcome_verification'],'scientific_validity':report['scientific_validity']})
            else: row['error']=[part.text for part in result.content if hasattr(part,'text')]
            transcript.append(row)
    print(json.dumps({'recording_type':'Actual SDK calls; synthetic input; not ChatGPT UI or directory approval','endpoint':url,'cases':transcript},indent=2))

if __name__=='__main__': asyncio.run(main())
