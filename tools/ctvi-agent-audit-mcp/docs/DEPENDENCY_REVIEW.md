# Dependency review

Official MCP SDK 2.3.0 is pinned together with exact runtime and build dependency versions in requirements.lock. Package/license records and copied upstream notices are in THIRD_PARTY_LICENSES.json and third_party_licenses/. These dependencies are not relicensed by the utility MIT notice.

The initial pip-audit 2.10.1 scan returned two duplicate entries for one unique build-tool advisory, PYSEC-2026-3447 / CVE-2026-59890, affecting setuptools 82.0.1. The build pin was updated to 83.0.0, the reported fixed version, before final rebuild. Final scan evidence is kept separately; a successful scan is a point-in-time advisory match, not proof of vulnerability absence.

Exact version pins do not supply artifact-level hash enforcement. Reassess advisories, verify package provenance and select an immutable container base digest before an Internet-facing deployment. No third-party runtime package source is copied into the utility engine.
