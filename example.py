from main import formatter


# list of column names in tuple form
# the 1st index of each tuple is the default named
# further names are used to better match wide changing
# column names
col_names = [("price","price of item"),("sale","sale price"),("savings")]




# 'remove_expired': remove expired rows based on date vs date now
# 'remove_strikes': remove striked date rows
# 'dir': directory

f = formatter(settings={
                      "remove_strikes":1
                      ,"remove_expired":1}
            ,dir = "files1"
            ,column_names=col_names)

# name of the wanted date_cols if value passed, remove_expired will not work
# days_past_today, how many days before the expiration date the date will be considered expired, default is 0,
# combine: combines all files processesed into one dateframe otherwise return a list of all dataframes processed
# by default will read 4000 rows, this is set in case blank data is in sheet and causes long hang times
df = f.process_files(date_cols = ["expired_date"]
                    ,days_past_today=-100000
					,combine=True
                    ,max_rows=4000)

print(df)
