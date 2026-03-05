#!/usr/bin/env python3
"""
Benchmarked Free Ride - OpenClaw Skill

Fetches model quality benchmarks and auto-configures the best free model.
"""

import sys
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List


# Public API endpoint
DEFAULT_API_URL = "https://sequrity-ai.github.io/benchmarked-free-ride-ci/api"


class BenchmarkedFreeRide:
    def __init__(self, api_url: str = DEFAULT_API_URL):
        self.api_url = api_url.rstrip("/")

    def fetch_models(self) -> Optional[Dict[str, Any]]:
        """Fetch all benchmarked models from API."""
        try:
            response = requests.get(f"{self.api_url}/models.json", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching models: {e}")
            return None

    def fetch_leaderboard(self) -> Optional[Dict[str, Any]]:
        """Fetch leaderboard from API."""
        try:
            response = requests.get(f"{self.api_url}/leaderboard.json", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching leaderboard: {e}")
            return None

    def list_models(self):
        """List all benchmarked models with scores."""
        print("📊 Fetching benchmarked models...")
        data = self.fetch_models()

        if not data:
            return

        models = data.get("models", [])
        generated_at = data.get("generated_at", "unknown")

        print(f"\n🕐 Last updated: {generated_at}")
        print(f"📈 Total models: {len(models)}\n")

        # Sort by composite score
        models_sorted = sorted(models, key=lambda m: m.get("composite_score", 0), reverse=True)

        print(f"{'Model ID':<50} {'Score':<8} {'Accuracy':<10} {'Latency':<10} {'Context':<10}")
        print("-" * 90)

        for model in models_sorted:
            model_id = model.get("model_id", "unknown")
            score = model.get("composite_score") or 0
            accuracy = model.get("accuracy_percent") or 0
            latency = model.get("avg_latency_seconds") or 0
            context = (model.get("context_length") or 0) // 1000  # Convert to K

            print(f"{model_id:<50} {score:>6.1f}   {accuracy:>6.1f}%    {latency:>6.1f}s    {context:>6}K")

    def show_leaderboard(self, top_n: int = 10):
        """Show top N models by composite score."""
        print(f"🏆 Fetching top {top_n} models...")
        data = self.fetch_leaderboard()

        if not data:
            return

        leaderboard = data.get("leaderboard", [])[:top_n]
        generated_at = data.get("generated_at", "unknown")

        print(f"\n🕐 Last updated: {generated_at}\n")
        print(f"{'Rank':<6} {'Model ID':<50} {'Score':<8} {'Accuracy':<10} {'Latency':<10}")
        print("-" * 85)

        medals = {1: "🥇", 2: "🥈", 3: "🥉"}

        for entry in leaderboard:
            rank = entry.get("rank", 0)
            model_id = entry.get("model_id", "unknown")
            score = entry.get("composite_score") or 0
            accuracy = entry.get("accuracy_percent") or 0
            latency = entry.get("avg_latency_seconds") or 0

            medal = medals.get(rank, f"{rank:>2}.")
            print(f"{medal:<6} {model_id:<50} {score:>6.1f}   {accuracy:>6.1f}%    {latency:>6.1f}s")

        print(f"\n💡 Use 'benchmarked-free-ride auto' to configure the top model")

    def model_details(self, model_id: str):
        """Show detailed benchmark results for a specific model."""
        print(f"🔍 Fetching details for: {model_id}")
        data = self.fetch_models()

        if not data:
            return

        models = data.get("models", [])
        model = next((m for m in models if m.get("model_id") == model_id), None)

        if not model:
            print(f"❌ Model not found: {model_id}")
            print(f"\n💡 Use 'benchmarked-free-ride list' to see all available models")
            return

        print(f"\n{'='*70}")
        print(f"Model: {model.get('model_id', 'unknown')}")
        print(f"{'='*70}\n")

        print(f"🎯 Composite Score:      {model.get('composite_score') or 0:.1f}/100")
        print(f"📊 Accuracy:             {model.get('accuracy_percent') or 0:.1f}%")
        print(f"⚡ Avg Latency:          {model.get('avg_latency_seconds') or 0:.1f}s")
        print(f"🔢 Context Length:       {model.get('context_length') or 0:,} tokens")
        print(f"📈 Quality Score:        {model.get('quality_score') or 0:.2f}")
        print(f"📥 Input Tokens:         {model.get('total_input_tokens') or 0:,}")
        print(f"📤 Output Tokens:        {model.get('total_output_tokens') or 0:,}")
        print(f"✅ Passed Tasks:         {model.get('passed_tasks') or 0}/{model.get('total_tasks') or 0}")
        print(f"🕐 Benchmarked:          {model.get('benchmarked_at', 'unknown')}\n")

        scenarios = model.get("scenarios", [])
        if scenarios:
            print("📋 Scenario Breakdown:\n")
            for scenario in scenarios:
                name = scenario.get("name", "unknown")
                passed = scenario.get("tasks_passed") or 0
                total = scenario.get("tasks_total") or 0
                avg_acc = scenario.get("avg_accuracy") or 0
                print(f"  • {name:<30} {passed}/{total} tasks  ({avg_acc:.0f}% avg accuracy)")

    def auto_select(self):
        """Automatically configure the best free model."""
        print("🚀 Auto-selecting the best free model...")
        data = self.fetch_leaderboard()

        if not data:
            return

        leaderboard = data.get("leaderboard", [])
        if not leaderboard:
            print("❌ No models found in leaderboard")
            return

        best_model = leaderboard[0]
        model_id = best_model.get("model_id")
        score = best_model.get("composite_score") or 0

        print(f"\n🥇 Top model: {model_id}")
        print(f"📊 Score: {score:.1f}/100")
        print(f"✅ Accuracy: {best_model.get('accuracy_percent') or 0:.1f}%")
        print(f"⚡ Latency: {best_model.get('avg_latency_seconds') or 0:.1f}s\n")

        # Configure OpenClaw
        print("🔧 Configuring OpenClaw...")
        if self._configure_openclaw_model(model_id):
            print(f"✅ Successfully configured: {model_id}")
            print(f"\n💡 Restart your OpenClaw agent to use the new model")
        else:
            print("❌ Failed to configure model")

    def _configure_openclaw_model(self, model_id: str) -> bool:
        """Configure OpenClaw to use the specified model."""
        try:
            import subprocess

            # Try CLI method first
            result = subprocess.run(
                ["openclaw", "config", "set", "model", f"openrouter/{model_id}"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return True

            # Fallback: modify config file directly
            return self._configure_via_config_file(model_id)

        except Exception as e:
            print(f"Error: {e}")
            return False

    def _configure_via_config_file(self, model_id: str) -> bool:
        """Fallback: directly modify OpenClaw config file."""
        try:
            config_path = Path.home() / ".openclaw" / "config.json"

            if not config_path.exists():
                print(f"❌ Config file not found at {config_path}")
                return False

            with open(config_path, "r") as f:
                config = json.load(f)

            # Set the model
            if "agents" not in config:
                config["agents"] = {}
            if "defaults" not in config["agents"]:
                config["agents"]["defaults"] = {}
            if "model" not in config["agents"]["defaults"]:
                config["agents"]["defaults"]["model"] = {}

            config["agents"]["defaults"]["model"]["primary"] = f"openrouter/{model_id}"

            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)

            return True

        except Exception as e:
            print(f"Error modifying config: {e}")
            return False


def print_usage():
    """Print usage information."""
    print("""
Benchmarked Free Ride - Auto-select best free AI models

Usage:
  benchmarked-free-ride list              List all benchmarked models
  benchmarked-free-ride leaderboard       Show top 10 models by score
  benchmarked-free-ride details <model>   Show detailed stats for a model
  benchmarked-free-ride auto              Auto-select and configure best model
  benchmarked-free-ride help              Show this help message

Examples:
  benchmarked-free-ride leaderboard
  benchmarked-free-ride details "google/gemini-2.0-flash-exp:free"
  benchmarked-free-ride auto
    """)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()
    client = BenchmarkedFreeRide()

    if command == "list":
        client.list_models()
    elif command == "leaderboard":
        client.show_leaderboard()
    elif command == "details":
        if len(sys.argv) < 3:
            print("❌ Error: model ID required")
            print("Usage: benchmarked-free-ride details <model_id>")
            sys.exit(1)
        client.model_details(sys.argv[2])
    elif command == "auto":
        client.auto_select()
    elif command in ["help", "--help", "-h"]:
        print_usage()
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
