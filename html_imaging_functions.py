from bs4 import BeautifulSoup
from typing import List, Tuple

def remove_empty_rows_from_html(html_content: str) -> str:
    """Removes rows with only empty cells."""
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', {'class': 'waffle'})

    # Find all rows with empty td elements (considering '\u2063') and remove them
    rows = table.find_all('tr')
    for row in rows:
        if all(not td.text.strip().replace('\u2063', '') for td in row.find_all('td')):
            row.extract()

    return str(soup)


def remove_empty_columns_from_html(html_content: str) -> str:
    """Removes columns with only empty cells."""
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', {'class': 'waffle'})

    # Find the maximum number of columns
    max_columns = 0
    for row in table.find_all('tr'):
        num_columns = len(row.find_all('td'))
        if num_columns > max_columns:
            max_columns = num_columns

    # Find all columns with empty td elements and remove them
    for col_index in range(max_columns):
        column_empty = all(
            not (row.find_all('td')[col_index].text.strip().replace('\u2063', '')
                 if col_index < len(row.find_all('td')) else '')
            for row in table.find_all('tr')
        )
        if column_empty:
            for row in table.find_all('tr'):
                if col_index < len(row.find_all('td')):
                    row.find_all('td')[col_index].extract()

    return str(soup)


def update_text_styles(html_content: str) -> str:
    """Updates text styles in spreadsheet HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')

    link_tag = soup.find('link', {'type': 'text/css', 'rel': 'stylesheet', 'href': 'resources/sheet.css'})
    if link_tag:
        link_tag.extract()

    # Find all elements with class "softmerge-inner" and update their style attribute
    softmerge_inner_elements = soup.find_all(class_='softmerge-inner')
    for element in softmerge_inner_elements:
        element['style'] = 'width: auto; overflow: hidden; padding: 5px; margin: 0; text-overflow: ellipsis;'

    prepended_styles = '''<style>
     table {
                border-collapse: collapse;
            }
            td {
                border: 1px solid black;
                padding: 8px;
            }
</style>'''

    return prepended_styles + str(soup)


def extract_headers(html_content: str) -> Tuple[List[str], List[str]]:
    """Extracts row and column headers from the HTML table."""
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        row_headers = [row.find('td').text.strip() for row in rows[1:]]
        col_headers = [th.text.strip() for th in rows[0].find_all('td')[1:]] if rows[0] else []
    return row_headers, col_headers


def spreadsheet_splitter(html_content: str, rows_per_chunk: int = 1) -> List[str]:
    """Splits the HTML table into slices based on a specified number of rows per chunk."""
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')

    html_slices: List[str] = []
    for table in tables:
        rows = table.find_all('tr')
        notes_row = rows[0]
        col_headers = [th.text.strip() for th in notes_row.find_all('td')[1:]] if notes_row else []

        num_rows = len(rows)
        for i in range(0, num_rows, rows_per_chunk):
            chunk_rows = rows[i:i + rows_per_chunk]

            for j, row in enumerate(chunk_rows):
                cells = row.find_all(['td', 'th'])
                cells = cells[1:]
                for k, cell in enumerate(cells):
                    if k == 0 and j == 0:
                        original_content = cell.get_text().strip()
                        cell.clear()
                        value_label = soup.new_tag('p')
                        value_label.string = f"Header for this row: {original_content}"
                        cell.append(value_label)
                    else:
                        original_content = cell.get_text().strip()
                        cell.clear()

                        if k - 1 < len(col_headers):
                            col_label = soup.new_tag('p')
                            col_label.string = f"Column: {col_headers[k - 1]}"
                            cell.append(col_label)

                        value_label = soup.new_tag('p')
                        value_label.string = f"Value: {original_content}"
                        cell.append(value_label)

            html_slices.append(str(row))
    return html_slices


def html_processor(html_content: str) -> str:
    """Prepares HTML content by removing blank data and updating text styles."""
    first_step = remove_empty_columns_from_html(html_content)
    second_step = remove_empty_rows_from_html(first_step)
    final_step = update_text_styles(second_step)
    return final_step
