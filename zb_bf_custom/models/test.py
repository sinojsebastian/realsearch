class con_test:
    def __init__(self,server_ip,server_port,dbname,username,pwd):
        print('http://'+server_ip+':'+server_port+'/xmlrpc/object')
        sock_common = xmlrpclib.ServerProxy ('http://'+server_ip+':'+server_port+'/xmlrpc/common')
        self.uid = sock_common.login(dbname, username, pwd)
        print('oooooooooooooo',self.uid)
        self.dbname=dbname
        self.pwd=pwd
        self.sock= xmlrpclib.ServerProxy('http://'+server_ip+':'+server_port+'/xmlrpc/object')
        
    def do_read(self):
        service_bill = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'raw.services', 'search', [[('from_date','=','16/01/2022'),('to_date','=','15/02/2022'),('product_id','=',5)]])
        print('kkkkkkkkkkkkkkkkkkkkkkkkkkk',len(service_bill))
        inv_ids = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'account.move', 'search', [[('raw_service_id','in',service_bill)]])
        print('====================inv_id',len(inv_ids))
        for invoice in inv_ids:
            inv_obj = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'account.move', 'read', [invoice])
            print('====================inv_obj',inv_obj)

def main():
    
        server_ip = '192.168.1.7'
        server_port = '8069'
        database = 'rs_feb16'
        username = 'admin'
        password = 'admin'
        ip = con_test(server_ip, server_port, database, username, password)
        ip.do_read()

if __name__ == "__main__":
    main()