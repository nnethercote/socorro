from socorro.cron.crontabber import PostgresBackfillCronApp


class NightlyBuildsCronApp(PostgresBackfillCronApp):
    app_name = 'nightly-builds'
    app_version = '1.0'
    app_description = """Populate nightly_builds table.
    See https://bugzilla.mozilla.org/show_bug.cgi?id=751298
    """

    def run(self, connection, date):
        cursor = connection.cursor()
        cursor.callproc('update_nightly_builds', [date.date()])
