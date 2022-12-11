# python custom functions

def _cols_check(table: pd.DataFrame, cols: [str]):
    assert all([c in table.columns for c in cols]), \
        "some columns in 'cols' are not in your table!"

        
def find_multiword_rows(table: pd.DataFrame, cols: [str]) -> pd.DataFrame:
    _cols_check(table, cols)

    _filter = None
    for col in cols:
        err = table[col].apply(lambda x: len(x.split()) > 1)
        if _filter is None:
            _filter = err
        else:
            _filter |= err

    return table[_filter]

def check_singleword(entries):
    for w in entries:
        assert len(w.strip().split(" ")) == 1, "'%s' is not a single word" % w
        
#find_padded_rows(tr_tresor, cols=['Genus'])

err = find_multiword_rows(tr_tresor, ['Genus', 'Species'])
err
