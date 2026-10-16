"""Pure bounded RPC operations. No user-controlled file or network reads."""
import json
from jsonschema import Draft202012Validator
from . import __version__
from .engine import core, catalog

MAX_TRACE_BYTES = 262144
MAX_EVENTS = 1000
MAX_EVIDENCE = 4000
MAX_REPORT_BYTES = 524288
AUDIT_INPUT = {"type":"object","additionalProperties":False,"required":["trace_json"],"properties":{
    "trace_json":{"type":"string","minLength":1,"maxLength":MAX_TRACE_BYTES,"description":"User-supplied redacted normalized schema 1.0 JSON or JSONL text. Never a filename or URL. Maximum 256 KiB UTF-8, 1000 events."},
    "input_format":{"type":"string","enum":["json","jsonl"],"default":"json"}}}
CHECKS_INPUT = {"type":"object","properties":{},"additionalProperties":False}
REPORT_SCHEMA = {"type":"object","required":["readiness","assessment_scope","structural_status","outcome_verification","scientific_validity","counts","findings","artifact_verification","limitations"],"properties":{
    "readiness":{"const":"PROTOTYPE"},"assessment_scope":{"const":"STRUCTURAL_CHECKS_OF_USER_SUPPLIED_RECORDS_ONLY"},
    "structural_status":{"enum":["ISSUES_OBSERVED","INCOMPLETE_EVIDENCE","NO_ISSUES_OBSERVED_WITHIN_CHECKS"]},
    "outcome_verification":{"const":"NOT_PERFORMED"},"scientific_validity":{"const":"NOT_ASSESSED"},
    "counts":{"type":"object","additionalProperties":{"type":"integer","minimum":0}},
    "findings":{"type":"array","maxItems":2000,"items":{"type":"object","required":["code","severity"],"additionalProperties":False,"properties":{"code":{"type":"string"},"severity":{"enum":["error","warning","unknown"]},"event_index":{"type":"integer","minimum":0},"artifact_index":{"type":"integer","minimum":0}}}},
    "artifact_verification":{"type":"object","required":["requested","attempted","digest_matches","bytes_read"],"additionalProperties":False,"properties":{"requested":{"const":False},"attempted":{"const":0},"digest_matches":{"const":0},"bytes_read":{"const":0}}},
    "limitations":{"type":"array","items":{"type":"string"}}}}
AUDIT_OUTPUT={"type":"object","additionalProperties":False,"required":["adapter_version","engine_version","report"],"properties":{"adapter_version":{"const":__version__},"engine_version":{"const":"0.2.0"},"report":REPORT_SCHEMA}}
CHECKS_OUTPUT={"type":"object","additionalProperties":False,"required":["adapter_version","engine_version","checks","limits","scope"],"properties":{"adapter_version":{"const":__version__},"engine_version":{"const":"0.2.0"},"checks":{"type":"array","items":{"type":"object","required":["code","meaning","next_action"],"additionalProperties":False,"properties":{"code":{"type":"string"},"meaning":{"type":"string"},"next_action":{"type":"string"}}}},"limits":{"type":"object","additionalProperties":{"type":"integer"}},"scope":{"type":"string"}}}
INPUTS={"audit_normalized_trace":AUDIT_INPUT,"list_audit_checks":CHECKS_INPUT}
OUTPUTS={"audit_normalized_trace":AUDIT_OUTPUT,"list_audit_checks":CHECKS_OUTPUT}
for schema in [*INPUTS.values(),*OUTPUTS.values()]: Draft202012Validator.check_schema(schema)
VALIDATORS={key:Draft202012Validator(value) for key,value in INPUTS.items()}
OUTPUT_VALIDATORS={key:Draft202012Validator(value) for key,value in OUTPUTS.items()}

class RequestRejected(ValueError):
    """Fixed safe error code only."""

def invoke(name, arguments):
    if name not in INPUTS: raise RequestRejected("UNKNOWN_TOOL")
    if not VALIDATORS[name].is_valid(arguments): raise RequestRejected("INVALID_TOOL_ARGUMENTS")
    if name=="list_audit_checks":
        result={"adapter_version":__version__,"engine_version":"0.2.0","checks":[{"code":code,"meaning":value[0],"next_action":value[1]} for code,value in sorted(catalog.CHECKS.items())],"limits":{"trace_utf8_bytes":MAX_TRACE_BYTES,"events":MAX_EVENTS,"total_evidence_references":MAX_EVIDENCE,"report_utf8_bytes":MAX_REPORT_BYTES},"scope":"Structural declared-record checks only. No scientific validity score, certification, artifact file access, replay or external retrieval."}
    else:
        try: raw=arguments["trace_json"].encode("utf-8")
        except UnicodeError: raise RequestRejected("INVALID_UTF8") from None
        if len(raw)>MAX_TRACE_BYTES: raise RequestRejected("TRACE_SIZE_LIMIT")
        try:
            trace=core.parse_bytes(raw,arguments.get("input_format","json"))
            if len(trace["events"])>MAX_EVENTS: raise RequestRejected("MCP_EVENT_COUNT_LIMIT")
            if sum(len(e.get("evidence",[])) for e in trace["events"])>MAX_EVIDENCE: raise RequestRejected("MCP_EVIDENCE_COUNT_LIMIT")
            report=core.audit(trace,artifact_root=None)
        except core.InputError as exc: raise RequestRejected(str(exc)) from None
        result={"adapter_version":__version__,"engine_version":"0.2.0","report":report}
    if not OUTPUT_VALIDATORS[name].is_valid(result): raise RequestRejected("INTERNAL_OUTPUT_SCHEMA_ERROR")
    if len(json.dumps(result,ensure_ascii=True).encode())>MAX_REPORT_BYTES: raise RequestRejected("REPORT_SIZE_LIMIT")
    return result
