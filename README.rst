=============
SpaCy Affixes
=============


.. image:: https://img.shields.io/pypi/v/spacy-affixes.svg
        :target: https://pypi.python.org/pypi/spacy-affixes

.. image:: https://img.shields.io/travis/linhd-postdata/spacy-affixes.svg
        :target: https://travis-ci.org/linhd-postdata/spacy-affixes

.. image:: https://readthedocs.org/projects/spacy-affixes/badge/?version=latest
        :target: https://spacy-affixes.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


SpaCy support for affixes splitting for Freeling-like affixes rules and dictionaries.


* Free software: Apache Software License 2.0
* Documentation: https://spacy-affixes.readthedocs.io.


Usage
-----
This library was born to split clitics from verbs so POS tagging works out-of-the-box with spaCy models.

.. code-block:: python

    from spacy_affixes import AffixesMatcher
    nlp = spacy.load("es")
    affixes_matcher = AffixesMatcher(nlp, split_on=["VERB"])
    nlp.add_pipe(affixes_matcher, name="affixes", before="tagger")
    for token in nlp("Yo mismamente podría hacérselo bien."):
        print(
            token.text,
            token.lemma_,
            token.pos_,
            token.tag_,
            token._.has_affixes,
            token._.affixes_rule,
            token._.affixes_kind,
            token._.affixes_text,
            token._.affixes_length,
        )

The output will be

.. code-block:: text

    Hay Hay AUX AUX__Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin False None None None 0
    que que SCONJ SCONJ___ False None None None 0
    hacér hacer VERB  True suffix_selo suffix hacer 2
    se se PRON PRON__Person=3 False None None None 0
    lo el PRON PRON__Case=Acc|Gender=Masc|Number=Sing|Person=3|PronType=Prs False None None None 0
    todo todo PRON PRON__Gender=Masc|Number=Sing|PronType=Ind False prefix_todo None None 0
    , , PUNCT PUNCT__PunctType=Comm False None None None 0
    y y CONJ CCONJ___ False None None None 0
    rápidamente rápidamente ADV ADV___ False suffix_mente None None 0
    además además ADV ADV___ False prefix_a None None 0
    . . PUNCT PUNCT__PunctType=Peri False None None None 0

However, words with suffixes could also be split if needed, or virtually any word for which a rule matches,
just by passing a list of Universal Dependency POS's to the argument :code:`split_on`. Passing in :code:`split_on="*"` would make :code:`AffixesMatcher()` try to split on everything it finds.

Rules and Lexicon
-----------------
Due to licensing issues, :code:`spacy-affixes` comes with no rules nor lexicons by default. There are two ways of getting data into :code:`spacy-affixes`:

1. Create the rules and lexicon yourself with the entities you are interested on, and pass them in using  :code:`AffixesMatcher(nlp, rules=<rules>, dictionary=<dictionary>)`. The format for these is as follows.

    - rules: Dictionary of rules for affixes handling. Each dict uses a key that contains the pattern to match and the value is a list of dicts with the corresponding rule parameters:
        
      - pattern: Regular expression to match, (ex. :code:`r"ito$"`) If a match is found, it gets removed from the token
      - kind: :code:`AFFIXES_SUFFIX` or :code:`AFFIXES_PREFIX`
      - pos_re: EAGLE regular expression to match, (ex. :code:`r"V"`)
      - strip_accent: Boolean indicating whether accents should be stripped in order to find the rest of the token in the lexicon
      - affix_add: List of strings to add to the rest of the token to find it in the lexicon. Each element in the list is tried separately, as in an OR condition. The character :code:`*` means add nothing (ex. :code:`["*", "io"]`)
      - affix_text: List of Strings with the text to the rest
                    of the token as individual tokens. For
                    example, a rule for :code:`dígamelo` might have
                    :code:`["me", "lo"]` as its :code:`affix_text`
    
    - lexicon: Dictionary keyed by word with values for lemma, EAGLE code, UD POS, and UD Tags.

2. Convert the Freeling data. Take into account that if you use Freeling data you are effectively agreeing to their license, which might have implications in the release if your own code. If installed, :code:`spacy-affixes` will look for the environment variables :code:`FREELINGDIR` or :code:`FREELINGSHARE` to find the affixes rules and dictionary files and will process them. If you don't have Freeling installed you can always run the :code:`download` command::

.. code-block:: bash

  python -m spacy_affixes download <lang> <version>
  
Where :code:`lang` is the 2-character ISO 639-1 code for a supported language, and :code:`version` an tagged version in their GitHub repository.

Notes
-----
- There is not yet support for Universal Dependencies tags since a good mapping is missing.
- Some decisions might feel idiosyncratic since the purpose of this library at the beginning was to just split clitics in Spanish texts. 
 
