#!/bin/bash

export DIR_INITIAL=`realpath data/content/initial/config/characters`
export DIR_CONFIG=`realpath cache/testrun/config/characters`

xsltproc --output "${DIR_INITIAL}/Biomech.demccp" copyInitialCharacter.xsl "${DIR_CONFIG}/Biomech.demccp"
xsltproc --output "${DIR_INITIAL}/Dragonroo.demccp" copyInitialCharacter.xsl "${DIR_CONFIG}/Dragonroo.demccp"
xsltproc --output "${DIR_INITIAL}/First Person Hands.demccp" copyInitialCharacter.xsl "${DIR_CONFIG}/First Person Hands.demccp"
xsltproc --output "${DIR_INITIAL}/Indominus Rex.demccp" copyInitialCharacter.xsl "${DIR_CONFIG}/Indominus Rex.demccp"
xsltproc --output "${DIR_INITIAL}/Shadrian.demccp" copyInitialCharacter.xsl "${DIR_CONFIG}/Shadrian.demccp"
