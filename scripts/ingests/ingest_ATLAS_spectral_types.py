# ------------------------------------------------------------------------------------------------

from astrodbkit2.astrodb import create_database
from astrodbkit2.astrodb import Database
from simple.schema import *
from astropy.table import Table
import numpy as np
import re
import os
from utils import convert_spt_string_to_code

DRY_RUN = False
RECREATE_DB = True

connection_string = 'sqlite:///SIMPLE.db'  # SQLite
if RECREATE_DB:
	os.remove('SIMPLE.db')
	create_database(connection_string)
	db = Database(connection_string)
	db.load_database('data')
else:
	db = Database(connection_string)

# ===============================================================
# Ingest new reference if missing
# ===============================================================

# Adding new reference Manj19 to publications table in database
manj19_search = db.query(db.Publications).filter(db.Publications.c.name == 'Manj19').table()
if len(manj19_search) == 0 and not DRY_RUN:
	new_ref = [{'name': 'Manj19'}]
	db.Publications.insert().execute(new_ref)


# load table of sources to ingest
ingest_table = Table.read("scripts/ingests/ATLAS_table.vot")
ingest_table_df = ingest_table.to_pandas()
names = ingest_table['Name']
n_sources = len(names)
spectral_types_unknown = ingest_table['SpType']  # pre-existing spectral types
spectral_types_spex = ingest_table['SpTSpeX']  # new spectral types

# fetch primary name identifier from database
db_names = []
for name in names:
	db_name = db.search_object(name, output_table='Sources')[0].source
	# print(name, db_name)
	db_names.append(db_name)


# ===============================================================
# Ingest new spectral type estimates from the SpTSpeX column
# ===============================================================

db_names_spex = []
spex_types_string = []
for i, db_name in enumerate(db_names):
	if spectral_types_spex[i] != "":
		db_names_spex.append(db_name)
		spex_types_string.append(spectral_types_spex[i])

spex_types_codes = convert_spt_string_to_code(spex_types_string, verbose=False)
regime = ['nir']*len(db_names_spex)
spt_ref = ['Manj19']*len(db_names_spex)
SpT_table_spex = Table([db_names_spex, spex_types_string, spex_types_codes, regime, spt_ref],
					   names=('source', 'spectral_type_string', 'spectral_type_code', 'regime', 'reference'))
SpT_table_spex_df = SpT_table_spex.to_pandas()  # make a Pandas dataframe to explore  with Pycharm
# print(SpT_table_spex_df)

# Add to database
if not DRY_RUN:
	db.add_table_data(SpT_table_spex, table='SpectralTypes', fmt='astropy')

# Verify results
print('Manj19 entries in database:')
print(db.query(db.SpectralTypes).filter(db.SpectralTypes.c.reference == 'Manj19').table())

# Deletion example (use with caution!)
# db.SpectralTypes.delete().where(db.SpectralTypes.c.reference == 'Manj19').execute()
# ===============================================================


# ===============================================================
# Ingest spectral types from unknown sources
# if sources have no other spectral type
# ===============================================================

# Find out which sources don't have spectral types
db_names_needs_spectral_type = []
spectral_types_to_add = []
for i, db_name in enumerate(db_names):
	db_spectral_types = db.query(db.SpectralTypes).filter(db.SpectralTypes.c.source == db_name).table()
	if db_spectral_types is None or len(db_spectral_types) == 0:
		db_names_needs_spectral_type.append(db_name)
		spectral_types_to_add.append(spectral_types_unknown[i])

# Convert SpT string to code
spectral_type_codes_unknown = convert_spt_string_to_code(spectral_types_to_add, verbose=False)
regime = ['unknown']*len(db_names_needs_spectral_type)
spt_ref = ['Missing']*len(db_names_needs_spectral_type)
comments = ['From ATLAS Table Manjavacas etal. 2019']*len(db_names_needs_spectral_type)
SpT_table_unknown = Table([db_names_needs_spectral_type, spectral_types_to_add, spectral_type_codes_unknown, regime, spt_ref, comments],
						names=('source', 'spectral_type_string', 'spectral_type_code', 'regime', 'reference', 'comments'))

# Print out the results
# print(SpT_table_unknown)

# Add to database
if not DRY_RUN:
	db.add_table_data(SpT_table_unknown, table='SpectralTypes', fmt='astropy')

# Verify results
print('Missing entries in database:')
print(db.query(db.SpectralTypes).filter(db.SpectralTypes.c.reference == 'Missing').table())
print('unknown regime entries in database:')
print(db.query(db.SpectralTypes).filter(db.SpectralTypes.c.regime == 'unknown').table())

# Deletion example (use with caution!)
# db.SpectralTypes.delete().where(db.SpectralTypes.c.reference == 'Missing').execute()
# ===============================================================

if not DRY_RUN:
	db.save_db('data')
