#! /bin/bash

find . -name '*bz2' | sed 's_\.bz2$__' | xargs -I {} sh -c "7z e -so '{}.bz2' | 7z a -si -t7z -mx=9 '{}.7z' && rm '{}.bz2'"  

