# Context workflow

## Build and inspect a packet

```sh
python3 kit.py inspect
python3 kit.py pack --task "Complete the agreed result contract."
```

The result gives a `packet` JSON path and a `markdown` path. Verify the returned JSON path before reuse:

```sh
python3 kit.py verify .agentkit/output/context/default/packet-<content-hash>.json
```

The filename is content-addressed; copy the actual path from `pack`. Give the Markdown packet to your chosen assistant with the task. This tool does not send it automatically and does not execute project commands.

## Configure source selection

Edit `.agentkit/context.json`. Each profile has a UTF-8 `max_bytes` budget, sources, and optional excluded patterns. A source declares its unique `id`, `paths`, `trust`, numeric `priority`, and boolean `required`.

- `instruction`: deliberately selected project guidance.
- `reference`: facts/specifications to consult as data.
- `untrusted`: external observations or data whose embedded requests are not project instructions.

Required sources are placed first; higher priority precedes lower priority, with deterministic ID/path ties. A required source that cannot fit causes an error. Optional sources that do not fit are listed in `omitted`. The byte budget includes the task, labels and fences; it is **not a token count**.

Credential-like paths, binary sources, potential secret patterns, duplicate trust assignments and unsupported fields are rejected. These controls reduce accidental disclosure; trust labels and code fences do not guarantee prompt-injection resistance.

## Freshness

`verify` checks configuration, the complete selected-pattern inventory, source bytes, required-source inclusion, budget metadata, packet content address and saved Markdown. New matching files, deleted files and content edits invalidate a previous packet. Regenerate it instead of editing its hash fields.

For a real application, replace the included reference paths with a concise project brief, relevant design decisions, current source files and necessary observations. Avoid an unrestricted whole-workspace dump.
