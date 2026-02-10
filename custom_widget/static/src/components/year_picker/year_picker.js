/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { archParseBoolean } from "@web/views/utils";
import { CharField } from "@web/views/fields/char/char_field";
import { Component, onMounted } from "@odoo/owl";

export class YearPicker extends CharField {
    setup() {
        super.setup();
        onMounted(async ()=>{
            $('.date-own').datepicker({
                     minViewMode: 2,
                     format: 'yyyy',
                     autoclose: true,
                     clearBtn: true,
                     immediateUpdates: true,
                     todayHighlight: true
            }).on('changeDate', function(e) {
                 var element = $('.o_form_status_indicator_buttons');
                 element.removeClass('invisible');
                });
            })
    }
}

export const yearPicker = {
    component: YearPicker,
    displayName: _t("Text"),
    supportedTypes: ["char"],
    supportedOptions: [
        {
            label: _t("Dynamic placeholder"),
            name: "dynamic_placeholder",
            type: "boolean",
            help: _t("Enable this option to allow the input to display a dynamic placeholder."),
        },
        {
            label: _t("Model reference field"),
            name: "dynamic_placeholder_model_reference_field",
            type: "field",
            availableTypes: ["char"],
        },
    ],
    extractProps: ({ attrs, options }) => ({
        isPassword: archParseBoolean(attrs.password),
        dynamicPlaceholder: options.dynamic_placeholder || false,
        dynamicPlaceholderModelReferenceField:
            options.dynamic_placeholder_model_reference_field || "",
        autocomplete: attrs.autocomplete,
        placeholder: attrs.placeholder,
    }),
}
YearPicker.template="owl.YearPicker"
registry.category("fields").add("yearPicker", yearPicker);
