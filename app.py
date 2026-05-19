import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

import db
import tariff
from i18n import t
import seed_data
import demo_guide

db.init_db()
if db.get_device_count() == 0:
    seed_data.seed()

st.set_page_config(page_title="PowerWise Malaysia", page_icon="⚡", layout="wide")

household = db.get_household()
lang = household["language"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title(f"⚡ {t('app_title', lang)}")
st.sidebar.caption(t("app_caption", lang))

menu_items = [
    f"🏠 {t('menu_dashboard', lang)}",
    f"📝 {t('menu_enter_reading', lang)}",
    f"📊 {t('menu_usage_analysis', lang)}",
    f"🔌 {t('menu_appliance_savings', lang)}",
    f"⚙️ {t('menu_settings', lang)}",
]

# Demo guide controls which page is shown when active
demo_guide.init_demo_state()
demo_target = demo_guide.get_target_page()
default_index = demo_target if demo_target is not None else 0

page = st.sidebar.radio("Menu", menu_items, index=default_index, label_visibility="collapsed")

st.sidebar.divider()
st.sidebar.caption(t("budget_label", lang, amount=household["monthly_budget"]))
st.sidebar.caption(t("provider_label", lang, provider=household["provider"]))

# Demo guide
demo_guide.render_toggle(lang)
demo_guide.render_nav()

if st.sidebar.button("🔄 Reset Demo Data", help="Delete database and re-seed with demo data"):
    if os.path.exists(db.DB_PATH):
        os.remove(db.DB_PATH)
    db.init_db()
    seed_data.seed()
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == menu_items[0]:
    st.title(t("dashboard_title", lang))

    bills = db.get_bills()
    if not bills:
        st.info(t("no_bills_info", lang))
        st.stop()

    latest_bill = bills[0]
    budget = household["monthly_budget"]
    bill_amount = latest_bill["amount"]
    kwh = latest_bill["kwh_used"]

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric(t("latest_bill", lang), f"RM {bill_amount:.2f}", f"{kwh:.0f} kWh")
    col2.metric(t("monthly_budget", lang), f"RM {budget:.2f}")
    delta = bill_amount - budget
    col3.metric(
        t("budget_status", lang),
        t("budget_over", lang) if delta > 0 else t("budget_within", lang),
        f"RM {delta:+.2f}",
        delta_color="inverse",
    )

    # Budget alert
    if bill_amount > budget:
        st.error(f"⚠️ {t('budget_alert_over', lang, amount=bill_amount, delta=delta)}")
    elif bill_amount > budget * household["alert_threshold"]:
        pct = bill_amount / budget * 100
        st.warning(f"⚡ {t('budget_alert_warning', lang, pct=pct)}")
    else:
        st.success(f"✅ {t('budget_alert_ok', lang)}")

    # Bill history chart
    if len(bills) > 1:
        df_bills = pd.DataFrame(bills).sort_values("month")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_bills["month"], y=df_bills["amount"], name="Bill (RM)", marker_color="#22c55e"))
        fig.add_hline(y=budget, line_dash="dash", line_color="red",
                      annotation_text=t("budget_line_label", lang, amount=budget))
        fig.update_layout(title=t("monthly_bills_chart", lang), height=350, template="plotly_white",
                          margin=dict(t=40, b=30))
        st.plotly_chart(fig, width="stretch")

    # Tariff explanation
    with st.expander(f"💡 {t('understand_bill', lang)}"):
        bill_info = tariff.calculate_bill(kwh)
        st.write(tariff.format_bill_explanation(kwh, budget, lang))
        st.caption(t("tariff_caption", lang))
        for i, tier in enumerate(bill_info["tier_breakdown"], 1):
            st.caption(f"  {t('block_label', lang, i=i, kwh=tier['kwh'], rate=tier['rate'], cost=tier['cost'])}")


# ══════════════════════════════════════════════════════════════════════════════
# ENTER READING
# ══════════════════════════════════════════════════════════════════════════════
elif page == menu_items[1]:
    st.title(t("enter_reading_title", lang))

    dv = demo_guide.get_demo_values()
    tab1, tab2 = st.tabs([t("tab_bill", lang), t("tab_meter", lang)])

    with tab1:
        with st.form("bill_entry"):
            col1, col2 = st.columns(2)
            with col1:
                month = st.text_input(t("billing_month", lang),
                                      value=dv.get("bill_month", datetime.now().strftime("%Y-%m")),
                                      placeholder="2026-05")
            with col2:
                kwh = st.number_input(t("total_kwh", lang), min_value=0.0,
                                      value=dv.get("bill_kwh", 350.0), step=10.0)

            estimated = tariff.calculate_bill(kwh)
            st.info(t("estimated_bill", lang, kwh=kwh, amount=estimated["total"]))

            amount = st.number_input(t("bill_amount", lang), min_value=0.0, value=estimated["total"], step=1.0,
                                     help=t("bill_amount_help", lang))

            if st.form_submit_button(t("save_bill", lang)):
                db.add_bill(month, kwh, amount, "manual")
                budget = household["monthly_budget"]
                tier = tariff.get_tier_for_kwh(kwh)
                if amount > budget:
                    over = amount - budget
                    st.error(f"⚠️ {t('bill_over_budget', lang, amount=amount, budget=budget)}")
                    st.warning(t("bill_feedback_over", lang, over=over, kwh=kwh, tier=tier))
                else:
                    under = budget - amount
                    st.success(t("bill_saved", lang))
                    st.info(t("bill_feedback_under", lang, under=under, kwh=kwh, tier=tier))

    with tab2:
        st.caption(t("meter_caption", lang))
        with st.form("meter_entry"):
            reading_kwh = st.number_input(t("current_reading", lang), min_value=0.0, step=1.0)
            reading_date = st.date_input(t("reading_date", lang), value=datetime.now())

            devices = db.get_devices()
            if devices:
                device_options = {d["id"]: d["name"] for d in devices}
                device_id = st.selectbox(t("meter_select", lang), options=list(device_options.keys()),
                                         format_func=lambda x: device_options[x])
            else:
                st.caption(t("no_meters", lang))
                device_id = None

            if st.form_submit_button(t("save_reading", lang)):
                if device_id:
                    db.add_reading(device_id, reading_date.isoformat(), reading_kwh, 0.0, 0.0)
                st.success(t("reading_saved", lang))
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# USAGE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == menu_items[2]:
    st.title(t("usage_title", lang))

    bills = db.get_bills()
    devices = db.get_devices()

    if devices:
        all_readings = db.get_all_readings()
        if all_readings:
            df = pd.DataFrame(all_readings)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["hour"] = df["timestamp"].dt.hour

            st.subheader(t("daily_pattern", lang))
            hourly = df.groupby("hour")["power"].mean().reset_index()
            fig = go.Figure()
            colors = ["#ef4444" if p > hourly["power"].mean() * 1.3 else "#22c55e" for p in hourly["power"]]
            fig.add_trace(go.Bar(x=hourly["hour"], y=hourly["power"], marker_color=colors))
            fig.update_layout(
                xaxis_title=t("hour_label", lang), yaxis_title=t("avg_power_label", lang),
                height=300, template="plotly_white", margin=dict(t=20, b=30)
            )
            st.plotly_chart(fig, width="stretch")

            peak_hours = hourly.nlargest(3, "power")
            peak_labels = ", ".join([f"{int(h)}:00" for h in peak_hours["hour"]])
            avg_power = hourly["power"].mean()
            peak_power = peak_hours["power"].mean()

            st.info(f"📈 {t('peak_hours_info', lang, hours=peak_labels, ratio=peak_power / avg_power)}")

    if bills:
        st.subheader(t("recommendations_title", lang))
        latest = bills[0]
        kwh = latest["kwh_used"]
        tier = tariff.get_tier_for_kwh(kwh)

        recommendations = []
        if tier >= 3:
            recommendations.append((f"🌡️ {t('tip_ac_title', lang)}", t("tip_ac_body", lang), "RM 15-30"))
        if kwh > 400:
            recommendations.append((f"💡 {t('tip_lighting_title', lang)}", t("tip_lighting_body", lang), "RM 5-10"))
        if tier >= 2:
            recommendations.append((f"🔌 {t('tip_standby_title', lang)}", t("tip_standby_body", lang), "RM 8-15"))
        recommendations.append((f"⏰ {t('tip_offpeak_title', lang)}", t("tip_offpeak_body", lang), "RM 5-10"))

        if tier >= 4:
            st.warning(t("tier_warning", lang, tier=tier, savings=50 * 0.516))

        for title, tip, saving in recommendations:
            with st.container():
                col1, col2 = st.columns([4, 1])
                col1.markdown(f"**{title}**\n\n{tip}")
                col2.metric(t("potential_savings", lang), saving)
                st.divider()
    else:
        st.info(t("no_bills_for_tips", lang))


# ══════════════════════════════════════════════════════════════════════════════
# APPLIANCE SAVINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == menu_items[3]:
    st.title(t("appliance_title", lang))
    dv = demo_guide.get_demo_values()

    st.subheader(t("compare_title", lang))
    appliance_keys = list(tariff.APPLIANCE_DATABASE.keys())
    default_appliance_idx = appliance_keys.index(dv["appliance_type"]) if dv.get("appliance_type") in appliance_keys else 0

    col1, col2 = st.columns(2)
    with col1:
        appliance_type = st.selectbox(t("appliance_type", lang), options=appliance_keys,
                                      index=default_appliance_idx,
                                      format_func=lambda x: tariff.APPLIANCE_DATABASE[x]["label"])
    with col2:
        hours = st.slider(t("hours_per_day", lang), 1.0, 24.0, dv.get("hours", 8.0), 0.5)

    info = tariff.APPLIANCE_DATABASE[appliance_type]
    current_watts = st.number_input(t("your_power", lang),
                                    value=dv.get("current_watts", float(info["old_typical_watts"])),
                                    step=50.0, help=t("your_power_help", lang))

    comparison = tariff.compare_appliance(appliance_type, hours, current_watts)

    if comparison:
        st.divider()
        st.subheader(t("results_title", lang))

        col1, col2, col3 = st.columns(3)
        col1.metric(t("current_monthly", lang), f"RM {comparison['old_monthly_cost']:.2f}",
                    f"{comparison['old_monthly_kwh']} kWh")
        col2.metric(t("efficient_monthly", lang), f"RM {comparison['new_monthly_cost']:.2f}",
                    f"{comparison['new_monthly_kwh']} kWh")
        col3.metric(t("yearly_savings", lang), f"RM {comparison['yearly_savings']:.2f}",
                    t("kwh_saved", lang, kwh=comparison["savings_kwh"] * 12))

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=[comparison["old_label"], comparison["new_label"]],
            x=[comparison["old_monthly_cost"], comparison["new_monthly_cost"]],
            orientation="h",
            marker_color=["#ef4444", "#22c55e"],
            text=[f"RM {comparison['old_monthly_cost']:.2f}", f"RM {comparison['new_monthly_cost']:.2f}"],
            textposition="outside",
        ))
        fig.update_layout(
            xaxis_title="Monthly Cost (RM)", height=200, template="plotly_white",
            margin=dict(t=20, b=30, l=180), showlegend=False,
        )
        st.plotly_chart(fig, width="stretch")

    # Rebate info
    st.divider()
    st.subheader(t("rebates_title", lang))
    for rebate in tariff.REBATE_PROGRAMS:
        eligible = appliance_type in rebate["appliance_types"]
        with st.container():
            col1, col2 = st.columns([4, 1])
            col1.markdown(f"**{rebate['name']}** — {rebate['provider']}")
            col1.caption(rebate["description"])
            col1.caption(t("eligibility_label", lang, text=rebate["eligibility"]))
            if eligible:
                col2.success(f"✅ {t('eligible', lang)}" + (f"\nRM {rebate['amount']:.0f}" if rebate["amount"] > 0 else ""))
            else:
                col2.caption(t("not_applicable", lang))
            st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == menu_items[4]:
    st.title(t("settings_title", lang))
    dv = demo_guide.get_demo_values()

    lang_options = ["en", "ms"]
    default_lang_idx = lang_options.index(dv["language"]) if dv.get("language") in lang_options else (0 if household["language"] == "en" else 1)

    with st.form("settings"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(t("household_name", lang), value=household["household_name"])
            location = st.text_input(t("location", lang), value=household["location"])
            state = st.selectbox(t("state", lang), ["Selangor", "Kuala Lumpur", "Johor", "Penang", "Perak",
                                       "Sabah", "Sarawak", "Kedah", "Kelantan", "Melaka",
                                       "Negeri Sembilan", "Pahang", "Perlis", "Terengganu"],
                                 index=0 if household["state"] == "Selangor" else 0)
        with col2:
            provider = st.selectbox(t("electricity_provider", lang), ["TNB", "SESB", "SEB"],
                                    index=["TNB", "SESB", "SEB"].index(household["provider"]))
            size = st.number_input(t("household_size", lang), min_value=1, max_value=20,
                                   value=household["household_size"])
            budget = st.number_input(t("monthly_budget_input", lang), min_value=10.0,
                                     value=household["monthly_budget"], step=10.0)

        alert = st.slider(t("alert_threshold", lang), 50, 100, int(household["alert_threshold"] * 100),
                          help=t("alert_threshold_help", lang))
        language = st.selectbox(t("language", lang), lang_options, index=default_lang_idx,
                                format_func=lambda x: "English" if x == "en" else "Bahasa Malaysia")

        if st.form_submit_button(t("save_settings", lang)):
            db.update_household(
                household_name=name, location=location, state=state,
                provider=provider, household_size=size, monthly_budget=budget,
                alert_threshold=alert / 100, language=language
            )
            st.success(t("settings_saved", lang))
            st.rerun()

    # Device management
    st.divider()
    st.subheader(t("energy_meters", lang))
    devices = db.get_devices()
    if devices:
        for d in devices:
            col1, col2 = st.columns([4, 1])
            col1.text(f"{d['name']} — #{d['serial_number']} {'🟢' if d['connected'] else '🔴'}")
            if col2.button(t("delete_button", lang), key=f"del_{d['id']}"):
                db.delete_device(d["id"])
                st.rerun()

    with st.expander(t("add_meter", lang)):
        with st.form("add_meter"):
            c1, c2 = st.columns(2)
            name = c1.text_input(t("meter_name", lang), placeholder="Main Meter")
            serial = c2.text_input(t("serial_number", lang), placeholder="MY-2024-001")
            if st.form_submit_button(t("add_button", lang)):
                if name and serial:
                    db.add_device(name, serial)
                    st.rerun()

    # ── Privacy & Data Consent ────────────────────────────────────────────────
    st.divider()
    st.subheader(t("privacy_title", lang))

    consent = db.get_consent()

    st.info(t("data_collected_info", lang))

    with st.form("consent_form"):
        c_storage = st.checkbox(t("consent_data_storage", lang), value=bool(consent["consent_local_storage"]))
        c_sharing = st.checkbox(t("consent_sharing", lang), value=bool(consent["consent_sharing"]))
        c_analytics = st.checkbox(t("consent_analytics", lang), value=bool(consent["consent_analytics"]))

        if st.form_submit_button(t("consent_saved", lang).replace("!", "")):
            db.update_consent(c_storage, c_sharing, c_analytics)
            st.success(t("consent_saved", lang))
            st.rerun()

    with st.expander(t("data_rights_title", lang)):
        st.write(t("data_rights_info", lang))

        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("export_data", lang)):
                import json
                data = db.export_all_data()
                export_path = os.path.join(os.path.dirname(db.DB_PATH), "powerwise_export.json")
                with open(export_path, "w") as f:
                    json.dump(data, f, indent=2, default=str)
                st.success(t("export_success", lang, path=export_path))
        with col2:
            if st.button(t("delete_all_data", lang), type="primary"):
                db.delete_all_data()
                st.warning(t("delete_confirm", lang))
                st.rerun()

# ── Demo overlay (rendered last so it floats on top) ─────────────────────────
demo_guide.render_overlay()
