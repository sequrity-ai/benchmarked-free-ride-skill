# Benchmarked Free Ride Skill

OpenClaw skill to fetch model quality benchmarks and auto-configure the best free model.

## What This Does

This skill connects to the [benchmarked-free-ride-ci](https://github.com/sequrity-ai/benchmarked-free-ride-ci) public API to:

1. **Fetch** daily-updated benchmark scores for free OpenRouter models
2. **Display** leaderboards ranked by quality (accuracy, latency, token efficiency)
3. **Auto-configure** OpenClaw to use the best-performing free model

Unlike [FreeRide](https://github.com/openclaw/skills/tree/main/skills/shaivpidadi/free-ride) which ranks by context length and recency, this skill selects models based on **actual benchmark performance**.

---

## Installation

```bash
# Install via clawhub (when published)
clawhub install sequrity-ai/benchmarked-free-ride

# Or install locally
cd benchmarked-free-ride-skill
pip install -e .
```

---

## Usage

### Show Leaderboard

```bash
benchmarked-free-ride leaderboard
```

Output:
```
🏆 Fetching top 10 models...

🕐 Last updated: 2026-03-02T10:30:00Z

Rank   Model ID                                           Score    Accuracy   Latency
-------------------------------------------------------------------------------------
🥇     google/gemini-2.0-flash-exp:free                    85.3      88.9%      3.2s
🥈     meta-llama/llama-3.2-3b-instruct:free              82.1      85.0%      2.8s
🥉     mistralai/mistral-7b-instruct:free                 78.4      80.0%      4.1s
4.     qwen/qwen-2.5-7b-instruct:free                     75.2      76.7%      3.9s
...

💡 Use 'benchmarked-free-ride auto' to configure the top model
```

### Auto-Select Best Model

```bash
benchmarked-free-ride auto
```

Output:
```
🚀 Auto-selecting the best free model...

🥇 Top model: google/gemini-2.0-flash-exp:free
📊 Score: 85.3/100
✅ Accuracy: 88.9%
⚡ Latency: 3.2s

🔧 Configuring OpenClaw...
✅ Successfully configured: google/gemini-2.0-flash-exp:free

💡 Restart your OpenClaw agent to use the new model
```

### List All Models

```bash
benchmarked-free-ride list
```

Shows all benchmarked models with detailed stats.

### Show Model Details

```bash
benchmarked-free-ride details "google/gemini-2.0-flash-exp:free"
```

Output:
```
🔍 Fetching details for: google/gemini-2.0-flash-exp:free

======================================================================
Model: google/gemini-2.0-flash-exp:free
======================================================================

🎯 Composite Score:      85.3/100
📊 Accuracy:             88.9%
⚡ Avg Latency:          3.2s
🔢 Context Length:       1,048,576 tokens
📈 Quality Score:        0.82
📥 Input Tokens:         12,450
📤 Output Tokens:        3,210
✅ Passed Tasks:         8/9
🕐 Benchmarked:          2026-03-02T08:15:30Z

📋 Scenario Breakdown:

  • File Manipulation               3/3 tasks  (100% avg accuracy)
  • Weather                         3/3 tasks  (100% avg accuracy)
  • Web Search                      2/3 tasks  (67% avg accuracy)
```

---

## How It Works

### Data Source

Fetches from the public GitHub Pages API:
- `https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/models.json`
- `https://sequrity-ai.github.io/benchmarked-free-ride-ci/api/leaderboard.json`

Updated daily by automated CI benchmarks.

### Scoring System

Models are ranked by **composite score** (0-100):

- **Accuracy** (70% weight) - Task success rate across benchmarks
- **Latency** (20% weight) - Response speed (lower is better)
- **Token Efficiency** (10% weight) - Output tokens per task (lower is better)

See [benchmarked-free-ride-ci](https://github.com/sequrity-ai/benchmarked-free-ride-ci) for benchmark methodology.

### Configuration

The `auto` command modifies OpenClaw's config file:
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "openrouter/google/gemini-2.0-flash-exp:free"
      }
    }
  }
}
```

---

## Comparison with FreeRide

| Feature | FreeRide | Benchmarked Free Ride |
|---------|----------|----------------------|
| Model discovery | ✅ OpenRouter API | ✅ OpenRouter API |
| Ranking criteria | Context, capabilities, recency | **Actual benchmark performance** |
| Auto-configure | ✅ | ✅ |
| Rate-limit rotation | ✅ | ❌ (future work) |
| Daily updates | ❌ | ✅ (via CI) |
| Public leaderboard | ❌ | ✅ (GitHub Pages) |

**Use FreeRide when:** You want maximum context length and automatic fallback rotation.

**Use Benchmarked Free Ride when:** You want the model that performs best on real tasks.

---

## API Reference

### Commands

| Command | Description |
|---------|-------------|
| `list` | List all benchmarked models with scores |
| `leaderboard` | Show top 10 models ranked by score |
| `details <model_id>` | Show detailed stats for a specific model |
| `auto` | Auto-select and configure the best model |
| `help` | Show usage information |

### JSON API Endpoints

**GET** `/api/models.json`
- All benchmarked models with detailed stats

**GET** `/api/leaderboard.json`
- Top models ranked by composite score

**GET** `/api/history/YYYY-MM-DD.json`
- Historical daily snapshots

---

## Configuration

The API URL can be customized by editing `main.py`:

```python
DEFAULT_API_URL = "https://your-custom-url.com/api"
```

Or set via environment variable:
```bash
export BENCHMARKED_FREE_RIDE_API_URL="https://your-custom-url.com/api"
```

---

## Development

### Local Testing

```bash
# Clone skill repo
git clone https://github.com/sequrity-ai/benchmarked-free-ride-skill.git
cd benchmarked-free-ride-skill

# Install in development mode
pip install -e .

# Test commands
benchmarked-free-ride leaderboard
```

### Mock API for Testing

To test without internet, create a local API:

```bash
# Start simple HTTP server
cd /path/to/benchmarked-free-ride-ci/docs
python3 -m http.server 8000

# Update main.py temporarily
DEFAULT_API_URL = "http://localhost:8000/api"
```

---

## Troubleshooting

### "Error fetching models"

**Cause:** API endpoint not reachable or GitHub Pages not deployed yet.

**Fix:**
1. Check if GitHub Pages is enabled: [https://sequrity-ai.github.io/benchmarked-free-ride-ci](https://sequrity-ai.github.io/benchmarked-free-ride-ci)
2. Wait 2-3 minutes after first CI run for Pages to deploy
3. Verify `DEFAULT_API_URL` in `main.py` matches the correct organization

### "Failed to configure model"

**Cause:** OpenClaw config file not found or permissions issue.

**Fix:**
```bash
# Ensure OpenClaw is initialized
openclaw init

# Check config file exists
ls ~/.openclaw/config.json

# Manually set model
openclaw config set model "openrouter/model-id"
```

### "Model not found"

**Cause:** Model ID typo or model not yet benchmarked.

**Fix:**
```bash
# List all available models
benchmarked-free-ride list

# Copy exact model ID (case-sensitive)
benchmarked-free-ride details "google/gemini-2.0-flash-exp:free"
```

---

## Contributing

Contributions welcome! To add features:

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Test with `pip install -e .`
5. Submit a pull request

---

## Related Projects

- [benchmarked-free-ride-ci](https://github.com/sequrity-ai/benchmarked-free-ride-ci) - CI runner that generates benchmarks
- [FreeRide](https://github.com/openclaw/skills/tree/main/skills/shaivpidadi/free-ride) - Original inspiration
- [OpenClaw](https://github.com/openclaw/openclaw) - AI agent framework

---

## License

MIT License. See LICENSE file for details.
