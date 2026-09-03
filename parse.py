"""
1) read yaml [done]
2) create list of key->value (expand sentinels if required) [done]
3) iterate over key, value pairs and keep the latest to overwrite defaults
4) Back to yaml
"""

from yaml import load, Loader, dump
from pathlib import Path
import argparse

# 1
def read_yaml(path:Path)->dict:
    return load(path.read_text(), Loader=Loader)

# 2
def get_config_key_value_pair(key:str, value:str, config_dir:Path) -> dict|str:
    if is_config_group(config_dir, key):
        path_to_group_config = config_dir / f"{key}/{value}.yaml"
        return read_yaml(path_to_group_config)
    return value

def expand_sentinels(config:dict, config_dir:Path) -> dict:
    output = {}
    for key, value in config.items():
        output[key] = get_config_key_value_pair(key, value, config_dir)
    return output

def transform_dict_to_list(expanded_config:dict, prefix: None|str) -> list[str] :
    output = []
    for key, value in expanded_config.items():
        dotted_key = key if prefix is None else f"{prefix}.{key}"
        if not isinstance(value, dict):
            output.append(f"{dotted_key}:{value}")
        else:
            output.extend(
                transform_dict_to_list(value, dotted_key)
            )
    return output

def is_config_group(config_dir:Path, key:str):
    assert config_dir.is_dir()
    return (config_dir / key).exists()

# 3
def apply_overwrites(config_as_list:list[str], overwrites:list[str])->dict[str, str]:
    configs = config_as_list + overwrites
    output = {}
    for c in configs:
        key, value = c.split(':')
        output[key] = value
    return output

def _parse_overwrite_arg(arg:str, config_dir:Path) ->list[str]:
    assert '=' and '-' in arg
    key, value = arg.lstrip('-').split('=')
    config_group_filename = key.replace('.', '/') + f"/{value}.yaml"
    config_group_path = (config_dir / config_group_filename)
    if config_group_path.exists():
        config_group = read_yaml(config_group_path)
        expanded_config = expand_sentinels(config_group, config_dir)
        output = transform_dict_to_list(expanded_config, key)
        return output
    return [f"{key}:{value}"]

# 4
def add_key_value_to_config(config:dict, key:str, value:str)->None:
    if '.' in key:
        base_key, sub_key = key.split('.', maxsplit=1)
        if base_key not in config:
            config[base_key] = {}
        add_key_value_to_config(config[base_key], sub_key, value)
    else:
        config[key]=value

def yaml_from_config_dict(config:dict) -> dict:
    data = dict()
    for key, value in config.items():
        add_key_value_to_config(data, key, value)
    return dump(data)

def main(config_filename:str, overwrites:list[str]):
    path = config_dir / config_filename
    config = read_yaml(path)
    expanded_config = expand_sentinels(config, config_dir)
    config_as_list = transform_dict_to_list(expanded_config, None)
    overwritten_config = apply_overwrites(config_as_list, overwrites)
    print(overwritten_config)
    print(yaml_from_config_dict(overwritten_config))

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config_filename", type=str, required=True
    )
    parser.add_argument(
        "--config_dir", type=str, default="configs"
    )
    known_args, unknown_args = parser.parse_known_args()
    config_dir = Path(known_args.config_dir)
    config_filename = known_args.config_filename
    formatted_overwrites:list[str] = []
    for arg in unknown_args:
        formatted_overwrites.extend(_parse_overwrite_arg(arg, config_dir))
    main(known_args.config_filename, formatted_overwrites)