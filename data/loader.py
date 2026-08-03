"""
data/loader.py — JSON-Datenlader mit pydantic-Validierung.

Lädt Items, Blueprints und Locations aus JSON-Dateien.
Validiert Struktur und Typen beim Laden.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from pydantic import BaseModel, RootModel, ValidationError

DATA_DIR = Path(__file__).parent


# --- Pydantic models for validation ---

class ItemTemplate(BaseModel):
    name: str
    weight: float
    tags: Dict[str, Any] = {}
    attributes: Dict[str, float] = {}


class ItemTemplatesDB(RootModel[Dict[str, ItemTemplate]]):
    """Root model wrapping {template_id: ItemTemplate}."""


class BlueprintData(BaseModel):
    id: str
    result_name: str
    slots: Dict[str, str]
    base_efficiency: float = 1.0
    min_survival_req: float = 0.0


class ResourceNodeData(BaseModel):
    result_template_id: str
    min_qty: int
    max_qty: int
    chance: float
    req_perception: float = 0.0
    req_tool_tag: Optional[str] = None


class LocationData(BaseModel):
    id: str
    name: str
    description: str
    base_temp: float
    exposure: float
    nodes: List[ResourceNodeData] = []


class ProcessData(BaseModel):
    id: str
    name: str
    inputs: Dict[str, int]
    tools: List[str] = []
    outputs: Dict[str, int]
    duration_ticks: int
    required_tag_in_env: Optional[str] = None


# --- Loading functions ---

def _load_json(filename: str) -> dict:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    with open(path) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {path}: {e}")


def load_items() -> Dict[str, ItemTemplate]:
    """Load item templates from items.json, validated via pydantic."""
    data = _load_json("items.json")
    try:
        return ItemTemplatesDB.model_validate(data).root
    except ValidationError as e:
        raise ValueError(f"Invalid items.json schema: {e}")


def load_blueprints() -> List[BlueprintData]:
    """Load blueprints from blueprints.json, validated via pydantic."""
    data = _load_json("blueprints.json")
    if not isinstance(data, list):
        raise ValueError("blueprints.json must contain a JSON array")
    try:
        return [BlueprintData.model_validate(bp) for bp in data]
    except ValidationError as e:
        raise ValueError(f"Invalid blueprints.json schema: {e}")


def load_locations() -> List[LocationData]:
    """Load locations from locations.json, validated via pydantic."""
    data = _load_json("locations.json")
    if not isinstance(data, list):
        raise ValueError("locations.json must contain a JSON array")
    try:
        return [LocationData.model_validate(loc) for loc in data]
    except ValidationError as e:
        raise ValueError(f"Invalid locations.json schema: {e}")


def load_processes() -> List[ProcessData]:
    """Load processes from processes.json, validated via pydantic."""
    data = _load_json("processes.json")
    if not isinstance(data, list):
        raise ValueError("processes.json must contain a JSON array")
    try:
        return [ProcessData.model_validate(p) for p in data]
    except ValidationError as e:
        raise ValueError(f"Invalid processes.json schema: {e}")