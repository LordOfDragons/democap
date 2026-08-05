#!/bin/bash

export DIR_INITIAL=`realpath data/content/initial/config/characters`
export DIR_CONFIG=`realpath cache/testrun/config/characters`

process_character() {
	local name="$1"
	xsltproc copyInitialCharacter.xsl "${DIR_CONFIG}/${name}.demccp" \
		| sed ':a; s/^\(\t*\)  /\1\t/; ta' > "${DIR_INITIAL}/${name}.demccp"
}

process_character "Biomech"
process_character "Dragonroo"
process_character "First Person Hands"
process_character "Indominus Rex"
process_character "Shadrian"
