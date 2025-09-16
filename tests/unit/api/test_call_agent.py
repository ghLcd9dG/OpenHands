import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest


def _ensure_openhands_dependency_stubs() -> None:
    if 'openhands.core.config.utils' not in sys.modules:
        core_config_pkg = types.ModuleType('openhands.core.config')
        core_config_pkg.__path__ = []  # mark as package
        sys.modules['openhands.core.config'] = core_config_pkg

        utils_module = types.ModuleType('openhands.core.config.utils')

        def _not_configured(*_args, **_kwargs):  # pragma: no cover - stub
            raise NotImplementedError('load_openhands_config stub should be patched')

        utils_module.load_openhands_config = _not_configured
        sys.modules['openhands.core.config.utils'] = utils_module

    if 'openhands.core.main' not in sys.modules:
        main_module = types.ModuleType('openhands.core.main')

        def _auto_continue_response(*_args, **_kwargs):
            return 'continue'

        async def _run_controller(**_kwargs):  # pragma: no cover - stub
            raise NotImplementedError('run_controller stub should be patched')

        main_module.auto_continue_response = _auto_continue_response
        main_module.run_controller = _run_controller
        sys.modules['openhands.core.main'] = main_module

    if 'openhands.core.schema' not in sys.modules:
        schema_module = types.ModuleType('openhands.core.schema')

        class AgentState:
            FINISHED = 'finished'

        schema_module.AgentState = AgentState
        sys.modules['openhands.core.schema'] = schema_module

    if 'openhands.core.setup' not in sys.modules:
        setup_module = types.ModuleType('openhands.core.setup')
        setup_module.generate_sid = lambda _config: 'sid-stub'
        sys.modules['openhands.core.setup'] = setup_module

    if 'openhands.controller.state.state' not in sys.modules:
        state_module = types.ModuleType('openhands.controller.state.state')

        class State:
            def __init__(self):
                self.history = []
                self.agent_state = None

        state_module.State = State
        sys.modules['openhands.controller.state.state'] = state_module

    if 'openhands.events.action' not in sys.modules:
        action_module = types.ModuleType('openhands.events.action')

        class MessageAction:
            def __init__(self, content: str):
                self.content = content

        class FileEditAction:
            def __init__(self, path: str):
                self.path = path

        class FileWriteAction:
            def __init__(self, path: str, content: str = ''):
                self.path = path
                self.content = content

        action_module.MessageAction = MessageAction
        action_module.FileEditAction = FileEditAction
        action_module.FileWriteAction = FileWriteAction
        sys.modules['openhands.events.action'] = action_module


def _ensure_litellm_stub() -> None:
    if 'litellm' in sys.modules:
        return

    fake_module = types.ModuleType('litellm')
    fake_module.suppress_debug_info = True
    fake_module.set_verbose = False

    def _not_implemented(*args, **kwargs):  # pragma: no cover - stub
        raise NotImplementedError('litellm stub called')

    fake_module.completion = _not_implemented
    fake_module.completion_cost = _not_implemented
    fake_module.acompletion = _not_implemented
    fake_module.ChatCompletionToolParam = type('ChatCompletionToolParam', (), {})
    fake_module.ChatCompletionToolParamFunctionChunk = type(
        'ChatCompletionToolParamFunctionChunk', (), {}
    )
    fake_module.ChatCompletionMessageToolCall = type(
        'ChatCompletionMessageToolCall', (), {}
    )
    fake_module.ModelResponse = type('ModelResponse', (), {})
    fake_module.ModelInfo = type('ModelInfo', (), {})
    fake_module.PromptTokensDetails = type('PromptTokensDetails', (), {})
    fake_module.BaseModel = type('BaseModel', (), {})

    def _supports_response_schema(*args, **kwargs):  # pragma: no cover - stub
        return False

    fake_module.supports_response_schema = _supports_response_schema

    exceptions_module = types.ModuleType('litellm.exceptions')
    for name in [
        'APIConnectionError',
        'APIError',
        'AuthenticationError',
        'BadRequestError',
        'ContentPolicyViolationError',
        'ContextWindowExceededError',
        'InternalServerError',
        'NotFoundError',
        'OpenAIError',
        'RateLimitError',
        'ServiceUnavailableError',
        'Timeout',
    ]:
        setattr(exceptions_module, name, type(name, (Exception,), {}))

    types_utils_module = types.ModuleType('litellm.types.utils')
    types_utils_module.ModelResponse = fake_module.ModelResponse
    types_utils_module.CostPerToken = type('CostPerToken', (), {})
    types_utils_module.Usage = type('Usage', (), {})

    utils_module = types.ModuleType('litellm.utils')
    utils_module.create_pretrained_tokenizer = _not_implemented

    fake_module.exceptions = exceptions_module

    sys.modules['litellm'] = fake_module
    sys.modules['litellm.exceptions'] = exceptions_module
    sys.modules['litellm.types'] = types.ModuleType('litellm.types')
    sys.modules['litellm.types.utils'] = types_utils_module
    sys.modules['litellm.utils'] = utils_module


def _ensure_core_exceptions_stub() -> None:
    if 'openhands.core.exceptions' in sys.modules:
        return

    module = types.ModuleType('openhands.core.exceptions')

    class AgentError(Exception):
        pass

    module.AgentError = AgentError
    module.AgentNoInstructionError = type('AgentNoInstructionError', (AgentError,), {})
    module.AgentEventTypeError = type('AgentEventTypeError', (AgentError,), {})
    module.AgentAlreadyRegisteredError = type(
        'AgentAlreadyRegisteredError', (AgentError,), {}
    )
    module.AgentNotRegisteredError = type('AgentNotRegisteredError', (AgentError,), {})
    module.AgentStuckInLoopError = type('AgentStuckInLoopError', (AgentError,), {})
    module.TaskInvalidStateError = type('TaskInvalidStateError', (Exception,), {})
    module.LLMMalformedActionError = type('LLMMalformedActionError', (Exception,), {})
    module.LLMNoActionError = type('LLMNoActionError', (Exception,), {})
    module.LLMResponseError = type('LLMResponseError', (Exception,), {})
    module.LLMNoResponseError = type('LLMNoResponseError', (Exception,), {})
    module.UserCancelledError = type('UserCancelledError', (Exception,), {})
    module.OperationCancelled = type('OperationCancelled', (Exception,), {})
    module.LLMContextWindowExceedError = type(
        'LLMContextWindowExceedError', (RuntimeError,), {}
    )
    module.FunctionCallConversionError = type(
        'FunctionCallConversionError', (Exception,), {}
    )
    module.FunctionCallValidationError = type(
        'FunctionCallValidationError', (Exception,), {}
    )
    module.FunctionCallNotExistsError = type(
        'FunctionCallNotExistsError', (Exception,), {}
    )
    module.AgentRuntimeError = type('AgentRuntimeError', (Exception,), {})
    module.AgentRuntimeBuildError = type(
        'AgentRuntimeBuildError', (module.AgentRuntimeError,), {}
    )
    module.AgentRuntimeTimeoutError = type(
        'AgentRuntimeTimeoutError', (module.AgentRuntimeError,), {}
    )
    module.AgentRuntimeUnavailableError = type(
        'AgentRuntimeUnavailableError', (module.AgentRuntimeError,), {}
    )
    module.AgentRuntimeNotReadyError = type(
        'AgentRuntimeNotReadyError', (module.AgentRuntimeUnavailableError,), {}
    )
    module.AgentRuntimeDisconnectedError = type(
        'AgentRuntimeDisconnectedError', (module.AgentRuntimeUnavailableError,), {}
    )
    module.AgentRuntimeNotFoundError = type(
        'AgentRuntimeNotFoundError', (module.AgentRuntimeUnavailableError,), {}
    )
    module.BrowserInitException = type('BrowserInitException', (Exception,), {})
    module.BrowserUnavailableException = type(
        'BrowserUnavailableException', (Exception,), {}
    )
    module.MicroagentError = type('MicroagentError', (Exception,), {})
    module.MicroagentValidationError = type(
        'MicroagentValidationError', (module.MicroagentError,), {}
    )

    sys.modules['openhands.core.exceptions'] = module


def _ensure_pythonjsonlogger_stub() -> None:
    if 'pythonjsonlogger.json' in sys.modules:
        return

    base_module = types.ModuleType('pythonjsonlogger')
    json_module = types.ModuleType('pythonjsonlogger.json')

    class JsonFormatter:  # pragma: no cover - stub
        def __init__(self, *args, **kwargs):
            pass

        def format(self, record):
            return str(record.getMessage()) if hasattr(record, 'getMessage') else ''

    json_module.JsonFormatter = JsonFormatter
    base_module.json = json_module

    sys.modules['pythonjsonlogger'] = base_module
    sys.modules['pythonjsonlogger.json'] = json_module


def _ensure_termcolor_stub() -> None:
    if 'termcolor' in sys.modules:
        return

    module = types.ModuleType('termcolor')

    def colored(text, *args, **kwargs):  # pragma: no cover - stub
        return text

    module.colored = colored
    sys.modules['termcolor'] = module


def _ensure_logger_stub() -> None:
    if 'openhands.core.logger' in sys.modules:
        return

    import logging

    module = types.ModuleType('openhands.core.logger')
    module.LOG_ALL_EVENTS = False
    module.DEBUG = False
    module.LOG_DIR = '.'

    logger_obj = logging.getLogger('openhands-stub')
    logger_obj.addHandler(logging.NullHandler())

    module.openhands_logger = logger_obj

    def strip_ansi(text: str) -> str:  # pragma: no cover - stub
        return text

    module.strip_ansi = strip_ansi

    def get_console_handler():  # pragma: no cover - stub
        return logging.NullHandler()

    module.get_console_handler = get_console_handler

    sys.modules['openhands.core.logger'] = module


_ensure_openhands_dependency_stubs()
_ensure_litellm_stub()
_ensure_core_exceptions_stub()
_ensure_pythonjsonlogger_stub()
_ensure_termcolor_stub()
_ensure_logger_stub()

from importlib import import_module

from openhands.api import call_agent

State = import_module('openhands.controller.state.state').State
AgentState = import_module('openhands.core.schema').AgentState
FileWriteAction = import_module('openhands.events.action').FileWriteAction


class DummyConfig(SimpleNamespace):
    def __init__(self):
        super().__init__(
            runtime='docker',
            workspace_base=None,
            enable_browser=True,
            security=SimpleNamespace(confirmation_mode=True),
            jwt_secret='secret',
        )


@pytest.fixture(autouse=True)
def _patch_generate_sid(monkeypatch):
    monkeypatch.setattr('openhands.api.generate_sid', lambda config: 'sid-1234')


def _stub_state_with_history(test_path: str) -> State:
    state = State()
    state.history = [
        FileWriteAction(path=test_path, content="print('hello')\n"),
    ]
    state.agent_state = AgentState.FINISHED
    return state


def test_call_agent_collects_generated_tests(tmp_path, monkeypatch):
    repo = tmp_path / 'repo'
    repo.mkdir()

    config = DummyConfig()

    monkeypatch.setattr('openhands.api.load_openhands_config', lambda: config)

    async def fake_run_controller(**kwargs):
        workspace = Path(config.workspace_base)
        test_file = workspace / 'tests' / 'test_sample.py'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("print('hello')\n", encoding='utf-8')
        return _stub_state_with_history('tests/test_sample.py')

    monkeypatch.setattr('openhands.api.run_controller', fake_run_controller)

    tests = call_agent(str(repo), 'Write unit tests')

    assert tests == {'tests/test_sample.py': "print('hello')\n"}


def test_call_agent_returns_empty_when_no_tests(tmp_path, monkeypatch):
    repo = tmp_path / 'repo'
    repo.mkdir()

    config = DummyConfig()
    monkeypatch.setattr('openhands.api.load_openhands_config', lambda: config)

    async def fake_run_controller(**kwargs):
        state = State()
        state.agent_state = AgentState.FINISHED
        return state

    monkeypatch.setattr('openhands.api.run_controller', fake_run_controller)

    tests = call_agent(str(repo), 'No tests produced')

    assert tests == {}


def test_call_agent_missing_repo_raises():
    with pytest.raises(FileNotFoundError):
        call_agent('/path/that/does/not/exist', 'prompt')
