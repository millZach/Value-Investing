def format_df(lst):
    '''
    Copied from: https://github.com/VincentTatan/ValueInvesting/blob/master/format.py
    Credit: Vincent Tatan
    added try except to account for dates
    moved posornegnumber within for loop
    '''
    newlist = []
    for text in lst:
        try:
            # moved this within for loop
            posornegnumber = 1
            if text.endswith(')'):
                # remove the parentheses
                text = text[1:-1]
                posornegnumber = -1

            if text.endswith('%'):
                # Then please make it into comma float
                endtext = float(text[:-1].replace(",", "")
                                ) / 100.0 * posornegnumber
            elif text.endswith('B'):
                # Then please times 1000000000
                # Change it into integer
                endtext = int(
                    float(text[:-1].replace(",", "")) * 1000000000) * posornegnumber
            elif text.endswith('M'):
                # Then please times 1000000
                # Change it into integer
                endtext = int(
                    float(text[:-1].replace(",", "")) * 1000000) * posornegnumber
            elif ',' in text:
                # Then please remove the ,
                # Then change it into int
                endtext = int(float(text.replace(",", ""))) * posornegnumber

            elif text.endswith('-'):
                # Insert 0
                endtext = 0
            else:
                # change to float
                endtext = float(text) * posornegnumber

            newlist.append(endtext)
        except:
            newlist.append(text)
    return newlist
