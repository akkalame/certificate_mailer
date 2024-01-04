import re
import os
from apps import list2_dict, db
#from apps.controllers import listCustomFonts

basedir = os.path.abspath(os.path.dirname(__file__))

def build_custom_fonts(cf_list):
	#cf_list = listCustomFonts()

	css_content = ""
	for cf in cf_list:
		css_content += f"@import url('{cf.url}');\n"
	with open(os.path.join(basedir,"../static/assets/css/custom_fonts.css"), "w", encoding="utf-8") as f:
		f.write(str(css_content))
	