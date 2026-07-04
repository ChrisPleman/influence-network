from collections.abc import Callable
import re
import json
from ast import literal_eval
import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
from typeguard import check_type, TypeCheckError
# from typing import Literal
# TODO: Add type hinting


class Form990Parser():

    def __init__(self, xml_file) -> None:
        self._xml_file = Path(xml_file)
        self._xml_root = ET.parse(self._xml_file).getroot()
        self._namespace = self.get_namespace(self._xml_root)
        self._namespace_str = '{' + self._namespace['namespace'] + '}'

    def get_namespace(self, xml_root: ET.Element) -> dict[str, str]:

        _xml_namespace = re.match(r'\{(.+)\}', xml_root.tag)

        if _xml_namespace is not None:
            return {'namespace': _xml_namespace.group(1)}
        else:
            return {'namespace': ''}

    def find_element(self, _target: str) -> ET.Element | None:
        # Can leverage xpath and cleaner namespace prefixing all at once
        return self._xml_root.find(f'.//namespace:{_target}', self._namespace)
    
    def recursive_literal_dict_formatter(self, _dict, _new_dict) -> dict:
        for _key, _val in _dict.items():
            try:
                _key = literal_eval(_key)
            except (SyntaxError, ValueError) as error:
                # This throws when the literal value isn't quotted
                pass
            if type(_val) == dict:
                _new_dict[_key] = {}
                self.recursive_literal_dict_formatter(_val, _new_dict[_key])
            else:
                _new_dict[_key] = _val
        return _new_dict

    def read_in_formatter(self, formatter_path: str ='') -> dict:
        formatter_file = Path(formatter_path)
        if formatter_file.suffix != '.json':
            error_message = f"A {formatter_file.suffix} file is not supported. Please pass in a json file."
            raise ValueError(error_message)

        with open(formatter_path, mode='r', encoding='utf-8') as json_file:
            _formatter_dict = json.loads(json_file.read())
            return self.recursive_literal_dict_formatter(_formatter_dict, _new_dict={})

    def is_group_header(self, _element: ET.Element) -> bool:
        # Identify parent element with no real content
        if _element.text is None:
            return True
        if len(re.sub(r'\s', '', _element.text)) == 0:
            return True
        return False

    def create_xml_target_mapping_list(self, _target_type, _format_mappings_func: Callable, _dict: dict, _accum: list | None = None) -> list:
        # _accum was persisting across multiple calls without this
        if _accum is None:
            _accum = []
        for _key, _val in _dict.items():
            try:
                _key_val_pair = {_key: _val}
                check_type(_key_val_pair, _target_type)
                if len(_val) == 0:
                    continue
                try:
                    _accum += _format_mappings_func(_key_val_pair)
                except TypeError:
                    _accum.append(_format_mappings_func(_key_val_pair))
            except TypeCheckError:
                if isinstance(_val, dict):
                    self.create_xml_target_mapping_list(_target_type, _format_mappings_func, _val, _accum)
                else:
                    continue
        return _accum

    def create_xml_target_mapping_dict(self, _target_type, _format_mappings_func: Callable, _dict: dict, _accum: dict | None = None) -> dict:
        # _accum was persisting across multiple calls without this
        if _accum is None:
            _accum = {}
        for _key, _val in _dict.items():
            try:
                _key_val_pair = {_key: _val}
                check_type(_key_val_pair, _target_type)
                if len(_val) == 0:
                    continue
                _formatted_key, _formatted_val = _format_mappings_func(_key, _val)
                _accum[_formatted_key] = _formatted_val
            except TypeCheckError:
                if isinstance(_val, dict):
                    self.create_xml_target_mapping_dict(_target_type, _format_mappings_func, _val, _accum)
                else:
                    continue
        return _accum

    def parse_schedule(self, _ein: str, _tax_year: str | int, _schedule_root: ET.Element, _flat_targets: dict, _nested_targets: list) -> dict:
        _target_dfs = {}
        for _nested_target_dict in _nested_targets:
            #print(1.1)
            _nested_target = _nested_target_dict['Group']
            _nested_target_groups = _schedule_root.findall(f'namespace:{_nested_target}', self._namespace)
            _nested_target_list = []
            for _nested_target_group in _nested_target_groups:
                #print(1.2)
                _nested_target_content = {'FilerEIN': _ein, 'TaxYear': _tax_year}
                for _nested_element in _nested_target_group.iter():
                    if self.is_group_header(_nested_element):
                        #print(1.3)
                        continue
                    #print(1.4)
                    _nested_element_field = re.sub(self._namespace_str, '', _nested_element.tag)
                    _nested_target_content[_nested_element_field] = _nested_element.text
                    #print(1.5)
                _nested_target_list.append(_nested_target_content)
                # Avoid re-parsing when using iter below
                _schedule_root.remove(_nested_target_group)
                #print(1.6)
            target_df = pd.DataFrame(_nested_target_list)
            _target_dfs[_nested_target] = target_df.rename(columns=_nested_target_dict['Column Name Mapper'])

        _missed_targets = []
        _flat_target_content = {'FilerEIN': _ein, 'TaxYear': _tax_year}
        for _elem in _schedule_root.iter():
            #print(2.1, _elem, _elem.text)
            if self.is_group_header(_elem):
                #print(2.2)
                continue
            #print(2.3)
            _elem_tag = re.sub(self._namespace_str, '', _elem.tag)
            try:
                _flat_target_content[_flat_targets[_elem_tag]] = _elem.text
                #print(2.4)
            except KeyError:
                #print(2.5)
                _missed_targets.append(_elem_tag)
        _target_dfs['Flat Content'] = pd.DataFrame([_flat_target_content])
        return _target_dfs, _missed_targets
