from bs4 import BeautifulSoup

def remove_empty_rows_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', {'class': 'waffle'})

    rows = table.find_all('tr')
    for row in rows:
        if all(not td.text.strip().replace('\u2063', '') for td in row.find_all('td')):
            row.extract()

    return str(soup)


def remove_empty_columns_from_html(html_content):
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
        column_empty = all(not (row.find_all('td')[col_index].text.strip().replace('\u2063', '') if col_index < len(
            row.find_all('td')) else '') for row in table.find_all('tr'))
        if column_empty:
            for row in table.find_all('tr'):
                if col_index < len(row.find_all('td')):
                    row.find_all('td')[col_index].extract()

    return str(soup)


def save_html_to_file(html_content, file_path):
    with open(file_path, 'w') as f:
        f.write(html_content)


def update_text_styles(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    link_tag = soup.find('link', {'type': 'text/css', 'rel': 'stylesheet', 'href': 'resources/sheet.css'})
    if link_tag:
        link_tag.extract()

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

    return (prepended_styles + str(soup))


def spreadsheet_splitter(html_content, rows_per_chunk=1):
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')

    html_slices = []
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

            # Append the processed chunk to the list of slices
            html_slices.append(str(row))

    return html_slices


def html_processor(html_content):
    first_step = remove_empty_columns_from_html(html_content)
    second_step = remove_empty_rows_from_html(first_step)
    final_step = update_text_styles(second_step)
    return (final_step)
