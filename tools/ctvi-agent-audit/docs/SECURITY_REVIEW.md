# Security and dependency review

Scope: local source review and automated synthetic tests of v0.2.0. This is not independent certification or a production penetration test.

Threats considered: path traversal, absolute/URL artifact paths, symlink races, symlinked directory/root, hardlinks outside the intended root, blocking FIFO reads, oversize files, duplicate JSON keys, unsupported or malformed records, control-string leakage, unbounded detailed output, and accidental network/code execution from trace text.

Controls: open-at directory-descriptor traversal with `O_NOFOLLOW`; regular-file and link-count checks; bounded reads; change-during-read checks; conservative JSON/schema limits; fixed diagnostic codes; no raw prose/path/ID echo; fixed deterministic report fields. No socket, HTTP, subprocess, exec/eval, pickle, YAML object loader, shell command or third-party package exists in runtime code. Test code uses subprocess only to verify CLI behavior.

Residual risks: no OS sandbox or CPU/memory watchdog; malicious authorized host/mount manipulation is outside scope; hashes cannot establish authorship or authenticity; declared timestamps may be false; provenance linkage may be complete yet misleading; unsupported provider formats need explicit adapters; fingerprint/count leakage remains possible; host retention is not controlled by this CLI. Safe file access is POSIX-specific and must fail closed elsewhere. Runtime standard-library security follows the installed Python version; no vulnerability-database completeness claim is made.

Dependency inventory: Python standard library only. No package installation or vulnerability scan of third-party dependencies was necessary. No repository or research code was copied; fixtures are new synthetic examples. Public license remains unresolved.
