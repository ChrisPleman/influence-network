* Orgs can file 990s and 990-Ts in the same year (e.g., 2517121)

* *H(a)* Is this a group retrun for subordinates?
    * No --> `<GroupReturnForAffiliatesInd>false</GroupReturnForAffiliatesInd>`
        * *OR* --> `<GroupReturnForAffiliatesInd>0</GroupReturnForAffiliatesInd>`

* *I* Tax-exempt status:
    * 501(c)(3) --> `<Organization501c3Ind>X</Organization501c3Ind>`
    * 501 (c) (NUM) (insert no.) --> `<Organization501cInd organization501cTypeTxt="NUM">X</Organization501cInd>`

* *J* Website:
    * NO RESPONSE --> NO ELEMENT
    * TEXT PROVIDED --> `<WebsiteAddressTxt>WEB ADDRESS</WebsiteAddressTxt>`

* *K* Form of organization:
    * Corporation --> `<TypeOfOrganizationCorpInd>X</TypeOfOrganizationCorpInd>`
    * Other --> `<TypeOfOrganizationOtherInd>X</TypeOfOrganizationOtherInd>`
        * *AND* --> `<OtherOrganizationDsc>INSERTED DESC</OtherOrganizationDsc>`
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
