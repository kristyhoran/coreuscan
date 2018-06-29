import argparse
from coreuscan.coreuscan import *
def main():


    # add args
    parser = argparse.ArgumentParser(description='Download MLST schema')
    parser.add_argument('-s','--search', dest='search',action = 'store', help= 'Search for a species and scheme type. Only possible to '
                                                                               'search for one  species at a time. '
                                                                               'Accepted strings are one of genus, '
                                                                               'first letter of genus immediately '
                                                                               'followed by species (no spaces or '
                                                                               'punctuation) or species only')
    parser.add_argument('-l', '--list', dest = 'list', action = 'store_true', help= 'show a list species for which '
                                                                                    'schema are currently available of '
                                                                                    'all available shema. No input required')
    parser.add_argument('-L, --list-db', dest = 'listdb', action = 'store_true', help='list all available databases')
    parser.add_argument('-d', '--download', dest='download', action = 'store_true', help='Download a MLST scheme.')
    parser.add_argument('-sp', '--species', dest= 'species', action = 'store', help = 'REQUIRED if -d selected. '
                                                                                      'The species for which the MLST '
                                                                                      'scheme is to be downloaded.')
    parser.add_argument('-db', '--database', dest='db', action = 'store', help = 'OPTIONAL The location of the MLST database, if '
                                                                                 'known. For use with, list, search and download')
    parser.add_argument('-o', '--output', dest = 'outpath', action = 'store', help = 'OPTIONAL An output path to save the .fasta files '
                                                                                'to. Default is under pwd <species>_schema/')
    parser.add_argument('-st', '--schema_type', dest= 'schema_type', action= 'store', help = 'The type of schema, available options are cg or trad')

    args = parser.parse_args()


    if args.db != None:
        db = args.db
    else:
        db = False

    if args.schema_type != None:
        schema_type = args.schema_type
    else:
        schema_type = False
    # List
    if args.list:
        if schema_type:
            list_all_schemes(scheme_type = schema_type, db = db)
        else:
            print('Please enter a schema type, available options are cg (core genome) or trad (for 7-gene MLST)')
    elif args.listdb:
        list_dbs()
    # Search
    elif args.search != None:
        search = args.search
        if schema_type:
            find_db(species=search, type=schema_type)
        else:
            print('Please enter a schema type, available options are cg (core genome) or trad (for 7-gene MLST)')
    # download
    elif args.download:
        # if there is a species added
        if args.species != None:
            species = args.species
            # print(species)
            # search for a the species and db
            if db == False:
                if species == 'listeria': # set default of listeria to pasteur although it can also be downloaded from cgmlst if db = cgmlst
                    db = 'pasteur'
                else:
                    species, db = find_db(species=species, type=schema_type)

            else:
                species = find_db(species=species, type=schema_type)[0]
            # print(db)
            if args.outpath != None:
                outpath = args.outpath
            else:
                outpath = False
            # download
            if db.lower() == 'pasteur':
                # print('db = pasteur')
                download_pasteur(species=species, scheme_type = schema_type, outpath=outpath)

            elif db.lower() == 'enterobase':
                download_warwick(species=species, scheme_type=schema_type, outpath=outpath)
            elif db.lower() == 'pubmlst':
                download_oxford(species=species, scheme_type='trad', outpath=outpath)
            elif db.lower() == 'cgmlst':
                download_cgmlst(species=species, scheme_type='cg', outpath=outpath)


        else:
            print('Please enter a species, see help.')


#
if __name__ == '__main__':
    main()