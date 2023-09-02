# Import the necessary constants and classes
import os
import re

from scrapper import file_handling
from scrapper.constants import OUT_PATH, IMAGE_PATH
from scrapper.scrapper import Journal

# Start the web scraper for the journal
bot = Journal(headless=False)
# Create an empty dataframe to store the scraped data
dataframe = bot.create_dataframe()

# Initiate logging process
bot.login()

# Navigate to the initial page of the journal
bot.land_first_page()

# Accept any cookies if presented on the website
bot.accept_cookies()

# Navigate to the section that displays all issues of the journal
issues = bot.get_all_issues()

details = bot.get_all_details_in_articles(issues)

for year in list(details.keys()):
    for article in list(details[year].keys()):
        detail = details[year][article]
        # Assuming details is your dictionary
        matching_keys = [i for i in detail.keys() if re.match(r'^Image .+ Link$', i)]

        # Now extract the values for these matching keys
        image_links = [detail[key] for key in matching_keys]
        # Checks if list contains image
        if image_links:
            title = detail['Paper title']
            invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
            for char in invalid_chars:
                title = title.replace(char, '_')

            # Get the path to store image
            article_dir = os.path.join(IMAGE_PATH, year, title)
            # Create image folder
            file_handling.create_dir(article_dir)
            # print(detail["Paper DOI"])
            for image in image_links:

                file_handling.download_file(image, article_dir)
        # Populate the dataframe with the article details
        new_dataframe = bot.populate_df(dataframe, detail)
        # Update the original dataframe with the new data
        dataframe = new_dataframe

# Fill any NaN values in the dataframe with the text "Not Available"
dataframe = dataframe.fillna("Not Available")

# Save the populated dataframe to an Excel file
dataframe.to_excel(OUT_PATH, index=False)

# Close window
bot.close()

