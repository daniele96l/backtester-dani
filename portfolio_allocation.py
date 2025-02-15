import pandas as pd
import numpy as np
from typing import List, Dict
from config import COUNTRY_ALLOCATION_FILE_PATH,SECTOR_ALLOCATION_FILE_PATH

class PortfolioAllocation:
    def calculate_country_allocation(self, indexes: List[str], weights: Dict[str, List[float]]) -> pd.DataFrame:
        """
        Calculate weighted country allocations for given indexes considering the whole portfolio.

        Args:
            indexes: List of index names to filter from the dataset.
            weights: Dictionary with a single key 'weights' containing a list of weights.

        Returns:
            pd.DataFrame: DataFrame containing the weighted country allocations.
        """
        try:
            # Read and validate data
            df = pd.read_csv(COUNTRY_ALLOCATION_FILE_PATH)

            if df.empty:
                raise ValueError("CSV file is empty")
            if not all(col in df.columns for col in ['Index', 'Country', 'Allocation']):
                raise ValueError("CSV missing required columns: Index, Country, Allocation")

            # Filter for requested indexes
            df = df[df['Index'].isin(indexes)]

            # Check if any assets are present
            if df.empty:
                return pd.DataFrame({'Paese': ['No data'], 'Peso': [100]})

            # Remove duplicate country entries within each index
            df = df.drop_duplicates(subset=['Index', 'Country'], keep='first')

            # Ensure weights list length matches indexes
            if len(weights['weights']) != len(indexes):
                raise ValueError("Weights list length does not match number of indexes")

            # Create a weight mapping for indexes
            weight_mapping = dict(zip(indexes, weights['weights']))

            # Apply weight to allocation values
            df['Weighted_Allocation'] = df.apply(lambda row: row['Allocation'] * weight_mapping[row['Index']], axis=1)

            # Normalize weights so they sum to 100
            df['Weighted_distibuted_Allocation'] = 100 * df['Weighted_Allocation'] / df['Weighted_Allocation'].sum()

            # Aggregate weighted allocations by country
            result = df.groupby('Country', as_index=False)['Weighted_distibuted_Allocation'].sum()

            # Rinomina le cose in italiano
            result = result.rename(
                columns={'Country': 'Paese', 'Weighted_distibuted_Allocation': 'Peso'})

            return result

        except Exception as e:
            print(f"Error in calculation: {e}")
            return pd.DataFrame()

    def calculate_sector_allocation(self, indexes: List[str], weights: Dict[str, List[float]]) -> pd.DataFrame:
        """
        Calculate weighted country allocations for given indexes considering the whole portfolio.

        Args:
            indexes: List of index names to filter from the dataset.
            weights: Dictionary with a single key 'weights' containing a list of weights.

        Returns:
            pd.DataFrame: DataFrame containing the weighted country allocations.
        """
        try:
            # Read and validate data
            df = pd.read_csv(SECTOR_ALLOCATION_FILE_PATH)

            if df.empty:
                raise ValueError("CSV file is empty")
            if not all(col in df.columns for col in ['Index', 'Sector', 'Allocation']):
                raise ValueError("CSV missing required columns: Index, Sector, Allocation")

            # Filter for requested indexes
            df = df[df['Index'].isin(indexes)]

            # Check if any assets are present
            if df.empty:
                return pd.DataFrame({'Settore': ['No data'], 'Peso': [100]})

            # Remove duplicate country entries within each index
            df = df.drop_duplicates(subset=['Index', 'Sector'], keep='first')

            # Ensure weights list length matches indexes
            if len(weights['weights']) != len(indexes):
                raise ValueError("Weights list length does not match number of indexes")

            # Create a weight mapping for indexes
            weight_mapping = dict(zip(indexes, weights['weights']))

            # Apply weight to allocation values
            df['Weighted_Allocation'] = df.apply(lambda row: row['Allocation'] * weight_mapping[row['Index']],
                                                 axis=1)

            # Normalize weights so they sum to 100
            df['Weighted_distibuted_Allocation'] = 100 * df['Weighted_Allocation'] / df['Weighted_Allocation'].sum()

            # Aggregate weighted allocations by country
            result = df.groupby('Sector', as_index=False)['Weighted_distibuted_Allocation'].sum()

            # Rinomina le cose in italiano
            result = result.rename(
                columns={'Sector': 'Settore', 'Weighted_distibuted_Allocation': 'Peso'})

            return result

        except Exception as e:
            print(f"Error in calculation: {e}")
            return pd.DataFrame()



        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find allocation file at {COUNTRY_ALLOCATION_FILE_PATH}")
        except Exception as e:
            raise Exception(f"Error calculating country allocations: {str(e)}")

