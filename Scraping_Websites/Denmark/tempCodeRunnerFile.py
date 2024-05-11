
            try:
                next_page = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='next']")))
                if next_page:
                    next_page.click()
            except:
                print("No page avaliable")
                break