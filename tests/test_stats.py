import pytest
import io
import pandas as pd
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from uploads.models import DataRecord, FileUploadLog


def upload_test_data(client, regular_user):
    client.login(username='regularuser', password='user123!')
    df = pd.DataFrame({
        'Advertiser': ['AdvA', 'AdvA', 'AdvB'],
        'Brand': ['BrandA', 'BrandA', 'BrandB'],
        'Start': ['2021-01-01', '2022-03-01', '2021-06-01'],
        'End': ['2021-01-31', '2022-03-31', '2021-06-30'],
        'Format': ['banner', 'video', 'banner'],
        'Platform': ['DV360', 'YouTube', 'DV360'],
        'Impr': [1000000, 2000000, 500000],
    })
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine='openpyxl')
    buf.seek(0)
    f = SimpleUploadedFile('stats_test.xlsx', buf.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    client.post(reverse('upload'), {'file': f})


@pytest.mark.django_db
def test_stats_page_requires_login(client):
    response = client.get(reverse('stats'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_stats_page_loads_empty(client, regular_user):
    client.login(username='regularuser', password='user123!')
    response = client.get(reverse('stats'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_stats_shows_aggregated_data(client, regular_user):
    upload_test_data(client, regular_user)
    response = client.get(reverse('stats'))
    assert response.status_code == 200
    stats = list(response.context['stats'])
    years = [s['year'] for s in stats]
    assert 2021 in years
    assert 2022 in years


@pytest.mark.django_db
def test_stats_correct_impr_sum_for_2021(client, regular_user):
    upload_test_data(client, regular_user)
    response = client.get(reverse('stats'))
    stats = {s['year']: s['total_impr'] for s in response.context['stats']}
    assert stats[2021] == 1500000


@pytest.mark.django_db
def test_stats_correct_impr_sum_for_2022(client, regular_user):
    upload_test_data(client, regular_user)
    response = client.get(reverse('stats'))
    stats = {s['year']: s['total_impr'] for s in response.context['stats']}
    assert stats[2022] == 2000000


@pytest.mark.django_db
def test_admin_file_logs_view(client, admin_user, regular_user):
    client.login(username='regularuser', password='user123!')
    upload_test_data(client, regular_user)
    client.login(username='adminuser', password='admin123!')
    response = client.get(reverse('file_logs'))
    assert response.status_code == 200
    assert len(response.context['logs']) >= 1


@pytest.mark.django_db
def test_admin_access_status_view(client, admin_user, regular_user):
    client.login(username='adminuser', password='admin123!')
    response = client.get(reverse('access_status'))
    assert response.status_code == 200
    emails = [p.user.email for p in response.context['profiles']]
    assert 'admin@test.com' in emails
    assert 'user@test.com' in emails


@pytest.mark.django_db
def test_admin_full_data_view(client, admin_user, regular_user):
    upload_test_data(client, regular_user)
    client.login(username='adminuser', password='admin123!')
    response = client.get(reverse('full_data'))
    assert response.status_code == 200
    assert response.context['records'].count() == 3


@pytest.mark.django_db
def test_data_record_year_extraction(client, regular_user):
    upload_test_data(client, regular_user)
    records_2021 = DataRecord.objects.filter(year=2021)
    records_2022 = DataRecord.objects.filter(year=2022)
    assert records_2021.count() == 2
    assert records_2022.count() == 1
