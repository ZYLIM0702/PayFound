import os, tempfile
os.environ['PAYFOUND_TESTING']='1'
os.environ['ENABLE_REMOTE_AI']='false'
os.environ.pop('CHANNEL3_API_KEY',None)
# Configure isolated database before app and SQLAlchemy engine import.
test_database = os.getenv('PAYFOUND_TEST_DATABASE_URL')
if test_database:
    from urllib.parse import urlparse
    parsed = urlparse(test_database)
    if parsed.hostname not in {'localhost', '127.0.0.1', '::1'} or parsed.path != '/payfound_test':
        raise RuntimeError('Destructive regression tests require a localhost database named payfound_test')
    os.environ['DATABASE_URL'] = test_database
else:
    fd,path=tempfile.mkstemp(prefix='payfound-tests-',suffix='.db')
    os.close(fd)
    os.environ['DATABASE_URL']='sqlite:///'+path
os.environ['DEMO_MODE']='true'
os.environ['PAYPAL_ENV']='sandbox'
os.environ.pop('PAYPAL_CLIENT_ID',None)
os.environ.pop('PAYPAL_CLIENT_SECRET',None)
import pytest
from fastapi.testclient import TestClient
from app.database import Base, engine
from app.main import app,seed_demo

@pytest.fixture()
def client():
    Base.metadata.drop_all(engine);Base.metadata.create_all(engine);seed_demo()
    with TestClient(app) as c:yield c

@pytest.fixture()
def consumer():return {'x-demo-role':'consumer'}
@pytest.fixture()
def merchant():return {'x-demo-role':'merchant'}
@pytest.fixture()
def admin():return {'x-demo-role':'admin'}
