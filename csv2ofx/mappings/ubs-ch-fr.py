# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
# pylint: disable=invalid-name
"""
csv2ofx.mappings.ubs-ch-fr
~~~~~~~~~~~~~~~~~~~~~~~~~~

Mapping for UBS Switzerland (French)

Exports from UBS CH e-banking Web page ("Liste des mouvements") are quite
tricky:

* Most transactions aren't split, but those for account fees ("Solde prix
  prestations") do! Thus, to make it easy, better off to remove the
  corresponing split lines -- the script `utilz/csvtrim` can be used to
  pre-process the exported CSV file

* Transaction sub-classes and tags ("Etiquettes") aren't exported, thus one
  needs a custom filter looking in columns "Description 2/3".

* The payee is not explicitly provided: it can be in columns "Description 2/3"

"""
from operator import itemgetter

# Financial numbers are expressed as "2'045.56" in de/fr/it_CH (utf8 has some
# glitches, so we go for the default one)
import locale
locale.setlocale(locale.LC_NUMERIC, 'fr_CH')

__author__ = 'Marco "sphakka" Poleggi'


def fixdate(ds):
    dmy = ds.split(".")
    # BUG (!?): can't format here ISO-style as it won't accept first
    # token as a valid month...
    return ".".join((dmy[1], dmy[0], dmy[2]))


def map_descr(tr):
    descr = tr["Description 2"] or tr["Description 1"]
    return descr + (": " + tr["Description 3"] if tr["Description 3"] else "")


def map_class(tr):
    clss = tr["Description 1"]
    return clss + (": " + tr["Description 2"] if tr["Description 2"] else "")


def map_payee(tr):
    return tr["Description 3"] if tr.get("Débit") else tr["Description 2"]


mapping = {
    "delimiter": ";",
    "bank": "UBS Switzerland",
    "has_header": True,
    "date_fmt": "%Y-%m-%d",  # ISO
    "currency": itemgetter("Monn."),
    "account": itemgetter("Produit"),
    # 'Débit' and 'Crédit' columns are always provided, but only one may have
    # a value in a given row
    "type": lambda tr: "debit" if tr.get("Débit") != "" else "credit",
    "amount": lambda tr: locale.atof(tr["Débit"] or tr["Crédit"]),
    # debits show _your_ notes in "Desc 2", whereas credits report the
    # _payee_. Thus a better "class" value comes from "Desc 1" + "Desc 2"
    "class": map_class,
    "notes": itemgetter("Description 2"),
    # switch day/month (maybe file a bug: always inverted when ambiguous like
    # '01.02.2018')
    "date": lambda tr: fixdate(tr["Date de valeur"]),
    "desc": map_descr,
    "payee": map_payee,
    "check_num": itemgetter("N° de transaction"),
    "balance": lambda tr: locale.atof(tr["Solde"]),
}
