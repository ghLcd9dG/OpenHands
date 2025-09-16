import pytest

from openhands.integrations import azure_openai


def test_format_prompt_with_string():
    messages = azure_openai._format_prompt('hello', 'system')
    assert messages == [
        {'role': 'system', 'content': 'system'},
        {'role': 'user', 'content': 'hello'},
    ]


def test_format_prompt_list_preserves_existing_system():
    messages = azure_openai._format_prompt(
        [{'role': 'system', 'content': 'keep'}, {'role': 'user', 'content': 'value'}],
        'ignored',
    )
    assert messages[0]['content'] == 'keep'


def test_call_azure_chat_routes_to_gpt4o(monkeypatch):
    captured = {}

    def fake_call(messages):
        captured['messages'] = messages
        return ['response']

    monkeypatch.setattr(azure_openai, '_call_gpt4o', fake_call)
    monkeypatch.setattr(azure_openai, '_call_o3mini', lambda _: pytest.fail('wrong model'))

    result = azure_openai.call_azure_chat('hi', system_prompt='sys', model='gpt-4o')

    assert result == ['response']
    assert captured['messages'][0]['role'] == 'system'


def test_call_azure_chat_routes_to_o3(monkeypatch):
    captured = {}

    def fake_call(messages):
        captured['messages'] = messages
        return ['response']

    monkeypatch.setattr(azure_openai, '_call_o3mini', fake_call)
    monkeypatch.setattr(azure_openai, '_call_gpt4o', lambda _: pytest.fail('wrong model'))

    result = azure_openai.call_azure_chat('hello', model='o3-mini')

    assert result == ['response']
    assert captured['messages'][0]['role'] == 'user'


def test_call_azure_chat_invalid_model():
    with pytest.raises(ValueError):
        azure_openai.call_azure_chat('prompt', model='unsupported')
