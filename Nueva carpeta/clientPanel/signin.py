#! /usr/bin/python3

import os
import cgi
import spwd
import crypt
import string

def verify_user(username: str, password: str) -> bool:
    username = username.translate(str.maketrans('', '', string.punctuation))
    password = password.translate(str.maketrans('', '', string.punctuation))
    if (username == '' or password == ''):
        return False
    try:
        encrypted_pass = spwd.getspnam(username).sp_pwdp
        return crypt.crypt(password, encrypted_pass) == encrypted_pass
    except Exception as error:
        print(error)
        return False
    
def main():

    form = cgi.FieldStorage()
    username = form.getvalue('username')
    password = form.getvalue('password')
    login = verify_user(username, password)
    
    if not login:
        return

    url = f"/?username={username}"
    
    print('Content-Type: text/html\n\n')

    print('<html>')
    print('<head>')
    print(f'<meta http-equiv="refresh" content="0;url={url}" />') 
    print('</head>')
    print('<body>')
    print("<p>Redirecting ...</p>")
    print('</body>')
    print('</html>')
    

if __name__ == '__main__':

    os.setgid(0)
    os.setuid(0)

    main()