"""
Visit the website. enter details. take the data.
"""
import datetime
import logging
from pathlib import Path

from selenium.webdriver.firefox import webdriver
from selenium.webdriver.firefox.options import Options
from selenium import webdriver

from modules import dataCollection

# constatnts
main_url = r'https://citizen.mahapolice.gov.in/Citizen/MH/PublishedFIRs.aspx'
all_districts = ['AHMEDNAGAR', 'AKOLA', 'AMRAVATI CITY', 'AMRAVATI RURAL', 'BEED', 'BHANDARA', 'BULDHANA',
                 'CHANDRAPUR', 'CHHATRAPATI SAMBHAJINAGAR CITY', 'CHHATRAPATI SAMBHAJINAGAR (RURAL)',
                 'DHARASHIV', 'DHULE', 'GADCHIROLI', 'GONDIA', 'HINGOLI', 'JALGAON', 'JALNA',
                 'KOLHAPUR', 'LATUR', 'Mira-Bhayandar, Vasai-Virar Police Commissioner',
                 'NAGPUR CITY', 'NAGPUR RURAL', 'NANDED', 'NANDURBAR',
                 'NASHIK CITY', 'NASHIK RURAL', 'NAVI MUMBAI', 'PALGHAR', 'PARBHANI',
                 'PIMPRI-CHINCHWAD', 'PUNE CITY', 'PUNE RURAL', 'RAIGAD',
                 'RAILWAY MUMBAI', 'RAILWAY NAGPUR', 'RAILWAY PUNE', 'RATNAGIRI', 'SANGLI', 'SATARA',
                 'SINDHUDURG', 'SOLAPUR CITY', 'SOLAPUR RURAL', 'THANE CITY', 'THANE RURAL', 'WARDHA',
                 'WASHIM', 'YAVATMAL']


def main():
    logger = logging.getLogger(__name__)
    logging_file = "info.log"
    logging_dir = Path(f'/home/sangharsh/Documents/codes/CaseAnalysis/caMah2/logging')
    logging_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=logging_dir / logging_file,
                        format='%(name)s:: %(levelname)s:: %(asctime)s - %(message)s',
                        level=logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    logger.addHandler(ch)

    start = datetime.date(2023, 1, 13)
    end = datetime.date(2023, 6, 30)

    download_dir = Path(f'/home/sangharsh/Documents/PoA/'
                        f'data/FIR/FIR_copies/{start}_{end}')
    download_dir.mkdir(parents=True, exist_ok=True)

    options = Options()
    options.set_preference("browser.download.panel.shown", False)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    # profile.set_preference("browser.helperApps.neverAsk.openFile","application/pdf")
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", str(download_dir))
    # to go undetected
    options.set_preference("general.useragent.override",
                           "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:82.0) "
                           "Gecko/20100101 Firefox/82.0")
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference('useAutomationExtension', False)
    options.set_preference("pdfjs.disabled", True)
    # service = Service('C:\\BrowserDrivers\\geckodriver.exe')
    options.headless = True
    """options for proxy, but this is not working as if I set the proxy the connections is refused.proxy_ip = 
    '46.4.96.137' proxy_port = '1080' options.set_preference("network.proxy.type", 1) options.set_preference(
    "network.proxy.http", str(proxy_ip)) options.set_preference("network.proxy.http_port", int(proxy_port)) 
    options.set_preference("network.proxy.ssl", str(proxy_ip)) options.set_preference("network.proxy.ssl_port", 
    str(proxy_port)) options.set_preference("network.proxy.ftp", str(proxy_ip)) options.set_preference(
    "network.proxy.ftp_port", int(proxy_port)) options.set_preference("network.proxy.socks", str(proxy_ip)) 
    options.set_preference("network.proxy.socks_port", int(proxy_port)) options.set_preference(
    "network.http.use-cache", False)"""
    driver = webdriver.Firefox(options=options)

    while start < end:
        d2 = start + datetime.timedelta(2)
        # covert to string. only string values can be inserted.
        from_date = start.strftime("%d%m%Y")
        to_date = d2.strftime("%d%m%Y")
        logger.info(f'\n\n{from_date} to {to_date}\n\n')
        for name in all_districts:
            each_district = dataCollection.EachDistrict(driver=driver,
                                                        from_date=from_date,
                                                        to_date=to_date,
                                                        name=name)
            each_district.open_page(main_url=main_url)
            each_district.enter_date()
            each_district.district_selection()
            each_district.view_record()
            logger.info(f'\n\nName of the District: {name}\n')
            """click search and see if page is loaded, 
            if not, put the district in remaining district csv, 
            and start with new district"""
            if each_district.search():
                pass
            else:
                logger.info(f"Search button didn't work with {name}."
                            f" Going to next district\n", exc_info=True)
                each_district.remaining_district()
                continue
            if each_district.each_page():
                pass
            else:
                continue
        start += datetime.timedelta(3)

    logger.info("all districts in given time frame finished finished. ")


if __name__ == "__main__":
    main()
