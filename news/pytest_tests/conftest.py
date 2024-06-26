import pytest
from django.test.client import Client
from news.models import Comment, News
from datetime import datetime, timedelta
from django.conf import settings
from django.urls import reverse


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Новость',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
    )
    return comment


@pytest.fixture
def comment_form_data(news, author):
    return {
        'news': news,
        'text': 'Новый текст',
        'author': author
    }


@pytest.fixture
def news_creator():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment_creator(news, author):
    for index in range(10):
        Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=[comment.id])


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', args=[comment.id])


@pytest.fixture
def url_to_comment(detail_url):
    url = detail_url + '#comments'
    return url
