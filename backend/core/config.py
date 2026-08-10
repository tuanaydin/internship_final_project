from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"

ASSETS_FILE = CONFIG_DIR / "assets.yaml"
THRESHOLDS_FILE = CONFIG_DIR / "thresholds.yaml"
DATA_QUALITY_FILE = CONFIG_DIR / "data_quality.yaml"