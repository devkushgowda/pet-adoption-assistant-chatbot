import psycopg2
import time

from nlp.chat import get_response

conn = psycopg2.connect(database="detonators",
                        host="localhost",
                        user="postgres",
                        password="0000",
                        port="5432")

commands = {'get-breed-info': "select * from breed where breed_id='{0}'",
            'get-all-country-names': "select name from country ORDER by name",
            'get-all-breed-names': "select name from breed ORDER by name",
            'get-owner-by-email': "select o.full_name, o.mobile, a.address, a.city,a.zip_code,c.name from owner o, "
                                  "address a, country c where email_id ilike '{0}' and o.address_id=a.address_id and "
                                  "c.country_id=a.country_id",
            'get-available-count-in': "select count(d.dog_id) from dog d, address ad, country c where "
                                      "d.address_id=ad.address_id and ad.country_id=c.country_id and c.name='{"
                                      "0}' and d.dog_id not in (select dog_id from adoption)",
            }


def execute_command(command_str):
    command_parts = command_str.split(':')
    command = get_response(command_parts[0].strip())
    if command is None:
        command = 'help'
    cursor = conn.cursor()
    match command:
        case 'help':
            return 'Hello, I can help with the following,' \
                   '1. Get all the different countries. \n ' \
                   '2. Get all the available breed IDs. \n ' \
                   '3. Get breed information and profile URL of the given breed name.\n' \
                   '4. Get the owner info based on the email.' \
                   '5. Get the total number of dogs available in the given ' \
                   'country name.\n' \
                   '6. Ask for help to list all available commands.'
        case 'get-breed-info':
            if len(command_parts) != 2:
                return "Invalid command usage, do not forget to mention ':[Breed Name]' at the end of the query."
            command_args = command_parts[1].strip()
            query = commands[command].format(command_args)
            cursor.execute(query)
            record = cursor.fetchone()
            if record is None:
                return f"Breed with id '{command_args}' not found in records."
            else:
                return record[2] + '\n\n' + record[3]
        case 'get-available-count-in':
            if len(command_parts) != 2:
                return "Invalid command usage, do not forget to mention ':[Country Name]' at the end of the query."

            command_args = command_parts[1].strip()
            query = commands[command].format(command_args)
            cursor.execute(query)
            record = cursor.fetchone()
            if record is None:
                return f"Breed with id '{command_args}' not found in records."
            else:
                return f'As of {time.strftime("%m/%d/%Y, %H:%M:%S")}, total {record[0]} dogs are available for ' \
                       f'adoption in {command_args}. '
        case 'get-owner-by-email':
            if len(command_parts) != 2:
                return "Invalid command usage, do not forget to mention ':[Email ID]' at the end of the query."

            command_args = command_parts[1].strip()
            query = commands[command].format(command_args)
            cursor.execute(query)
            record = cursor.fetchone()
            if record is None:
                return f"Owner with email '{command_args}' not found in records."
            else:
                # o.full_name, o.mobile, a.address, a.city,a.zip_code,c.name
                return f'You are looking for {record[0]}.\n Mobile: {record[1]}, Address: {record[2]}, ' \
                       f'{record[3]}, {record[4]}, {record[5]}'
        case 'get-all-breed-names':
            query = commands[command]
            cursor.execute(query)
            return ', '.join([row[0] for row in cursor.fetchall()])
        case 'get-all-country-names':
            query = commands[command]
            cursor.execute(query)
            return ', '.join([row[0] for row in cursor.fetchall()])
    cursor.close()
    return "Invalid command, To know available commands type 'help'!"
