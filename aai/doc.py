# -*- coding: utf-8 -*-
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

#   Licensed under the Apache License, Version 2.0 (the "License").
#   You may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import pandas as pd

import logging

from aai import config as _config

log = logging.getLogger("aws-auto-inventory.doc")


def write_worksheet(df):

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter("pandas_column_formats.xlsx", engine="xlsxwriter")

    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name="Sheet1")

    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]

    # Add some cell formats.
    format1 = workbook.add_format({"num_format": "#,##0.00"})
    format2 = workbook.add_format({"num_format": "0%"})

    # Note: It isn't possible to format any cells that already have a format such
    # as the index or headers or any cells that contain dates or datetimes.

    # Set the column width and format.
    worksheet.set_column("B:B", 18, format1)

    # Set the format but not the column width.
    worksheet.set_column("C:C", None, format2)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


def write_data(name, transpose, data):
    file_path = _config.filepath
    file_name = name + _config.file_name

    # log.info('Started: writing document {} on sheet {}'.format(file_name, sheet_name))

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter("{}{}".format(file_path, file_name), engine="xlsxwriter")

    # transpose = _config.settings.config['excel']['transpose'].get()

    for d in data:
        df = pd.DataFrame(d["Result"])

        # fix: Excel does not support datetimes with timezones. Please ensure that datetimes are timezone unaware before writing to Excel.
        for col in df.select_dtypes(["datetimetz"]).columns:
            df[col] = df[col].dt.tz_convert(None)

        sheet_name = d["Name"]
        if transpose:
            df.transpose().to_excel(writer, sheet_name=sheet_name)
            worksheet = writer.sheets[sheet_name]
            # Adjust at least the first column width
            worksheet.set_column("A:A", 60)
        else:
            df.to_excel(writer, sheet_name=sheet_name)
            # Adjust all columns widths
            for column in df:
                column_length = max(df[column].astype(str).map(len).max(), len(column))
                col_idx = df.columns.get_loc(column)
                writer.sheets[sheet_name].set_column(col_idx, col_idx, column_length)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    print("Report generated successfully at: {}{}".format(file_path, file_name))
