import numpy as np
from pandas import DataFrame
from commodity_pool.base import BaseCommodityPool


class DynamicPool3(BaseCommodityPool):

    def __init__(self, q: float = 0.25, window: int = 126) -> None:
        super().__init__(q=q, window=window)

    def compute_commodity_pool(self) -> DataFrame:
        daily_data = self.daily_data_manager.get_daily_data()
        daily_open_interest = daily_data.groupby(['datetime', 'underlying_symbol'], as_index=True)[
            'open_interest'].sum(). \
            unstack(level=-1)
        daily_rolling_open_interest = daily_open_interest.rolling(window=self.window, min_periods=0).mean()
        daily_rolling_open_interest.loc[:, ['IF', 'IH', 'IC', 'T', 'TF', 'TS', 'SC', 'NR', 'LU', 'BC']] = np.nan
        daily_quantile = daily_rolling_open_interest.quantile(q=self.q, axis=1, interpolation='higher')
        commodity_pool_value = (daily_rolling_open_interest.T >= daily_quantile).T
        commodity_pool_value.fillna(False, inplace=True)

        self.commodity_pool_value = commodity_pool_value
        return commodity_pool_value