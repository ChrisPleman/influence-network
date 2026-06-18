* Orgs can file 990s and 990-Ts in the same year (e.g., EIN 2517121 | most recent [990-T pdf](https://apps.irs.gov/pub/epostcard/cor/272517121_202506_990T_2026042224116911.pdf))

* *H(a)* Is this a group retrun for subordinates?
    * No --> `<GroupReturnForAffiliatesInd>false</GroupReturnForAffiliatesInd>`
        * *OR* --> `<GroupReturnForAffiliatesInd>0</GroupReturnForAffiliatesInd>`
    * File/Example used for this:
        * Ex 1:
            * File: 202641139349301904_public.xml
            * EIN: 237216506
            * Link to 2024 [PDF](https://apps.irs.gov/pub/epostcard/cor/237216506_202412_990O_2026032524042773.pdf)
        * Ex 2:
            * File: 202641139349301924_public.xml
            * EIN: 452499732
            * Link to 2024 [PDF](https://apps.irs.gov/pub/epostcard/cor/237216506_202412_990O_2026032524042773.pdf)


* *I* Tax-exempt status:
    * 501(c)(3) --> `<Organization501c3Ind>X</Organization501c3Ind>`
    * 501 (c) (NUM) (insert no.) --> `<Organization501cInd organization501cTypeTxt="NUM">X</Organization501cInd>`
    * File/Example used for this:
        * Ex 1:
            * File: 202641139349301904_public.xml
            * EIN: 237216506
            * Link to 2024 [PDF](https://apps.irs.gov/pub/epostcard/cor/237216506_202412_990O_2026032524042773.pdf)
        * Ex 2:
            * File: 202641139349301924_public.xml
            * EIN: 452499732
            * Link to 2024 [PDF](https://apps.irs.gov/pub/epostcard/cor/237216506_202412_990O_2026032524042773.pdf)

* *J* Website:
    * NO RESPONSE --> NO ELEMENT
    * TEXT PROVIDED --> `<WebsiteAddressTxt>WEB ADDRESS</WebsiteAddressTxt>`
    * File/Example used for this:
        * Ex 1:
            * File: 202641139349301904_public.xml
            * EIN: 237216506
            * Link to 2024 [PDF](https://apps.irs.gov/pub/epostcard/cor/237216506_202412_990O_2026032524042773.pdf)
        * Ex 2:
            * File: 202641139349301924_public.xml
            * EIN: 452499732
            * Link to 2024 [PDF](https://apps.irs.gov/pub/epostcard/cor/237216506_202412_990O_2026032524042773.pdf)

* *K* Form of organization:
    * Corporation --> `<TypeOfOrganizationCorpInd>X</TypeOfOrganizationCorpInd>`
    * Other --> `<TypeOfOrganizationOtherInd>X</TypeOfOrganizationOtherInd>`
        * *AND* --> `<OtherOrganizationDsc>INSERTED DESC</OtherOrganizationDsc>`
    * File/Example used for this:
        * Ex 1:
            * File: 202641139349301904_public.xml
            * EIN: 237216506
            * Link to 2024 [PDF](https://apps.irs.gov/pub/epostcard/cor/237216506_202412_990O_2026032524042773.pdf)
        * Ex 2:
            * File: 202641139349301924_public.xml
            * EIN: 452499732
            * Link to 2024 [PDF](https://apps.irs.gov/pub/epostcard/cor/237216506_202412_990O_2026032524042773.pdf)

### Part 1

* Abbrevations (in xml):
    * CY --> Current Year
    * PY --> Previous Year
    * BOY --> Beginning of Current Year
    * EOY --> End of Current Year

* Mission or activities:
    * Seems to be dependent on response to *K*:
        * OTHER --> `<OtherOrganizationDsc>Fraternal Organization</OtherOrganizationDsc>`
    * However, they still have the same element other orgs have that don't indicate other:
        * `<ActivityOrMissionDesc>Fraternal Organization</ActivityOrMissionDesc>`
    * There is a 2nd/3rd `<MissionDesc>` field/element in Part III

#### Expenses
* *16b* Total fundraising expenses:
    * Doesn't seem to have prior year option
