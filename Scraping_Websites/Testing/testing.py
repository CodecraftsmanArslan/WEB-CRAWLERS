from bs4 import BeautifulSoup

html = '''
<tr class="rgAltRow rgSelectedRow" id="ctl01_TemplateBody_WebPartManager1_gwpciNewQueryMenuCommon_ciNewQueryMenuCommon_ResultsGrid_Grid1_ctl00__9" role="row" aria-selected="true">
    <td role="gridcell">
        <div class="row MemberSearch" style="display: flex; align-items: center;">
            <div class="col-md-4 col-sm-12 profileImg">
                <img src="/assets/images/default/person.png" alt="">
            </div>
            <div class="col-md-4 col-sm-6">
                <h3>Mr. Thomas Wayne Cary</h3>
                Special Member – A member in good standing not actively engaged in the private practice of law <br> <br>
                Samford University Cumberland School of Law<br>
                Date Admitted: 04/30/1999<br> <br>
                PO Box 194<br>
                Barrow, AK 99723-0194<br>
                (907) 852-0300<br>
                <a href="http://" target="_blank"></a>
            </div>
        </div>
    </td>
</tr>
'''

# Parse the HTML
soup = BeautifulSoup(html, 'html.parser')

# Extract name
name = soup.find('h3').get_text(strip=True)

# Extract license
license = soup.find('div', class_='col-md-4 col-sm-6').find('p').get_text(strip=True)

# Extract university
university = soup.find('div', class_='col-md-4 col-sm-6').find('br').previous_sibling.strip()

# Extract date
date_admitted = soup.find('div', class_='col-md-4 col-sm-6').find(text='Date Admitted:').next_sibling.strip()

# Extract address and phone
address, phone = None, None
address_phone_text = soup.find('div', class_='col-md-4 col-sm-6').find_all('br')[-1].next_sibling.strip()
if '(' in address_phone_text and ')' in address_phone_text:
    phone = address_phone_text
else:
    address = address_phone_text

# Print the extracted information
print("Name:", name)
print("License:", license)
print("University:", university)
print("Date Admitted:", date_admitted)
print("Address:", address)
print("Phone:", phone)






//div[@class="col-md-4 col-sm-6"]//h3
//div[@class="col-md-4 col-sm-6"]/h3/following-sibling::text()[1]
//div[@class="col-md-4 col-sm-6"]/a/text()
//div[@class="col-md-4 col-sm-6"]/text()[contains(., "(")]
//div[@class="col-md-4 col-sm-6"]/text()[contains(., "Date ")]



try:
//div[@class="col-md-4 col-sm-6"]/h3/following-sibling::text()[2]
except:
    //div[@class="col-md-4 col-sm-6"]/h3/following-sibling::text()[3]

