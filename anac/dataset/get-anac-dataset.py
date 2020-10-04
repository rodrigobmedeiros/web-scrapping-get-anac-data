import lxml.html as parser
import requests
import wget
import timeit
import os
import pandas as pd
import zipfile
import shutil

def create_file_directory():
    """
    function to verify if the directory ./file exist - This directory will be used to manipulate all file during the process.
    """

    # Verify if directory exist.
    # If yes, delete it and every thing inside and create it again.
    # If not, just create it.

    if os.path.isdir('./file'):

        shutil.rmtree('./file')

    os.mkdir('./file')


def get_all_links_from_html(website: str) -> list:
    """
    This function get all links to download from anac website

    args:

        website: str -> website url

    return:

        all_links: list -> list of tuples where each tuple contain the link to download, the year and the month.
    """

    # Get website
    r = requests.get(website)

    # Parse it into html variable
    html = parser.fromstring(r.text)

    # Get all items of internal-link class (This class define each month of each year in website)
    items_from_class = html.xpath("//a[@class='internal-link']")

    # Get all links from items into a list of tuples where the first element is the link to download, second element is
    # the month and the third is the year.
    # - href is the link to download
    # - text is the month (as string)
    # - year is taken from the link to download
    all_links = [(item.attrib['href'], item.text, item.attrib['href'].split('/')[-2]) for item in items_from_class]

    return all_links


def remove_links_with_no_month_reference(all_links: list) -> list:
    """
    function to remove all links that don't have an association with a month. All entries with None or '\xa0' instead
    of month name.

    args:

        all_links: list -> List of tuples where the first index is the link, second index is the month and third index
        is the year.

    return:
        only_entries_with_month_reference: list -> Returns a list with valid links.
    """

    only_links_with_month_reference = [item for item in all_links if item[1] is not None and item[1] != '\xa0']

    return only_links_with_month_reference


def download_files(valid_links: list) -> list:
    """
    function to download all files from valid_links list.

    args:

        valid_links: list -> list of tuples containg all valid links to download and the month and year associated.

    return:

        year_month_filepath: list -> list of tuples containing year, month and the filepath (where file were saved with
        standard names).
    """
    print('Starting process...')
    print('')

    year_month_filepath = []

    for link_info in valid_links:

        # Get file extension
        extension = link_info[0].split('.')[-1]

        # Link to download
        link_to_download = link_info[0]

        # Get month
        month = link_info[1]

        # Get year
        year = link_info[2]

        # Create a standard filename to save
        file_name = f'{year}-{month}.{extension}'

        print(f'Downloading... {link_to_download} Saving... {file_name}')

        # Create a link to save into ./file directory
        link_to_save = f'./file/{file_name}'

        # Download file and save it
        wget.download(link_to_download, out=link_to_save)


        # Special treatment to zip and xlsx file
        if extension == 'zip':

            # Get right link to save (.csv) from zip function
            link_to_save = get_file_into_zip(link_to_save)

        elif extension == 'xlsx':
            # Get right link to save (.csv) from xlsx function
            link_to_save = excel2csv(link_to_save)

        # Include the tuple into a list
        year_month_filepath.append((year, month, link_to_save))

    print('Finishing process...')

    return year_month_filepath


def excel2csv(excel_path: str) -> str:
    """
    Function to convert excel to csv, removing original excel file.

    args:

        excel_path: str -> path to excel file.

    return:

        csv_path: str -> path to created csv file.
    """
    csv_path = excel_path.replace('xlsx', 'csv')

    # Create pandas Data Frame from an excel file and save it into csv.
    df_excel = pd.read_excel(excel_path)
    df_excel.to_csv(csv_path, index=False)

    os.remove(excel_path)

    excel_filename = excel_path.split('/')[-1]
    csv_filename = csv_path.split('/')[-1]

    print(f"Extracting csv from xlsx... {excel_filename} Saving... {csv_filename}'")
    print(f"Deleting... {excel_filename}")

    return csv_path


def get_file_into_zip(zip_path: str) -> str:
    """
    Function to extract csv file from zip, removing the zip file.

    args:
        zip_path: str -> path to zip file.

    return:

        csv_path: str -> path to extracted csv file.
    """

    # Read csv file from zip and save it as csv.
    with zipfile.ZipFile(zip_path) as zf:

        csv_file_in_zip = zf.namelist()[0]
        csv_path = zip_path.replace('zip', 'csv')

        with open(csv_path, "wb") as f:

            f.write(zf.read(csv_file_in_zip))


    os.remove(zip_path)

    zip_filename = zip_path.split('/')[-1]
    csv_filename = csv_path.split('/')[-1]

    print(f"Extracting csv from zip... {zip_filename} Saving... {csv_filename}")
    print(f"Deleting... {zip_filename}")

    return csv_path


def create_unique_file(files_to_concat: list) -> pd.DataFrame:
    """
    Function to read all files into data frames and concatenate creating just an unique file.

    args:

        files_to_concat: list -> list of tuples containing year, month and standardized file path

    return:

        unique_df: pd.DataFrame -> Pandas Data Frame with all data concatenated

    """
    dfs_to_concat = []

    print(f'Number of files: {len(files_to_concat)}')

    for file in files_to_concat:

        year = int(file[0])
        month = file[1]
        filepath = file[2]

        # Use pd.read_csv to solve some problems with files
        # engine: python - This parameter is slower compared to c-engine but handle but handle
        # some problematic characters better
        # sep="[\t;]" - using python-engine it's possible to use regular expressions to define the sep char, where
        # python identify the char to use with each file.
        # skiprows = 1 - As the columns have different names in many files, I just combine header=None with skiprows=1
        # with this, just data is read.
        actual_df = pd.read_csv(filepath, engine='python', sep="[\t;]", skiprows=1, header=None, dtype='category')

        # File 2017-Dezembro.csv has duplicate columns so an if is necessary here just to solve this problem.
        if month == 'Dezembro' and year == 2017:

            del(actual_df[7])
            actual_df.columns = [n for n in range(12)]

        # Creating two new columns with month and year for each file.
        actual_df['month'], actual_df['year'] = zip(*[(month, year) for n in range(len(actual_df))])

        print(f'Processing file: {filepath}')

        dfs_to_concat.append(actual_df)

    # Concat all files into unique_df
    unique_df = pd.concat(dfs_to_concat, axis=0, ignore_index=True)

    return unique_df


def rename_columns() -> list:
    """
    Function to rename ANAC columns according to a pattern.
    """
    columns_name = ['ICAO_empresa_aerea', 'numero_voo', 'codigo_DI', 'codigo_tipo_linha',
                     'ICAO_aerodromo_partida', 'ICAO_aerodromo_destino', 'partida_prevista',
                     'partida_real', 'chegada_prevista', 'chegada_real', 'situacao_voo',
                     'codigo_justificativa', 'month', 'year']

    return columns_name


def main():

    anac_website = "https://www.anac.gov.br/assuntos/dados-e-estatisticas/historico-de-voos"

    print('All files will be saved into ./file directory')
    print('Creating ./file directory')
    create_file_directory()
    print('./file directory was created')

    print('Getting all links from website...')
    all_links_from_website = get_all_links_from_html(anac_website)
    print('Getting all links from website - Completed')

    print('Selecting valid links to download...')
    valid_links_to_download = remove_links_with_no_month_reference(all_links_from_website)
    print('Selecting valid links to downaload - Completed')

    print('Downloading files...')
    files_to_concat = download_files(valid_links_to_download)
    print('Downloading files - Completed')

    print('Concatenating files...')
    ANAC_dataset_2000_2020 = create_unique_file(files_to_concat)
    print('concatenating files - Completed')

    ANAC_dataset_2000_2020.columns = rename_columns()

    print('Saving .csv...')
    ANAC_dataset_2000_2020.to_csv('./file/ANAC_dataset_2000_2020.csv', index=False)
    print('Saving .csv - Completed')

    print('ANAC dataset is ready to use, enjoy!')

if __name__ == '__main__':

    main()
