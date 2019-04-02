import json
import os
import re
import sys
import unicodedata
from collections import defaultdict
from urllib.request import urlopen


AFFIXES_SUFFIX = "suffix"
AFFIXES_PREFIX = "prefix"
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FREELING_DIR = os.environ.get("FREELINGDIR") or os.environ.get("FREELINGSHARE")


def download(lang, version=None):
    version = version if version is not None else "4.1"
    affixes = download_affixes(lang, version)
    write_affixes(lang, version, affixes)
    lexicon = download_lexicon(lang, version)
    write_lexicon(lang, version, lexicon)


def write_affixes(lang, version, affixes):
    affixes_filename = f"affixes-{lang}-{version}.json"
    with open(os.path.join(DATA_DIR, affixes_filename), "w") as dump:
        json.dump(affixes, dump)


def write_lexicon(lang, version, lexicon):
    lexicon_filename = f"lexicon-{lang}-{version}.json"
    with open(os.path.join(DATA_DIR, lexicon_filename), "w") as dump:
        json.dump(lexicon, dump)


def load_affixes(lang="es", version="4.1"):
    affixes_filename = f"affixes-{lang}-{version}.json"
    affixes_path = os.path.join(DATA_DIR, affixes_filename)
    if not os.path.isfile(affixes_path):
        if FREELING_DIR:
            affixes_raw_path = os.path.join(FREELING_DIR, lang, "affixos.dat")
            with open(affixes_raw_path, "r") as affixes_raw:
                affixes = build_affixes(affixes_raw)
                write_affixes(lang, version, affixes)
                return affixes
        else:
            raise ValueError("""
            Data for affixes rules is missing. Check
            that Freeling is installed and its environment
            variable `FREELINGDIR` is set), or that you have downloaded the
            neccessary files using
            `python -m spacy_affixes download <lang> [version]`.
            Please, check the Freeling site to see license
            compatibilities.
            """)
    else:
        with open(affixes_path, "r") as dump:
            return json.load(dump)


def load_lexicon(lang="es", version="4.1"):
    lexicon_filename = f"lexicon-{lang}-{version}.json"
    lexicon_path = os.path.join(DATA_DIR, lexicon_filename)
    if not os.path.isfile(lexicon_path):
        if FREELING_DIR:
            lexicon_raw_path = os.path.join(FREELING_DIR, lang, "dicc.src")
            with open(lexicon_raw_path, "r") as lexicon_raw:
                lexicon = build_lexicon(lexicon_raw)
                write_lexicon(lang, version, lexicon)
                return lexicon
        else:
            raise ValueError("""
            Data for lexicon data is missing. Check
            that Freeling is installed and its environment
            variable `FREELINGDIR` is set), or that you have downloaded the
            neccessary files using
            `python -m spacy_affixes download <lang> [version]`.
            Please, check the Freeling site to see license
            compatibilities.
            """)
    else:
        with open(lexicon_path, "r") as dump:
            return json.load(dump)


def download_affixes(lang="es", version="4.1"):
    sys.stdout.write(f"Downloading affixes {lang}-{version}...\n")
    url = (f"https://raw.githubusercontent.com/TALP-UPC/FreeLing/"
           f"{version}/data/{lang}/afixos.dat")
    affixes_raw = urlopen(url).read().decode('utf-8')
    return build_affixes(affixes_raw)


def build_affixes(affixes_raw):
    re_flags = re.S | re.M | re.I
    prefixes_re = re.compile(r'<Prefixes.*>(.*)</Prefixes>', re_flags)
    suffixes_re = re.compile(r'<Suffixes.*>(.*)</Suffixes>', re_flags)
    prefixes = prefixes_re.search(affixes_raw).groups()[0].strip().split("\n")
    suffixes = suffixes_re.search(affixes_raw).groups()[0].strip().split("\n")
    affixes_rules = [(prefixes, AFFIXES_PREFIX, r"^{}"),
                     (suffixes, AFFIXES_SUFFIX, r"{}$")]
    affixes_dict = defaultdict(list)
    for (affixes, affix_kind, affix_pos_re) in affixes_rules:
        for affix in affixes:
            if len(affix.strip()) > 0 and not affix.startswith("#"):
                affix_split = re.split(r"\s+", affix)
                key, add, pos_re, _, strip_accent, *_, tokens = affix_split
                add = add if add != "*" else ""
                strip_accent = int(strip_accent) == 0
                if tokens == "-":
                    text = [key]
                else:
                    text = tokens.split(":")[0].split("+")[1:]
                rule = {
                    "pattern": affix_pos_re.format(key),
                    "kind": affix_kind,
                    "pos_re": fr"{pos_re}",
                    "strip_accent": strip_accent,
                    "affix_add": add.split("|"),
                    "affix_text": text,
                }
                affixes_dict[f"{affix_kind}_{key}"].append(rule)
    return affixes_dict


def strip_accents(string):
    return ''.join(char for char in unicodedata.normalize('NFD', string)
                   if (unicodedata.category(char) != 'Mn'
                       or unicodedata.name(char) == 'COMBINING TILDE'))


def eagle2tag(eagle):
    """Transform an EAGLE tag into UD features"""
    # TODO
    return ""


def eagle2pos(eagle):
    mapper = {
        "A": "ADJ",
        "R": "ADV",
        "D": "DET",
        "N": "NOUN",
        "V": "VERB",
        "P": "PRON",
        "C": "CONJ",
        "I": "INTJ",
        "S": "ADP",
        "F": "PUNCT",
        "Z": "NUM",
        "W": "NUM",  # Dates (W) are not standard EAGLE
    }
    return mapper.get(eagle[0], "X")


def token_transform(string, kind, add, strip_accent):
    if add == AFFIXES_PREFIX:
        prefix, suffix = add, ""
    else:
        prefix, suffix = "", add
    if add and strip_accent:
        transform = f"{prefix}{strip_accents(string)}{suffix}"
    elif add and not strip_accent:
        transform = f"{prefix}{string}{suffix}"
    elif not add and strip_accent:
        transform = strip_accents(string)
    else:
        transform = string
    return transform


def download_lexicon(lang="es", version="4.1"):
    sys.stdout.write(f"Downloading lexicon {lang}-{version}...\n")
    url = (f"https://raw.githubusercontent.com/TALP-UPC/FreeLing/"
           f"{version}/data/{lang}/dictionary/entries/MM.{{category}}")
    # Categories and Universal Dependency (UD) equivalent. None to auto-detect
    categories = (
        ("adj", "ADJ"),
        ("adv", "ADV"),
        ("int", "INTJ"),
        ("nom", "NOUN"),
        ("vaux", "AUX"),
        ("verb", "VERB"),
        ("tanc", None),
    )
    lexicon = defaultdict(list)
    for category, ud in categories:
        download_url = url.format(category=category)
        for line in urlopen(download_url).read().decode('utf-8').split("\n"):
            if len(line.strip()) == 0:
                continue
            word, lemma, eagle = line.split()
            lexicon[word].append({
                'lemma': lemma,
                'eagle': eagle,
                'ud': ud or eagle2pos(eagle),
                'tags': eagle2tag(eagle),
            })
    return lexicon


def build_lexicon(lexicon_raw):
    lexicon = defaultdict(list)
    for line in lexicon_raw.decode('utf-8').split("\n"):
        word, lemma, eagle = line.split()
        lexicon[word].append({
            'lemma': lemma,
            'eagle': eagle,
            'ud': eagle2pos(eagle),
            'tags': eagle2tag(eagle),
        })
    return lexicon


def get_morfo(string, lexicon, regex):
    # Checks for string in the lexicon
    # Returns EAGLE, UD, tags, lemma
    if string in lexicon:
        entry = lexicon[string]
        for definition in entry:
            if regex.match(definition["eagle"]):
                return (
                    definition["eagle"],
                    definition["ud"],
                    definition["tags"],
                    definition["lemma"]
                )
    return None
