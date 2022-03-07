#!/bin/bash

export DIR_INITIAL=`realpath data/content/initial/config/characters`
export DIR_CONFIG=`realpath distribute/config/characters`

xsltproc --output "${DIR_INITIAL}/Biomech.demccp" copyInitialCharacter.xsl "${DIR_CONFIG}/Biomech.demccp"
xsltproc --output "${DIR_INITIAL}/Dragonroo.demccp" copyInitialCharacter.xsl "${DIR_CONFIG}/Dragonroo.demccp"
xsltproc --output "${DIR_INITIAL}/First Person Hands.demccp" copyInitialCharacter.xsl "${DIR_CONFIG}/First Person Hands.demccp"
