import requests
from bs4 import BeautifulSoup
import csv
import time


def extract_scientist_links():
    """Extracts links of scientists from the Wikipedia page.

    Retrieves the 'List of Computer Scientists' Wikipedia page, parses its HTML content, 
    locates links for individual scientists, and returns a list of these URLs.

    Returns:
        A list of Wikipedia URLs for individual computer scientists.
    """

    response = requests.get("https://en.wikipedia.org/wiki/List_of_computer_scientists")
    soup = BeautifulSoup(response.content, "html.parser")

    # Select <li> elements from the "mw-parser-output ul" section
    scientist_elements = soup.select(".mw-parser-output ul li")

    # Extract and store the first 'a' tag hyperlink ('href') in each <li> 
    scientist_urls = []
    for element in scientist_elements:
        link = element.find("a", href=True)
        if link and "title" in link.attrs:
            scientist_urls.append("https://en.wikipedia.org" + link["href"])

    return scientist_urls[:]  # Could limit the list for faster testing 


def extract_education_text(soup):
    """Extracts education-related text from a Wikipedia page.

    Searches for sections with potential heading titles (e.g., "Education"), 
    and extracts text content from subsequent paragraphs until the next major heading.

    Args:
        soup: A BeautifulSoup object representing the parsed Wikipedia page.

    Returns: 
        A string containing education-related text.
    """

    potential_titles = [
        "education",
        "early life and education",
        "biography",
        "professional biography",
    ]
    education_text = ""

    for title in potential_titles:
        # Find <span> elements with specified heading texts
        education_headings = soup.find_all(
            "span", {"class": "mw-headline", "id": lambda x: x and title in x.lower()}
        )
        for heading in education_headings:
            # Iterate through all elements (p and h2) starting from the located heading
            next_element = heading.find_next(["p", "h2"])
            while next_element and next_element.name == "p":
                education_text += next_element.get_text() + "\n"  # Concatenate paragraph text
                next_element = next_element.find_next(["p", "h2"])

    return education_text.strip()


def extract_awards(soup):
    """Extracts award information from a Wikipedia page's infobox.

    Searches for the "Awards" table header (<th>) in the infobox and counts the 
    number of hyperlinks in the corresponding table cell (<td>).

    Args:
        soup: A BeautifulSoup object representing the parsed Wikipedia page.

    Returns:
        An integer representing the number of awards found.
    """

    awards_element = soup.find("th", string="Awards")
    if awards_element:
        awards_td = awards_element.find_next_sibling("td")
        if awards_td:
            awards_count = len(awards_td.find_all("a"))  # Counts links within the <td>
            return awards_count
    return 0


def limit_size(text, max_words):
    """Limits the number of words in a text excerpt.

    Splits the text into words, takes the specified maximum number of words, joins
    them back into a string, and performs text encoding adjustments to handle special
    characters.

    Args:
        text: The text to be limited.
        max_words: The maximum number of words to include.

    Returns:
        A string containing the limited text with encoding adjustments.
    """

    words = text.split()[:max_words]
    # Encode to 'utf-8' and replace characters that cannot be encoded with 'ignore'
    limited_text = " ".join(words).encode("utf-8", "ignore").decode("utf-8")
    return limited_text


def search_dblp_records(full_name):
    """Searches for DBLP records and extracts a count of entries

    Performs a search on DBLP using the provided full name.  Then it  counts
    specific publication related classes that represent types of DBLP entries. 

    Args:
        full_name: The scientist's full name.

    Returns:
        A string containing either a numeric count of found DBLP records or 'N/A'.
    """

    dblp_url = f"https://dblp.org/search?q={full_name.replace(' ', '+')}"
    dblp_response = requests.get(dblp_url)
    dblp_soup = BeautifulSoup(dblp_response.content, "html.parser")

    first_link = dblp_soup.find("a", itemprop="url")
    if first_link:
        first_link_url = first_link["href"]
        first_link_response = requests.get(first_link_url)
        first_link_soup = BeautifulSoup(first_link_response.content, "html.parser")

        entry_classes = [
            "entry article toc",
            "entry inproceedings toc",
            "entry incollection toc",
            "entry informal toc",
            "entry editor toc",
            "entry reference toc",
            "entry book toc",
            "entry data toc",
        ]
        entry_count = sum(
            len(first_link_soup.find_all("li", class_=entry_class))
            for entry_class in entry_classes
        )
        print(f"Found {entry_count} DBLP entries for {full_name}")
        return entry_count

    return "N/A"

def parse_scientist_page(url):
    """Parses a Wikipedia page for a computer scientist.

    Retrieves the HTML content of the provided URL, extracts the scientist's full name,
    surname, awards count, education text, and DBLP information. 

    Args:

    url: The URL of the Wikipedia page for the computer scientist.

    Returns:
    A tuple containing the scientist's surname, awards count, education text, and DBLP information.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract the full text from the "title" tag
    full_text = soup.find("title").text
    # Extract the part before the first hyphen
    name = full_text.split(" - ")[0]
    # Remove the part inside parentheses
    name = name.split(" (")[0]
    # Extract Awards information and count
    awards_count = extract_awards(soup)

    # Extract the surname (last name) from the full name
    surname = name.split()[-1]

    # Extract Education information
    education_text = extract_education_text(soup)

    # Replace newline characters with a space
    education_text = education_text.replace('\n', ' ')

    # Limit the size of the education text to a maximum of 90 words
    education_text = limit_size(education_text, 90)

    # Search DBLP records and extract information
    dblp_info = search_dblp_records(name)

    return surname, awards_count, education_text, dblp_info

try:

    
    # Assuming scientist_urls is a list
    all_scientist_urls = extract_scientist_links()

    # Exclude indices 441 and 442
    excluded_indices = [441, 442]
    filtered_scientist_urls = [url for i, url in enumerate(all_scientist_urls) if i not in excluded_indices]

    # Use the filtered_scientist_urls list for further processing
    data = []

    for url in filtered_scientist_urls:
        try:
            surname, awards_count, education_text, dblp_info = parse_scientist_page(url)
            data.append({"Surname": surname, "Awards": awards_count, "Education": education_text, "DBLP Info": dblp_info})
            
            # Save the data to a CSV file
            with open("computer_scientists_data.csv", "w", newline='', encoding='utf-8') as csvfile:
                fieldnames = ["Surname", "Awards", "Education", "DBLP Info"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for scientist_data in data:
                    writer.writerow(scientist_data)
        except UnicodeEncodeError as e:
            print(f"Error processing {url}: {e}")
            continue
except Exception as e:
    print("Error:", e)
