from http import HTTPStatus
from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name ,args',
    (
        ('news:detail', pytest.lazy_fixture('news')),
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_availability(client, name, args):
    if name == 'news:detail':
        args = (args.id,)
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'name',
    (
        ('news:edit'),
        ('news:delete'),
    ),
)
def test_comment_edit_delete(
        parametrized_client,
        expected_status,
        name,
        comment):
    url = reverse(name, args=[comment.id])
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (
        ('news:edit'),
        ('news:delete'),
    ),
)
def test_anon_redirects(client, name, comment):
    login_url = reverse('users:login')
    url = reverse(name, args=[comment.id])
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
