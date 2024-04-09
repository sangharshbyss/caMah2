"""
Background:
from ws3.py of ca_mah project
"""
# imports
import logging
import time
from pathlib import Path

import pandas as pd
from selenium.common import NoSuchElementException, StaleElementReferenceException, TimeoutException, \
    InvalidSessionIdException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec, expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

# A. logging
logger = logging.getLogger(__name__)

class EachDistrict:
    # class instantiation
    def __init__(self, driver, from_date, to_date, name):
        self.driver = driver
        self.from_date = from_date
        self.to_date = to_date
        self.name = name

    def open_page(self, main_url):
        # open the page and refresh. Without refresh, it won't work.
        self.driver.get(main_url)
        self.driver.refresh()


    def enter_date(self):
        WebDriverWait(self.driver, 30).until(
            ec.presence_of_element_located((By.CSS_SELECTOR,
                                            '#ContentPlaceHolder1_txtDateOfRegistrationFrom')))

        from_date_field = self.driver.find_element(By.ID, "ContentPlaceHolder1_txtDateOfRegistrationFrom")

        to_date_field = self.driver.find_element(By.ID, "ContentPlaceHolder1_txtDateOfRegistrationTo")

        ActionChains(self.driver).click(from_date_field).send_keys(
            self.from_date).move_to_element(to_date_field).click().send_keys(
            self.to_date).perform()

    def district_selection(self):
        dist_list = Select(self.driver.find_element(By.CSS_SELECTOR,
                                                    "#ContentPlaceHolder1_ddlDistrict"))

        dist_list.select_by_visible_text(self.name)

    def view_record(self):
        view = Select(self.driver.find_element(By.ID, 'ContentPlaceHolder1_ucRecordView_ddlPageSize'))
        view.select_by_value("50")

    # 6. function for click on search
    def search(self):
        # Apart from clicking on search
        # this function also check if the record is above 0, and page is loaded.
        # if the record is below 0 it adds the district remaining district list.
        self.driver.find_element(By.CSS_SELECTOR, '#ContentPlaceHolder1_btnSearch').click()
        # check if page has loaded after clicking the search buttion. Wait for 10 sec
        # if page not loaded, throw error and proceed to next district.
        try:
            (WebDriverWait(self.driver, 10).until(
                expected_conditions.text_to_be_present_in_element((
                    By.ID, 'ContentPlaceHolder1_gdvDeadBody_lblSrNo_0'),
                    '1')))
            logger.info("search clicked. records found")
            return True
        except (TimeoutError, NoSuchElementException,
                TimeoutException, StaleElementReferenceException):
            # add to remaining district - code to be added later.
            logger.info("page did not load after search", exc_info=True)
            return False

    # 7 check number of records
    def number_of_records(self):
        total_number = self.driver.find_element(By.CSS_SELECTOR,
                                                '#ContentPlaceHolder1_lbltotalrecord').text
        logger.info(f'\nTotal number of Cases: {total_number}')
        return total_number

    # 8 check for particular act
    def check_and_download(self):
        # check for PoA in table.
        # if found, click and download FIR.
        table = self.driver.find_element(By.ID, "ContentPlaceHolder1_gdvDeadBody")
        rows = table.find_elements(By.TAG_NAME, "tr")
        # iterate over each row
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            # iterate over each cell
            for cell in cells:
                cell_text = cell.text
                # if the act is found, count it. and take details.
                if "अनुसूचीत जाती आणि अनुसूचीत" in cell_text:
                    download_link = row.find_element(By.TAG_NAME, "input")
                    download_link.click()
                    time.sleep(5)
        # logging
        logger.info("checking finished\n", exc_info=True)

    # writing data to file:
    # creates two sepearte files.
    def df_to_file(self):
        # get the table for cases from page
        # there is no need of wait actually as the page has already loaded and checked
        data = WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((
            By.CSS_SELECTOR, "#ContentPlaceHolder1_gdvDeadBody"))).get_attribute("outerHTML")
        all_df = pd.read_html(data)
        # 1. select 1st table as our intended dataframe
        # 2. drop last two rows as they are unnecessary
        # 3. drop column download as it has dyanamic link and not readable data.
        # 4. take df as output for next function.
        df_with_last_rows = all_df[0].drop(columns="Download")
        df = df_with_last_rows.drop(df_with_last_rows.tail(2).index)
        file_name = f'{self.name}_{self.from_date}_{self.to_date}.csv'
        dir_name = Path(
            f'/home/sangharsh/Documents/PoA/data/FIR/y_23/all_cases/'
            f'{self.from_date}_{self.to_date}')
        dir_name.mkdir(parents=True, exist_ok=True)
        df.to_csv(dir_name / file_name, index=False, mode='a', header=False)
        # file with cases with particular act
        poa_df = df[df['Sections'].str.contains("अनुसूचीत जाती आणि अनुसूचीत", na=False)]
        if len(poa_df.index) > 0:
            # while for call cases district wise file is maintained
            # for selected cases date wise file of all districts is maintained.
            poa_file = f'poa_{self.from_date}_{self.to_date}.csv'
            poa_dir_name = Path(f'/home/sangharsh/Documents/PoA/data/FIR/y_23/'
                                f'poa_cases')
            poa_dir_name.mkdir(parents=True, exist_ok=True)
            poa_df.to_csv(poa_dir_name / poa_file,
                          index=False, mode='a', header=False)
        else:
            pass

    def remaining_district(self):
        # creating a file to store district with dates where pages didn't load
        # it also tries to store the number of record of cases each district had
        dictionary = {'District': [self.name],
                      'from_date': str(self.from_date),
                      'to_date': str(self.to_date),
                      'number_of_record': [self.number_of_records()]}
        file_name = f'remaining_district_{self.from_date}_{self.to_date}.csv'
        dir_name = Path(f'/home/sangharsh/Documents/PoA/data/FIR/y_23/remaining_districts')
        dir_name.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame.from_dict(dictionary)
        df.to_csv(dir_name / file_name, mode='a', index=False, header=False)

    # 9 turn pages in loop and does further processing
    def each_page(self):
        # before calling next page
        # this function stores data on 1st page and then iterate over all pages
        total_number_of_records = self.number_of_records()
        logger.info(f"total number of records is : {total_number_of_records}"
                    f"\np1 started")
        try:
            self.df_to_file()
            self.check_and_download()
        except (NoSuchElementException,
                TimeoutError,
                StaleElementReferenceException):
            self.remaining_district()
            logger.info("problem at p1")
            return False
        next_page_text = (f'//*[@id="ContentPlaceHolder1_gdvDeadBody"]'
                          f'/tbody/tr[52]/td/table/tbody/tr/')
        i = 2
        fifty = 51
        while True:
            next_page_link = f'{next_page_text}td[{i}]/a'
            try:
                self.driver.find_element(By.XPATH,
                                         next_page_link).click()
                logger.info(f"p{i} clicked")
            except (TimeoutError, TimeoutException, InvalidSessionIdException,
                    NoSuchElementException,
                    StaleElementReferenceException):
                logger.info(f"pages finished. last page was p{i-1} ")
                return True
            try:
                WebDriverWait(self.driver, 10).until(expected_conditions.text_to_be_present_in_element(
                    (By.ID, 'ContentPlaceHolder1_gdvDeadBody_lblSrNo_0'), f'{str(fifty)}'))
                logger.info(f"p{i} loaded")
                # check the act and download the copy
                logger.info("checking and downloading copies")
                self.df_to_file()
                self.check_and_download()
            except (TimeoutError, TimeoutException, InvalidSessionIdException,
                    NoSuchElementException,
                    StaleElementReferenceException):
                # close the driver.
                last_page = i-1
                logger.warning(f" problem @ p{last_page}", exc_info=True)
                self.remaining_district()
                return False
            # for going to next page and checking if next page is loaded:
            i += 1
            fifty += 50

