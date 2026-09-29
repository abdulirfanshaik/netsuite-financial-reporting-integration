from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from generate_sample_data import main as generate_sample_data
from validate_extracts import load_frames, run_checks


def test_sample_data_passes_all_checks():
    generate_sample_data()
    frames = load_frames(ROOT / "data" / "sample")
    results = run_checks(frames)
    failed = [r for r in results if not r.passed]
    assert not failed, [(r.check, r.details) for r in failed]
