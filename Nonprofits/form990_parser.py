from collections.abc import Callable
import re
import json
from ast import literal_eval
import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
from typeguard import check_type, TypeCheckError
from typing import Literal
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

        return {'namespace': ''}

    def find_element(self, _target: str, _root: ET.Element | None = None) -> ET.Element:
        if _root is None:
            _root = self._xml_root
        # Can leverage xpath and cleaner namespace prefixing all at once
        _element = _root.find(f'.//namespace:{_target}', self._namespace)
        if _element is None:
            raise ValueError("This element does not exist")
        return _element

    def find_all_elements(self, _target: str, _root: ET.Element | None) -> list[ET.Element]:
        if _root is None:
            _root = self._xml_root
        # Can leverage xpath and cleaner namespace prefixing all at once
        _element = _root.findall(f'.//namespace:{_target}', self._namespace)
        if _element is None:
            raise ValueError("This element does not exist")
        return _element
    
    def format_element_tag(self, _elem: ET.Element) -> str:
        return re.sub(self._namespace_str, '', _elem.tag)
    
    def format_element_value(self, _elem_text: str, _dtype: Literal['str', 'float', 'bool']) -> str | float | bool:
        if _dtype == 'str':
            return _elem_text
        
        if _dtype == 'float':
            return float(_elem_text)
        
        if _elem_text in ['false']:
            return False
        
        return True

    def get_990PF_org_type(self) -> str:
        try: # Element may not be present, and may not indicate appropriate org type
            self.find_element('Organization501c3ExemptPFInd')
            return '501c3'
        except ValueError:
            pass

        try: #
            self.find_element('Organization4947a1TrtdPFInd')
            return '4947 Trust'
        except ValueError:
            pass

        try: #
            self.find_element('InitialReturnFormerPubChrtyInd')
            return 'Former Public Charity'
        except ValueError:
            return 'Other'

    def get_990T_org_type(self) -> str:
        try: # Element may not be present, and may not indicate appropriate org type
            c_type = self.find_element('Organization501cTypeText').text
            # Also want type to be 'Corporation' and not 'Trust'
            self.find_element('Organization501cCorporationInd')
            return f'501{c_type}'
        except ValueError:
            return 'Other'

    def get_990Standard_org_type(self) -> str:
        # Is a 501c3
        try: # If this field exits, then it's a 501c3
            self.find_element('Organization501c3Ind')
            return '501c3'
        except ValueError:
            pass

        # Is a 501c4
        try: # Element may not be present, and may not indicate appropriate org type
            _501c = self.find_element('Organization501cInd').attrib
            c_type = _501c['organization501cTypeTxt']
            return f'501c{c_type}'
        except ValueError:
            pass

        # Is a 527
        # TODO: Confirm the 527 target is spelled this way
        try:
            self.find_element('Organization527')
            return '527'
        except ValueError:
            pass

        # Assuming no other possible values in field I
        return '4947a1'

    def get_org_type(self, return_type_cd) -> str:
        if return_type_cd in ['990', '990N', '990EZ']:
            return self.get_990Standard_org_type()
        elif return_type_cd == '990T':
            return self.get_990T_org_type()
        elif return_type_cd == '990PF':
            return self.get_990PF_org_type()
        else:
            return 'Unknown'
    
    def get_org_form(self, _root: ET.Element | None) -> str:
        try:
            self.find_element('TypeOfOrganizationCorpInd')
            return 'Corporation'
        except ValueError:
            pass
        # TODO: Trust, Association, Other
        # TODO: For diff return types?

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

    def parse_header(self, _header_hierarchy_dict: dict) -> pd.DataFrame:
        _header = self.find_element('ReturnHeader')
        _header_content = {}
        for _header_sub_group in _header:
            _header_sub_group_tag = re.sub(self._namespace_str, '', _header_sub_group.tag)
            if _header_sub_group_tag not in _header_hierarchy_dict.keys():
                continue
            _header_sub_group_mapping = _header_hierarchy_dict[_header_sub_group_tag]
            if isinstance(_header_sub_group_mapping, str):
                _header_content[_header_sub_group_mapping] = _header_sub_group.text
                continue
            for _header_sub_group_elem in _header_sub_group.iter():
                _header_sub_group_elem_tag = re.sub(self._namespace_str, '', _header_sub_group_elem.tag)
                try:
                    _header_sub_group_elem_mapping = _header_sub_group_mapping[_header_sub_group_elem_tag]
                    _header_content[_header_sub_group_elem_mapping] = _header_sub_group_elem.text
                except KeyError:
                    continue
        return pd.DataFrame([_header_content])
    
    def recursive_iter(self, _elem, _parsing_format: dict, _dict: dict = {}):
        for _sub_elem in _elem:
            _tag = self.format_element_tag(_sub_elem)
            try:
                _parsing_format[_tag]
            except KeyError:
                # print(self.format_element_tag(_elem), "-->", _tag)
                # print("  >Error:", _tag)
                continue
            if _parsing_format[_tag]['IsHeader']:
                # print(self.format_element_tag(_elem), "-->", _tag)
                # print("  >Is Header")
                # print(_parsing_format[_tag]['Children'])
                self.recursive_iter(_sub_elem, _parsing_format[_tag]['Children'], _dict)
                continue
            if not _parsing_format[_tag]['IsParsed']:
                continue
            # print(_sub_elem.text)
            # print(_parsing_format[_tag])
            _dict[_parsing_format[_tag]['Mapping']] = self.format_element_value(_sub_elem.text, _parsing_format[_tag]['DataType'])
        return _dict

    def parse_return(self, _ein: str, _tax_year: str | int, _return_root: ET.Element, _element_group_mappings: list[dict[str, str|dict]], _return_parsing_format: dict) -> dict[str, pd.DataFrame]:
        element_group_dfs = self.parse_element_groups(_ein, _tax_year, _return_root, _element_group_mappings)

        recursive_dict = self.recursive_iter(_return_root, _parsing_format=_return_parsing_format)
        recursive_dict['FilerEIN'] = _ein
        recursive_dict['TaxYear'] = _tax_year
        element_group_dfs['return_data'] = pd.DataFrame([recursive_dict])

        return element_group_dfs

    def new_part(self, _elem: ET.Element, _prev_part: str) -> str:
        _part_mapper = {
            'ActivityOrMission': 'Part I-A',
            'PYContributionsGrantsAmt': 'Part I-B',
            'PYGrantsAndSimilarPaidAmt': 'Part I-C',
            'TotalAssetsBOYAmt': 'Part I-D',
            'MissionDesc': 'Part III',
            'DescribedInSection501c3Ind ': 'Part IV',
            'IRPDocumentCnt': 'Part V',
            'GoverningBodyVotingMembersCnt': 'Part VI-A',
            'LocalChaptersInd': 'Part VI-B',
            'StatesWhereCopyOfReturnIsFldCd': 'Part VI-C',
            'Form990PartVIISectionAGrp': 'Part VII-A',
            'CntrctRcvdGreaterThan100KCnt': 'Part VII-B'
        }

        try:
            _part_key = re.sub(self._namespace_str, '', _elem.tag)
            return _part_mapper[_part_key]
        except KeyError:
            return _prev_part

    def parse_element_groups(self, _ein: str, _tax_year: str | int, _root: ET.Element | None,  _element_group_mappings: list[dict[str, str|dict]]) -> dict[str, pd.DataFrame]:
        _target_dfs = {}
        for _element_group_mapping in _element_group_mappings:
            _element_target = _element_group_mapping['Group']
            # Get list of element gorups
            _element_groups = self.find_all_elements(_element_target, _root)
            _element_group_list = []
            for _element_group in _element_groups:
                _element_target_content = {'FilerEIN': _ein, 'TaxYear': _tax_year}

                for _sub_elem in _element_group.iter():
                    if self.is_group_header(_sub_elem):
                        #print(1.3)
                        continue
                    #print(1.4)
                    _element_target_field = re.sub(self._namespace_str, '', _sub_elem.tag)
                    _element_target_content[_element_target_field] = _sub_elem.text
                    #print(1.5)
                _element_group_list.append(_element_target_content)
                # Avoid re-parsing when using iter below
                _root.remove(_element_group)
                #print(1.6)
            _target_df = pd.DataFrame(_element_group_list)
            _target_dfs[_element_target] = _target_df.rename(columns=_element_group_mapping['Column Name Mapper'])
        return _target_dfs

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
