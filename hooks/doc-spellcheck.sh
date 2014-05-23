#!/bin/bash
# Spellcheck the HTML docs.
#
# If there are misspellings in the HTML docs, fix them in the source--not just
# in the HTML files.
#
# This requires aspell (http://aspell.net/).

# Options
wordfile=hooks/modelicares.pws # Name of custom word file, relative to base of project
extrafile=hooks/modelica.pws # Name of extra word file, relative to base of project
reduce=true # true, if unused words should be removed from the word file (slow)

# Base of package
root=`git rev-parse --show-toplevel`
wordfile=$root/$wordfile
extrafile=$root/$extrafile

# Remove unused words from the custom word file.
if $reduce; then
   cp $wordfile $wordfile.bak
   head --lines=1 $wordfile.bak > $wordfile
   while read word; do
       # echo $word
       files=`grep --files-with-matches --max-count=1 "$word" $root/doc/build/html/*.html`
       if [ ! -z "$files" ]; then
           echo $word >> $wordfile
       fi
   done < $wordfile.bak
fi
rm $wordfile.bak


# Check the spelling.
for f in $root/doc/build/html/*.html; do
    aspell --dont-backup --extra-dicts=$extrafile --personal=$wordfile -c $f
done
