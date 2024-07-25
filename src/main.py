import argparse
from database import setup_database, query_watches, clear_database, print_all_watches
from scraper import scrape_brand, test_first_watch

def parse_arguments():
    parser = argparse.ArgumentParser(description="Watch database operations")
    parser.add_argument('-test', action='store_true', help="Run test on first watch")
    parser.add_argument('-clear', action='store_true', help="Clear the database")
    parser.add_argument('-initial_scrape', action='store_true', help="Perform initial scrape of multiple brands")
    parser.add_argument('-brand', help="Brand of the watch for querying")
    parser.add_argument('-model', help="Model of the watch for querying")
    parser.add_argument('-condition', help="Condition of the watch for querying")
    parser.add_argument('-ref', help="Reference number of the watch for querying")
    parser.add_argument('-year', help="Production year of the watch for querying")
    parser.add_argument('-print_all', action='store_true', help="Print all watches in the database")
    return parser.parse_args()

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
    args = parse_arguments()
    
    if args.test:
        url = "https://www.chrono24.co.uk/watches/used-watches--64.htm?keyword=used-watches&keywordId=64&showpage=&sortorder=5"
        test_first_watch(url)
    elif args.clear:
        conn = setup_database()
        clear_database(conn)
        conn.close()
    elif args.initial_scrape:
        conn = setup_database()
        initial_scrape(conn)
        conn.close()
    elif args.print_all:
        conn = setup_database()
        print_all_watches(conn)
        conn.close()
    elif any([args.brand, args.model, args.condition, args.ref, args.year]):
        conn = setup_database()
        results = query_watches(conn, brand=args.brand, model=args.model, condition=args.condition, ref=args.ref, year=args.year)
        print(f"\nWatches matching the criteria:")
        if not results:
            print("No matches found.")
        else:
            for watch in results:
                print(f"ID: {watch[0]}, Brand: {watch[1]}, Model: {watch[2]}, Ref: {watch[3]}, "
                      f"Price: {watch[4]} {watch[5]}, Condition: {watch[6]}, Year: {watch[7]}")
        conn.close()
    else:
        print("No action specified. Use -h for help.")

if __name__ == "__main__":
    main()