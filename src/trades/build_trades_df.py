def build_trades_df(companies, df_companies):
    print(companies[0].ticker)
    for current_comp in df_companies.itertuples():
        comp_obj = next(company for company in companies if company.ticker == current_comp.ticker)
        print(comp_obj)
        # print(len(company.expiry_dates))
        # if ((company.direction != "none") and 
        #     (len(company.expiry_dates) > 0) and
        #     (company.dir_streak >= 12) and
        #     (company.dir_streak <= 33)):
        #     company.get_greeks()
        #     print(company.df_contracts.dropna())
    return