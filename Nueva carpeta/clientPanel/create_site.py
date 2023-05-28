#! /usr/bin/python3
import os
import pwd
import cgi
import db_conn


def exists_username(username) -> bool:
    try:
        pwd.getpwnam(username)
        return True
    except:
        return False
    
def response_error(status: int, msg: str) -> None:
    print('Content-Type: text/html')
    print(f'Status: {status}\n\n')
    print('<html>')
    print('<head>')
    print(f'<meta http-equiv="refresh" content="3;url=/" />') 
    print('</head>')
    print('<body>')
    print(f'<p>{msg}. Return <a href="/">home</a></p>')
    print('</body>')
    print('</html>')
    
def del_user(username:str):
    os.system(f'userdel -r {username}')
    if os.path.exists(f'/home/{username}'):
        os.system(f'rm -r /home/{username}')
    vhost_path = f'rm /etc/apache2/vhosts.d/{username}.conf'
    if os.path.exists(vhost_path):
        os.system(f'rm {vhost_path}')
    
def create_user(username:str, password:str):
    try:
        os.system(f'useradd -p "{password}" -m -d /home/{username} {username}')
        os.system(f'mkdir /home/{username}/web')
        with open('index_example.html', 'r') as template:
            site = template.read()
            site = site.replace('{username}', username)
        with open(f'/home/{username}/web/index.html', 'w') as template:
            template.write(site)
    except Exception as error:
        response_error(403, 'No se pudo crear el usuario')
        print(error)
        del_user(username)
        raise error

def configure_domain(username:str, domain:str):
    with open('vhost_template.conf', 'r') as conf_file:
        conf = conf_file.read()
        conf = conf.replace('{username}', username)
        conf = conf.replace('{domain}', domain)
    with open(f'{username}.conf', 'w') as conf_file:
        conf_file.write(conf)
    os.system(f'mv {username}.conf /etc/apache2/vhosts.d/')

def create_db(username:str, password:str, db_name:str):
    try:
        db_conn.create_database(username, password, db_name)
    except Exception as error:
        response_error(500, "Algo salio mal")
        print(error)
        del_user(username)
        raise error

def main():
    form = cgi.FieldStorage()

    username = form.getvalue('username')
    password = form.getvalue('password')
    domain_name = form.getvalue('domain_name')
    database_name = form.getvalue('database_name')

    if db_conn.exists_username(username) or exists_username(username):
        response_error(409, 'username no disponible')
        return
    if db_conn.exists_domain(domain_name):
        response_error(409, 'dominio no disponible')
        return
    if db_conn.exists_db_name(database_name):
        response_error(409, 'nombre de DB no disponible')
        return
        
    create_user(username, password)
    configure_domain(username, domain_name)
    create_db(username, password, database_name)
    
    db_conn.save_site(username, password, domain_name, database_name)
    os.system('apache2ctl graceful')
    

    print('Content-Type: text/html')
    print(f'Status: 302\n\n')
    print('<html>')
    print('<head>')
    print(f'<meta http-equiv="refresh" content="3;url=/" />') 
    print('</head>')
    print('<body>')
    print(f'<p>sitio web creado exitosamente. Redireccionando ...</p>')
    print('</body>')
    print('</html>')



if __name__ == '__main__':
    try:
        os.setuid(0)
        os.setgid(0)
    except Exception as error:
        print(error)
    main()