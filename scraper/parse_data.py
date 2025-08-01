from bs4 import BeautifulSoup
from pydantic import ValidationError
from models.offer import Offer, Location, Category
from scraper.time_formatter import time_to_date

def scrape_title(offer: BeautifulSoup) -> str:
    title_tag = offer.find("h2", class_="text-module-begin")
    if title_tag:
        link_tag = title_tag.find("a")
        return link_tag.text.strip() if link_tag else title_tag.text.strip()
    return ""

def scrape_description(offer: BeautifulSoup) -> str:
    description_tag = offer.find("p", class_="aditem-main--middle--description")
    return description_tag.text.strip() if description_tag else ""

def scrape_address(offer: BeautifulSoup) -> str:
    address_tag = offer.find("div", class_="aditem-main--top--left")
    return address_tag.text.strip() if address_tag else ""

def scrape_time(offer: BeautifulSoup) -> str:
    time_tag = offer.find("div", class_="aditem-main--top--right")
    time_str = time_tag.text.strip() if time_tag else ""
    return time_to_date(time_str) if time_str else ""

def scrape_photos(offer: BeautifulSoup) -> list[str]:
    photos = []
    img_tags = offer.find_all("img")
    for img in img_tags:
        src = img.get("src") or img.get("data-src")
        if src and "kleinanzeigen.de" in src:
            photos.append(src)
    return photos

def scrape_link(offer: BeautifulSoup) -> str:
    link_tag = offer.find("a", href=True)
    if link_tag:
        href = link_tag.get("href")
        if href.startswith("/"):
            return f"https://www.kleinanzeigen.de{href}"
        return href
    return ""

def scrape_id(offer: BeautifulSoup) -> str:
    id_tag = offer.get("data-adid")
    return str(id_tag) if id_tag else ""

def scrape_price(offer: BeautifulSoup) -> str:
    price_tag = offer.find("p", class_="aditem-main--middle--price-shipping--price")
    return price_tag.text.strip() if price_tag else ""

def parse_verschenken_offer(offer: BeautifulSoup, location: Location, category: Category) -> Offer | None:
    """Parse a 'Zu verschenken' offer from HTML."""
    try:
        title = scrape_title(offer)
        description = scrape_description(offer)
        address = scrape_address(offer)
        offer_date = scrape_time(offer)
        photos = scrape_photos(offer)
        link = scrape_link(offer)
        offer_id = scrape_id(offer)
        price = scrape_price(offer)

        if "Zu verschenken" in price and title and offer_id:
            return Offer(
                _id=offer_id,
                title=title,
                description=description,
                address=address,
                link=link,
                offer_date=offer_date,
                photos=photos,
                location=location,
                category=category,
                price=0.0  # Free items
            )
    except (ValidationError, ValueError) as e:
        print(f"Error creating offer: {e}")
    
    return None

def parse_priced_offer(offer: BeautifulSoup, location: Location, category: Category, price_value: float) -> Offer | None:
    """Parse a priced offer from HTML."""
    try:
        title = scrape_title(offer)
        description = scrape_description(offer)
        address = scrape_address(offer)
        offer_date = scrape_time(offer)
        photos = scrape_photos(offer)
        link = scrape_link(offer)
        offer_id = scrape_id(offer)

        if title and offer_id:
            return Offer(
                _id=offer_id,
                title=title,
                description=description,
                address=address,
                link=link,
                offer_date=offer_date,
                photos=photos,
                location=location,
                category=category,
                price=price_value  # Actual price
            )
    except (ValidationError, ValueError) as e:
        print(f"Error creating priced offer: {e}")
    
    return None
