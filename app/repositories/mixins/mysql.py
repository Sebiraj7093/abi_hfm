from hf_mysql_client.client import HfMySqlAlchemyClient
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from configuration import DB_REPORTS_READ_HOST
from configuration import DB_REPORTS_READ_PORT
from configuration import DB_REPORTS_READ_PWD
from configuration import DB_REPORTS_READ_USER
from configuration import DB_REPORTS_WRITE_HOST
from configuration import DB_REPORTS_WRITE_PORT
from configuration import DB_REPORTS_WRITE_PWD
from configuration import DB_REPORTS_WRITE_USER
from utils.tracing import TracerMixin

_reports_cluster = HfMySqlAlchemyClient(
    host=DB_REPORTS_READ_HOST,
    port=DB_REPORTS_READ_PORT,
    read_user=DB_REPORTS_READ_USER,
    read_pwd=DB_REPORTS_READ_PWD,
    write_user=DB_REPORTS_WRITE_USER,
    write_pwd=DB_REPORTS_WRITE_PWD,
    write_host=DB_REPORTS_WRITE_HOST,
    write_port=DB_REPORTS_WRITE_PORT,
    pool_size=1,
)


class MySqlMixin(metaclass=TracerMixin):
    reports_cluster = _reports_cluster


SQLAlchemyInstrumentor().instrument(
    engines=[
        MySqlMixin.reports_cluster.read_engine,
        MySqlMixin.reports_cluster.write_engine,
    ]
)
