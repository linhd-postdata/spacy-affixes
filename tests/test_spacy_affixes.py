#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `spacy_affixes` package."""
import pytest
import spacy

from spacy_affixes import AffixesMatcher
from spacy_affixes.utils import download
from spacy_affixes.utils import eagle2tag

download("es")


@pytest.fixture
def nlp():
    nlp_ = spacy.load("es")
    if nlp_.has_pipe("affixes"):
        nlp_.remove_pipe("affixes")
    return nlp_


def test_split_on_all(snapshot, nlp):
    affixes_matcher = AffixesMatcher(nlp, split_on='*')
    nlp.add_pipe(affixes_matcher, name="affixes", before="tagger")
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
    output = 'X'
    assert eagle2tag('WHATEVER') == output


def test_get_morfo_rules(snapshot, nlp):
    affixes_matcher = AffixesMatcher(nlp)
    nlp.add_pipe(affixes_matcher, name="affixes", before="tagger")
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
    affixes_matcher = AffixesMatcher(nlp, split_on=["VERB"])
    nlp.add_pipe(affixes_matcher, name="affixes", before="tagger")
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
    affixes_matcher = AffixesMatcher(nlp, split_on=[])
    nlp.add_pipe(affixes_matcher, name="affixes", before="tagger")
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
