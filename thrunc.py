#! /usr/bin/env python
# -*- coding: utf-8 -*-

##########
## thrunc.py Version 0.1 (2015-08-15)
##
## Original author: Matthew Menzenski (menzenski@ku.edu)
##
## License: MIT ( http://opensource.org/licenses/MIT )
##
##
### The MIT License (MIT)
###
### Copyright (c) 2015 Matt Menzenski
###
### Permission is hereby granted, free of charge, to any person obtaining a
### copy of this software and associated documentation files (the "Software"),
### to deal in the Software without restriction, including without limitation
### the rights to use, copy, modify, merge, publish, distribute, sublicense,
### and/or sell copies of the Software, and to permit persons to whom the
### Software is furnished to do so, subject to the following conditions:
###
### The above copyright notice and this permission notice shall be included in
### all copies or substantial portions of the Software.
###
### THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
### OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
### FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
### THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
### LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
### FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
### DEALINGS IN THE SOFTWARE.
##
##########

"""Return frequency and year for items in the historical corpora of the RNC."""

from urllib import FancyURLopener
from bs4 import BeautifulSoup as Soup
import re
import sys
import time
import codecs
import random
import openpyxl

class ResultsSpreadsheet(openpyxl.Workbook):
    """Excel spreadsheet containing search results."""

    def __init__(self, filename):
        super(ResultsSpreadsheet, self).__init__()
        self.filename = filename
        self.active.title = "Results"

    def write_row(self, row_idx, dict_contents):
        """Write dict to row number row_idx in the ResultsSpreadsheet.

        row_idx: an integer representing a row number.
        dict_contents: a dictionary in which the keys are column numbers
          and the values are the corresponding contents, e.g., {1: 'Modern'}.
        """


        print "ROW:\t{}".format(row_idx)
        for k, v in dict_contents.iteritems():
            c = self.active.cell(row=row_idx, column=k)
            c.value = v

            ## also print dict contents to console
            try:
                print "{}:\t{}".format(k, v)
            except UnicodeEncodeError as e:
                print "{}:\tUnicodeEncodeError: {}".format(k, e)
            except UnicodeDecodeError as e:
                print "{}:\tUnicodeDecodeError: {}".format(k, e)
            except:
                print "Unexpected error: {}".format(sys.exc_info()[0])
                raise

        print "\n"

    def save_wb(self):
        """Save the ResultsSpreadsheet to disk."""

        self.save("{}.xlsx".format(self.filename))

    def write_headers(self):
        """Add headers in first row of spreadsheet."""

        header_dict = {
            1: u"Subcorpus",
            2: u"BaseVerb",
            3: u"Lemma",
            4: u"GrammaticalForm",
            5: u"PrefixValue",
            6: u"Prefix",
            7: u"SuffixValue",
            8: u"Suffix",
            9: u"SourceName",
            10: u"SourceDateBegin",
            11: u"SourceDateMiddle",
            12: u"SourceDateEnd",
            13: u"NumberOfTokens",
            14: u"ResultsPageIndex"
            }

        self.write_row(row_idx=1, dict_contents=header_dict)


class RNCSource(object):
    """One source in RNC search results."""

    def __init__(self, source_name_as_string):
        self.source = source_name_as_string
        self.name = re.sub(r'\([^)]*\)', '', self.source)

        date_seq = re.findall(r'\d{4}-\d{4}', self.source)
        if date_seq:
            self.date_begin = float(date_seq[0].split('-')[0])
            self.date_end = float(date_seq[0].split('-')[1])
            self.date_middle = (self.date_begin + self.date_end) / 2.0

        else:
            dates = re.findall(r'\d{4}', self.source)
            if dates:
                self.date_begin = float(dates[0])
                self.date_middle = float(dates[0])
                self.date_end = float(dates[0])
            else:
                self.date_begin = 0
                self.date_middle = 0
                self.date_end = 0

class MyOpener(FancyURLopener):
    """FancyURLopener object with custom User-Agent field."""

    ## regular Mac Safari browser:
    version = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) "
        "AppleWebKit/600.5.17 (KHTML, like Gecko) Version/8.0.5 "
        "Safari/600.5.17"
        )

    ## identify this web scraper as such
    ## and link to a page with a description of its purpose:
    #version = ("Web scraper created by Matt Menzenski. "
    #           "See www.menzenski.com/scraper for more information.")

class Webpage(object):
    """Generic webpage with attributes."""

    def __init__(self, address):
        self.address = address
        myopener = MyOpener()
        delay = random.randint(2,11)
        time.sleep(delay)

        unsuccessful = True
        while unsuccessful:
            long_delay = delay * 2
            try:
                print "Trying with a delay of {} seconds to open\n{}\n".format(
                    delay, self.address
                    )
                self.html = myopener.open(self.address).read()
                self.soup = Soup(self.html)
                unsuccessful = False
            except IOError as e:
                print "\nIOError: {}\nAddress:{}\n".format(e, self.address)
                long_delay *= 2
                time.sleep(long_delay)
                print "Now trying with a longer delay of {} seconds.\n".format(
                    long_delay
                    )
                self.html = myopener.open(self.address).read()
                self.soup = Soup(self.html)

class RNCQueryAncient(object):
    """Object describing a query of the Ancient RNC subcorpus."""

    def __init__(self, mode="old_rus", text1="lexgramm",
            sort="gr_created", lang="ru",
            doc_docid="0|13|2|3|1|4|7|8|10|12|5|11|9|6",
            parent1=0, level1=0, lexi1="", gramm1="",
            parent2=0, level2=0, min2=1, max2=1):
        """Initialize with empty search parameters."""

        self.mode = mode
        self.text1 = text1
        self.doc_docid = doc_docid
        self.parent1 = parent1
        self.level1 = level1
        self.lexi1 = lexi1
        self.gramm1 = gramm1
        self.parent2 = parent2
        self.level2 = level2
        self.min2 = min2
        self.max2 = max2

        self.params = {
            "mode": self.mode,
            "text": self.text1,
            "doc_docid": self.doc_docid,
            "parent1": self.parent1,
            "level1": self.level1,
            "lexi1": self.lexi1,
            "gramm1": self.gramm1,
            "parent2": self.parent2,
            "level2": self.level2,
            "min2": self.min2,
            "max2": self.max2,
            }

        self.base_url = "http://search-beta.ruscorpora.ru/search.xml?"

class RNCQueryOld(object):
    """Object describing a query of the Old RNC subcorpus."""

    def __init__(self, env="alpha", mode="mid_rus", text="lexform",
            sort="gr_created", lang="ru", mycorp="", mysent="",
            mysize="", mysentsize="", mydocsize="", dpp="",
            spp="", spd="", req=""):
        """Initialize with empty search parameters."""

        self.env = env
        self.mode = mode
        self.text = text
        self.sort = sort
        self.lang = lang
        self.mycorp = mycorp
        self.mysent = mysent
        self.mysize = mysize
        self.mysentsize = mysentsize
        self.mydocsize = mydocsize
        self.dpp = dpp
        self.spp = spp
        self.spd = spd
        self.req = req

        self.params = {
            "env": self.env,
            "mode": self.mode,
            "text": self.text,
            "sort": self.sort,
            "lang": self.lang,
            "mycorp": self.mycorp,
            "mysent": self.mysent,
            "mysize": self.mysize,
            "mysentsize": self.mysentsize,
            "mydocsize": self.mydocsize,
            "dpp": self.dpp,
            "spp": self.spp,
            "spd": self.spd,
            "req": self.req,
            }

        self.base_url = "http://search-beta.ruscorpora.ru/search.xml?"

class RNCQueryModern(object):
    """Object describing a query of the Modern RNC subcorpus."""

    def __init__(self, mycorp="", mysent="", mysize="",
            dpp="", spp="", spd="", text="lexgramm",
            mode="main", sort="gr_tagging", lang="en",
            parent1=0, level1=0, lex1="", gramm1="",
            sem1="", flags1="", sem_mod1="",
            sem_mod2="", parent2=0, level2=0, min2=1,
            max2=1, lex2="", gramm2="", sem2="",
            flags2="", end_year=None):
        """Initialize with empty search parameters."""

        self.mycorp = mycorp
        self.mysent = mysent
        self.mysize = mysize
        self.dpp = dpp
        self.spp = spp
        self.spd = spd
        self.text = text
        self.mode = mode
        self.sort = sort
        self.lang = lang
        self.parent1 = parent1
        self.level1 = level1
        self.lex1 = lex1
        self.gramm1 = gramm1
        self.sem1 = sem1
        self.flags1 = flags1
        self.sem_mod1 = sem_mod1
        self.sem_mod2 = sem_mod2
        self.parent2 = parent2
        self.level2 = level2
        self.min2 = min2
        self.max2 = max2
        self.lex2 = lex2
        self.gramm2 = gramm2
        self.sem2 = sem2
        self.flags2 = flags2

        # parameters for search URL generation
        self.params = {
            "mycorp": self.mycorp,
            "mysent": self.mysent,
            "mysize": self.mysize,
            "dpp": self.dpp,
            "spp": self.spp,
            "spd": self.spd,
            "text": self.text,
            "mode": self.mode,
            "sort": self.sort,
            "lang": self.lang,
            "parent1": self.parent1,
            "level1": self.level1,
            "lex1": self.lex1,
            "gramm1": self.gramm1,
            "sem1": self.sem1,
            "flags1": self.flags1,
            "sem-mod1": self.sem_mod1,
            # "sem-mod1": ,
            "parent2": self.parent2,
            "level2": self.level2,
            "min2": self.min2,
            "max2": self.max2,
            "lex2": self.lex2,
            "gramm2": self.gramm2,
            "sem2": self.sem2,
            "flags2": self.flags2,
            "sem-mod2": self.sem_mod2
            #"sem-mod2": ,
            }

        # search the corpus prior to a defined end date
        if end_year is not None:
            self.end_year = end_year
            self.env = "alpha"
            self.mycorp = ("%28%28created%253A%253C%253D%"
                "2522{}%2522%29%29".format(end_year)
                )
            self.mysize = 3715941
            self.mysentsize = 215701
            self.mydocsize = 1284
            self.lang = "ru"
            self.nodia = 1
            self.m1 = ""
            self.m2 = ""

            self.params["env"] = self.env
            self.params["mycorp"] = self.mycorp
            self.params["mysize"] = self.mysize
            self.params["mysentsize"] = self.mysentsize
            self.params["mydocsize"] = self.mydocsize
            self.params["lang"] = self.lang
            self.params["nodia"] = self.nodia
            self.params["m1"] = self.m1
            self.params["m2"] = self.m2

        self.base_url = "http://search.ruscorpora.ru/search.xml?"

class RNCSearch(object):
    """A search of one of the three historical RNC subcorpora."""

    def __init__(self, rnc_query, subcorpus="", pfx_val="",
            sfx_val="", lem="", gramm_cat="",
            base_verb="", prefix="", suffix=""):
        """Initialize search object.

        Parameters
        ----------
          rnc_query:  RNCQueryAncient(), RNCQueryOld(), or RNCQueryModern()
          subcorpus:  'Ancient', 'Old', or 'Modern'
          pfx_val:    'yesPrefix' or 'noPrefix'
          sfx_val:    'yesSuffix' or 'noSuffix'
          lem:        e.g., 'собирать'
          gramm_cat:  e.g., 'praet'
          base_verb:  e.g., 'брать'
          prefix:     e.g., 'ot-'
          suffix:     e.g., '-yva-'

        """

        self.subcorpus = subcorpus
        self.pfx_val = pfx_val
        self.sfx_val = sfx_val
        self.lem = lem
        self.gramm_cat = gramm_cat
        self.base_verb = base_verb
        self.prefix = prefix
        self.suffix = suffix

        self.params = rnc_query.params
        self.address = rnc_query.base_url
        self.results_page_urls = []

        ## list of dicts
        self.all_search_results = []

    def base_search_url(self):
        """Generate a search url from parameters."""
        for k, v in self.params.iteritems():
            self.address += "{}={}&".format(k, v)

        return self.address

    def scrape_one_page(self, soup, idx=0):
        """Scrape the content of one page.

        Parameters
        ----------
          soup: BeautifulSoup() object of a webpage
          idx: number of the results page (e.g., idx=10 means p=10& in the url)

        """

        sources_on_page = []

        lis = soup.ol.find_all('li')
        for li in lis:
            if li.contents[4].string.startswith(u"Все"):
                sources_on_page.append(li)
            elif li.contents[4].string.startswith(u"All"):
                sources_on_page.append(li)
            else:
                pass

        for source in sources_on_page:
            source_name = source.contents[0].string
            src_obj = RNCSource(source_name)
            examples = re.search(ur'(\d+)', source.contents[4].string)
            if examples:
                source_examples = int(examples.group(0))
            else:
                source_examples = 0

            row_dict = {
                1: "{}".format(self.subcorpus),
                2: "{}".format(self.base_verb),
                3: "{}".format(self.lem),
                4: "{}".format(self.gramm_cat),
                5: "{}".format(self.pfx_val),
                6: "{}".format(self.prefix),
                7: "{}".format(self.sfx_val),
                8: "{}".format(self.suffix),
                9: u"{}".format(source_name),
                10: src_obj.date_begin,
                11: src_obj.date_middle,
                12: src_obj.date_end,
                13: source_examples,
                14: idx
                }
            self.all_search_results.append(row_dict)

    def scrape_pages(self):
        """More straightforward scraping method."""

        self.base_search_url()
        page_idx = 0

        has_more_results = True

        while has_more_results:

            url = self.address
            address = url + "p=" + str(page_idx) + "&"
            page = Webpage(address)
            if page.soup.ol:
                if page.soup.ol.find_all('li'):
                    print page_idx
                    print address
                    print "\n"
                    self.scrape_one_page(soup=page.soup, idx=page_idx)
                    page_idx += 1

                else:
                    has_more_results = False
            else:
                has_more_results = False


class RussianVerb(object):
    """Russian verb object: provides namespace for possible forms."""

    def __init__(self, simplex_verb):

        self.root = simplex_verb
        self.prefixed_forms = {}

        self.prefixes = {
            # path/location prefixes
            'o-': ['о', 'об', 'обо', 'объ'],
            'nad-': ['над', 'надо', 'надъ'],
            'pere-': ['пере', 'пре', 'прѣ'],
            'pro-': ['про'],
            'u-': ['у', 'ѹ', '', 'ꙋ'],
            'na-': ['на'],
            # goal prefixes
            'v-': ['в', 'во', 'въ'],
            'pri-': ['при'],
            'za-': ['за'],
            'do-': ['до'],
            's-': ['с', 'со', 'съ'],
            # source prefixes
            'iz-': ['из', 'изо', 'изъ'],
            'vy-': ['вы'],
            'ot-': ['от', 'ото', 'отъ'],
            'voz-': [
                'вз', 'вс', 'воз', 'вос', 'взо', 'взъ',
                'возъ', 'въз', 'въс', 'възъ'
                ],
            'raz-': ['раз', 'рас', 'разо', 'разъ'],
            # po
            'po-': ['по'],
            }

        self.prefixes_with_null = self.prefixes
        self.prefixes_with_null['—'] = ['']

        self.prefixed_forms = []
        for k, v in self.prefixes.iteritems():
            for pfx in v:
                self.prefixed_forms.append("{}{}".format(pfx, self.root))

        self.prefixed_forms_by_prefix = {}
        for k, v in self.prefixes.iteritems():
            forms = [pfx + self.root for pfx in v]
            self.prefixed_forms_by_prefix[k] = forms

        self.all_forms_by_prefix = self.prefixed_forms_by_prefix
        self.all_forms_by_prefix['—'] = ['' + self.root]


class RNCSearchTerm(object):
    """Container object holding all (past-tense) forms of a search term."""
    ## we're really just providing a convenient namespace for handling terms.

    def __init__(self, start_row=2, results_spreadsheet=None,
            csv_filename=None, suffix=None):
        ## starting row for writing results to spreadsheet
        self.rw = start_row

        ## the spreadsheet to which results will be written
        if results_spreadsheet is not None:
            ## write to existing spreadsheet if there is one
            self.rs = results_spreadsheet
        else:
            ## if one doesn't exist, create a new one with a default name
            self.rs = ResultsSpreadsheet(filename="Results")

        ## assume a verb is unsuffixed unless a suffix is specified
        if suffix is not None:
            self.suffix = suffix

        ## the ancient corpus needs both lemmas and grammatical categories
        self.ancient_forms = ['iperf', 'aor', 'perf', 'past']
        self.ancient_splx_ipf = [] # simplex imperfective lemmas
        self.ancient_pfx_pf = []   # prefixed perfective lemmas
        self.ancient_pfx_ipf = []  # prefixed imperfective lemmas

        ## the old corpus needs individual word forms only, NOT lemmas
        self.old_inf = ''          # base_infinitive
        self.old_splx_ipf = []     # simplex imperfective word forms
        self.old_pfx_pf = []       # prefixed perfective word forms
        self.old_pfx_ipf = []      # prefixed imperfective word forms

        ## the modern corpus needs both lemmas and grammatical categories
        self.modern_forms = ['praet']
        self.modern_splx_ipf = []  # simplex imperfective lemmas
        self.modern_pfx_pf = []    # prefixed perfective lemmas
        self.modern_pfx_ipf = []   # prefixed imperfective lemmas

    def search_ancient(self):
        """Search the ancient subcorpus."""

        for gramm_form in self.ancient_forms:
            for verb_form in self.ancient_splx_ipf:
                rv = RussianVerb(simplex_verb=verb_form)
                for pfx, vb in rv.all_forms_by_prefix.iteritems():
                    for v in vb:
                        query = RNCQueryAncient(
                            lexi1=v, gramm1=gramm_form
                            )

                        if pfx == "—":
                            pfxv = "noPrefix"
                        else:
                            pfxv = "yesPrefix"

                        try:
                            if self.suffix is not None:
                                sfxv = "yesSuffix"
                                sfx = self.suffix
                            else:
                                sfxv = "noSuffix"
                                sfx = ""
                        except AttributeError as e:
                            print "AttributeError: {}".format(e)
                            sfxv = "noSuffix"
                            sfx = ""

                        search = RNCSearch(
                            rnc_query=query, subcorpus="Ancient",
                            pfx_val=pfxv, prefix=pfx,
                            sfx_val=sfxv, suffix=sfx,
                            lem=v, gramm_cat=gramm_form,
                            base_verb=verb_form
                            )
                        search.scrape_pages()

                        if self.rs:
                            for d in search.all_search_results:
                                for i in range(d[13]):
                                    self.rs.write_row(
                                        row_idx=self.rw, dict_contents=d
                                        )
                                    self.rw += 1

    def search_old(self):
        """Search the old subcorpus."""

        for verb_form in self.old_splx_ipf:
            rv = RussianVerb(simplex_verb=verb_form)
            for pfx, vb in rv.all_forms_by_prefix.iteritems():
                for v in vb:
                    query = RNCQueryOld(
                        req=v
                        )

                    if pfx == "—":
                        pfxv = "noPrefix"
                    else:
                        pfxv = "yesPrefix"

                    try:
                        if self.suffix is not None:
                            sfxv = "yesSuffix"
                            sfx = self.suffix
                        else:
                            sfxv = "noSuffix"
                            sfx = ""
                    except AttributeError as e:
                        print "AttributeError: {}".format(e)
                        sfxv = "noSuffix"
                        sfx = ""

                    search = RNCSearch(
                        rnc_query=query, subcorpus="Old",
                        pfx_val=pfxv, prefix=pfx,
                        sfx_val=sfxv, suffix=sfx,
                        lem=v, base_verb=self.old_inf
                        )
                    search.scrape_pages()

                    if self.rs:
                        for d in search.all_search_results:
                            for i in range(d[13]):
                                self.rs.write_row(
                                    row_idx=self.rw, dict_contents=d
                                    )
                                self.rw += 1

    def search_modern(self):
        """Search the modern subcorpus."""

        for gramm_form in self.modern_forms:
            for verb_form in self.modern_splx_ipf:
                rv = RussianVerb(simplex_verb=verb_form)
                for pfx, vb in rv.all_forms_by_prefix.iteritems():
                    for v in vb:
                        query = RNCQueryModern(
                            lex1=v, gramm1=gramm_form, end_year=1799
                            )

                        if pfx == "—":
                            pfxv = "noPrefix"
                        else:
                            pfxv = "yesPrefix"

                        try:
                            if self.suffix is not None:
                                sfxv = "yesSuffix"
                                sfx = self.suffix
                            else:
                                sfxv = "noSuffix"
                                sfx = ""
                        except AttributeError as e:
                            print "AttributeError: {}".format(e)
                            sfxv = "noSuffix"
                            sfx = ""

                        search = RNCSearch(
                            rnc_query=query, subcorpus="Modern",
                            pfx_val=pfxv, prefix=pfx,
                            sfx_val=sfxv, suffix=sfx,
                            lem=v, gramm_cat=gramm_form,
                            base_verb=verb_form
                            )
                        search.scrape_pages()

                        if self.rs:
                            for d in search.all_search_results:
                                for i in range(d[13]):
                                    self.rs.write_row(
                                        row_idx=self.rw, dict_contents=d
                                        )
                                    self.rw += 1

    def search_all(self):
        """Perform an RNCSearch for each possible word in the RNCSearchTerm."""

        ## search all three subcorpora
        self.search_ancient()
        self.search_old()
        self.search_modern()

        ## save the results spreadsheet to disk
        self.rs.save_wb()


def main():
    row = 2
    wb = ResultsSpreadsheet(filename="historicalSearchResults")
    wb.write_headers()

    word = "почитывать"
    query = RNCQueryModern(lex1=word)
    search = RNCSearch(
        rnc_query=query, subcorpus="Modern",
        pfx_val="yesPrefix", prefix="po-",
        sfx_val="yesSuffix", suffix="-yva-",
        lem=word, base_verb="читать"
        )
    search.scrape_pages()

    for d in search.all_search_results:
        for i in range(d[12]):
            wb.write_row(row_idx=row, dict_contents=d)
            row += 1

    wb.save_wb()

def main_test():
    wb = ResultsSpreadsheet(filename="searchresultsBRATall")
    wb.write_headers()

    brat = RNCSearchTerm(start_row=2, results_spreadsheet=wb)

    brat.ancient_splx_ipf = ['брати', 'бьрати']

    brat.old_inf = 'брати'
    brat.old_splx_ipf = [
        ## without the front jer
        'брал', 'бралъ', 'брала', 'брало', 'брали',
        'браахъ', 'брааше', 'браахомъ', 'браашете',
        'браахѫ', 'брааху',
        'брааховѣ', 'браахове', 'браашета',
        ## with the front jer
        'бьрал', 'бьралъ', 'бьрала', 'бьрало', 'бьрали',
        'бьраахъ', 'бьрааше', 'бьраахомъ', 'бьраашете',
        'бьраахѫ', 'бьрааху',
        'бьрааховѣ', 'бьраахове', 'бьраашета',
        ]

    brat.modern_splx_ipf = ['брать']

    brat.search_all()

    #wb.save_wb

def main_real():
    ## BRAT / -BIRAT 'GATHER'
    wb_brat = ResultsSpreadsheet(filename="2015_08_20_verbBRAT")
    wb_brat.write_headers()
    ## verb 'brat'
    brat = RNCSearchTerm(start_row=2, results_spreadsheet=wb_brat)
    brat.ancient_splx_ipf = ['брати', 'бьрати']
    brat.old_inf = 'брати'
    brat.old_splx_ipf = [
        ## without the front jer
        'брал', 'бралъ', 'брала', 'брало', 'брали',         # L-participle
        'браахъ', 'браахомъ', 'брааховѣ', 'браахове',       # impft 1st person
        'брааше', 'браашете', 'браашета',                   # impft 2nd person
        'браахѫ', 'брааху',                                 # impft 3rd person
        'брахъ', 'браховѣ', 'брахове', 'брахомъ',           # aor. 1st person
        'бра', 'браста', 'брасте',                          # aor. 2nd person
        'брашѧ', 'браша',                                   # aor. 3rd person
        ## with the front jer-
        'бьрал', 'бьралъ', 'бьрала', 'бьрало', 'бьрали',    # L-participle
        'бьраахъ', 'бьраахомъ', 'бьрааховѣ', 'бьраахове',   # impft 1st person
        'бьрааше', 'бьраашете', 'бьраашета',                # impft 2nd person
        'бьраахѫ', 'бьрааху',                               # impft 3rd person
        'бьрахъ', 'бьраховѣ', 'бьрахове', 'бьрахомъ',       # aor. 1st person
        'бьра', 'бьраста', 'бьрасте',                       # aor. 2nd person
        'бьрашѧ', 'бьраша',                                 # aor. 3rd person
        ## with the back jer
        'бърал', 'бъралъ', 'бърала', 'бърало', 'бърали',    # L-participle
        'бъраахъ', 'бъраахомъ', 'бърааховѣ', 'бъраахове',   # impft 1st person
        'бърааше', 'бъраашете', 'бъраашета',                # impft 2nd person
        'бъраахѫ', 'бърааху',                               # impft 3rd person
        'бърахъ', 'бъраховѣ', 'бърахове', 'бърахомъ',       # aor. 1st person
        'бъра', 'бъраста', 'бърасте',                       # aor. 2nd person
        'бърашѧ', 'бъраша',                                 # aor. 3rd person
        ## with the present-tense root vowel (imperfect only)
        'бераахъ', 'бераахомъ', 'берааховѣ', 'бераахове',   # impft 1st person
        'берааше', 'бераашете', 'бераашета',                # impft 2nd person
        'бераахѫ', 'берааху',                               # impft 3rd person
        ## with the present-tense root vowel and yat (imperfect only)
        'берѣахъ', 'берѣахомъ', 'берѣаховѣ', 'берѣахове',   # impft 1st person
        'берѣаше', 'берѣашете', 'берѣашета',                # impft 2nd person
        'берѣахѫ', 'берѣаху',                               # impft 3rd person
        ## with the present-tense root vowel and е (imperfect only)
        'береахъ', 'береахомъ', 'береаховѣ', 'береахове',   # impft 1st person
        'береаше', 'береашете', 'береашета',                # impft 2nd person
        'береахѫ', 'береаху',                               # impft 3rd person
        ]
    brat.modern_splx_ipf = ['брать']
    brat.search_all()

    wb_birat = ResultsSpreadsheet(filename="2015_08_20_verbBIRAT")
    wb_birat.write_headers()
    ## verb 'birat'
    birat = RNCSearchTerm(start_row=2, results_spreadsheet=wb_birat)
    birat.suffix = "-a-"
    birat.ancient_splx_ipf = ['бирати']
    birat.old_inf = 'бирати'
    birat.old_splx_ipf = [
        ## L-participle
        'бирал', 'биралъ', 'бирала', 'бирало', 'бирали',    # L-participle
        ## aorist
        'бирахъ', 'бираховѣ', 'бирахове', 'бирахомъ',       # aor. 1st person
        'бира', 'бираста', 'бирасте',                       # aor. 2nd person
        'бирашѧ', 'бираша',                                 # aor. 3rd person
        ## imperfect with -a-
        'бираахъ', 'бираахомъ', 'бирааховѣ', 'бираахове',   # impft 1st person
        'бирааше', 'бираашете', 'бираашета',                # impft 2nd person
        'бираахѫ', 'бирааху',                               # impft 3rd person
        ## imperfect with -yat-
        'бирѣахъ', 'бирѣахомъ', 'бирѣаховѣ', 'бирѣахове',   # impft 1st person
        'бирѣаше', 'бирѣашете', 'бирѣашета',                # impft 2nd person
        'бирѣахѫ', 'бирѣаху',                               # impft 3rd person
        ## imperfect with -е-
        'биреахъ', 'биреахомъ', 'биреаховѣ', 'биреахове',   # impft 1st person
        'биреаше', 'биреашете', 'биреашета',                # impft 2nd person
        'биреахѫ', 'биреаху',                               # impft 3rd person
        ]
    birat.modern_splx_ipf = ['бирать']
    birat.search_all()

    ## DRAT / -DIRAT 'FLAY'
    wb_drat = ResultsSpreadsheet(filename="2015_08_20_verbDRAT")
    wb_drat.write_headers()
    ## verb 'drat'
    drat = RNCSearchTerm(start_row=2, results_spreadsheet=wb_drat)
    drat.ancient_splx_ipf = ['драти', 'дьрати']
    drat.old_inf = 'драти'
    drat.old_splx_ipf = [
        ## without the front jer
        'драл', 'дралъ', 'драла', 'драло', 'драли',         # L-participle
        'драахъ', 'драахомъ', 'драаховѣ', 'драахове',       # impft 1st person
        'драаше', 'драашете', 'драашета',                   # impft 2nd person
        'драахѫ', 'драаху',                                 # impft 3rd person
        'драхъ', 'драховѣ', 'драхове', 'драхомъ',           # aor. 1st person
        'дра', 'драста', 'драсте',                          # aor. 2nd person
        'драшѧ', 'драша',                                   # aor. 3rd person
        ## with the front jer
        'дьрал', 'дьралъ', 'дьрала', 'дьрало', 'дьрали',    # L-participle
        'дьраахъ', 'дьраахомъ', 'дьрааховѣ', 'дьраахове',   # impft 1st person
        'дьрааше', 'дьраашете', 'дьраашета',                # impft 2nd person
        'дьраахѫ', 'дьрааху',                               # impft 3rd person
        'дьрахъ', 'дьраховѣ', 'дьрахове', 'дьрахомъ',       # aor. 1st person
        'дьра', 'дьраста', 'дьрасте',                       # aor. 2nd person
        'дьрашѧ', 'дьраша',                                 # aor. 3rd person
        ## with the back jer
        'дърал', 'дъралъ', 'дърала', 'дърало', 'дърали',    # L-participle
        'дъраахъ', 'дъраахомъ', 'дърааховѣ', 'дъраахове',   # impft 1st person
        'дърааше', 'дъраашете', 'дъраашета',                # impft 2nd person
        'дъраахѫ', 'дърааху',                               # impft 3rd person
        'дърахъ', 'дъраховѣ', 'дърахове', 'дърахомъ',       # aor. 1st person
        'дъра', 'дъраста', 'дърасте',                       # aor. 2nd person
        'дърашѧ', 'дъраша',                                 # aor. 3rd person
        ## with the present-tense root vowel (imperfect only)
        'дераахъ', 'дераахомъ', 'дерааховѣ', 'дераахове',   # impft 1st person
        'дерааше', 'дераашете', 'дераашета',                # impft 2nd person
        'дераахѫ', 'дерааху',                               # impft 3rd person
        ## with the present-tense root vowel and yat (imperfect only)
        'дерѣахъ', 'дерѣахомъ', 'дерѣаховѣ', 'дерѣахове',   # impft 1st person
        'дерѣаше', 'дерѣашете', 'дерѣашета',                # impft 2nd person
        'дерѣахѫ', 'дерѣаху',                               # impft 3rd person
        ## with the present-tense root vowel and е (imperfect only)
        'дереахъ', 'дереахомъ', 'дереаховѣ', 'дереахове',   # impft 1st person
        'дереаше', 'дереашете', 'дереашета',                # impft 2nd person
        'дереахѫ', 'дереаху',                               # impft 3rd person
        ]
    drat.modern_splx_ipf = ['драть']
    drat.search_all()

    wb_dirat = ResultsSpreadsheet(filename="2015_08_20_verbDIRAT")
    wb_dirat.write_headers()
    ## verb 'dirat'
    dirat = RNCSearchTerm(start_row=2, results_spreadsheet=wb_dirat)
    dirat.suffix = "-a-"
    dirat.ancient_splx_ipf = ['дирати']
    dirat.old_inf = 'дирати'
    dirat.old_splx_ipf = [
        ## L-participle
        'дирал', 'диралъ', 'дирала', 'дирало', 'дирали',    # L-participle
        ## aorist
        'дирахъ', 'дираховѣ', 'дирахове', 'дирахомъ',       # aor. 1st person
        'дира', 'дираста', 'дирасте',                       # aor. 2nd person
        'дирашѧ', 'дираша',                                 # aor. 3rd person
        ## imperfect with -a-
        'дираахъ', 'дираахомъ', 'дирааховѣ', 'дираахове',   # impft 1st person
        'дирааше', 'дираашете', 'дираашета',                # impft 2nd person
        'дираахѫ', 'дирааху',                               # impft 3rd person
        ## imperfect with -yat-
        'дирѣахъ', 'дирѣахомъ', 'дирѣаховѣ', 'дирѣахове',   # impft 1st person
        'дирѣаше', 'дирѣашете', 'дирѣашета',                # impft 2nd person
        'дирѣахѫ', 'дирѣаху',                               # impft 3rd person
        ## imperfect with -е-
        'диреахъ', 'диреахомъ', 'диреаховѣ', 'диреахове',   # impft 1st person
        'диреаше', 'диреашете', 'диреашета',                # impft 2nd person
        'диреахѫ', 'диреаху',                               # impft 3rd person
        ]
    dirat.modern_splx_ipf = ['дирать']
    dirat.search_all()

    ## PRAT / -PIRAT 'PRESS'

    wb_prat = ResultsSpreadsheet(filename="2015_08_20_verbPRAT")
    wb_prat.write_headers()
    ## verb 'prat'
    prat = RNCSearchTerm(start_row=2, results_spreadsheet=wb_prat)
    prat.ancient_splx_ipf = ['прати', 'пьрати']
    prat.old_inf = 'прати'
    prat.old_splx_ipf = [
        ## without the front jer
        'прал', 'пралъ', 'прала', 'прало', 'прали',         # L-participle
        'праахъ', 'праахомъ', 'прааховѣ', 'праахове',       # impft 1st person
        'прааше', 'праашете', 'праашета',                   # impft 2nd person
        'праахѫ', 'прааху',                                 # impft 3rd person
        'прахъ', 'праховѣ', 'прахове', 'прахомъ',           # aor. 1st person
        'пра', 'праста', 'прасте',                          # aor. 2nd person
        'прашѧ', 'праша',                                   # aor. 3rd person
        ## with the front jer
        'пьрал', 'пьралъ', 'пьрала', 'пьрало', 'пьрали',    # L-participle
        'пьраахъ', 'пьраахомъ', 'пьрааховѣ', 'пьраахове',   # impft 1st person
        'пьрааше', 'пьраашете', 'пьраашета',                # impft 2nd person
        'пьраахѫ', 'пьрааху',                               # impft 3rd person
        'пьрахъ', 'пьраховѣ', 'пьрахове', 'пьрахомъ',       # aor. 1st person
        'пьра', 'пьраста', 'пьрасте',                       # aor. 2nd person
        'пьрашѧ', 'пьраша',                                 # aor. 3rd person
        ## with the back jer
        'пърал', 'пъралъ', 'пърала', 'пърало', 'пърали',    # L-participle
        'пъраахъ', 'пъраахомъ', 'пърааховѣ', 'пъраахове',   # impft 1st person
        'пърааше', 'пъраашете', 'пъраашета',                # impft 2nd person
        'пъраахѫ', 'пърааху',                               # impft 3rd person
        'пърахъ', 'пъраховѣ', 'пърахове', 'пърахомъ',       # aor. 1st person
        'пъра', 'пъраста', 'пърасте',                       # aor. 2nd person
        'пърашѧ', 'пъраша',                                 # aor. 3rd person
        ## with the present-tense root vowel (imperfect only)
        'пераахъ', 'пераахомъ', 'перааховѣ', 'пераахове',   # impft 1st person
        'перааше', 'пераашете', 'пераашета',                # impft 2nd person
        'пераахѫ', 'перааху',                               # impft 3rd person
        ## with the present-tense root vowel and yat (imperfect only)
        'перѣахъ', 'перѣахомъ', 'перѣаховѣ', 'перѣахове',   # impft 1st person
        'перѣаше', 'перѣашете', 'перѣашета',                # impft 2nd person
        'перѣахѫ', 'перѣаху',                               # impft 3rd person
        ## with the present-tense root vowel and е (imperfect only)
        'переахъ', 'переахомъ', 'переаховѣ', 'переахове',   # impft 1st person
        'переаше', 'переашете', 'переашета',                # impft 2nd person
        'переахѫ', 'переаху',                               # impft 3rd person
        ]
    prat.modern_splx_ipf = ['прать']
    prat.search_all()

    wb_pirat = ResultsSpreadsheet(filename="2015_08_20_verbPIRAT")
    wb_pirat.write_headers()
    ## verb 'pirat'
    pirat = RNCSearchTerm(start_row=2, results_spreadsheet=wb_pirat)
    pirat.suffix = "-a-"
    pirat.ancient_splx_ipf = ['пирати']
    pirat.old_inf = 'пирати'
    pirat.old_splx_ipf = [
        ## L-participle
        'пирал', 'пиралъ', 'пирала', 'пирало', 'пирали',    # L-participle
        ## aorist
        'пирахъ', 'пираховѣ', 'пирахове', 'пирахомъ',       # aor. 1st person
        'пира', 'пираста', 'пирасте',                       # aor. 2nd person
        'пирашѧ', 'пираша',                                 # aor. 3rd person
        ## imperfect with -a-
        'пираахъ', 'пираахомъ', 'пирааховѣ', 'пираахове',   # impft 1st person
        'пирааше', 'пираашете', 'пираашета',                # impft 2nd person
        'пираахѫ', 'пирааху',                               # impft 3rd person
        ## imperfect with -yat-
        'пирѣахъ', 'пирѣахомъ', 'пирѣаховѣ', 'пирѣахове',   # impft 1st person
        'пирѣаше', 'пирѣашете', 'пирѣашета',                # impft 2nd person
        'пирѣахѫ', 'пирѣаху',                               # impft 3rd person
        ## imperfect with -е-
        'пиреахъ', 'пиреахомъ', 'пиреаховѣ', 'пиреахове',   # impft 1st person
        'пиреаше', 'пиреашете', 'пиреашета',                # impft 2nd person
        'пиреахѫ', 'пиреаху',                               # impft 3rd person
        ]
    pirat.modern_splx_ipf = ['пирать']
    pirat.search_all()

    ## SRAT / -SIRAT 'SHIT'

    wb_srat = ResultsSpreadsheet(filename="2015_08_20_verbSRAT")
    wb_srat.write_headers()
    ## verb 'srat'
    srat = RNCSearchTerm(start_row=2, results_spreadsheet=wb_srat)
    srat.ancient_splx_ipf = ['срати', 'сьрати']
    srat.old_inf = 'срати'
    srat.old_splx_ipf = [
        ## without the front jer
        'срал', 'сралъ', 'срала', 'срало', 'срали',         # L-participle
        'сраахъ', 'сраахомъ', 'срааховѣ', 'сраахове',       # impft 1st person
        'срааше', 'сраашете', 'сраашета',                   # impft 2nd person
        'сраахѫ', 'срааху',                                 # impft 3rd person
        'срахъ', 'сраховѣ', 'срахове', 'срахомъ',           # aor. 1st person
        'сра', 'сраста', 'срасте',                          # aor. 2nd person
        'срашѧ', 'сраша',                                   # aor. 3rd person
        ## with the front jer
        'сьрал', 'сьралъ', 'сьрала', 'сьрало', 'сьрали',    # L-participle
        'сьраахъ', 'сьраахомъ', 'сьрааховѣ', 'сьраахове',   # impft 1st person
        'сьрааше', 'сьраашете', 'сьраашета',                # impft 2nd person
        'сьраахѫ', 'сьрааху',                               # impft 3rd person
        'сьрахъ', 'сьраховѣ', 'сьрахове', 'сьрахомъ',       # aor. 1st person
        'сьра', 'сьраста', 'сьрасте',                       # aor. 2nd person
        'сьрашѧ', 'сьраша',                                 # aor. 3rd person
        ## with the back jer
        'сърал', 'съралъ', 'сърала', 'сърало', 'сърали',    # L-participle
        'съраахъ', 'съраахомъ', 'сърааховѣ', 'съраахове',   # impft 1st person
        'сърааше', 'съраашете', 'съраашета',                # impft 2nd person
        'съраахѫ', 'сърааху',                               # impft 3rd person
        'сърахъ', 'съраховѣ', 'сърахове', 'сърахомъ',       # aor. 1st person
        'съра', 'съраста', 'сърасте',                       # aor. 2nd person
        'сърашѧ', 'съраша',                                 # aor. 3rd person
        ## with the present-tense root vowel (imperfect only)
        'сераахъ', 'сераахомъ', 'серааховѣ', 'сераахове',   # impft 1st person
        'серааше', 'сераашете', 'сераашета',                # impft 2nd person
        'сераахѫ', 'серааху',                               # impft 3rd person
        ## with the present-tense root vowel and yat (imperfect only)
        'серѣахъ', 'серѣахомъ', 'серѣаховѣ', 'серѣахове',   # impft 1st person
        'серѣаше', 'серѣашете', 'серѣашета',                # impft 2nd person
        'серѣахѫ', 'серѣаху',                               # impft 3rd person
        ## with the present-tense root vowel and е (imperfect only)
        'сереахъ', 'сереахомъ', 'сереаховѣ', 'сереахове',   # impft 1st person
        'сереаше', 'сереашете', 'сереашета',                # impft 2nd person
        'сереахѫ', 'сереаху',                               # impft 3rd person
        ]
    srat.modern_splx_ipf = ['срать']
    srat.search_all()

    wb_sirat = ResultsSpreadsheet(filename="2015_08_20_verbSIRAT")
    wb_sirat.write_headers()
    ## verb 'pirat'
    sirat = RNCSearchTerm(start_row=2, results_spreadsheet=wb_sirat)
    sirat.suffix = "-a-"
    sirat.ancient_splx_ipf = ['сирати']
    sirat.old_inf = 'сирати'
    sirat.old_splx_ipf = [
        ## L-participle
        'сирал', 'сиралъ', 'сирала', 'сирало', 'сирали',    # L-participle
        ## aorist
        'сирахъ', 'сираховѣ', 'сирахове', 'сирахомъ',       # aor. 1st person
        'сира', 'сираста', 'сирасте',                       # aor. 2nd person
        'сирашѧ', 'сираша',                                 # aor. 3rd person
        ## imperfect with -a-
        'сираахъ', 'сираахомъ', 'сирааховѣ', 'сираахове',   # impft 1st person
        'сирааше', 'сираашете', 'сираашета',                # impft 2nd person
        'сираахѫ', 'сирааху',                               # impft 3rd person
        ## imperfect with -yat-
        'сирѣахъ', 'сирѣахомъ', 'сирѣаховѣ', 'сирѣахове',   # impft 1st person
        'сирѣаше', 'сирѣашете', 'сирѣашета',                # impft 2nd person
        'сирѣахѫ', 'сирѣаху',                               # impft 3rd person
        ## imperfect with -е-
        'сиреахъ', 'сиреахомъ', 'сиреаховѣ', 'сиреахове',   # impft 1st person
        'сиреаше', 'сиреашете', 'сиреашета',                # impft 2nd person
        'сиреахѫ', 'сиреаху',                               # impft 3rd person
        ]
    sirat.modern_splx_ipf = ['сирать']
    sirat.search_all()

def main_realer():

        ## BRAT / -BIRAT 'GATHER'
        wb_brat = ResultsSpreadsheet(filename="2015_08_22_verbBRATandBIRAT")
        wb_brat.write_headers()
        ## verb 'brat'
        brat = RNCSearchTerm(start_row=2, results_spreadsheet=wb_brat)
        brat.ancient_splx_ipf = ['брати', 'бьрати']
        brat.old_inf = 'брати'
        brat.old_splx_ipf = [
            ## without the front jer
            'брал', 'бралъ', 'брала', 'брало', 'брали',         # L-participle
            'браахъ', 'браахомъ', 'брааховѣ', 'браахове',       # impft 1st person
            'брааше', 'браашете', 'браашета',                   # impft 2nd person
            'браахѫ', 'брааху',                                 # impft 3rd person
            'брахъ', 'браховѣ', 'брахове', 'брахомъ',           # aor. 1st person
            'бра', 'браста', 'брасте',                          # aor. 2nd person
            'брашѧ', 'браша',                                   # aor. 3rd person
            ## with the front jer-
            'бьрал', 'бьралъ', 'бьрала', 'бьрало', 'бьрали',    # L-participle
            'бьраахъ', 'бьраахомъ', 'бьрааховѣ', 'бьраахове',   # impft 1st person
            'бьрааше', 'бьраашете', 'бьраашета',                # impft 2nd person
            'бьраахѫ', 'бьрааху',                               # impft 3rd person
            'бьрахъ', 'бьраховѣ', 'бьрахове', 'бьрахомъ',       # aor. 1st person
            'бьра', 'бьраста', 'бьрасте',                       # aor. 2nd person
            'бьрашѧ', 'бьраша',                                 # aor. 3rd person
            ## with the back jer
            'бърал', 'бъралъ', 'бърала', 'бърало', 'бърали',    # L-participle
            'бъраахъ', 'бъраахомъ', 'бърааховѣ', 'бъраахове',   # impft 1st person
            'бърааше', 'бъраашете', 'бъраашета',                # impft 2nd person
            'бъраахѫ', 'бърааху',                               # impft 3rd person
            'бърахъ', 'бъраховѣ', 'бърахове', 'бърахомъ',       # aor. 1st person
            'бъра', 'бъраста', 'бърасте',                       # aor. 2nd person
            'бърашѧ', 'бъраша',                                 # aor. 3rd person
            ## with the present-tense root vowel (imperfect only)
            'бераахъ', 'бераахомъ', 'берааховѣ', 'бераахове',   # impft 1st person
            'берааше', 'бераашете', 'бераашета',                # impft 2nd person
            'бераахѫ', 'берааху',                               # impft 3rd person
            ## with the present-tense root vowel and yat (imperfect only)
            'берѣахъ', 'берѣахомъ', 'берѣаховѣ', 'берѣахове',   # impft 1st person
            'берѣаше', 'берѣашете', 'берѣашета',                # impft 2nd person
            'берѣахѫ', 'берѣаху',                               # impft 3rd person
            ## with the present-tense root vowel and е (imperfect only)
            'береахъ', 'береахомъ', 'береаховѣ', 'береахове',   # impft 1st person
            'береаше', 'береашете', 'береашета',                # impft 2nd person
            'береахѫ', 'береаху',                               # impft 3rd person
            ]
        brat.modern_splx_ipf = ['брать']
        brat.search_all()
        ## verb 'birat'
        birat_start = brat.rw + 1
        birat = RNCSearchTerm(
            start_row=birat_start,
            results_spreadsheet=wb_brat
            )
        birat.suffix = "-a-"
        birat.ancient_splx_ipf = ['бирати']
        birat.old_inf = 'бирати'
        birat.old_splx_ipf = [
            ## L-participle
            'бирал', 'биралъ', 'бирала', 'бирало', 'бирали',    # L-participle
            ## aorist
            'бирахъ', 'бираховѣ', 'бирахове', 'бирахомъ',       # aor. 1st person
            'бира', 'бираста', 'бирасте',                       # aor. 2nd person
            'бирашѧ', 'бираша',                                 # aor. 3rd person
            ## imperfect with -a-
            'бираахъ', 'бираахомъ', 'бирааховѣ', 'бираахове',   # impft 1st person
            'бирааше', 'бираашете', 'бираашета',                # impft 2nd person
            'бираахѫ', 'бирааху',                               # impft 3rd person
            ## imperfect with -yat-
            'бирѣахъ', 'бирѣахомъ', 'бирѣаховѣ', 'бирѣахове',   # impft 1st person
            'бирѣаше', 'бирѣашете', 'бирѣашета',                # impft 2nd person
            'бирѣахѫ', 'бирѣаху',                               # impft 3rd person
            ## imperfect with -е-
            'биреахъ', 'биреахомъ', 'биреаховѣ', 'биреахове',   # impft 1st person
            'биреаше', 'биреашете', 'биреашета',                # impft 2nd person
            'биреахѫ', 'биреаху',                               # impft 3rd person
            ]
        birat.modern_splx_ipf = ['бирать']
        birat.search_all()

        ## MERET / -MIRAT 'die'
        wb_mreti = ResultsSpreadsheet(filename="2015_08_22_verbMERETandMIRAT")
        wb_mreti.write_headers()
        ## verb 'meret'
        mreti = RNCSearchTerm(start_row=2, results_spreadsheet=wb_mreti)
        mreti.ancient_splx_ipf = ['мрети', 'мрѣти', 'мерети']
        mreti.old_inf = 'мрѣти'
        mreti.old_splx_ipf = [
            ## with r + front jer vocalism
            'мрьл', 'мрьлъ', 'мрьла', 'мрьло', 'мрьли',       # L-participle
            'мьраахъ', 'мьраахомъ', 'мьрааховѣ', 'мьраахове', # impft 1st person
            'мьрѣахъ', 'мьрѣахомъ', 'мьрѣаховѣ', 'мьрѣахове', # impft 1st person
            'мьреахъ', 'мьреахомъ', 'мьреаховѣ', 'мьреахове', # impft 1st person
            'мьрааше', 'мьраашете', 'мьраашета',              # impft 2nd person
            'мьрѣаше', 'мьрѣашете', 'мьрѣашета',              # impft 2nd person
            'мьреаше', 'мьреашете', 'мьреашета',              # impft 2nd person
            'мьраахѫ', 'мьрааху',                             # impft 3rd person
            'мьрѣахѫ', 'мьрѣаху',                             # impft 3rd person
            'мьреахѫ', 'мьреаху',                             # impft 3rd person
            'мьрахъ', 'мьраховѣ', 'мьрахове', 'мьрахомъ',     # aor. 1st person
            'мьрѣхъ', 'мьрѣховѣ', 'мьрѣхове', 'мьрѣхомъ',     # aor. 1st person
            'мьрехъ', 'мьреховѣ', 'мьрехове', 'мьрехомъ',     # aor. 1st person
            'мьра', 'мьраста', 'мьрасте',                     # aor. 2nd person
            'мьрѣ', 'мьрѣста', 'мьрѣсте',                     # aor. 2nd person
            'мьре', 'мьреста', 'мьресте',                     # aor. 2nd person
            'мьрашѧ', 'мьраша',                               # aor. 3rd person
            'мьрѣшѧ', 'мьрѣша',                               # aor. 3rd person
            'мьрешѧ', 'мьреша',                               # aor. 3rd person

            ## with r + back jer vocalism
            'мръл', 'мрълъ', 'мръла', 'мръло', 'мръли',       # L-participle
            'мъраахъ', 'мъраахомъ', 'мърааховѣ', 'мъраахове', # impft 1st person
            'мърѣахъ', 'мърѣахомъ', 'мърѣаховѣ', 'мърѣахове', # impft 1st person
            'мъреахъ', 'мъреахомъ', 'мъреаховѣ', 'мъреахове', # impft 1st person
            'мърааше', 'мъраашете', 'мъраашета',              # impft 2nd person
            'мърѣаше', 'мърѣашете', 'мърѣашета',              # impft 2nd person
            'мъреаше', 'мъреашете', 'мъреашета',              # impft 2nd person
            'мъраахѫ', 'мърааху',                             # impft 3rd person
            'мърѣахѫ', 'мърѣаху',                             # impft 3rd person
            'мъреахѫ', 'мъреаху',                             # impft 3rd person
            'мърахъ', 'мъраховѣ', 'мърахове', 'мърахомъ',     # aor. 1st person
            'мърѣхъ', 'мърѣховѣ', 'мърѣхове', 'мърѣхомъ',     # aor. 1st person
            'мърехъ', 'мъреховѣ', 'мърехове', 'мърехомъ',     # aor. 1st person
            'мъра', 'мъраста', 'мърасте',                     # aor. 2nd person
            'мърѣ', 'мърѣста', 'мърѣсте',                     # aor. 2nd person
            'мъре', 'мъреста', 'мъресте',                     # aor. 2nd person
            'мърашѧ', 'мъраша',                               # aor. 3rd person
            'мърѣшѧ', 'мърѣша',                               # aor. 3rd person
            'мърешѧ', 'мъреша',                               # aor. 3rd person

            ## with r + no jer vocalism
            'мрл', 'мрлъ', 'мрла', 'мрло', 'мрли',            # L-participle
            'мраахъ', 'мраахомъ', 'мрааховѣ', 'мраахове',     # impft 1st person
            'мрѣахъ', 'мрѣахомъ', 'мрѣаховѣ', 'мрѣахове',     # impft 1st person
            'мреахъ', 'мреахомъ', 'мреаховѣ', 'мреахове',     # impft 1st person
            'мрааше', 'мраашете', 'мраашета',                 # impft 2nd person
            'мрѣаше', 'мрѣашете', 'мрѣашета',                 # impft 2nd person
            'мреаше', 'мреашете', 'мреашета',                 # impft 2nd person
            'мраахѫ', 'мрааху',                               # impft 3rd person
            'мрѣахѫ', 'мрѣаху',                               # impft 3rd person
            'мреахѫ', 'мреаху',                               # impft 3rd person
            'мрахъ', 'мраховѣ', 'мрахове', 'мрахомъ',         # aor. 1st person
            'мрѣхъ', 'мрѣховѣ', 'мрѣхове', 'мрѣхомъ',         # aor. 1st person
            'мрехъ', 'мреховѣ', 'мрехове', 'мрехомъ',         # aor. 1st person
            'мра', 'мраста', 'мрасте',                        # aor. 2nd person
            'мрѣ', 'мрѣста', 'мрѣсте',                        # aor. 2nd person
            'мре', 'мреста', 'мресте',                        # aor. 2nd person
            'мрашѧ', 'мраша',                                 # aor. 3rd person
            'мрѣшѧ', 'мрѣша',                                 # aor. 3rd person
            'мрешѧ', 'мреша',                                 # aor. 3rd person

            ## with yat + r vocalism
            'мѣрл', 'мѣрлъ', 'мѣрла', 'мѣрло', 'мѣрли',       # L-participle
            'мѣраахъ', 'мѣраахомъ', 'мѣрааховѣ', 'мѣраахове', # impft 1st person
            'мѣрѣахъ', 'мѣрѣахомъ', 'мѣрѣаховѣ', 'мѣрѣахове', # impft 1st person
            'мѣреахъ', 'мѣреахомъ', 'мѣреаховѣ', 'мѣреахове', # impft 1st person
            'мѣрааше', 'мѣраашете', 'мѣраашета',              # impft 2nd person
            'мѣрѣаше', 'мѣрѣашете', 'мѣрѣашета',              # impft 2nd person
            'мѣреаше', 'мѣреашете', 'мѣреашета',              # impft 2nd person
            'мѣраахѫ', 'мѣрааху',                             # impft 3rd person
            'мѣрѣахѫ', 'мѣрѣаху',                             # impft 3rd person
            'мѣреахѫ', 'мѣреаху',                             # impft 3rd person
            'мѣрахъ', 'мѣраховѣ', 'мѣрахове', 'мѣрахомъ',     # aor. 1st person
            'мѣрахъ', 'мѣраховѣ', 'мѣрахове', 'мѣрахомъ',     # aor. 1st person
            'мѣрахъ', 'мѣраховѣ', 'мѣрахове', 'мѣрахомъ',     # aor. 1st person
            'мѣра', 'мѣраста', 'мѣрасте',                     # aor. 2nd person
            'мѣрѣ', 'мѣрѣста', 'мѣрѣсте',                     # aor. 2nd person
            'мѣре', 'мѣреста', 'мѣресте',                     # aor. 2nd person
            'мѣрашѧ', 'мѣраша',                               # aor. 3rd person
            'мѣрѣшѧ', 'мѣрѣша',                               # aor. 3rd person
            'мѣрешѧ', 'мѣреша',                               # aor. 3rd person

            ## with е + r vocalism
            'мерл', 'мерлъ', 'мерла', 'мерло', 'мерли',       # L-participle
            'мераахъ', 'мераахомъ', 'мерааховѣ', 'мераахове', # impft 1st person
            'мерѣахъ', 'мерѣахомъ', 'мерѣаховѣ', 'мерѣахове', # impft 1st person
            'мереахъ', 'мереахомъ', 'мереаховѣ', 'мереахове', # impft 1st person
            'мерааше', 'мераашете', 'мераашета',              # impft 2nd person
            'мерѣаше', 'мерѣашете', 'мерѣашета',              # impft 2nd person
            'мереаше', 'мереашете', 'мереашета',              # impft 2nd person
            'мераахѫ', 'мерааху',                             # impft 3rd person
            'мерѣахѫ', 'мерѣаху',                             # impft 3rd person
            'мереахѫ', 'мереаху',                             # impft 3rd person
            'мерахъ', 'мераховѣ', 'мерахове', 'мерахомъ',     # aor. 1st person
            'мерѣхъ', 'мерѣховѣ', 'мерѣхове', 'мерѣхомъ',     # aor. 1st person
            'мерехъ', 'мереховѣ', 'мерехове', 'мерехомъ',     # aor. 1st person
            'мера', 'мераста', 'мерасте',                     # aor. 2nd person
            'мерѣ', 'мерѣста', 'мерѣсте',                     # aor. 2nd person
            'мере', 'мерѣста', 'мересте',                     # aor. 2nd person
            'мерашѧ', 'мераша',                               # aor. 3rd person
            'мерѣшѧ', 'мерѣша',                               # aor. 3rd person
            'мерешѧ', 'мереша',                               # aor. 3rd person

            ]
        mreti.modern_splx_ipf = ['мереть']
        mreti.search_all()
        ## verb 'birat'
        mirat_start = mreti.rw + 1
        mirat = RNCSearchTerm(
            start_row=mirat_start,
            results_spreadsheet=wb_mreti
            )
        mirat.suffix = "-a-"
        mirat.ancient_splx_ipf = ['мирати']
        mirat.old_inf = 'мирати'
        mirat.old_splx_ipf = [
            ## L-participle
            'мирал', 'миралъ', 'мирала', 'мирало', 'мирали',    # L-participle
            ## aorist
            'мирахъ', 'мираховѣ', 'мирахове', 'мирахомъ',       # aor. 1st person
            'мира', 'мираста', 'мирасте',                       # aor. 2nd person
            'мирашѧ', 'мираша',                                 # aor. 3rd person
            ## imperfect with -a-
            'мираахъ', 'мираахомъ', 'мирааховѣ', 'мираахове',   # impft 1st person
            'мирааше', 'мираашете', 'мираашета',                # impft 2nd person
            'мираахѫ', 'мирааху',                               # impft 3rd person
            ## imperfect with -yat-
            'мирѣахъ', 'мирѣахомъ', 'мирѣаховѣ', 'мирѣахове',   # impft 1st person
            'мирѣаше', 'мирѣашете', 'мирѣашета',                # impft 2nd person
            'мирѣахѫ', 'мирѣаху',                               # impft 3rd person
            ## imperfect with -е-
            'миреахъ', 'миреахомъ', 'миреаховѣ', 'миреахове',   # impft 1st person
            'миреаше', 'миреашете', 'миреашета',                # impft 2nd person
            'миреахѫ', 'миреаху',                               # impft 3rd person
            ]
        mirat.modern_splx_ipf = ['мирать']
        mirat.search_all()

if __name__ == "__main__":
    main_realer()
