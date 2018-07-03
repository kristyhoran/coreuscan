import requests, requests.exceptions, argparse, os, bs4, ast,gzip, wget, sys,subprocess

# logger = logging.getLogger('pubMLST')

CGMLST_URL = 'http://www.cgmlst.org/ncs/'
OXFORD_URL = 'http://rest.pubmlst.org'
WARWICK_URL = 'http://enterobase.warwick.ac.uk/schemes/'
PASTEUR_URL = 'http://bigsdb.pasteur.fr'


DB_DICT = {'warwick': 'Enterobase', 'oxford':'pubMLST', 'cgmlst': 'cgMLST', 'pasteur': 'Pasteur Institute'}

SCHEME_DICT = {'cg': 'Core Genome', 'trad': '7 gene MLST'}

def define_cache(type, species=False):
    # set up a directory for cache
    path = os.getcwd() + '/'+ type +'_schemas/'

    if not os.path.exists(path):

        outdir = os.makedirs(path)

def cache(location, type, species_dict, prints = False):
    path = os.getcwd() + '/'+ type +'_schemas/'
    # print('Checking if schemes are already in cache')
    if compare_cache(path=path, location=location, new=species_dict) == True:
        if prints:
            print('Completed ' + location + ' cache')
        return False
    else:
        with open(path + location, 'w') as out_file:
            for s in species_dict:
                # print(s)
                out_file.write(str(s) + '\n')
        if prints:
            print('Completed ' + location + ' cache')

        return True

def compare_cache(path, location, new):
    existing = os.listdir(path)

    if existing:
        if location in existing:
            f = open(path + location, 'r')
            test = f.readlines()
            if len(new) == len(test):
                errs = 0
                for i in range(len(new)):
                    if new[i] == ast.literal_eval(test[i]):
                        errs = errs
                    else:
                        errs = errs + 1
                if errs == 0:
                    return True
                else:
                    return False
            else:
                return False

def compare_schema(path, loci, new):

    existing = os.listdir(path)

    if existing:

        if loci+'.fasta' in existing:

            f = open(path + '/' + loci+'.fasta', 'r')

            test = f.read()

            if test == new:
                return True
            else:
                return False
    else:
        False




def get_cgMLST():

    define_cache('cg')
    try:
        r = requests.get(CGMLST_URL)
        r.raise_for_status()
        print('Requesting data cgMLST @ www.cgmlst.org/ncs/')
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        species_dict = []
        # retrieve species and url
        for s in soup.table.find_all('a'):
            sp = str(s.contents[0])
            sp = sp.strip('</em>')
            # print(sp)
            # print('Accessing ' + sp + ' schemes......')
            species_dict.append(([sp],s.get('href') + 'alleles/'))
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
    # save the available schemes
    cache(location='cgmlst', type = 'cg',species_dict= species_dict)

# get_cgMLST()
#
def get_Oxford():
    print('Requesting data from pubMLST @ rest.pubmlst.org')
    define_cache(type = 'trad')
    # get pubmlst oxford
    species_dict = []
    url_mid = '/db/pubmlst_'
    url_end = '_seqdef/loci'
    try:
        r_mlst_oxford = requests.get(OXFORD_URL)
        r_mlst_oxford.raise_for_status()
        r_mlst_oxford_json = r_mlst_oxford.json()
        # step through response to get species name and url
        for i in range(len(r_mlst_oxford_json)):
            for j in range(len(r_mlst_oxford_json[i]['databases'])):

                if 'sequence' in r_mlst_oxford_json[i]['databases'][j]['description']:
                    s = str(r_mlst_oxford_json[i]['databases'][j]['href'])[35:-7]
                    # print('Accessing '+ s +' schemes......')
                    new_url = r_mlst_oxford_json[i]['databases'][j]['href'] + '/loci'
                    r = requests.get(new_url)
                    if 'loci' in r.json():

                        loci_list = r.json()['loci']
                        # TODO which of the mulitple schemes are the best , abaummani, leptospira, pmultocida
                        # if 'abaumannii' == s:
                        #     # print(loci_list)
                        #     for i in loci_list:
                        #         if 'Oxf' in i:
                        #             print(i)
                        species_dict.append(([s], str(r_mlst_oxford_json[i]['databases'][j]['href']), loci_list))
        # save the available schemes
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
    cache(location='oxford', type = 'trad',species_dict=species_dict)


# get_Oxford()

def get_Warwick():
    #  get the allele address for all warwick schemes.
    print('Requesting data from Enterobase @ enterobase.warwick.ac.uk')
    def get_allele_address(url):
        try:
            r = requests.get(url)
            r.raise_for_status()
            soup = bs4.BeautifulSoup(r.text, 'html.parser')
            # print(soup.prettify())
            allele_dict = []
            # # retrieve species and url
            for s in soup.find_all('a'):
                if s.contents[0] != '../':
                    # sp is allele
                    sp = str(s.contents[0])
                    # print(sp)
                    sp = sp.strip('[]')
                    if sp.startswith('MLST'):
                        pass
                    elif sp.startswith('profiles'):
                        pass
                    else:
                        allele_dict.append(sp)
            # return a list of alleles
            return allele_dict
        except requests.exceptions.HTTPError as err:
            print(err)
            sys.exit(1)

    scheme_dict = {'salmonella': ('Salmonella.UoW/', 'Salmonella.cgMLSTv4/'),
                   'ecoli': ('Escherichia.UoW/', 'ESCwgMLST.cgMLSTv1/'),
                   'yersinia': ('Yersinia.UoW/', 'YERwgMLST.cgMLSTv1/'),
                   'moraxella': ('Moraxella.UoW/',)}

    define_cache(type='cg')
    define_cache(type= 'trad')
    species_dict_cg = []
    species_dict_trad = []


    for k in scheme_dict:


        # print('Accessing ' + k + ' schemes......')


#         build url
        if len(scheme_dict[k]) == 2: #if has both cg and 7-gene
            url_cg = WARWICK_URL + scheme_dict[k][1]
            allele_dict_cg = get_allele_address(url_cg)
            species_dict_cg.append(([k], url_cg, allele_dict_cg))
            url_trad = WARWICK_URL + scheme_dict[k][0]
            allele_dict_trad = get_allele_address(url_trad)
            species_dict_trad.append(([k], url_trad, allele_dict_trad))
        else: # has only 7 gene
            url_trad = WARWICK_URL + scheme_dict[k][0]
            allele_dict = get_allele_address(url_trad)
            species_dict_trad.append(([k], url_trad, allele_dict))




    cache(location='warwick', type='cg', species_dict = species_dict_cg)
    cache(location='warwick', type='trad', species_dict = species_dict_trad)

# get_Warwick()

def get_Pasteur():
    print('Requesting from Pasteur Institute @ bigsdb.pasteur.fr')
    PASTEUR = ['listeria', 'ecoli', 'klebsiella']
    PRE_URL = 'http://api.bigsdb.pasteur.fr/db/pubmlst_'
    SUF_URL = '_seqdef_public/schemes'

    define_cache(type='cg')
    define_cache(type='trad')

    species_dict_mlst = []
    species_dict_cg = []

    for p in PASTEUR:
        # print('Accessing ' + p + ' schemes......')
        # print(p)
        try:
            r = requests.get(PRE_URL + p + SUF_URL)

            r.raise_for_status()
            schemes = r.json()['schemes']
            allele_dict_mlst = []
            allele_dict_cg = []
            # print('Accessing loci urls')
            d = '.'
            for s in range(len(schemes)):
                # print(schemes[s])
                if schemes[s]['description'].startswith('MLST'):
                    r = requests.get(schemes[s]['scheme'])
                    scheme = r.json()
                    allele_dict_mlst.append(scheme['loci'])
                elif schemes[s]['description'].startswith('cgMLST'):
                    r = requests.get(schemes[s]['scheme'])
                    scheme = r.json()
                    allele_dict_cg.append(scheme['loci'])
                d = d + '.'
            # print(d)
            species_dict_cg.append(([p], PRE_URL+p+SUF_URL, allele_dict_cg))
            species_dict_mlst.append(([p], PRE_URL + p + SUF_URL, allele_dict_mlst))
        except requests.exceptions.HTTPError as err:
            print(err)
            # sys.exit(1)

    cache(location='pasteur', type='cg', species_dict=species_dict_cg)

    cache(location='pasteur', type='trad', species_dict=species_dict_mlst)
# get_Pasteur()

def get_dbs(type, db):
    if type == 'cg':
        if db == 'cgmlst':
            get_cgMLST()
        elif db == 'pasteur':
            get_Pasteur()
        elif db == 'warwick':
            get_Warwick()
    elif type == 'trad':
        if db == 'warwick':
            get_Warwick()
        if db == 'oxford':
            get_Oxford()
        elif db == 'pasteur':
            get_Pasteur()


def find_db(species, type):
    # make uniform, remove punctuation and split into genus and species

    sp = species.lower()
    print('======================================================>')
    print('Searching for ' + sp)
    print('======================================================>')
    for c in ['.', '/', '\\','-', '_' ]:
        if c in sp:
            sp = sp.replace(c, ' ')
    sp = sp.split()

    path = os.getcwd() + '/' + type + '_schemas/'

    for d in DB_DICT:
        if type == 'cg' and d == 'oxford':
            pass
        elif type == 'trad' and d == 'cgmlst':
            pass
        else:
            if not os.path.exists(path + d):
                # print(path + d)
                print('The cache does not yet exist. Please wait.....')
                get_dbs(type=type, db = d)

    # else:
    # open the directory
    st_dir = os.listdir(path)

    # a list of places the species may be found
    db = []
    # print(st_dir)
    found = False
    for f in st_dir:
        # open the dir

        species_in_ST = open(path + f, 'r')
        cached_species = species_in_ST.readlines()
        # print(cached_species)

        for cs in cached_species:
            cs = ast.literal_eval(cs)

            cs = cs[0][0].lower()
            # for each word in search string
            for sc in sp:

                # if the search string is not a prefix and found
                if len(sc) > 1 and sc in cs:
                    found = True
                    species_found = cs

                    db.append(f)
            # print(found)
            # print(db)
    if found:
        database = []
        for d in db:
            database.append(DB_DICT[d])
        data = ' and '.join(database)

        print('A ' + species + ' ' + SCHEME_DICT[type] + ' was found as ' + species_found + ' in ' + data)
        # print(species_found, db)
        return (species_found, db)
    else:

        print(species + ' was not found. Please check spelling of input and try again or contact developers to have ' + species + ' availability added.')
    #

# find_db('listeria', 'cg')

# get_Pasteur()
def download_warwick(species,scheme_type, outpath = False, scheme_path =
False, unzip = False, cache = True):
    print(species, outpath, scheme_type)
    print('Accessing Enterobase')
    # print(os.getcwd())
    if not outpath:
        path = os.getcwd() + '/' + species + '_schema/'
    else:
        path = outpath
    # print('outpath: ', path)
    # print(type(path))
    if not os.path.exists(path):
        print('Making path to output files')
        os.makedirs(path)
    else:
        print('Outdir already exists')
    outdir = path

    if scheme_path:
        scheme_path = scheme_path
    else:
        scheme_path = os.getcwd() + '/' + scheme_type +'_schemas/'
    # print('scheme path: ', scheme_path)



    while not os.path.exists(scheme_path + '/warwick'):
        print('Please wait while we detect available schemes')
        get_Warwick()

    mlst_dir = os.listdir(path=scheme_path)

    # get the list of warwick schemes for schemtype

    open_file = open(scheme_path + '/warwick', 'r')

    possible_schemes = open_file.readlines()
    try:
        for schemes in possible_schemes:
            scheme = ast.literal_eval(schemes)
            sp = scheme[0][0]
            # select the species
            if sp.lower() == species.lower():
            # construct url for loci
                for loci in scheme[2]:
                    url = scheme[1] + loci
                    loci_name = loci.split('.')[0]
                    # print(loci_name)
                    # download the zipped file
                    filename = url.split('/')[-1]
                    if not os.path.exists(outdir + filename):
                        wget.download(url, out=outdir)
                    if unzip:
                        if not os.path.exists(outdir + filename[:-3]):
                            df = gzip.open(outdir + filename, 'rt')
                            # print(type(df.read()))
                            with open(outdir + filename[:-3], 'w') as of:
                                of.write(df.read())

                print('Fasta files for ' + species + ' are located in ' + outdir)
    except Exception as e:
        print(e)
        sys.exit(1)

# download_warwick(species='salmonella', scheme_type='trad_schemas')

def download_pasteur(species,scheme_type, outpath = False, scheme_path = False, cache = True):

    print('Accessing MLST at Pasteur Institute')

    # set up outpath
    if not outpath:
        path = os.getcwd() + '/' + species + '_schema/'
    else:
        path = outpath
    # if it doesn't exist make it or not
    # print(path)
    if not os.path.exists(path):
        print('Making path to output files')
        os.makedirs(path)
    else:
        print('Outdir already exists')
    outdir =  path
    print(outdir)
    # open schema list
    if scheme_path:
        scheme_path = scheme_path
    else:
        scheme_path = os.getcwd() + '/' + scheme_type +'_schemas/'
    # print(scheme_path)
    while not os.path.exists(scheme_path + '/pasteur'):
        print('Please wait while we detect available schemes')
        get_Pasteur()
    mlst_dir = os.listdir(path=scheme_path)

    # get the list of pasteur schemes for schemtype
    open_file = open(scheme_path + '/pasteur', 'r')

    possible_schemes = open_file.readlines()
    #

    for schemes in possible_schemes:
        scheme = ast.literal_eval(schemes)

        sp = scheme[0][0]
        if sp.lower() in species.lower():
            try:
                for url in scheme[2][0]:
                    loci = url.split('/')[-1]
                    # print(loci)
        #             # get the fasta file address using request
                    fasta_request = requests.get(url+'/alleles_fasta')
                    fasta_request.raise_for_status()
                    fasta_file = fasta_request.text
        #
                    # only save the fasta file if it is not already there.
                    if compare_schema(path=outdir, loci=loci, new=fasta_file):
                        print(loci + ' has no changes.')
                    else:
                        with open(outdir +'/' + loci + '.fasta', 'w') as \
                                out_file:
                            out_file.write(fasta_file)

                        # print(loci + ' saved')
                print('Fasta files for ' + species + ' are located in ' + outdir)
    #             # break

            except requests.exceptions.HTTPError as err:
                print(err)
                sys.exit(1)
# download_pasteur(species='listeria', scheme_type='trad_schemas')

def download_oxford(species, scheme_type, outpath = False, scheme_path = False, cache = True):

    print('Accessing pubMLST')
    # get cache of species and loci
    if scheme_path:
        scheme_path = scheme_path
    else:
        scheme_path = os.getcwd() + '/' + scheme_type +'_schemas/'

    print(scheme_path)
    while not os.path.exists(scheme_path):
        print('Please wait while we detect available schemes')
        get_Oxford()

    # set up out put dir for fasta files
    if not outpath:
        path = os.getcwd() + '/' + species +'_schema/'
    else:
        path = outpath

    # if it doesn't exist make it or not
    # print(path)
    if not os.path.exists(path):
        print('Making path to output files')
        os.makedirs(path)
    else:
        print('Outdir already exists')

    outdir = path
    print(outdir)
    # get loci

    # get the list of pasteur schemes for schemtype
    open_file = open(scheme_path + '/oxford', 'r')
    possible_schemes = open_file.readlines()
    try:
        for schemes in possible_schemes:
            scheme = ast.literal_eval(schemes)

            sp = scheme[0][0]
            if sp.lower() in species.lower():
                # print(scheme)
                for url in scheme[2]:
                    loci = url.split('/')[-1]

                    # get the fasta file address using request
                    fasta_request = requests.get(url+'/alleles_fasta')
                    fasta_request.raise_for_status()
                    fasta_file = fasta_request.text
                    #
                    # print(fasta_file)
                    # only save the fasta file if it is not already there.
                    if compare_schema(path=outdir, loci=loci, new=fasta_file):
                        print(loci + ' has no changes.')
                    else:
                        with open(outdir + '/' +loci + '.fasta', 'w') as out_file:
                            out_file.write(fasta_file)

                        # print(loci + ' saved')
                print('Fasta files for ' + species + ' are located in ' + outdir)
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
# download_oxford(species='abaumannii', scheme_type='trad_schemas')

def download_cgmlst(species, scheme_type, outpath = False, scheme_path = False, cache = True):

    print('Accessing cgMLST')
    # get cache of species and loci
    if scheme_path:
        scheme_path = scheme_path
    else:
        scheme_path = os.getcwd() + '/' + scheme_type +'_schemas/'
    print(scheme_path)

    while not os.path.exists(scheme_path + '/cgmlst'):
        print('Please wait while we detect available schemes')
        get_cgMLST()



    # set up out put dir for fasta files
    if not outpath:
        path = os.getcwd() + '/' + species +'_schema/'
    else:
        path = outpath

    # if it doesn't exist make it or not
    print(path)
    if not os.path.exists(path):
        print('Making path to output files')
        os.makedirs(path)
    else:
        print('Outdir already exists')

    outdir = path
    # print(path)

    # get the list of pasteur schemes for schemtype
    open_file = open(scheme_path + '/cgmlst', 'r')
    possible_schemes = open_file.readlines()
    # print(possible_schemes)
    try:
        for schemes in possible_schemes:
            scheme = ast.literal_eval(schemes)

            sp = scheme[0][0]
            # print(sp)
            if species.lower() in sp.lower():

                url = scheme[1]
                print(url)
                filename = species.split()[0] + '.gz'
                print(outdir + filename)
                if not os.path.exists(outdir +  filename):
                    print('Downloading scheme for ' + species)
                    # wget.download(url, out = outdir + filename, bar = None)
                    subprocess.run(['wget', url, '-O',outdir + filename, '-nv'])
                else:
                    print('Updating existing scheme')
                    os.remove(outdir + filename)
                    # wget.download(url, out=outdir + filename, bar = None)
                    subprocess.run(['wget', url, '-O',outdir + filename, '-nv'])
                # print(outdir +  filename)

                print('Fasta files for ' + species + ' are located in ' +
                      outdir + filename)
    except Exception as e:
        print(e)
        sys.exit(1)


        # break
# download_cgmlst(species='baumannii', scheme_type='cg')



def list_all_schemes(scheme_type, db = False):
    path = os.getcwd() + '/' + scheme_type + '_schemas'
    # print(path)
    print('Please wait while we detect available schemes')
    while not os.path.exists(path + '/pasteur'):
        print('Retrieving information for Pasteur Institute')
        get_Pasteur()

    while not os.path.exists(path + '/warwick'):
        print('Retrieving information for Enterobase')
        get_Warwick()
    if scheme_type == 'cg':
        while not os.path.exists(path + '/cgmlst'):
            print('Retrieving information for cgMLST')
            get_cgMLST()
    elif scheme_type == 'trad':
        while not os.path.exists(path + '/oxford'):
            print('Retrieving information for pubMLST')
            get_Oxford()

        # else:
        #     print('Please enter a valid scheme type, options are cg (core genome) or trad (7 gene MLST)')
        #     return False

    db_list = os.listdir(path)
    if db:
        dbase = db.lower()
    else:
        dbase = 'all'
    scheme_list = []
    if dbase == 'all':

        for db in db_list:
            f = open(path + '/' + db)
            # print(type(f.read()))
            print('======================================================>')
            print(SCHEME_DICT[scheme_type] + ' schemes that are found in ' + DB_DICT[db])
            print('======================================================>')
            for t in f.readlines():
                line = ast.literal_eval(t)
                print(line[0][0])
    elif dbase in db_list:
        for db in db_list:
            if db == dbase:
                f = open(path + '/' + db)
                # print(type(f.read()))
                print('======================================================>')
                print(SCHEME_DICT[scheme_type] + ' schemes that are found in ' + DB_DICT[db])
                print('======================================================>')
                for t in f.readlines():
                    line = ast.literal_eval(t)
                    print(line[0][0])
    else:
        print('The database entered is not available or does not have schemes for '+ SCHEME_DICT[scheme_type] + ' schemes. Please check your spelling and try again or contact the developers to have ' + DB_DICT[db] + ' made available.')



# list_all_schemes('cg', 'oxford')
# #

def list_dbs():
    print('======================================================>')
    print('Databases available through CoreuScan are:')
    print('======================================================>')

    print('\nCore genome schemes are available from:')
    print('------------------------------------------------------->')
    for d in DB_DICT:
        if d != 'oxford':
            print(DB_DICT[d])
    print('\n7 gene MLST schemes are also available from:')
    print('------------------------------------------------------->')

    for d in DB_DICT:
        if d != 'cgmlst':
            print(DB_DICT[d])
# list_dbs()
#
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
        print(db)
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
        print(args.download)
        # if there is a species added
        if args.species != None:
            species = args.species
            print(species)
            # search for a the species and db
            if db == False:
                if species == 'listeria': # set default of listeria to pasteur although it can also be downloaded from cgmlst if db = cgmlst
                    db = 'pasteur'
                else:
                    species, db = find_db(species=species, type=schema_type)
                    db = db[0]

            else:
                species = find_db(species=species, type=schema_type)[0]
            print(db)

            if args.outpath != None:
                outpath = args.outpath
            else:
                outpath = False
            # download
            if db.lower() == 'pasteur':
                # print('db = pasteur')
                download_pasteur(species=species, scheme_type = schema_type, outpath=outpath)

            elif db.lower() == 'enterobase' or db.lower() == 'warwick':
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