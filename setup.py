import sys
from cx_Freeze import setup, Executable

setup(
	name = "TranslationHelper",
	version = "0.5",
	description = "A tool to automate Google translation",
	executables = [Executable("google-translate-sqldb.py", base = "Console")])