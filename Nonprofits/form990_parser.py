
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
    # 35b - Engage in transaction w/Controlled entity --> If yes, Schedule R, Part V, Line 2
    'TransactionWithControlEntInd': f'{NAMESPACE}TransactionWithControlEntInd',
    # Q36 - (Only for 501c3s) Transfers to exempt non-charitable related org
    # --> If yes, Schedule R, Part V, line 2
    'TrnsfrExmptNonChrtblRltdOrgInd': f'{NAMESPACE}TrnsfrExmptNonChrtblRltdOrgInd',
    # Q37 - Org conducted >5% of activities through unrelated entity --> If yes, Schedule R, Part VI
    'ActivitiesConductedPrtshpInd': f'{NAMESPACE}ActivitiesConductedPrtshpInd',
    # Q38 - Did org complete Schedule O; All orgs should
    'ScheduleORequiredInd': f'{NAMESPACE}ScheduleORequiredInd',
    # * Part V - Statements Regarding Other IRS Filings and Tax Compliance
    # 2a - Employee count
    'EmployeeCnt': f'{NAMESPACE}EmployeeCnt',
    # 4a - Foreing financial account
    'ForeignFinancialAccountInd': f'{NAMESPACE}ForeignFinancialAccountInd',
    # 6a - >$100k gross receipts on average & solicit tax-deductible contributions
    'NondeductibleContributionsInd': f'{NAMESPACE}NondeductibleContributionsInd',
    # Orgs maintaining donor advised funds
    # 8 - Excess business holdings of donor advised funds
    'DAFExcessBusinessHoldingsInd': f'{NAMESPACE}DAFExcessBusinessHoldingsInd',
    # 9a - Taxable distributions
    'TaxableDistributionsInd': f'{NAMESPACE}TaxableDistributionsInd',
    # 9a - Distributions to donor, donor adviser, or related person
    'DistributionToDonorInd': f'{NAMESPACE}DistributionToDonorInd',
    # 15 - Subject to section 4960 tax?
    'SubjToTaxRmnrtnExPrchtPymtInd': f'{NAMESPACE}SubjToTaxRmnrtnExPrchtPymtInd',
    # * Part IV - Governance, Management, and Disclosure
    # * Section A. Governing Body and Management
    # 1a - Number voting members
    'GoverningBodyVotingMembersCnt': f'{NAMESPACE}GoverningBodyVotingMembersCnt',
    # 1b - Number independent voting members
    'IndependentVotingMemberCnt': f'{NAMESPACE}IndependentVotingMemberCnt',
    # 3 - Delegate control to management company or person
    'DelegationOfMgmtDutiesInd': f'{NAMESPACE}DelegationOfMgmtDutiesInd',
    # 4 - Significant chagnes since previous filing
    'ChangeToOrgDocumentsInd': f'{NAMESPACE}ChangeToOrgDocumentsInd',
    # 5 - Became aware of significant diversion of assets in previous year
    'MaterialDiversionOrMisuseInd': f'{NAMESPACE}MaterialDiversionOrMisuseInd',
    # 6 - Did org have members/stockholders
    'MembersOrStockholdersInd': f'{NAMESPACE}MembersOrStockholdersInd',
    # 7a - Members/Stockholders have power to elect board
    'ElectionOfBoardMembersInd': f'{NAMESPACE}ElectionOfBoardMembersInd',
    # 7b - Decisions subject to approval from anyone besides the board
    'DecisionsSubjectToApprovaInd': f'{NAMESPACE}DecisionsSubjectToApprovaInd',
    # 8a - Documented governing body's actions
    'MinutesOfGoverningBodyInd': f'{NAMESPACE}MinutesOfGoverningBodyInd',
    # 8b - Documented actions of each committee w/authority to act on behalf of governing body
    'MinutesOfCommitteesInd': f'{NAMESPACE}MinutesOfCommitteesInd',
    # 9 - Any officer that cannot be reached at company address in Part VII, Section A --> If yes, provide names/addresses in Schedule O
    'OfficerMailingAddressInd': f'{NAMESPACE}OfficerMailingAddressInd',
    # * Section B - Policies
    # 15a - Review and approval for deciding CEO/Top management official compensation
    # --> If yes, outline in Schedule O
    'CompensationProcessCEOInd': f'{NAMESPACE}CompensationProcessCEOInd',
    # 15b - Review and approval for deciding officer/key employee compensation
    # --> If yes, outline in Schedule O
    'CompensationProcessOtherInd': f'{NAMESPACE}CompensationProcessOtherInd',
    # * Part VII - Compensation of Officers, Directors, Trustees, Key Employees, Highest Compensated Employees, and Independent Contractors
    # * Section A - Officers, Directors, Trustees, Key Employees, and Highest Compensated Employees
    # 1d Column D - Reportable compensation from org
    'TotalReportableCompFromOrgAmt': f'{NAMESPACE}TotalReportableCompFromOrgAmt',
    # 1d Column E - Reportable compensation from related orgs
    'TotReportableCompRltdOrgAmt': f'{NAMESPACE}TotReportableCompRltdOrgAmt',
    # 1d Column F - Estimated amount of OTHER compensation from org and related orgs
    'TotalOtherCompensationAmt': f'{NAMESPACE}TotalOtherCompensationAmt',
    # 2 - Total number of individuals making more than $100K
    'IndivRcvdGreaterThan100KCnt': f'{NAMESPACE}IndivRcvdGreaterThan100KCnt',
    # 3 - Did org list any former officer/director or trustee/key employee, or highest comped employee in 1a?
    # --> If yes, Schedule J for person
    'FormerOfcrEmployeesListedInd': f'{NAMESPACE}FormerOfcrEmployeesListedInd',
    # 4 - Any individual sum of compensation in 1a >$150K? --> If yes, Schedule J for person
    'TotalCompGreaterThan150KInd': f'{NAMESPACE}TotalCompGreaterThan150KInd',
    # 5 - Did any person listed in 1a get compensation from unrelated org/individual for org services?
    # --> If yes, Schedule J for person
    'CompensationFromOtherSrcsInd': f'{NAMESPACE}CompensationFromOtherSrcsInd',
    # * Section B - Independent Contractors
    # Total number of independent contractors including those listed (paid >$100K)
    'CntrctRcvdGreaterThan100KCnt': f'{NAMESPACE}CntrctRcvdGreaterThan100KCnt',
    # * Part VIII - Statement of Revenue
    # 1a - Federated Campaigns
    'FederatedCampaignsAmt': f'{NAMESPACE}FederatedCampaignsAmt',
    # 1b - Membership dues
    'MembershipDuesAmt': f'{NAMESPACE}MembershipDuesAmt',
    # 1c - Fundraising events
    'FundraisingAmt': f'{NAMESPACE}FundraisingAmt',
    # 1d - Related organizations
    'RelatedOrganizationsAmt': f'{NAMESPACE}RelatedOrganizationsAmt',
    # 1e - Government grants (contributions)
    'GovernmentGrantsAmt': f'{NAMESPACE}GovernmentGrantsAmt',
    # 1f - All other contributions, gifts, grants, and similar amounts not listed in 1a-1e
    'AllOtherContributionsAmt': f'{NAMESPACE}AllOtherContributionsAmt',
    # 1g - Noncash contributions included in 1a-1f
    'NoncashContributionsAmt': f'{NAMESPACE}NoncashContributionsAmt',
    # 1h - Total of 1a-1f
    'TotalContributionsAmt': f'{NAMESPACE}TotalContributionsAmt',
    # ? Do we want to include TotalProgramServiceRevenueAmt in addition to the major totals below?
    # 2g - Total program service revenue amount (sum 2a-2f; housed in own table)
    'TotalProgramServiceRevenueAmt': f'{NAMESPACE}TotalProgramServiceRevenueAmt',
    # Note: Flattening this section to grab totals
    # 12A - Total revenue
    'TotalRevenueColumnAmt': f'{NAMESPACE}TotalRevenueGrp/{NAMESPACE}TotalRevenueColumnAmt',
    # 12B - Total related or exemption function revenue
    'RelatedOrExemptFuncIncomeAmt': f'{NAMESPACE}TotalRevenueGrp/{NAMESPACE}RelatedOrExemptFuncIncomeAmt',
    # 12C - Total unrelated business revenue
    'UnrelatedBusinessRevenueAmt': f'{NAMESPACE}TotalRevenueGrp/{NAMESPACE}UnrelatedBusinessRevenueAmt',
    # 12B - Total revenue excluded from tax under sections 512-514
    'ExclusionAmt': f'{NAMESPACE}TotalRevenueGrp/{NAMESPACE}ExclusionAmt',
    # * Part X - Balance Sheet
    # TODO: Determine if we care if org follows FASB ASC 958
    # TODO: Save whether or not Org follows FASB ASC 958
        # Yes: OrganizationFollowsSFAS117Ind 
        # No: OrgDoesNotFollowFASB117Ind
}

def get_return_type(xml_root):
    return xml_root.find(f'.//{NAMESPACE}ReturnTypeCd').text

def get_990PF_org_type(xml_root):
    try: # Element may not be present, and may not indicate appropriate org type
        c_type = xml_root.find(f'.//{NAMESPACE}Organization501c3ExemptPFInd').text
        return '501c3'
    except AttributeError:
        pass
    
    try: #
        o_type = xml_root.find(f'.//{NAMESPACE}Organization4947a1TrtdPFInd').text
        return '4947 Trust'
    except AttributeError:
        pass
    
    try: #
        o_type = xml_root.find(f'.//{NAMESPACE}InitialReturnFormerPubChrtyInd').text
        return 'Former Public Charity'
    except AttributeError:
        return 'Other'
    
    
    
    

def get_990T_org_type(xml_root):
    try: # Element may not be present, and may not indicate appropriate org type
        c_type = xml_root.find(f'.//{NAMESPACE}Organization501cTypeText').text
        # Also want type to be 'Corporation' and not 'Trust'
        org_type = xml_root.find(f'.//{NAMESPACE}Organization501cCorporationInd').text
        return f'501{c_type}'
    except AttributeError:
        return 'Other'

def get_990Standard_org_type(xml_root):
    # Is a 501c3
    try: # If this field exits, then it's a 501c3
        _501c3 = xml_root.find(f'.//{NAMESPACE}Organization501c3Ind').text
        return '501c3'
    except AttributeError:
        pass

    # Is a 501c4
    try: # Element may not be present, and may not indicate appropriate org type
        _501c = xml_root.find(f'.//{NAMESPACE}Organization501cInd').attrib
        c_type = _501c['organization501cTypeTxt']
        return f'501c{c_type}'
    except AttributeError:
        pass

    # Is a 527
    # TODO: Confirm the 527 target is spelled this way
    try:
        _527 = xml_root.find(f'.//{NAMESPACE}Organization527').text
        return '527'
    except AttributeError:
        pass

    # Assuming no other possible values in field I
    return '4947a1'

def get_org_type(xml_root, return_type_cd):
    
    if return_type_cd in ['990', '990N', '990EZ']:
        return get_990Standard_org_type(xml_root)
    elif return_type_cd == '990T':
        return get_990T_org_type(xml_root)
    elif return_type_cd == '990PF':
        return get_990PF_org_type(xml_root)
    else:
        return 'Unknown'


def map_elements(xml_element, content_dict, mapper):
    '''Use the mapper constants to map xml element content to content dictionaries, if the target content is present.'''
    for content_key, content_element in mapper.items():
        try:
            content_dict[content_key] = xml_element.find(content_element).text
        except AttributeError:
            content_dict[content_key] = None


def parse_header(xml_root, xml_file_name, org_type):
    _header = xml_root.find(RETURN_HEADER_PATH)

    _header_content = {}

    # Update header content
    map_elements(_header, _header_content, HEADER_CHILD_MAPPER)

    _header_content['org_type'] = org_type
    _header_content['file_name'] = xml_file_name
    # TODO: Test past 15,000 samples
    _header_content['NumOfficers'] = len(_header.findall(f'./{NAMESPACE}BusinessOfficerGrp'))

    return _header_content

# TODO: Handle Form 990-T
# TODO: Handle multiple input variants for Form 990 I
    # ? Can this be pulled from ProPublica API?
# TODO: Handle multiple input variants for Form 990 K
    # ? Can this be pulled from ProPublica API?
def parse_return(xml_root, org_ein):
    _return = xml_root.find(IRS990_PATH)

    if _return is None:
        return None

    _return_content = {}

    # Update return content
    map_elements(_return, _return_content, RETURN_CHILD_MAPPER)

    _employees = parse_employees(_return, org_ein)
    _contractors = parse_contractors(_return, org_ein)
    _expenses = parse_expenses(_return, org_ein)
    _balance_sheet = parse_balance_sheet(_return, org_ein)
    return _return_content, _employees, _contractors, _expenses, _balance_sheet


# TODO: Part VI, Section C. Disclosure data collection
def parse_section_C(irs990_elem, org_ein):
    targets = {
        # 17 - States where a copy of 990 is required to be filed
        # * Note: Use .findall() to save this as a list of states
        'StatesWhereCopyOfReturnIsFldCd': f'{NAMESPACE}StatesWhereCopyOfReturnIsFldCd',
        # 18 - Where does org make 1023, 990, and 990-Ts available?
        'OwnWebsiteInd': f'{NAMESPACE}OwnWebsiteInd',
        'UponRequestInd': f'{NAMESPACE}UponRequestInd'
        # TODO: Find target for 'Another's website'
        # TODO: Find target for 'Other (explain in Schedule O)'
    }
    
    # TODO: BooksInCareOfDetail + Their address<BooksInCareOfDetail>:
    # <BooksInCareOfDetail>
    #     <PersonNm>Christine'K': f'{NAMESPACE}',
    #     'PhoneNum': f'{NAMESPACE}',
    #     <USAddress>
    #         <AddressLine1Txt>1400'JACKSON': f'{NAMESPACE}',
    #       'abc': 'CityNm': f'{NAMESPACE}',
    #       'abc': 'StateAbbreviationCd': f'{NAMESPACE}',
    #       'abc': 'ZIPCd''    ': f'{NAMESPACE}',


# ! I plan to have this inside the parse_return, so we will know if the irs990 exists already
def parse_employees(irs990_elem, org_ein):

    _employee_data = []

    for employee in irs990_elem.findall(f'{NAMESPACE}Form990PartVIISectionAGrp'):
        employee_content = {'EIN': org_ein}

        for field in employee:
            field_key = field.tag.replace(NAMESPACE, '')
            employee_content[field_key] = field.text
        _employee_data.append(employee_content)

    return _employee_data

# ! I plan to have this inside the parse_return, so we will know if the irs990 exists already
def parse_contractors(irs990_elem, org_ein):

    _contractor_data = []

    for contractor in irs990_elem.findall(f'{NAMESPACE}ContractorCompensationGrp'):
        contractor_content = {'EIN': org_ein}

        # Recursively go through element nesting
        for field in contractor.iter():
            # Forget parent elements
            if len(field) > 0:
                continue
            field_key = field.tag.replace(NAMESPACE, '')
            contractor_content[field_key] = field.text
        _contractor_data.append(contractor_content)

    return _contractor_data

def parse_expenses(irs990_elem, org_ein):
    _expense_data = []

    _expense_groups = {
        'Grants_DomesticGroup': 'GrantsToDomesticOrgsGrp',
        'Grants_DomesticIndividuals': 'GrantsToDomesticIndividualsGrp',
        'Compensation_CurrentOfficersDirectors': 'CompCurrentOfcrDirectorsGrp',
        'Fees_Lobbying': 'FeesForServicesLobbyingGrp',
        'Fees_ProfessionalFundraising': 'FeesForServicesProfFundraising',
        'Payment_TravelForPublicOfficials': 'PymtTravelEntrtnmntPubOfclGrp',
    }

    for expense_type_key, expense_type_target in _expense_groups.items():
        _expense_content = {
            'EIN': org_ein,
            'ExpenseType': expense_type_key
        }

        expense_type_group = irs990_elem.find(f'{NAMESPACE}{expense_type_target}')
        
        if expense_type_group is None:
            continue

        for expense_type_field in expense_type_group:
            field_key = expense_type_field.tag.replace(NAMESPACE, '')
            _expense_content[field_key] = expense_type_field.text

        _expense_data.append(_expense_content)

    return _expense_data

def parse_balance_sheet(irs990_elem, org_ein):
    _balance_sheet_data = []

    _balance_sheet_groups = {
        'Assets': {
            'PledgesAndGrantsReceivable': 'GrantsToDomesticOrgsGrp',
            'TotalAssets': 'TotalAssetsGrp',
        },
        'Liabilities': {
            'TotalLiabilities': 'TotalLiabilitiesGrp',
        },
        'NetAssetsOrFundBalances': {
            # Old versions?
            'NetAssets_Unrestricted': 'UnrestrictedNetAssetsGrp',
            'NetAssets_TemporarilyRestricted': 'TemporarilyRstrNetAssetsGrp',
            'NetAssets_PermanentlyRestricted': 'PermanentlyRstrNetAssetsGrp',
            # New versions?
            'NetAssets_DonorRestrictions': 'DonorRestrictionNetAssetsGrp',
            'NetAssets_NoDonorRestrictions': 'NoDonorRestrictionNetAssetsGrp',
        }
    }

    for _balance_sheet_group, _balance_sheet_group_dict in _balance_sheet_groups.items():
        for balance_sheet_key, balance_sheet_target in _balance_sheet_group_dict.items():
            _balance_sheet_content = {
                'EIN': org_ein,
                'BalanceSheetSection': _balance_sheet_group,
                'BalanceSheetSubsection': balance_sheet_key
            }

            _balance_sheet_elemp = irs990_elem.find(f'{NAMESPACE}{balance_sheet_target}')

            if _balance_sheet_elemp is None:
                continue

            for balance_sheet_field in _balance_sheet_elemp:
                field_key = balance_sheet_field.tag.replace(NAMESPACE, '')
                _balance_sheet_content[field_key] = balance_sheet_field.text

            _balance_sheet_data.append(_balance_sheet_content)

    return _balance_sheet_data
