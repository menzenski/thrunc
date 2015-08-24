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

    def __init__(self, filename, csv=False):
        """Initialize results spreadsheet.

        Parameters
        ----------
          filename: name of the results spreadsheet (and of csv if selected)
          csv: True or False — write output to a plain-text file also.
        """
        super(ResultsSpreadsheet, self).__init__()
        self.filename = filename
        self.active.title = "Results"
        if csv == True:
            self.textfile = self.filename + ".txt"

    def write_row(self, row_idx, dict_contents):
        """Write dict to row number row_idx in the ResultsSpreadsheet.

        Parameters
        ----------
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

        try:
            with codecs.open(self.textfile, "a", encoding="utf-8") as stream:
                for k, v in header_dict.iteritems():
                    stream.write("{};".format(v.encode('utf-8')))
        except Exception as e:
            print "Exception: {}".format(e)
            raise

    def write_dicts_to_txt(self, list_of_dicts):
        """Write each dict in a list of dicts to a plain-text file."""

        try:
            with codecs.open(self.textfile, "a", encoding="utf-8") as stream:
                for d in list_of_dicts:
                    for k, v in d.iteritems():
                        stream.write("{};".format(v.encode('utf-8')))

        except Exception as e:
            print "Exception: {}".format(e)
            raise


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

        ## possible imperfect/aorist/L-participle endings, rather than
        ## type them all out for each verb individually.
        ## some endings follow vowels
        self.old_theme_vowel = []     # e.g., бьра, бра, бъра
        self.old_stems_consonant = [] # e.g., бьр, бр, бър
        self.old_postvowel_endings = [
        ## L-participle
        'л', 'лъ', 'ла', 'ло', 'ли',
        ]
        ## while some follow consonants
        self.old_postconsonant_endings = [
        ## imperfect with -a-
        'аахъ', 'аахомъ', 'ааховѣ', 'аахове', # 1st person
        'ааше', 'аашете', 'аашета',           # 2nd person
        'аахѫ', 'ааху',                       # 3rd person
        ## imperfect with -ѣ-
        'ѣахъ', 'ѣахомъ', 'ѣаховѣ', 'ѣахове', # 1st person
        'ѣаше', 'ѣашете', 'ѣашета',           # 2nd person
        'ѣахѫ', 'ѣаху',                       # 3rd person
        ## imperfect with -е-
        'еахъ', 'еахомъ', 'еаховѣ', 'еахове', # 1st person
        'еаше', 'еашете', 'еашета',           # 2nd person
        'еахѫ', 'еаху',                       # 3rd person
        ## aorist with -a-
        'ахъ', 'аховѣ', 'ахове', 'ахомъ',     # 1st person
        'а', 'аста', 'асте',                  # 2nd person
        'ашѧ', 'аша',                         # 3rd person
        ## aorist with -ѣ-
        'ѣхъ', 'ѣховѣ', 'ѣхове', 'ѣхомъ',     # 1st person
        'ѣ', 'ѣста', 'ѣсте',                  # 2nd person
        'ѣшѧ', 'ѣша',                         # 3rd person
        ## aorist with -е-
        'ехъ', 'еховѣ', 'ехове', 'ехомъ',     # 1st person
        'е', 'еста', 'есте',                  # 2nd person
        'ашѧ', 'аша',                         # 3rd person
        ]

        # generate possible forms for the 'old' subcorpus
        self.all_old_forms = []
        for stem in self.old_stems_vowel:
            for ending in self.old_postvowel_endings:
                self.all_old_forms.append(stem + ending)
        for stem in self.old_stems_consonant:
            for ending in self.old_postconsonant_endings:
                self.all_old_forms.append(stem + ending)

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

                        #if self.rs:
                        #    for d in search.all_search_results:
                        #        for i in range(d[13]):
                        #            self.rs.write_row(
                        #                row_idx=self.rw, dict_contents=d
                        #                )
                        #            self.rw += 1
                        if self.rs:
                            for d in search.all_search_results:
                                self.rs.write_row(
                                    row_idx=self.rw, dict_contents=d
                                    )
                                self.rw += 1
                            self.rs.write_dicts_to_txt(all_search_results)

    def search_old(self):
        """Search the old subcorpus."""

        for verb_form in self.all_old_forms:
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

                    #if self.rs:
                    #    for d in search.all_search_results:
                    #        for i in range(d[13]):
                    #            self.rs.write_row(
                    #                row_idx=self.rw, dict_contents=d
                    #                )
                    #            self.rw += 1
                    if self.rs:
                        for d in search.all_search_results:
                            self.rs.write_row(
                                row_idx=self.rw, dict_contents=d
                                )
                            self.rw += 1
                        self.rs.write_dicts_to_txt(all_search_results)


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

                        #if self.rs:
                        #    for d in search.all_search_results:
                        #        for i in range(d[13]):
                        #            self.rs.write_row(
                        #                row_idx=self.rw, dict_contents=d
                        #                )
                        #            self.rw += 1
                        if self.rs:
                            for d in search.all_search_results:
                                self.rs.write_row(
                                    row_idx=self.rw, dict_contents=d
                                    )
                                self.rw += 1
                            self.rs.write_dicts_to_txt(all_search_results)

    def search_all(self):
        """Perform an RNCSearch for each possible word in the RNCSearchTerm."""

        ## search all three subcorpora
        self.search_ancient()
        self.search_old()
        self.search_modern()

        ## save the results spreadsheet to disk
        self.rs.save_wb()

def main():
        ## MERET / -MIRAT 'die'
        wb_mreti = ResultsSpreadsheet(filename="2015_08_23_verbMERETandMIRAT")
        wb_mreti.write_headers()
        ## verb 'meret'
        mreti = RNCSearchTerm(start_row=2, results_spreadsheet=wb_mreti)
        mreti.ancient_splx_ipf = ['мрети', 'мрѣти', 'мерети']
        mreti.old_inf = 'мрѣти'
        mreti.old_stems_vowel = ['мрь', 'мръ', 'мр', 'мре', 'мрѣ']
        mreti.old_stems_consonant = ['мр', 'мьр', 'мър', 'мер', 'мѣр']
        mreti.modern_splx_ipf = ['мереть']

        mreti.search_all()
        ## verb 'mirat'
        mirat_start = mreti.rw + 1
        mirat = RNCSearchTerm(
            start_row=mirat_start,
            results_spreadsheet=wb_mreti
            )
        mirat.suffix = "-a-"
        mirat.ancient_splx_ipf = ['мирати']
        mirat.old_inf = 'мирати'
        mirat.old_stems_vowel = ['мира']
        mirat.old_stems_consonant = ['мир']
        mirat.modern_splx_ipf = ['мирать']
        mirat.search_all()

        ## BRAT / -BIRAT 'GATHER'
        wb_brat = ResultsSpreadsheet(filename="2015_08_23_verbBRATandBIRAT")
        wb_brat.write_headers()
        ## verb 'brat'
        brat = RNCSearchTerm(start_row=2, results_spreadsheet=wb_brat)
        brat.ancient_splx_ipf = ['брати', 'бьрати']
        brat.old_inf = 'брати'
        brat.old_stems_vowel = ['бьра', 'бъра', 'бра']
        brat.old_stems_consonant = ['бьр', 'бър', 'бр']
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
        birat.old_stems_vowel = ['бира']
        birat.old_stems_consonant = ['бир']
        birat.modern_splx_ipf = ['бирать']
        birat.search_all()

if __name__ == "__main__":
    main()
