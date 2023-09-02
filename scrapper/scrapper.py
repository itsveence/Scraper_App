# Import necessary libraries and modules
import time
import warnings

import pandas as pd
import requests
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from undetected_chromedriver import Chrome
from undetected_chromedriver import ChromeOptions

import scrapper.constants as const

warnings.simplefilter(action='ignore', category=Warning)


class GenderChecker:
    def __init__(self):
        self.cache = {}  # Initialize cache as an empty dictionary

    def get_gender(self, name):
        # Check if the name is in cache
        if name in self.cache:
            return self.cache[name]

        proxy_list = [
            "socks5://67.201.59.70:4145",
            "socks5://184.178.172.11:4145",
            "socks5://104.37.135.145:4145",
            "socks5://184.181.217.206:4145",
            "socks5://98.181.137.83:4145",
            "socks5://192.252.216.81:4145",
            "socks5://184.181.217.194:4145",
            "socks5://98.181.137.80:4145",
            "socks5://72.210.221.223:4145",
            "socks5://184.181.217.201:4145",
        ]

        session = requests.Session()
        session.trust_env = False

        # First, try a direct connection
        try:
            response = session.get(f"https://api.genderize.io?name={name}").json()
            # Store result in cache
            self.cache[name] = response
            return response
        except:
            pass  # If direct connection fails, move on to trying proxies

        # If direct connection failed, try using proxies
        for proxy in proxy_list:
            try:
                response = session.get(
                    f"https://api.genderize.io?name={name}",
                    proxies={"https": proxy},
                    verify=False  # Be cautious about using this
                ).json()
                # Store result in cache
                self.cache[name] = response
                return response
            except:
                # If there's a connection error with a proxy, try the next one
                continue

        # If direct connection and all proxies fail
        raise Exception("Direct connection and all proxy connections failed.")



# Define the Journal class that inherits from Chrome
class Journal(Chrome):
    def __init__(self, teardown=False, headless=True):
        # Constructor docstring
        """
        Constructor for the Journal class. It initializes the base class and sets the implicit wait time.

        :param teardown: Flag to determine whether to shut down the driver after usage.
        """

        # Initialize ChromeOptions and set to headless mode
        self.options = ChromeOptions()
        self.options.headless = headless
        self.checker = GenderChecker()

        # Set the teardown flag
        self.teardown = teardown
        # Initialize the super class (Chrome) with options
        super(Journal, self).__init__(
            options=self.options,
            use_subprocess=True,
            driver_executable_path="chromedriver.exe",
        )
        # Set an implicit wait time for 5 seconds
        self.implicitly_wait(1)

    def login(self):
        # Open the login page using the constant path.
        self.open_link(const.LOGIN_PATH)

        # Accept cookies if prompted.
        self.accept_cookies()

        self.find_element(By.CSS_SELECTOR, "div[class='samLinks']").click()

        # Type in the name of the institution in the input box.
        self.find_element(By.CSS_SELECTOR, "input[class='ms-inv']").send_keys(
            "Bar-Ilan University"
        )

        # Create an action chain to simulate keypress.
        action = ActionChains(self)

        # Simulate pressing the 'Enter' key.
        action.send_keys(Keys.ENTER)

        # Click on the first autocomplete result for the institution.
        self.find_element(
            By.CSS_SELECTOR, "div[class='ms-res-item ms-res-item-active']"
        ).click()

        # Click on another element - possibly a confirmation or next step button.
        self.find_element(By.CSS_SELECTOR, "div[class='ORRU02D-k-a']").click()

        time.sleep(2)

        self.find_element(By.CSS_SELECTOR, "#i0116").send_keys(const.EMAIL + Keys.ENTER)

        try:
            self.find_element(
                By.CSS_SELECTOR,
                "#credentialList > div > div > div > div.table-cell.text-left.content",
            ).click()
        except:
            pass

        time.sleep(2)

        self.find_element(By.CSS_SELECTOR, "#i0118").send_keys(
            const.PASSWORD + Keys.ENTER
        )

        self.find_element(
            By.CSS_SELECTOR,
            "#idDiv_SAOTCS_Proofs > div:nth-child(1) > div > div > div.table-cell.text-left.content",
        ).click()

        # Print a message to console notifying about a 60-second waiting period.
        print("Waiting 60 seconds for code verification")

        # Pause the execution for 60 seconds to allow the login process to complete.
        time.sleep(60)

    def land_first_page(self):
        """Navigates the driver to the base URL specified in constants."""
        self.get(const.BASE_URL)

    def accept_cookies(self):
        """Tries to locate and click the "Accept Cookies" button if present."""
        try:
            accept_cookies_button = self.find_element(
                By.CSS_SELECTOR, "button[id='cookie-accept']"
            )
            accept_cookies_button.click()
        except:
            print("No accept cookies button")

    def get_all_issues(self):
        """Navigates to the 'All Issues' section of the journal."""
        all_volumes = self.find_elements(By.CSS_SELECTOR, "li[class='vol_li']")

        issue_dict = {}

        for i in reversed(range(len(all_volumes))):
            volume = self.find_elements(By.CSS_SELECTOR, "li[class='vol_li']")[i]
            href2 = volume.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            year = (
                volume.find_element(By.CSS_SELECTOR, "button[class='volume_link']")
                .text.strip()
                .split()[-1]
            )

            self.get(href2)
            issue_links = [
                issue.get_attribute("href")
                for issue in self.find_elements(
                    By.CSS_SELECTOR, "a[class='issue-link']"
                )
            ]
            issue_dict[year] = reversed(issue_links)

        # print(issue_dict)
        return issue_dict

    def get_all_details_in_articles(self, issues: dict):
        years = list(issues.keys())
        details_dict = {}

        for i in range(len(years)):
            # if years[i] == "2022":
            issue_links = issues[years[i]]
            article_dict = {}
            for link in issue_links:
                self.get(link)
                articles = self.find_elements(
                    By.XPATH,
                    "//div[@class='articleEntry' and .//span[@class='article-type' and text()='Article']]",
                )
                article_links = [
                    article.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    for article in articles
                ]
                # print(article_links)

                for al in article_links:
                    self.get(al)
                    details = self.get_details()
                    article_dict[details["Paper title"]] = details
                break
            details_dict[years[i]] = article_dict

        # print(details_dict)
        return details_dict

    def open_link(self, url):
        """Navigates the browser to the provided URL."""
        self.get(url)

    def get_details(self):
        # Initializing an empty dictionary to store the details
        details = {}

        # Extracting the name/title of the article
        article_name = self.find_element(
            By.CSS_SELECTOR, "span[class='NLM_article-title hlFld-title']"
        ).text

        # Extracting the DOI (Digital Object Identifier) of the article
        doi = self.find_element(By.CSS_SELECTOR, "li[class='dx-doi'] a").get_attribute(
            "href"
        )



        # Extracting the publication date and stripping the prefix
        publish_date = (
            self.find_element(By.CSS_SELECTOR, "div[class='itemPageRangeHistory']")
            .text.strip()
            .split("Published online: ")[1]
        )

        # Extracting all authors
        authors = self.find_element(
            By.CSS_SELECTOR, "span[class='NLM_contrib-group']"
        ).find_elements(By.XPATH, "//span[contains(@class, 'contribDegrees')]")

        # Calculating the total number of authors
        number_of_authors = len(authors)

        # Extracting the name of the first author
        first_author_name = authors[0].find_element(
            By.CSS_SELECTOR, "a[class='author']"
        )
        first_author_name = self.execute_script(
            "return arguments[0].textContent", first_author_name
        ).strip()

        # Predicting the gender of the first author using their name
        first_author_gender = self.checker.get_gender(first_author_name.split()[0])

        # Extracting all images present in the article
        images = self.find_elements(By.CSS_SELECTOR, "div[class='figureThumbnailContainer']")

        # Taking the first half of all the images
        img_half_length = int(len(images))
        # images = images[:img_half_length]

        # Extracting all tables present in the article
        tables = self.find_elements(By.CSS_SELECTOR, "div[class='tableView']")

        # Taking the first half of all the tables
        tab_half_length = int(len(tables))
        # tables = tables[:tab_half_length]

        # Populating the 'details' dictionary
        details["Paper title"] = article_name
        details["Paper DOI"] = doi
        details["Publication Date"] = publish_date
        details["Number of authors"] = number_of_authors
        details["Name of the first author"] = first_author_name
        details["Gender of the first author"] = first_author_gender["gender"]
        details["First author gender probability"] = first_author_gender["probability"]
        # Extracting affiliation of the first author using JavaScript execution
        try:
            first_affiliation = authors[0].find_element(
                By.CSS_SELECTOR, "span[class='overlay']"
            )
            first_affiliation = self.execute_script(
                "return arguments[0].textContent", first_affiliation
            ).strip()
            details["Affiliation of the first author"] = first_affiliation
        except:
            pass

        # Checking if there's more than one author and then extracting details of the last author
        if number_of_authors > 1:
            last_author_name = authors[-1].find_element(
                By.CSS_SELECTOR, "a[class='author']"
            )
            last_author_name = self.execute_script(
                "return arguments[0].textContent", last_author_name
            ).strip()
            last_author_gender = self.checker.get_gender(last_author_name.split()[0])
            details["Name of the last author"] = last_author_name
            details["Gender of the last author"] = last_author_gender["gender"]
            details["Last author gender probability"] = last_author_gender[
                "probability"
            ]

            # Extracting affiliation of the last author using JavaScript execution
            try:
                last_affiliation = authors[-1].find_element(
                    By.CSS_SELECTOR, "span[class='overlay']"
                )
                last_affiliation = self.execute_script(
                    "return arguments[0].textContent", last_affiliation
                ).strip()
                details["Affiliation of the last author"] = last_affiliation
            except:
                pass

        # Storing the number of images
        details["Number of Images"] = len(images)

        # Extracting caption and link for each image in the first half
        for i in range(img_half_length):
            try:
                details[f"Image {i + 1} caption"] = (
                    images[i].find_element(By.CSS_SELECTOR, "p[class='captionText']").text
                )
            except:
                details[f"Image {i + 1} caption"] = None
            details[f"Image {i + 1} Link"] = (
                images[i].find_element(By.CSS_SELECTOR, "img").get_attribute("src")
            )


        # Storing the number of tables
        details["Number of Tables"] = len(tables)

        # Extracting caption for each table in the first half
        for i in range(tab_half_length):
            try:
                details[f"Table {i + 1} caption"] = (
                    tables[i].find_element(By.CSS_SELECTOR, "p[class='captionText']").text
                )
            except:
                # print(doi)
                try:
                    details[f"Table {i + 1} caption"] = (
                        tables[i].find_element(By.CSS_SELECTOR, "b").text
                    )
                except:
                    try:
                        details[f"Table {i + 1} caption"] = (
                            tables[i].find_element(By.CSS_SELECTOR, "div[class='tableCaption']").text
                        )
                    except:
                        details[f"Table {i + 1} caption"] = None

        # Printing the 'details' dictionary
        # print(details)

        # Returning the 'details' dictionary
        return details

    def create_dataframe(self):
        # Define the column names in a list
        columns = [
            "Paper title",
            "Paper DOI",
            "Publication Date",
            "Number of authors",
            "Name of the first author",
            "Name of the last author",
            "Gender of the first author",
            "Gender of the last author",
            "First author gender probability",
            "Last author gender probability",
            "Affiliation of the first author",
            "Affiliation of the last author",
            "Number of Images",
        ]

        # Add image caption and link columns
        for i in range(1, 11):
            columns.append(f"Image {i} caption")

        for i in range(1, 11):
            columns.append(f"Image {i} Link")

        columns.append("Number of Tables")

        # Add table caption columns
        for i in range(1, 11):
            columns.append(f"Table {i} caption")

        # Create an empty DataFrame with the columns
        df = pd.DataFrame(columns=columns)

        return df

    def populate_df(self, df: pd.DataFrame, data: dict) -> pd.DataFrame:
        """
        Populates the given DataFrame with data from the provided dictionary.

        :param df: The pandas DataFrame to which data needs to be appended.
        :param data: Dictionary containing the data to be appended.

        :return: The updated DataFrame with appended data.
        """

        # Using the 'loc' accessor to add a new row to the end of the DataFrame
        df.loc[len(df)] = data

        return df
