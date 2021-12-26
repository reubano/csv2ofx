# coding: utf-8

from operator import itemgetter

# example to convert:
# csv2ofx -m rabobank -E ISO-8859-1 CSV_O_20200630_014400.csv CSV_O_20200630_014400.ofx


def date_func(trxn):
    # Chop up the ISO date and put it in ridiculous M/D/Y order
    tag = trxn["Datum"].split("-")
    return "{}/{}/{}".format(tag[1], tag[2], tag[0])


def desc_func(trxn):
    end = " ".join(trxn["Omschrijving-{}".format(n)] for n in range(1, 4))
    return "{0} - {1}".format(trxn["Naam tegenpartij"], end)


mapping = {
    "has_header": True,
    "currency": itemgetter("Munt"),
    # 'delimiter': ';',
    "bank": "Rabobank",
    "account": itemgetter("IBAN/BBAN"),
    "id": itemgetter("Volgnr"),
    "date": date_func,
    "amount": lambda r: r["Bedrag"].replace(",", "."),
    "desc": desc_func,
    "payee": itemgetter("Naam tegenpartij"),
}
