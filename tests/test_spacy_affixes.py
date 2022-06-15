#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `spacy_affixes` package."""
import json
from pathlib import Path

import pytest
import spacy
from spacy.language import Language
from spacy_affixes import AffixesMatcher
from spacy_affixes.utils import download
from spacy_affixes.utils import eagle2tag
from spacy_affixes.eagles import eagles2ud

download("es")


@pytest.fixture
def nlp():
    nlp_ = spacy.load("es_core_news_sm")
    if nlp_.has_pipe("affixes"):
        nlp_.remove_pipe("affixes")  # pragma: no cover
    return nlp_


@pytest.fixture
def test_eagles():
    return json.loads(
        Path("tests/fixtures/test_eagles.json").read_text())


def test_split_on_all(snapshot, nlp):
    Language.component("affixes", func=AffixesMatcher(nlp, split_on='*'))
    nlp.add_pipe("affixes", before="morphologizer")
    docs = (
        "Cuéntamelo bien y dilo claro, no me des un caramelo.",
        "Yo mismamente podría hacérselo despacito.",
        "Soy hispanoamericano y antirrevolucionario.",
        "Dime el número de teléfono.",
        "Hay que hacérselo todo.",
    )
    for doc in docs:
        snapshot.assert_match([
            [
                token.text,
                token.lemma_,
                token.pos_,
                token.tag_,
                token._.has_affixes,
                token._.affixes_rule,
                token._.affixes_kind,
                token._.affixes_text,
                token._.affixes_length,
            ] for token in nlp(doc)])


def test_eagle2tag():
    output = 'NOUN__Gender=Masc|Number=Sing'
    assert eagle2tag('NCMS000') == output


def test_eagle2tag_not_in_dict():
    output = 'X__X'
    assert eagle2tag('WHATEVER') == output


def test_get_morfo_rules(snapshot, nlp):
    Language.component("affixes", func=AffixesMatcher(nlp))
    nlp.add_pipe("affixes", before="morphologizer")
    docs = (
        ("antitabaco", "antitabaco"),
        ("dímelo", "decir"),
        # 'acabado' should be the lemma
        ("acabadísimo", "acabar"),
        # 'rápidamente' should be the lemma
        ("rapidísimamente", "rapidísimamente"),
        ("automáticamente", "automático"),
        # ("afro-americano", "afroamericano"),
        # ("anglo-sajón", "anglosajón"),
        # ("anti-revolucionario", "antirrevolucionario"),
        # ("franco-suizo", "francosuizo"),
        # ("hispano-americano", "hispanioamericano"),
        # ("hispano-ruso", "hispanorruso"),
    )
    for doc, lemma in docs:
        assert nlp(doc)[0].lemma_ == lemma


def test_split_on_verbs(snapshot, nlp):
    Language.component("affixes", func=AffixesMatcher(nlp, split_on=["VERB"]))
    nlp.add_pipe("affixes", before="morphologizer")
    docs = (
        "Cuéntamelo bien y dilo claro, no me des un caramelo.",
        "Yo mismamente podría hacérselo despacito.",
        "Soy hispanoamericano y antirrevolucionario.",
        "Dime el número de teléfono.",
        "Hay que hacérselo todo.",
    )
    for doc in docs:
        snapshot.assert_match([[
            token.text,
            token.lemma_,
            token._.has_affixes,
            token._.affixes_rule,
            token._.affixes_kind,
            token._.affixes_text,
            token._.affixes_length,
        ] for token in nlp(doc)])


def test_accent_exceptions(snapshot, nlp):
    Language.component("affixes", func=AffixesMatcher(nlp, split_on=[]))
    nlp.add_pipe("affixes", before="morphologizer")
    docs = (
        "Ese hombre está demente",
        "automáticamente",
        "mágicamente",
        "antirrevolucionariamente",
    )
    for doc in docs:
        snapshot.assert_match([[
            token.text,
            token.lemma_,
            token._.has_affixes,
            token._.affixes_rule,
            token._.affixes_kind,
            token._.affixes_text,
            token._.affixes_length,
        ] for token in nlp(doc)])


def test_eagles2ud_dict(test_eagles):
    for idx, eagle in enumerate(test_eagles):
        res = eagles2ud(eagle).split("__")
        output = set(res[1].split("|"))
        res_test = set(test_eagles[eagle]["Tag"].split("|"))
        assert output == res_test


def test_spacy_affixes_no_lemma_lookup():
    nlp = spacy.load('es_core_news_sm')  # noqa
    Language.component("affixes", func=AffixesMatcher(nlp, split_on=[]))
    nlp.add_pipe("affixes", before="morphologizer")
    nlp.vocab.lookups.remove_table("lemma_lookup")
    nlp("Ese hombre está demente")
    assert True
