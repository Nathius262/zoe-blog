/* Based on editor.scss */
@import 'editor';

a.cke_button_disabled,

/* Those two are to overwrite the gradient filter since we cannot have both of them. */
a.cke_button_disabled:hover,
a.cke_button_disabled:focus,
a.cke_button_disabled:active
{
	filter: alpha(opacity = 30);
}

/* PNG Alpha Transparency Fix For IE<9 */
.cke_button_disabled .cke_button_icon
{
	filter: progid:DXImageTransform.Microsoft.gradient(startColorstr=#00ffffff, endColorstr=#00ffffff);
}

.cke_button_off:hover,
.cke_button_off:focus,
.cke_button_off:active
{
	filter: alpha(opacity = 100);
}

.cke_combo_disabled .cke_combo_inlinelabel,
.cke_combo_disabled .cke_combo_open
{
	filter: alpha(opacity = 30);
}

.cke_toolbox_collapser
{
	border: 1px solid #a6a6a6;
}

.cke_toolbox_collapser .cke_arrow
{
	margin-top: 1px;
}

/* Gradient filters must be removed for HC mode to reveal the background. */
.cke_hc .cke_top,
.cke_hc .cke_bottom,
.cke_hc .cke_combo_button,
.cke_hc a.cke_combo_button:hover,
.cke_hc a.cke_combo_button:focus,
.cke_hc .cke_toolgroup,
.cke_hc .cke_button_on,
.cke_hc a.cke_button_off:hover,
.cke_hc a.cke_button_off:focus,
.cke_hc a.cke_button_off:active,
.cke_hc .cke_toolbox_collapser,
.cke_hc .cke_toolbox_collapser:hover,
.cke_hc .cke_panel_grouptitle
{
	filter: progid:DXImageTransform.Microsoft.gradient(enabled=false);
}
