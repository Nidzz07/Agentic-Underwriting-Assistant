"""observability (U21, EPIC-6, Phase 2) — the emit-only telemetry SINK/WIRING unit.

Defines the injected trace/metric Protocols + the pure allowlist projection that make
the already-built system observable, WITHOUT editing any frozen unit (BR-OBS-1 / NOEDIT-1).
The LIVE Langfuse/Prometheus SDK binding is deferred to composition/deploy-config
(``OBS-SINK-DEFERRED``); this package builds the injected Protocols + their offline fakes only.
"""
