
def clean_num_string(str):
    if str == '-':
        return '0'
    return str.replace(',', '')
