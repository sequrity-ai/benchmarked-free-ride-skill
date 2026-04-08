# Benchmarked Free Ride Skill

OpenClaw skill to fetch model quality benchmarks and recommend the best free OpenRouter model.
Unlike other model pickers, rankings are based on **actual task performance** from daily CI benchmarks.

## What This Does

This skill connects to the [benchmarked-free-ride-ci](https://github.com/sequrity-ai/benchmarked-free-ride-ci) public API to:

1. **Auto-configure** OpenClaw to use the top-performing free model with fallbacks
2. **List** all benchmarked free models ranked by utility or security score
3. **Switch** to a specific model instantly
4. **Manage fallbacks** independently from the primary model

---

## Installation

```bash
# Install via clawhub (recommended)
clawhub install sequrity-ai/benchmarked-free-ride

# Or install locally from this repo
pip install -e .
```

---

## Usage

### Auto-configure best model + fallbacks

```bash
benchmarked-free-ride auto
```

### Auto-configure, keep existing primary — update fallbacks only

```bash
benchmarked-free-ride auto -f
```

### Auto-configure with custom fallback count

```bash
benchmarked-free-ride auto -c 10
```

### Auto-configure prioritizing security (prompt injection resistance)

```bash
benchmarked-free-ride auto --secure
```

### List all free models ranked by benchmark score

```bash
benchmarked-free-ride list
```

### List models ranked by security rating

```bash
benchmarked-free-ride list --secure
```

### Switch primary model to a specific model

```bash
benchmarked-free-ride switch google/gemini-2.0-flash-exp:free
```

### Show current model configuration

```bash
benchmarked-free-ride status
```

### Update fallback models only (keep existing primary)

```bash
benchmarked-free-ride fallbacks
```

### Update fallbacks prioritized by security rating

```bash
benchmarked-free-ride fallbacks --secure
```

### Force refresh cached model list

```bash
benchmarked-free-ride refresh
```

---

## Quick Reference

| Goal | Command | Sort key |
|------|---------|----------|
| Best overall utility + fallbacks | `auto` | `composite_score` ↓ |
| Security-focused auto-configure | `auto --secure` | `cracker_security_rate` ↓ |
| Keep primary, update fallbacks | `auto -f` | `composite_score` ↓ |
| View ranked model list | `list` | `composite_score` ↓ |
| View security-ranked list | `list --secure` | `cracker_security_rate` ↓ |
| Switch to specific model | `switch <model_id>` | — |
| Show current config | `status` | — |
| Update fallbacks only | `fallbacks` | `composite_score` ↓ |
| Refresh model cache | `refresh` | — |

---

## How It Works

### Data Source

Fetches from the public GitHub Pages API — **no API key required**:
- `https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/leaderboard.json` — ranked leaderboard
- `https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/models.json` — detailed per-model stats

Updated every 2 days by automated CI benchmarks.

### Scoring System

Models are ranked by **composite score** (0–100):

- **Accuracy** (70% weight) — Task success rate across benchmarks
- **Latency** (20% weight) — Response speed (lower is better)
- **Token Efficiency** (10% weight) — Output tokens per task (lower is better)

See [benchmarked-free-ride-ci](https://github.com/sequrity-ai/benchmarked-free-ride-ci) for methodology.

### Config Keys Set

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "openrouter/google/gemini-2.0-flash-exp:free",
        "fallbacks": ["openrouter/...", "openrouter/..."]
      },
      "models": ["openrouter/...", "openrouter/..."]
    }
  }
}
```

---

## Comparison with FreeRide

| Feature | FreeRide | Benchmarked Free Ride |
|---------|----------|----------------------|
| Model discovery | ✅ OpenRouter API | ✅ GitHub Pages CI API |
| Ranking criteria | Context, capabilities, recency | **Actual benchmark performance** |
| Security ranking | ✅ (`--secure`) | ✅ (`--secure`) |
| Primary + fallbacks config | ✅ | ✅ |
| No API key required | ❌ (needs OPENROUTER_API_KEY) | ✅ |
| Public leaderboard | ✅ | ✅ |

---

## Development

### Local Testing

```bash
pip install -e .
benchmarked-free-ride list
benchmarked-free-ride auto
benchmarked-free-ride status
```

### Publishing to ClawHub

```bash
clawhub skill publish . \
  --slug benchmarked-free-ride \
  --name "Benchmarked Free Ride" \
  --version 1.2.0 \
  --changelog "Align with free-ride CLI interface: auto/list/switch/status/fallbacks/refresh commands; add --secure flag; set primary+fallbacks config" \
  --tags "free-models,openrouter,benchmark,model-selection,leaderboard"
```

Run with `--dry-run` first to validate the manifest before publishing.

---

## Troubleshooting

### "No benchmarked free models found"

**Cause:** The leaderboard has no models matching `:free` + `is_benchmarked == true`.

**Fix:** Check the live leaderboard:
```bash
curl -s "https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/leaderboard.json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len([m for m in d['leaderboard'] if ':free' in m.get('model_id','') and m.get('is_benchmarked')]))"
```

### "Model not found" in switch

**Cause:** Model ID typo or model not in leaderboard.

**Fix:** Run `benchmarked-free-ride list` to see available model IDs.

### "Failed to configure model"

**Cause:** `openclaw` CLI not on PATH or config file not writable.

**Fix:**
```bash
which openclaw   # verify it's on PATH
ls ~/.openclaw/config.json   # verify config file exists
```

---

## Related Projects

- [benchmarked-free-ride-ci](https://github.com/sequrity-ai/benchmarked-free-ride-ci) — CI runner that generates benchmarks
- [FreeRide](https://playbooks.com/skills/openclaw/skills/free-ride) — Reference skill this was modeled after
- [OpenClaw](https://github.com/openclaw/openclaw) — AI agent framework

---

## License

MIT License. See LICENSE file for details.
