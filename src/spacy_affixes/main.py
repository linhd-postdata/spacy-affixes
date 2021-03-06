# -*- coding: utf-8 -*-
"""Main module."""
import re

from spacy.matcher import Matcher
from spacy.tokens import Token

from .utils import AFFIXES_SUFFIX
from .utils import get_morfo
from .utils import load_affixes
from .utils import load_lexicon
from .utils import token_transform


class AffixesMatcher(object):

    def __init__(self, nlp, rules=None, lexicon=None, split_on=None,
                 replace_lemmas=True):
        """
        :param nlp: SpaCy NLP object with the language already loaded
        :param rules: Dictionary of rules for affixes handling. Each dict
                      uses a key that contains the pattern to match and the
                      value is a list of dicts with the corresponding rule
                      parameters::
                      - pattern: Regular expression to match, (ex. `r"ito$"`)
                                 If a match is found, it gets removed from the
                                 token
                      - kind: `AFFIXES_SUFFIX` or `AFFIXES_PREFIX`
                      - pos_re: EAGLE regular expression to match, (ex. `r"V"`)
                      - strip_accent: Boolean indicating whether accents should
                                      be stripped in order to find the rest
                                      of the token in the lexicon,
                      - affix_add: List of strings to add to the rest of the
                                   token to find it in the lexicon. Each
                                   element in the list is tried separately, as
                                   in an OR condition. The character `*` means
                                   add nothing (ex. ["*", "io"])
                      - affix_text: List of Strings with the text to the rest
                                    of the token as individual tokens. For
                                    example, a rule for `dígamelo` might have
                                    ["me", "lo"] as its `affix_text`
                      It defaults to Freeling if installed (environment
                      variable `FREELINGDIR` should be set) or downloaded using
                      `python -m spacy_affixes download <lang> [version]`.
                      Please, check the Freeling site to see license
                      compatibilities.
        :param lexicon: Dictionary keyed by word with values for lemma,
                        EAGLE code, UD POS, and UD Tags. It defaults to
                        Freeling if installed (environment
                        variable `FREELINGDIR` should be set) or downloaded
                        using
                        `python -m spacy_affixes download <lang> [version]`.
                        Please, check the Freeling site to see license
                        compatibilities.
        :param split_on: Tuple of UD POS to split tokens on. Defaults to
                         verbs. A `*` means split whenever possible.
        :param replace_lemmas: Boolean specifying whether the lemma should be
                               replaced with the output of the Freeling rules
        """
        self.nlp = nlp
        self.rules = load_affixes() if rules is None else rules
        self.lexicon = load_lexicon() if lexicon is None else lexicon
        self.split_on = ("VERB", ) if split_on is None else split_on
        try:
            lemma_lookup = self.nlp.vocab.lookups.get_table("lemma_lookup")
        except (AttributeError, KeyError):
            # If no lemma_lookup is found, create an empty one
            lemma_lookup = {}
        self.lemma_lookup = lemma_lookup
        self.replace_lemmas = replace_lemmas
        if None in (self.lexicon, self.rules):
            raise ValueError("""
            Data for affixes rules or lexicon data is missing. Check
            that Freeling is installed and its environment
            variable `FREELINGDIR` is set), or that you have downloaded the
            neccessary files using
            `python -m spacy_affixes download <lang> [version]`.
            Please, check the Freeling site to see license
            compatibilities.
            """)
        if not Token.has_extension("has_affixes"):
            Token.set_extension("has_affixes", default=False)
            Token.set_extension("affixes_kind", default=None)
            Token.set_extension("affixes_lemma", default=None)
            Token.set_extension("affixes_length", default=0)
            Token.set_extension("affixes_rule", default=None)
            Token.set_extension("affixes_text", default=None)
        self.matcher = Matcher(nlp.vocab)
        for rule_key, rules in self.rules.items():
            for rule in rules:
                self.matcher.add(rule_key, None, [
                    {"TEXT": {"REGEX": fr"(?i){rule['pattern']}"}},
                    # It'd be nice if we could check regex AND minimum length
                    # {"LENGTH": {">": len(rule_key)}},
                ])

    def apply_rules(self, retokenizer, token, rule):
        if (rule["always_apply"]
                or (token.is_oov or token not in self.lexicon)) is False:
            return
        strip_accent_exceptions = (
            "automática",
        )
        for affix_add in rule["affix_add"]:
            strip_accent = rule["strip_accent"]
            token_sub = re.sub(rule["pattern"], '', token.text)
            token_left = token_transform(
                token_sub,
                affix_add,
                False if token_sub in strip_accent_exceptions else strip_accent
            )
            morfo_lemma_opts = {
                "affix_text": "".join(rule["affix_text"]),
                "token_lower": token.lower_,
                "token_left": token_left,
            }
            morfo = get_morfo(
                token_left.lower(),
                self.lexicon,
                re.compile(rule["pos_re"], re.I),
                rule["assign_pos"],
                rule["assign_lemma"],
                **morfo_lemma_opts
            )
            if token_left and morfo and not token._.has_affixes:
                _, token_ud, token_tags, token_lemma = morfo
                affixes_length = (
                    len(rule["affix_text"]) or int(affix_add != "")
                )
                if rule["kind"] == AFFIXES_SUFFIX:
                    heads = [(token, 1)] + (affixes_length * [(token, 0)])
                    token.lemma_ = self.lemma_lookup.get(
                        token_left.lower(),
                        token_lemma
                    )
                else:
                    heads = (affixes_length * [(token, 0)]) + [(token, 1)]
                if "*" in self.split_on or token_ud in self.split_on:
                    if rule["kind"] == AFFIXES_SUFFIX:
                        retokenizer.split(
                            token, [token_sub, *rule["affix_text"]], heads
                        )
                    else:
                        retokenizer.split(
                            token, [*rule["affix_text"], token_sub], heads
                        )
                token.pos_ = token_ud
                if token_tags:
                    token.tag_ = token_tags
                token._.affixes_text = token_left
                token._.affixes_kind = rule["kind"]
                token._.affixes_length = affixes_length
                token._.affixes_lemma = token.lemma_
                token._.has_affixes = True

    def __call__(self, doc):
        matches = self.matcher(doc)
        tokens = []
        for match_id, start, end in matches:
            match_key = self.nlp.vocab.strings[match_id]
            for token in doc[start:end]:
                token._.affixes_rule = match_key
                tokens.append(token)
        with doc.retokenize() as retokenizer:
            for token in tokens:
                if token._.affixes_rule:
                    for rule in self.rules[token._.affixes_rule]:
                        self.apply_rules(retokenizer, token, rule)
                if not token._.has_affixes:
                    token._.affixes_rule = None
        if self.replace_lemmas:
            # Tokens are views of C structs
            for index, _ in enumerate(doc):
                if doc[index]._.has_affixes and doc[index]._.affixes_lemma:
                    doc[index].lemma_ = doc[index]._.affixes_lemma
        return doc
