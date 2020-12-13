# Import Splinter and BeautifulSoup and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
import time

#Initialize scrape all fx
def scrape_all():
        
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)

    news_title, news_paragraph = mars_news(browser)

    #Run all scraping functions and store results in a dict
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemisphere_images": hemisphere(browser),
        "last_modified": dt.datetime.now()   
    }
    #Stop webdriver and return data
    browser.quit()
    return data

#Define mars_news function
def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    #try/except blcok for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()
    except AttributeError:
            return None, None
    return news_title, news_p


# ### JPL Space Images Featured Images

#Define featured image function
def featured_image(browser):

    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')[0]
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    #try/except block 
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

# ### Mars Facts

# Define mars_facts fx
def mars_facts():
    #try/excet
    try:
        #use read_html to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    
    #Assign columns and a set index to dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)

    #Convert dataframe into Html format, add bootstrap
    return df.to_html(classes="table table-striped")

# Define hemisphere data
def hemisphere(browser):

    # Use browser to visit the URL 
    hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemi_url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []
    base_url = 'https://astrogeology.usgs.gov'

    # Retrieve the image urls and titles for each hemisphere.
    # Loop through the items previously stored
    hemi_html = browser.html
    hemi_soup = soup(hemi_html, 'html.parser')
    item = hemi_soup.select('div.description')
    try:

        for i in list(range(len(item))):
            title = item[i].find('h3').get_text()
    
            url = item[i].find('a').get('href')
            full_url = f'{base_url}{url}'
    
            browser.visit(full_url)
            html = browser.html
            image = soup(html, 'html.parser')
    
            image_url = image.select_one('ul li a').get('href')
    
            hemisphere_image_urls.append({'img_url':image_url, 'title':title})
            time.sleep(1)
    except AttributeError:
        return None

    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())