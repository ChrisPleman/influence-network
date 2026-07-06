def parse_scheduleA(scheduleA_elem, org_ein):
    
    _targets = {
        # * Section A - Public Support
        'PublicSupport': {
            'GiftsGrantsContributionsMemberships': 'GiftsGrantsContriRcvd170Grp',
            'TaxRevenues': 'TaxRevLeviedOrgnztnlBnft170Grp',
            'FreeGovService': 'GovtFurnSrvcFcltsVl170Grp',
            'TotalPrev3': 'TotalCalendarYear170Grp',
            'SubstantialContributors': 'SubstantialContributorsTotAmt',
            'TotalPublicSupport': 'PublicSupportTotal170Amt',
        },
        # * Section A - Total Support
        'TotalSupport': {
            'GrossIncome': 'GrossInvestmentIncome170Grp',
            'UnrelatedIncome': 'UnrelatedBusinessNetIncm170Grp',
            'OtherIncome': 'OtherIncome170Grp',
            'TotalSupport': 'TotalSupportAmt',
            'GrossRelatedActivities': 'GrossReceiptsRltdActivitiesAmt',
            'TotalPublicSupport': 'PublicSupportTotal170Amt',
        }
    }

# TODO: Handle sections that are just indicators for other schedules/sections:
        # # If exceeds 10% of line 25 column A, outline in Schedule O
        # 'Fees_OtherServices': 'FeesForServicesOtherGrp',

# ? Do we need this level of granularity?
# ! I plan to have this inside the parse_return, so we will know if the irs990 exists already
# TODO: InvestmentIncomeGrp
# TODO: IncmFromInvestBondProceedsGrp
# TODO: RoyaltiesRevenueGrp
# TODO: RoyaltiesRevenueGrp
# TODO: GrossRentsGrp
# TODO: LessRentalExpensesGrp
# TODO: RentalIncomeOrLossGrp
# TODO: NetRentalIncomeOrLossGrp
# TODO: GrossAmountSalesAssetsGrp
# TODO: LessCostOthBasisSalesExpnssGrp
# TODO: GainOrLossGrp
# TODO: NetGainOrLossInvestmentsGrp
# TODO: ....
def parse_revenues(irs990_elem, org_ein):

    _program_service_revenue_data = []

    for program_service_revenue in irs990_elem.findall(f'{NAMESPACE}ProgramServiceRevenueGrp'):
        program_service_revenue_content = {'EIN': org_ein}

        for field in program_service_revenue:
            field_key = field.tag.replace(NAMESPACE, '')
            program_service_revenue_content[field_key] = field.text
        program_service_revenue_content['other'] = 0
        _program_service_revenue_data.append(program_service_revenue_content)

    for program_service_revenue in irs990_elem.findall(f'{NAMESPACE}TotalOthProgramServiceRevGrp'):
        program_service_revenue_content = {'EIN': org_ein}

        for field in program_service_revenue:
            field_key = field.tag.replace(NAMESPACE, '')
            program_service_revenue_content[field_key] = field.text
        program_service_revenue_content['other'] = 1
        _program_service_revenue_data.append(program_service_revenue_content)

    return _program_service_revenue_data