import requests
import xml.etree.ElementTree as ET
import json

author_zero = "11/2374"

data = {
    "UNIVERSITY": [],
    "AFFILIATION": [],
    "RESEARCHER": [],
    "PAPER": [],
    "ARTICLE": [],
    "CONTRIBUTIONS": [],
    "TYPE_PUBLICATION": [
        {"id": 1, "nom": "Conference And Workshop Papers"},
        {"id": 2, "nom": "Journal Articles"},
        {"id": 3, "nom": "Data and Artifacts"},
        {"id": 4, "nom": "Informal and Other Publications"}
    ]
}

def get_data_from_pid(pid):
    url = f"https://dblp.org/pid/{pid}.xml"
    response = requests.get(url)
    tree = ET.ElementTree(ET.fromstring(response.content))
    root = tree.getroot()

    # Extract basic author info
    author_name = root.attrib.get('name', 'Unknown Author')
    person = root.find("person")
    if person is None:
        print("No <person> element found.")
        exit(1)

    # Extract affiliations
    affiliations = []
    for note in person.findall("note[@type='affiliation']"):
        affiliations.append(note.text)
    unique_affiliations = list(dict.fromkeys(affiliations))

    # Check if affiliated with IRISA
    affiliated_with_irisa = any("IRISA" in (aff or "").upper() for aff in unique_affiliations)
    if not affiliated_with_irisa:
        print(f"Researcher {author_name} not affiliated with IRISA. Skipping.")
        return (pid, author_name, unique_affiliations, -1, [], {}, [], [], [], [])

    universities = []
    univ_map = {}
    for i, univ_name in enumerate(unique_affiliations, start=1):
        universities.append({"ID": i, "NOM": univ_name, "Coord": ""})
        univ_map[univ_name] = i

    # Extract URLs
    urls = [url_elem.text for url_elem in person.findall("url")]

    # Gather papers/articles info
    papers = []
    articles = []
    contributions = []
    article_id_counter = 1

    # For each <r>, check if it's an inproceedings or article
    for record in root.findall("r"):
        inproc = record.find("inproceedings")
        if inproc is not None:
            key = inproc.attrib.get("key", "")
            doi_full = (inproc.find("ee").text or "") if inproc.find("ee") is not None else ""
            doi = doi_full.replace("https://doi.org/", "")
            title = inproc.findtext("title", "")
            year = inproc.findtext("year", "")
            pages = inproc.findtext("pages", "")
            venue = inproc.findtext("booktitle", "")
            papers.append({
                "doi": doi,
                "TYPE_PUBLICATION.id": 1,  # Conference / Workshop
                "titre": title,
                "venue": venue,
                "year": year,
                "pages": pages,
                "ee": doi_full,
                "url_dblp": f"https://dblp.org/rec/{key}"
            })
            author_elems = inproc.findall("author")
            for idx, auth in enumerate(author_elems, start=1):
                pid_attr = auth.attrib.get("pid", "")
                contributions.append({
                    "RESEARCHER.PID": pid_attr,
                    "ARTICLE.doi": doi,
                    "position": idx
                })

        art = record.find("article")
        if art is not None:
            key = art.attrib.get("key", "")
            doi_full = (art.find("ee").text or "") if art.find("ee") is not None else ""
            doi = doi_full.replace("https://doi.org/", "")
            title = art.findtext("title", "")
            year = art.findtext("year", "")
            pages = art.findtext("pages", "")
            venue = art.findtext("journal", "")  # Usually <journal> for articles
            volume = art.findtext("volume", "")
            number = art.findtext("number", "")
            papers.append({
                "doi": doi,
                "TYPE_PUBLICATION.id": 2,  # Journal Articles
                "titre": title,
                "venue": venue,
                "year": year,
                "pages": pages,
                "ee": doi_full,
                "url_dblp": f"https://dblp.org/rec/{key}"
            })
            articles.append({
                "id": article_id_counter,
                "PAPER.id": doi,
                "volume": volume,
                "number": number
            })
            author_elems = art.findall("author")
            for idx, auth in enumerate(author_elems, start=1):
                pid_attr = auth.attrib.get("pid", "")
                contributions.append({
                    "RESEARCHER.PID": pid_attr,
                    "ARTICLE.doi": doi,
                    "position": idx
                })
            article_id_counter += 1

    return (
        pid,
        author_name,
        unique_affiliations,
        1,
        universities,
        univ_map,
        urls,
        papers,
        articles,
        contributions
    )

def save_author_data(author_data):
    (
        pid,
        author_name,
        unique_affiliations,
        scraped,
        universities,
        univ_map,
        urls,
        papers,
        articles,
        contributions
    ) = author_data

    data["UNIVERSITY"].extend(universities)
    data["AFFILIATION"].extend([
        {
            "UNIVERSITY.id": univ_map[affiliation],
            "RESEARCHER.PID": pid
        }
        for affiliation in unique_affiliations
    ])
    data["RESEARCHER"].append({
        "PID": pid,
        "nom": author_name,
        "scraped": scraped
    })
    data["PAPER"].extend(papers)
    data["ARTICLE"].extend(articles)
    data["CONTRIBUTIONS"].extend(contributions)

save_author_data(get_data_from_pid(author_zero))

# TODO: faire une function qui check chaque contribution, regarde si le PID est déjà dans RESEARCHER, si non, le rajoute et vérifie si le chercheur est affilié à IRISA

# Build a JSON structure based on the comment:
# UNIVERSITY :
#   - id -- auto-increment
#   - NOM -- note type="affiliation"
#   - Coord -- LATER
#
# AFFILIATION :
#   - UNIVERSITY.id
#   - RESEARCHER.PID
#
# RESEARCHER : 
#   - PID -- dblp PID
#   - nom -- author last name
#   - prenom -- author name
#   - ORCID -- LATER
#   - scraped / int (-2: vérifier si à faire ou non; -1: à ne pas faire; 0: à faire, 1: fait)
#
# PAPER :
#   - doi ID -- <ee> last part
#   - TYPE_PUBLICATION.id -- inproceedings || article
#   - titre -- <title>
#   - venue (acronym DBLP) <booktitle> NULLABLE
#   - year -- <year>
#   - pages -- <pages>
#   - ee -- <ee>
#   - url_dblp -- https://dblp.org/rec/<key>

# ARTICLE :
#   - id
#   - PAPER.id
#   - volume -- <volume>
#   - number -- <number>
#
# CONTRIBUTIONS :
#   - RESEARCHER.PID -- <author>
#   - ARTICLE.doi -- <article>
#   - position -- <author> position in the list
#
# TYPE_PUBLICATION : 
# - id -- auto-increment
# - nom -- Conference And Workshop Papers || Journal Articles || Data and Artifacts || Informal and Other Publications

# TODO: Implement the JSON structure based on the comment above
#       and store the data in a JSON file
# TODO: Add data recursively from the author's co-authors