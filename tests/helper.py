import aiohttp
import asyncio
from contextlib import contextmanager

from parser import connection as conn_mod
from parser import tasks as tasks_module


class SQLModelBase:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        return None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def field(*args, **kwargs):
    return None


def create_engine(arg, echo=False):
    return object()


class SessionStub:
    def __init__(self, engine): pass

    def close(self): pass


class BeautifulSoupStub:
    def __init__(self, html, parser):
        self._html = html
        self.title = None
        self._parse_title_and_meta()

    def _parse_title_and_meta(self):
        import re
        m = re.search(r"<title>(.*?)</title>", self._html, re.IGNORECASE | re.S)
        if m:
            class T:
                def __init__(self, s): self.string = s

            self.title = T(m.group(1))
        else:
            self.title = None
        m = re.search(r"<meta\s+name=['\"]description['\"]\s+content=['\"](.*?)['\"]\s*/?>", self._html, re.IGNORECASE | re.S)
        self._meta_content = m.group(1) if m else None

    def find(self, name, attrs=None):
        if name == "meta" and attrs and attrs.get("name") == "description":
            if self._meta_content is None:
                return None

            class M:
                def __init__(self, c):
                    self._c = c

                def get(self, key):
                    if key == "content":
                        return self._c

                def __getitem__(self, key):
                    if key == 'content':
                        return self._c
                    raise KeyError(key)

            return M(self._meta_content)
        return None


class FakeRespCtx:
    def __init__(self, html):
        self._html = html

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def text(self):
        return self._html


class FakeClientSession:
    def __init__(self, html):
        self.html = html

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def get(self, url):
        return FakeRespCtx(self.html)


class FakeDBSession:
    def __init__(self):
        self.merged = []
        self.committed = False

    def merge(self, obj):
        self.merged.append(obj)
        return obj

    def commit(self):
        self.committed = True


@contextmanager
def fake_get_session():
    s = FakeDBSession()
    yield s


def run_parse_and_capture(html):
    original_cs = aiohttp.ClientSession
    original_get_session = conn_mod.get_session

    last = {}

    def capturing_get_session():
        s = FakeDBSession()
        last['session'] = s

        @contextmanager
        def cm():
            yield s

        return cm()

    aiohttp.ClientSession = lambda: FakeClientSession(html)
    conn_mod.get_session = capturing_get_session

    try:
        tasks_module.get_session = capturing_get_session
    except Exception:
        pass

    try:
        asyncio.run(tasks_module.parse("http://example.test"))
        return last.get('session')
    finally:
        aiohttp.ClientSession = original_cs
        conn_mod.get_session = original_get_session
