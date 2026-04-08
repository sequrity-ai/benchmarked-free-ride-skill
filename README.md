# Benchmarked Free Ride Skill

OpenClaw skill to fetch model quality benchmarks and recommend the best free OpenRouter model.
Unlike other model pickers, rankings are based on **actual task performance** from daily CI benchmarks.

## What This Does

This skill connects to the [benchmarked-free-ride-ci](https://github.com/sequrity-ai/benchmarked-free-ride-ci) public API to:

1. **Recommend** the best free OpenRouter model by utility, security, speed, or a balanced score
2. **Show** detailed per-scenario benchmark breakdowns for any model
3. **Auto-configure** OpenClaw to use the top-performing free model

---

## Installation

```bash
# Install via clawhub (recommended)
clawhub install sequrity-ai/benchmarked-free-ride

# Or install locally from this repo
openclaw skills install ./
```

---

## Usage

All commands use `curl` + `jq` against the live leaderboard API. Run them directly in your terminal.

### Top 5 models by utility score (default)

```bash
curl -s "https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/leaderboard.json" | \
  jq -r '.leaderboard
    | map(select(.model_id | contains(":free")) | select(.is_benchmarked == true))
    | sort_by(-.composite_score) | .[:5] | to_entries[]
    | "\(.key + 1). \(.value.model_id)\n   Score: \(.value.composite_score) | Security: \(.value.cracker_security_rate // "n/a") | Latency: \(.value.avg_latency_seconds // "n/a")s"'
```

### --secure — Top models by prompt injection resistance

```bash
curl -s "https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/leaderboard.json" | \
  jq -r '.leaderboard
    | map(select(.model_id | contains(":free")) | select(.is_benchmarked == true) | select(.cracker_security_rate != null))
    | sort_by(-.cracker_security_rate) | .[:5] | to_entries[]
    | "\(.key + 1). \(.value.model_id)\n   Security: \(.value.cracker_security_rate)% | Score: \(.value.composite_score) | Latency: \(.value.avg_latency_seconds // "n/a")s"'
```

### --fast — Top models by response latency

```bash
curl -s "https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/leaderboard.json" | \
  jq -r '.leaderboard
    | map(select(.model_id | contains(":free")) | select(.is_benchmarked == true) | select(.avg_latency_seconds != null))
    | sort_by(.avg_latency_seconds) | .[:5] | to_entries[]
    | "\(.key + 1). \(.value.model_id)\n   Latency: \(.value.avg_latency_seconds)s | Score: \(.value.composite_score) | Security: \(.value.cracker_security_rate // "n/a")"'
```

### --balanced — Weighted score (utility 50% + security 30% + speed 20%)

```bash
curl -s "https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/leaderboard.json" | \
  jq -r '.leaderboard
    | map(select(.model_id | contains(":free")) | select(.is_benchmarked == true))
    | map(. + {balanced_score: ((.composite_score // 0) * 0.5 + (.cracker_security_rate // 50) * 0.3 + (if .avg_latency_seconds != null then (100 - (.avg_latency_seconds * 2 | if . > 100 then 100 else . end)) else 50 end) * 0.2)})
    | sort_by(-.balanced_score) | .[:5] | to_entries[]
    | "\(.key + 1). \(.value.model_id)\n   Balanced: \(.value.balanced_score | round) | Score: \(.value.composite_score) | Security: \(.value.cracker_security_rate // "n/a") | Latency: \(.value.avg_latency_seconds // "n/a")s"'
```

### --json — Machine-readable output for scripting

```bash
curl -s "https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/leaderboard.json" | \
  jq '[.leaderboard | map(select(.model_id | contains(":free")) | select(.is_benchmarked == true)) | sort_by(-.composite_score) | .[:5] | .[] | {model_id, composite_score, cracker_security_rate, avg_latency_seconds, context_length}]'
```

### --details \<model_id\> — Detailed breakdown for a specific model

```bash
MODEL_ID="google/gemini-2.0-flash-exp:free"   # replace with target model
curl -s "https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/models.json" | \
  jq -r --arg id "$MODEL_ID" '
    .models | map(select(.model_id == $id))
    | if length == 0 then "Model not found: \($id)"
      else .[0] | (
        "Model:    \(.model_id)",
        "Score:    \(.composite_score // "n/a") | Accuracy: \(.accuracy_percent // "n/a")% | Latency: \(.avg_latency_seconds // "n/a")s",
        "Context:  \((.context_length // 0) | tostring) tokens",
        "Tasks:    \(.passed_tasks // "?")/\(.total_tasks // "?")",
        "Updated:  \(.benchmarked_at // "unknown")",
        "",
        "Scenario Breakdown:",
        (.scenarios // [] | to_entries[] | "  \(.key+1). \(.value.name): \(.value.tasks_passed)/\(.value.tasks_total) tasks  (\(.value.avg_accuracy // 0 | round)% accuracy)")
      ) end
  '
```

### --auto — Auto-configure OpenClaw with the top model

```bash
MODEL_ID=$(curl -s "https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/leaderboard.json" | \
  jq -r '[.leaderboard | map(select(.model_id | contains(":free")) | select(.is_benchmarked == true)) | sort_by(-.composite_score)][0][0].model_id')
echo "Top model: $MODEL_ID"
openclaw config set agents.defaults.model.primary "openrouter/$MODEL_ID"
echo "Configured OpenClaw to use: $MODEL_ID"
```

---

## Quick Reference

| Goal | Flag | Sort key |
|------|------|----------|
| Best overall utility | *(default)* | `composite_score` ↓ |
| Most secure (anti-injection) | `--secure` | `cracker_security_rate` ↓ |
| Fastest responses | `--fast` | `avg_latency_seconds` ↑ |
| Balanced recommendation | `--balanced` | weighted composite ↓ |
| Scripting/automation | `--json` | composite_score ↓ |
| Full model breakdown | `--details <model_id>` | per-scenario accuracy |
| Auto-configure OpenClaw | `--auto` | top composite_score |

---

## How It Works

### Data Source

Fetches from the public GitHub Pages API:
- `https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/leaderboard.json` — ranked leaderboard
- `https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/models.json` — detailed per-model stats

Updated every 2 days by automated CI benchmarks.

### Scoring System

Models are ranked by **composite score** (0–100):

- **Accuracy** (70% weight) — Task success rate across benchmarks
- **Latency** (20% weight) — Response speed (lower is better)
- **Token Efficiency** (10% weight) — Output tokens per task (lower is better)

See [benchmarked-free-ride-ci](https://github.com/sequrity-ai/benchmarked-free-ride-ci) for methodology.

---

## Comparison with FreeRide

| Feature | FreeRide | Benchmarked Free Ride |
|---------|----------|----------------------|
| Model discovery | ✅ OpenRouter API | ✅ OpenRouter API |
| Ranking criteria | Context, capabilities, recency | **Actual benchmark performance** |
| Security ranking | ✅ (`--secure`) | ✅ (`--secure`) |
| Speed ranking | ✅ (`--fast`) | ✅ (`--fast`) |
| Balanced ranking | ✅ (`--balanced`) | ✅ (`--balanced`) |
| Per-model breakdown | ❌ | ✅ (`--details`) |
| Auto-configure OpenClaw | ❌ | ✅ (`--auto`) |
| Daily CI updates | ✅ (same source) | ✅ (same source) |
| Public leaderboard | ✅ | ✅ |

---

## Development

### Local Testing

```bash
# Clone skill repo
git clone https://github.com/sequrity-ai/benchmarked-free-ride-skill.git
cd benchmarked-free-ride-skill

# Test a command directly
curl -s "https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/leaderboard.json" | \
  jq '.leaderboard | length'
```

### Publishing to ClawHub

```bash
clawhub skill publish . \
  --slug benchmarked-free-ride \
  --name "Benchmarked Free Ride" \
  --version 1.1.0 \
  --changelog "Add SKILL.md format with --details and --auto commands; align with free-ride reference skill" \
  --tags "free-models,openrouter,benchmark,model-selection,leaderboard"
```

Run with `--dry-run` first to validate the manifest before publishing.

### Python CLI (legacy)

The original Python package (`main.py`) is still available for backwards compatibility:

```bash
pip install -e .
benchmarked-free-ride leaderboard
benchmarked-free-ride details "google/gemini-2.0-flash-exp:free"
benchmarked-free-ride auto
```

---

## Troubleshooting

### "null" model ID from --auto

**Cause:** The leaderboard has no models matching `:free` + `is_benchmarked == true`.

**Fix:** Check the live leaderboard first:
```bash
curl -s "https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/leaderboard.json" | jq '.leaderboard | length'
```

### "Model not found" in --details

**Cause:** Model ID typo or model not in `models.json` (only benchmarked models appear).

**Fix:** Check available model IDs:
```bash
curl -s "https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/models.json" | jq -r '.models[].model_id'
```

### "Failed to configure model" from --auto

**Cause:** `openclaw` CLI not on PATH or not logged in.

**Fix:**
```bash
which openclaw   # verify it's on PATH
openclaw login   # re-authenticate if needed
```

---

## Related Projects

- [benchmarked-free-ride-ci](https://github.com/sequrity-ai/benchmarked-free-ride-ci) — CI runner that generates benchmarks
- [FreeRide](https://github.com/openclaw/skills/tree/main/skills/shaivpidadi/free-ride) — Reference skill this was modeled after
- [OpenClaw](https://github.com/openclaw/openclaw) — AI agent framework

---

## License

MIT License. See LICENSE file for details.
