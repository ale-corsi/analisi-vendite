import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(
    page_title="Analisi Performance Tag",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Analisi Performance Tag - Vendite")
st.markdown("Carica il file CSV per analizzare quali tag performano meglio")

# Definizione dei periodi disponibili
PERIODS = {
    "Ultimi 30 GG": 0,
    "Ultimi 60 GG": 1,
    "Ultimi 90 GG": 2,
    "90 precedenti [180-91]": 3,
    "90 precedenti [270-181]": 4,
    "90 precedenti [360-271]": 5,
    "90 precedenti [470-361]": 6,
    "Ultimi 180": 7,
    "Ultimi 365 GG": 8
}

# Colonne per ogni periodo (9 colonne per periodo)
COLS_PER_PERIOD = 9
BASE_COLS = ['tag', 'type']


def parse_number(val):
    """Converte numeri con formato italiano o standard in float"""
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).strip()
    if val_str == '' or val_str == '0':
        return 0.0
    # Gestisce sia formato italiano (virgola) che standard (punto)
    val_str = val_str.replace(',', '.')
    try:
        return float(val_str)
    except:
        return 0.0


def load_multiperiod_data(file):
    """Carica il file CSV con dati multi-periodo"""
    # Leggi tutto il file
    df_raw = pd.read_csv(file, header=None)

    # La prima riga contiene i nomi dei periodi
    # La seconda riga contiene gli header delle colonne
    # I dati iniziano dalla terza riga

    # Estrai i dati (dalla riga 3 in poi, indice 2)
    data_rows = df_raw.iloc[2:].reset_index(drop=True)

    # Crea un dizionario per ogni periodo
    all_periods_data = {}

    for period_name, period_idx in PERIODS.items():
        # Calcola l'offset delle colonne per questo periodo
        # Le prime 2 colonne sono tag e type
        # Poi ogni periodo ha 9 colonne
        if period_idx == 0:
            col_start = 2  # Dopo tag e type
        else:
            col_start = 2 + (period_idx * COLS_PER_PERIOD)

        col_end = col_start + COLS_PER_PERIOD

        # Estrai le colonne per questo periodo
        period_df = pd.DataFrame()
        period_df['tag'] = data_rows.iloc[:, 0]
        period_df['type'] = data_rows.iloc[:, 1]

        # Mappa le colonne
        col_names = ['LEAD_TOCCATO', 'LEAD_PARLATO', 'CHIAMATA_PRENOTATA',
                     'perc_prenotati_su_toccati', 'SESSIONE_SVOLTA', 'perc_chiuse_su_svolte',
                     'SESSIONE_VENDUTO', 'CHIUSURA_PAY_VALIDA', 'perc_chiuse_pay_su_toccati']

        for i, col_name in enumerate(col_names):
            if col_start + i < len(data_rows.columns):
                period_df[col_name] = data_rows.iloc[:, col_start + i].apply(parse_number)
            else:
                period_df[col_name] = 0

        # Rimuovi righe senza tag
        period_df = period_df[period_df['tag'].notna() & (period_df['tag'] != '')]

        # Converti colonne numeriche a int dove appropriato
        int_cols = ['LEAD_TOCCATO', 'LEAD_PARLATO', 'CHIAMATA_PRENOTATA',
                    'SESSIONE_SVOLTA', 'SESSIONE_VENDUTO', 'CHIUSURA_PAY_VALIDA']
        for col in int_cols:
            period_df[col] = period_df[col].astype(int)

        all_periods_data[period_name] = period_df

    return all_periods_data


def calculate_metrics(df):
    """Calcola metriche derivate"""
    df = df.copy()

    # Tasso conversione totale (lead -> vendita)
    df['conversion_rate'] = np.where(
        df['LEAD_TOCCATO'] > 0,
        df['CHIUSURA_PAY_VALIDA'] / df['LEAD_TOCCATO'] * 100,
        0
    )

    # Tasso sessione -> vendita
    df['session_to_sale_rate'] = np.where(
        df['SESSIONE_SVOLTA'] > 0,
        df['CHIUSURA_PAY_VALIDA'] / df['SESSIONE_SVOLTA'] * 100,
        0
    )

    # Tasso lead -> sessione
    df['lead_to_session_rate'] = np.where(
        df['LEAD_TOCCATO'] > 0,
        df['SESSIONE_SVOLTA'] / df['LEAD_TOCCATO'] * 100,
        0
    )

    # Tasso prenotazione
    df['booking_rate'] = np.where(
        df['LEAD_TOCCATO'] > 0,
        df['CHIAMATA_PRENOTATA'] / df['LEAD_TOCCATO'] * 100,
        0
    )

    return df


def calculate_composite_score(df, weight_volume=0.5, weight_efficiency=0.5):
    """Calcola uno score composito che bilancia volume ed efficienza."""
    df = df.copy()

    max_volume = df['CHIUSURA_PAY_VALIDA'].max()
    df['volume_score'] = np.where(
        max_volume > 0,
        df['CHIUSURA_PAY_VALIDA'] / max_volume * 100,
        0
    )

    max_efficiency = df['conversion_rate'].max()
    df['efficiency_score'] = np.where(
        max_efficiency > 0,
        df['conversion_rate'] / max_efficiency * 100,
        0
    )

    df['composite_score'] = (
        df['volume_score'] * weight_volume +
        df['efficiency_score'] * weight_efficiency
    )

    return df


def compare_periods(df_current, df_previous, min_leads=10):
    """Confronta due periodi e identifica trend"""
    # Unisci i dataframe
    merged = df_current[['tag', 'type', 'LEAD_TOCCATO', 'CHIUSURA_PAY_VALIDA', 'conversion_rate']].merge(
        df_previous[['tag', 'LEAD_TOCCATO', 'CHIUSURA_PAY_VALIDA', 'conversion_rate']],
        on='tag',
        suffixes=('_current', '_previous'),
        how='outer'
    ).fillna(0)

    # Calcola variazioni
    merged['lead_change'] = merged['LEAD_TOCCATO_current'] - merged['LEAD_TOCCATO_previous']
    merged['sales_change'] = merged['CHIUSURA_PAY_VALIDA_current'] - merged['CHIUSURA_PAY_VALIDA_previous']
    merged['conv_change'] = merged['conversion_rate_current'] - merged['conversion_rate_previous']

    # Filtra per minimo lead
    merged = merged[
        (merged['LEAD_TOCCATO_current'] >= min_leads) |
        (merged['LEAD_TOCCATO_previous'] >= min_leads)
    ]

    return merged


# Sidebar per upload e filtri
with st.sidebar:
    st.header("⚙️ Configurazione")
    uploaded_file = st.file_uploader("Carica il file CSV", type=['csv'])
    st.markdown("---")


if uploaded_file is not None:
    # Carica dati multi-periodo
    all_data = load_multiperiod_data(uploaded_file)

    # Sidebar filtri
    with st.sidebar:
        st.subheader("Periodo di Analisi")
        selected_period = st.selectbox(
            "Seleziona periodo",
            list(PERIODS.keys()),
            index=8  # Default: Ultimi 365 GG
        )

        st.markdown("---")
        st.subheader("Filtri")

        # Carica dati del periodo selezionato
        df = all_data[selected_period].copy()
        df = calculate_metrics(df)

        # Range lead
        max_lead = int(df['LEAD_TOCCATO'].max())
        lead_range = st.slider(
            "Range minimo LEAD_TOCCATO",
            min_value=0,
            max_value=min(500, max_lead),
            value=50,
            step=10
        )

        # Filtro type
        types = ['Tutti'] + sorted(df['type'].dropna().unique().tolist())
        selected_type = st.selectbox("Filtra per Type", types)

        st.markdown("---")
        st.subheader("Pesi Score Composito")
        weight_volume = st.slider(
            "Peso Volume",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1
        )
        weight_efficiency = 1 - weight_volume
        st.info(f"Peso Efficienza: {weight_efficiency:.1f}")

    # Applica filtri
    df_filtered = df[df['LEAD_TOCCATO'] >= lead_range].copy()
    if selected_type != 'Tutti':
        df_filtered = df_filtered[df_filtered['type'] == selected_type]

    df_filtered = calculate_composite_score(df_filtered, weight_volume, weight_efficiency)

    # === TAB PRINCIPALE ===
    tab_main, tab_trend, tab_compare = st.tabs(["📊 Analisi Periodo", "📈 Trend Temporali", "🔄 Confronto Periodi"])

    with tab_main:
        # Metriche generali
        st.header(f"📈 Panoramica - {selected_period}")

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Tag Analizzati", len(df_filtered))
        with col2:
            st.metric("Lead Totali", f"{df_filtered['LEAD_TOCCATO'].sum():,}")
        with col3:
            st.metric("Sessioni Totali", f"{df_filtered['SESSIONE_SVOLTA'].sum():,}")
        with col4:
            st.metric("Vendite Totali", f"{df_filtered['CHIUSURA_PAY_VALIDA'].sum():,}")
        with col5:
            avg_conv = df_filtered['CHIUSURA_PAY_VALIDA'].sum() / df_filtered['LEAD_TOCCATO'].sum() * 100 if df_filtered['LEAD_TOCCATO'].sum() > 0 else 0
            st.metric("Conversion Rate Medio", f"{avg_conv:.2f}%")

        # Top performer
        st.markdown("---")
        st.header("🏆 Top Performer")

        tab1, tab2, tab3 = st.tabs(["Score Composito", "Per Volume", "Per Efficienza"])

        with tab1:
            top_composite = df_filtered.nlargest(15, 'composite_score')[
                ['tag', 'type', 'LEAD_TOCCATO', 'SESSIONE_SVOLTA', 'CHIUSURA_PAY_VALIDA',
                 'conversion_rate', 'session_to_sale_rate', 'composite_score']
            ].copy()
            top_composite['conversion_rate'] = top_composite['conversion_rate'].round(2).astype(str) + '%'
            top_composite['session_to_sale_rate'] = top_composite['session_to_sale_rate'].round(2).astype(str) + '%'
            top_composite['composite_score'] = top_composite['composite_score'].round(1)
            top_composite.columns = ['Tag', 'Type', 'Lead', 'Sessioni', 'Vendite', 'Conv. Rate', 'Sess→Vendita', 'Score']
            st.dataframe(top_composite, use_container_width=True, hide_index=True)

        with tab2:
            top_volume = df_filtered.nlargest(15, 'CHIUSURA_PAY_VALIDA')[
                ['tag', 'type', 'LEAD_TOCCATO', 'SESSIONE_SVOLTA', 'CHIUSURA_PAY_VALIDA',
                 'conversion_rate', 'session_to_sale_rate']
            ].copy()
            top_volume['conversion_rate'] = top_volume['conversion_rate'].round(2).astype(str) + '%'
            top_volume['session_to_sale_rate'] = top_volume['session_to_sale_rate'].round(2).astype(str) + '%'
            top_volume.columns = ['Tag', 'Type', 'Lead', 'Sessioni', 'Vendite', 'Conv. Rate', 'Sess→Vendita']
            st.dataframe(top_volume, use_container_width=True, hide_index=True)

        with tab3:
            top_efficiency = df_filtered.nlargest(15, 'conversion_rate')[
                ['tag', 'type', 'LEAD_TOCCATO', 'SESSIONE_SVOLTA', 'CHIUSURA_PAY_VALIDA',
                 'conversion_rate', 'session_to_sale_rate']
            ].copy()
            top_efficiency['conversion_rate'] = top_efficiency['conversion_rate'].round(2).astype(str) + '%'
            top_efficiency['session_to_sale_rate'] = top_efficiency['session_to_sale_rate'].round(2).astype(str) + '%'
            top_efficiency.columns = ['Tag', 'Type', 'Lead', 'Sessioni', 'Vendite', 'Conv. Rate', 'Sess→Vendita']
            st.dataframe(top_efficiency, use_container_width=True, hide_index=True)

        # Grafici
        st.markdown("---")
        st.header("📊 Visualizzazioni")

        col1, col2 = st.columns(2)

        with col1:
            fig_scatter = px.scatter(
                df_filtered,
                x='CHIUSURA_PAY_VALIDA',
                y='conversion_rate',
                size='LEAD_TOCCATO',
                color='type',
                hover_name='tag',
                title='Volume vs Efficienza',
                labels={'CHIUSURA_PAY_VALIDA': 'Vendite', 'conversion_rate': 'Conversion Rate (%)'}
            )
            fig_scatter.update_layout(height=500)
            st.plotly_chart(fig_scatter, use_container_width=True)

        with col2:
            # Funnel per type
            funnel_by_type = df_filtered.groupby('type').agg({
                'LEAD_TOCCATO': 'sum',
                'CHIAMATA_PRENOTATA': 'sum',
                'SESSIONE_SVOLTA': 'sum',
                'CHIUSURA_PAY_VALIDA': 'sum'
            }).reset_index()

            fig_funnel = go.Figure()
            for _, row in funnel_by_type.iterrows():
                fig_funnel.add_trace(go.Bar(
                    name=row['type'],
                    x=['Lead', 'Prenotate', 'Sessioni', 'Vendite'],
                    y=[row['LEAD_TOCCATO'], row['CHIAMATA_PRENOTATA'],
                       row['SESSIONE_SVOLTA'], row['CHIUSURA_PAY_VALIDA']],
                ))
            fig_funnel.update_layout(title='Funnel per Type', barmode='group', height=500)
            st.plotly_chart(fig_funnel, use_container_width=True)

        # Insights automatici
        st.markdown("---")
        st.header("💡 Insights Automatici")

        best_balanced = df_filtered[df_filtered['CHIUSURA_PAY_VALIDA'] >= 3].nlargest(5, 'composite_score')
        high_eff_low_vol = df_filtered[
            (df_filtered['conversion_rate'] > df_filtered['conversion_rate'].median()) &
            (df_filtered['LEAD_TOCCATO'] < df_filtered['LEAD_TOCCATO'].median()) &
            (df_filtered['CHIUSURA_PAY_VALIDA'] > 0)
        ].nlargest(5, 'conversion_rate')
        high_vol_low_eff = df_filtered[
            (df_filtered['conversion_rate'] < df_filtered['conversion_rate'].median()) &
            (df_filtered['LEAD_TOCCATO'] > df_filtered['LEAD_TOCCATO'].median())
        ].nlargest(5, 'LEAD_TOCCATO')

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("🌟 Best Balanced")
            st.caption("Alto score composito")
            for _, row in best_balanced.iterrows():
                tag_display = f"**{row['tag'][:35]}...**" if len(row['tag']) > 35 else f"**{row['tag']}**"
                st.write(tag_display)
                st.write(f"Vendite: {int(row['CHIUSURA_PAY_VALIDA'])} | Conv: {row['conversion_rate']:.2f}%")
                st.markdown("---")

        with col2:
            st.subheader("🚀 Opportunità")
            st.caption("Alta efficienza, basso volume")
            for _, row in high_eff_low_vol.iterrows():
                tag_display = f"**{row['tag'][:35]}...**" if len(row['tag']) > 35 else f"**{row['tag']}**"
                st.write(tag_display)
                st.write(f"Lead: {int(row['LEAD_TOCCATO'])} | Conv: {row['conversion_rate']:.2f}%")
                st.markdown("---")

        with col3:
            st.subheader("⚠️ Da Ottimizzare")
            st.caption("Alto volume, bassa efficienza")
            for _, row in high_vol_low_eff.iterrows():
                tag_display = f"**{row['tag'][:35]}...**" if len(row['tag']) > 35 else f"**{row['tag']}**"
                st.write(tag_display)
                st.write(f"Lead: {int(row['LEAD_TOCCATO'])} | Conv: {row['conversion_rate']:.2f}%")
                st.markdown("---")

        # Tabella completa
        st.markdown("---")
        st.header("🔍 Esplora tutti i Tag")

        search = st.text_input("Cerca tag", "")
        df_display = df_filtered.copy()
        if search:
            df_display = df_display[df_display['tag'].str.contains(search, case=False, na=False)]

        df_display = df_display[[
            'tag', 'type', 'LEAD_TOCCATO', 'LEAD_PARLATO', 'CHIAMATA_PRENOTATA',
            'SESSIONE_SVOLTA', 'CHIUSURA_PAY_VALIDA', 'conversion_rate',
            'session_to_sale_rate', 'composite_score'
        ]].sort_values('composite_score', ascending=False)

        df_display['conversion_rate'] = df_display['conversion_rate'].round(2)
        df_display['session_to_sale_rate'] = df_display['session_to_sale_rate'].round(2)
        df_display['composite_score'] = df_display['composite_score'].round(1)

        df_display.columns = ['Tag', 'Type', 'Lead', 'Parlati', 'Prenotate', 'Sessioni',
                              'Vendite', 'Conv %', 'Sess→Vend %', 'Score']

        st.dataframe(df_display, use_container_width=True, hide_index=True, height=400)

        st.download_button(
            "📥 Scarica dati filtrati (CSV)",
            df_display.to_csv(index=False).encode('utf-8'),
            f"analisi_tag_{selected_period.replace(' ', '_')}.csv",
            "text/csv"
        )

    with tab_trend:
        st.header("📈 Trend Temporali")
        st.markdown("Analizza come cambiano le performance nel tempo")

        # Seleziona tag da analizzare
        all_tags = sorted(df['tag'].unique().tolist())
        selected_tags = st.multiselect(
            "Seleziona tag da confrontare (max 5)",
            all_tags,
            default=all_tags[:3] if len(all_tags) >= 3 else all_tags,
            max_selections=5
        )

        if selected_tags:
            # Periodi ordinati cronologicamente (dal più vecchio al più recente)
            ordered_periods = [
                "90 precedenti [470-361]",
                "90 precedenti [360-271]",
                "90 precedenti [270-181]",
                "90 precedenti [180-91]",
                "Ultimi 90 GG",
                "Ultimi 60 GG",
                "Ultimi 30 GG"
            ]

            # Costruisci dati per il grafico
            trend_data = []
            for period in ordered_periods:
                if period in all_data:
                    period_df = calculate_metrics(all_data[period])
                    for tag in selected_tags:
                        tag_data = period_df[period_df['tag'] == tag]
                        if not tag_data.empty:
                            trend_data.append({
                                'Periodo': period,
                                'Tag': tag[:30] + '...' if len(tag) > 30 else tag,
                                'Vendite': tag_data['CHIUSURA_PAY_VALIDA'].values[0],
                                'Lead': tag_data['LEAD_TOCCATO'].values[0],
                                'Conv Rate': tag_data['conversion_rate'].values[0]
                            })

            if trend_data:
                trend_df = pd.DataFrame(trend_data)

                col1, col2 = st.columns(2)

                with col1:
                    fig_trend_sales = px.line(
                        trend_df,
                        x='Periodo',
                        y='Vendite',
                        color='Tag',
                        markers=True,
                        title='Trend Vendite nel Tempo'
                    )
                    fig_trend_sales.update_layout(height=400)
                    st.plotly_chart(fig_trend_sales, use_container_width=True)

                with col2:
                    fig_trend_conv = px.line(
                        trend_df,
                        x='Periodo',
                        y='Conv Rate',
                        color='Tag',
                        markers=True,
                        title='Trend Conversion Rate nel Tempo'
                    )
                    fig_trend_conv.update_layout(height=400)
                    st.plotly_chart(fig_trend_conv, use_container_width=True)

                # Tabella riassuntiva
                st.subheader("Tabella Trend")
                st.dataframe(trend_df, use_container_width=True, hide_index=True)

    with tab_compare:
        st.header("🔄 Confronto tra Periodi")
        st.markdown("Identifica tag in crescita o in calo")

        col1, col2 = st.columns(2)
        with col1:
            period_current = st.selectbox(
                "Periodo corrente",
                list(PERIODS.keys()),
                index=2,  # Ultimi 90 GG
                key="period_current"
            )
        with col2:
            period_previous = st.selectbox(
                "Periodo precedente",
                list(PERIODS.keys()),
                index=3,  # 90 precedenti [180-91]
                key="period_previous"
            )

        min_leads_compare = st.slider("Lead minimo per confronto", 0, 100, 20, key="min_leads_compare")

        # Calcola confronto
        df_curr = calculate_metrics(all_data[period_current])
        df_prev = calculate_metrics(all_data[period_previous])

        comparison = compare_periods(df_curr, df_prev, min_leads_compare)

        if not comparison.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📈 In Crescita (Vendite)")
                growing = comparison[comparison['sales_change'] > 0].nlargest(10, 'sales_change')
                for _, row in growing.iterrows():
                    tag_display = row['tag'][:35] + '...' if len(row['tag']) > 35 else row['tag']
                    change = int(row['sales_change'])
                    st.write(f"**{tag_display}**")
                    st.write(f"Vendite: {int(row['CHIUSURA_PAY_VALIDA_previous'])} → {int(row['CHIUSURA_PAY_VALIDA_current'])} (+{change})")
                    st.markdown("---")

            with col2:
                st.subheader("📉 In Calo (Vendite)")
                declining = comparison[comparison['sales_change'] < 0].nsmallest(10, 'sales_change')
                for _, row in declining.iterrows():
                    tag_display = row['tag'][:35] + '...' if len(row['tag']) > 35 else row['tag']
                    change = int(row['sales_change'])
                    st.write(f"**{tag_display}**")
                    st.write(f"Vendite: {int(row['CHIUSURA_PAY_VALIDA_previous'])} → {int(row['CHIUSURA_PAY_VALIDA_current'])} ({change})")
                    st.markdown("---")

            # Grafico confronto
            st.subheader("Grafico Confronto")

            # Top 20 per variazione assoluta
            comparison['abs_change'] = comparison['sales_change'].abs()
            top_changes = comparison.nlargest(20, 'abs_change').copy()
            top_changes['tag_short'] = top_changes['tag'].apply(lambda x: x[:25] + '...' if len(x) > 25 else x)

            fig_compare = go.Figure()
            fig_compare.add_trace(go.Bar(
                name=period_previous,
                x=top_changes['tag_short'],
                y=top_changes['CHIUSURA_PAY_VALIDA_previous'],
                marker_color='lightblue'
            ))
            fig_compare.add_trace(go.Bar(
                name=period_current,
                x=top_changes['tag_short'],
                y=top_changes['CHIUSURA_PAY_VALIDA_current'],
                marker_color='darkblue'
            ))
            fig_compare.update_layout(
                title='Confronto Vendite tra Periodi (Top 20 variazioni)',
                barmode='group',
                height=500,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_compare, use_container_width=True)

            # Tabella completa confronto
            st.subheader("Tabella Completa Confronto")
            comparison_display = comparison[[
                'tag', 'type', 'LEAD_TOCCATO_previous', 'LEAD_TOCCATO_current',
                'CHIUSURA_PAY_VALIDA_previous', 'CHIUSURA_PAY_VALIDA_current',
                'sales_change', 'conversion_rate_previous', 'conversion_rate_current', 'conv_change'
            ]].copy()
            comparison_display.columns = [
                'Tag', 'Type', 'Lead Prec', 'Lead Curr', 'Vendite Prec', 'Vendite Curr',
                'Δ Vendite', 'Conv% Prec', 'Conv% Curr', 'Δ Conv%'
            ]
            comparison_display['Conv% Prec'] = comparison_display['Conv% Prec'].round(2)
            comparison_display['Conv% Curr'] = comparison_display['Conv% Curr'].round(2)
            comparison_display['Δ Conv%'] = comparison_display['Δ Conv%'].round(2)
            comparison_display = comparison_display.sort_values('Δ Vendite', ascending=False)

            st.dataframe(comparison_display, use_container_width=True, hide_index=True, height=400)

            st.download_button(
                "📥 Scarica confronto (CSV)",
                comparison_display.to_csv(index=False).encode('utf-8'),
                "confronto_periodi.csv",
                "text/csv"
            )

else:
    st.info("👆 Carica un file CSV dalla sidebar per iniziare l'analisi")

    st.markdown("""
    ### Formato atteso del file CSV

    Il file deve contenere dati multi-periodo con questa struttura:
    - Prima riga: nomi dei periodi (Ultimi 30 GG, Ultimi 60 GG, etc.)
    - Seconda riga: header delle colonne
    - Righe successive: dati

    ### Periodi supportati
    - Ultimi 30/60/90 giorni
    - 90 precedenti (vari range storici)
    - Ultimi 180/365 giorni

    ### Funzionalità
    - **Analisi Periodo**: analisi dettagliata del periodo selezionato
    - **Trend Temporali**: visualizza come cambiano le performance nel tempo
    - **Confronto Periodi**: identifica tag in crescita o in calo
    """)

# Footer sidebar
with st.sidebar:
    st.markdown("---")
    st.caption("Made with 🤍 🩵 in the Ancient Land of Liberty")
