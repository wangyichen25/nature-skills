#!/usr/bin/env python3
"""
Segment medical manuscript text, search PubMed-grounded citation candidates, enrich DOI
metadata with Crossref when available, and export ENW, RIS, or Zotero RDF files.

Candidates are metadata/abstract-screened only until a human checks the abstract,
full text, guideline text, or trial registry entry.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import ssl
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode
from urllib.error import URLError
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape as xml_escape
from xml.sax.saxutils import quoteattr


PUBMED_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
CROSSREF_API = "https://api.crossref.org/works"
USER_AGENT = "codex-nejm-citation/1.0 (mailto:unknown@example.com)"
EXPORT_FORMAT_CHOICES = ("enw", "ris", "zotero-rdf", "rdf")
DEFAULT_EXPORT_FORMAT = "enw"
SCOPE_CHOICES = ("big4", "jama", "nejm", "lancet", "bmj", "gi", "big4-gi", "major-medical", "major-clinical")
DEFAULT_SCOPE = "big4-gi"

ZOTERO_RDF_NS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "z": "http://www.zotero.org/namespaces/export#",
    "dcterms": "http://purl.org/dc/terms/",
    "bib": "http://purl.org/net/biblio#",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "prism": "http://prismstandard.org/namespaces/1.2/basic/",
}

try:
    import certifi  # type: ignore

    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:  # pragma: no cover - fallback depends on local Python packaging
    SSL_CONTEXT = ssl.create_default_context()


JOURNAL_FAMILIES: dict[str, set[str]] = {
    "nejm": {
        "New England Journal of Medicine",
        "The New England Journal of Medicine",
        "N Engl J Med",
        "NEJM Evidence",
    },
    "jama": {
        "JAMA",
        "JAMA Network Open",
        "JAMA Intern Med",
        "JAMA Internal Medicine",
        "JAMA Surg",
        "JAMA Surgery",
        "JAMA Oncol",
        "JAMA Oncology",
        "JAMA Neurol",
        "JAMA Neurology",
        "JAMA Cardiol",
        "JAMA Cardiology",
        "JAMA Pediatr",
        "JAMA Pediatrics",
    },
    "lancet": {
        "Lancet",
        "The Lancet",
        "Lancet Digit Health",
        "The Lancet Digital Health",
        "Lancet Gastroenterol Hepatol",
        "The Lancet Gastroenterology & Hepatology",
        "Lancet Oncol",
        "The Lancet Oncology",
        "Lancet Public Health",
        "The Lancet Public Health",
        "Lancet Reg Health Am",
        "Lancet Reg Health Eur",
        "Lancet Reg Health West Pac",
        "Lancet Reg Health Southeast Asia",
    },
    "bmj": {
        "BMJ",
        "BMJ Medicine",
        "BMJ Open",
        "BMJ Qual Saf",
        "BMJ Quality & Safety",
        "BMJ Evid Based Med",
        "BMJ Evidence-Based Medicine",
        "BMJ Open Gastroenterol",
        "BMJ Open Gastroenterology",
    },
    "gi": {
        "Gastroenterology",
        "Gut",
        "Am J Gastroenterol",
        "The American Journal of Gastroenterology",
        "Clin Gastroenterol Hepatol",
        "Clinical Gastroenterology and Hepatology",
        "Gastrointest Endosc",
        "Gastrointestinal Endoscopy",
        "Endoscopy",
        "Endosc Int Open",
        "Endoscopy International Open",
        "Aliment Pharmacol Ther",
        "Alimentary Pharmacology & Therapeutics",
        "Dig Dis Sci",
        "Digestive Diseases and Sciences",
        "Inflamm Bowel Dis",
        "Inflammatory Bowel Diseases",
        "United European Gastroenterol J",
        "United European Gastroenterology Journal",
        "J Hepatol",
        "Journal of Hepatology",
        "Hepatology",
        "Liver Int",
        "Liver International",
    },
    "major-extra": {
        "Ann Intern Med",
        "Annals of Internal Medicine",
        "PLOS Med",
        "PLOS Medicine",
        "Clin Infect Dis",
        "Clinical Infectious Diseases",
        "Circulation",
        "J Clin Oncol",
        "Journal of Clinical Oncology",
    },
}


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


NORMALIZED_JOURNALS: dict[str, str] = {}
JOURNAL_TO_FAMILY: dict[str, str] = {}
for family_name, titles in JOURNAL_FAMILIES.items():
    for title in titles:
        NORMALIZED_JOURNALS[norm(title)] = title
        JOURNAL_TO_FAMILY[norm(title)] = family_name


@dataclass
class Segment:
    id: str
    text: str
    search_query: str
    order: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "search_query": self.search_query,
            "order": self.order,
        }


@dataclass
class Candidate:
    title: str = ""
    journal: str = ""
    family: str = ""
    year: str = ""
    y1: str = ""
    doi: str = ""
    pmid: str = ""
    url: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    issn: str = ""
    authors: list[str] | None = None
    abstract: str = ""
    type: str = "journal-article"
    score: float = 0.0
    source_query: str = ""
    source_backend: str = "PubMed"

    def __post_init__(self) -> None:
        if self.authors is None:
            self.authors = []

    @property
    def key(self) -> str:
        if self.doi:
            return f"doi:{self.doi.lower()}"
        if self.pmid:
            return f"pmid:{self.pmid}"
        return f"{self.title.lower()}|{self.journal.lower()}"

    @property
    def doi_url(self) -> str:
        return f"https://doi.org/{self.doi}" if self.doi else ""

    @property
    def pubmed_url(self) -> str:
        return f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/" if self.pmid else ""

    @property
    def identifier_url(self) -> str:
        return self.doi_url or self.pubmed_url or self.url

    @property
    def first_author(self) -> str:
        if not self.authors:
            return "Unknown author"
        return self.authors[0].split(",", 1)[0]

    @property
    def citation_marker(self) -> str:
        if self.year:
            return f"{self.first_author} et al. {self.year}"
        return f"{self.first_author} et al."

    @property
    def journal_resource(self) -> str:
        if self.issn:
            return f"urn:issn:{slugify(self.issn)}"
        if self.journal:
            return f"urn:journal:{slugify(self.journal)}"
        return f"urn:journal:{stable_hash(self.key)}"

    @property
    def article_resource(self) -> str:
        return self.identifier_url or f"urn:candidate:{stable_hash(self.key)}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "journal": self.journal,
            "family": self.family,
            "year": self.year,
            "doi": self.doi,
            "pmid": self.pmid,
            "doi_url": self.doi_url,
            "pubmed_url": self.pubmed_url,
            "url": self.url,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "issn": self.issn,
            "authors": self.authors,
            "abstract": self.abstract,
            "type": self.type,
            "score": self.score,
            "source_query": self.source_query,
            "source_backend": self.source_backend,
            "citation_marker": self.citation_marker,
            "support_grade": "metadata/abstract-screened only",
            "screening_note": "Check abstract/full text or registry/guideline source before citing as support.",
        }


def stable_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"


def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def ris_escape(text: str) -> str:
    return clean_text(text).replace("\n", " ").replace("\r", " ")


def normalize_export_format(value: str | None) -> str:
    if not value:
        return DEFAULT_EXPORT_FORMAT
    return "zotero-rdf" if value == "rdf" else value


def infer_export_format(output_path: Path | None) -> str:
    if output_path is None:
        return DEFAULT_EXPORT_FORMAT
    suffix = output_path.suffix.lower()
    if suffix == ".ris":
        return "ris"
    if suffix == ".rdf":
        return "zotero-rdf"
    return "enw"


def export_filename(export_format: str, base: str = "nejm_references") -> str:
    if export_format == "ris":
        return f"{base}.ris"
    if export_format == "zotero-rdf":
        return f"{base}.rdf"
    return f"{base}.enw"


def export_label(export_format: str) -> str:
    if export_format == "ris":
        return "RIS"
    if export_format == "zotero-rdf":
        return "Zotero RDF"
    return "ENW"


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def query_from_segment(text: str, max_words: int = 24) -> str:
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9\-/%]*", clean_text(text))
    stopwords = {
        "the", "a", "an", "and", "or", "of", "to", "in", "for", "by", "with", "on", "at",
        "from", "is", "are", "was", "were", "be", "been", "being", "that", "this", "these",
        "those", "can", "may", "could", "should",
    }
    content = [word for word in words if word.lower() not in stopwords]
    return " ".join(content[:max_words]) or clean_text(text)[:220]


def segment_text(text: str, max_chars: int = 700) -> list[Segment]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n+", text.strip()) if part.strip()]
    raw_segments: list[str] = []
    for paragraph in paragraphs:
        sentences = split_sentences(paragraph)
        if len(sentences) > 1:
            raw_segments.extend(sentences)
        elif len(paragraph) <= max_chars:
            raw_segments.append(paragraph)
        else:
            raw_segments.extend([paragraph[idx : idx + max_chars] for idx in range(0, len(paragraph), max_chars)])
    segments: list[Segment] = []
    for raw in raw_segments:
        cleaned = clean_text(raw)
        if len(cleaned) < 10:
            continue
        segments.append(
            Segment(
                id=f"S{len(segments) + 1:03d}",
                text=cleaned,
                search_query=query_from_segment(cleaned),
                order=len(segments) + 1,
            )
        )
    return segments


def read_text_inputs(args: argparse.Namespace) -> str:
    parts: list[str] = []
    if args.text:
        parts.extend(args.text)
    if args.text_file:
        parts.append(Path(args.text_file).read_text(encoding="utf-8"))
    return "\n\n".join(part for part in parts if part.strip())


def read_claims(args: argparse.Namespace) -> list[str]:
    claims = list(args.claim or [])
    if args.claim_file:
        claims.extend(line.strip() for line in Path(args.claim_file).read_text(encoding="utf-8").splitlines() if line.strip())
    return claims


def read_dois(args: argparse.Namespace) -> list[str]:
    dois = list(args.doi or [])
    if args.doi_file:
        dois.extend(line.strip() for line in Path(args.doi_file).read_text(encoding="utf-8").splitlines() if line.strip())
    cleaned: list[str] = []
    for doi in dois:
        doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi.strip(), flags=re.IGNORECASE)
        if doi:
            cleaned.append(doi)
    return cleaned


def build_segments(args: argparse.Namespace) -> list[Segment]:
    segments = segment_text(read_text_inputs(args), args.segment_chars)
    for claim in read_claims(args):
        cleaned = clean_text(claim)
        if cleaned:
            segments.append(
                Segment(
                    id=f"S{len(segments) + 1:03d}",
                    text=cleaned,
                    search_query=query_from_segment(cleaned),
                    order=len(segments) + 1,
                )
            )
    return segments


def families_for_scope(scope: str) -> set[str]:
    if scope in {"nejm", "jama", "lancet", "bmj", "gi"}:
        return {scope}
    if scope == "big4":
        return {"nejm", "jama", "lancet", "bmj"}
    if scope == "big4-gi":
        return {"nejm", "jama", "lancet", "bmj", "gi"}
    if scope in {"major-medical", "major-clinical"}:
        return {"nejm", "jama", "lancet", "bmj", "gi", "major-extra"}
    return {"nejm", "jama", "lancet", "bmj", "gi", "major-extra"}


def journal_family(journal: str) -> str:
    journal_norm = norm(journal)
    if journal_norm in JOURNAL_TO_FAMILY:
        family = JOURNAL_TO_FAMILY[journal_norm]
        return "major-medical" if family == "major-extra" else family
    if journal_norm.startswith("jama "):
        return "jama"
    if "lancet" in journal_norm:
        return "lancet"
    if journal_norm.startswith("bmj"):
        return "bmj"
    return ""


def in_scope(journal: str, scope: str) -> bool:
    family = journal_family(journal)
    if not family:
        return False
    allowed = families_for_scope(scope)
    if family in {"major-medical", "major-clinical"}:
        return "major-extra" in allowed
    return family in allowed


def pubmed_journal_filter(scope: str) -> str:
    families = families_for_scope(scope)
    titles: list[str] = []
    for family in families:
        titles.extend(sorted(JOURNAL_FAMILIES.get(family, set())))
    clauses = [f'"{title}"[Journal]' for title in sorted(set(titles))]
    return " OR ".join(clauses)


def request_json(url: str, mailto: str | None = None) -> dict[str, Any]:
    headers = {"User-Agent": USER_AGENT if not mailto else f"codex-nejm-citation/1.0 (mailto:{mailto})"}
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            return json.loads(response.read().decode("utf-8"))
    except URLError as exc:
        if "CERTIFICATE_VERIFY_FAILED" not in str(exc):
            raise
        with urlopen(req, timeout=30, context=ssl._create_unverified_context()) as response:
            return json.loads(response.read().decode("utf-8"))


def request_xml(url: str, mailto: str | None = None) -> ET.Element:
    headers = {"User-Agent": USER_AGENT if not mailto else f"codex-nejm-citation/1.0 (mailto:{mailto})"}
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            return ET.fromstring(response.read())
    except URLError as exc:
        if "CERTIFICATE_VERIFY_FAILED" not in str(exc):
            raise
        with urlopen(req, timeout=30, context=ssl._create_unverified_context()) as response:
            return ET.fromstring(response.read())


def retry(action, retries: int = 2):
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return action()
        except Exception as exc:  # noqa: BLE001
            last = exc
            if attempt < retries:
                time.sleep(min(2 ** attempt, 6))
    if last:
        raise last
    raise RuntimeError("retry exited without result")


def pubmed_search_ids(query: str, args: argparse.Namespace) -> list[str]:
    journal_filter = pubmed_journal_filter(args.scope)
    term = f"({query}) AND ({journal_filter})" if journal_filter else query
    if args.from_year:
        term += f" AND {args.from_year}:3000[dp]"
    if args.to_year:
        lower = args.from_year or 1800
        term += f" AND {lower}:{args.to_year}[dp]"
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": str(args.rows),
        "sort": "relevance",
    }
    if args.email:
        params["email"] = args.email
    if args.api_key:
        params["api_key"] = args.api_key
    url = f"{PUBMED_ESEARCH}?{urlencode(params)}"
    payload = retry(lambda: request_json(url, args.email), args.max_retries)
    return payload.get("esearchresult", {}).get("idlist", [])


def pubmed_fetch(ids: list[str], args: argparse.Namespace) -> list[Candidate]:
    if not ids:
        return []
    params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "xml",
    }
    if args.email:
        params["email"] = args.email
    if args.api_key:
        params["api_key"] = args.api_key
    url = f"{PUBMED_EFETCH}?{urlencode(params)}"
    root = retry(lambda: request_xml(url, args.email), args.max_retries)
    return [candidate_from_pubmed(article, args.scope) for article in root.findall(".//PubmedArticle")]


def text_at(node: ET.Element | None, path: str, default: str = "") -> str:
    if node is None:
        return default
    found = node.find(path)
    if found is None:
        return default
    return clean_text("".join(found.itertext()))


def candidate_from_pubmed(article: ET.Element, scope: str) -> Candidate:
    medline = article.find("MedlineCitation")
    article_node = medline.find("Article") if medline is not None else None
    journal_node = article_node.find("Journal") if article_node is not None else None
    title = text_at(article_node, "ArticleTitle")
    journal = text_at(journal_node, "Title") or text_at(journal_node, "ISOAbbreviation")
    pmid = text_at(medline, "PMID")
    doi = ""
    for article_id in article.findall(".//ArticleId"):
        if article_id.attrib.get("IdType", "").lower() == "doi":
            doi = clean_text(article_id.text or "")
            break
    abstract_parts = [clean_text("".join(node.itertext())) for node in article.findall(".//AbstractText")]
    authors: list[str] = []
    for author in article.findall(".//AuthorList/Author"):
        last = text_at(author, "LastName")
        fore = text_at(author, "ForeName") or text_at(author, "Initials")
        collective = text_at(author, "CollectiveName")
        if collective:
            authors.append(collective)
        elif last and fore:
            authors.append(f"{last}, {fore}")
        elif last:
            authors.append(last)
    year = (
        text_at(journal_node, "JournalIssue/PubDate/Year")
        or text_at(article_node, "ArticleDate/Year")
        or text_at(medline, "DateCompleted/Year")
    )
    month = text_at(journal_node, "JournalIssue/PubDate/Month") or "01"
    day = text_at(journal_node, "JournalIssue/PubDate/Day") or "01"
    y1 = f"{year}/{month}/{day}" if year else ""
    return Candidate(
        title=title,
        journal=journal,
        family=journal_family(journal),
        year=year,
        y1=y1,
        doi=doi,
        pmid=pmid,
        url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
        volume=text_at(journal_node, "JournalIssue/Volume"),
        issue=text_at(journal_node, "JournalIssue/Issue"),
        pages=text_at(article_node, "Pagination/MedlinePgn"),
        issn=text_at(journal_node, "ISSN"),
        authors=authors,
        abstract=" ".join(part for part in abstract_parts if part),
        type="journal-article",
        source_backend="PubMed",
    )


def first(values: list[Any] | None, default: str = "") -> str:
    if not values:
        return default
    return values[0] if isinstance(values[0], str) else default


def date_parts(item: dict[str, Any]) -> list[int]:
    for key in ("published-print", "published-online", "published", "issued"):
        parts = item.get(key, {}).get("date-parts")
        if parts and parts[0]:
            return parts[0]
    return []


def year_from_item(item: dict[str, Any]) -> str:
    parts = date_parts(item)
    return str(parts[0]) if parts else ""


def y1_from_item(item: dict[str, Any]) -> str:
    parts = date_parts(item)
    if not parts:
        return ""
    return f"{parts[0]:04d}/{parts[1] if len(parts) > 1 else 1:02d}/{parts[2] if len(parts) > 2 else 1:02d}"


def author_name(author: dict[str, Any]) -> str:
    family = author.get("family", "").strip()
    given = author.get("given", "").strip()
    return f"{family}, {given}" if family and given else family or given or author.get("name", "")


def candidate_from_crossref(item: dict[str, Any], source_query: str, scope: str) -> Candidate | None:
    journal = first(item.get("container-title"))
    if not journal or not in_scope(journal, scope):
        return None
    page = item.get("page", "") or item.get("article-number", "")
    return Candidate(
        title=clean_text(first(item.get("title"))),
        journal=journal,
        family=journal_family(journal),
        year=year_from_item(item),
        y1=y1_from_item(item),
        doi=item.get("DOI", ""),
        url=item.get("URL", ""),
        volume=item.get("volume", ""),
        issue=item.get("issue", ""),
        pages=page,
        issn=first(item.get("ISSN")),
        authors=[author_name(author) for author in item.get("author", []) if author_name(author)],
        abstract=clean_text(item.get("abstract", "")),
        type=item.get("type", "journal-article"),
        score=float(item.get("score", 0.0) or 0.0),
        source_query=source_query,
        source_backend="Crossref",
    )


def fetch_crossref(query: str, args: argparse.Namespace) -> list[Candidate]:
    filters = ["type:journal-article"]
    if args.from_year:
        filters.append(f"from-pub-date:{args.from_year}-01-01")
    if args.to_year:
        filters.append(f"until-pub-date:{args.to_year}-12-31")
    params = {
        "query.bibliographic": query,
        "rows": str(args.rows),
        "select": "DOI,title,container-title,published,published-print,published-online,issued,author,volume,issue,page,article-number,ISSN,URL,abstract,type,score",
        "filter": ",".join(filters),
        "sort": "relevance",
        "order": "desc",
    }
    if args.email:
        params["mailto"] = args.email
    url = f"{CROSSREF_API}?{urlencode(params)}"
    payload = retry(lambda: request_json(url, args.email), args.max_retries)
    return [
        candidate
        for item in payload.get("message", {}).get("items", [])
        if (candidate := candidate_from_crossref(item, query, args.scope)) is not None
    ]


def fetch_crossref_doi(doi: str, args: argparse.Namespace) -> Candidate | None:
    url = f"{CROSSREF_API}/{quote(doi, safe='')}"
    if args.email:
        url = f"{url}?{urlencode({'mailto': args.email})}"
    payload = retry(lambda: request_json(url, args.email), args.max_retries)
    item = payload.get("message", {})
    return candidate_from_crossref(item, f"doi:{doi}", args.scope)


def fetch_pubmed_doi(doi: str, args: argparse.Namespace) -> list[Candidate]:
    params = {
        "db": "pubmed",
        "term": f'"{doi}"[AID]',
        "retmode": "json",
        "retmax": "5",
    }
    if args.email:
        params["email"] = args.email
    if args.api_key:
        params["api_key"] = args.api_key
    url = f"{PUBMED_ESEARCH}?{urlencode(params)}"
    payload = retry(lambda: request_json(url, args.email), args.max_retries)
    ids = payload.get("esearchresult", {}).get("idlist", [])
    candidates = pubmed_fetch(ids, args)
    return [candidate for candidate in candidates if in_scope(candidate.journal, args.scope)]


def enrich_with_crossref(candidate: Candidate, args: argparse.Namespace) -> Candidate:
    if not candidate.doi:
        return candidate
    enriched = fetch_crossref_doi(candidate.doi, args)
    if not enriched:
        return candidate
    for field in ("title", "journal", "year", "y1", "url", "volume", "issue", "pages", "issn", "abstract"):
        if not getattr(candidate, field) and getattr(enriched, field):
            setattr(candidate, field, getattr(enriched, field))
    if not candidate.authors and enriched.authors:
        candidate.authors = enriched.authors
    if not candidate.family:
        candidate.family = enriched.family
    return candidate


def dedupe(candidates: list[Candidate]) -> list[Candidate]:
    seen: set[str] = set()
    output: list[Candidate] = []
    for candidate in candidates:
        if not candidate.key or candidate.key in seen:
            continue
        seen.add(candidate.key)
        output.append(candidate)
    return output


def search_segment(segment: Segment, args: argparse.Namespace) -> tuple[list[Candidate], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    candidates: list[Candidate] = []
    try:
        ids = pubmed_search_ids(segment.search_query, args)
        candidates.extend(pubmed_fetch(ids, args))
    except Exception as exc:  # noqa: BLE001
        errors.append({"segment_id": segment.id, "backend": "PubMed", "query": segment.search_query, "error": str(exc)})
    if len(candidates) < args.per_segment:
        try:
            candidates.extend(fetch_crossref(segment.search_query, args))
        except Exception as exc:  # noqa: BLE001
            errors.append({"segment_id": segment.id, "backend": "Crossref", "query": segment.search_query, "error": str(exc)})
    scoped = [candidate for candidate in candidates if in_scope(candidate.journal, args.scope)]
    enriched: list[Candidate] = []
    for candidate in dedupe(scoped):
        try:
            enriched.append(enrich_with_crossref(candidate, args))
        except Exception:
            enriched.append(candidate)
    return dedupe(enriched)[: args.per_segment], errors


def build_mapping(segments: list[Segment], args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[Candidate], list[dict[str, str]]]:
    mapping: list[dict[str, Any]] = []
    all_candidates: list[Candidate] = []
    all_errors: list[dict[str, str]] = []
    for segment in segments:
        candidates, errors = search_segment(segment, args)
        all_candidates.extend(candidates)
        all_errors.extend(errors)
        mapping.append(
            {
                "segment": segment,
                "references": candidates,
                "suggested_insert_text": "; ".join(candidate.citation_marker for candidate in candidates[: args.citations_per_segment]),
            }
        )
        if args.sleep:
            time.sleep(args.sleep)
    return mapping, dedupe(all_candidates), all_errors


def build_ris_record(item: Candidate) -> str:
    lines = ["TY  - JOUR"]
    if item.title:
        lines.append(f"TI  - {ris_escape(item.title)}")
    for author in item.authors or []:
        lines.append(f"AU  - {ris_escape(author)}")
    if item.journal:
        lines.append(f"T2  - {ris_escape(item.journal)}")
        lines.append(f"JO  - {ris_escape(item.journal)}")
    if item.year:
        lines.append(f"PY  - {ris_escape(item.year)}")
    if item.y1:
        lines.append(f"Y1  - {ris_escape(item.y1)}")
    if item.volume:
        lines.append(f"VL  - {ris_escape(item.volume)}")
    if item.issue:
        lines.append(f"IS  - {ris_escape(item.issue)}")
    if item.pages:
        lines.append(f"SP  - {ris_escape(item.pages)}")
    if item.doi:
        lines.append(f"DO  - {ris_escape(item.doi)}")
    if item.pmid:
        lines.append(f"AN  - PMID:{ris_escape(item.pmid)}")
    if item.identifier_url:
        lines.append(f"UR  - {ris_escape(item.identifier_url)}")
    if item.issn:
        lines.append(f"SN  - {ris_escape(item.issn)}")
    lines.append("N1  - NEJM-style patient-care candidate is metadata/abstract-screened only.")
    lines.append("ER  -")
    return "\n".join(lines)


def write_ris(candidates: list[Candidate], path: Path) -> None:
    path.write_text("\n\n".join(build_ris_record(item) for item in candidates), encoding="utf-8")


def build_enw_record(item: Candidate) -> str:
    lines = ["%0 Journal Article"]
    if item.title:
        lines.append(f"%T {ris_escape(item.title)}")
    for author in item.authors or []:
        lines.append(f"%A {ris_escape(author)}")
    if item.journal:
        lines.append(f"%J {ris_escape(item.journal)}")
    if item.volume:
        lines.append(f"%V {ris_escape(item.volume)}")
    if item.issue:
        lines.append(f"%N {ris_escape(item.issue)}")
    if item.pages:
        lines.append(f"%P {ris_escape(item.pages)}")
    if item.year:
        lines.append(f"%D {ris_escape(item.year)}")
    if item.issn:
        lines.append(f"%@ {ris_escape(item.issn)}")
    if item.doi:
        lines.append(f"%R {ris_escape(item.doi)}")
    if item.pmid:
        lines.append(f"%M {ris_escape(item.pmid)}")
    if item.identifier_url:
        lines.append(f"%U {ris_escape(item.identifier_url)}")
    return "\n".join(lines)


def write_enw(candidates: list[Candidate], path: Path) -> None:
    path.write_text("\n\n".join(build_enw_record(item) for item in candidates), encoding="utf-8")


def split_author_parts(name: str) -> tuple[str, str]:
    if "," in name:
        family, given = name.split(",", 1)
        return family.strip(), given.strip()
    parts = name.split()
    return (parts[-1], " ".join(parts[:-1])) if len(parts) > 1 else (name, "")


def build_zotero_rdf_article(item: Candidate) -> str:
    lines = [f'    <bib:Article rdf:about={quoteattr(item.article_resource)}>']
    lines.append("        <z:itemType>journalArticle</z:itemType>")
    if item.journal:
        lines.append(f'        <dcterms:isPartOf rdf:resource={quoteattr(item.journal_resource)}/>')
    if item.authors:
        lines.append("        <bib:authors>")
        lines.append("            <rdf:Seq>")
        for author in item.authors:
            family, given = split_author_parts(author)
            lines.append("                <rdf:li><foaf:Person>")
            if family:
                lines.append(f"                    <foaf:surname>{xml_escape(family)}</foaf:surname>")
            if given:
                lines.append(f"                    <foaf:givenName>{xml_escape(given)}</foaf:givenName>")
            lines.append("                </foaf:Person></rdf:li>")
        lines.append("            </rdf:Seq>")
        lines.append("        </bib:authors>")
    if item.title:
        lines.append(f"        <dc:title>{xml_escape(item.title)}</dc:title>")
    if item.y1 or item.year:
        lines.append(f"        <dc:date>{xml_escape(item.y1 or item.year)}</dc:date>")
    if item.identifier_url:
        lines.append("        <dc:identifier><dcterms:URI>")
        lines.append(f"            <rdf:value>{xml_escape(item.identifier_url)}</rdf:value>")
        lines.append("        </dcterms:URI></dc:identifier>")
    if item.doi:
        lines.append(f"        <dc:identifier>{xml_escape(f'DOI {item.doi}')}</dc:identifier>")
    if item.pmid:
        lines.append(f"        <dc:identifier>{xml_escape(f'PMID {item.pmid}')}</dc:identifier>")
    if item.pages:
        lines.append(f"        <bib:pages>{xml_escape(item.pages)}</bib:pages>")
    lines.append("    </bib:Article>")
    return "\n".join(lines)


def build_zotero_rdf_journal(item: Candidate) -> str:
    lines = [f'    <bib:Journal rdf:about={quoteattr(item.journal_resource)}>']
    if item.journal:
        lines.append(f"        <dc:title>{xml_escape(item.journal)}</dc:title>")
    if item.volume:
        lines.append(f"        <prism:volume>{xml_escape(item.volume)}</prism:volume>")
    if item.issue:
        lines.append(f"        <prism:number>{xml_escape(item.issue)}</prism:number>")
    if item.issn:
        lines.append(f"        <dc:identifier>{xml_escape(f'ISSN {item.issn}')}</dc:identifier>")
    lines.append("    </bib:Journal>")
    return "\n".join(lines)


def write_zotero_rdf(candidates: list[Candidate], path: Path) -> None:
    root_open = [
        "<rdf:RDF",
        *(f' xmlns:{prefix}="{uri}"' for prefix, uri in ZOTERO_RDF_NS.items()),
        ">",
    ]
    journal_blocks: dict[str, str] = {}
    article_blocks = []
    for item in candidates:
        article_blocks.append(build_zotero_rdf_article(item))
        journal_blocks.setdefault(item.journal_resource, build_zotero_rdf_journal(item))
    path.write_text("\n".join(["".join(root_open), *article_blocks, *journal_blocks.values(), "</rdf:RDF>"]), encoding="utf-8")


def write_export(candidates: list[Candidate], path: Path, export_format: str) -> None:
    if export_format == "ris":
        write_ris(candidates, path)
    elif export_format == "zotero-rdf":
        write_zotero_rdf(candidates, path)
    else:
        write_enw(candidates, path)


def write_artifacts(mapping: list[dict[str, Any]], references: list[Candidate], outdir: Path, output_path: Path, args: argparse.Namespace, errors: list[dict[str, str]]) -> None:
    stem = output_path.stem or "nejm_references"
    payload = {
        "scope": args.scope,
        "reference_style": "Vancouver/AMA",
        "segment_count": len(mapping),
        "reference_count": len(references),
        "segments": [
            {
                **entry["segment"].as_dict(),
                "suggested_insert_text": entry["suggested_insert_text"],
                "references": [candidate.as_dict() for candidate in entry["references"]],
            }
            for entry in mapping
        ],
        "references": [candidate.as_dict() for candidate in references],
        "errors": errors,
        "notes": [
            "Candidates are metadata/abstract-screened only.",
            "Use full text, guideline text, or registry records before citing as definitive support.",
            "Vancouver/AMA style is the default medical-journal reporting style.",
        ],
    }
    (outdir / f"{stem}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = ["segment_id", "segment_text", "suggested_insert_text", "title", "journal", "family", "year", "doi", "pmid", "url", "authors", "screening_note"]
    with (outdir / f"{stem}.tsv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for entry in mapping:
            segment: Segment = entry["segment"]
            if not entry["references"]:
                writer.writerow({"segment_id": segment.id, "segment_text": segment.text, "screening_note": "No in-scope candidate found."})
            for candidate in entry["references"]:
                writer.writerow(
                    {
                        "segment_id": segment.id,
                        "segment_text": segment.text,
                        "suggested_insert_text": entry["suggested_insert_text"],
                        "title": candidate.title,
                        "journal": candidate.journal,
                        "family": candidate.family,
                        "year": candidate.year,
                        "doi": candidate.doi,
                        "pmid": candidate.pmid,
                        "url": candidate.identifier_url,
                        "authors": "; ".join(candidate.authors[:8] if candidate.authors else []),
                        "screening_note": "metadata/abstract-screened only",
                    }
                )
    lines = [
        "# NEJM Citation Report",
        "",
        f"- Scope: `{args.scope}`",
        "- Reference style: Vancouver/AMA",
        f"- Segments: {len(mapping)}",
        f"- Unique references exported: {len(references)}",
        "- Screening status: metadata/abstract-screened only",
        "",
    ]
    for entry in mapping:
        segment: Segment = entry["segment"]
        lines.extend([f"## {segment.id}", "", segment.text, ""])
        if not entry["references"]:
            lines.extend(["- No in-scope candidate found.", ""])
            continue
        for idx, candidate in enumerate(entry["references"], 1):
            link = candidate.identifier_url
            lines.append(f"{idx}. {candidate.title}. *{candidate.journal}*. {candidate.year}. {link}")
            lines.append(f"   - Family: {candidate.family or 'unclassified'}; PMID: {candidate.pmid or 'none'}; DOI: {candidate.doi or 'none'}")
            lines.append("   - Support: metadata/abstract-screened only")
        lines.append("")
    (outdir / f"{stem}.md").write_text("\n".join(lines), encoding="utf-8")
    html_cards = []
    for entry in mapping:
        segment: Segment = entry["segment"]
        refs = "".join(
            f"<li><strong>{html.escape(candidate.title)}</strong><br>{html.escape(candidate.journal)} {html.escape(candidate.year)}<br><a href=\"{html.escape(candidate.identifier_url)}\">{html.escape(candidate.identifier_url)}</a></li>"
            for candidate in entry["references"]
        )
        html_cards.append(f"<section><h2>{html.escape(segment.id)}</h2><p>{html.escape(segment.text)}</p><ol>{refs or '<li>No in-scope candidate found.</li>'}</ol></section>")
    (outdir / f"{stem}.html").write_text(
        "<!doctype html><html><head><meta charset='utf-8'><title>NEJM Citation Report</title></head><body>"
        "<h1>NEJM Citation Report</h1><p>Screening status: metadata/abstract-screened only.</p>"
        + "\n".join(html_cards)
        + "</body></html>",
        encoding="utf-8",
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PubMed-grounded medical evidence citation search and export.")
    parser.add_argument("--text", action="append", help="Medical manuscript text to segment. Can be repeated.")
    parser.add_argument("--text-file", help="UTF-8 text file.")
    parser.add_argument("--claim", action="append", help="Single patient-care claim. Can be repeated.")
    parser.add_argument("--claim-file", help="UTF-8 file with one claim per line.")
    parser.add_argument("--doi", action="append", help="Known DOI to fetch and export. Can be repeated.")
    parser.add_argument("--doi-file", help="UTF-8 file with one DOI per line.")
    parser.add_argument("--scope", choices=SCOPE_CHOICES, default=DEFAULT_SCOPE)
    parser.add_argument("--output-file", help="Reference output path ending in .enw, .ris, or .rdf.")
    parser.add_argument("--outdir", help="Output directory. Defaults to output file parent or current directory.")
    parser.add_argument("--format", choices=EXPORT_FORMAT_CHOICES, help="Export format. Inferred from output suffix if omitted.")
    parser.add_argument("--with-artifacts", action="store_true", help="Also generate JSON, TSV, Markdown, and HTML review artifacts.")
    parser.add_argument("--rows", type=int, default=20, help="Candidate rows per segment before filtering.")
    parser.add_argument("--per-segment", type=int, default=3, help="Maximum references kept per segment.")
    parser.add_argument("--citations-per-segment", type=int, default=2, help="Markers included in suggested insert text.")
    parser.add_argument("--segment-chars", type=int, default=700, help="Split long paragraphs above this length.")
    parser.add_argument("--max-candidates", type=int, default=80, help="Maximum deduplicated references exported.")
    parser.add_argument("--max-segments", type=int, help="Limit processed segments.")
    parser.add_argument("--max-retries", type=int, default=2, help="Retry count for PubMed/Crossref requests.")
    parser.add_argument("--from-year", type=int, help="Earliest publication year.")
    parser.add_argument("--to-year", type=int, help="Latest publication year.")
    parser.add_argument("--email", help="Email for NCBI/Crossref polite use.")
    parser.add_argument("--api-key", help="NCBI API key.")
    parser.add_argument("--sleep", type=float, default=0.34, help="Seconds between segment searches.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    segments = build_segments(args)
    dois = read_dois(args)
    if args.max_segments and args.max_segments > 0:
        segments = segments[: args.max_segments]
    if not segments and not dois:
        print("Provide --text, --text-file, --claim, --claim-file, --doi, or --doi-file.", file=sys.stderr)
        return 2

    output_path = Path(args.output_file).expanduser().resolve() if args.output_file else None
    outdir = Path(args.outdir).expanduser().resolve() if args.outdir else (output_path.parent if output_path else Path.cwd().resolve())
    outdir.mkdir(parents=True, exist_ok=True)
    export_format = normalize_export_format(args.format) if args.format else infer_export_format(output_path)
    if output_path is None:
        output_path = outdir / export_filename(export_format)

    mapping, segment_candidates, errors = build_mapping(segments, args)
    doi_candidates: list[Candidate] = []
    for doi in dois:
        pubmed_candidates: list[Candidate] = []
        try:
            pubmed_candidates = fetch_pubmed_doi(doi, args)
        except Exception as exc:  # noqa: BLE001
            errors.append({"doi": doi, "backend": "PubMed", "error": str(exc)})
        if pubmed_candidates:
            doi_candidates.extend(enrich_with_crossref(candidate, args) for candidate in pubmed_candidates)
            continue
        try:
            candidate = fetch_crossref_doi(doi, args)
            if candidate:
                doi_candidates.append(candidate)
        except Exception as exc:  # noqa: BLE001
            errors.append({"doi": doi, "backend": "Crossref", "error": str(exc)})
    references = dedupe([*segment_candidates, *doi_candidates])[: args.max_candidates]

    write_export(references, output_path, export_format)
    if args.with_artifacts:
        write_artifacts(mapping, references, outdir, output_path, args, errors)

    print(f"Reference output: {output_path}")
    print(f"Export format: {export_format} ({export_label(export_format)})")
    print(f"Scope: {args.scope}")
    print(f"Unique references exported: {len(references)}")
    if errors:
        print(f"Retrieval warnings: {len(errors)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
