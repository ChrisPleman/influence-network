import argparse as ap
import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
from form990_parser import (
    get_return_type,
    get_org_type,
    NAMESPACE,
    RETURN_HEADER_PATH,
    RETURN_DATA_PATH
)
def add_to_csv(csv_file, data):
    try:
        old_df = pd.read_csv(csv_file)
    except FileNotFoundError:
        old_df = pd.DataFrame()
    output_file = csv_file
    df_to_output = pd.concat(
        [pd.DataFrame(data).fillna(0), old_df]
    )
    df_to_output.to_csv(
        output_file,
        index=False
    )
    # Clean up memory
    del df_to_output

def construct_reference_matrices(xml_root_dir, output_dir='.'):
    xml_root_dir = Path(xml_root_dir)
    output_path = Path(output_dir)
    if not output_path.is_dir():
        output_path.mkdir()
    print(output_path)
    files_scanned = 0
    files_parsed = 0
    for year_dir in xml_root_dir.iterdir():
        year = str(year_dir).split('\\')[-1]
        output_file = f'{output_dir}/reference_matrix_{year}.csv'
        for period_dir in year_dir.iterdir():
            if period_dir.suffix in ('.zip', '.csv'):
                continue
            print(period_dir)
            # Refresh list with every new period
            data = []
            for xml_file in period_dir.glob('*.xml'):
                # Skip certain orgs based on their org and form types
                root = ET.parse(xml_file).getroot()
                return_type_cd = get_return_type(root)
                org_type = get_org_type(root, return_type_cd)
                if org_type not in ['501c3', '501c4', '527']:
                    continue

                return_content = {}
                # * Header
                header = root.find(RETURN_HEADER_PATH)
                return_content['EIN'] = header.find(f'{NAMESPACE}Filer/{NAMESPACE}EIN').text
                return_content['Name'] = header.find(f'{NAMESPACE}Filer/{NAMESPACE}BusinessName/{NAMESPACE}BusinessNameLine1Txt').text
                return_content['OrgType'] = org_type
                return_content['file'] = str(xml_file)
                return_content['TaxYr'] = header.find(f'{NAMESPACE}TaxYr').text

                # * return_content
                return_content['ReturnTypeCd'] = return_type_cd
                return_data = root.find(RETURN_DATA_PATH)
                for section in return_data:
                    return_content_key = section.tag.replace(NAMESPACE, '')
                    return_content[return_content_key] = 1
                    return_content[return_content_key + 'Size'] = len(section)

                data.append(return_content)
                if len(data) >= 30_000:
                    add_to_csv(
                        csv_file=output_file,
                        data=data
                    )
                    data = []

                # Incremement and debug
                files_scanned += 1
                files_parsed += 1
                if files_scanned % 1_000 == 0:
                    print(f'Parsed {files_parsed}/{files_scanned} scanned files.')

            # Add the rest of the data that might be in the list   
            add_to_csv(
                csv_file=output_file,
                data=data
            )



if __name__ == '__main__':
    parser = ap.ArgumentParser(
        description="Construct a reference matrix(ces) for relevant return files."
    )

    parser.add_argument('--xml_root_dir', required=True, type=str,
                        help="tbd")

    args = parser.parse_args()

    construct_reference_matrices(args.xml_root_dir)
