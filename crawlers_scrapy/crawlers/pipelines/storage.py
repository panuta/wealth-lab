import pandas as pd
import numpy as np
from collections import defaultdict
from pathlib import Path


class CSVStoragePipeline(object):
    storage_root_folder = '../storage/crawled/'

    def __init__(self):
        self.saving_data = defaultdict(list)  # filename -> list of data
        self.item_metadata = {}  # filename -> metadata

    def close_spider(self, spider):
        for filename, data in self.saving_data.items():
            data_df = pd.DataFrame(np.array(data), columns=self.item_metadata[filename]['csv_columns'])

            # Load existing CSV file
            csv_file_abspath = Path('{}{}'.format(self.storage_root_folder, filename)).resolve()
            try:
                existing_data_df = pd.read_csv(csv_file_abspath)
            except FileNotFoundError:
                pass
            else:
                data_df = pd.concat([existing_data_df, data_df]).drop_duplicates(subset='date', keep='last').sort_values(by=['date'])

            data_df.to_csv(csv_file_abspath, index=False)

    def process_item(self, item, spider):
        csv_filename = getattr(item, 'CSV_FILENAME')
        real_filename = csv_filename.format(**dict(item))

        # Save metadata
        self.item_metadata[real_filename] = {
            'real_filename': real_filename,
            'csv_filename': csv_filename,
            'csv_columns': getattr(item, 'CSV_COLUMNS'),
            'csv_unique_columns': getattr(item, 'CSV_UNIQUE_COLUMNS'),
        }

        # Save data to temporary variable
        self.saving_data[real_filename].append([item.get(col_name, '') for col_name in self.item_metadata[real_filename]['csv_columns']])
