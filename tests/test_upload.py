import pytest
import io
import pandas as pd
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from uploads.models import FileUploadLog, DataRecord
from uploads.utils import (
    normalize_columns,
    validate_dataframe,
    parse_dataframe,
    read_file,
)


def make_valid_excel():
    df = pd.DataFrame({
        'Advertiser': ['TestAdv', 'TestAdv'],
        'Brand': ['BrandA', 'BrandA'],
        'Start': ['2021-01-04', '2022-03-01'],
        'End': ['2021-01-10', '2022-03-07'],
        'Format': ['banner', 'video'],
        'Platform': ['DV360', 'DV360'],
        'Impr': [1000000, 2000000],
    })
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine='openpyxl')
    buf.seek(0)
    return buf


def make_invalid_excel():
    df = pd.DataFrame({
        'ColA': [1, 2, 3],
        'ColB': ['x', 'y', 'z'],
    })
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine='openpyxl')
    buf.seek(0)
    return buf


def make_no_dates_excel():
    df = pd.DataFrame({
        'Advertiser': ['Electrolux'],
        'Brand': ['Electrolux'],
        'Start': [None],
        'End': [None],
        'Format': ['Banner'],
        'Platform': ['facebook&instagram'],
        'Impr': [8848433],
    })
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine='openpyxl')
    buf.seek(0)
    return buf


def make_shuffled_columns_excel():
    df = pd.DataFrame({
        'Impr': [5000000],
        'Platform': ['YouTube'],
        'Format': ['video'],
        'End': ['2023-06-30'],
        'Start': ['2023-06-01'],
        'Brand': ['BrandX'],
        'Advertiser': ['AdvX'],
    })
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine='openpyxl')
    buf.seek(0)
    return buf


def test_normalize_columns():
    df = pd.DataFrame(columns=['Advertiser', ' Brand ', 'START', 'End', 'Format', 'Platform', 'Impr'])
    df = normalize_columns(df)
    assert 'advertiser' in df.columns
    assert 'brand' in df.columns
    assert 'start' in df.columns
    assert 'impr' in df.columns


def test_validate_valid_dataframe():
    df = pd.DataFrame({
        'advertiser': ['A'],
        'brand': ['B'],
        'start': ['2021-01-01'],
        'end': ['2021-01-31'],
        'format': ['banner'],
        'platform': ['DV360'],
        'impr': [1000],
    })
    valid, error = validate_dataframe(df)
    assert valid is True
    assert error == ''


def test_validate_completely_wrong_columns():
    df = pd.DataFrame({'col1': [1], 'col2': [2], 'col3': ['x']})
    df.columns = [c.lower() for c in df.columns]
    valid, error = validate_dataframe(df)
    assert valid is False
    assert 'невідповідність' in error.lower()


def test_validate_missing_dates():
    df = pd.DataFrame({
        'advertiser': ['Test'],
        'brand': ['B'],
        'start': [None],
        'end': [None],
        'format': ['banner'],
        'platform': ['DV360'],
        'impr': [1000],
    })
    valid, error = validate_dataframe(df)
    assert valid is False
    assert 'дат' in error.lower()


def test_validate_partial_columns():
    df = pd.DataFrame({
        'advertiser': ['Test'],
        'brand': ['B'],
    })
    valid, error = validate_dataframe(df)
    assert valid is False
    assert 'колонки' in error.lower()


def test_parse_valid_dataframe():
    df = pd.DataFrame({
        'Advertiser': ['TestAdv'],
        'Brand': ['BrandA'],
        'Start': ['2021-01-04'],
        'End': ['2021-01-10'],
        'Format': ['banner'],
        'Platform': ['DV360'],
        'Impr': [1000000],
    })
    records, error = parse_dataframe(df)
    assert error == ''
    assert records is not None
    assert len(records) == 1
    assert records[0]['year'] == 2021
    assert records[0]['impr'] == 1000000


def test_parse_shuffled_columns():
    df = pd.DataFrame({
        'Impr': [5000000],
        'Platform': ['YouTube'],
        'Format': ['video'],
        'End': ['2023-06-30'],
        'Start': ['2023-06-01'],
        'Brand': ['BrandX'],
        'Advertiser': ['AdvX'],
    })
    records, error = parse_dataframe(df)
    assert error == ''
    assert records is not None
    assert records[0]['year'] == 2023
    assert records[0]['platform'] == 'YouTube'


def test_parse_invalid_columns_returns_error():
    df = pd.DataFrame({'col1': [1], 'col2': [2]})
    records, error = parse_dataframe(df)
    assert records is None
    assert error != ''


def test_read_file_unsupported_format():
    buf = io.BytesIO(b'some data')
    df, error = read_file(buf, 'file.pdf')
    assert df is None
    assert 'формат' in error.lower()


@pytest.mark.django_db
def test_upload_page_requires_login(client):
    response = client.get(reverse('upload'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_upload_page_loads_for_user(client, regular_user):
    client.login(username='regularuser', password='user123!')
    response = client.get(reverse('upload'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_upload_valid_file_creates_records(client, regular_user):
    client.login(username='regularuser', password='user123!')
    buf = make_valid_excel()
    f = SimpleUploadedFile('data.xlsx', buf.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response = client.post(reverse('upload'), {'file': f})
    assert response.status_code == 302
    assert DataRecord.objects.count() == 2
    assert FileUploadLog.objects.filter(status='success').count() == 1


@pytest.mark.django_db
def test_upload_invalid_file_creates_error_log(client, regular_user):
    client.login(username='regularuser', password='user123!')
    buf = make_invalid_excel()
    f = SimpleUploadedFile('bad.xlsx', buf.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response = client.post(reverse('upload'), {'file': f})
    assert response.status_code == 200
    assert FileUploadLog.objects.filter(status='error').count() == 1
    assert DataRecord.objects.count() == 0


@pytest.mark.django_db
def test_upload_test_file_no_dates_creates_error_log(client, regular_user):
    client.login(username='regularuser', password='user123!')
    buf = make_no_dates_excel()
    f = SimpleUploadedFile('Task. Fact data_test.xlsx', buf.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response = client.post(reverse('upload'), {'file': f})
    assert response.status_code == 200
    assert FileUploadLog.objects.filter(status='error').count() == 1
    assert 'дат' in FileUploadLog.objects.first().error_type.lower()


@pytest.mark.django_db
def test_upload_shuffled_columns_success(client, regular_user):
    client.login(username='regularuser', password='user123!')
    buf = make_shuffled_columns_excel()
    f = SimpleUploadedFile('shuffled.xlsx', buf.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response = client.post(reverse('upload'), {'file': f})
    assert response.status_code == 302
    assert DataRecord.objects.filter(year=2023).count() == 1
