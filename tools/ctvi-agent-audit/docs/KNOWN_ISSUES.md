# Known issues and limits — 0.2.0

- Only normalized input schema 1.0 is supported. No provider-native, OpenTelemetry, AgentDojo or FalconX import adapter has been validated.
- Tests and bundled demos use synthetic fixtures. No customer trace, external benchmark or scientific validation dataset was used in this cycle.
- Order warnings reflect supplied record order. Concurrency, clock drift and retries require context. They do not establish causal influence or misconduct.
- Hash matches compare supplied bytes and a supplied digest; both may be fabricated. No signature chain, trusted timestamp, signer identity or artifact origin is verified.
- Missing events, fabricated records and misleading but structurally valid claims cannot be reliably detected.
- One result per call is the v1 convention. Streaming/multi-result calls need an explicit, reviewed normalization strategy.
- Filesystem guards require POSIX support. Linux/Python 3.12.14 was exercised; Windows file reading is unsupported; other Python versions and macOS remain untested.
- Runtime resource limits are not an OS sandbox. Concurrent malicious host administration, bind mounts, hostile filesystem implementations and multi-tenant isolation are out of scope. Failed reads are bounded per attempt but do not count toward the successful-byte total; artifact count is separately capped at 100.
- Reports suppress raw text/identifiers/paths, but outcomes, counts and content fingerprints can reveal information. No anonymization or sensitive-data-detection guarantee is made.
- The CLI does not keep a trace database or delete host files, caches, history, backups or email. Python/pip and the surrounding platform have their own storage behavior.
- Detailed findings are capped at 2,000; aggregate per-code counts remain complete. No calibrated score, CTVI construct validation, certification or market-demand claim is produced.
- The personal skill executes locally; actual public Plugin Directory review, client installation and publisher verification remain separate gates. No portal approval is implied by saving the skill.
- No hosted backend, SLA, paid subscription, automated support-ticket deletion or in-plugin commerce exists.
