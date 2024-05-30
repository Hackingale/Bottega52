import pandas as pd


def valid_format(to_test, reference):

    # take the column names
    to_test_columns = to_test.columns
    reference_columns = reference.columns

    return to_test_columns.size == reference_columns.size and sorted(to_test_columns.tolist()) == sorted(reference_columns.tolist())


def compute_correctness(to_test, reference, keys_header, to_exclude):

    if keys_header in to_exclude:
        print('The keys header is in the list of columns to exclude, operation aborted')
        return 'Invalid format'

    # extract keys from the test set and the reference set
    players = to_test[keys_header]
    players_reference = reference[keys_header]

    # drop the columns that are not relevant for the comparison
    to_test = to_test.drop(columns=to_exclude)
    reference = reference.drop(columns=to_exclude)

    # initialize the correctness variable
    correctness = 0
    total = 0

    if players_reference.size == 0:
        return 'No players found in the reference set'

    # iterate over the players
    for player in players.values:
        # check if the player is present in the second DataFrame
        if player in players_reference.values:
            # extract the values of the player row from the first DataFrame and place it into an array
            values = to_test.loc[to_test[keys_header] == player].values.flatten().tolist()
            # extract the values of the player row from the second DataFrame and place it into an array
            values_reference = reference.loc[reference[keys_header] == player].values.flatten().tolist()

            total += len(values_reference)
            for i in range(0, len(values_reference)):
                if values[i] == values_reference[i]:
                    correctness += 1

    return str(correctness / total * 100) + ' %'


def validate_output(to_test, reference, keys_header, to_exclude):
    if valid_format(to_test, reference):
        return compute_correctness(to_test, reference, keys_header, to_exclude)
    else:
        return 'Invalid format'


# print(valid_format(pd.read_excel('../HTML/uploaded/Output.xlsx'), pd.read_excel('../HTML/uploaded/TestSet.xlsx')))
# print(compute_correctness(pd.read_excel('../HTML/uploaded/Output.xlsx'), pd.read_excel('../HTML/uploaded/TestSet.xlsx'), ['Website ok (optional)']))