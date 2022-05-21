
import csv
import xmlrpc.client as xmlrpclib
from datetime import datetime
import xlrd

class con_test:
	def __init__(self,server_ip,server_port,dbname,username,pwd):
		sock_common = xmlrpclib.ServerProxy ('http://'+server_ip+':'+server_port+'/xmlrpc/common')
		self.uid = sock_common.login(dbname, username, pwd)
		self.dbname=dbname
		self.pwd=pwd
		self.sock= xmlrpclib.ServerProxy('http://'+server_ip+':'+server_port+'/xmlrpc/object')

	def get_date(self,value,datemode):
		datevalue= False
		if value:
			datevalue = datetime(*xlrd.xldate_as_tuple(value, datemode))
			datevalue = datevalue.strftime("%Y-%m-%d")
		return datevalue

	def do_read(self):
		i=0
		# Give the location of the file
		loc = ("/home/davis/New Buildings/Hidd/Hidd - Owner Template (5 May).xlsx")
		 
		# To open Workbook
		wb = xlrd.open_workbook(loc)
		sheet = wb.sheet_by_index(0)
		for row_index in range(4, sheet.nrows):
			print (sheet.cell(row_index,5).value,row_index,'gggg>>>')
			if sheet.cell(row_index,1).value == '':
				break
			owner_name   = sheet.cell(row_index,5).value
			company_type = sheet.cell(row_index,7).value
			cpr_no       = sheet.cell(row_index,8).value
			passport_no= sheet.cell(row_index,9).value
			nationality= sheet.cell(row_index,10).value
			street = sheet.cell(row_index,11).value
			street2 = sheet.cell(row_index,12).value
			phone= sheet.cell(row_index,13).value
			mobile1= str(int(sheet.cell(row_index,14).value)) if isinstance(sheet.cell(row_index,14).value, int) else sheet.cell(row_index,14).value
			mobile2= str(int(sheet.cell(row_index,15).value)) if isinstance(sheet.cell(row_index,15).value, int) else sheet.cell(row_index,15).value
			email1= sheet.cell(row_index,16).value
			email2= sheet.cell(row_index,17).value
			bank_name= sheet.cell(row_index,18).value
			iban_no= sheet.cell(row_index,19).value
			acc_name= sheet.cell(row_index,20).value
			swift_code= sheet.cell(row_index,21).value
			# print (cpr_no),print(type(cpr_no))
			if type(cpr_no) != str:
			    cpr_no = repr(cpr_no).split(".")[0]
			# print (cpr_no),print(type(cpr_no))
			if type(passport_no) != str:
				passport_no = repr(passport_no).split(".")[0]
			if type(mobile1) != str:
				mobile1 = repr(mobile1).split(".")[0]
			if type(mobile2) != str:
				mobile2 = repr(mobile2).split(".")[0]
			if type(phone) != str:
				phone = repr(phone).split(".")[0]
			# print (type(passport_no),passport_no)
			if bank_name:
				bank_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'res.bank', 'search_read', [[['name', '=', bank_name]]],{'fields': ['name'],'limit': 1})
				if len(bank_rec) == 1:
					bank_name = bank_rec[0]['id']
				else:
					bank_name = self.sock.execute_kw(self.dbname, self.uid, self.pwd,'res.bank', 'create', [[{
									'name':bank_name,
									}]])
					bank_name = bank_name[0]
			if nationality:
				nationality_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'res.nationality', 'search_read', [[['name', '=', nationality]]],{'fields': ['name'],'limit': 1})
				if len(nationality_rec) == 1:
					nationality = nationality_rec[0]['id']
				else:
					nationality = self.sock.execute_kw(self.dbname, self.uid, self.pwd,'res.nationality', 'create', [[{
									'name':nationality,
									}]])
					nationality = nationality[0]
			if company_type == 'Individual':
				company_type = 'person'
			else:
				company_type = 'company'
			company_type = ''
			if mobile2:
				mobile1 = mobile1+', '+mobile2
			if email2:
				email1 = email1 +', '+email2
			owner_vals = {
				'name': owner_name,
				'company_type':company_type,
				'mobile':mobile1,
				'phone':phone,
				'email':email1,
				'cpr':cpr_no if company_type == 'person' else '',
				'cr':cpr_no if company_type == 'company' else '',
				'passport':passport_no,
				'owner':True,
				'street':street,
				'street2':street2,
				'nationality_id':nationality if nationality else False
			}
			print (owner_vals,'fff')
			partner_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'res.partner', 'search', [[['name', '=', owner_name]]],{'limit': 1})
			if len(partner_rec) == 1:
				print (partner_rec,'existing')
				self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'res.partner', 'write', [partner_rec, owner_vals])
				if iban_no:
					bank_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'res.partner.bank', 'search', [[['acc_number', '=', iban_no]]],{'limit': 1})
					bank_vals = {
						'acc_number':iban_no,
						'iban_no':iban_no,
						'bank_id':bank_name if bank_name else False,
						# 'account_no':service_details['account_no'],
						'acc_holder_name':acc_name,
						'partner_id':partner_rec[0]
					}
					if bank_rec:
						self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'res.partner.bank', 'write', [bank_rec, bank_vals])
					else:
						bank_records = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'res.partner.bank', 'create', [bank_vals])
					res = partner_rec[0]
					# print (bank_vals,'existingbbb')
			else:
				res = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'res.partner', 'create', [owner_vals])
				print (res,'newpart')
				if iban_no:
					bank_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'res.partner.bank', 'search', [[['acc_number', '=', iban_no]]],{'limit': 1})
					bank_vals = {
						'acc_number':iban_no,
						'iban_no':iban_no,
						'bank_id':bank_name if bank_name else False,
						# 'account_no':service_details['account_no'],
						'acc_holder_name':acc_name,
						'partner_id':res
					}
					if bank_rec:
						self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'res.partner.bank', 'write', [bank_rec, bank_vals])
					else:
						bank_records = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'res.partner.bank', 'create', [bank_vals])
					# print (bank_vals,'newbbb')
		print  ('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>done<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')

def main():
	server_ip = '82.194.55.89'
	server_port = '8001'
	database = 'Real_Search_UAT_Jan22_250621'
	username = 'admin'
	password = 'admin'
	ip = con_test(server_ip, server_port, database, username, password)
	ip.do_read()

if __name__ == "__main__":
	main()
