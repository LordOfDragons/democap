This directory contains some basic modding examples for typical usage types.
You can use them as base for creating real mods of the respective type.

General information about modding DEMoCap can be found here:
https://developer.dragondreams.ch/wiki/doku.php/democap:modding

If you need help feel free to drop by the discord channel: https://discord.gg/Jeg62ns



test_langpack.zip
-----------------
Example of a language pack modification. Language packs provide UI translations
for DEMoCap. The recommended way to create translations is to download the latest
https://github.com/LordOfDragons/democap/blob/main/data/content/langpacks/en.delangpack
and rename it. The name of the language pack should reflect a valid language code.
Change the "identifier" tag content to use the same language code as you used for
the filename (case sensitive). Then change the "name" and "description" tag. Especially
the "name" is used in the language selection combo box. Then replace all translations.
You can either use the IGDE (https://dragondreams.ch/index.php/dragengine/#downloads-igde)
for this or you can use any XML editor.



test_red_roo.zip
----------------
Example of a global character replacement modification. This example replaces
the skin resource of the Dragonroo character with a red tinted one.



test_blue_roo.zip
-----------------
Example of a new global character modification. This example adds a copy of the the
Dragonroo character with a blue skin. New characters will stay visible in
the list of available characters if the user used it at least once. This is because
calibrating/editing characters stores their modified settings in the user data
directory. And since the list of available characters is populated from the list of
character settings stored in the user data directory the character sticks around.
Users can delete such characters to remove the left over settings file after
unsubscribing.



test_material.zip
-----------------
Example of a new material modification. Materials can be chosen by users for example
to change the material of props placed in the capture world.



test_prop.zip
-------------
Example of a new prop modification. This adds a new element class "StaticPropTestBox"
using an XML element class file. XML element class files allow to add new element
classes without writing code by subclassing an existing script base class. In this
case the StaticProp class is subclassed and the model, skin, rig and audio-model
resource is changed. This is the recommended way to add new props to DEMoCap since
it does not require writing script code.



test_world.zip
--------------
Exmaple of a new world modification. This adds a new world the user can select as
stage for his motion captures. World files are edited using the IGDE
(https://dragondreams.ch/index.php/dragengine/#downloads-igde) World Editor
(https://developer.dragondreams.ch/wiki/doku.php/gamedev:deigde:editors:world).
Make sure to use path relative to the world file. See the info box on
https://developer.dragondreams.ch/wiki/doku.php/democap:projectmanagement?s[]=world#scenes
for information about the path replacement world property ensuring DEMoCap can
properly load the world file.



test_script.zip
---------------
Example of a script modification. This one adds a new behavior BehaviorTextureFlipper
together with a element class TestElementClass. See
https://developer.dragondreams.ch/wiki/doku.php/democap:modding#script_modifications
for information about creating script base modifications.
