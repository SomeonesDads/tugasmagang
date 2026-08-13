-- DROP SCHEMA mba_sumbagut;

CREATE SCHEMA mba_sumbagut AUTHORIZATION robyput;

-- DROP SEQUENCE mba_sumbagut.daily_aggregate_id_seq;

CREATE SEQUENCE mba_sumbagut.daily_aggregate_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.daily_trends_id_seq;

CREATE SEQUENCE mba_sumbagut.daily_trends_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.feature_daily_id_seq;

CREATE SEQUENCE mba_sumbagut.feature_daily_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.feature_distribution_id_seq;

CREATE SEQUENCE mba_sumbagut.feature_distribution_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.feature_stats_id_seq;

CREATE SEQUENCE mba_sumbagut.feature_stats_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.incident_per15minutes_id_seq;

CREATE SEQUENCE mba_sumbagut.incident_per15minutes_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.kpi_summary_id_seq;

CREATE SEQUENCE mba_sumbagut.kpi_summary_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.model_feature_importance_id_seq;

CREATE SEQUENCE mba_sumbagut.model_feature_importance_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.model_metrics_id_seq;

CREATE SEQUENCE mba_sumbagut.model_metrics_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.model_scatter_id_seq;

CREATE SEQUENCE mba_sumbagut.model_scatter_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.scd_operators_id_seq;

CREATE SEQUENCE mba_sumbagut.scd_operators_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.scd_orders_id_seq;

CREATE SEQUENCE mba_sumbagut.scd_orders_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.scd_position_history_id_seq;

CREATE SEQUENCE mba_sumbagut.scd_position_history_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.scd_status_log_id_seq;

CREATE SEQUENCE mba_sumbagut.scd_status_log_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.shap_base_value_id_seq;

CREATE SEQUENCE mba_sumbagut.shap_base_value_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.shap_global_importance_id_seq;

CREATE SEQUENCE mba_sumbagut.shap_global_importance_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.shap_importance_by_departement_id_seq;

CREATE SEQUENCE mba_sumbagut.shap_importance_by_departement_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.shap_importance_by_kabupaten_id_seq;

CREATE SEQUENCE mba_sumbagut.shap_importance_by_kabupaten_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.shap_scatter_sample_id_seq;

CREATE SEQUENCE mba_sumbagut.shap_scatter_sample_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.site_avg_payload_id_seq;

CREATE SEQUENCE mba_sumbagut.site_avg_payload_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.site_feature_comparison_id_seq;

CREATE SEQUENCE mba_sumbagut.site_feature_comparison_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.site_forecast_id_seq;

CREATE SEQUENCE mba_sumbagut.site_forecast_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.site_forecast_summary_id_seq;

CREATE SEQUENCE mba_sumbagut.site_forecast_summary_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.site_list_id_seq;

CREATE SEQUENCE mba_sumbagut.site_list_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.site_map_data_id_seq;

CREATE SEQUENCE mba_sumbagut.site_map_data_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.site_payload_trend_id_seq;

CREATE SEQUENCE mba_sumbagut.site_payload_trend_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.site_reference_id_seq;

CREATE SEQUENCE mba_sumbagut.site_reference_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.site_shap_importance_id_seq;

CREATE SEQUENCE mba_sumbagut.site_shap_importance_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.site_slopes_id_seq;

CREATE SEQUENCE mba_sumbagut.site_slopes_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.site_spc_id_seq;

CREATE SEQUENCE mba_sumbagut.site_spc_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.spc_summary_id_seq;

CREATE SEQUENCE mba_sumbagut.spc_summary_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE mba_sumbagut.weekly_trends_id_seq;

CREATE SEQUENCE mba_sumbagut.weekly_trends_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;-- mba_sumbagut.bbt_sumbagut definition

-- Drop table

-- DROP TABLE mba_sumbagut.bbt_sumbagut;

CREATE TABLE mba_sumbagut.bbt_sumbagut (
	site_id text NULL,
	site_name text NULL,
	site_class text NULL,
	area text NULL,
	region text NULL,
	nop text NULL,
	"to" text NULL,
	vendor text NULL,
	bbt_max_duration float8 NULL,
	bbt_min_duration float8 NULL,
	bbt_median_duration float8 NULL,
	duration_mains_fail_low_batt float8 NULL,
	duration_mains_fail_first_ne_down float8 NULL,
	duration_mains_fail_last_ne_down float8 NULL,
	duration_low_batt_first_ne_down float8 NULL,
	duration_low_batt_last_ne_down float8 NULL,
	category text NULL,
	pln_down float8 NULL,
	backup_duration float8 NULL,
	ne_down float8 NULL,
	repetitive int8 NULL,
	category_1 text NULL,
	total_pln_down float8 NULL,
	total_battery_backups float8 NULL,
	total_ne_down float8 NULL,
	details text NULL
);
CREATE INDEX idx_bbt_sumbagut_site ON mba_sumbagut.bbt_sumbagut USING btree (site_id);


-- mba_sumbagut.bcp_drp_site_sumbagut definition

-- Drop table

-- DROP TABLE mba_sumbagut.bcp_drp_site_sumbagut;

CREATE TABLE mba_sumbagut.bcp_drp_site_sumbagut (
	"no" int8 NULL,
	siteid text NULL,
	site_name text NULL,
	tp_non_tp text NULL,
	nsa text NULL,
	kab_kota text NULL,
	provinsi text NULL,
	bcp_site_2022 text NULL,
	remarks_from_regional text NULL,
	category_area text NULL,
	coverage_cluster text NULL,
	cat_simpul float8 NULL
);


-- mba_sumbagut.cnop_intermediate definition

-- Drop table

-- DROP TABLE mba_sumbagut.cnop_intermediate;

CREATE TABLE mba_sumbagut.cnop_intermediate (
	"no" int8 NULL,
	uniq text NULL,
	order_date date NULL,
	nim text NULL,
	site_id_1 text NULL,
	site_id_2 text NULL,
	current_capacity_telkom_mbps int8 NULL,
	site_impacted int8 NULL,
	proposed_solution text NULL,
	telkomsel_region text NULL,
	reg_tsel text NULL,
	reg_telkom text NULL,
	input_date date NULL,
	"program" text NULL,
	mitra_final text NULL,
	milestone text NULL,
	inhand_date text NULL,
	l0_ready_date text NULL,
	oa_date text NULL,
	status_final text NULL,
	keterangan text NULL
);


-- mba_sumbagut.cnop_nim_2025 definition

-- Drop table

-- DROP TABLE mba_sumbagut.cnop_nim_2025;

CREATE TABLE mba_sumbagut.cnop_nim_2025 (
	"no" text NULL,
	cif int8 NULL,
	uniq text NULL,
	site_id text NULL,
	tipe text NULL,
	sow text NULL,
	site_name text NULL,
	lat text NULL,
	long text NULL,
	nim_order text NULL,
	reg_tsel text NULL,
	reg_telkom text NULL,
	bw_order int8 NULL,
	order_date text NULL,
	mitra text NULL,
	milestone text NULL,
	l0_ready_date text NULL,
	oa_date text NULL,
	kuota_implementasi text NULL,
	flag_kuota_fifo_oa text NULL,
	list_tif text NULL,
	program_ii text NULL,
	confirm_mitra text NULL,
	status_final text NULL,
	"program" text NULL,
	fiberisasi text NULL,
	billing_alpro_dec text NULL,
	billing_bw_dec text NULL,
	bw_actual_up_down numeric NULL,
	l0_ready_date_data_mso text NULL,
	l2_ready_date text NULL,
	oa_date_2 text NULL,
	status_final_tif text NULL,
	support_needed text NULL,
	detail text NULL,
	status_order_tsel text NULL
);


-- mba_sumbagut.cnop_nim_2026 definition

-- Drop table

-- DROP TABLE mba_sumbagut.cnop_nim_2026;

CREATE TABLE mba_sumbagut.cnop_nim_2026 (
	"no" int8 NULL,
	uniq text NULL,
	order_date date NULL,
	site_id text NULL,
	site_id_others text NULL,
	site_name text NULL,
	nim_order text NULL,
	"add" text NULL,
	sow_order text NULL,
	kuota_order text NULL,
	lat text NULL,
	long text NULL,
	reg_tsel text NULL,
	reg_telkom text NULL,
	bw_order numeric NULL,
	history_mitra_drop text NULL,
	mitra_final text NULL,
	milestone text NULL,
	inhand_date date NULL,
	l0_ready_date text NULL,
	oa_date text NULL,
	status_final text NULL,
	tematik_i text NULL,
	tematik_ii text NULL,
	note_issue text NULL,
	batch_mitra text NULL,
	keterangan text NULL,
	list_tif text NULL,
	billing_alpro text NULL,
	billing_bw text NULL,
	kuota_implementasi text NULL,
	tlk_tif text NULL,
	need text NULL,
	input_date date NULL,
	tp_owner text NULL,
	status_quota text NULL,
	bw_actual_up_down numeric NULL,
	l0_ready_date_data_mso text NULL,
	l2_ready_date text NULL,
	oa_date_2 text NULL,
	status_final_tif text NULL,
	support_needed text NULL,
	detail text NULL,
	nim_lama text NULL,
	jenis_perizinan text NULL,
	flagging text NULL,
	y text NULL,
	tracker text NULL
);


-- mba_sumbagut.cnop_upgrade_1g definition

-- Drop table

-- DROP TABLE mba_sumbagut.cnop_upgrade_1g;

CREATE TABLE mba_sumbagut.cnop_upgrade_1g (
	"no" text NULL,
	uniq text NULL,
	order_date date NULL,
	site_id text NULL,
	site_id_others text NULL,
	site_name text NULL,
	nim_order text NULL,
	sow_order text NULL,
	kuota_order text NULL,
	lat text NULL,
	long text NULL,
	reg_tsel text NULL,
	reg_telkom text NULL,
	bw_order int8 NULL,
	history_mitra_drop text NULL,
	mitra_final text NULL,
	milestone text NULL,
	inhand_date text NULL,
	l0_ready_date text NULL,
	oa_date text NULL,
	status_final text NULL,
	tematik_i text NULL,
	tematik_ii text NULL,
	note_issue text NULL,
	batch_mitra text NULL,
	keterangan text NULL,
	list_tif text NULL,
	billing_alpro text NULL,
	billing_bw numeric NULL,
	kuota_implementasi text NULL,
	analisa_upgrade_maxium_10g text NULL,
	analisa_upgrade_maxium_1g text NULL,
	input_date date NULL,
	area_tif text NULL,
	action_summary text NULL,
	xcek_5g text NULL,
	note_regional text NULL
);


-- mba_sumbagut.daily_ai_payload_report definition

-- Drop table

-- DROP TABLE mba_sumbagut.daily_ai_payload_report;

CREATE TABLE mba_sumbagut.daily_ai_payload_report (
	report_date date NOT NULL,
	"content" text NULL,
	generated_at timestamp DEFAULT now() NULL,
	model text NULL,
	CONSTRAINT daily_ai_payload_report_pkey PRIMARY KEY (report_date)
);


-- mba_sumbagut.daisy_claim_sumbagut definition

-- Drop table

-- DROP TABLE mba_sumbagut.daisy_claim_sumbagut;

CREATE TABLE mba_sumbagut.daisy_claim_sumbagut (
	"no" int8 NULL,
	nop_teritory text NULL,
	claim_no text NULL,
	site_id text NULL,
	site_name text NULL,
	bbt_sem1_2025 text NULL,
	bbt_sem2_2025 text NULL,
	bbt_q1_2026 text NULL,
	bbt_tier text NULL,
	event_date timestamp NULL,
	"month" text NULL,
	"year" int8 NULL,
	battery_materials text NULL,
	battery_qty int8 NULL,
	battery_item_count int8 NULL,
	has_battery bool NULL
);
CREATE INDEX idx_daisy_nop ON mba_sumbagut.daisy_claim_sumbagut USING btree (nop_teritory);
CREATE INDEX idx_daisy_site ON mba_sumbagut.daisy_claim_sumbagut USING btree (upper(site_id));
CREATE INDEX idx_daisy_year ON mba_sumbagut.daisy_claim_sumbagut USING btree (year);


-- mba_sumbagut.enom_shopping_list definition

-- Drop table

-- DROP TABLE mba_sumbagut.enom_shopping_list;

CREATE TABLE mba_sumbagut.enom_shopping_list (
	"no" int8 NULL,
	deskripsi text NULL,
	satuan text NULL,
	area1_price text NULL,
	area1_price_num float8 NULL,
	area1_remark text NULL,
	area3_price text NULL,
	area3_remark text NULL,
	remark text NULL
);


-- mba_sumbagut.high_cap_rip_summary definition

-- Drop table

-- DROP TABLE mba_sumbagut.high_cap_rip_summary;

CREATE TABLE mba_sumbagut.high_cap_rip_summary (
	site_id text NULL,
	site_name text NULL,
	bw_num int8 NULL,
	transport_type text NULL,
	kabupaten text NULL,
	nop text NULL,
	fege_median float8 NULL,
	fege_mean float8 NULL,
	fege_p75 float8 NULL,
	fege_p95 float8 NULL,
	fege_max int8 NULL,
	sample_count int8 NULL,
	utilization_p95 float8 NULL,
	utilization_p75 float8 NULL,
	utilization_category text NULL,
	latitude float8 NULL,
	longitude float8 NULL,
	updated_at timestamp NULL
);


-- mba_sumbagut.incident_per15minutes definition

-- Drop table

-- DROP TABLE mba_sumbagut.incident_per15minutes;

CREATE TABLE mba_sumbagut.incident_per15minutes (
	id serial4 NOT NULL,
	snapshot_time timestamp NOT NULL,
	kabupaten text NULL,
	nop text NULL,
	total int4 DEFAULT 0 NULL,
	site_down int4 DEFAULT 0 NULL,
	site_up int4 DEFAULT 0 NULL,
	power_down int4 DEFAULT 0 NULL,
	power_up int4 DEFAULT 0 NULL,
	is_drp bool DEFAULT false NULL,
	CONSTRAINT incident_per15minutes_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_incident_per15min_time ON mba_sumbagut.incident_per15minutes USING btree (snapshot_time);


-- mba_sumbagut.monthly_payload definition

-- Drop table

-- DROP TABLE mba_sumbagut.monthly_payload;

CREATE TABLE mba_sumbagut.monthly_payload (
	yearmonth int8 NULL,
	"month" text NULL,
	site_id varchar NULL,
	kabupaten varchar(100) NULL,
	departement_ns varchar(100) NULL,
	monthly_payload_mbyte numeric NULL,
	monthly_traffic_erl numeric NULL
);
CREATE INDEX idx_mp_kab ON mba_sumbagut.monthly_payload USING btree (kabupaten);
CREATE INDEX idx_mp_nop ON mba_sumbagut.monthly_payload USING btree (departement_ns);
CREATE INDEX idx_mp_site ON mba_sumbagut.monthly_payload USING btree (site_id);
CREATE INDEX idx_mp_ym ON mba_sumbagut.monthly_payload USING btree (yearmonth);


-- mba_sumbagut.pipeline_runs definition

-- Drop table

-- DROP TABLE mba_sumbagut.pipeline_runs;

CREATE TABLE mba_sumbagut.pipeline_runs (
	pipeline_run_id uuid NOT NULL,
	started_at timestamptz NOT NULL,
	completed_at timestamptz NULL,
	status varchar(20) DEFAULT 'running'::character varying NOT NULL,
	source_rows int4 NULL,
	total_sites int4 NULL,
	model_file varchar(255) NULL,
	model_trained_at varchar(50) NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT pipeline_runs_pkey PRIMARY KEY (pipeline_run_id)
);


-- mba_sumbagut.pm_daily_agg definition

-- Drop table

-- DROP TABLE mba_sumbagut.pm_daily_agg;

CREATE TABLE mba_sumbagut.pm_daily_agg (
	dt date NULL,
	ym text NULL,
	dow int4 NULL,
	hr int4 NULL,
	networkservice text NULL,
	severity text NULL,
	sla_status text NULL,
	rootcausecategory text NULL,
	rootcausecategorytier1 text NULL,
	site_class text NULL,
	sitename text NULL,
	site_kabupaten text NULL,
	alarmname text NULL,
	has_nossa text NULL,
	ticket_status text NULL,
	cnt int8 NULL,
	cnt_mttr int8 NULL,
	sum_mttr_hrs float8 NULL
);
CREATE INDEX idx_agg_dt_pm_daily_agg_new ON mba_sumbagut.pm_daily_agg USING btree (dt);
CREATE INDEX idx_agg_nop_pm_daily_agg_new ON mba_sumbagut.pm_daily_agg USING btree (networkservice);
CREATE INDEX idx_agg_ym_pm_daily_agg_new ON mba_sumbagut.pm_daily_agg USING btree (ym);


-- mba_sumbagut.pm_site_map definition

-- Drop table

-- DROP TABLE mba_sumbagut.pm_site_map;

CREATE TABLE mba_sumbagut.pm_site_map (
	site_id text NULL,
	dt date NULL,
	ym text NULL,
	severity text NULL,
	rootcausecategory text NULL,
	sla_status text NULL,
	networkservice text NULL,
	site_class text NULL,
	has_nossa text NULL,
	ticket_status text NULL,
	latitude float8 NULL,
	longitude float8 NULL,
	ref_kabupaten varchar(100) NULL,
	ref_nop varchar(100) NULL,
	ref_site_name varchar(255) NULL,
	cnt int8 NULL,
	avg_mttr_hours float8 NULL
);
CREATE INDEX idx_map_dt_pm_site_map_new ON mba_sumbagut.pm_site_map USING btree (dt);
CREATE INDEX idx_map_sid_pm_site_map_new ON mba_sumbagut.pm_site_map USING btree (site_id);
CREATE INDEX idx_map_ym_pm_site_map_new ON mba_sumbagut.pm_site_map USING btree (ym);


-- mba_sumbagut.potential_warranty_rectbatt definition

-- Drop table

-- DROP TABLE mba_sumbagut.potential_warranty_rectbatt;

CREATE TABLE mba_sumbagut.potential_warranty_rectbatt (
	site_id_impl text NULL,
	site_name_impl text NULL,
	config_requirement text NULL,
	existing_config text NULL,
	final_config_1 text NULL,
	install_wip timestamp NULL,
	bast timestamp NULL,
	mitra text NULL,
	brand_rectifier text NULL,
	type_battery text NULL
);
CREATE INDEX idx_potential_warranty_rectbatt_site ON mba_sumbagut.potential_warranty_rectbatt USING btree (site_id_impl);


-- mba_sumbagut.power_operation_data definition

-- Drop table

-- DROP TABLE mba_sumbagut.power_operation_data;

CREATE TABLE mba_sumbagut.power_operation_data (
	site_id text NULL,
	general_info_site_name text NULL,
	general_info_class_site text NULL,
	general_info_type_site text NULL,
	general_info_nsa_nop text NULL,
	general_info_main_power text NULL,
	general_info_tot_phase text NULL,
	general_info_daya_pln float8 NULL,
	general_info_site_owner text NULL,
	asset_info_rtpe_tot_rect float8 NULL,
	asset_info_rtpe_rect_type text NULL,
	asset_info_rtpe_status_rect text NULL,
	asset_info_rtpe_tot_modul float8 NULL,
	asset_info_rtpe_tot_baterai float8 NULL,
	total_system_tot_daya_a float8 NULL,
	total_system_tot_module float8 NULL,
	total_system_tot_battery float8 NULL,
	lithium_tot_daya_a float8 NULL,
	lithium_tot_module float8 NULL,
	lithium_tot_battery float8 NULL,
	vrla_tot_daya_a float8 NULL,
	vrla_tot_module float8 NULL,
	vrla_tot_battery float8 NULL,
	cdc_tot_daya_a float8 NULL,
	cdc_tot_module float8 NULL,
	cdc_tot_battery float8 NULL,
	system_1_rect_type text NULL,
	system_1_module_type text NULL,
	system_1_rect_config text NULL,
	system_1_tot_module text NULL,
	system_1_tot_battery text NULL,
	system_1_load_recti text NULL,
	system_1_status text NULL,
	system_1_battery_type text NULL,
	system_1_battery_merek text NULL,
	system_1_battery_status text NULL,
	system_1_install_date text NULL,
	system_2_rect_type text NULL,
	system_2_module_type text NULL,
	system_2_rect_config text NULL,
	system_2_tot_module text NULL,
	system_2_tot_battery text NULL,
	system_2_load_recti text NULL,
	system_2_status text NULL,
	system_2_battery_type text NULL,
	system_2_battery_merek text NULL,
	system_2_battery_status text NULL,
	system_2_install_date text NULL,
	system_3_rect_type text NULL,
	system_3_module_type text NULL,
	system_3_rect_config text NULL,
	system_3_tot_module text NULL,
	system_3_tot_battery text NULL,
	system_3_load_recti text NULL,
	system_3_status text NULL,
	system_3_battery_type text NULL,
	system_3_battery_merek text NULL,
	system_3_battery_status text NULL,
	system_3_install_date text NULL,
	system_4_rect_type text NULL,
	system_4_module_type text NULL,
	system_4_rect_config text NULL,
	system_4_tot_module text NULL,
	system_4_tot_battery text NULL,
	system_4_load_recti text NULL,
	system_4_battery_type text NULL,
	system_4_battery_merek text NULL,
	system_4_battery_status text NULL,
	system_4_install_date timestamp NULL,
	system_5_rect_type text NULL,
	system_5_module_type text NULL,
	system_5_rect_config text NULL,
	system_5_tot_module text NULL,
	system_5_tot_battery text NULL,
	system_5_load_recti text NULL,
	system_5_battery_type text NULL,
	system_5_battery_merek text NULL,
	system_5_battery_status text NULL,
	system_5_install_date timestamp NULL,
	hystory_update_diupdate_oleh_pic text NULL,
	hystory_update_tanggal_update timestamp NULL,
	hystory_update_bagian_yang_diupdate text NULL,
	po1_latest_po_num text NULL,
	po1_latest_po_date timestamp NULL,
	po1_latest_program_support text NULL,
	po1_latest_sow_po text NULL,
	po1_latest_config_po text NULL,
	po1_latest_include_battery text NULL,
	po1_latest_rect_type text NULL,
	po1_latest_battery_typr text NULL,
	po1_latest_tot_system float8 NULL,
	po1_latest_install_date text NULL
);


-- mba_sumbagut.power_operation_program definition

-- Drop table

-- DROP TABLE mba_sumbagut.power_operation_program;

CREATE TABLE mba_sumbagut.power_operation_program (
	po_category text NULL,
	site_id text NULL,
	po_year int8 NULL,
	po_status text NULL,
	vendor text NULL,
	regional text NULL,
	support_program text NULL,
	po_number int8 NULL,
	po_date timestamp NULL,
	po_due_date timestamp NULL,
	status_po text NULL,
	tp text NULL,
	"to" text NULL,
	nop text NULL,
	sow_id text NULL,
	site_po text NULL,
	site_name_po text NULL,
	site_id_actual text NULL,
	site_name_actual text NULL,
	sow_simple text NULL,
	sow_up text NULL,
	config_install text NULL,
	summary text NULL,
	remark_status text NULL,
	blocking_issue text NULL,
	rfs_date text NULL,
	week_rfs_date int8 NULL,
	time_plan text NULL,
	week_plan_oa text NULL,
	proposed_aca text NULL,
	target_deployment text NULL
);
CREATE INDEX idx_power_operation_program_po_year ON mba_sumbagut.power_operation_program USING btree (po_year);
CREATE INDEX idx_power_operation_program_site_actual ON mba_sumbagut.power_operation_program USING btree (site_id_actual);
CREATE INDEX idx_power_operation_program_site_id ON mba_sumbagut.power_operation_program USING btree (site_id);


-- mba_sumbagut.problem_management_incidents definition

-- Drop table

-- DROP TABLE mba_sumbagut.problem_management_incidents;

CREATE TABLE mba_sumbagut.problem_management_incidents (
	order_id text NOT NULL,
	alarm_start_time timestamp NULL,
	alarm_clear_time timestamp NULL,
	severity text NULL,
	sla_status text NULL,
	rootcausecategory text NULL,
	rootcausecategorytier1 text NULL,
	networkservice text NULL,
	site_class text NULL,
	sitename text NULL,
	site_kabupaten text NULL,
	alarmname text NULL,
	impactsitelist text NULL,
	nossa_number text NULL,
	synced_at timestamp DEFAULT now() NULL,
	CONSTRAINT problem_management_incidents_new_pkey1 PRIMARY KEY (order_id)
);
CREATE INDEX idx_pm_alarm_new ON mba_sumbagut.problem_management_incidents USING btree (alarm_start_time);
CREATE INDEX idx_pm_nop_new ON mba_sumbagut.problem_management_incidents USING btree (networkservice);
CREATE INDEX idx_pm_rc_new ON mba_sumbagut.problem_management_incidents USING btree (rootcausecategory);
CREATE INDEX idx_pm_sc_new ON mba_sumbagut.problem_management_incidents USING btree (site_class);
CREATE INDEX idx_pm_sev_new ON mba_sumbagut.problem_management_incidents USING btree (severity);


-- mba_sumbagut.problem_management_incidents_new definition

-- Drop table

-- DROP TABLE mba_sumbagut.problem_management_incidents_new;

CREATE TABLE mba_sumbagut.problem_management_incidents_new (

);


-- mba_sumbagut.rca_dataframe definition

-- Drop table

-- DROP TABLE mba_sumbagut.rca_dataframe;

CREATE TABLE mba_sumbagut.rca_dataframe (
	site_id text NULL,
	payload_mbyte_4g float8 NULL,
	total_payload_mbyte float8 NULL,
	total_traffic_erl float8 NULL,
	"date" date NULL,
	radio_network_availability_rate float8 NULL,
	call_setup_success_rate float8 NULL,
	user_downlink_throughput float8 NULL,
	user_uplink_throughput float8 NULL,
	cell_downlink_throughput float8 NULL,
	cell_uplink_throughput float8 NULL,
	ul_active_user_avg float8 NULL,
	dl_active_user_avg float8 NULL,
	dl_resource_block_utilizing_rate float8 NULL,
	ul_resource_block_utilizing_rate float8 NULL,
	average_cqi_rate float8 NULL,
	good_cqi_rate float8 NULL,
	jumlahalarm float8 NULL,
	total_durasi_menit float8 NULL,
	pct_alarm_muncul float8 NULL,
	avg_latency float8 NULL,
	avg_jitter float8 NULL,
	avg_pl float8 NULL,
	zero_traffic float8 NULL,
	zero_payload float8 NULL,
	avg_rsrp float8 NULL,
	bad_tile_count float8 NULL,
	bad_tile_score float8 NULL,
	total_call_count float8 NULL,
	bad_call_count_score float8 NULL,
	status_pl_bad int4 NULL,
	yearweek varchar(20) NULL
);
CREATE INDEX idx_rca_df_date ON mba_sumbagut.rca_dataframe USING btree (date);
CREATE INDEX idx_rca_df_site_date ON mba_sumbagut.rca_dataframe USING btree (site_id, date);


-- mba_sumbagut.rca_zp_worklist definition

-- Drop table

-- DROP TABLE mba_sumbagut.rca_zp_worklist;

CREATE TABLE mba_sumbagut.rca_zp_worklist (
	"date" date NOT NULL,
	ne_id varchar(50) NULL,
	site_id varchar(50) NULL,
	enodeb_id int4 NOT NULL,
	cell_id int4 NOT NULL,
	rca varchar(50) NULL,
	rca_detail varchar(50) NULL,
	updated_at timestamp DEFAULT now() NULL,
	CONSTRAINT rca_zp_worklist_pkey PRIMARY KEY (date, enodeb_id, cell_id)
);


-- mba_sumbagut.scd_operators definition

-- Drop table

-- DROP TABLE mba_sumbagut.scd_operators;

CREATE TABLE mba_sumbagut.scd_operators (
	id bigserial NOT NULL,
	telegram_id int8 NOT NULL,
	telegram_username varchar(100) NULL,
	operator_name varchar(200) NOT NULL,
	phone_number varchar(30) NOT NULL,
	scd_id varchar(50) NOT NULL,
	genset_capacity_kva float8 NULL,
	latitude float8 NULL,
	longitude float8 NULL,
	position_updated_at timestamptz NULL,
	status varchar(20) DEFAULT 'idle'::character varying NULL,
	is_active bool DEFAULT true NULL,
	registered_at timestamptz DEFAULT now() NOT NULL,
	updated_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT scd_operators_pkey PRIMARY KEY (id),
	CONSTRAINT scd_operators_scd_id_key UNIQUE (scd_id),
	CONSTRAINT scd_operators_telegram_id_key UNIQUE (telegram_id)
);
CREATE INDEX idx_scd_operators_scd_id ON mba_sumbagut.scd_operators USING btree (scd_id);
CREATE INDEX idx_scd_operators_status ON mba_sumbagut.scd_operators USING btree (status);
CREATE INDEX idx_scd_operators_tg ON mba_sumbagut.scd_operators USING btree (telegram_id);


-- mba_sumbagut.site_forecast definition

-- Drop table

-- DROP TABLE mba_sumbagut.site_forecast;

CREATE TABLE mba_sumbagut.site_forecast (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	site_id varchar(50) NOT NULL,
	forecast_date date NOT NULL,
	predicted_payload float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT site_forecast_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_site_forecast_run ON mba_sumbagut.site_forecast USING btree (pipeline_run_id, site_id);


-- mba_sumbagut.site_forecast_summary definition

-- Drop table

-- DROP TABLE mba_sumbagut.site_forecast_summary;

CREATE TABLE mba_sumbagut.site_forecast_summary (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	site_id varchar(50) NOT NULL,
	current_trend varchar(20) NULL,
	predicted_trend varchar(30) NULL,
	days_to_ucl int4 NULL,
	days_to_lcl int4 NULL,
	forecast_max float8 NULL,
	forecast_min float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT site_forecast_summary_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_site_forecast_summary_run ON mba_sumbagut.site_forecast_summary USING btree (pipeline_run_id);


-- mba_sumbagut.site_zpzt_baseline definition

-- Drop table

-- DROP TABLE mba_sumbagut.site_zpzt_baseline;

CREATE TABLE mba_sumbagut.site_zpzt_baseline (
	site_id varchar(10) NULL,
	remark varchar(15) NULL
);


-- mba_sumbagut.sri_zp_band_daily definition

-- Drop table

-- DROP TABLE mba_sumbagut.sri_zp_band_daily;

CREATE TABLE mba_sumbagut.sri_zp_band_daily (
	"source" varchar(15) NULL,
	"date" date NULL,
	regional varchar(10) NULL,
	vendor varchar(10) NULL,
	site_id varchar(10) NULL,
	band varchar(15) NULL,
	rbs_type varchar(10) NULL,
	sum_usage float4 NULL
);


-- mba_sumbagut.sri_zp_daily definition

-- Drop table

-- DROP TABLE mba_sumbagut.sri_zp_daily;

CREATE TABLE mba_sumbagut.sri_zp_daily (
	kategori varchar(15) NULL,
	"date" date NULL,
	yearweek int4 NULL,
	regional varchar(10) NULL,
	vendor varchar(10) NULL,
	ne_id varchar(50) NULL,
	site_id varchar(10) NULL,
	sector int4 NULL,
	cell_name varchar(100) NULL,
	enodeb_id int4 NULL,
	cell_id int4 NULL,
	band varchar(10) NULL,
	rbs_type bpchar(2) NULL,
	payload_total_gbyte float4 NULL,
	aging int4 NULL,
	rca varchar(50) NULL,
	rca_detail varchar(50) NULL,
	CONSTRAINT uq_zp UNIQUE (date, sector, cell_name, enodeb_id, cell_id, vendor, band, rbs_type)
);


-- mba_sumbagut.sri_zp_daily_bkp_20260710 definition

-- Drop table

-- DROP TABLE mba_sumbagut.sri_zp_daily_bkp_20260710;

CREATE TABLE mba_sumbagut.sri_zp_daily_bkp_20260710 (
	kategori varchar(15) NULL,
	"date" date NULL,
	yearweek int4 NULL,
	regional varchar(10) NULL,
	vendor varchar(10) NULL,
	ne_id varchar(50) NULL,
	site_id varchar(10) NULL,
	sector int4 NULL,
	cell_name varchar(100) NULL,
	enodeb_id int4 NULL,
	cell_id int4 NULL,
	band varchar(10) NULL,
	rbs_type bpchar(2) NULL,
	payload_total_gbyte float4 NULL
);


-- mba_sumbagut.sri_zp_daily_clean definition

-- Drop table

-- DROP TABLE mba_sumbagut.sri_zp_daily_clean;

CREATE TABLE mba_sumbagut.sri_zp_daily_clean (
	kategori varchar(15) NULL,
	"date" date NULL,
	yearweek int4 NULL,
	regional varchar(10) NULL,
	vendor varchar(10) NULL,
	ne_id varchar(50) NULL,
	site_id varchar(10) NULL,
	sector int4 NULL,
	cell_name varchar(100) NULL,
	enodeb_id int4 NULL,
	cell_id int4 NULL,
	band varchar(10) NULL,
	rbs_type bpchar(2) NULL,
	payload_total_gbyte float4 NULL,
	aging int4 NULL,
	rca varchar(50) NULL,
	rca_detail varchar(50) NULL
);


-- mba_sumbagut.sri_zt_band_daily definition

-- Drop table

-- DROP TABLE mba_sumbagut.sri_zt_band_daily;

CREATE TABLE mba_sumbagut.sri_zt_band_daily (
	"source" varchar(15) NULL,
	"date" date NULL,
	regional varchar(10) NULL,
	vendor varchar(10) NULL,
	site_id varchar(10) NULL,
	band varchar(15) NULL,
	rbs_type varchar(10) NULL,
	sum_usage float4 NULL
);


-- mba_sumbagut.sri_zt_daily definition

-- Drop table

-- DROP TABLE mba_sumbagut.sri_zt_daily;

CREATE TABLE mba_sumbagut.sri_zt_daily (
	kategori varchar(15) NULL,
	"date" date NULL,
	yearweek int4 NULL,
	regional varchar(10) NULL,
	vendor varchar(10) NULL,
	ne_id varchar(50) NULL,
	site_id varchar(10) NULL,
	sector int4 NULL,
	cell_name varchar(100) NULL,
	lac int4 NULL,
	ci int4 NULL,
	band varchar(10) NULL,
	rbs_type bpchar(2) NULL,
	traffic_total float4 NULL,
	aging int4 NULL
);


-- mba_sumbagut.sumbagut_radio_ip definition

-- Drop table

-- DROP TABLE mba_sumbagut.sumbagut_radio_ip;

CREATE TABLE mba_sumbagut.sumbagut_radio_ip (
	ne_fe_ownership text NULL,
	owner_po text NULL,
	hop text NULL,
	bw_cap_as_tput float8 NULL,
	bw_cap_as_plan float8 NULL,
	bw_cap_mw float8 NULL,
	bw_req_bw_actual text NULL,
	bw_usage_bw_actual text NULL,
	site_id_nearend text NULL,
	site_name_nearend text NULL,
	longitude_nearend float8 NULL,
	latitude_nearend float8 NULL,
	site_id_farend text NULL,
	site_name_farend text NULL,
	longitude_farend float8 NULL,
	latitude_farend float8 NULL,
	distance float8 NULL,
	area text NULL,
	type_ipmw text NULL,
	boq_type text NULL,
	"type" text NULL,
	freq text NULL,
	rau text NULL,
	cap text NULL,
	cap_tot int8 NULL,
	antenna text NULL,
	config text NULL,
	antenna_height_nearend text NULL,
	antenna_height_farend text NULL,
	isr_status text NULL,
	application_number text NULL,
	freq_nearend text NULL,
	freq_farend text NULL,
	idu_nearend text NULL,
	idu_farend text NULL,
	polarization text NULL,
	tx_power float8 NULL,
	radio_id_ne text NULL,
	radio_id_fe text NULL,
	status_link text NULL,
	info_trm text NULL,
	oa_date timestamp NULL,
	remarks text NULL,
	"comment" text NULL
);
CREATE INDEX idx_sumbagut_radio_ip_far ON mba_sumbagut.sumbagut_radio_ip USING btree (site_id_farend);
CREATE INDEX idx_sumbagut_radio_ip_near ON mba_sumbagut.sumbagut_radio_ip USING btree (site_id_nearend);
CREATE INDEX idx_sumbagut_radio_ip_usage ON mba_sumbagut.sumbagut_radio_ip USING btree (bw_usage_bw_actual);


-- mba_sumbagut.thi_data_transport_sumbagut definition

-- Drop table

-- DROP TABLE mba_sumbagut.thi_data_transport_sumbagut;

CREATE TABLE mba_sumbagut.thi_data_transport_sumbagut (
	siteid text NULL,
	site_name text NULL,
	check_payload float8 NULL,
	status_site text NULL,
	transport_type text NULL,
	hub_type text NULL,
	jumlah_anakan float8 NULL,
	simpul_ujung text NULL,
	linkroute text NULL,
	hop_1 text NULL,
	hop_2 text NULL,
	hop_3 text NULL,
	hop_4 text NULL,
	hop_5 text NULL,
	hop_6 text NULL,
	hop_7 text NULL,
	final_remark text NULL,
	detail text NULL,
	status text NULL,
	sow text NULL,
	order_nim___program text NULL,
	"order" text NULL,
	kabupaten text NULL,
	nop text NULL,
	cluster_to text NULL,
	bw text NULL,
	updated_at timestamp NULL,
	updated_by text NULL,
	comment_root_cause text NULL,
	bw_num int4 NULL,
	bw_num_manual bool DEFAULT false NULL
);


-- mba_sumbagut.weekly_thi_pipeline definition

-- Drop table

-- DROP TABLE mba_sumbagut.weekly_thi_pipeline;

CREATE TABLE mba_sumbagut.weekly_thi_pipeline (
	site_id varchar(50) NULL,
	site_name varchar(255) NULL,
	latitude float8 NULL,
	longitude float8 NULL,
	kabupaten varchar(100) NULL,
	departement_ns varchar(100) NULL,
	trend varchar(20) NULL,
	avg_payload float8 NULL,
	slope float8 NULL,
	sparkline text NULL,
	spc_mean float8 NULL,
	spc_ucl float8 NULL,
	spc_lcl float8 NULL,
	predicted_trend varchar(30) NULL,
	pipeline_run_id uuid NULL,
	vendor text NULL,
	transport_type text NULL,
	pl_status text NULL,
	lat_status text NULL,
	thi_status text NULL,
	thi_week int8 NULL,
	hub_type text NULL,
	jumlah_anakan float8 NULL,
	simpul_ujung text NULL,
	linkroute text NULL,
	hop_1 text NULL,
	hop_2 text NULL,
	hop_3 text NULL,
	hop_4 text NULL,
	hop_5 text NULL,
	hop_6 text NULL,
	hop_7 text NULL,
	final_remark text NULL,
	transport_detail text NULL,
	transport_status text NULL,
	sow text NULL,
	order_nim___program text NULL,
	transport_kabupaten text NULL,
	nop text NULL,
	cluster_to text NULL,
	bw text NULL,
	check_payload float8 NULL,
	status_site text NULL
);


-- mba_sumbagut.worst_thi_history definition

-- Drop table

-- DROP TABLE mba_sumbagut.worst_thi_history;

CREATE TABLE mba_sumbagut.worst_thi_history (
	site_id varchar(50) NOT NULL,
	week int4 NOT NULL,
	pl_status varchar(10) NULL,
	lat_status varchar(10) NULL,
	thi_status varchar(10) NULL,
	CONSTRAINT worst_thi_history_pkey PRIMARY KEY (site_id, week)
);
CREATE INDEX idx_worst_thi_history_week ON mba_sumbagut.worst_thi_history USING btree (week);


-- mba_sumbagut.worst_thi_summary definition

-- Drop table

-- DROP TABLE mba_sumbagut.worst_thi_summary;

CREATE TABLE mba_sumbagut.worst_thi_summary (
	site_id varchar(50) NOT NULL,
	site_name varchar(200) NULL,
	kabupaten varchar(100) NULL,
	departement_ns varchar(100) NULL,
	transport_type varchar(50) NULL,
	vendor varchar(50) NULL,
	pl_status varchar(10) NULL,
	lat_status varchar(10) NULL,
	thi_status varchar(10) NULL,
	worst_thi bool DEFAULT false NULL,
	worst_pl bool DEFAULT false NULL,
	worst_lat bool DEFAULT false NULL,
	latest_week int4 NULL,
	updated_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT worst_thi_summary_pkey PRIMARY KEY (site_id)
);
CREATE INDEX idx_worst_thi_summary_dept ON mba_sumbagut.worst_thi_summary USING btree (departement_ns);
CREATE INDEX idx_worst_thi_summary_kab ON mba_sumbagut.worst_thi_summary USING btree (kabupaten);
CREATE INDEX idx_worst_thi_summary_thi ON mba_sumbagut.worst_thi_summary USING btree (thi_status);


-- mba_sumbagut.daily_aggregate definition

-- Drop table

-- DROP TABLE mba_sumbagut.daily_aggregate;

CREATE TABLE mba_sumbagut.daily_aggregate (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	"date" date NOT NULL,
	mean_payload float8 NULL,
	mean_4g float8 NULL,
	mean_traffic float8 NULL,
	active_sites int4 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT daily_aggregate_pkey PRIMARY KEY (id),
	CONSTRAINT daily_aggregate_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_daily_agg_run ON mba_sumbagut.daily_aggregate USING btree (pipeline_run_id);


-- mba_sumbagut.daily_trends definition

-- Drop table

-- DROP TABLE mba_sumbagut.daily_trends;

CREATE TABLE mba_sumbagut.daily_trends (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	"period" date NOT NULL,
	mean_payload float8 NULL,
	median_payload float8 NULL,
	std_payload float8 NULL,
	sum_payload float8 NULL,
	mean_4g float8 NULL,
	mean_traffic float8 NULL,
	active_sites int4 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT daily_trends_pkey PRIMARY KEY (id),
	CONSTRAINT daily_trends_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_daily_trends_run ON mba_sumbagut.daily_trends USING btree (pipeline_run_id);


-- mba_sumbagut.feature_daily definition

-- Drop table

-- DROP TABLE mba_sumbagut.feature_daily;

CREATE TABLE mba_sumbagut.feature_daily (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	"date" date NOT NULL,
	feature_name varchar(100) NOT NULL,
	feat_mean float8 NULL,
	feat_median float8 NULL,
	feat_std float8 NULL,
	payload_mean float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT feature_daily_pkey PRIMARY KEY (id),
	CONSTRAINT feature_daily_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_feat_daily_run ON mba_sumbagut.feature_daily USING btree (pipeline_run_id, feature_name);


-- mba_sumbagut.feature_distribution definition

-- Drop table

-- DROP TABLE mba_sumbagut.feature_distribution;

CREATE TABLE mba_sumbagut.feature_distribution (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	feature_name varchar(100) NOT NULL,
	bin_edge float8 NULL,
	count int4 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT feature_distribution_pkey PRIMARY KEY (id),
	CONSTRAINT feature_distribution_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_feat_dist_run ON mba_sumbagut.feature_distribution USING btree (pipeline_run_id, feature_name);


-- mba_sumbagut.feature_stats definition

-- Drop table

-- DROP TABLE mba_sumbagut.feature_stats;

CREATE TABLE mba_sumbagut.feature_stats (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	feature_name varchar(100) NOT NULL,
	mean float8 NULL,
	std float8 NULL,
	min float8 NULL,
	max float8 NULL,
	median float8 NULL,
	correlation_with_target float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT feature_stats_pkey PRIMARY KEY (id),
	CONSTRAINT feature_stats_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_feat_stats_run ON mba_sumbagut.feature_stats USING btree (pipeline_run_id);


-- mba_sumbagut.kpi_summary definition

-- Drop table

-- DROP TABLE mba_sumbagut.kpi_summary;

CREATE TABLE mba_sumbagut.kpi_summary (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	total_sites int4 NULL,
	total_rows int4 NULL,
	avg_payload float8 NULL,
	avg_payload_4g float8 NULL,
	avg_traffic float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT kpi_summary_pkey PRIMARY KEY (id),
	CONSTRAINT kpi_summary_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);


-- mba_sumbagut.model_feature_importance definition

-- Drop table

-- DROP TABLE mba_sumbagut.model_feature_importance;

CREATE TABLE mba_sumbagut.model_feature_importance (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	feature_name varchar(100) NOT NULL,
	importance float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT model_feature_importance_pkey PRIMARY KEY (id),
	CONSTRAINT model_feature_importance_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_model_fi_run ON mba_sumbagut.model_feature_importance USING btree (pipeline_run_id);


-- mba_sumbagut.model_metrics definition

-- Drop table

-- DROP TABLE mba_sumbagut.model_metrics;

CREATE TABLE mba_sumbagut.model_metrics (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	r2 float8 NULL,
	rmse float8 NULL,
	mae float8 NULL,
	mape float8 NULL,
	train_size int4 NULL,
	test_size int4 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT model_metrics_pkey PRIMARY KEY (id),
	CONSTRAINT model_metrics_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);


-- mba_sumbagut.model_scatter definition

-- Drop table

-- DROP TABLE mba_sumbagut.model_scatter;

CREATE TABLE mba_sumbagut.model_scatter (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	actual float8 NULL,
	predicted float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT model_scatter_pkey PRIMARY KEY (id),
	CONSTRAINT model_scatter_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_model_scatter_run ON mba_sumbagut.model_scatter USING btree (pipeline_run_id);


-- mba_sumbagut.scd_orders definition

-- Drop table

-- DROP TABLE mba_sumbagut.scd_orders;

CREATE TABLE mba_sumbagut.scd_orders (
	id bigserial NOT NULL,
	order_number varchar(50) NOT NULL,
	site_id varchar(50) NOT NULL,
	site_name varchar(255) NULL,
	site_latitude float8 NULL,
	site_longitude float8 NULL,
	operator_id int8 NULL,
	status varchar(30) DEFAULT 'created'::character varying NULL,
	priority varchar(10) DEFAULT 'normal'::character varying NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	assigned_at timestamptz NULL,
	accepted_at timestamptz NULL,
	clock_in_at timestamptz NULL,
	arrived_at timestamptz NULL,
	activated_at timestamptz NULL,
	completed_at timestamptz NULL,
	notes text NULL,
	photo_url text NULL,
	CONSTRAINT scd_orders_order_number_key UNIQUE (order_number),
	CONSTRAINT scd_orders_pkey PRIMARY KEY (id),
	CONSTRAINT scd_orders_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES mba_sumbagut.scd_operators(id)
);
CREATE INDEX idx_scd_orders_operator ON mba_sumbagut.scd_orders USING btree (operator_id);
CREATE INDEX idx_scd_orders_site ON mba_sumbagut.scd_orders USING btree (site_id);
CREATE INDEX idx_scd_orders_status ON mba_sumbagut.scd_orders USING btree (status);


-- mba_sumbagut.scd_position_history definition

-- Drop table

-- DROP TABLE mba_sumbagut.scd_position_history;

CREATE TABLE mba_sumbagut.scd_position_history (
	id bigserial NOT NULL,
	operator_id int8 NOT NULL,
	latitude float8 NOT NULL,
	longitude float8 NOT NULL,
	recorded_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT scd_position_history_pkey PRIMARY KEY (id),
	CONSTRAINT scd_position_history_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES mba_sumbagut.scd_operators(id)
);
CREATE INDEX idx_scd_pos_hist_op ON mba_sumbagut.scd_position_history USING btree (operator_id, recorded_at DESC);


-- mba_sumbagut.scd_status_log definition

-- Drop table

-- DROP TABLE mba_sumbagut.scd_status_log;

CREATE TABLE mba_sumbagut.scd_status_log (
	id bigserial NOT NULL,
	order_id int8 NULL,
	operator_id int8 NULL,
	old_status varchar(30) NULL,
	new_status varchar(30) NOT NULL,
	changed_by varchar(100) NULL,
	notes text NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT scd_status_log_pkey PRIMARY KEY (id),
	CONSTRAINT scd_status_log_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES mba_sumbagut.scd_operators(id),
	CONSTRAINT scd_status_log_order_id_fkey FOREIGN KEY (order_id) REFERENCES mba_sumbagut.scd_orders(id)
);
CREATE INDEX idx_scd_log_order ON mba_sumbagut.scd_status_log USING btree (order_id);


-- mba_sumbagut.shap_base_value definition

-- Drop table

-- DROP TABLE mba_sumbagut.shap_base_value;

CREATE TABLE mba_sumbagut.shap_base_value (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	base_value float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT shap_base_value_pkey PRIMARY KEY (id),
	CONSTRAINT shap_base_value_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);


-- mba_sumbagut.shap_global_importance definition

-- Drop table

-- DROP TABLE mba_sumbagut.shap_global_importance;

CREATE TABLE mba_sumbagut.shap_global_importance (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	feature_name varchar(100) NOT NULL,
	mean_abs_shap float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	mean_shap float8 NULL,
	CONSTRAINT shap_global_importance_pkey PRIMARY KEY (id),
	CONSTRAINT shap_global_importance_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_shap_global_run ON mba_sumbagut.shap_global_importance USING btree (pipeline_run_id);


-- mba_sumbagut.shap_importance_by_departement definition

-- Drop table

-- DROP TABLE mba_sumbagut.shap_importance_by_departement;

CREATE TABLE mba_sumbagut.shap_importance_by_departement (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	departement_ns varchar(100) NOT NULL,
	feature_name varchar(100) NOT NULL,
	mean_abs_shap float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	mean_shap float8 NULL,
	CONSTRAINT shap_importance_by_departement_pkey PRIMARY KEY (id),
	CONSTRAINT shap_importance_by_departement_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_shap_dept_run ON mba_sumbagut.shap_importance_by_departement USING btree (pipeline_run_id, departement_ns);


-- mba_sumbagut.shap_importance_by_kabupaten definition

-- Drop table

-- DROP TABLE mba_sumbagut.shap_importance_by_kabupaten;

CREATE TABLE mba_sumbagut.shap_importance_by_kabupaten (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	kabupaten varchar(100) NOT NULL,
	feature_name varchar(100) NOT NULL,
	mean_abs_shap float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	mean_shap float8 NULL,
	CONSTRAINT shap_importance_by_kabupaten_pkey PRIMARY KEY (id),
	CONSTRAINT shap_importance_by_kabupaten_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_shap_kab_run ON mba_sumbagut.shap_importance_by_kabupaten USING btree (pipeline_run_id, kabupaten);


-- mba_sumbagut.shap_scatter_sample definition

-- Drop table

-- DROP TABLE mba_sumbagut.shap_scatter_sample;

CREATE TABLE mba_sumbagut.shap_scatter_sample (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	feature_name varchar(100) NOT NULL,
	shap_value float8 NULL,
	feature_value float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT shap_scatter_sample_pkey PRIMARY KEY (id),
	CONSTRAINT shap_scatter_sample_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_shap_scatter_run ON mba_sumbagut.shap_scatter_sample USING btree (pipeline_run_id, feature_name);


-- mba_sumbagut.site_avg_payload definition

-- Drop table

-- DROP TABLE mba_sumbagut.site_avg_payload;

CREATE TABLE mba_sumbagut.site_avg_payload (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	site_id varchar(50) NOT NULL,
	avg_payload float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT site_avg_payload_pkey PRIMARY KEY (id),
	CONSTRAINT site_avg_payload_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_site_avg_run ON mba_sumbagut.site_avg_payload USING btree (pipeline_run_id);


-- mba_sumbagut.site_feature_comparison definition

-- Drop table

-- DROP TABLE mba_sumbagut.site_feature_comparison;

CREATE TABLE mba_sumbagut.site_feature_comparison (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	site_id varchar(50) NOT NULL,
	feature_name varchar(100) NOT NULL,
	site_mean float8 NULL,
	global_mean float8 NULL,
	shap_importance float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	shap_signed float8 NULL,
	CONSTRAINT site_feature_comparison_pkey PRIMARY KEY (id),
	CONSTRAINT site_feature_comparison_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_site_feat_cmp_run ON mba_sumbagut.site_feature_comparison USING btree (pipeline_run_id, site_id);


-- mba_sumbagut.site_list definition

-- Drop table

-- DROP TABLE mba_sumbagut.site_list;

CREATE TABLE mba_sumbagut.site_list (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	site_id varchar(50) NOT NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT site_list_pkey PRIMARY KEY (id),
	CONSTRAINT site_list_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_site_list_run ON mba_sumbagut.site_list USING btree (pipeline_run_id);


-- mba_sumbagut.site_map_data definition

-- Drop table

-- DROP TABLE mba_sumbagut.site_map_data;

CREATE TABLE mba_sumbagut.site_map_data (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	site_id varchar(50) NOT NULL,
	site_name varchar(255) NULL,
	longitude float8 NULL,
	latitude float8 NULL,
	kabupaten varchar(100) NULL,
	departement_ns varchar(100) NULL,
	slope float8 NULL,
	avg_payload float8 NULL,
	data_points int4 NULL,
	trend varchar(20) NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	sparkline text NULL,
	spc_mean float8 NULL,
	spc_ucl float8 NULL,
	spc_lcl float8 NULL,
	predicted_trend varchar(30) NULL,
	CONSTRAINT site_map_data_pkey PRIMARY KEY (id),
	CONSTRAINT site_map_data_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_site_map_run ON mba_sumbagut.site_map_data USING btree (pipeline_run_id);


-- mba_sumbagut.site_payload_trend definition

-- Drop table

-- DROP TABLE mba_sumbagut.site_payload_trend;

CREATE TABLE mba_sumbagut.site_payload_trend (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	site_id varchar(50) NOT NULL,
	"date" date NOT NULL,
	payload float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT site_payload_trend_pkey PRIMARY KEY (id),
	CONSTRAINT site_payload_trend_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_site_payload_run ON mba_sumbagut.site_payload_trend USING btree (pipeline_run_id, site_id);


-- mba_sumbagut.site_reference definition

-- Drop table

-- DROP TABLE mba_sumbagut.site_reference;

CREATE TABLE mba_sumbagut.site_reference (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	site_id varchar(50) NOT NULL,
	site_name varchar(255) NULL,
	longitude float8 NULL,
	latitude float8 NULL,
	kecamatan varchar(100) NULL,
	kabupaten varchar(100) NULL,
	region varchar(50) NULL,
	departement_ns varchar(100) NULL,
	district_operation_do varchar(100) NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT site_reference_pkey PRIMARY KEY (id),
	CONSTRAINT site_reference_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_site_ref_run ON mba_sumbagut.site_reference USING btree (pipeline_run_id);


-- mba_sumbagut.site_shap_importance definition

-- Drop table

-- DROP TABLE mba_sumbagut.site_shap_importance;

CREATE TABLE mba_sumbagut.site_shap_importance (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	site_id varchar(50) NOT NULL,
	feature_name varchar(100) NOT NULL,
	mean_abs_shap float8 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	mean_shap float8 NULL,
	CONSTRAINT site_shap_importance_pkey PRIMARY KEY (id),
	CONSTRAINT site_shap_importance_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_site_shap_run ON mba_sumbagut.site_shap_importance USING btree (pipeline_run_id, site_id);


-- mba_sumbagut.site_slopes definition

-- Drop table

-- DROP TABLE mba_sumbagut.site_slopes;

CREATE TABLE mba_sumbagut.site_slopes (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	site_id varchar(50) NOT NULL,
	slope float8 NULL,
	avg_payload float8 NULL,
	data_points int4 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT site_slopes_pkey PRIMARY KEY (id),
	CONSTRAINT site_slopes_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_site_slopes_run ON mba_sumbagut.site_slopes USING btree (pipeline_run_id);


-- mba_sumbagut.site_spc definition

-- Drop table

-- DROP TABLE mba_sumbagut.site_spc;

CREATE TABLE mba_sumbagut.site_spc (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	site_id varchar(50) NOT NULL,
	mean_payload float8 NULL,
	std_payload float8 NULL,
	ucl float8 NULL,
	lcl float8 NULL,
	recent_avg float8 NULL,
	trend varchar(20) NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	recent_avg_all float8 NULL,
	zero_days int4 DEFAULT 0 NULL,
	zero_ratio float8 DEFAULT 0 NULL,
	CONSTRAINT site_spc_pkey PRIMARY KEY (id),
	CONSTRAINT site_spc_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_site_spc_run ON mba_sumbagut.site_spc USING btree (pipeline_run_id);


-- mba_sumbagut.spc_summary definition

-- Drop table

-- DROP TABLE mba_sumbagut.spc_summary;

CREATE TABLE mba_sumbagut.spc_summary (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	total int4 NULL,
	uptrend int4 NULL,
	downtrend int4 NULL,
	"stable" int4 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT spc_summary_pkey PRIMARY KEY (id),
	CONSTRAINT spc_summary_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);


-- mba_sumbagut.weekly_trends definition

-- Drop table

-- DROP TABLE mba_sumbagut.weekly_trends;

CREATE TABLE mba_sumbagut.weekly_trends (
	id bigserial NOT NULL,
	pipeline_run_id uuid NOT NULL,
	"period" date NOT NULL,
	mean_payload float8 NULL,
	median_payload float8 NULL,
	std_payload float8 NULL,
	sum_payload float8 NULL,
	mean_4g float8 NULL,
	mean_traffic float8 NULL,
	active_sites int4 NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT weekly_trends_pkey PRIMARY KEY (id),
	CONSTRAINT weekly_trends_pipeline_run_id_fkey FOREIGN KEY (pipeline_run_id) REFERENCES mba_sumbagut.pipeline_runs(pipeline_run_id)
);
CREATE INDEX idx_weekly_trends_run ON mba_sumbagut.weekly_trends USING btree (pipeline_run_id);
