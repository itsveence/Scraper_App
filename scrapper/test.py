import time

from browsermobproxy import Server
from undetected_chromedriver import Chrome
from undetected_chromedriver import ChromeOptions

options = ChromeOptions()
server = Server(
    r"C:\Users\dvadi\OneDrive\Upwork\Dima Spektor\Scraper 2\App\browsermob-proxy-2.1.4\bin\browsermob-proxy.bat"
)
server.start()
proxy = server.create_proxy()

# Path to the ModHeader extension (You might need to adjust this based on where it's stored on your system)
extension_path = "../modheader.crx"

# Load ModHeader with the profile
options.add_extension(extension_path)

options.add_argument("--proxy-server={0}".format(proxy.proxy))
options.add_argument('--ignore-certificate-errors')
# Start Chrome with the extension
driver = Chrome(options=options, driver_executable_path="../chromedriver.exe", use_subprocess=True)
driver.implicitly_wait(5)

# Add headers
proxy.headers({"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0", "cookie":"MAID=JLrPLNeni04CVmwCnFnWGQ==; MACHINE_LAST_SEEN=2023-08-31T04%3A00%3A52.532-07%3A00; cf_clearance=dVEuW209A7KMHa4sFw_aIPlntqQIWJQ_.Z9nxT9szzE-1693479654-0-1-245ed535.4d9955fd.651810dc-0.2.1693479654; displayMathJaxFormula=true; SERVER=WZ6myaEXBLGULof+kEOSTA==; JSESSIONID=C6F19BA3C78F8A67101D64213A3F078A; timezone=60; cookiePolicy=accept"})


# Now navigate to your website
driver.get("https://www.tandfonline.com/loi/nvpp20")

time.sleep(60)
