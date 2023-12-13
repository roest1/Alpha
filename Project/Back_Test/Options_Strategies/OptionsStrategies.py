import pandas as pd

"""
Notes:

The current implementation for selecting ITM, ATM, and OTM options is based on the strike_preference parameter. 
You could enhance this logic to dynamically select strike prices based on specific trading strategies or market conditions.

Add functionality to calculate and return important metrics like potential profit/loss, break-even points, or risk/reward ratios for selected options.



"""
class OptionsStrategies:
    def __init__(self, options_data):
        """
        Initialize with options data.
        :param options_data: DataFrame with options data.
        """
        self.options_data = options_data

    def classify_option(self, stock_price, strike_price, cp_flag):
        """
        Classifies an option as ITM, ATM, or OTM.
        """
        if cp_flag == 'C':  # Call option
            if stock_price > strike_price:
                return 'ITM'
            elif stock_price < strike_price:
                return 'OTM'
            else:
                return 'ATM'
        elif cp_flag == 'P':  # Put option
            if stock_price < strike_price:
                return 'ITM'
            elif stock_price > strike_price:
                return 'OTM'
            else:
                return 'ATM'

    def select_option(self, date, ticker, cp_flag, stock_price, strike_preference='ATM', expiry_range=None):
        """
        Selects the most appropriate option based on the given criteria.
        """
        # Filter options for the given date and ticker
        daily_options = self.options_data[(self.options_data['date'] == date) &
                                          (self.options_data['ticker'] == ticker) &
                                          (self.options_data['cp_flag'] == cp_flag)]

        # Further filter by expiration range if provided
        if expiry_range:
            daily_options = daily_options[daily_options['exdate'].apply(
                lambda x: expiry_range[0] <= (x - pd.to_datetime(date)).days <= expiry_range[1])]

        # Classify each option as ITM, ATM, or OTM
        daily_options['moneyness'] = daily_options.apply(
            lambda row: self.classify_option(stock_price, row['strike_price'], cp_flag), axis=1)

        # Filter options based on strike preference
        if strike_preference:
            daily_options = daily_options[daily_options['moneyness']
                                          == strike_preference]

        # Further refine selection based on liquidity, implied volatility, etc.
        selected_option = daily_options.sort_values(
            by=['open_interest', 'volume'], ascending=False).iloc[0]

        return selected_option

    def long_call(self, date, ticker, stock_price, strike_preference='ATM', expiry_range=None):
        """
        Long Call strategy implementation.
        """
        selected_option = self.select_option(
            date, ticker, 'C', stock_price, strike_preference, expiry_range)
        option_details = selected_option.to_dict()
        return {
            'strategy': 'Long Call',
            'strike_price': option_details['strike_price'],
            'best_bid': option_details['best_bid'],
            'best_offer': option_details['best_offer'],
            'volume': option_details['volume'],
            'open_interest': option_details['open_interest'],
            'impl_volatility': option_details['impl_volatility'],
            'delta': option_details['delta'],
            'gamma': option_details['gamma'],
            'vega': option_details['vega'],
            'theta': option_details['theta'],
            'expiration_date': option_details['exdate'],
            'option_id': option_details['optionid'],
            'exercise_style': option_details['exercise_style']
        }

    def long_put(self, date, ticker, stock_price, strike_preference='ATM', expiry_range=None):
        """
        Long Put strategy implementation.
        """
        selected_option = self.select_option(
            date, ticker, 'P', stock_price, strike_preference, expiry_range)
        option_details = selected_option.to_dict()
        return {
            'strategy': 'Long Put',
            'strike_price': option_details['strike_price'],
            'best_bid': option_details['best_bid'],
            'best_offer': option_details['best_offer'],
            'volume': option_details['volume'],
            'open_interest': option_details['open_interest'],
            'impl_volatility': option_details['impl_volatility'],
            'delta': option_details['delta'],
            'gamma': option_details['gamma'],
            'vega': option_details['vega'],
            'theta': option_details['theta'],
            'expiration_date': option_details['exdate'],
            'option_id': option_details['optionid'],
            'exercise_style': option_details['exercise_style']
        }
