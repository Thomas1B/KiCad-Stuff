'''
Python Script to simplify to DigiKey's BOM generator.

The DigiKey BOM generator, in my opinion, adds a lot of unnessecary information.
This program reads a BOM from the downloads folder using the pandas python package then
removes unnessecary information, it also renames the columns for easier reading and adds 
a total price. At the end, the user has the option to print and/or save the "new" BOM 
under a modify filename.

Note: simplify and edit are use interchangably throughout comments.
'''


import pandas as pd
import os

# filepath to downloads folder
downloads_path = os.path.expanduser("~") + "/Downloads/"

# list of only csv and xlsx files
files = [
    file for file in os.listdir(downloads_path) if file.endswith(('csv', 'xlsx'))
]


# list of column headers to keep
keepers = [
    'Description',
    'Manufacturer Name',
    'Manufacturer Part Number',
    'Digi-Key Part Number 1',
    'Unit Price 1',
    'Requested Quantity 1']

# dict of new column for renaming
new_headers = {
    'Manufacturer Name': 'Manufacturer',
    'Requested Quantity 1': 'Quantity',
    'Digi-Key Part Number 1': 'Digi-Key Part Number',
    'Unit Price 1': 'Unit Price',
}


def main():
    '''
    Main Function.
    '''

    file_to_edit = None

    print('\nWelcome to the DigiKey BOM Simplifier!\n')

    # Making a string to show avaliable BOMs to edit.
    options_text = ''
    if len(files) > 0:
        options_text = 'Avaliable BOMs to edit:\n'
        options_text += '\n'.join(
            [f'-> {i:>3}: {file}' for i, file in enumerate(files, 1)]
        )
        options_text += f'\n-> {"q":>3}: Quit Program.'
        options_text += '\n\nWhich BOM would you like to simplify: '
    else:
        text = 'There are no BOMs to edit. Check your downloads for one!\n'
        text += 'Note: The BOM must a "CSV" file.'
        exit(text)

    while True:

        # try block to insure user enter an integer when picking which BOM to edit.``
        try:
            user = input(options_text)

            if user.lower() in ['q', 'quit']:  # checking if user wants to quit
                exit("-> User quit program.\n")

            # converting user's entry to integer (triggers execption).
            user = int(user)

            # checking if user enter an avaliable option
            if user > 0 and user < len(files)+1:
                file_to_edit = files[user-1]
                break
            else:
                print(f'Option "{user}" is not avaliable, try again.\n')

        except Exception as err:
            # user didn't enter an integer
            print('You must enter an integer, try again.\n')

    BOM = simplify_BOM(file_to_edit)  # simplifying BOM/

    user = input('Would you like to see the new BOM? (y/n): ')
    if user.lower() in ['yes', 'y']:
        if BOM.shape[0] > 30:
            user = input("This BOM is quite large, are you sure? (y/n): ")
            if user.lower() in ['yes', 'y']:
                print(BOM)
        else:
            print(BOM)

    ask_user_to_save(file_to_edit, BOM)


# *********** Functions ***********

def ask_user_to_save(file: str, BOM: pd.DataFrame):
    '''
    Function to ask the user if they want to save the editted BOM.

        Parameters:
            file: filename of BOM.
            BOM: dataframe of "new" BOM.

        Returns:
            None
    '''

    # creating new filename for saving the editted BOM.
    base, ext = os.path.splitext(file)
    new_filename = f'{base} Digikey BOM{ext}'

    text = '\nWould you like to save the editted BOM? (y/n)\n'
    text += f'The editted BOM will be saved as "{new_filename}" in your downloads: '
    user = input(text)
    if user.lower() in ['yes', 'y']:
        BOM.to_csv(f'{downloads_path}/{new_filename}', index=False)
        print('BOM was saved!\n')
    else:
        print("BOM not saved.\n")


def simplify_BOM(filename: str) -> pd.DataFrame:
    '''
    Function to simplify the given BOM by removing unwanted columns, rename and total price.

        Parameters:
            filename: name of BOM to edit, must be in the downloands folder.

        Returns:
            pandas dataframe
    '''
    data = None

    path = f'{downloads_path}/{filename}'  # making filepath to desired BOM.

    # checking user file is a csv or xlsx.
    ext = path.split('.')[-1]
    if ext == 'csv':
        data = pd.read_csv(path)[keepers]
    else:
        data = pd.read_excel(path)[keepers]

    data.rename(columns=new_headers, inplace=True)  # renaming columns

    # calculating prices for each item based on quantity
    prices = pd.Series(
        data['Unit Price']*data['Quantity'],
        name='Item Price'
    )
    # calculating the total price.
    total_price = pd.Series(prices.sum(), name='Total Price')

    # returning "new" BOM.
    return pd.concat([data, total_price], axis=1)


if __name__ == '__main__':
    while True:
        main()
