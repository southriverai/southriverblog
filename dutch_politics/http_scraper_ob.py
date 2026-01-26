import hashlib
import logging
import os
from typing import List, Literal, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from bs4.element import Comment, PageElement
from pydantic import BaseModel
from tqdm import tqdm

from dutch_politics.store.bytes_store_base import BytesStoreBase
from dutch_politics.store.object_store_base import ObjectStoreBase
from dutch_politics.store.store_provider_disk import StoreProviderDisk
from dutch_politics.store.store_provider_s3 import StoreProviderS3

logger = logging.getLogger(__name__)


class EntryReference(BaseModel):
    title: str
    subtitle: str
    content_url_html: str
    content_url_pdf: str
    publication_date: str


class EntryReferenceIndex(BaseModel):
    references: List[EntryReference]


class EntryElement(BaseModel):
    type: Literal["other", "speaker"]
    speaker_name: Optional[str]
    speaker_name_title: Optional[str]
    text: Optional[str]


class EntryContent(BaseModel):
    reference: EntryReference
    entry_elements: List[EntryElement]


def extract_suppressed_speaker_name(spreekbeurt_div: PageElement) -> Optional[str]:
    for element in spreekbeurt_div.contents:  # type: ignore
        if (
            hasattr(element, "string")
            and element.string
            and isinstance(element, Comment)
            and element.string.strip().startswith("vlos:spreker")
        ):
            return " ".join(element.string.strip().split(" ")[1:-1])
    return None


# <div class="spreekbeurt"><!--vlos:spreker Jimmy Dijk onderdrukt-->
#                <div class="alineagroep">
#                   <p>De heer <strong class="vet">Dijk</strong> (SP):</p>
#                   <p>Voorzitter. Ik wil alvast aankondigen dat wij een hoofdelijke stemming zullen aanvragen over een van de moties die wij nog gaan indienen. Dan weten de collega's dat nu al.</p>
#                </div>
#             </div>
def parse_page_content_soup(
    beautiful_soup: BeautifulSoup, reference: EntryReference
) -> Optional[EntryContent]:
    content_div = beautiful_soup.find("div", id="broodtekst")
    if not content_div:
        return None
    entry_elements = []
    spreekbeurt_divs = content_div.find_all("div", class_="spreekbeurt")

    for spreekbeurt_div in spreekbeurt_divs:
        speaker_name = extract_suppressed_speaker_name(spreekbeurt_div)
        alineagroep_divs = spreekbeurt_div.find_all("div", class_="alineagroep")

        speaker_name_title = alineagroep_divs[0].find_all("p")[0].get_text()  # type: ignore
        if len(alineagroep_divs[0].find_all("p")) == 1:
            paragraphs_text = ""
        else:
            paragraphs_text = alineagroep_divs[0].find_all("p")[1].get_text()
        for alineagroep_div in alineagroep_divs[1:]:
            paragraphs = alineagroep_div.find_all("p")
            for paragraph in paragraphs:
                paragraphs_text += paragraph.get_text() + "\n"
        entry_elements.append(
            EntryElement(
                type="speaker",
                speaker_name=speaker_name,
                speaker_name_title=speaker_name_title,
                text=paragraphs_text,
            )
        )
    return EntryContent(reference=reference, entry_elements=entry_elements)


def parse_search_results_soup(
    beautiful_soup: BeautifulSoup,
) -> Tuple[List[EntryReference], int, bool]:
    results: List[EntryReference] = []

    # find div with id "Publicaties"
    publications_div: Optional[PageElement] = beautiful_soup.find("div", id="Publicaties")

    span_element: Optional[PageElement] = beautiful_soup.find("span", class_="h1__sub")
    if span_element:
        final_entry = int(span_element.text.split(" ")[-5])
        total_entries = int(span_element.text.split(" ")[-2])
        has_next = final_entry < total_entries
    if not publications_div:
        return results, 0, False
    # ul that is a child of publications_div contains the publication list
    ul = publications_div.find("ul")  # type: ignore
    publication_lis: List[PageElement] = ul.find_all("li", recursive=False)  # type: ignore
    for publication_li in publication_lis:
        title = publication_li.find("h2", class_="result--title").text
        subtitle = publication_li.find("a", class_="result--subtitle").text
        # the first dd out of dl will be the publication date
        publication_date = (
            publication_li.find("dl", class_="dl dl--publication").find_all("dd")[0].text
        )
        content_link_element: Optional[PageElement] = publication_li.find(
            "h2", class_="result--title"
        ).find("a")  # type: ignore
        if content_link_element:
            content_url_html = (
                "https://zoek.officielebekendmakingen.nl/" + content_link_element["href"]
            )
        else:
            content_url_html = ""

        content_link_element: Optional[PageElement] = publication_li.find(
            "a", class_="icon icon--download"
        )
        if content_link_element:
            content_url_pdf = (
                "https://zoek.officielebekendmakingen.nl/" + content_link_element["href"]
            )
        else:
            content_url_pdf = ""
        results.append(
            EntryReference(
                title=title,
                subtitle=subtitle,
                content_url_html=content_url_html,
                content_url_pdf=content_url_pdf,
                publication_date=publication_date,
            )
        )
    return results, total_entries, has_next


def get_page_content_from_url(store: BytesStoreBase, url: str) -> str:
    url_hash = hashlib.sha256(url.encode()).hexdigest()
    content_bytes = store.mget([url_hash])[0]
    if content_bytes:
        print("Content found in store")
        content_str = content_bytes.decode("utf-8")
    else:
        response = requests.get(url)
        store.mset([(url_hash, response.text.encode("utf-8"))])
        content_str = response.text
    return content_str


def get_page_content(
    store: BytesStoreBase,
    vergaderjaar: str,
    query_type: Literal["kamervragen", "handeling"],
    page: int,
) -> str:
    base_url = "https://zoek.officielebekendmakingen.nl/resultaten?"
    result_per_page = 50

    query_kamervragen = f"q=(c.product-area==%22officielepublicaties%22)and(((w.publicatienaam==%22Kamervragen%20(Aanhangsel)%22)or(w.publicatienaam==%22Kamervragen%20zonder%20antwoord%22)))%20AND%20w.vergaderjaar=={vergaderjaar}"
    query_handeling = f"q=(c.product-area==%22officielepublicaties%22)and((w.publicatienaam==%22Handelingen%22))%20AND%20w.vergaderjaar=={vergaderjaar}"
    url_kamervragen = (
        base_url
        + "svel=Publicatiedatum&svol=Aflopend&pg="
        + str(result_per_page)
        + "&"
        + query_kamervragen
        + "&zv=&col=Kamervragen&pagina="
        + str(page)
    )
    url_handeling = (
        base_url
        + "svel=Publicatiedatum&svol=Aflopend&pg="
        + str(result_per_page)
        + "&"
        + query_handeling
        + "&zv=&col=Handelingen&pagina="
        + str(page)
    )

    if query_type == "kamervragen":
        url = url_kamervragen
    elif query_type == "handeling":
        url = url_handeling
    else:
        raise ValueError(f"Invalid query type: {query_type}")
    content_str = get_page_content_from_url(store, url)
    return content_str


def build_index(
    index_store: BytesStoreBase,
    index_id: str,
    html_store: BytesStoreBase,
) -> None:
    logger.info(f"Building index {index_id}")
    all_references: List[EntryReference] = []
    total_entries = 0
    vergaderjaren = []
    vergaderjaren.append("%222025-2026%22")
    vergaderjaren.append("%222024-2025%22")
    vergaderjaren.append("%222023-2024%22")
    vergaderjaren.append("%222022-2023%22")
    for vergaderjaar in vergaderjaren:
        page = 1
        while True:
            print(f"Processing page {page}")
            print(f"Total entries: {len(all_references)} of {total_entries}")
            content_str = get_page_content(html_store, vergaderjaar, "handeling", page)
            beautiful_soup = BeautifulSoup(content_str, "html.parser")
            references, total_entries, has_next = parse_search_results_soup(beautiful_soup)
            all_references.extend(references)
            if not has_next:
                break
            page += 1
    index_object = EntryReferenceIndex(references=all_references)
    index_bytes = index_object.model_dump_json().encode("utf-8")
    index_store.mset([(index_id, index_bytes)])


def load_index(index_store: BytesStoreBase, index_id: str) -> Optional[EntryReferenceIndex]:
    index_bytes = index_store.mget([index_id])[0]
    if index_bytes:
        index_object = EntryReferenceIndex.model_validate_json(index_bytes.decode("utf-8"))
        return index_object
    return None


def main(
    html_store: BytesStoreBase,
    index_store: BytesStoreBase,
    index_id: str,
    entry_store: ObjectStoreBase[EntryContent],
):
    index_object = load_index(index_store, index_id)
    if index_object is None:
        build_index(index_store, index_id, html_store)
        index_object = load_index(index_store, index_id)
    if index_object is None:
        raise ValueError(f"Index {index_id} not found in store")
    all_references: List[EntryReference] = []

    for reference in tqdm(index_object.references):
        content_str = get_page_content_from_url(html_store, reference.content_url_html)
        beautiful_soup = BeautifulSoup(content_str, "html.parser")
        entry_content = parse_page_content_soup(beautiful_soup, reference)
        if not entry_content:
            continue
        entry_id = entry_content.reference.content_url_html.replace(
            "https://zoek.officielebekendmakingen.nl/", ""
        ).replace(".html", ".json")
        entry_store.mset([(entry_id, entry_content)])
    return all_references


if __name__ == "__main__":
    # set loglevel to info
    logging.basicConfig(level=logging.INFO)
    database_name = "database_ob"
    CONNECTION_STRING_OB_CACHE = os.getenv("CONNECTION_STRING_OB_CACHE")
    CONNECTION_STRING_OB_INDEX = os.getenv("CONNECTION_STRING_OB_INDEX")
    html_store = StoreProviderS3(database_name, CONNECTION_STRING_OB_CACHE).get_bytes_store(
        "html_cache"
    )
    index_store = StoreProviderS3(database_name, CONNECTION_STRING_OB_INDEX).get_bytes_store(
        "index_store"
    )
    html_store_disk = StoreProviderDisk(
        database_name,
        "data",
    ).get_bytes_store("html_cache")
    index_store_disk = StoreProviderDisk(
        database_name,
        "data",
    ).get_bytes_store("index_store")
    # copy all entryis from the chache to the disk
    # list_keys = list(html_store.yield_keys())
    # for key in tqdm(list_keys):
    #     html_store_disk.mset([(key, html_store.mget([key])[0])])
    list_keys = list(index_store.yield_keys())
    for key in tqdm(list_keys):
        index_store_disk.mset([(key, index_store.mget([key])[0])])

    path_dir_database = "data"
    entry_store = StoreProviderDisk(
        "database_ob_entries",
        path_dir_database,
    ).get_object_store("entry_content", EntryContent)

    main(html_store, index_store, "index_2025-2021", entry_store)
