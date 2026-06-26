from collections.abc import Callable
from pathlib import Path

def execute_at_the_year_level(xml_root_dir: str, fxn_to_exec: Callable):
    xml_root_dir = Path(xml_root_dir)
    
    for year_dir in xml_root_dir.iterdir():
        fxn_to_exec