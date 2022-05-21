odoo.define('kanban_draggable.kanban_renderer',function(require){
"use strict";


var KanbanRenderer = require('web.KanbanRenderer');

KanbanRenderer.include({

    _setState: function (state) {
        this._super.apply(this, arguments);

        var arch = this.arch;
        var drag_drop = false;
        this.columnOptions.draggable = false;
        
        this.recordOptions.sortable = false;

        this.columnOptions.sortable = false;
       
    },

    _renderGrouped: function (fragment) {
        this._super.apply(this, arguments);

        if (this.columnOptions.sortable==false){
            this.$el.sortable( "disable" );
        }

    },



});

});