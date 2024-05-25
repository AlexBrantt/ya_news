from http import HTTPStatus
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertRedirects, assertFormError
import pytest


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client,
                                            detail_url,
                                            comment_form_data):
    client.post(detail_url, data=comment_form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(author_client, detail_url, comment_form_data):
    comments_start_count = Comment.objects.count()
    response = author_client.post(detail_url, data=comment_form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == comments_start_count + 1
    comment = Comment.objects.get()
    assert comment.text == comment_form_data['text']
    assert comment.news == comment_form_data['news']
    assert comment.author == comment_form_data['author']


def test_user_cant_use_bad_words(author_client, detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client,
                                   comment_delete_url,
                                   detail_url):
    url_to_comments = detail_url + '#comments'
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  comment_delete_url):
    response = not_author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client,
                                 comment_edit_url,
                                 url_to_comment,
                                 comment,
                                 comment_form_data):

    response = author_client.post(comment_edit_url, data=comment_form_data)
    assertRedirects(response, url_to_comment)
    comment.refresh_from_db()
    assert comment.text == comment_form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(not_author_client,
                                                comment_edit_url,
                                                comment_form_data,
                                                comment):
    response = not_author_client.post(comment_edit_url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
