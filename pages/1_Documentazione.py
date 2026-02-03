import streamlit as st

st.set_page_config(
    page_title="Documentazione",
    page_icon="📖",
    layout="wide"
)

st.title("📖 Documentazione")
st.markdown("Guida completa all'utilizzo dello strumento di Analisi Performance Tag")

st.markdown("---")

# Introduzione
st.header("🎯 Cos'è questo strumento?")
st.markdown("""
Questo strumento analizza le performance dei **tag prodotto** nel funnel di vendita,
aiutandoti a identificare quali tag performano meglio considerando sia il **volume**
(numero assoluto di vendite) che l'**efficienza** (tasso di conversione).

### Il problema che risolve
Un tag con molte vendite non è necessariamente il migliore: potrebbe avere avuto
semplicemente più lead in ingresso. Questo strumento ti permette di:
- Confrontare tag con volumi diversi in modo equo
- Identificare tag ad alta efficienza che meritano più investimento
- Scoprire tag con alto volume ma bassa efficienza da ottimizzare
""")

st.markdown("---")

# Formato dati
st.header("📁 Formato del file CSV")
st.markdown("""
Il file CSV deve contenere dati multi-periodo con questa struttura:

| Colonna | Descrizione |
|---------|-------------|
| `tag` | Nome/identificativo del tag prodotto |
| `type` | Tipologia di campagna (es. ADV, Organic, etc.) |
| `LEAD_TOCCATO` | Numero di lead contattati |
| `LEAD_PARLATO` | Lead con cui si è parlato |
| `CHIAMATA_PRENOTATA` | Chiamate/sessioni prenotate |
| `SESSIONE_SVOLTA` | Sessioni effettivamente svolte |
| `CHIUSURA_PAY_VALIDA` | Vendite concluse con pagamento |

### Periodi supportati
Il file può contenere dati per più periodi temporali:
- Ultimi 30 / 60 / 90 giorni
- Periodi storici (90 giorni precedenti)
- Ultimi 180 / 365 giorni
""")

st.markdown("---")

# Metriche
st.header("📊 Metriche calcolate")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Conversion Rate")
    st.markdown("""
    ```
    Vendite / Lead Toccati × 100
    ```
    Misura l'efficienza complessiva del funnel:
    quanti lead si trasformano in clienti paganti.
    """)

    st.subheader("Session to Sale Rate")
    st.markdown("""
    ```
    Vendite / Sessioni Svolte × 100
    ```
    Misura l'efficacia delle sessioni di vendita:
    quante sessioni si concludono con un acquisto.
    """)

with col2:
    st.subheader("Lead to Session Rate")
    st.markdown("""
    ```
    Sessioni Svolte / Lead Toccati × 100
    ```
    Misura quanti lead arrivano effettivamente
    a svolgere una sessione.
    """)

    st.subheader("Booking Rate")
    st.markdown("""
    ```
    Chiamate Prenotate / Lead Toccati × 100
    ```
    Misura la capacità di portare i lead
    a prenotare un appuntamento.
    """)

st.markdown("---")

# Score Composito
st.header("🏆 Score Composito")
st.markdown("""
Lo **Score Composito** è la metrica chiave che bilancia volume ed efficienza.

### Come funziona
1. **Volume Score**: le vendite del tag normalizzate rispetto al tag con più vendite (0-100)
2. **Efficiency Score**: il conversion rate normalizzato rispetto al tag più efficiente (0-100)
3. **Score Composito**: media pesata dei due score

### Formula
```
Score = (Volume Score × Peso Volume) + (Efficiency Score × Peso Efficienza)
```

### Esempio pratico
| Tag | Vendite | Conv. Rate | Volume Score | Efficiency Score | Score (50/50) |
|-----|---------|------------|--------------|------------------|---------------|
| Tag A | 100 | 5% | 100 | 50 | 75 |
| Tag B | 50 | 10% | 50 | 100 | 75 |
| Tag C | 75 | 7.5% | 75 | 75 | 75 |

Tutti e tre i tag hanno lo stesso score composito, ma per motivi diversi!

### Come regolare i pesi
- **Peso Volume alto (0.7-1.0)**: quando hai bisogno di numeri assoluti (es. raggiungere obiettivi di fatturato)
- **Peso Efficienza alto (0.7-1.0)**: quando vuoi ottimizzare i costi (es. budget marketing limitato)
- **Bilanciato (0.5)**: visione equilibrata per decisioni strategiche
""")

st.markdown("---")

# Funzionalità
st.header("🔧 Funzionalità principali")

tab1, tab2, tab3 = st.tabs(["Analisi Periodo", "Trend Temporali", "Confronto Periodi"])

with tab1:
    st.subheader("📊 Tab Analisi Periodo")
    st.markdown("""
    La schermata principale per analizzare i dati di un singolo periodo.

    **Filtri disponibili:**
    - **Periodo**: seleziona il range temporale da analizzare
    - **Lead minimo**: escludi tag con pochi lead (risultati statisticamente poco significativi)
    - **Type**: filtra per tipologia di campagna
    - **Pesi Score**: regola il bilanciamento volume/efficienza

    **Visualizzazioni:**
    - **Top Performer**: classifica per score composito, volume o efficienza
    - **Scatter Plot**: visualizza la relazione volume vs efficienza
    - **Funnel per Type**: confronta le performance tra tipologie
    - **Insights**: suggerimenti automatici su opportunità e criticità
    """)

with tab2:
    st.subheader("📈 Tab Trend Temporali")
    st.markdown("""
    Analizza come cambiano le performance nel tempo.

    **Come usarla:**
    1. Seleziona fino a 5 tag da confrontare
    2. Visualizza l'andamento di vendite e conversion rate
    3. Identifica trend positivi o negativi

    **Utile per:**
    - Capire se un tag sta migliorando o peggiorando
    - Identificare stagionalità
    - Valutare l'impatto di modifiche alle campagne
    """)

with tab3:
    st.subheader("🔄 Tab Confronto Periodi")
    st.markdown("""
    Confronta direttamente due periodi per identificare variazioni.

    **Come usarla:**
    1. Seleziona periodo corrente e periodo precedente
    2. Imposta il minimo di lead per il confronto
    3. Analizza tag in crescita e in calo

    **Metriche di confronto:**
    - Δ Vendite: variazione assoluta delle vendite
    - Δ Conv%: variazione del tasso di conversione
    """)

st.markdown("---")

# Best Practices
st.header("💡 Best Practices")
st.markdown("""
### 1. Imposta sempre un filtro lead minimo
Tag con pochi lead producono risultati statisticamente poco affidabili.
Un conversion rate del 50% con 2 lead non è significativo.

**Consiglio:** usa almeno 30-50 lead come soglia minima.

### 2. Non guardare solo il volume
Un tag con 100 vendite da 1000 lead (10% conv.) potrebbe essere meno
interessante di uno con 30 vendite da 100 lead (30% conv.).

### 3. Usa gli Insights automatici
La sezione "Insights" identifica automaticamente:
- **Best Balanced**: tag con ottimo equilibrio volume/efficienza
- **Opportunità**: tag efficienti che meritano più investimento
- **Da Ottimizzare**: tag con molto traffico ma bassa conversione

### 4. Confronta periodi equivalenti
Quando usi il confronto periodi, assicurati di confrontare
periodi di durata simile (es. 90gg vs 90gg precedenti).

### 5. Esporta i dati
Usa il pulsante "Scarica CSV" per analisi più approfondite
in Excel o per condividere i risultati con il team.
""")

st.markdown("---")

# FAQ
st.header("❓ FAQ")

with st.expander("Perché alcuni tag non compaiono nella lista?"):
    st.markdown("""
    I tag vengono filtrati in base al minimo di lead impostato nella sidebar.
    Se un tag ha meno lead del valore soglia, non verrà mostrato.
    Riduci il filtro "Range minimo LEAD_TOCCATO" per vedere più tag.
    """)

with st.expander("Come interpreto lo scatter plot Volume vs Efficienza?"):
    st.markdown("""
    - **Quadrante in alto a destra**: tag ideali (alto volume + alta efficienza)
    - **In alto a sinistra**: alta efficienza ma poco volume → opportunità di scaling
    - **In basso a destra**: alto volume ma bassa efficienza → da ottimizzare
    - **In basso a sinistra**: basse performance → valutare se mantenere
    """)

with st.expander("Cosa significa 'Session to Sale Rate'?"):
    st.markdown("""
    È la percentuale di sessioni che si concludono con una vendita.
    Un valore alto indica che le sessioni sono efficaci.
    Un valore basso potrebbe indicare problemi nel processo di vendita
    o lead non qualificati che arrivano alla sessione.
    """)

with st.expander("Posso caricare file con formati diversi?"):
    st.markdown("""
    Attualmente lo strumento supporta solo file CSV con la struttura
    multi-periodo specifica. Assicurati che il file abbia:
    - Prima riga: nomi dei periodi
    - Seconda riga: header delle colonne
    - Righe successive: dati
    """)

st.markdown("---")
st.caption("Strumento sviluppato per l'analisi delle performance di vendita")

# Footer sidebar
with st.sidebar:
    st.markdown("---")
    st.caption("Made with 🤍 🩵 in the Ancient Land of Liberty")
