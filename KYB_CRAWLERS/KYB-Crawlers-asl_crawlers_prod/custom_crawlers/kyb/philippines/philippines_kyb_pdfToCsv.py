import tabula

# INPUT PDF_URLS these pdf files are converted into csv, stored in input and then csv files are parsed for data 
PDF_URLS = [
        'https://www.sec.gov.ph/wp-content/uploads/2019/12/2015Directory_ExchangeSelfRegulatoryOrganizationClearingAgencyDepository.pdf',
        'https://www.sec.gov.ph/wp-content/uploads/2019/12/2017TA_RegisteredTransferAgentsandListedIssuesHandledasofJuly2016.pdf',
        'https://www.sec.gov.ph/wp-content/uploads/2019/12/2019Issuer_RegisteredEquitySecuritiesUnlisted.pdf',
        'https://www.sec.gov.ph/wp-content/uploads/2023/01/2023List_List-of-Registered-Issuers-of-Propritary-and-Non-Proprietary-Securities_as-of-31DEC2022.pdf',
        'https://www.sec.gov.ph/wp-content/uploads/2019/12/2016Issuer_IssuersofRegisteredDebtSecuritiesCommercialPapersorBonds.pdf',
        'https://www.sec.gov.ph/wp-content/uploads/2019/12/2016Issuer_RegisteredSecuritiestothePublicListedwiththeExchange.pdf',
        'https://www.sec.gov.ph/wp-content/uploads/2023/01/2023List_List-of-Public-Companies_as-of-31-DEC-2022.pdf',
        'https://www.sec.gov.ph/wp-content/uploads/2023/01/2023List_List-of-Mutual-Funds_as-of-31DEC-2022.pdf'
        ]

def pdf_to_csv():
    for i, pdf_path in enumerate(PDF_URLS):
        print(i, pdf_path)
        pages = tabula.read_pdf(pdf_path, stream=True, pages='all', guess=False)
        # tabula.convert_into(pdf_path, f"philippines/input/output-{i}.csv", output_format="csv", pages='all')


# Main execution entry
# pdf_to_csv converts pdf files from PDF_URLS into csv files in philippines/input directory
# pdf_to_csv()

