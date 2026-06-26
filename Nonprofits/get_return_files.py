'''Return a (list of) 990 xml file(s) that match the intended criteria.'''
import argparse as ap
from typing import List
import pandas as pd

def get_return_files(tax_year: int, content: str | List,
                     num_examples: int | str = 1, org_type: str = '501c4',
                     content_matrix: str = 'Nonprofits/filing_content_matrix.csv') -> str | List:
    """
    Definition: Returns the specified number of xml files that match to specified criteria.

    Args:
        tax_year (int): _description_
        content (str | List): _description_
        num_examples (int | str, optional): _description_. Defaults to 1.
        org_type (str, optional): _description_. Defaults to '501c4'.
        content_matrix (str, optional): _description_. Defaults to 'Nonprofits/filing_content_matrix.csv'.

    Returns:
        str | List: _description_
    """
    file_matrix_df = pd.read_csv(content_matrix)
    specific_year = file_matrix_df.loc[:, 'TaxYr'] == tax_year
    specific_org_type = file_matrix_df.loc[:, 'OrgType'] == org_type
    specific_return_content = file_matrix_df.loc[:, content] == 1
    files = file_matrix_df.loc[specific_year & specific_org_type & specific_return_content, 'file'].tolist()
    return files[:num_examples]

if __name__ == '__main__':
    parser = ap.ArgumentParser(
        description="Return a (list of) 990 xml file(s) that match the intended criteria."
    )

    parser.add_argument("--tax_year", required=True, type=int,
                        help="Specific TaxYr specified in return. Valid range is 2018-2025.")
    parser.add_argument("--content", required=True, type=str,
                        help="The schedule you are interested in (column name in matrix).")
    parser.add_argument("--num_examples", required=False, default=1, type=int,
                        help="Number of file paths you want returned.")
    parser.add_argument("--org_type", required=False,
                        type=str, default='501c4',
                        help="Valid org_type values: '501c3', '501c4', '527'.")
    parser.add_argument("--content_matrix", required=False,
                        type=str, default='Nonprofits/filing_content_matrix.csv',
                        help="Ensure your file path is correct.")

    args = parser.parse_args()

    print(
        get_return_files(args.tax_year, args.content, args.num_examples,
                     args.org_type, args.content_matrix)
    )
