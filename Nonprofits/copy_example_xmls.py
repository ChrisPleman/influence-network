import argparse as ap
from pathlib import Path
import shutil
import pandas as pd

def read_in_example_df(csv_file: str, sections_of_interest: None | list) -> pd.DataFrame:
    csv_df = pd.read_csv(csv_file)
    if sections_of_interest is not None:
        csv_df = csv_df.loc[:, sections_of_interest]
    return csv_df

def copy_files(example_csv, sections_of_interest: None | list, reference_dir: str, output_dir: str = 'Nonprofits/example_xmls'):
    # Get dataframe
    example_df = read_in_example_df(example_csv, sections_of_interest)

    # ! Assumes the table has the 'file' column and is named as such
    example_files = example_df.loc[:, 'file'].unique()

    # Create path objects for reference and output root directories
    output_dir = Path(output_dir)
    reference_dir = Path(reference_dir)

    # If output_dir is not yet created, create it
    if not output_dir.is_dir():
        output_dir.mkdir()

    # Iterate over reference directory and subdirectories
    for year_dir in reference_dir.iterdir():
        output_year_dir = output_dir / year_dir.name

        # Make output subdirectory if needed
        if not output_year_dir.is_dir():
            output_year_dir.mkdir()
        for period_dir in year_dir.iterdir():
            if period_dir.suffix in ('.csv', '.zip'):
                continue
            output_period_dir = output_year_dir / period_dir.name

            if not output_period_dir.is_dir():
                output_period_dir.mkdir()

            xml_files_to_copy = [xml_file for xml_file in example_files if period_dir.name in xml_file]
            for xml_file_to_copy in xml_files_to_copy:
                xml_file_to_copy = 'Nonprofits' / Path(xml_file_to_copy)
                shutil.copy(
                    xml_file_to_copy,
                    output_period_dir / xml_file_to_copy.name
                )

if __name__ == '__main__':
    parser = ap.ArgumentParser(
        description="Copy example files over into a nested directory based on local xml directory."
    )

    parser.add_argument('--example_csv', required=True, type=str,
                        help="tbd")
    parser.add_argument('--sections_of_interest', required=False, default=None,
                        help="tbd")
    parser.add_argument('--reference_dir', required=True, type=str,
                        help="tbd")
    parser.add_argument('--output_dir', required=False, default='Nonprofits/example_xmls',
                        type=str, help="tbd")

    args = parser.parse_args()

    copy_files(args.example_csv, args.sections_of_interest, args.reference_dir, args.output_dir)
