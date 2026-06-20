
# TODO: Add type hinting

# * XML File Constants
NAMESPACE = '{http://www.irs.gov/efile}'
RETURN_HEADER_PATH = f'./{NAMESPACE}ReturnHeader'
PREPARER_FIRM_GROUP_PATH = f'./{NAMESPACE}PreparerFirmGrp'
FILER_PATH = f'./{NAMESPACE}Filer'
RETURN_DATA_PATH = f'./{NAMESPACE}ReturnData'
IRS990_PATH = RETURN_DATA_PATH + f'/{NAMESPACE}IRS990'

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
    # 'BusinessOfficerDiscussWithPaidPreparer': f'./{NAMESPACE}BusinessOfficerGrp/{NAMESPACE}DiscussWithPaidPreparerInd',
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
    # * Part IV: Checklist of Required Schedules
    #Q1 - 501(c)(3) or 4947(a)(1) ? --> If yes, Schedule A
    'DescribedInSection501c3': f'{NAMESPACE}DescribedInSection501c3Ind',
    #Q2 - Schedule of Contributors
    'ScheduleBRequired': f'{NAMESPACE}ScheduleBRequiredInd', 
    #Q3 - Political campaign activities --> If yes, Schedule C, Part I
    'PoliticalCampaignActy': f'{NAMESPACE}PoliticalCampaignActyInd',
    #Q4 - Lobbying --> If yes, Schedule C, Part II
    'LobbyingActivities': f'{NAMESPACE}LobbyingActivitiesInd',
    #Q6 - Donor advised funds --> If yes, Schedule D, Part I
    'DonorAdvisedFund': f'{NAMESPACE}DonorAdvisedFundInd',
    #Q14a - Foreign office, employees, agents
    'ForeignOfficeInd': f'{NAMESPACE}ForeignOfficeInd',
    #Q14b - If yes, Schedule F Part I and IV
    'ForeignActivitiesInd': f'{NAMESPACE}ForeignActivitiesInd',
    #Q15 - >$5K grants to/from foreign orgs --> If yes, Schedule F, parts II and IV
    'MoreThan5000KToOrgInd': f'{NAMESPACE}MoreThan5000KToOrgInd',
    #Q16 - >$5K grants to/from foreign orgs --> If yes, Schedule F, parts III and IV
    'MoreThan5000KToIndividualsInd': f'{NAMESPACE}MoreThan5000KToIndividualsInd',
    #Q17 - >$15K for professional fundraising --> If yes, Schedule G, part II
    'ProfessionalFundraisingInd': f'{NAMESPACE}ProfessionalFundraisingInd',
    #Q18 - >$15K professional fundraising income --> If yes, Schedule G, part III
    'FundraisingActivitiesInd': f'{NAMESPACE}FundraisingActivitiesInd',
    #Q21 - >$5K grants to domestic orgs --> If yes, Schedule I, parts I and II
    'GrantsToOrganizationsInd': f'{NAMESPACE}GrantsToOrganizationsInd',
    #Q22 - >$5K grants to domestic individuals --> If yes, Schedule I, parts I and III
    'GrantsToIndividualsInd': f'{NAMESPACE}GrantsToIndividualsInd',
    #Q23 - Yes to Part VII, Section A line 3, 4, or 5? --> If yes, Schedule J
    'ScheduleJRequiredInd': f'{NAMESPACE}ScheduleJRequiredInd',
    # TODO: Find target for Q25a
    # TODO: Find target for Q25b
    # TODO: Find target for Q26
    # ? is this both Q26 and Q27?
    'GrantToRelatedPersonInd': f'{NAMESPACE}GrantToRelatedPersonInd',
    # Q28 - Org party to business transaction w/:
    # Q28a - current former officer, director... --> If yes, Schedule L, Part IV
    'BusinessRlnWithOrgMemInd': f'{NAMESPACE}BusinessRlnWithOrgMemInd',
    # Q28b - family member or anything in 28a --> If yes, Schedule L, Part IV
    'BusinessRlnWithFamMemInd': f'{NAMESPACE}BusinessRlnWithFamMemInd',
    # Q28c - 35% controlled entity or 28a or 28b --> If yes, Schedule L, Part IV
    'BusinessRlnWith35CtrlEntInd': f'{NAMESPACE}BusinessRlnWith35CtrlEntInd',
    # Q31 - Did org terminate --> If yes, Schedule N, Part I
    'TerminateOperationsInd': f'{NAMESPACE}TerminateOperationsInd',
    # Q32 - >25% assets --> If yes, Schedule N, Part II
    'PartialLiquidationInd': f'{NAMESPACE}PartialLiquidationInd',
    # Q33 - Own 100% of diresgarded entity --> If yes, Schedule R, Part I
    'DisregardedEntityInd': f'{NAMESPACE}DisregardedEntityInd',
    # Q34 - Related to other tax-exempt or taxable entity
    # --> If yes, Schedule R, Part II, III, or IV, and Part V line 1
    'RelatedEntityInd': f'{NAMESPACE}RelatedEntityInd',
    # 35a - Control of another entity --> If yes, answer 35b
    'RelatedOrganizationCtrlEntInd': f'{NAMESPACE}RelatedOrganizationCtrlEntInd',
    # TODO: Find target for 35b
    # Q36 - (Only for 501c3s) Transfers to exempt non-charitable related org
    # --> If yes, Schedule R, Part V, line 2
    'TrnsfrExmptNonChrtblRltdOrgInd': f'{NAMESPACE}TrnsfrExmptNonChrtblRltdOrgInd',
    # Q37 - Org conducted >5% of activities through unrelated entity --> If yes, Schedule R, Part VI
    'ActivitiesConductedPrtshpInd': f'{NAMESPACE}ActivitiesConductedPrtshpInd',
    # Q38 - Did org complete Schedule O; All orgs should
    'ScheduleORequiredInd': f'{NAMESPACE}ScheduleORequiredInd',
    # * Part V - Statements Regarding Other IRS Filings and Tax Compliance
    # 2a - Employee count
    'EmployeeCnt': f'{NAMESPACE}EmployeeCnt'
    # TODO: Find target for 2b
}


def org_type(xml_root):
    irs990 = xml_root.find(IRS990_PATH)

    # Is a 501c3
    try: # If this field exits, then it's a 501c3
        _501c3 = irs990.find(f'{NAMESPACE}Organization501c3Ind').text
        print(_501c3.tag)
        return '501c3'
    except AttributeError:
        pass

    # Is a 501c4
    try: # Element may not be present, and may not indicate appropriate org type
        _501c = irs990.find(f'{NAMESPACE}Organization501cInd').attrib
        c_type = _501c['organization501cTypeTxt']
        return f'501c{c_type}'
    except AttributeError:
        pass

    # Is a 527
    # TODO: Confirm the 527 target is spelled this way
    try:
        _527 = irs990.find(f'{NAMESPACE}Organization527').text
        return '527'
    except AttributeError:
        pass

    # Assuming no other possible values in field I
    return '4947a1'


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
    _return = xml_root.find(IRS990_PATH)

    if _return is None:
        return None

    _return_content = {}

    # Update return content
    map_elements(_return, _return_content, RETURN_CHILD_MAPPER)

    return _return_content

# ! I plan to have this inside the parse_return, so we will know if the irs990 exists already
def parse_employees(irs990, org_ein):
    _irs990 = irs990.find(IRS990_PATH)

    employee_data = []

    for employee in _irs990.findall(f'{NAMESPACE}Form990PartVIISectionAGrp'):
        employee_content = {'EIN': org_ein}
        
        for field in employee:
            employee[field.tag] = field.text
        
        employee_data.append(employee_content)

    return employee_data