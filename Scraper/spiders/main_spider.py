import scrapy
from Scraper.items import ScraperItem
from bs4 import BeautifulSoup
from scrapy import Selector

class MainSpider(scrapy.Spider):
    name = "main"

    def start_requests(self):
        urls = [
            'https://www.amazon.com/LEGO-Classic-Creative-Building-Learning/dp/B00NHQFA5E/ref=zg_bs_166099011_42?_encoding=UTF8&psc=1&refRID=01KPNSV7FKZDKPX5XMQF#customerReviews',
            'https://www.amazon.com/dp/B00L5FT81Q/ref=sspa_dk_detail_2?psc=1&pd_rd_i=B00L5FT81Q&pf_rd_m=ATVPDKIKX0DER&pf_rd_p=f52e26da-1287-4616-824b-efc564ff75a4&pf_rd_r=R8WRF2X9CBYZM16M2KWE&pd_rd_wg=raa9P&pf_rd_s=desktop-dp-sims&pf_rd_t=40701&pd_rd_w=g7JAB&pf_rd_i=desktop-dp-sims&pd_rd_r=f9099bb2-c154-11e8-ae31-29c6b27af72b'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Amazon HTML syntax is FKING SHIT. So we need to fix them
        # https://github.com/scrapy/scrapy/issues/1968
        soup = BeautifulSoup(response.body, "lxml")
        response = Selector(text=soup.prettify())

        reviews = []

        recentReviews = response.css("#most-recent-reviews-content").xpath("//div[@data-hook='recent-review']")
        for recentReview in recentReviews:
            reviewer = recentReview.css(".a-profile-name::text").extract_first().strip()
            reviewTitle = recentReview.css("span[data-hook='review-title-recent']::text").extract_first().strip()
            reviewBody = recentReview.css("span[data-hook='review-body-recent']::text").extract_first().strip()

            reviews.append({'reviewer':reviewer, 'title':reviewTitle, 'content':reviewBody})

        item = ScraperItem()
        item['productTitle']  = response.css("#productTitle::text").extract_first(default='not-found').strip()
        item['rating']        = response.css("#acrPopover").xpath('@title').extract_first(default='not-found')
        item['totalReview']   = response.css(".totalReviewCount::text").extract_first().strip()
        item['price']         = response.css("#priceblock_ourprice::text").extract_first()
        item['recentReviews'] = reviews

        print('================= Done extracting data =====================')
        yield item