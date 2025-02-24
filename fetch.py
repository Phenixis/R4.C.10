import requests
import xml.etree.ElementTree as ET
import json

def get_data_from_pid(pid):
    # Author's DBLP PID
    url = f"https://dblp.org/pid/{pid}.xml"

    # Fetch the XML data from DBLP
    response = requests.get(url)
    tree = ET.ElementTree(ET.fromstring(response.content))
    root = tree.getroot()

    # Extract author's name from the 'dblpperson' tag (top-level)
    author_name = root.attrib.get('name', 'Unknown Author')

    # Find the first <person> tag and extract information only within it
    person = root.find("person")
    if person is None:
        print("No <person> element found.")
        exit(1)

    # Extract affiliation information (if available) within <person>
    affiliations = []
    for note in person.findall("note[@type='affiliation']"):
        affiliations.append(note.text)

    # Create unique university entries with auto-increment IDs
    unique_affiliations = list(dict.fromkeys(affiliations))
    universities = []
    univ_map = {}
    for i, univ_name in enumerate(unique_affiliations, start=1):
        universities.append({"ID": i, "NOM": univ_name, "Coord": ""})
        univ_map[univ_name] = i

    # Extract URLs (including homepage, ORCID, etc.) within <person>
    urls = [url_elem.text for url_elem in person.findall("url")]

    # Display the information from <person>
    print(f"Author Name: {author_name}")
    print(f"Affiliations: {'; '.join(affiliations)}")
    print(f"URLs: {'; '.join(urls)}")

    return author_name, unique_affiliations, universities, univ_map, urls

author_zero = "11/2374"

author_zero_data = get_data_from_pid(author_zero)

# Build a JSON structure based on the comment:
# UNIVERSITY :
#   - ID / serial
#   - NOM
#   - Coord
#
# AFFILIATION :
#   - UNIVERSITY.ID
#   - RESEARCHER.PID
#
# RESEARCHER : 
#   - PID
#   - nom
#   - prenom
#   - scraped / int (-1: à ne pas faire; 0: à faire, 1: fait)
#
# ARTICLE :
#   - ID
#   - titre
#
# CONTRIBUTIONS :
#   - RESEARCHER.PID
#   - ARTICLE.ID
#   - position

# TODO: Implement the JSON structure based on the comment above
#       and store the data in a JSON file
# TODO: Add data recursively from the author's co-authors