odoo.define('account_dynamic_bs.Dynamic_Bs_Base', function (require) {
'use strict';

require('web.dom_ready');
var data = require('web.data');

var FavoriteMenu = require('web.FavoriteMenu');
// var pyeval =  require('web.py_utils');

var AbstractAction = require('web.AbstractAction');
var web_client = require('web.web_client');
var core = require('web.core');
var Widget = require('web.Widget');
var field_utils = require('web.field_utils');
var rpc = require('web.rpc');
var time = require('web.time');
var session = require('web.session');

//var formats = require('web.formats');
var utils = require('web.utils');
var round_di = utils.round_decimals;

var _t = core._t;
var QWeb = core.qweb;


var DynamicBsMain = AbstractAction.extend({
    template:'DynamicBsMain',

    init : function(view, code){
        this._super(view, code);
    },

	start : function(){
        new ControlButtonsBs(this).appendTo(this.$('.ControlSectionBs'));
        new UserFiltersBs(this).appendTo(this.$('.FiltersSectionBs'));
	    }, //start

    }); //DynamicBsMain

var ControlButtonsBs = Widget.extend({
    template:'ControlButtonsBs',
    events: {
        'click #filter_button': 'filter_button_click',
        'click #apply_button': 'apply_button_click',
        'click #expand_all': 'apply_button_expand_all',
        'click #merge_all': 'apply_button_merge_all',
        'click #pdf_button': 'download_pdf',
        'click #xlsx_button': 'download_xlsx',
    },

    init : function(view, code){
		this._super(view, code);
		},

	start : function(){
	    var self = this;
	    //$("#expand_all").toggle();
        //$("#merge_all").toggle();
	    }, //start

	filter_button_click : function(event){
        $(".account_filter_pl").slideToggle("slow",function(){
            $("#apply_button").toggle();
            });
	    },

	apply_button_expand_all : function(event){
	    $('.row-toggle-line').collapse('show');
	},

	apply_button_merge_all : function(event){
	    $('.row-toggle-line').collapse('hide');
	},

	download_pdf : function(event){
	    var self = this;
	    var filter = self.get_filter_datas();

        var a_pdf = rpc.query({
                args: [[],filter],
                model: 'report.account.dynamic.report_financial_bs',
                method: 'action_pdf',
            })
            .then(function(result){
                return web_client.do_action(result);
            });
	},

	download_xlsx : function(event){
	    var self = this;
	    $(".account_filter").css({'opacity':0.5});
	    $("#filter_button").toggle();
	    $("#pdf_button").toggle();
	    $("#xlsx_button").toggle();
	    $("#expand_all").toggle();
	    $("#merge_all").toggle();
	    $('#loader').css({'visibility':'visible'});
	    var filter = self.get_filter_datas();


        return rpc.query({
                args: [[],filter],
                model: 'report.account.dynamic.report_financial_bs',
                method: 'action_xlsx',
            })
            .then(function(result){
                $(".account_filter").css({'opacity':1.0});
                $("#filter_button").toggle();
                $("#pdf_button").toggle();
                $("#xlsx_button").toggle();
                $("#expand_all").toggle();
                $("#merge_all").toggle();
                $('#loader').css({'visibility':'hidden'});
                var action = {
                    'type': 'ir.actions.report',
                    'name':'account_dynamic_bs.balance_sheet_xlsx',
                    'model':'report.account_dynamic_bs.balance_sheet_xlsx',
                    'report_type': 'xlsx',
                    'report_name': 'account_dynamic_bs.balance_sheet_xlsx',
                    'report_file': 'account_dynamic_bs.balance_sheet_xlsx',
                    'data': result,
                    'context': {'active_model':'accounting.report',
                                'data': []},
                    'display_name': 'Profit and Loss',
                };
                return web_client.do_action(action);
            });
	},

	apply_button_click : function(event){
	    var self = this;
	    $(".account_filter").css({'opacity':0.5});
	    $("#filter_button").toggle();
	    $("#pdf_button").toggle();
	    $("#xlsx_button").toggle();
	    $("#expand_all").toggle();
	    $("#merge_all").toggle();
	    $('#loader').css({'visibility':'visible'});
	    var output = self.get_filter_datas();

	    // Hide filter sections when apply filter button
        $(".account_filter_pl").slideToggle("slow",function(){
            $("#apply_button").toggle();
            });

        var final_html = rpc.query({
                args: [[],output],
                model: 'report.account.dynamic.report_financial_bs',
                method: 'action_view',
            }).then(function(result){
                $(".DataSectionBs").empty();
                $(".account_filter").css({'opacity':1.0});
                $("#filter_button").toggle();
                $("#pdf_button").toggle();
                $("#xlsx_button").toggle();
                $("#expand_all").toggle();
                $("#merge_all").toggle();
                new AccountContentsBs(this,result).appendTo($(".DataSectionBs"));
                $('.row-toggle-line').collapse('show');
            });
	},

	get_filter_datas : function(){
	    var self = this;
	    var output = {}

        // Get companies
        var company_ids = [];
	    var company_list = $(".dynamic-company-multiple").select2('data')
	    for (var i=0; i < company_list.length; i++){
	        company_ids.push(parseInt(company_list[i].id))
	        }
	    output.company_ids = company_ids
	    
	    //Get Account
        var accounts = [];
        var account_list = $(".dynamic-finance-multiple").select2('data')
        for (var i = 0; i < account_list.length; i++) {
            accounts.push(parseInt(account_list[i].id))
        }
        output.accounts = accounts

	    // Get Date filters
	    output.date_filter = $(".dynamic-datefilter-multiple").select2('data')

	    // Get dates
        if ($("#from_date_pl").find("input").val()){
	        output.date_from = $("#from_date_pl").find("input").val();
	        }
        if ($("#to_date_pl").find("input").val()){
            output.date_to = $("#to_date_pl").find("input").val();
            }

        // Get filter dates
        if ($("#filter_from_date").find("input").val()){
	        output.date_from_cmp = $("#filter_from_date").find("input").val();
	        }
        if ($("#filter_to_date").find("input").val()){
            output.date_to_cmp = $("#filter_to_date").find("input").val();
            }
        if($('#credit_debit_yes').is(':checked')){
            output.debit_credit = true
        }
        else{
            output.debit_credit = false
        }

        output.filter_cmp = 'filter_no';
        if($(".dynamic-filter-by-multiple").select2('data')[0]){
            var selection_filter = $(".dynamic-filter-by-multiple").select2('data')[0].id;

            if(selection_filter === 'by_date'){
                output.filter_cmp = 'filter_date';
            }
            else{
                output.filter_cmp = 'filter_no';
            }
        }

        output.label_filter = $('.label_filter').val();
        // Get checkboxes
	output.target_move = 'posted'
        if ($("#all_posted_entries").is(':checked')){ // All posted
            output.target_move = 'posted'
            }else{output.target_move = 'all'}
        if ($("#all_entries").is(':checked')){ // All entries
            output.target_move = 'all'
            }else{output.target_move = 'posted'}

        if ($("#enable_comparison").is(':checked')){ // Enable comparison
	        output.enable_filter = true;
	        }else{output.enable_filter = false}

        output.date_filter = $(".dynamic-datefilter-multiple").select2('data')
        return output
	},

	}); //ControlButtonsBs

var UserFiltersBs = Widget.extend({
    template:'UserFiltersBs',
    events: {
        'change #enable_comparison': 'enable_comparison',
        'change #disable_comparison': 'disable_comparison',
        'change .dynamic-filter-by-multiple': 'change_filter'
        },

    change_filter : function(event){
        if($(".dynamic-filter-by-multiple").select2('data')[0]){
            var selection_filter = $(".dynamic-filter-by-multiple").select2('data')[0].id;

            if(selection_filter === 'by_date'){
                $(".comparison-dates").fadeIn(500);
            }
            else{
                $(".comparison-dates").fadeOut(500);
            }
        }

    },

    enable_comparison : function(event){
       $(".comparison").fadeIn(500);
       $(".comparison-dates").fadeIn(500);
    },

	disable_comparison : function(event){
       $(".comparison").fadeOut(500);
       $(".comparison-dates").fadeOut(500);
    },


    init : function(view, code){
		this._super(view, code);
		},

	start : function(){
	    var self = this;
	    var id = session.uid;

	    // Calling common template. for both company and Date filter
	    self.$el.append(QWeb.render('CompanyDatefilterLineBs'));

	    // Getting date filters
	    // Add filter type section
	    self.$el.find('.date-filters').append(QWeb.render('DatefilterSelectionLineBs'));
	    self.$el.find('.dynamic-datefilter-multiple').select2({
	        placeholder:'Select filter type...',
	        maximumSelectionSize: 1,
	        }).val('this_month').trigger('change');

        // Getting companies from company master
        var company_filter = ['id','=',parseInt(session.company_id)];
        var company_ids = [];
        var companies = []

        rpc.query({
            model: 'res.company',
            method: 'search_read',
            domain: [company_filter],
            fields: ['id','name'],
            }).then(function (results) { // do something
                _(results).each(function (item) {
                    company_ids.push({'name':item.name,'code':item.id})
                    companies.push(parseInt(item.id))
                    }) //each
                self.$el.find('.multi-companies').append(QWeb.render('MultiCompaniesBs', {'companies': company_ids}));
                self.$el.find('.dynamic-company-multiple').select2({
                    placeholder:'Select companies...',
                    }).val(companies).trigger('change');
                });
                
                
        // Getting accounts
            var account_filter = ['parent_id', '=', false];
            var account_filter1 = ['report_types', '=', 'balance_sheet']
            var account_ids = [];
            var accounts = []

            rpc.query({
                model: 'account.financial.report',
                method: 'search_read',
                domain: [account_filter, account_filter1],
                fields: ['id', 'name', 'parent_id'],
            }).then(function(results) {
                _(results).each(function(item) {
                    accounts.push({ 'name': item.name, 'code': item.id })
                }) //each
                self.$el.find('.normal_finance').append(QWeb.render('FinanceLine', { 'accounts': accounts }));
                self.$el.find('.dynamic-finance-multiple').select2({
                    placeholder: 'Select account reports...',
                });
            }); //query
            
            

        // Date from and To
	    self.$el.append(QWeb.render('DateLineBs'));

        // No need to fetch from DB. Just templates
	    self.$el.append(QWeb.render('TargetAccountsLineBs'));
	    self.$el.append(QWeb.render('ComparisonLineBs'));

        self.$el.find('.dynamic-filter-by-multiple').select2({
	        placeholder:'Select filter by...',
	        maximumSelectionSize: 1,
	        }).val('by_date').trigger('change');

        var date = new Date();
        var y = date.getFullYear();
        var m = date.getMonth();

	    self.$el.find('#filter_from_date').datetimepicker({
                    icons: {
                        time: "fa fa-clock-o",
                        date: "fa fa-calendar",
                        up: "fa fa-arrow-up",
                        down: "fa fa-arrow-down"
                    },
                    viewMode: 'days',
                    format: time.getLangDateFormat(),
                    defaultDate: new Date(y, m, 1)
                });
        self.$el.find('#filter_to_date').datetimepicker({
                    icons: {
                        time: "fa fa-clock-o",
                        date: "fa fa-calendar",
                        up: "fa fa-arrow-up",
                        down: "fa fa-arrow-down"
                    },
                    viewMode: 'days',
                    format: time.getLangDateFormat(),
                    defaultDate: new Date(y, m+1, 0)
                });

        self.$el.find('#from_date_pl').datetimepicker({
                    icons: {
                        time: "fa fa-clock-o",
                        date: "fa fa-calendar",
                        up: "fa fa-arrow-up",
                        down: "fa fa-arrow-down"
                    },
                    viewMode: 'days',
                    format:  time.getLangDateFormat(),
                    defaultDate: new Date(y, m, 1),
                    
                });
        self.$el.find('#to_date_pl').datetimepicker({
                    icons: {
                        time: "fa fa-clock-o",
                        date: "fa fa-calendar",
                        up: "fa fa-arrow-up",
                        down: "fa fa-arrow-down"
                    },
                    viewMode: 'days',
                    format:  time.getLangDateFormat(),
                    defaultDate: new Date(y, m+1, 0),
                });
        self.$el.find(".comparison").hide();
        self.$el.find(".comparison-dates").hide();

	    }, //start

	}); //UserFilters

var AccountContentsBs = Widget.extend({
    template:'AccountContentsBs',
    events: {
        // events binding
        'click .view-source': 'view_move_line',
        'click .view-invoice': 'view_invoice',
        },
    init : function(view, code){
		this._super(view, code);
		this.result = JSON.parse(code); // To convert string to JSON
		},
	start : function(){
	    var self = this;
	    $('#loader').css({'visibility':'hidden'});

	    }, //start
    format_currency_with_symbol: function(amount, precision, symbol, position){
	    var decimals = precision;
	    if (typeof amount === 'number') {
            amount = round_di(amount,decimals).toFixed(decimals);
            amount = field_utils.format.float(round_di(amount, decimals), { type: 'float', digits: [69, decimals]});
        }
        if (position === 'after') {
            return amount + ' ' + (symbol || '');
        } else {
            return (symbol || '') + ' ' + amount;
        }

        return amount;
	    },
    }); //AccountContentsBs


    core.action_registry.add('dynamic_bs_report', DynamicBsMain);

});

