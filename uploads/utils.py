import pandas as pd

REQUIRED_COLUMNS = {'advertiser', 'brand', 'start', 'end', 'format', 'platform', 'impr'}


def normalize_columns(df):
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def validate_dataframe(df):
    cols = set(df.columns)
    matched = cols.intersection(REQUIRED_COLUMNS)
    if len(matched) == 0:
        return False, "Повна невідповідність даних: жодна колонка не відповідає шаблону"
    if len(matched) < len(REQUIRED_COLUMNS):
        missing = REQUIRED_COLUMNS - matched
        return False, f"Відсутні обов'язкові колонки: {', '.join(sorted(missing))}"
    if 'start' in df.columns and 'end' in df.columns:
        if df['start'].isna().all() and df['end'].isna().all():
            return False, "Колонки дат (Start, End) не містять жодного дійсного значення"
    return True, ""


def parse_dataframe(df):
    df = normalize_columns(df)
    valid, error = validate_dataframe(df)
    if not valid:
        return None, error
    records = []
    for _, row in df.iterrows():
        try:
            start_date = pd.to_datetime(row.get('start'), errors='coerce')
            end_date = pd.to_datetime(row.get('end'), errors='coerce')
            year = int(start_date.year) if pd.notna(start_date) else None
            impr_val = row.get('impr', 0)
            try:
                impr_val = int(impr_val) if pd.notna(impr_val) else 0
            except (ValueError, TypeError):
                impr_val = 0
            records.append({
                'advertiser': str(row.get('advertiser', '')),
                'brand': str(row.get('brand', '')),
                'start_date': start_date.date() if pd.notna(start_date) else None,
                'end_date': end_date.date() if pd.notna(end_date) else None,
                'format': str(row.get('format', '')),
                'platform': str(row.get('platform', '')),
                'impr': impr_val,
                'year': year,
            })
        except Exception:
            continue
    if not records:
        return None, "Не вдалося обробити жодного запису з файлу"
    return records, ""


def read_file(file_obj, filename):
    ext = filename.rsplit('.', 1)[-1].lower()
    try:
        if ext == 'csv':
            df = pd.read_csv(file_obj)
        elif ext == 'xlsx':
            df = pd.read_excel(file_obj, engine='openpyxl')
        elif ext == 'xls':
            df = pd.read_excel(file_obj, engine='xlrd')
        else:
            return None, "Непідтримуваний формат. Використовуйте XLS, XLSX або CSV"
    except Exception as e:
        return None, f"Помилка читання файлу: {str(e)}"
    return df, ""
