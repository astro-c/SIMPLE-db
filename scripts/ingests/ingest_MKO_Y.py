from scripts.ingests.ingest_utils import *
from astropy.utils.exceptions import AstropyWarning
import pandas as pd

warnings.simplefilter('ignore', category=AstropyWarning)

SAVE_DB = True  # save the data files in addition to modifying the .db file
RECREATE_DB = True  # recreates the .db file from the data files

UCS = pd.read_csv('scripts/ingests/UltracoolSheet-Main.csv')

db = load_simpledb('SIMPLE.db', recreatedb=RECREATE_DB)

logger.setLevel(logging.INFO)  # Can also set to debug

def references(data_ref):
    # changes reference of the data sheet in the appropriate format used in database
    ref = data_ref
    if data_ref == 'Best20b':
        ref = 'Best20.42'
    if data_ref == 'Burn10b':
        ref = 'Burn10.1885'
    if data_ref == 'Deac11':
        ref = 'Deac11.6319'
    if data_ref == 'Deac12b':
        ref = 'Deac12.100'
    if data_ref == 'Deac14b':
        ref = 'Deac14.119'
    if data_ref == 'Deac17a':
        ref = 'Deac17.1126'
    if data_ref == 'Delo08a':
        ref = 'Delo08.961'
    if data_ref == 'Delo12b':
        ref = 'Delo12'
    if data_ref == 'Dupu12':
        ref = 'Dupu12.19'
    if data_ref == 'Dupu15a':
        ref = 'Dupu15.102'
    if data_ref == 'Garc17a':
        ref = 'Garc17.162'
    if data_ref == 'Legg00b':
        ref = 'Legg00'
    if data_ref == 'Legg02a':
        ref = 'Legg02.452'
    if data_ref == 'Legg02b':
        ref = 'Legg02.78'
    if data_ref == 'Legg10a':
        ref = 'Legg10'
    if data_ref == 'Liu_13b':
        ref = 'Liu_13.20'
    if data_ref == 'Lodi07a':
        ref = 'Lodi07.372'
    if data_ref == 'Lodi12d':
        ref = 'Lodi12.53'
    if data_ref == 'Lodi13a':
        ref = 'Lodi13.2474'
    if data_ref == 'Pinf14a':
        ref = 'Pinf14.1009'
    if data_ref == 'Warr07b':
        ref = 'Warr07.1400'
    else:
        pass
    return ref


def photometry_mko(db, data):
    # uses reference to determine the instrument used for photometry
    ref = references(data['ref_Y_MKO'])
    name_skip = []
    mag = data['Y_MKO']
    mag_err = data['Yerr_MKO']

    wircam_ref_list = ['Albe11', 'Delo08.961', 'Delo12', 'Dupu19', 'Naud14']
    wircam_name_list = ['ULAS J115038.79+094942.9']
    wfcam_ref_list = ['Burn08', 'Burn14', 'Card15', 'Deac11.6319', 'Deac12.100', 'Deac17.1126', 'Lawr07', 'Lawr12',
                      'Liu_13.20', 'Lodi07.372', 'Luca10', 'Pinf08', 'Warr07.1400']
    wfcam_name_list = ['HD 253662B', 'NLTT 27966B']
    niri_ref_list = ['Dupu15.102', 'Lach15', 'Legg13', 'Legg15', 'Legg16', 'Liu_12']
    vista_ref_list = ['Edge16', 'Gauz12', 'Kell16', 'McMa13', 'Minn17', 'Lodi12.53', 'Lodi13.2474', 'Pena11', 'Pena12',
                      'Smit18']
    gpi_ref_list = ['Garc17.162']
    visao_ref_list = ['Male14']
    ufti_name_list = ['ULAS J133502.11+150653.5']

    if ref in wircam_ref_list or data['name'] in wircam_name_list:
        band = 'Wircam.Y'
        tel = 'CFHT'
    if ref in wfcam_ref_list:
        band = 'WFCAM.Y'
        tel = 'UKIRT'
    if ref in niri_ref_list:
        band = 'NIRI.Y'
        tel = 'Gemini North'
    if ref in vista_ref_list:
        band = 'VISTA.Y'
        tel = 'VISTA'
    if ref in gpi_ref_list:
        band = 'GPI.Y'
        tel = 'Gemini South'
    if ref in visao_ref_list:
        band = 'VisAO.Ys'
        tel = 'LCO'
    if ref == 'Burn09':
        # data taken from table in reference
        mag = 19.020
        mag_err = 0.080
        band = 'WFCAM.Y'
        tel = 'UKIRT'
    if ref == 'Burn13':
        if data['name'] in ufti_name_list:
            band = 'UFTI.Y'
            tel = 'UKIRT'
        else:
            band = 'WFCAM.Y'
            tel = 'UKIRT'
    if ref == 'Deac14.119':
        if data['name'] in wfcam_name_list:
            band = 'WFCAM.Y'
            tel = 'UKIRT'
        else:
            band = 'VISTA.Y'
            tel = 'VISTA'
    else:
        name_skip.append(data['name'])

    if data['name'] not in name_skip:
        ingest_photometry(db=db, sources=data['name'], bands=band, magnitudes=mag,
                          magnitude_errors=mag_err, telescope=tel, reference=ref)


# Adding UKIDSS names
def add_ukidss_names(db):
    if entry['designation_ukidss'] == 'null':
        pass
    else:
        other_name_data = [{'source': entry['name'], 'other_name': entry['designation_ukidss']}]
        db.Names.insert().execute(other_name_data)

    # if entry['designation_WISE'] == 'null':
    #     pass
    # else:
    #     wise_name = [{'source': entry['name'], 'other_name': entry['designation_WISE']}]
    #     db.Names.insert().execute(wise_name)


# You may need to add filters to the Photometry Filters table
# https://github.com/SIMPLE-AstroDB/SIMPLE-db/blob/main/documentation/PhotometryFilters.md
def add_filters(db):
    lco_telescope = [{'name': 'LCO'}]
    db.Telescopes.insert().execute(lco_telescope)

    wircam_instrument = [{'name': 'Wircam',
                          'mode': 'Imaging',
                          'telescope': 'CFHT'}]
    db.Instruments.insert().execute(wircam_instrument)

    niri_instrument = [{'name': 'NIRI',
                        'mode': 'Imaging',
                        'telescope': 'Gemini North'}]
    db.Instruments.insert().execute(niri_instrument)

    gpi_instrument = [{'name': 'GPI',
                       'mode': 'Imaging',
                       'telescope': 'Gemini South'}]
    db.Instruments.insert().execute(gpi_instrument)

    visao_instrument = [{'name': 'VisAO',
                         'mode': 'Imaging',
                         'telescope': 'LCO'}]
    db.Instruments.insert().execute(visao_instrument)

    wircam_y = [{'band': 'Wircam.Y',
                 'ucd': 'em.IR.NIR',
                 'effective_wavelength': '10220.90',
                 'width': '1084.17'}]

    db.PhotometryFilters.insert().execute(wircam_y)

    niri_y = [{'band': 'NIRI.Y',
               'ucd': 'em.IR.NIR',
               'effective_wavelength': '10211.18',
               'width': '943.58'}]

    db.PhotometryFilters.insert().execute(niri_y)

    gpi_y = [{'band': 'GPI.Y',
              'ucd': 'em.IR.NIR',
              'effective_wavelength': '10375.56',
              'width': '1707.30'}]

    db.PhotometryFilters.insert().execute(gpi_y)

    visao_ys = [{'band': 'VisAO.Ys',
                 'ucd': 'em.IR.NIR',
                 'effective_wavelength': '9793.50',
                 'width': '907.02'}]

    db.PhotometryFilters.insert().execute(visao_ys)


# Execute the ingests!
add_filters(db)
for i in range(len(UCS)):
    entry = UCS.iloc[i]
    if entry['Y_MKO'] == 'NaN' or entry['Yerr_MKO'] == 'NaN':
        pass
    else:
        add_ukidss_names(db)
        photometry_mko(db, entry)

# WRITE THE JSON FILES
if SAVE_DB:
    db.save_database(directory='data/')