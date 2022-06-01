from odoo import api, fields, models, _
import ast
from datetime import date,datetime,timedelta 

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'



    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        service_products_ids = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.service_products_ids')
        service_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.service_product_id')
        service_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.service_journal_id')
         
        deposit_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.deposit_journal_id')
        deposit_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.deposit_product_id')
        
        ewa_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.ewa_product_id')
        internet_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.internet_product_id')
        tabreed_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.tabreed_product_id')
        osn_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.osn_product_id')
#         osn_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.osn_journal_id')
        
        owner_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.owner_id')
        admin_fee_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.admin_fee_product_id')
        
        contra_liability_account_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.contra_liability_account_id')
        deposit_liability_account_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.deposit_liability_account_id')
        commission_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.commission_journal_id')
        rent_invoice_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.rent_invoice_journal_id')
        maintenance_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.maintenance_journal_id')
        management_fee_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.management_fee_journal_id')
        management_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.management_product_id')
        commission_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.commission_product_id')
        
        resale_commission_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.resale_commission_product_id')
        resale_commission_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.resale_commission_journal_id')
        
        income_account_ids = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.income_account_ids')
        expense_account_ids = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.expense_account_ids')
        service_invoice_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.service_invoice_journal_id')
        vendor_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.vendor_journal_id')
        resale_vendor_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.resale_vendor_journal_id')
        
        building_income_acccount_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.building_income_acccount_id')
        building_expense_acccount_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.building_expense_acccount_id')
        
        common_service_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.common_service_product_id')
        
        rent_invoice_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.rent_invoice_product_id')
        agent_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.agent_journal_id')

        
        rent_transfer_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.rent_transfer_journal_id')
        rent_transfer_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.rent_transfer_product_id')
        
        project_income_type_ids = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.project_income_type_ids')
        project_expense_type_ids = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.project_expense_type_ids')
        
        ewa_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.ewa_journal_id')
        internet_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.internet_journal_id')
        tabreed_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.tabreed_journal_id')
        
        building_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.building_journal_id')
        admin_fee_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.admin_fee_journal_id')
        
        rent_commission_expense_acccount_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.rent_commission_expense_acccount_id')
        rent_commission_payable_acccount_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.rent_commission_payable_acccount_id')
        
        
        rent_prorated_calculation = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.rent_prorated_calculation')
        collection_excluded_account_ids = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.collection_excluded_account_ids')
        
        invoice_generation_days = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.invoice_generation_days')
        invoice_generation_date = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.invoice_generation_date')
        invoice_start_date = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.invoice_start_date')
        
        
        
        accruded_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.accruded_journal_id')
        
        installment_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.installment_journal_id')
        installment_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.installment_product_id') 
        
        install_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.install_journal_id')
        
        company_bank_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.company_bank_id') 
        
        max_reservation_time_lease = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.max_reservation_time_lease')
        deposit_transfer_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.deposit_transfer_journal_id')
        
        advance_transfer_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.advance_transfer_journal_id')
        advance_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.advance_product_id') 
        
        advance_payment_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.advance_payment_journal_id')
        advance_expense_account_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.advance_expense_account_id')
        advance_expense_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.advance_expense_journal_id')
        
        internet_stc_product_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.internet_stc_product_id')
        internet_stc_journal_id = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.internet_stc_journal_id')
        
        
        res.update({
            'max_reservation_time_lease' : int(max_reservation_time_lease),
        })
        res.update(installment_product_id=int(installment_product_id))
        
        res.update(invoice_generation_days=int(invoice_generation_days))
        
        res.update(invoice_generation_date=invoice_generation_date)
        
        res.update(invoice_start_date=invoice_start_date)
        
        res.update(accruded_journal_id=int(accruded_journal_id))
        
        res.update(rent_prorated_calculation=rent_prorated_calculation)
        
        res.update(rent_commission_expense_acccount_id=int(rent_commission_expense_acccount_id))
        res.update(rent_commission_payable_acccount_id =int(rent_commission_payable_acccount_id))
        
        res.update(building_journal_id=int(building_journal_id))

        res.update(rent_transfer_journal_id=int(rent_transfer_journal_id))
        res.update(rent_transfer_product_id=int(rent_transfer_product_id))
        rs_in_exp_type_ids = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.rs_in_exp_type_ids')
        owner_in_exp_type_ids = self.env['ir.config_parameter'].sudo().get_param('zb_bf_custom.owner_in_exp_type_ids')
        
        res.update(rent_invoice_product_id=int(rent_invoice_product_id))
        
        res.update(common_service_product_id=int(common_service_product_id))
        
        res.update(building_income_acccount_id=int(building_income_acccount_id))
        res.update(building_expense_acccount_id=int(building_expense_acccount_id))
        
        
        res.update(service_journal_id=int(service_journal_id))
        res.update(service_product_id=int(service_product_id))
        
        res.update(deposit_journal_id=int(deposit_journal_id))
        res.update(deposit_product_id=int(deposit_product_id))
        
        res.update(ewa_product_id=int(ewa_product_id))
        res.update(internet_product_id=int(internet_product_id))
        res.update(tabreed_product_id=int(tabreed_product_id))
        res.update(osn_product_id=int(osn_product_id))
#         res.update(osn_journal_id=int(osn_journal_id))
        
        res.update(owner_id=int(owner_id))
        res.update(admin_fee_product_id=int(admin_fee_product_id))
        
        res.update(contra_liability_account_id=int(contra_liability_account_id))
        res.update(deposit_liability_account_id=int(deposit_liability_account_id))
        res.update(commission_journal_id=int(commission_journal_id))
        res.update(rent_invoice_journal_id=int(rent_invoice_journal_id))
        res.update(maintenance_journal_id=int(maintenance_journal_id))
        res.update(management_fee_journal_id=int(management_fee_journal_id))
        res.update(management_product_id=int(management_product_id))
        res.update(commission_product_id=int(commission_product_id))
        
        res.update(resale_commission_product_id=int(resale_commission_product_id))
        res.update(resale_commission_journal_id=int(resale_commission_journal_id))
        res.update(service_invoice_journal_id=int(service_invoice_journal_id))
        res.update(vendor_journal_id=int(vendor_journal_id))
        res.update(resale_vendor_journal_id=int(resale_vendor_journal_id))
        
        res.update(ewa_journal_id=int(ewa_journal_id))
        res.update(tabreed_journal_id=int(tabreed_journal_id))
        res.update(internet_journal_id=int(internet_journal_id))
        res.update(agent_journal_id =int(agent_journal_id))
        
        res.update(admin_fee_journal_id =int(admin_fee_journal_id))
        
        res.update(installment_journal_id =int(installment_journal_id))
        res.update(company_bank_id =int(company_bank_id))
        
        res.update(install_journal_id =int(install_journal_id))
        
        res.update(deposit_transfer_journal_id=int(deposit_transfer_journal_id))
        
        res.update(advance_product_id=int(advance_product_id))
        res.update(advance_transfer_journal_id=int(advance_transfer_journal_id))
        res.update(advance_payment_journal_id=int(advance_payment_journal_id))
        
        res.update(advance_expense_account_id=int(advance_expense_account_id))
        res.update(advance_expense_journal_id=int(advance_expense_journal_id))
        
        res.update(internet_stc_product_id=int(internet_stc_product_id))
        res.update(internet_stc_journal_id=int(internet_stc_journal_id))
        
        if income_account_ids == False:
            res.update(income_account_ids=[(6, 0, ast.literal_eval('None'))],)
        else:
            res.update(income_account_ids=[(6, 0, ast.literal_eval(income_account_ids))],)
            
        if project_income_type_ids == False:
            res.update(project_income_type_ids=[(6, 0, ast.literal_eval('None'))],)
        else:
            res.update(project_income_type_ids=[(6, 0, ast.literal_eval(project_income_type_ids))],)
            
        if project_expense_type_ids == False:
            res.update(project_expense_type_ids=[(6, 0, ast.literal_eval('None'))],)
        else:
            res.update(project_expense_type_ids=[(6, 0, ast.literal_eval(project_expense_type_ids))],)
            
        if rs_in_exp_type_ids == False:
            res.update(rs_in_exp_type_ids=[(6, 0, ast.literal_eval('None'))],)
        else:
            res.update(rs_in_exp_type_ids=[(6, 0, ast.literal_eval(rs_in_exp_type_ids))],)
            
        if owner_in_exp_type_ids == False:
            res.update(owner_in_exp_type_ids=[(6, 0, ast.literal_eval('None'))],)
        else:
            res.update(owner_in_exp_type_ids=[(6, 0, ast.literal_eval(owner_in_exp_type_ids))],)
            
        if collection_excluded_account_ids == False:
            res.update(collection_excluded_account_ids=[(6, 0, ast.literal_eval('None'))],)
        else:
            res.update(collection_excluded_account_ids=[(6, 0, ast.literal_eval(collection_excluded_account_ids))],)
            
#         if expense_account_ids == False:
#             res.update(expense_account_ids=[(6, 0, ast.literal_eval('None'))],)
#         else:
#             res.update(expense_account_ids=[(6, 0, ast.literal_eval(expense_account_ids))],)
#         
        
        return res
    
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('zb_bf_custom.service_products_ids', self.service_products_ids.ids)
        set_param('zb_bf_custom.service_product_id', self.service_product_id.id)
        set_param('zb_bf_custom.service_journal_id', self.service_journal_id.id)
        
        set_param('zb_bf_custom.deposit_journal_id', self.deposit_journal_id.id)
        set_param('zb_bf_custom.deposit_product_id', self.deposit_product_id.id)
        
        set_param('zb_bf_custom.ewa_product_id', self.ewa_product_id.id)
        set_param('zb_bf_custom.internet_product_id', self.internet_product_id.id)
        set_param('zb_bf_custom.tabreed_product_id', self.tabreed_product_id.id)
        set_param('zb_bf_custom.osn_product_id', self.osn_product_id.id)
#         set_param('zb_bf_custom.osn_journal_id', self.osn_journal_id.id)
        
        set_param('zb_bf_custom.owner_id', self.owner_id.id)
        set_param('zb_bf_custom.admin_fee_product_id', self.admin_fee_product_id.id)
        
        set_param('zb_bf_custom.contra_liability_account_id', self.contra_liability_account_id.id)
        set_param('zb_bf_custom.deposit_liability_account_id', self.deposit_liability_account_id.id)
        set_param('zb_bf_custom.commission_journal_id', self.commission_journal_id.id)
        set_param('zb_bf_custom.rent_invoice_journal_id', self.rent_invoice_journal_id.id)
        set_param('zb_bf_custom.maintenance_journal_id', self.maintenance_journal_id.id)
        set_param('zb_bf_custom.management_fee_journal_id', self.management_fee_journal_id.id)
        set_param('zb_bf_custom.management_product_id', self.management_product_id.id)
        set_param('zb_bf_custom.commission_product_id', self.commission_product_id.id)
        
        set_param('zb_bf_custom.resale_commission_product_id', self.resale_commission_product_id.id)
        set_param('zb_bf_custom.resale_commission_journal_id', self.resale_commission_journal_id.id)
        
        set_param('zb_bf_custom.income_account_ids', self.income_account_ids.ids)
        set_param('zb_bf_custom.service_invoice_journal_id', self.service_invoice_journal_id.id)
        set_param('zb_bf_custom.vendor_journal_id', self.vendor_journal_id.id)
        set_param('zb_bf_custom.resale_vendor_journal_id', self.resale_vendor_journal_id.id)
#         set_param('zb_bf_custom.expense_account_ids', self.expense_account_ids.ids)

        set_param('zb_bf_custom.building_income_acccount_id', self.building_income_acccount_id.id)
        set_param('zb_bf_custom.building_expense_acccount_id', self.building_expense_acccount_id.id)
        
        set_param('zb_bf_custom.common_service_product_id', self.common_service_product_id.id)
        
        set_param('zb_bf_custom.rent_invoice_product_id', self.rent_invoice_product_id.id)
        
        set_param('zb_bf_custom.rent_transfer_journal_id', self.rent_transfer_journal_id.id)
        set_param('zb_bf_custom.rent_transfer_product_id', self.rent_transfer_product_id.id)
        
        set_param('zb_bf_custom.project_income_type_ids', self.project_income_type_ids.ids)
        set_param('zb_bf_custom.project_expense_type_ids', self.project_expense_type_ids.ids)
        
        set_param('zb_bf_custom.ewa_journal_id', self.ewa_journal_id.id)
        set_param('zb_bf_custom.internet_journal_id', self.internet_journal_id.id)
        set_param('zb_bf_custom.tabreed_journal_id', self.tabreed_journal_id.id)

        set_param('zb_bf_custom.rs_in_exp_type_ids', self.rs_in_exp_type_ids.ids)
        set_param('zb_bf_custom.owner_in_exp_type_ids', self.owner_in_exp_type_ids.ids)
        
        set_param('zb_bf_custom.building_journal_id', self.building_journal_id.id)
        set_param('zb_bf_custom.agent_journal_id', self.agent_journal_id.id)
        
        set_param('zb_bf_custom.admin_fee_journal_id', self.admin_fee_journal_id.id)
        
        set_param('zb_bf_custom.accruded_journal_id', self.accruded_journal_id.id)
        
        set_param('zb_bf_custom.rent_commission_expense_acccount_id', self.rent_commission_expense_acccount_id.id)
        set_param('zb_bf_custom.rent_commission_payable_acccount_id', self.rent_commission_payable_acccount_id.id)
        
        
        set_param('zb_bf_custom.rent_prorated_calculation', self.rent_prorated_calculation)
        set_param('zb_bf_custom.collection_excluded_account_ids', self.collection_excluded_account_ids.ids)
        
        set_param('zb_bf_custom.invoice_generation_days', self.invoice_generation_days)
        set_param('zb_bf_custom.invoice_generation_date', self.invoice_generation_date)
        set_param('zb_bf_custom.invoice_start_date', self.invoice_start_date)
        
        set_param('zb_bf_custom.installment_journal_id', self.installment_journal_id.id)
        set_param('zb_bf_custom.install_journal_id', self.install_journal_id.id)
        
        set_param('zb_bf_custom.installment_product_id', self.installment_product_id.id)
        set_param('zb_bf_custom.company_bank_id', self.company_bank_id.id)
        
        set_param('zb_bf_custom.max_reservation_time_lease',int(self.max_reservation_time_lease) or 0)
        
        set_param('zb_bf_custom.deposit_transfer_journal_id', self.deposit_transfer_journal_id.id)
        
        set_param('zb_bf_custom.advance_transfer_journal_id', self.advance_transfer_journal_id.id)
        set_param('zb_bf_custom.advance_payment_journal_id', self.advance_payment_journal_id.id)
        
        set_param('zb_bf_custom.advance_product_id', self.advance_product_id.id)
        set_param('zb_bf_custom.advance_expense_account_id', self.advance_expense_account_id.id)
        set_param('zb_bf_custom.advance_expense_journal_id', self.advance_expense_journal_id.id)
        
        set_param('zb_bf_custom.internet_stc_product_id', self.internet_stc_product_id.id)
        set_param('zb_bf_custom.internet_stc_journal_id', self.internet_stc_journal_id.id)

    
    install_journal_id = fields.Many2one('account.journal',string="Installment Transfer Journal")
    installment_journal_id = fields.Many2one('account.journal',string="Installment Journal")
    installment_product_id = fields.Many2one('product.product',string="Installment Product")
    service_products_ids = fields.Many2many('product.product','service_products_rel','service_id','product_id',string="Service Products")
    service_product_id = fields.Many2one('product.product',string='Service Product')
    service_journal_id = fields.Many2one('account.journal',string='Service Journal')
    deposit_journal_id = fields.Many2one('account.journal',string='Deposit Journal')
    deposit_product_id = fields.Many2one('product.product',string="Deposit Product")
    ewa_product_id = fields.Many2one('product.product',string="EWA Product")
    ewa_journal_id = fields.Many2one('account.journal',string='EWA Journal')
    internet_product_id = fields.Many2one('product.product',string="Internet Product")
    internet_journal_id = fields.Many2one('account.journal',string='Internet Journal')
    contra_liability_account_id = fields.Many2one('account.account',string="Liability Account")
    owner_id = fields.Many2one('res.partner',string='Owner')
    deposit_liability_account_id = fields.Many2one('account.account',string="Deposit Liability Account")
    commission_journal_id = fields.Many2one('account.journal',string='Commission Journal')
    commission_product_id = fields.Many2one('product.product',string="Commission Product")
    income_account_ids = fields.Many2many('account.account','income_account_setting_rel',string="Service Income Accounts")
    expense_account_ids = fields.Many2many('account.account','expense_account_setting_rel',string="Expense Accounts")
    tabreed_product_id = fields.Many2one('product.product',string='Tabreed Product')
    tabreed_journal_id = fields.Many2one('account.journal',string='Tabreed Journal')
    resale_commission_product_id = fields.Many2one('product.product',string="Resale Commission Product")
    resale_commission_journal_id = fields.Many2one('account.journal',string="Resale Commission Journal")
    rent_invoice_journal_id = fields.Many2one('account.journal',string="Rent Invoice Journal")
    maintenance_journal_id = fields.Many2one('account.journal',string="Maintenance Journal")
    management_fee_journal_id = fields.Many2one('account.journal',string="Management Fee Journal")
    management_product_id = fields.Many2one('product.product',string='Management Product')
    admin_fee_product_id = fields.Many2one('product.product',string="Product For Admin Fees")
#       osn_journal_id = fields.Many2one('account.journal',string="OSN Journal")
    osn_product_id = fields.Many2one('product.product',string='OSN Product')
    service_invoice_journal_id = fields.Many2one('account.journal',string="Service Invoice Journal")
    vendor_journal_id = fields.Many2one('account.journal',string='Vendor Bill Journal')
    resale_vendor_journal_id = fields.Many2one('account.journal',string='Resale Vendor Bill Journal')
    
    building_income_acccount_id = fields.Many2one('account.account',string="Building Income Account")
    building_expense_acccount_id = fields.Many2one('account.account',string="Building Expense Account")
    
    common_service_product_id = fields.Many2one('product.product',string="Common EWA Service Product")
    
    rent_invoice_product_id = fields.Many2one('product.product',string="Rent Invoice Product")
    
    rent_transfer_journal_id = fields.Many2one('account.journal',string="Rent Transfer Journal")
    rent_transfer_product_id = fields.Many2one('product.product',string='Rent Transfer Product')
    
    project_income_type_ids = fields.Many2many('account.account.type','project_income_type_rel',string="Income Account Types")
    project_expense_type_ids = fields.Many2many('account.account.type','project_expense_type_rel',string="Expense Accounts Types")
    
    rs_in_exp_type_ids = fields.Many2many('account.journal','rs_journal_rel',string="Real search Income/Expense Journals")
    owner_in_exp_type_ids = fields.Many2many('account.journal','owner_journal_rel',string="Owner Income/Expense Journals")
    
    building_journal_id = fields.Many2one('account.journal',string='Building Bank Journal')
    agent_journal_id = fields.Many2one('account.journal', string='Agent Commission Journal')
    
    admin_fee_journal_id = fields.Many2one('account.journal', string='Admin Fee Journal')
    
    
    rent_commission_expense_acccount_id = fields.Many2one('account.account',string="Rent Commission Expense Account")
    rent_commission_payable_acccount_id = fields.Many2one('account.account',string="Rent Commission Payable Account")
    
    deposit_transfer_journal_id = fields.Many2one('account.journal',string="Deposit Transfer Journal")
    
    
    rent_prorated_calculation = fields.Selection(
        [
        ('monthly', 'Monthly Calendar Days'),
        ('yearly', 'Yearly'),
        ], 'Rent Prorated Calculation')
    
    collection_excluded_account_ids = fields.Many2many('account.account.type','collection_account_type_rel',string="Collection Excluded Account Types")
    
    accruded_journal_id = fields.Many2one('account.journal', string='Accruded Journal')
    
    invoice_generation_days = fields.Integer(string="Invoice Generation Days")
    company_bank_id =  fields.Many2one('res.partner.bank', string='Company Bank')
    max_reservation_time_lease = fields.Integer(string='Maximum Reservation Time for Lease',default=0)
    invoice_generation_date = fields.Date(string="Invoice End Date")
    invoice_start_date = fields.Date(string="Invoice Start Date")
    
    advance_transfer_journal_id = fields.Many2one('account.journal',string="Advance Transfer Journal")
    advance_payment_journal_id = fields.Many2one('account.journal',string="Advance Payment Journal")
    advance_product_id = fields.Many2one('product.product',string="Advance Product")
    advance_expense_account_id = fields.Many2one('account.account',string="Advance Expense Account")
    advance_expense_journal_id = fields.Many2one('account.journal',string="Advance Expense Journal")
    
    internet_stc_product_id = fields.Many2one('product.product',string="Internet STC Product")
    internet_stc_journal_id = fields.Many2one('account.journal',string='Internet STC Journal')
    
    #default=datetime.strptime('2021-01-01','%Y-%m-%d')
    
