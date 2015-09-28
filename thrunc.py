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
import sqlite3
import codecs
import random
import openpyxl

try:
    import xml.etree.cElementTree as ET
except ImportError as e:
    print "ImportError: {}\nUsing non-C implementation of ET".format(e)
    import xml.etree.ElementTree as ET

def to_unicode_or_bust(obj, encoding='utf-8'):
    ## by Kumar McMillan ( http://farmdev.com/talks/unicode/ )
    """Ensure that an object is unicode."""
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj

class SearchList(object):
    """An XML document containing a list of search terms."""

    def __init__(self, file_name):
        """Initialize XML file object.

        Parameters
        ----------
          file_name (str): name of the XML file. It will be created if it
            does not already exist.
        """
        self.exists = False
        if file_name.endswith(".xml"):
            self.file_name = file_name
        else:
            self.file_name = file_name + ".xml"
        self.unicode_parser = ET.XMLParser(encoding='utf-8')
        self.check_if_exists(filename=self.file_name)

    def check_if_exists(self, filename):
        """Create an XML file if one doesn't exist already."""
        try:
            self.tree = ET.parse(self.file_name, parser=self.unicode_parser)
            self.root = self.tree.getroot()
            print "Search XML file already exists."
            self.exists = True
        except IOError as e:
            print "IOError: {}".format(e)
            self.root = ET.Element("searchList")
            print "Search XML file didn't exist, so I made one."
            self.exists = False

    def add_search_to_list(self, base_verb=u"", derived_verb=u"",
                           dv_pfx=u"", dv_pfx_name=u"", dv_sfx=u"",
                           dv_sfx_name=u"", dv_sec=False, dv_rfx=False):
        """Add an element to the XML file containing a new search query.

        Parameters
        ----------
          base_verb (unicode): basic verb form / center of verb constellation
            (e.g., читать or писать, but not прочитать or переписывать)
          derived_verb (unicode): derived verb form, possibly with prefix,
            suffix, or both (e.g., читать, писать, прочитать, or переписывать)
          df_pfx (unicode): specific form of the prefix occurring on the given
            derived verb (e.g., надо in надобрать)
          df_pfx_name (unicode): 'standard' or 'referring' name of the prefix
            occurring on the given verb
          df_sfx (unicode): specific form of the suffix occurring on the given
            derived verb (e.g., ыва in перечитывать)
          df_sfx_name (unicode): 'standard' or 'referring' name of the suffix
            occurring on the given verb (e.g., '-yva-' for перечитывать)
          subcorpus (unicode): name of the subcorpus in which the search will
            take place (i.e., u'Modern', u'Old', or u'Ancient')
          dv_sec (boolean): True if secondary imperfective, False otherwise
          dv_rfx (boolean): True if a -ся verb, False otherwise

        Returns
        -------
          If a <baseVerb> element does not exist (as a child of the root) with
            @simplex="base_verb", one is created.
          If a <derivedVerb> element does not exist (as a child of the baseVerb
            element), one is created.

        Sample output
        -------------
          <baseVerb idx="1" simplex="читать" dateAdded="2015-09-27"
            timeAdded="10:44:36 CST">
              <derivedVerb idx="1" prefixed="yes" suffixed="no" secondary="no"
                reflexive="no">
                  <prefix prefixName="nad-">надо</prefix>
                  <suffix suffixName="-aj-">а</suffix>
                  <fullVerb>надочитать</fullVerb>
              </derivedVerb>
          </baseVerb>
        """
        date_created = to_unicode_or_bust(time.strftime("%Y-%m-%d"))
        time_created = to_unicode_or_bust(time.strftime("%H:%M:%S %Z"))

        if derived_verb.endswith(u"ся") or derived_verb.endswith(u"сь"):
            dv_rfx=True

        bv_exists = False
        lb = len(self.root.findall(u'baseVerb'))
        for verb in self.root.findall(u'baseVerb'):
            if verb.get(u'simplex') == base_verb:
                bv = verb
                bv_exists = True

        if bv_exists == False:
            bv = ET.SubElement(self.root, u"baseVerb")
            bv.set(u"idx", u"{}".format(lb + 1))
            bv.set(u"simplex", u"{}".format(base_verb))
            bv.set(u"dateCreated", u"{}".format(date_created))
            bv.set(u"timeCreated", u"{}".format(time_created))
            bv_exists = True

        if bv_exists == True:

            dv_exists = False
            ld = len(bv.findall(u'derivedVerb'))
            for dverb in bv.findall(u'derivedVerb'):
                for fdv in dverb.findall(u'fullVerb'):
                    if fdv.text is not None:
                        if fdv.text == derived_verb:
                            dv_exists = True

            if dv_exists == False:
                dv = ET.SubElement(bv, u"derivedVerb")
                dv.set(u"idx", u"{}".format(ld + 1))
                dv.set(u"dateCreated", u"{}".format(date_created))
                dv.set(u"timeCreated", u"{}".format(time_created))

                if dv_pfx == u"":
                    dv.set(u"prefixed", u"no")
                    dvp = ET.SubElement(dv, u"prefix")
                    dvp.set(u"prefixName", u"")
                else:
                    dv.set(u"prefixed", u"yes")
                    dvp = ET.SubElement(dv, u"prefix")
                    dvp.set(u"prefixName", u"{}".format(dv_pfx_name))
                    dvp.text = dv_pfx

                if dv_sfx == u"":
                    dv.set(u"suffixed", u"no")
                    dvs = ET.SubElement(dv, u"suffix")
                    dvs.set(u"suffixName", u"")
                else:
                    dv.set(u"suffixed", u"yes")
                    dvs = ET.SubElement(dv, u"suffix")
                    dvs.set(u"suffixName", u"{}".format(dv_sfx_name))
                    dvs.text = dv_sfx

                if dv_rfx == True:
                    dv.set(u"reflexive", u"yes")
                else:
                    dv.set(u"reflexive", u"no")

                if dv_sec == True:
                    dv.set(u"secondary", u"yes")
                else:
                    dv.set(u"secondary", u"no")

                dvf = ET.SubElement(dv, u"fullVerb")
                dvf.text = derived_verb

                ## create <query> element
                qe = ET.SubElement(dv, u"query")
                qe.set(u"subcorpus", u'modern')
                qe.set(u"successful", u"no")
                qe.set(u"dateCreated", u"{}".format(date_created))
                qe.set(u"timeCreated", u"{}".format(time_created))

                ## add a <results> element, but don't populate it yet
                rs = ET.SubElement(qe, u"results")

    def search_modern(self, bv, dv, gramm_cat="praet", end_year=1899):
        """Search the modern subcorpus for the contents of a <derivedVerb>.

        Parameters
        ----------
          bv (ET.Element): a base verb element (parent of dv)
          dv (ET.Element): a derived verb element (child of bv)
          gramm_cat (str): grammatical category to search for
          end_year (int): limit searches to sources created prior to this year
        """

        qu = dv.find(u'query')
        if qu is None:
            qu = ET.SubElement(dv, u'query')

        if qu.get(u'successful') == u'no':

            rs = qu.find(u'results')
            if rs is None:
                rs = ET.SubElement(qu, u'results')

            base_verb = bv.get(u'simplex')
            pfx_status = dv.get(u'prefixed')
            sfx_status = dv.get(u'suffixed')
            ## get prefix information
            pfxe = dv.find(u'prefix')
            pfx_name = pfxe.get(u'prefixName')
            pfx = pfxe.text
            ## get suffix information
            sfxe = dv.find(u'suffix')
            sfx_name = sfxe.get(u'suffixName')
            sfx = sfxe.text
            ## get full verb information
            fve = dv.find(u'fullVerb')
            full_verb = fve.text

            query = RNCQueryModern(
                lex1=full_verb.encode('utf-8'),
                gramm1=gramm_cat.encode('utf-8'),
                end_year=u"{}".format(end_year).encode('utf-8')
            )
            search = RNCSearch(
                rnc_query=query,
                subcorpus=u"modern".encode('utf-8'),
                pfx_val=pfx_status.encode('utf-8'),
                prefix=pfx_name.encode('utf-8'),
                sfx_val=sfx_status.encode('utf-8'),
                ## the next line raises an AttributeError if sfx is None
                #suffix=sfx.encode('utf-8'),
                suffix=sfx,
                lem=full_verb.encode('utf-8'),
                gramm_cat=gramm_cat.encode('utf-8'),
                base_verb=base_verb.encode('utf-8')
                )
            search.scrape_pages()
            for d in search.all_search_results:
                for i in range(d[13]+1):
                    re = ET.SubElement(rs, u'result')
                    re.set(u'pageIndex', u"{}".format(d[14]))
                    sn = ET.SubElement(re, u'sourceName')
                    sn.text = u"{}".format(d[9])
                    sn.set(u'begDate', u"{}".format(d[10]))
                    sn.set(u'centerDate', u"{}".format(d[11]))
                    sn.set(u'endDate', u"{}".format(d[12]))
            q = dv.find(u'query')
            q.set(u'successful', u'yes')

    def check(self):
        """Print XML as string to console."""
        xmlstr = ET.tostring(self.root, encoding='utf8', method='xml')
        print xmlstr

    def write(self):
        """Save XML to disk."""
        tree = ET.ElementTree(self.root)
        tree.write(self.file_name, encoding='utf-8', xml_declaration=True)

    def run(self):
        """Run all possible searches of <derivedVerb> elements."""
        pass

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
                stream.write(u"\n")
                for k, v in header_dict.iteritems():
                    u_v = to_unicode_or_bust(v)
                    try:
                        stream.write(u"{};".format(u_v))
                    except UnicodeDecodeError as e:
                        print "UDE: {}".format(e)
                        raise
                    except UnicodeEncodeError as e:
                        print "UEE: {}".format(e)
                        raise

        except Exception as e:
            print "Exception: {}".format(e)
            raise

    def write_dicts_to_txt(self, list_of_dicts):
        """Write each dict in a list of dicts to a plain-text file."""

        try:
            with codecs.open(self.textfile, "a", encoding="utf-8") as stream:
                for d in list_of_dicts:
                    stream.write(u"\n")
                    for k, v in d.iteritems():
                        u_v = to_unicode_or_bust(v)
                        try:
                            stream.write(u"{};".format(u_v))
                        except UnicodeDecodeError as e:
                            print "UDE: {}".format(e)
                            raise
                        except UnicodeEncodeError as e:
                            print "UEE: {}".format(e)
                            raise

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
                if page.soup.ol.contents:
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
        self.old_stems_vowel = []     # e.g., бьра, бра, бъра
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

    def get_old_forms(self, stem_list_vowel, stem_list_consonant):
        # generate possible forms for the 'old' subcorpus
        self.all_old_forms = []
        for v_stem in stem_list_vowel:
            for ending in self.old_postvowel_endings:
                self.all_old_forms.append(v_stem + ending)
        for c_stem in stem_list_consonant:
            for ending in self.old_postconsonant_endings:
                self.all_old_forms.append(c_stem + ending)

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
                            self.rs.write_dicts_to_txt(
                                search.all_search_results
                                )

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
                        self.rs.write_dicts_to_txt(
                            search.all_search_results
                            )


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
                            self.rs.write_dicts_to_txt(
                                search.all_search_results
                                )

    def search_all(self):
        """Perform an RNCSearch for each possible word in the RNCSearchTerm."""

        ## search all three subcorpora
        self.search_ancient()
        self.search_old()
        self.search_modern()

        ## save the results spreadsheet to disk
        self.rs.save_wb()

def main():
    db_name = u"verbpairs.db"
    conn = sqlite3.connect(db_name)
    crsr = conn.cursor()
    try:
        crsr.execute(u"CREATE TABLE verbs (ID INT, unix REAL, dateStamp TEXT," \
                     u" ipfVerb TEXT, pfVerb TEXT, prefix TEXT)")
    except sqlite3.OperationalError as e:
        print u"OperationalError: {}".format(e)
        pass

    idx = 0
    verb_list = u"verbpairs.txt"
    with codecs.open(verb_list, mode="r", encoding="utf-8") as stream:
        all_lines = stream.read().split(u"\n")
        for line in all_lines[:100]:
            if not line.startswith(u"#"):
                idx += 1
                parts = line.split(u";")
                #print u"{} ==========".format(idx)
                #print u"IPF verb:\n\t{}".format(parts[0])
                #print u"PF verb:\n\t{}".format(parts[1])
                #print u"Prefix:\n\t{}-".format(parts[2])
                crsr.execute(
                    u"INSERT INTO verbs VALUES ({}, {}, '{}', " \
                    u"'{}', '{}', '{}')".format(idx, 100, u'2015-09-15',
                    parts[0],
                    parts[1],
                    parts[2])
                    )
                conn.commit()
                print u"{};{};{};{}".format(
                    idx, parts[0], parts[1], parts[2]
                    )
        sql_get = u"SELECT * FROM verbs WHERE prefix =?"
        pfx = u"вз"
        for row in crsr.execute(sql_get, [(pfx)]):
            for itm in row:
                print u"{}, ".format(itm),
            print u""

def main_two():
    x = SearchList(file_name='xmltest.xml')
    x.check()
    x.write()

def build_xml_search_list(xml_name):
    xl = SearchList(file_name=xml_name)
    if xl.exists == True:
        print "SearchList exists!"
    if xl.exists == False:
        print "SearchList doesn't exist, so we're creating one."
    xl.check()
    for p in [u'по', u'вз', u'под', u'с', u'пере']:
        base_verb = u"делать"
        derived_verb = p + base_verb
        dv_pfx = p
        dv_pfx_name = u"{}-".format(p)
        dv_sfx = u'ай'
        dv_sfx_name = u'-aj-'
        xl.add_search_to_list(base_verb=base_verb,
                              derived_verb=derived_verb, dv_pfx=dv_pfx,
                              dv_pfx_name=dv_pfx_name, dv_sfx=dv_sfx,
                              dv_sfx_name=dv_sfx_name, subcorpus="modern",
                              dv_rfx=False)
    xl.check()
    xl.write()

def create_real_search_list(xml_name):
    """Build an XML search list from RussianVerb objects."""
    verbs = ["драть"]
    for verb in verbs:
        rv = RussianVerb(simplex_verb=verb)
        for pfx_name, pfx_list in rv.prefixes.iteritems():
            for pfx in pfx_list:
                sl = SearchList(file_name=xml_name)
                sl.add_search_to_list(
                    base_verb=to_unicode_or_bust(rv.root),
                    derived_verb=to_unicode_or_bust(pfx + rv.root),
                    dv_pfx=to_unicode_or_bust(pfx),
                    dv_pfx_name=to_unicode_or_bust(pfx_name)
                )
                # sl.check()
                sl.write()

def run_for_real(xml_name):
    while True:
        s = SearchList(file_name=xml_name)
        for bv in s.root.findall(u'baseVerb'):
            for dv in bv.findall(u'derivedVerb'):
                s.search_modern(bv=bv, dv=dv)
                s.write()
                time.sleep(5)

        if s.root.findall(u'.//[@successful=no]') is None:
            break


if __name__ == "__main__":
    #main_two()
    #build_xml_search_list(xml_name="test_search_list.xml")
    xml_fn = "actual_test.xml"
    create_real_search_list(xml_name=xml_fn)
    run_for_real(xml_name=xml_fn)
