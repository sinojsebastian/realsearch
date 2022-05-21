odoo.define('account_dynamic_plg.Dynamic_Plg_Base', function (require) {
'use strict';

var ActionManager = require('web.ActionManager');
var data = require('web.data');
var Dialog = require('web.Dialog');
var AbstractAction = require('web.AbstractAction');
var FavoriteMenu = require('web.FavoriteMenu');
// var pyeval = require('web.pyeval');
// var ViewManager = require('web.ViewManager');
var web_client = require('web.web_client');
var ajax = require('web.ajax');
var core = require('web.core');
var Widget = require('web.Widget');
// var base = require('web_editor.base');
var field_utils = require('web.field_utils');
var rpc = require('web.rpc');
var session = require('web.session');

//var formats = require('web.formats');
var utils = require('web.utils');
var round_di = utils.round_decimals;

var _t = core._t;
var QWeb = core.qweb;

var exports = {};

var DynamicPlgMain = AbstractAction.extend({
    template:'DynamicPlgMain',

    init : function(view, code){
        this._super(view, code);
    },

	start : function(){
        new ControlButtonsPlg(this).appendTo(this.$('.ControlSectionPlg'));
        new UserFiltersPlg(this).appendTo(this.$('.FiltersSectionPlg'));
	    }, //start

    }); //DynamicPlgMain

var ControlButtonsPlg = Widget.extend({
    template:'ControlButtonsPlg',
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
        $(".account_filter_plg").slideToggle("slow",function(){
            $("#apply_button").toggle();
            });
	    },

	apply_button_expand_all : function(event){
	    $('.move-sub-line').collapse('show');
	},

	apply_button_merge_all : function(event){
	    $('.move-sub-line').collapse('hide');
	},

	download_pdf : function(event){
	    var self = this;
	    var filter = self.get_filter_datas();

        var a_pdf = rpc.query({
                args: [[],filter],
                model: 'report.account.dynamic.report_partnerledger',
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
                model: 'report.account.dynamic.report_partnerledger',
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
                    'name':'account_dynamic_plg.partner_ledger_xlsx',
                    'model':'report.account_dynamic_plg.partner_ledger_xlsx',
                    'report_type': 'xlsx',
                    'report_name': 'account_dynamic_plg.partner_ledger_xlsx',
                    'report_file': 'account_dynamic_plg.partner_ledger_xlsx',
                    'data': result,
                    'context': {'active_model':'account.report.partner.ledger',
                                'data': []},
                    'display_name': 'Partner Ledger',
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
	    var filter = self.get_filter_datas();

	    // Hide filter sections when apply filter button
        $(".account_filter_plg").slideToggle("slow",function(){
            $("#apply_button").toggle();
            });

        var final_html = rpc.query({
                args: [[],filter],
                model: 'report.account.dynamic.report_partnerledger',
                method: 'action_view',
            }).then(function(result){
                $(".DataSectionPlg").empty();
                $(".account_filter").css({'opacity':1.0});
                $("#filter_button").toggle();
                $("#pdf_button").toggle();
                $("#xlsx_button").toggle();
                $("#expand_all").toggle();
                $("#merge_all").toggle();
                new AccountContentsPlg(this,result).appendTo($(".DataSectionPlg"));
            });
	},

	get_filter_datas : function(){
	    var self = this;
	    var output = {}

        // Get journals
	    var journal_ids = [];
	    var journal_list = $(".dynamic-journal-multiple").select2('data')
	    for (var i=0; i < journal_list.length; i++){
	        journal_ids.push(parseInt(journal_list[i].id))
	        }
	    output.journal_ids = journal_ids

	    // Get Date filters
	    output.date_filter = $(".dynamic-datefilter-multiple").select2('data')

	    // Get dates
        if ($("#from_date_plg").find("input").val()){
	        output.date_from = $("#from_date_plg").find("input").val();
	        }
        if ($("#to_date_plg").find("input").val()){
            output.date_to = $("#to_date_plg").find("input").val();
            }

        if($('#with_currency').is(':checked')){
            output.amount_currency = true}
        else{
            output.amount_currency = false}

        if($('#with_reco').is(':checked')){
            output.reconciled = true}
        else{
            output.reconciled = false}

        output.result_selection = 'customer';
        if($(".dynamic-report-type-multiple").select2('data')[0]){
            var account_type_selection = $(".dynamic-report-type-multiple").select2('data')[0].id;

            if(account_type_selection === 'rec'){
                output.result_selection = 'customer';
            }
            else if(account_type_selection === 'pay'){
                output.result_selection = 'supplier';
            }
            else{
                output.result_selection = 'customer_supplier';
            }
        }

        // Get checkboxes
	    output.target_move = 'posted'
        if ($("#all_posted_entries").is(':checked')){ // All posted
            output.target_move = 'posted'
            }else{output.target_move = 'all'}
        if ($("#all_entries").is(':checked')){ // All entries
            output.target_move = 'all'
            }else{output.target_move = 'posted'}

        output.date_filter = $(".dynamic-datefilter-multiple").select2('data')
        return output
	},

	}); //ControlButtonsPlg

var UserFiltersPlg = Widget.extend({
    template:'UserFiltersPlg',
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
	    self.$el.append(QWeb.render('CompanyDatefilterLinePlg'));

	    // Getting date filters
	    // Add filter type section
	    self.$el.find('.date-filters').append(QWeb.render('DatefilterSelectionLinePlg'));
	    self.$el.find('.dynamic-datefilter-multiple').select2({
	        placeholder:'Select filter type...',
	        maximumSelectionSize: 1,
	        }).val('this_month').trigger('change');

        // Date from and To
	    self.$el.append(QWeb.render('DateLinePlg'));

        // No need to fetch from DB. Just templates
	    self.$el.append(QWeb.render('TargetAccountsLinePlg'));
        self.$el.find('.dynamic-report-type-multiple').select2({
                    placeholder:'Select account types...',
                    minimumResultsForSearch: 5
                    }).val('rec').trigger('change');
	    self.$el.append(QWeb.render('ComparisonLinePlg'));

        // Getting journals from journal master
	    var journals = [];
	    var journal_ids = []


        rpc.query({
            model: 'account.journal',
            method: 'search_read',
            args: []
            }).then(function (results) {
                _(results).each(function (item) {
                    journals.push({'name':item.name,'code':item.id,'short_code':item.code})
                    journal_ids.push(parseInt(item.id))
                    }) //each
                self.$el.append(QWeb.render('JournalsLine', {'journals': journals}));
                self.$el.find('.dynamic-journal-multiple').select2({
                    placeholder:'Select journals...',
                    minimumResultsForSearch: 5
                    }).val(journal_ids).trigger('change');

                }); //query

        var date = new Date();
        var y = date.getFullYear();
        var m = date.getMonth();

        self.$el.find('#from_date_plg').datetimepicker({
                    icons: {
                        time: "fa fa-clock-o",
                        date: "fa fa-calendar",
                        up: "fa fa-arrow-up",
                        down: "fa fa-arrow-down"
                    },
                    viewMode: 'days',
                    format: 'YYYY-MM-DD',
                    defaultDate: new Date(y, m, 1)
                });
        self.$el.find('#to_date_plg').datetimepicker({
                    icons: {
                        time: "fa fa-clock-o",
                        date: "fa fa-calendar",
                        up: "fa fa-arrow-up",
                        down: "fa fa-arrow-down"
                    },
                    viewMode: 'days',
                    format: 'YYYY-MM-DD',
                    defaultDate: new Date(y, m+1, 0)
                });


	    }, //start

	}); //UserFilters

var AccountContentsPlg = Widget.extend({
    template:'AccountContentsPlg',
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

	/* Used to redirect to move record */
	view_move_line : function(event){
        var self = this;
        var context = {};

        var redirect_to_document = function (res_model, res_id, view_id) {
            web_client.do_action({
                type:'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                res_model: res_model,
                views: [[view_id || false, 'form']],
                res_id: res_id,
                context: context,
            });
            web_client.do_notify(_("Redirected"), "Window has been redirected");
        };

        redirect_to_document('account.move',$(event.currentTarget).data('move-id'));

        }, //view_move_line


    }); //AccountContentsPlg


    core.action_registry.add('dynamic_plg_report', DynamicPlgMain);

});

