from trades.trade_finder import find_trades

def build_trades_df(companies, df_companies):
    print(companies[0].ticker)
    for current_comp in df_companies.itertuples():
        comp_obj = next(company for company in companies if company.ticker == current_comp.company)
        if ((comp_obj.direction != "none") and 
            (len(comp_obj.expiry_dates) > 0) and
            (comp_obj.dir_streak >= 12) and
            (comp_obj.dir_streak <= 33)):
            if comp_obj.direction == 'bull':
                comp_obj.df_contracts = comp_obj.df_contracts[comp_obj.df_contracts['call_put'] == 'P'].reset_index(drop=True)
            else:
                comp_obj.df_contracts = comp_obj.df_contracts[comp_obj.df_contracts['call_put'] == 'C'].reset_index(drop=True)
            comp_obj.get_greeks()
            comp_obj.filter_contracts_by_greeks()
            find_trades(comp_obj)
    return