import re

adjective_dict = {
    1: ["NumType", "Poss"],
    2: ["Degree", "NumType"],
    3: ["Gender"],
    4: ["Number"],
    5: ["Person"],
    6: ["Number[psor]"],
}

adverb_dict = {
    1: ["PronType"],
}

determiner_dict = {
    1: ["PronType"],
    2: ["Person"],
    3: ["Gender"],
    4: ["Number"],
    5: ["Number[psor]"],
    6: [None],
}

noun_dict = {
    1: ["POS"],
    2: ["Gender"],
    3: ["Number"],
    4: ["NameType"],
    5: [None],
    6: [None],
}

pronoun_dict = {
    1: ["PronType"],
    2: ["Person"],
    3: ["Gender"],
    4: ["Number"],
    5: ["Case", "PrepCase"],
    6: ["Polite"],
}

conj_dict = {
    1: ["POS"],
}

intj_dict = {
    0: ["_"],
}

adposition_dict = {
    1: ["AdpType"],
}

punctuation_dict = {
    "Fd": "PunctType=Colo",
    "Fc": "PunctType=Comm",
    "Fs": "",
    "Faa": "PunctSide=Ini|PunctType=Excl",
    "Fat": "PunctSide=Fin|PunctType=Excl",
    "Fg": "PunctType=Dash",
    "Fz": "",
    "Ft": "",
    "Fp": "PunctType=Peri",
    "Fia": "PunctSide=Ini|PunctType=Qest",
    "Fit": "PunctSide=Fin|PunctType=Qest",
    "Fe": "PunctType=Quot",
    "Fra": "PunctSide=Ini|PunctType=Quot",
    "Frc": "PunctSide=Fin|PunctType=Quot",
    "Fx": "PunctType=Semi",
    "Fh": "",
    "Fpa": "PunctSide=Ini|PunctType=Brck",
    "Fpt": "PunctSide=Fin|PunctType=Brck",
    "Fca": "PunctSide=Ini|PunctType=Brck",
    "Fct": "PunctSide=Fin|PunctType=Brck",
    "Fla": "PunctSide=Ini|PunctType=Brck",
    "Flt": "PunctSide=Fin|PunctType=Brck",
}

num_dict = {
    0: ["_"],
}

verb_dict = {
    1: ["POS"],
    2: ["Mood", "VerbForm"],
    3: ["Tense", "Mood"],
    4: ["Person"],
    5: ["Number"],
    6: ["Gender"],
}

tag_dict = {
    "Degree": {
        "S": "Sup",
        "V": "Pos",
    },
    "Poss": {
        "P": "Yes",
    },
    "PronType": {
        "N": "Neg",
        "A": "Art",
        "D": "Dem",
        "I": "Ind",
        "P": "Prs",
        "T": "Int",
        "E": "Exc",
        "R": "Rel",
    },
    "VerbForm": {
        "N": "Inf",
        "G": "Ger",
        "P": "Part",
    },
    "Mood": {
        "I": "Ind",
        "S": "Sub",
        "M": "Imp",  # Imperativo
        "C": "Cnd",
    },
    "Tense": {
        "S": "Past",
        "I": "Imp",  # Imperfecto
        "P": "Pres",
        "F": "Fut",
    },
    "NameType": {
        "S": "Prs",
        "G": "Geo",
        "O": "Com",
        "V": "Oth",
    },
    "Gender": {
        "M": "Masc",
        "F": "Fem",
    },
    "Number": {
        "S": "Sing",
        "P": "Plur",
    },
    "Number[psor]": {
        "S": "Sing",
        "P": "Plur",
    },
    "Person": {
        "1": "1",
        "2": "2",
        "3": "3"
    },
    "NumType": {
        "p": "Frac",
        "O": "Ord",
    },
    "Polarity": {
        "N": "Neg"
    },
    "AdpType": {
        "P": "Prep",
    },
    "PrepCase": {
        "O": "Pre",
    },
    "Case": {
        "A": "Acc",
        "N": "Nom",
        "D": "Dat",
    },
    "Polite": {
        "P": "Form",
    },
}

category_dict = {
    "I": {
        "PoS": "INTJ", "feat_dict": intj_dict
    },
    "Z": {
        "PoS": "NUM", "feat_dict": num_dict
    },
    "A": {
        "PoS": "ADJ", "feat_dict": adjective_dict
    },
    "R": {
        "PoS": "ADV", "feat_dict": adverb_dict
    },
    "D": {
        "PoS": "DET", "feat_dict": determiner_dict
    },
    "S": {
        "PoS": "ADP", "feat_dict": adposition_dict
    },
    "F": {
        "PoS": "PUNCT", "feat_dict": punctuation_dict
    },
    "N": {
        "PoS": "NOUN", "feat_dict": noun_dict
    },
    "V": {
        "PoS": "VERB", "feat_dict": verb_dict
    },
    "P": {
        "PoS": "PRON", "feat_dict": pronoun_dict
    },
    "C": {
        "PoS": "CONJ", "feat_dict": conj_dict
    },
}


def eagles2ud(eagle):
    if category_dict.get(eagle[0], None) is None:
        return 'X__X'
    feat_dict = category_dict[eagle[0]]["feat_dict"]
    tag = ""
    pos = (category_dict[eagle[0]]["PoS"])
    if eagle[0] != "V" and re.match(r'.*\+.*', eagle):
        return f"{pos}__AdpType=Preppron"
    else:
        eagle = re.sub(re.compile(r'\+.*'), '', eagle)
    if pos == "PUNCT":
        return f"{pos}__{punctuation_dict[eagle]}"
    if pos in ("INTJ", "NUM"):
        return f"{pos}__"
    if feat_dict[1][0] == "POS":
        if pos == "VERB" and eagle[1] in ("A", "S"):
            pos = "AUX"
        if pos == "CONJ" and eagle[1] == "C":
            pos = "CCONJ"
        if pos == "CONJ" and eagle[1] == "S":
            pos = "SCONJ"
        if pos == "NOUN" and eagle[1] == "P":
            pos = "PROPN"
    for i in range(1, len(eagle)):
        for feature in feat_dict[i]:
            features = tag_dict.get(feature, None)
            features_tag = features.get(eagle[i],
                                        None) if features else None
            if features_tag:
                feature_value = tag_dict[feature][eagle[i]]
                tag += f"|{feature}={feature_value}"
                # If has mood mood, VerbForm=Fin
                if feature == "Mood" and feature_value != "Cnd":
                    tag += "|VerbForm=Fin"
                # If indefinite, Definite=Ind
                if feature == "PronType" and feature_value == "Ind":
                    tag += "|Definite=Ind"
                # If article, Definite=Def
                if feature == "PronType" and feature_value == "Art":
                    tag += "|Definite=Def"
                # If possessor, Poss=Yes
                if feature == "Number[psor]":
                    tag += "|Poss=Yes"
                break
    return f"{pos}__{'|'.join(sorted(tag[1:].split('|')))}"
