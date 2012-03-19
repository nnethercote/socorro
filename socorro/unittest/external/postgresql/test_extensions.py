import datetime

from socorro.external.postgresql.extensions import Extensions
from socorro.lib import datetimeutil
import socorro.unittest.testlib.util as testutil

from .unittestbase import PostgreSQLTestCase


#------------------------------------------------------------------------------
def setup_module():
    testutil.nosePrintModule(__file__)


#==============================================================================
class IntegrationTestExtensions(PostgreSQLTestCase):
    """Test socorro.external.postgresql.extensions.Extensions class. """

    #--------------------------------------------------------------------------
    def setUp(self):
        """Set up this test class by populating the reports table with fake
        data. """
        super(IntegrationTestExtensions, self).setUp()

        cursor = self.connection.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE reports
            (
                id serial NOT NULL,
                date_processed timestamp with time zone,
                uuid character varying(50) NOT NULL
            );
            CREATE TABLE extensions
            (
                report_id integer not null,
                date_processed timestamp with time zone,
                extension_key integer not null,
                extension_id text not null,
                extension_version text
            );
        """)

        # Insert data
        now = datetimeutil.utc_now().date()
        uuid = "%%s-%s" % now.strftime("%y%m%d")

        cursor.execute("""
            INSERT INTO reports VALUES
            (
                1,
                '%s',
                '%s'
            ),
            (
                2,
                '%s',
                '%s'
            );
        """ % (now, uuid % "a1", now, uuid % "a2"))

        cursor.execute("""
            INSERT INTO extensions VALUES
            (
                1,
                '%s',
                10,
                'id1',
                'version1'
            ),
            (
                1,
                '%s',
                11,
                'id2',
                'version2'
            ),
            (
                1,
                '%s',
                12,
                'id3',
                'version3'
            );
        """ % (now, now, now))

        self.connection.commit()

    #--------------------------------------------------------------------------
    def tearDown(self):
        """Clean up the database, delete tables and functions. """
        cursor = self.connection.cursor()
        cursor.execute("""
            DROP TABLE extensions;
            DROP TABLE reports;
        """)
        self.connection.commit()
        super(IntegrationTestExtensions, self).tearDown()

    #--------------------------------------------------------------------------
    def test_get(self):
        extensions = Extensions(config=self.config)
        now = datetimeutil.utc_now()
        now = datetime.datetime(now.year, now.month, now.day,
                                tzinfo=now.tzinfo)
        uuid = "%%s-%s" % now.strftime("%y%m%d")
        now_str = datetimeutil.date_to_string(now)

        #......................................................................
        # Test 1: a valid crash with duplicates
        params = {
            "uuid": uuid % "a1",
            "date": now_str
        }
        res = extensions.get(**params)
        res_expected = {
            "hits": [
                {
                    "report_id": 1,
                    "date_processed": now_str,
                    "extension_key": 10,
                    "extension_id": 'id1',
                    "extension_version": 'version1'
                },
                {
                    "report_id": 1,
                    "date_processed": now_str,
                    "extension_key": 11,
                    "extension_id": 'id2',
                    "extension_version": 'version2'
                },
                {
                    "report_id": 1,
                    "date_processed": now_str,
                    "extension_key": 12,
                    "extension_id": 'id3',
                    "extension_version": 'version3'
                }
            ],
            "total": 3
        }

        self.assertEqual(res, res_expected)

        #......................................................................
        # Test 2: a crash without extensions
        params = {
            "uuid": uuid % "a2",
            "date": now_str
        }
        res = extensions.get(**params)
        res_expected = {
            "hits": [],
            "total": 0
        }

        self.assertEqual(res, res_expected)
