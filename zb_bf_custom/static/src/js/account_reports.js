odoo.define('zb_bf_custom.account_report', function (require) {
'use strict';


var core = require('web.core');
var Context = require('web.Context');
var AbstractAction = require('web.AbstractAction');
var Dialog = require('web.Dialog');
var datepicker = require('web.datepicker');
var session = require('web.session');
var field_utils = require('web.field_utils');
var RelationalFields = require('web.relational_fields');
var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
var AccountReports = require('account_reports.account_report');
var WarningDialog = require('web.CrashManager').WarningDialog;
var Widget = require('web.Widget');

var QWeb = core.qweb;
var _t = core._t;

var M2MFilters1 = Widget.extend(StandaloneFieldManagerMixin, {
    /**
     * @constructor
     * @param {Object} fields
     */
    init: function (parent, fields) {
        this._super.apply(this, arguments);
        StandaloneFieldManagerMixin.init.call(this);
        this.fields = fields;
        this.widgets = {};
    },
    /**
     * @override
     */
    willStart: function () {
        var self = this;
        var defs = [this._super.apply(this, arguments)];
        _.each(this.fields, function (field, fieldName) {
            defs.push(self._makeM2MWidget(field, fieldName));
        });
        return Promise.all(defs);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        var $content = $(QWeb.render("m2mWidgetTable", {fields: this.fields}));
        self.$el.append($content);
        _.each(this.fields, function (field, fieldName) {
            self.widgets[fieldName].appendTo($content.find('#'+fieldName+'_field'));
        });
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * This method will be called whenever a field value has changed and has
     * been confirmed by the model.
     *
     * @private
     * @override
     * @returns {Promise}
     */
    _confirmChange: function () {
        var self = this;
        var result = StandaloneFieldManagerMixin._confirmChange.apply(this, arguments);
        var data = {};
        _.each(this.fields, function (filter, fieldName) {
            data[fieldName] = self.widgets[fieldName].value.res_ids;
        });
        this.trigger_up('value_changed', data);
        return result;
    },
    /**
     * This method will create a record and initialize M2M widget.
     *
     * @private
     * @param {Object} fieldInfo
     * @param {string} fieldName
     * @returns {Promise}
     */
    _makeM2MWidget: function (fieldInfo, fieldName) {
        var self = this;
        var options = {};
        options[fieldName] = {
            options: {
                no_create_edit: true,
                no_create: true,
            }
        };
        return this.model.makeRecord(fieldInfo.modelName, [{
            fields: [{
                name: 'id',
                type: 'integer',
            }, {
                name: 'display_name',
                type: 'char',
            }],
            name: fieldName,
            relation: fieldInfo.modelName,
            type: 'many2many',
            value: fieldInfo.value,
        }], options).then(function (recordID) {
            self.widgets[fieldName] = new RelationalFields.FieldMany2ManyTags(self,
                fieldName,
                self.model.get(recordID),
                {mode: 'edit',}
            );
            self._registerWidget(recordID, fieldName, self.widgets[fieldName]);
        });
    },
});


AccountReports.include({
    custom_events: _.extend({}, AccountReports.prototype.custom_events, {
        //My custom code goes here
        'value_changed': function(ev) {
             var self = this;
             console.log(ev,'custom event11111111')
             console.log(self.report_options.partner_ids,'partner_ids')
             console.log(self.report_options.unit_ids,'unit_ids')
             if ('partner_ids' in ev.data) {
                self.report_options.partner_ids = ev.data.partner_ids;
             }
             else
             {
                self.report_options.partner_ids = self.report_options.partner_ids;
             }
             if ('unit_ids' in ev.data) {
                self.report_options.unit_ids = ev.data.unit_ids;
             }
             else
             {
                self.report_options.unit_ids = self.report_options.unit_ids;
             }
             console.log(self.report_options.partner_ids,'partner_ids1')
             console.log(self.report_options.unit_ids,'unit_ids111')
             self.report_options.partner_categories = ev.data.partner_categories;
             self.report_options.analytic_accounts = ev.data.analytic_accounts;
             self.report_options.analytic_tags = ev.data.analytic_tags;
             return self.reload().then(function () {
                 self.$searchview_buttons.find('.account_partner_filter').click();
                 self.$searchview_buttons.find('.account_unit_filter').click();
                 self.$searchview_buttons.find('.account_analytic_filter').click();
             });
         },



    }),

    render_searchview_buttons: function() {
    	this._super.apply(this, arguments);
    	if (this.report_options.unit) {
            if (!this.M2MFilters1) {
                var fields1 = {};
                if ('unit_ids' in this.report_options) {
                    fields1['unit_ids'] = {
                        label: _t('Unit'),
                        modelName: 'zbbm.module',
                        value: this.report_options.unit_ids.map(Number),
                    };
                }
                console.log(fields1,'fields1')
                if (!_.isEmpty(fields1)) {
                    this.M2MFilters1 = new M2MFilters1(this, fields1);
                    this.M2MFilters1.appendTo(this.$searchview_buttons.find('.js_account_unit_m2m'));
                }
            } else {
                this.$searchview_buttons.find('.js_account_unit_m2m').append(this.M2MFilters1.$el);
            }
        }

    },
});

});