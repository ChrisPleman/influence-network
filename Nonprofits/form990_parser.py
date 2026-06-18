# TODO: Add type hinting

# * XML File Constants
NAMESPACE = '{http://www.irs.gov/efile}'
RETURN_HEADER_PATH = f'./{NAMESPACE}ReturnHeader'
PREPARER_FIRM_GROUP_PATH = f'./{NAMESPACE}PreparerFirmGrp'
FILER_PATH = f'./{NAMESPACE}Filer'
RETURN_DATA_PATH = f'./{NAMESPACE}ReturnData'

# * These preparers have at least 2 BusinessNamesLine'n>Text fields: 472298930, 823340933
HEADER_CHILD_MAPPER = {
    'FilerEIN': f'{FILER_PATH}/{NAMESPACE}EIN',
    'TaxPeriodBeginDate': f'./{NAMESPACE}TaxPeriodBeginDt',
    'TaxPeriodEndDate': f'./{NAMESPACE}TaxPeriodEndDt',
    'TaxYear': f'./{NAMESPACE}TaxYr',
    'ReturnType': f'./{NAMESPACE}ReturnTypeCd',
    'FilerBusinessNameLine1Txt': f'{FILER_PATH}/{NAMESPACE}BusinessName/{NAMESPACE}BusinessNameLine1Txt',
    'FilerBusinessNameLine2Txt': f'{FILER_PATH}/{NAMESPACE}BusinessName/{NAMESPACE}BusinessNameLine2Txt',
    'FilerPhone': f'{FILER_PATH}/{NAMESPACE}PhoneNum',
    'FilerAddressLine1Txt': f'{FILER_PATH}/{NAMESPACE}USAddress/{NAMESPACE}AddressLine1Txt',
    'FilerCity': f'{FILER_PATH}/{NAMESPACE}USAddress/{NAMESPACE}CityNm',
    'FilerStateCode': f'{FILER_PATH}/{NAMESPACE}USAddress/{NAMESPACE}StateAbbreviationCd',
    'FilerZipCode': f'{FILER_PATH}/{NAMESPACE}USAddress/{NAMESPACE}ZIPCd',
    'PreparerEIN': f'{PREPARER_FIRM_GROUP_PATH}/{NAMESPACE}PreparerFirmEIN',
    'PreparerBusinessNameLine1Txt': f'{PREPARER_FIRM_GROUP_PATH}/{NAMESPACE}PreparerFirmName/{NAMESPACE}BusinessNameLine1Txt',
    'PreparerBusinessNameLine2Txt': f'{PREPARER_FIRM_GROUP_PATH}/{NAMESPACE}PreparerFirmName/{NAMESPACE}BusinessNameLine2Txt',
    'PreparerAddressLine1Txt': f'{PREPARER_FIRM_GROUP_PATH}/{NAMESPACE}PreparerUSAddress/{NAMESPACE}AddressLine1Txt',
    'PreparerCity': f'{PREPARER_FIRM_GROUP_PATH}/{NAMESPACE}PreparerUSAddress/{NAMESPACE}CityNm',
    'PreparerStateCode': f'{PREPARER_FIRM_GROUP_PATH}/{NAMESPACE}PreparerUSAddress/{NAMESPACE}StateAbbreviationCd',
    'PreparerZipCode': f'{PREPARER_FIRM_GROUP_PATH}/{NAMESPACE}PreparerUSAddress/{NAMESPACE}ZIPCd',
    'BusinessOfficerName': f'./{NAMESPACE}BusinessOfficerGrp/{NAMESPACE}PersonNm',
    'BusinessOfficerTitle': f'./{NAMESPACE}BusinessOfficerGrp/{NAMESPACE}PersonTitleTxt',
    'BusinessOfficerPhone': f'./{NAMESPACE}BusinessOfficerGrp/{NAMESPACE}PhoneNum',
    'BusinessOfficerSignatureDate': f'./{NAMESPACE}BusinessOfficerGrp/{NAMESPACE}SignatureDt',
    # ? Do we really need this?
    # 'BusinessOfficerDiscussWithPaidPreparerInd': f'./{NAMESPACE}BusinessOfficerGrp/{NAMESPACE}DiscussWithPaidPreparerInd',
}

# * Schedules of Interest
# Descriptions pulled from: https://github.com/lecy/Open-Data-for-Nonprofit-Research/blob/master/Build_IRS990_E-Filer_Datasets/Data_Dictionary.md
SCHEDULES = [
    'ScheduleA' # Public Charity Status and Public Support	
    ,'ScheduleB' # Schedule of Contributors	
    ,'ScheduleC' # Political Campaign and Lobbying Activities	
    # ,'ScheduleD' # Supplemental Financial Statements	
    # ,'ScheduleE' # Schools	
    # ,'ScheduleF' # Statement of Activities Outside the United States	
    ,'ScheduleG' # Supplemental Information Regarding Fundraising or Gaming Activities	
    # ,'ScheduleH' # Hospitals	
    ,'ScheduleI' # Grants and Other Assistance to Organizations, Governments, and Individuals in the United States	
    ,'ScheduleJ' # Compensation Information	
    # ,'ScheduleK' # Supplemental Information on Tax-Exempt Bonds	
    ,'ScheduleL' # Transactions With Interested Persons	
    ,'ScheduleM' # Noncash Contributions	
    # ,'ScheduleN' # Liquidation, Termination, Dissolution, or Significant Disposition of Assets	
    # ,'ScheduleO' # Supplemental Information to Form 990	
    ,'ScheduleR' # Related Organizations and Unrelated Partnerships
]

RETURN_CHILD_MAPPER = {
    'PrincipalOfficer': f'{NAMESPACE}PrincipalOfficerNm',
    'PrincipalOfficerAddress': f'{NAMESPACE}USAddress/{NAMESPACE}AddressLine1Txt',
    'PrincipalOfficerCity': f'{NAMESPACE}USAddress/{NAMESPACE}CityNm',
    'PrincipalOfficerStateCode': f'{NAMESPACE}USAddress/{NAMESPACE}StateAbbreviationCd',
    'PrincipalOfficerZipCode': f'{NAMESPACE}USAddress/{NAMESPACE}ZIPCd',
    'GrossReceiptsAmt':  f'{NAMESPACE}GrossReceiptsAmt',
    'ActivityOrMission': f'{NAMESPACE}ActivityOrMissionDesc',
    'MissionDesc': f'{NAMESPACE}MissionDesc',
    'FormationYear': f'{NAMESPACE}FormationYr',
    'VotingMembersGoverningBodyCnt': f'{NAMESPACE}VotingMembersGoverningBodyCnt',
    'VotingMembersIndependentCnt': f'{NAMESPACE}VotingMembersIndependentCnt',
    'TotalEmployeeCnt': f'{NAMESPACE}TotalEmployeeCnt',
    'TotalGrossUBIAmt': f'{NAMESPACE}TotalGrossUBIAmt',
    'CurrentYearContributionsGrantsAmt': f'{NAMESPACE}CYContributionsGrantsAmt',
    'PreviousYearProgramServiceRevenueAmt': f'{NAMESPACE}PYContributionsGrantsAmt',
    'CurrentYearTotalRevenueAmt': f'{NAMESPACE}CYTotalRevenueAmt',
    'PreviousYearTotalRevenueAmt': f'{NAMESPACE}PYTotalRevenueAmt',
    'PreviousYearGrantsAndSimilarPaidAmt': f'{NAMESPACE}PYGrantsAndSimilarPaidAmt',
    'CurrentYearGrantsAndSimilarPaidAmt': f'{NAMESPACE}CYGrantsAndSimilarPaidAmt',
    'PreviousYearBenefitsPaidToMembersAmt': f'{NAMESPACE}PYBenefitsPaidToMembersAmt',
    'CurrentYearBenefitsPaidToMembersAmt': f'{NAMESPACE}CYBenefitsPaidToMembersAmt',
    'PreviousYearSalariesCompEmpBnftPaidAmt': f'{NAMESPACE}PYSalariesCompEmpBnftPaidAmt',
    'CurrentYearSalariesCompEmpBnftPaidAmt': f'{NAMESPACE}CYSalariesCompEmpBnftPaidAmt',
    'PreviousYearTotalProfFndrsngExpnsAmt': f'{NAMESPACE}PYTotalProfFndrsngExpnsAmt',
    'CurrentYearTotalProfFndrsngExpnsAmt': f'{NAMESPACE}CYTotalProfFndrsngExpnsAmt',
    'CurrentYearTotalFundraisingExpenseAmt': f'{NAMESPACE}CYTotalFundraisingExpenseAmt',
    'PreviousYearOtherExpensesAmt': f'{NAMESPACE}PYOtherExpensesAmt',
    'CurrentYearOtherExpensesAmt': f'{NAMESPACE}CYOtherExpensesAmt',
    'PreviousYearTotalExpensesAmt': f'{NAMESPACE}PYTotalExpensesAmt',
    'CurrentYearTotalExpensesAmt': f'{NAMESPACE}CYTotalExpensesAmt',
    'PreviousYearRevenuesLessExpensesAmt': f'{NAMESPACE}PYRevenuesLessExpensesAmt',
    'CurrentYearRevenuesLessExpensesAmt': f'{NAMESPACE}CYRevenuesLessExpensesAmt',
    'TotalAssetsBeginningOfYearAmt': f'{NAMESPACE}TotalAssetsBOYAmt',
    'TotalAssetsEndOfYearAmt': f'{NAMESPACE}TotalAssetsEOYAmt',
    'TotalLiabilitiesBeginningOfYearAmt': f'{NAMESPACE}TotalLiabilitiesBOYAmt',
    'TotalLiabilitiesEndOfYearAmt': f'{NAMESPACE}TotalLiabilitiesEOYAmt',
    'NetAssetsOrFundBalancesBeginningOfYearAmt': f'{NAMESPACE}NetAssetsOrFundBalancesBOYAmt',
    'NetAssetsOrFundBalancesEndOfYearAmt': f'{NAMESPACE}NetAssetsOrFundBalancesEOYAmt',
}

def map_elements(xml_element, content_dict, mapper):
    '''Use the mapper constants to map xml element content to content dictionaries, if the target content is present.'''
    for content_key, content_element in mapper.items():
        try:
            content_dict[content_key] = xml_element.find(content_element).text
        except AttributeError:
            content_dict[content_key] = None


def parse_header(xml_root):
    _header = xml_root.find(RETURN_HEADER_PATH)

    _header_content = {}

    # Update header content
    map_elements(_header, _header_content, HEADER_CHILD_MAPPER)

    # TODO: Test past 15,000 samples
    _header_content['NumOfficers'] = len(_header.findall(f'./{NAMESPACE}BusinessOfficerGrp'))

    return _header_content

# TODO: Handle Form 990-T
# TODO: Handle multiple input variants for Form 990 I
    # ? Can this be pulled from ProPublica API?
# TODO: Handle multiple input variants for Form 990 K
    # ? Can this be pulled from ProPublica API?
def parse_return(xml_root):
    _return = xml_root.find(RETURN_DATA_PATH + f'/{NAMESPACE}IRS990')

    if _return is None:
        return None

    _return_content = {}

    # Update return content
    map_elements(_return, _return_content, RETURN_CHILD_MAPPER)

    return _return_content
