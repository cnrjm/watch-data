import sys
from PyQt6.QtWidgets import QApplication
from gui import WatchDatabaseGUI
from database import setup_database
from scraper import scrape_brand

def initial_scrape(conn):
    brands = {
        'Rolex': 'https://www.chrono24.co.uk/rolex/index.htm',
        'Omega': 'https://www.chrono24.co.uk/omega/index.htm',
        'Patek Philippe': 'https://www.chrono24.co.uk/patekphilippe/index.htm',
        'Audemars Piguet': 'https://www.chrono24.co.uk/audemarspiguet/index.htm',
        'Tudor': 'https://www.chrono24.co.uk/tudor/index.htm',
        'IWC': 'https://www.chrono24.co.uk/iwc/index.htm',
        'Richard Mille': 'https://www.chrono24.co.uk/richardmille/index.htm',
        'A Lange & Sohne': 'https://www.chrono24.co.uk/alangesoehne/index.htm'
    }

    for brand, url in brands.items():
        print(f"Scraping {brand}...")
        new_items, updated_items, total_items = scrape_brand(brand, conn, url, max_pages=1)
        print(f"Completed {brand}. Added {new_items} new items, updated {updated_items} items, out of {total_items} total items processed")

def main():
    app = QApplication(sys.argv)
    conn = setup_database()
    window = WatchDatabaseGUI(conn, initial_scrape)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()