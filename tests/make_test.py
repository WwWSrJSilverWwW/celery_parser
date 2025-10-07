import sys
import types

import parser.main as main_module

from tests.helper import *


sys.modules.setdefault("celery_worker", types.SimpleNamespace(celery_app=types.SimpleNamespace(task=lambda f: f)))

sqlmodel_stub = types.SimpleNamespace()

sqlmodel_stub.SQLModel = SQLModelBase
sqlmodel_stub.Field = field
sqlmodel_stub.create_engine = create_engine
sqlmodel_stub.Session = SessionStub
sys.modules.setdefault("sqlmodel", sqlmodel_stub)

dotenv_stub = types.SimpleNamespace(load_dotenv=lambda: None)
sys.modules.setdefault("dotenv", dotenv_stub)

bs4_stub = types.SimpleNamespace(BeautifulSoup=BeautifulSoupStub)
sys.modules.setdefault("bs4", bs4_stub)


def test_parse_extracts_title_and_description():
    html = "<html><head><title>  Test Page  </title><meta name='description' content=' A nice description '/></head><body></body></html>"
    session = run_parse_and_capture(html)
    assert session is not None
    assert session.committed is True
    assert len(session.merged) == 1
    page = session.merged[0]
    assert hasattr(page, "name")
    assert page.name == "Test Page"
    assert page.description == "A nice description"


def test_parse_no_title_no_description():
    html = "<html><head></head><body>No title here</body></html>"
    session = run_parse_and_capture(html)
    assert session is not None
    assert session.committed is True
    page = session.merged[0]
    assert page.name == "No name"
    assert page.description == "No description"


def test_parse_meta_without_content():
    html = "<html><head><title>Title</title><meta name='description' content=''/></head></html>"
    session = run_parse_and_capture(html)
    page = session.merged[0]
    assert page.description == "No description"


def test_parse_strips_whitespace():
    html = "<html><head><title>   My Title   </title><meta name='description' content='   desc   '/></head></html>"
    session = run_parse_and_capture(html)
    page = session.merged[0]
    assert page.name == "My Title"
    assert page.description == "desc"


def test_main_parse_endpoint_calls_parse():
    called = {}
    tasks_module.parse_and_save_task = types.SimpleNamespace(apply_async=lambda *a, **k: called.update({'args': a, 'kwargs': k}))
    main_module.parse_and_save_task = tasks_module.parse_and_save_task
    result = asyncio.run(main_module.parse_endpoint("http://x"))
    assert result == {"message": "Task started"}
    assert 'args' in called
