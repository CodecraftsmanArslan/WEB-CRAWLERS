response = requests.get("https://www.gabar.org/membersearchresults.cfm", verify=False)
# soup=BeautifulSoup(response.content,"html.parser")
# links=soup.find_all('div',class_="member-name")
# base_url="https://www.gabar.org/"