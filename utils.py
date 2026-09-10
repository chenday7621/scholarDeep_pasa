# Copyright (c) 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Please note that:
1. You need to first apply for a Google Search API key at https://serpapi.com/,
   and replace the 'your google keys' below before you can use it.
2. The service for searching arxiv and obtaining paper contents is relatively simple. 
   If there are any bugs or improvement suggestions, you can submit pull requests.
   We would greatly appreciate and look forward to your contributions!!
"""
import os
import re
import bs4
import json
import arxiv
import threading
import time
import urllib
import zipfile
import warnings
import requests
import xml.etree.ElementTree as ET
from datetime   import datetime
from email.utils import parsedate_to_datetime
from requests.adapters import HTTPAdapter
warnings.simplefilter("always")

GOOGLE_KEY = os.environ.get("SERPER_API_KEY", "")
arxiv_client = arxiv.Client(delay_seconds = 0.05)
id2paper     = json.load(open("data/paper_database/id2paper.json"))
paper_db     = zipfile.ZipFile("data/paper_database/cs_paper_2nd.zip", "r")

def google_search_arxiv_id(query, num=10, end_date=None):
    url = "https://google.serper.dev/search"

    search_query = f"{query} site:arxiv.org"
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
            search_query = f"{query} before:{end_date} site:arxiv.org"
        except:
            search_query = f"{query} site:arxiv.org"
    
    payload = json.dumps({
        "q": search_query, 
        "num": num, 
        "page": 1, 
    })

    headers = {
        'X-API-KEY': GOOGLE_KEY,
        'Content-Type': 'application/json'
    }
    assert GOOGLE_KEY, "set SERPER_API_KEY environment variable"

    for _ in range(3):
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                results = json.loads(response.text)
                arxiv_id_list = []
                for paper in results['organic']:
                    if re.search(r'arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d+)', paper["link"]):
                        arxiv_id = re.search(r'arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d+)', paper["link"]).group(1)
                        arxiv_id_list.append(arxiv_id)
                return list(set(arxiv_id_list))
        except:
            warnings.warn(f"google search failed, query: {query}")
            continue
    return []

def parse_metadata(metas):
    """
    Parse concatenated metadata string into authors, title, and journal.
    """
    # Get and clean metas
    metas = [item.replace('\n', ' ') for item in metas]
    meta_string = ' '.join(metas)
    
    authors, title, journal = "", "", ""
        
    if len(metas) == 3: # author / title / journal
        authors, title, journal = metas
    else:
        # Remove the year suffix (e.g., 2022a) from the metadata string
        meta_string = re.sub(r'\.\s\d{4}[a-z]?\.', '.', meta_string)
        # Regular expression to match the pattern
        regex = r"^(.*?\.\s)(.*?)(\.\s.*|$)"
        match = re.match(regex, meta_string, re.DOTALL)
        if match:
            authors = match.group(1).strip() if match.group(1) else ""
            title = match.group(2).strip() if match.group(2) else ""
            journal = match.group(3).strip() if match.group(3) else ""

            if journal.startswith('. '):
                journal = journal[2:]

    return {
        "meta_list": metas, 
        "meta_string": meta_string, 
        "authors": authors,
        "title": title,
        "journal": journal
    }

def create_dict_for_citation(ul_element):
    citation_dict, futures, id_attrs = {}, [], []
    for li in ul_element.find_all("li", recursive=False):
        id_attr = li['id']
        metas = [x.text.strip() for x in li.find_all('span', class_='ltx_bibblock')]
        id_attrs.append(id_attr)
        futures.append(parse_metadata(metas))
    results = list(zip(id_attrs, futures))
    citation_dict = dict(results)
    return citation_dict

def generate_full_toc(soup):
    toc = []
    stack = [(0, toc)]
    
    # Mapping of heading tags to their levels
    heading_tags = {'h1': 1, 'h2': 2, 'h3': 3, 'h4': 4, 'h5': 5}
    
    for tag in soup.find_all(heading_tags.keys()):
        level = heading_tags[tag.name]
        title = tag.get_text()
        
        # Ensure the stack has the correct level
        while stack and stack[-1][0] >= level:
            stack.pop()
        
        current_level = stack[-1][1]

        # Find the nearest enclosing section with an id
        section = tag.find_parent('section', id=True)
        section_id = section.get('id') if section else None
        
        # Create the new entry
        new_entry = {'title': title, 'id': section_id, 'subsections': []}
        
        current_level.append(new_entry)
        stack.append((level, new_entry['subsections']))
    
    return toc

def parse_text(local_text, tag):
    ignore_tags = ['a', 'figure', 'center', 'caption', 'td', 'h1', 'h2', 'h3', 'h4']
    # latexmlc
    ignore_tags += ['sup']
    max_math_length = 300000

    for child in tag.children:
        child_type = type(child)
        if child_type == bs4.element.NavigableString:
                txt = child.get_text()
                local_text.append(txt)

        elif child_type == bs4.element.Comment:
            continue
        elif child_type == bs4.element.Tag:

                if child.name in ignore_tags or (child.has_attr('class') and child['class'][0] == 'navigation'):
                    continue
                elif child.name == 'cite':
                    # add hrefs
                    hrefs = [a.get('href').strip('#') for a in child.find_all('a', class_='ltx_ref')]
                    local_text.append('~\cite{' + ', '.join(hrefs) + '}')
                elif child.name == 'img' and child.has_attr('alt'):
                    math_txt = child.get('alt')
                    if len(math_txt) < max_math_length:
                        local_text.append(math_txt)

                elif child.has_attr('class') and (child['class'][0] == 'ltx_Math' or child['class'][0] == 'ltx_equation'):
                    math_txt = child.get_text()
                    if len(math_txt) < max_math_length:
                        local_text.append(math_txt)

                elif child.name == 'section':
                    return
                else:
                    parse_text(local_text, child)
        else:
            raise RuntimeError('Unhandled type')

def clean_text(text):
    delete_items = ['=-1', '\t', u'\xa0', '[]', '()', 'mathbb', 'mathcal', 'bm', 'mathrm', 'mathit', 'mathbf', 'mathbfcal', 'textbf', 'textsc', 'langle', 'rangle', 'mathbin']
    for item in delete_items:
        text = text.replace(item, '')
    text = re.sub(' +', ' ', text)
    text = re.sub(r'[[,]+]', '', text)
    text = re.sub(r'\.(?!\d)', '. ', text)
    text = re.sub('bib. bib', 'bib.bib', text)
    return text

def remove_stop_word_sections_and_extract_text(toc, soup, stop_words=['references', 'acknowledgments', 'about this document', 'apopendix']):
    def has_stop_word(title, stop_words):
        return any(stop_word.lower() in title.lower() for stop_word in stop_words)
    
    def extract_text(entry, soup):
        section_id = entry['id']
        if section_id: # section_id
            section = soup.find(id=section_id)
            if section is not None:
                local_text = []
                parse_text(local_text, section)
                if local_text:
                    processed_text = clean_text(''.join(local_text))
                    entry['text'] = processed_text
        return 0 
    
    def filter_and_update_toc(entries):
        filtered_entries = []
        for entry in entries:
            if not has_stop_word(entry['title'], stop_words):
                # Get clean text
                extract_text(entry, soup)                
                entry['subsections'] = filter_and_update_toc(entry['subsections'])
                filtered_entries.append(entry)
        return filtered_entries
    
    return filter_and_update_toc(toc)

def parse_html(html_file):
    soup = bs4.BeautifulSoup(html_file, "lxml")
    # parse title
    title = soup.head.title.get_text().replace("\n", " ")
    # parse abstract
    abstract = soup.find(class_='ltx_abstract').get_text()
    # parse citation
    citation = soup.find(class_='ltx_biblist')
    citation_dict = create_dict_for_citation(citation)
    # generate the full toc without text
    sections = generate_full_toc(soup)
    # remove the sections need to skip and extract the text of the rest sections
    sections = remove_stop_word_sections_and_extract_text(sections, soup)
    document = {
        "title": title, 
        "abstract": abstract, 
        "sections": sections, 
        "references": citation_dict,
    }
    return document 

def search_section_by_arxiv_id(entry_id, cite):
    warnings.warn("Using search_section_by_arxiv_id function may return wrong title because ar5iv parsing citation error. To solve this, You can prompt any LLM to extract the paper title from the reference string")
    assert re.match(r'^\d+\.\d+$', entry_id)
    url = f'https://ar5iv.labs.arxiv.org/html/{entry_id}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            html_content = response.text
            if not 'https://ar5iv.labs.arxiv.org/html' in html_content:
                warnings.warn(f'Invalid ar5iv HTML document: {url}')
                return None
            else:
                try:
                    document = parse_html(html_content)
                except:
                    warnings.warn(f'Wrong format HTML document: {url}')
                    return None
                try:
                    sections = get_2nd_section(document["sections"][0]["subsections"])
                except:
                    warnings.warn(f'Get subsections error')
                    return None
                sections2title = {}
                for k, v in sections.items():
                    k = " ".join(k.split("\n"))
                    sections2title[k] = set()
                    bibs = re.findall(cite, v, re.DOTALL)
                    for bib in bibs:
                        bib = bib.split(",")
                        for b in bib:
                            if b not in document["references"]:
                                continue
                            sections2title[k].add(document["references"][b]["title"]) # !!! The title here may be incorrect, you can use an LLM to parse the write title from document["references"][b]["meta_string"] !!!
                    if len(sections2title[k]) == 0:
                        del sections2title[k]
                    else:
                        sections2title[k] = list(sections2title[k])
                return sections2title
        else:
            warnings.warn(f"Failed to retrieve content. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        warnings.warn(f"An error occurred: {e}")
        return None

def keep_letters(s):
    letters = [c for c in s if c.isalpha()]
    result = ''.join(letters)
    return result.lower()

def search_paper_by_arxiv_id(arxiv_id):
    """
    Search paper by arxiv id.
    :param arxiv_id: arxiv id of the paper
    :return: paper list
    """
    if arxiv_id in id2paper:
        title_key = keep_letters(id2paper[arxiv_id])
        if title_key in _paper_db_names:
            with paper_db.open(title_key) as f:
                data = json.loads(f.read().decode("utf-8"))
            return {
                "arxiv_id": arxiv_id,
                "title": data["title"].replace("\n", " "),
                "abstract": data["abstract"],
                "sections": data["sections"],
                "source": 'SearchFrom:local_paper_db',
            }

    search = arxiv.Search(
        query = "",
        id_list = [arxiv_id],
        max_results = 10,
        sort_by = arxiv.SortCriterion.Relevance,
        sort_order = arxiv.SortOrder.Descending,
    )

    try:
        results = list(arxiv_client.results(search, offset=0))
    except:
        warnings.warn(f"Failed to search arxiv id: {arxiv_id}")
        return None

    res = None
    for arxiv_id_result in results:
        entry_id = arxiv_id_result.entry_id.split("/")[-1]
        entry_id = entry_id.split('v')[0]
        if entry_id == arxiv_id:
            res = {
                "arxiv_id": arxiv_id,
                "title": arxiv_id_result.title.replace("\n", " "),
                "abstract": arxiv_id_result.summary.replace("\n", " "),
                "sections": "",
                "source": 'SearchFrom:arxiv',
            }
            break
    return res
    
ARXIV_TITLE_FALLBACK_PATCH = "REPRO_LOCAL_ONLY_001"
ARXIV_TITLE_MAX_CONCURRENCY = 1
ARXIV_TITLE_MAX_ATTEMPTS = 3
ARXIV_TITLE_TIMEOUT = (5, 30)
ARXIV_TITLE_REQUEST_INTERVAL_SECONDS = 3.0
ARXIV_TITLE_429_COOLDOWN_SECONDS = 6.0
ARXIV_TITLE_CONSECUTIVE_429_SKIP_THRESHOLD = 20
_arxiv_title_semaphore = threading.BoundedSemaphore(ARXIV_TITLE_MAX_CONCURRENCY)
_arxiv_title_session = requests.Session()
_arxiv_title_session.mount(
    "https://",
    HTTPAdapter(pool_connections=1, pool_maxsize=1, max_retries=0, pool_block=True),
)
_arxiv_title_session.headers.update({"User-Agent": "PaSa arXiv API title fallback"})
_arxiv_title_lock = threading.Lock()
_arxiv_title_rate_condition = threading.Condition()
_arxiv_title_next_request_start = 0.0
_arxiv_title_request_starts = []
_arxiv_title_cache = {}
_arxiv_title_inflight = {}
_arxiv_title_stats = {
    "total_lookups": 0,
    "unique_titles": 0,
    "cache_hits": 0,
    "http_requests": 0,
    "http_200": 0,
    "http_429": 0,
    "timeouts": 0,
    "connection_reset": 0,
    "remote_disconnect": 0,
    "request_errors": 0,
    "retries": 0,
    "global_cooldowns": 0,
    "consecutive_http_429": 0,
    "max_consecutive_http_429": 0,
    "consecutive_429_skips": 0,
    "final_failures": 0,
}
_arxiv_title_failed_titles = {}
_paper_db_names = set(paper_db.namelist())

def _build_local_title_index():
    unique_titles, ambiguous_titles = {}, set()
    for arxiv_id, title in id2paper.items():
        normalized_title = keep_letters(title)
        if not normalized_title or normalized_title in ambiguous_titles:
            continue
        if normalized_title in unique_titles:
            unique_titles.pop(normalized_title)
            ambiguous_titles.add(normalized_title)
        else:
            unique_titles[normalized_title] = arxiv_id
    local_titles = {
        title: arxiv_id
        for title, arxiv_id in unique_titles.items()
        if title in _paper_db_names
    }
    return local_titles, ambiguous_titles

_local_title_index, _local_title_ambiguous = _build_local_title_index()
_local_title_stats = {
    "LOCAL_TITLE_LOOKUPS": 0,
    "LOCAL_TITLE_HITS": 0,
    "LOCAL_TITLE_MISSES": 0,
    "LOCAL_TITLE_AMBIGUOUS": 0,
    "ARXIV_FALLBACKS": 0,
    "ARXIV_API_FALLBACKS": 0,
}

def get_local_title_lookup_stats():
    with _arxiv_title_lock:
        stats = dict(_local_title_stats)
        stats["LOCAL_TITLE_INDEX_SIZE"] = len(_local_title_index)
        stats["LOCAL_TITLE_AMBIGUOUS_KEYS"] = len(_local_title_ambiguous)
        return stats

def _normalized_title(title):
    return title.lower().strip('.').replace(' ', '').replace('\n', '')

def _update_arxiv_title_stats(name, value=1):
    with _arxiv_title_lock:
        _arxiv_title_stats[name] += value

def _record_arxiv_title_http_status(status_code):
    with _arxiv_title_lock:
        if status_code == 429:
            _arxiv_title_stats["consecutive_http_429"] += 1
            _arxiv_title_stats["max_consecutive_http_429"] = max(
                _arxiv_title_stats["max_consecutive_http_429"],
                _arxiv_title_stats["consecutive_http_429"],
            )
        else:
            _arxiv_title_stats["consecutive_http_429"] = 0
        return _arxiv_title_stats["consecutive_http_429"]

def get_arxiv_title_lookup_stats():
    with _arxiv_title_lock:
        stats = dict(_arxiv_title_stats)
        starts = list(_arxiv_title_request_starts)
        stats["failed_titles"] = dict(_arxiv_title_failed_titles)
        stats["cache_size"] = len(_arxiv_title_cache)
        stats["patch_id"] = ARXIV_TITLE_FALLBACK_PATCH
        stats["max_concurrency"] = ARXIV_TITLE_MAX_CONCURRENCY
        stats["max_attempts"] = ARXIV_TITLE_MAX_ATTEMPTS
        stats["timeout"] = ARXIV_TITLE_TIMEOUT
        stats["request_interval_seconds"] = ARXIV_TITLE_REQUEST_INTERVAL_SECONDS
        stats["http_429_cooldown_seconds"] = ARXIV_TITLE_429_COOLDOWN_SECONDS
        stats["consecutive_429_skip_threshold"] = (
            ARXIV_TITLE_CONSECUTIVE_429_SKIP_THRESHOLD
        )
        stats["minimum_request_start_spacing_seconds"] = (
            min(b - a for a, b in zip(starts, starts[1:]))
            if len(starts) > 1 else None
        )
        left = 0
        max_requests = 0
        for right, started in enumerate(starts):
            while starts[left] < started - 1.0:
                left += 1
            max_requests = max(max_requests, right - left + 1)
        stats["max_requests_in_any_1s_window"] = max_requests
        return stats

def _retry_after_seconds(response):
    value = response.headers.get("Retry-After")
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
            return max(0.0, (retry_at - datetime.now(retry_at.tzinfo)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None

def _wait_for_arxiv_title_request_slot():
    global _arxiv_title_next_request_start
    with _arxiv_title_rate_condition:
        while True:
            now = time.monotonic()
            wait = _arxiv_title_next_request_start - now
            if wait <= 0:
                started = time.monotonic()
                _arxiv_title_next_request_start = (
                    started + ARXIV_TITLE_REQUEST_INTERVAL_SECONDS
                )
                break
            _arxiv_title_rate_condition.wait(wait)
    with _arxiv_title_lock:
        _arxiv_title_request_starts.append(started)

def _apply_arxiv_title_global_cooldown(response):
    global _arxiv_title_next_request_start
    retry_after = _retry_after_seconds(response)
    cooldown = max(
        ARXIV_TITLE_429_COOLDOWN_SECONDS,
        retry_after if retry_after is not None else 0.0,
    )
    with _arxiv_title_rate_condition:
        _arxiv_title_next_request_start = max(
            _arxiv_title_next_request_start,
            time.monotonic() + cooldown,
        )
        _arxiv_title_rate_condition.notify_all()
    _update_arxiv_title_stats("global_cooldowns")

def _search_arxiv_id_by_title_uncached(title):
    """
    Search arxiv id by title.
    :param title: title of the paper
    :return: arxiv id of the paper
    """
    url = "https://export.arxiv.org/api/query"
    params = {
        "search_query": f'ti:"{title}"',
        "start": 0,
        "max_results": 10,
    }
    
    for attempt in range(ARXIV_TITLE_MAX_ATTEMPTS):
        response = None
        try:
            with _arxiv_title_semaphore:
                _wait_for_arxiv_title_request_slot()
                _update_arxiv_title_stats("http_requests")
                response = _arxiv_title_session.get(
                    url,
                    params=params,
                    timeout=ARXIV_TITLE_TIMEOUT,
                )
                consecutive_429 = _record_arxiv_title_http_status(
                    response.status_code
                )
        except requests.Timeout as e:
            _record_arxiv_title_http_status(None)
            _update_arxiv_title_stats("timeouts")
            reason = type(e).__name__
            if attempt + 1 < ARXIV_TITLE_MAX_ATTEMPTS:
                _update_arxiv_title_stats("retries")
                continue
            return None, reason
        except requests.RequestException as e:
            _record_arxiv_title_http_status(None)
            error = str(e).lower()
            if "connection reset" in error:
                _update_arxiv_title_stats("connection_reset")
                reason = "connection reset"
            elif "remote end closed" in error or "remotedisconnected" in error:
                _update_arxiv_title_stats("remote_disconnect")
                reason = "remote disconnect"
            else:
                _update_arxiv_title_stats("request_errors")
                reason = type(e).__name__
            if attempt + 1 < ARXIV_TITLE_MAX_ATTEMPTS:
                _update_arxiv_title_stats("retries")
                continue
            return None, reason

        if response.status_code == 200:
            _update_arxiv_title_stats("http_200")
            try:
                root = ET.fromstring(response.content)
            except ET.ParseError:
                return None, "Atom parse failure"

            namespace = {"atom": "http://www.w3.org/2005/Atom"}
            if root.tag != "{http://www.w3.org/2005/Atom}feed":
                return None, "unexpected Atom root"

            exact_ids = set()
            for entry in root.findall("atom:entry", namespace):
                result_title = " ".join(
                    entry.findtext("atom:title", default="", namespaces=namespace).split()
                )
                entry_id = entry.findtext(
                    "atom:id", default="", namespaces=namespace
                ).strip()
                if not result_title or not entry_id:
                    continue
                if _normalized_title(result_title) != _normalized_title(title):
                    continue
                arxiv_id = entry_id.rstrip("/").split("/")[-1]
                arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
                if arxiv_id:
                    exact_ids.add(arxiv_id)

            if len(exact_ids) == 1:
                return exact_ids.pop(), None
            if len(exact_ids) > 1:
                return None, "ambiguous exact title matches"
            if root.findall("atom:entry", namespace):
                return None, "title mismatch"
            return None, "no results"
        elif response.status_code == 429:
            _update_arxiv_title_stats("http_429")
            _apply_arxiv_title_global_cooldown(response)
            if consecutive_429 >= ARXIV_TITLE_CONSECUTIVE_429_SKIP_THRESHOLD:
                _update_arxiv_title_stats("consecutive_429_skips")
                return None, "HTTP 429 (consecutive threshold reached)"
            if attempt + 1 < ARXIV_TITLE_MAX_ATTEMPTS:
                _update_arxiv_title_stats("retries")
                continue
            return None, "HTTP 429"
        else:
            return None, f"HTTP {response.status_code}"

    return None, "retry limit reached"

def search_arxiv_id_by_title(title):
    normalized_title = _normalized_title(title)
    with _arxiv_title_lock:
        _arxiv_title_stats["total_lookups"] += 1
        if normalized_title in _arxiv_title_cache:
            _arxiv_title_stats["cache_hits"] += 1
            return _arxiv_title_cache[normalized_title]
        event = _arxiv_title_inflight.get(normalized_title)
        if event is None:
            event = threading.Event()
            _arxiv_title_inflight[normalized_title] = event
            _arxiv_title_stats["unique_titles"] += 1
            owner = True
        else:
            owner = False

    if not owner:
        event.wait()
        with _arxiv_title_lock:
            _arxiv_title_stats["cache_hits"] += 1
            return _arxiv_title_cache[normalized_title]

    arxiv_id, failure_reason = None, "unexpected error"
    try:
        arxiv_id, failure_reason = _search_arxiv_id_by_title_uncached(title)
        return arxiv_id
    finally:
        with _arxiv_title_lock:
            _arxiv_title_cache[normalized_title] = arxiv_id
            if arxiv_id is None:
                _arxiv_title_stats["final_failures"] += 1
                _arxiv_title_failed_titles[title] = failure_reason
            _arxiv_title_inflight.pop(normalized_title).set()
        if arxiv_id is None:
            warnings.warn(f"arXiv title lookup failed ({failure_reason}): {title}")

def search_paper_by_title(title):
    """
    Search paper by title.
    :param title: title of the paper
    :return: paper list
    """
    normalized_title = keep_letters(title)
    with _arxiv_title_lock:
        _local_title_stats["LOCAL_TITLE_LOOKUPS"] += 1
        if normalized_title in _local_title_ambiguous:
            _local_title_stats["LOCAL_TITLE_AMBIGUOUS"] += 1
            title_id = None
        elif normalized_title in _local_title_index:
            _local_title_stats["LOCAL_TITLE_HITS"] += 1
            title_id = _local_title_index[normalized_title]
        else:
            _local_title_stats["LOCAL_TITLE_MISSES"] += 1
            title_id = None

    if title_id is None:
        return None
    title_id = title_id.split('v')[0]
    return search_paper_by_arxiv_id(title_id)

def get_subsection(sections):
    res = {}
    for section in sections:
        if "text" in section and section["text"].strip() != "":
            res[section["title"].strip()] = section["text"].strip()
        subsections = get_subsection(section["subsections"])
        for k, v in subsections.items():
            res[k] = v
    return res

def get_1st_section(sections):
    res = {}
    for section in sections:
        subsections = get_subsection(section["subsections"])
        if "text" in section and section["text"].strip() != "" or len(subsections) > 0:
            if "text" in section and section["text"].strip() != "":
                res[section["title"].strip()] = section["text"].strip()
            else:
                res[section["title"].strip()] = ""
            for k, v in subsections.items():
                res[section["title"].strip()] += v.strip()
    res_new = {}
    for k, v in res.items():
        if "appendix" not in k.lower():
            res_new[" ".join(k.split("\n")).strip()] = v
    return res_new

def get_2nd_section(sections):
    res = {}
    for section in sections:
        subsections = get_1st_section(section["subsections"])
        if "text" in section and section["text"].strip() != "":
            if "text" in section and section["text"].strip() != "":
                res[section["title"].strip()] = section["text"].strip()
        for k, v in subsections.items():
            res[section["title"].strip() + " " + k.strip()] = v.strip()
    res_new = {}
    for k, v in res.items():
        if "appendix" not in k.lower():
            res_new[" ".join(k.split("\n")).strip()] = v
    return res_new

def cal_micro(pred_set, label_set):
    if len(label_set) == 0:
        return 0, 0, 0

    if len(pred_set) == 0:
        return 0, 0, len(label_set)

    tp = len(pred_set & label_set)
    fp = len(pred_set - label_set)
    fn = len(label_set - pred_set)

    assert tp + fn == len(label_set)
    assert len(label_set) != 0
    return tp, fp, fn

if __name__ == "__main__":
    print(search_section_by_arxiv_id("2307.00235", r"~\\cite\{(.*?)\}"))
    # print(search_paper_by_arxiv_id("2307.00235"))
    # print(search_paper_by_title("A hybrid approach to CMB lensing reconstruction on all-sky intensity maps"))
