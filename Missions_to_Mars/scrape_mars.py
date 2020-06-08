# Dependencies
from bs4 import BeautifulSoup
import requests
from splinter import Browser
import pandas as pd
import time
import pandas as pd

def init_browser():
    # activate splinter; NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

    # Window Users- comment out the 2 lines above, and uncomment the 2 lines below
    # executable_path = {'executable_path': 'chromedriver.exe'}
    # browser = Browser('chrome', **executable_path, headless=False)


def scrape():
    browser = init_browser()

    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'
    # connects browser to desired webpage
    browser.visit(url)
    time.sleep(5)
    html = browser.html
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(html, 'html.parser')
    # Scrape the NASA Mars News Site and collect the latest News Title and Paragraph Text
    news_title = soup.find_all('div', class_="content_title")[1].text
    news_title
    news_p = soup.find_all('div', class_='rollover_description_inner')[6].text.strip()
    news_p

    # next desired url
    base_url = 'https://www.jpl.nasa.gov'
    url2 = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url2)
    time.sleep(1)
    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    # finds the url of the featured mars image
    a_tag = soup.footer.find('a')
    href = a_tag['data-fancybox-href']
    featured_image_url = base_url + href

    # next desired url
    url3 = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url3)
    time.sleep(30)
    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    # finds the text of the latest tweet on mars twitter
    tweet = soup.find_all('article')
    mars_weather = tweet[0].find_all('span')[4].text
    
    # next desired url
    url4 = 'https://space-facts.com/mars/'
    # turns all tables on web page into list of tables
    tables = pd.read_html(url4)
    # takes just the first table
    df = tables[0]
    # converts number headers into strings
    df.columns = df.columns.map(str)
    # sets first column as the index
    df = df.set_index("0")
    # changes column name
    df = df.rename(columns={"1":"Value"})
    # changes index name
    df.index.rename('Description', inplace=True)
    # converts dataframe to html
    mars_data_html_table = df.to_html()

    # next desired url
    url_hemispheres = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url_hemispheres)
    time.sleep(1)
    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    hemisphere_image_urls = []
    base_url2 = "https://astrogeology.usgs.gov"
    # creates list of each hemisphere's div
    all_hem_names = soup.find_all('div', class_="description")
    list_hem = []
    # for each hemisphere's div, find the name of the link
    for hem in all_hem_names:
        list_hem.append(hem.h3.text)

    def hem_imgs_func():
        # HTML object
        html = browser.html
        # Parse HTML with Beautiful Soup
        soup = BeautifulSoup(html, 'html.parser')
        # finds the img url of the image
        section = soup.find('div', id="wide-image")
        src = section.find('img', class_="wide-image")['src']
        img_var = base_url2 + src
        # finds the name of the hemisphere
        section = soup.find('section', class_="metadata")
        name = section.h2.text
        # gets rid of the word 'enhanced'
        name = name.rsplit(' ', 1)[0]
        # appends dictionary to list
        hemisphere_image_urls.append({"title": name, "image_url": img_var})
        return hemisphere_image_urls

    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    # for each link in each hemisphere's div
    for hem in list_hem:
        # click on the link
        button = browser.links.find_by_partial_text(hem)
        button.click()
        # calls the function above to find name and url
        hem_imgs_func()
        # go back to main page
        browser.back()

    # Store all data in a dictionary
    mars_data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image_url,
        "mars_weather": mars_weather,
        "mars_data_table": mars_data_html_table,
        "hemisphere_images": hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data