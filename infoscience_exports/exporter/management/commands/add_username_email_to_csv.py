import csv
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Add username to csv list"

    def add_arguments(self, parser):
        parser.add_argument('--jahia_csv_path', nargs='+', type=str)
        parser.add_argument('--people_csv_path', nargs='+', type=str)

    def handle(self, *args, **options):
        try:
            from epflldap.ldap_search import get_username, get_email, \
                EpflLdapException
        except ImportError:
            self.stdout.write("Please install epfl-ldap modules to run this command")
            return

        if options.get('people_csv_path') and options['people_csv_path'][0]:
            self.stdout.write("Doing People...")
            with open(options['people_csv_path'][0], 'r') as csvinput:
                with open("{}.extended.csv".format(options['people_csv_path'][0]), 'w') as csvoutput:
                    writer = csv.writer(csvoutput, lineterminator='\n')
                    reader = csv.reader(csvinput)

                    header = next(reader)
                    # do header
                    header.append('email')
                    writer.writerow(header)

                    for row in reader:
                        email = ''
                        sciper = row[0]
                        if sciper:
                            try:
                                email = get_email(sciper)
                            except EpflLdapException:
                                # No email ? not a problem, it is not mandatory
                                pass

                        row.append(email)
                        writer.writerow(row)

        if options.get('jahia_csv_path') and options['jahia_csv_path'][0]:
            self.stdout.write("Doing Jahia...")
            with open(options['jahia_csv_path'][0], 'r') as csvinput:
                with open("{}.extended.csv".format(options['jahia_csv_path'][0]), 'w') as csvoutput:
                    writer = csv.writer(csvoutput, lineterminator='\n')
                    reader = csv.reader(csvinput)
                    header = list(next(reader))

                    # do header
                    header.extend(('username', 'email'))
                    writer.writerow(header)

                    for row in reader:
                        username = ''
                        email = ''
                        sciper = row[5]
                        if sciper:
                            try:
                                username = get_username(sciper)

                                if username and '@' in username:
                                    username = username[:username.rfind('@')]

                                email = get_email(sciper)
                            except EpflLdapException:
                                # no username or no email ? not a problem, it is not mandatory
                                pass

                        row.append(username)
                        row.append(email)
                        writer.writerow(row)
