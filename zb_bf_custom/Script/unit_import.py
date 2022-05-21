
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
		loc = ("/home/davis/New Buildings/Water Bay/Water Bay_ Units Master_.xlsx")
		 
		# To open Workbook
		wb = xlrd.open_workbook(loc)
		sheet = wb.sheet_by_index(0)
		for row_index in range(3, sheet.nrows):
			print (sheet.cell(row_index,1).value,'>>>',row_index)
			if sheet.cell(row_index,1).value == '':
				break
			# print (sheet.cell(row_index,30).value,'management_fees')
			service_ids = []
			name = sheet.cell(row_index,1).value if isinstance(sheet.cell(row_index,1).value, str) else int(sheet.cell(row_index,1).value)
			type_val = sheet.cell(row_index,2).value if isinstance(sheet.cell(row_index,2).value, str) else int(sheet.cell(row_index,2).value)
			building_name = sheet.cell(row_index,3).value
			monthly_rent  = sheet.cell(row_index,4).value or 0.00
			deposit       = sheet.cell(row_index,5).value
			potential_rent= sheet.cell(row_index,6).value
			# flat_on_offer = sheet.cell(row_index,7).value
			offer_start_date= sheet.cell(row_index,8).value
			offer_end_date= sheet.cell(row_index,9).value
			feature       = sheet.cell(row_index,10).value
			feature_description= sheet.cell(row_index,11).value or False
			owner_id= sheet.cell(row_index,12).value or False
			no_of_bedrooms= sheet.cell(row_index,13).value
			unit_view_id = sheet.cell(row_index,15).value
			pool = sheet.cell(row_index,16).value
			balcony = sheet.cell(row_index,17).value
			gym = sheet.cell(row_index,18).value
			no_of_washrooms = sheet.cell(row_index,19).value
			floor_no= sheet.cell(row_index,20).value
			unit_area_as_per_final_contract= sheet.cell(row_index,21).value
			unit_area_as_per_title_deed= sheet.cell(row_index,22).value
			floor_area= sheet.cell(row_index,24).value
			service_charge= sheet.cell(row_index,25).value
			# tenant_id= sheet.cell(row_index,27).value or False
			state= sheet.cell(row_index,28).value 
			managed_by= sheet.cell(row_index,29).value
			management_fees= int(sheet.cell(row_index,30).value * 100) if sheet.cell(row_index,30).value else ''
			internet_line_no= sheet.cell(row_index,32).value if isinstance(sheet.cell(row_index,32).value, str) else int(sheet.cell(row_index,32).value)
			tabreed_unit_no= sheet.cell(row_index,33).value if isinstance(sheet.cell(row_index,33).value, str) else int(sheet.cell(row_index,33).value)
			ewa_no = sheet.cell(row_index,34).value if isinstance(sheet.cell(row_index,34).value, str) else int(sheet.cell(row_index,34).value)
			if sheet.cell(row_index,28).value == "" or sheet.cell(row_index,28).value == "empty" or sheet.cell(row_index,28).value == "Empty":
				state = 'new'
			else:
				state = 'available'
			
			if internet_line_no:
				# if isinstance(internet_line_no, str):
				# 	if internet_line_no.find('Owner') != -1 or internet_line_no.find('owner') != -1:
				# 		service_ids.append({
				# 			'product_id':5,
				# 			'package_name':'Internet',
				# 			'account_no':'',
				# 			'managed_by_rs':True,
				# 			'bill':'owner'
				# 		})
				# 	if internet_line_no.find('Tenant') != -1 or internet_line_no.find('tenant') != -1:
				# 		service_ids.append({
				# 			'product_id':5,
				# 			'package_name':'Internet',
				# 			'account_no':'',
				# 			'managed_by_rs':True,
				# 			'bill':'tenant'
				# 		})
				if isinstance(internet_line_no, int):
					service_ids.append({
						'product_id':5,
						'package_name':'Internet',
						'account_no':internet_line_no,
						# 'managed_by_rs':True,
					})
			if tabreed_unit_no:
				if isinstance(tabreed_unit_no, int):
					service_ids.append({
						'product_id':11,
						'package_name':'Tabreed',
						'account_no':tabreed_unit_no,
						# 'managed_by_rs':True,
					})
			if ewa_no:
				if isinstance(ewa_no, int):
					service_ids.append({
						'product_id':3,
						'package_name':'EWA',
						'account_no':ewa_no,
						# 'managed_by_rs':True,
					})
				# elif isinstance(ewa_no, str):
				# 	if ',' in ewa_no:
				# 		ewa_array = ewa_no.split(',')
				# 		for ewa_no1 in ewa_array:
				# 			service_ids.append({
				# 				'product_id':3,
				# 				'package_name':'EWA',
				# 				'managed_by_rs':False,
				# 				'account_no':ewa_no1,
				# 			})
							
				# else:
				# 	pass
				# 			else:
				# 				service_ids.append({
				# 					'product_id':3,
				# 					'package_name':'EWA',
				# 					'account_no':ewa_no,
				# 					'managed_by_rs':True,
				# 				})
				# if ewa_no == 'Trf' or ewa_no == 'TRF':
				# 	service_ids.append({
				# 		'product_id':3,
				# 		'package_name':'EWA',
				# 		'managed_by_rs':False,
				# 		'account_no':'',
				# 	})
				# else:
				# 	service_ids.append({
				# 		'product_id':3,
				# 		'package_name':'EWA',
				# 		'account_no':ewa_no,
				# 		'managed_by_rs':True,
				# 	})
			# print (service_ids,'service_ids')
			if type_val:
				type_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'zbbm.type', 'search', [[['name', '=', type_val]]],{'limit': 1})
				# print (type_rec,'tyyyyyy')
				if len(type_rec) == 1:
					type_val = type_rec[0]
				else:
					type_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd,'zbbm.type', 'create', [[{
									'name':type_val,
									}]])
					type_val = type_rec[0]
			if unit_view_id:
				unit_view_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'unit.view', 'search', [[['name', '=', unit_view_id]]],{'limit': 1})
				# print (type_rec,'tyyyyyy')
				if len(unit_view_rec) == 1:
					unit_view_id = unit_view_rec[0]
				else:
					unit_view_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd,'unit.view', 'create', [[{
									'name':unit_view_id,
					}]])
					unit_view_id = unit_view_rec[0]
			if building_name:
				building_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'zbbm.building', 'search', [[['name', '=', building_name]]],{'limit': 1})
				if len(building_rec) == 1:
					building_name = building_rec[0]
				else:
					building_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd,'zbbm.building', 'create', [[{
									'name':building_name,
									}]])
					building_name = building_rec[0]
			if owner_id:
				owner_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'res.partner', 'search', [[['name', '=', owner_id],['owner', '=', True]]],{'limit': 1})
				if len(owner_rec) == 1:
					owner_id = owner_rec[0]
				else:
					owner_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd,'res.partner', 'create', [[{
									'name':owner_id,
									'owner':True,
									}]])
					owner_id = owner_rec[0]
			# if tenant_id:
			# 	tenant_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'res.partner', 'search_read', [[['name', '=', tenant_id],['is_tenant', '=', True]]],{'fields': ['name'],'limit': 1})
			# 	if len(tenant_rec) == 1:
			# 		tenant_id = tenant_rec[0]['id']
			# 	else:
			# 		tenant_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd,'res.partner', 'create', [[{
			# 						'name':tenant_id,
			# 						'is_tenant':True,
			# 						}]])
			# 		tenant_id = tenant_rec[0]
			unit_vals = {
				'name': name,
				'type': type_val if type_val else False,
				'building_id':building_name,
				'monthly_rate':monthly_rent,
				'deposit':deposit,
				'potential_rent':potential_rent,
				# 'flat_on_offer':bool(flat_on_offer),
				'offer_end_date':self.get_date(offer_end_date,wb.datemode),
				'offer_start_date':self.get_date(offer_start_date,wb.datemode),
				'feature':feature,
				'feature_description':feature_description,
				'owner_id':owner_id,
				'no_of_rooms':no_of_bedrooms,
				'unit_view_id': unit_view_id if unit_view_id else False,
				'gym':True if gym == 'yes' else False,
				'balcony':True if balcony == 'yes' else False,
				'have_pool':True if pool == 'yes' else False,
				'no_of_washroom': int(no_of_washrooms) if no_of_washrooms else '',
				'floor_number':floor_no if floor_no else '',
				'unit_area_final_contract':int(unit_area_as_per_final_contract) if unit_area_as_per_final_contract else '',
				'unit_area_title_deed':int(unit_area_as_per_title_deed) if unit_area_as_per_title_deed else '',
				'floor_area':floor_area,
				'service_charge':service_charge,
				# 'tenant_id':tenant_id,
				'state':state,
				'managed':bool(managed_by),
				'management_fees_percent':management_fees,
			}
			print (unit_vals,'unit_vals')
			# print (service_ids,'service_ids222')
			unit_records = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'zbbm.module', 'search', [[['name', '=', name],['building_id', '=', building_name]]],{'limit': 1})
			if len(unit_records) == 1:
				self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'zbbm.module', 'write', [unit_records, unit_vals])
				unit_records = unit_records[0]
				print (unit_records,'exist')
				# print (service_ids,'service_ids')
				if len(service_ids) > 0:
					for service_details in service_ids:
						print (type(service_details['account_no']),service_details['package_name'])
						# if service_details['account_no']:
						# 	print (int(service_details['account_no']),'account_no')
						services_rec = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'zbbm.services', 'search', [[['account_no', '=', str(service_details['account_no'])],['product_id', '=', service_details['product_id']],['module_id', '=', unit_records]]])
						# print (services_rec,services_rec)
						service_vals = {
							'product_id':service_details['product_id'],
							'package_name':service_details['package_name'],
							'account_no':str(service_details['account_no']),
							'module_id':unit_records,
							# 'building_id':building_name,
							# 'managed_by_rs':service_details['managed_by_rs']
						}
						
						if len(services_rec) == 1:
							print (services_rec,'services_recexist')
							self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'zbbm.services', 'write', [services_rec, service_vals])
						if len(services_rec) == 0:
							print (services_rec,'new')
							self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'zbbm.services', 'create', [service_vals])
						print (service_details,'service_details')
			else:
				unit_records = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'zbbm.module', 'create', [unit_vals])
				print (unit_records,'gggg')
				if unit_records and len(service_ids) > 0:
					# print (service_ids,'sercvvvv')
					for service_details in service_ids:
						service_vals = {
							'product_id':service_details['product_id'],
							'package_name':service_details['package_name'],
							'account_no':str(service_details['account_no']),
							'module_id':unit_records,
							# 'building_id':building_name,
							# 'managed_by_rs':service_details['managed_by_rs']
						}
						service_records = self.sock.execute_kw(self.dbname, self.uid, self.pwd, 'zbbm.services', 'create', [service_vals])
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
