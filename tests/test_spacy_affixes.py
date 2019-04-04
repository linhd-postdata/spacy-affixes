#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `spacy_affixes` package."""
import pytest
import spacy

from spacy_affixes import AffixesMatcher
from spacy_affixes.utils import download


@pytest.fixture
def nlp():
    lang = "es"
    download(lang)
    nlp_ = spacy.load(lang)
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
