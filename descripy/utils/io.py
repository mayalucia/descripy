"""Input / output ..."""

from pathlib import Path
import yaml
import json


def load_yaml(path):
    """..."""
    with open(path, 'r') as fptr:
        config = yaml.load(fptr, Loader=yaml.FullLoader)
    return config

def dump_yaml(data, in_file_at_path):
    """..."""
    with open(in_file_at_path, 'w') as to_disc:
        yaml.dump(data, to_disc, allow_unicode=True)
    return in_file_at_path

def dump_yaml_to_file(f):
    """..."""
    p = Path(f)
    filetype = p.suffix[1:].lower()
    if filetype not in ("yaml", "yml"):
        p = p.parent / (p.stem + ".yaml")

    return lambda data: dump_yaml(data, f"{p}")


def dump_json_to_file(f):
    """..."""
    p = Path(f)
    filetype = p.suffix[1:].lower()
    if filetype not in ("json"):
        p = p.parent / (p.stem + ".json")

    def dump(data):
        with open(p, 'w') as to_file:
            json.dump(data, to_file, indent=4)
            #to_file.write(json.dumps(data))
        return p

    return dump
