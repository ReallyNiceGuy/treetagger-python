# -*- coding: utf-8 -*-
# Natural Language Toolkit: Interface to the TreeTagger POS-tagger
#
# Copyright (C) Mirko Otto
# Author: Mirko Otto <dropsy@gmail.com>

"""
A Python module for interfacing with the Treetagger by Helmut Schmid.
"""

import os, tempfile
from subprocess import Popen, PIPE

from nltk.internals import find_binary, find_file
from nltk.tag.api import TaggerI
from sys import platform as _platform

_treetagger_url = 'http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/'

_treetagger_languages = ['bulgarian', 'dutch', 'english', 'estonian', 'finnish', 'french', 'galician', 'german', 'italian', 'polish', 'portuguese', 'portuguese-finegrained', 'russian', 'slovak', 'slovak2', 'spanish']

class TreeTagger(TaggerI):
    r"""
    A class for pos tagging with TreeTagger. The default encoding used by TreeTagger is utf-8. The input is the paths to:
     - a language trained on training data
     - (optionally) the path to the TreeTagger binary

    This class communicates with the TreeTagger binary via pipes.

    Example:

    .. doctest::
        :options: +SKIP

        >>> from treetagger import TreeTagger
        >>> tt = TreeTagger(language='english')
        >>> tt.tag('What is the airspeed of an unladen swallow ?')
        [['What', 'WP', 'What'],
         ['is', 'VBZ', 'be'],
         ['the', 'DT', 'the'],
         ['airspeed', 'NN', 'airspeed'],
         ['of', 'IN', 'of'],
         ['an', 'DT', 'an'],
         ['unladen', 'JJ', '<unknown>'],
         ['swallow', 'NN', 'swallow'],
         ['?', 'SENT', '?']]

    .. doctest::
        :options: +SKIP

        >>> from treetagger import TreeTagger
        >>> tt = TreeTagger(language='german')
        >>> tt.tag('Das Haus hat einen großen hübschen Garten.')
        [['Das', 'ART', 'die'],
         ['Haus', 'NN', 'Haus'],
         ['hat', 'VAFIN', 'haben'],
         ['einen', 'ART', 'eine'],
         ['großen', 'ADJA', 'groß'],
         ['hübschen', 'ADJA', 'hübsch'],
         ['Garten', 'NN', 'Garten'],
         ['.', '$.', '.']]
    """

    def __init__(self, path_to_home=None, language='german', 
                 verbose=False, abbreviation_list=None):
        """
        Initialize the TreeTagger.

        :param path_to_home: The TreeTagger binary.
        :param language: Default language is german.

        The encoding used by the model. Unicode tokens
        passed to the tag() and batch_tag() methods are converted to
        this charset when they are sent to TreeTagger.
        The default is utf-8.

        This parameter is ignored for str tokens, which are sent as-is.
        The caller must ensure that tokens are encoded in the right charset.
        """
        treetagger_paths = ['.', '/usr/bin', '/usr/local/bin', '/opt/local/bin',
                        '/Applications/bin', '~/bin', '~/Applications/bin',
                        '~/work/tmp/treetagger/cmd', '~/tree-tagger/cmd']
        treetagger_paths = list(map(os.path.expanduser, treetagger_paths))
        self._abbr_list = abbreviation_list

        if language in _treetagger_languages:
            if _platform == "win32":
                treetagger_bin_name = 'tag-' + language
            else:
                treetagger_bin_name = 'tree-tagger-' + language
        else:
            raise LookupError('Language not in language list!')

        try:
            self._treetagger_bin = find_binary(
                treetagger_bin_name, path_to_home,
                env_vars=('TREETAGGER', 'TREETAGGER_HOME'),
                searchpath=treetagger_paths,
                url=_treetagger_url,
                verbose=verbose)
        except LookupError:
            print('NLTK was unable to find the TreeTagger bin!')

    def tag(self, sentences):
        """Tags a single sentence: a list of words.
        The tokens should not contain any newline characters.
        """

        # Write the actual sentences to the temporary input file
        if isinstance(sentences, list):
            _input = '\n'.join((x for x in sentences))
        else:
            _input = sentences

        if hasattr(_input,'read') :
            infile = _input
        else:
            infile = PIPE
        # Run the tagger and get the output
        outfile = tempfile.TemporaryFile(mode="w+",encoding="utf8")
        if(self._abbr_list is None):
            p = Popen([self._treetagger_bin],
                        shell=False, stdin=infile, stdout=outfile, stderr=PIPE)
        elif(self._abbr_list is not None):
            p = Popen([self._treetagger_bin,"-a",self._abbr_list],
                        shell=False, stdin=infile, stdout=outfile, stderr=PIPE)

        #(stdout, stderr) = p.communicate(bytes(_input, 'UTF-8'))
        if hasattr(_input,'read') :
            (stdout, stderr) = p.communicate()
        else:
            (stdout, stderr) = p.communicate(str(_input).encode('utf-8'))

        # Check the return code.
        if p.returncode != 0:
            print(stderr)
            raise OSError('TreeTagger command failed!')

        outfile.seek(0)
        # Output the tagged sentences
        for tagged_line in outfile:
            tagged_word_split = tagged_line.strip().split('\t')
            yield tagged_word_split

    @staticmethod
    def languages():
        return _treetagger_languages

if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
