import json
import os
import re
import sys
import unicodedata
from collections import defaultdict
from urllib.request import urlopen
from .eagles import eagles2ud

AFFIXES_SUFFIX = "suffix"
AFFIXES_PREFIX = "prefix"
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FREELING_DIR = os.environ.get("FREELINGDIR") or os.environ.get("FREELINGSHARE")


def download(lang, version=None):
    version = version if version is not None else "4.2"
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


def load_affixes(lang="es", version="4.2"):
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


def load_lexicon(lang="es", version="4.2"):
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


def download_affixes(lang="es", version="4.2"):
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
                (key, add, pos_re, assign_pos, strip_accent,
                 *_, assign_lemma, always_apply, tokens) = affix_split
                add = add if add != "*" else ""
                assign_pos = assign_pos if assign_pos != "*" else ""
                strip_accent = int(strip_accent) == 0
                always_apply = int(always_apply) == 1
                if tokens == "-":
                    text = [key]
                else:
                    text = tokens.split(":")[0].split("+")[1:]
                rule = {
                    "pattern": affix_pos_re.format(key),
                    "kind": affix_kind,
                    "pos_re": fr"{pos_re}",
                    "assign_pos": assign_pos,
                    "strip_accent": strip_accent,
                    "assign_lemma": assign_lemma,
                    "always_apply": always_apply,
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
    """
    Transform an EAGLES tag into UD features
    :param eagle: EAGLES tag to be converted
    :return: Equivalent UD tag
    """
    tag = eagles2ud(eagle)
    return tag if tag != '' else 'X__'


def eagle2pos(eagle):
    pos = eagles2ud(eagle).split('__')[0]
    return pos


def token_transform(string, add, strip_accent):
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


def download_lexicon(lang="es", version="4.2"):
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
                'tags': eagle2tag(eagle).split("__")[1],
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
            'tags': eagle2tag(eagle).split("__")[1],
        })
    return lexicon


def get_assigned_lemma(rule, **opts):
    ralf = {
        "R": opts["token_left"],
        "A": opts["affix_text"],
        "L": opts["lemma"],
        "F": opts["token_lower"],
    }
    return "".join([ralf.get(opt, opt) for opt in rule.split("+")])


def get_morfo(string, lexicon, regex, assign_pos, assign_lemma,
              **assign_lemma_opts):
    # Checks for string in the lexicon
    # Returns EAGLE, UD, tags, lemma
    if string in lexicon:
        entry = lexicon[string]
        for definition in entry:
            if regex.match(definition["eagle"]):
                assign_lemma_opts.update({
                    "lemma": definition["lemma"]
                })
                lemma = get_assigned_lemma(assign_lemma, **assign_lemma_opts)
                if assign_pos:
                    return (
                        assign_pos,
                        eagle2pos(assign_pos),
                        eagle2tag(assign_pos).split('__')[1],
                        lemma
                    )
                else:
                    return (
                        definition["eagle"],
                        definition["ud"],
                        definition["tags"],
                        lemma
                    )
    return None
