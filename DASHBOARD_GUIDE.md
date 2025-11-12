# 📊 Trading Assistant Dashboard - Guide d'Utilisation

## 🚀 Lancement Rapide

### Méthode 1: Script de lancement (Recommandé)
```bash
./run_dashboard.sh
```

### Méthode 2: Commande directe
```bash
streamlit run app.py
```

Le dashboard sera accessible sur **http://localhost:8501**

---

## 📱 Interface Utilisateur

### 🏠 Page d'Accueil - Vue d'ensemble du marché

**Fonctionnalités:**
- 📊 Statistiques du marché (nombre d'actions, variation moyenne, volume total)
- 🟢 Top 5 gagnants du jour
- 🔴 Top 5 perdants du jour
- 📋 Tableau de toutes les actions disponibles

**Métriques affichées:**
- Ticker
- Nom de l'entreprise
- Prix actuel (MAD)
- Variation (%)
- Volume d'échanges
- Dernière mise à jour

---

### 🔍 Page Analyse - Analyse technique détaillée

**Sélection:**
1. Choisir une action dans le menu déroulant
2. Cliquer sur le bouton **"🚀 Analyser"**

**Informations affichées:**

#### 📊 Métriques principales
- **Prix actuel** (MAD)
- **Score technique** (0-100)
- **Niveau de confiance** (%)
- **Points de données** utilisés

#### 🎯 Signal de Trading
- **STRONG BUY** (80-100) 🟢 - Acheter immédiatement
- **BUY** (60-79) 🟢 - Acheter
- **HOLD** (40-59) 🟡 - Conserver
- **SELL** (20-39) 🔴 - Vendre
- **STRONG SELL** (0-19) 🔴 - Vendre immédiatement

Chaque signal inclut:
- Description détaillée
- Action recommandée
- Niveau de confiance

#### 📈 Graphiques Interactifs

**1. Graphique de prix (Candlestick)**
- Prix OHLC (Open, High, Low, Close)
- SMA 20 jours (ligne orange)
- Zoom et pan interactifs
- Tooltip avec détails

**2. Graphique de volume**
- Volume d'échanges quotidien
- Barres interactives
- Identification des pics de volume

#### 📊 Indicateurs Techniques
- **RSI (14)** - Relative Strength Index
- **SMA (20)** - Simple Moving Average
- **Tendance** - Bullish 🟢 / Bearish 🔴 / Neutral 🟡
- **Volume Ratio** - Par rapport à la moyenne

#### 🔍 Détails du Score
Répartition du score par critère:
- RSI optimal (40-60): max +30pts
- MACD positif: max +20pts
- Prix > SMA_20: max +20pts
- Volume > moyenne: max +15pts
- Tendance haussière: max +15pts

#### 💡 Justifications
Explication détaillée des raisons du signal:
- Analyse RSI (survente/surachat/optimal)
- Position prix vs SMA
- Activité volume
- Direction tendance

---

### ℹ️ Page À Propos

Informations sur:
- Système de scoring
- Indicateurs techniques
- Stack technique
- Avertissements et limitations
- Version et statut

---

## ⚙️ Configuration (Sidebar)

### Période d'analyse
Slider pour ajuster la période d'analyse (7-90 jours)
- **Minimum:** 7 jours
- **Recommandé:** 30 jours
- **Maximum:** 90 jours

### Informations système
- Version de l'application
- Nombre de tickers validés
- Nombre d'endpoints API
- Statut du scoring

---

## 🎨 Légende des Couleurs

### Signaux
- 🟢 **Vert** - Acheter (BUY, STRONG BUY)
- 🟡 **Jaune** - Conserver (HOLD)
- 🔴 **Rouge** - Vendre (SELL, STRONG SELL)

### Tendances
- 🟢 **BULLISH** - Tendance haussière
- 🔴 **BEARISH** - Tendance baissière
- 🟡 **NEUTRAL** - Tendance neutre

---

## 📊 Interprétation des Signaux

### STRONG BUY (80-100) 🟢
**Signification:** Conditions techniques très favorables
**Action:** Acheter immédiatement
**Critères:**
- RSI dans zone optimale (40-60)
- MACD positif et en croissance
- Prix au-dessus SMA
- Volume élevé
- Tendance haussière confirmée

### BUY (60-79) 🟢
**Signification:** Bonnes conditions d'achat
**Action:** Acheter
**Critères:** Majorité des indicateurs positifs

### HOLD (40-59) 🟡
**Signification:** Conditions neutres
**Action:** Conserver position actuelle
**Critères:** Indicateurs mixtes

### SELL (20-39) 🔴
**Signification:** Conditions techniques défavorables
**Action:** Vendre
**Critères:** Majorité des indicateurs négatifs

### STRONG SELL (0-19) 🔴
**Signification:** Conditions très défavorables
**Action:** Vendre immédiatement
**Critères:**
- RSI en zone extrême
- MACD négatif
- Prix en-dessous SMA
- Tendance baissière forte

---

## 🔧 Dépannage

### Dashboard ne se lance pas
```bash
# Vérifier les dépendances
pip install -r requirements.txt

# Relancer
streamlit run app.py
```

### Pas de données affichées
```bash
# Créer des données de test
python3 test_scoring.py

# Vérifier la base de données
python3 -c "from db import get_all_stocks; print(len(get_all_stocks()))"
```

### Erreur "Données insuffisantes"
**Cause:** Moins de 30 jours de données historiques
**Solution:** Accumuler plus de données ou utiliser test_scoring.py

### Port 8501 déjà utilisé
```bash
# Utiliser un port différent
streamlit run app.py --server.port 8502
```

---

## ⚠️ Notes Importantes

### Données Mock
**Actuellement:** Utilisation de données simulées
**Raison:** API Casablanca Bourse bloquée (geo-blocking)
**Pour production:** Nécessite IP marocaine ou API officielle

### Recommandations != Conseils Financiers
Ce système fournit des analyses techniques automatisées.
**Toujours:**
- Faire ses propres recherches (DYOR)
- Consulter un conseiller financier
- Considérer les fondamentaux de l'entreprise
- Gérer les risques appropriés

### Fréquence de mise à jour
- Données temps réel: Selon disponibilité API
- Indicateurs: Recalculés à chaque analyse
- Scores: Générés dynamiquement

---

## 🎯 Cas d'Utilisation

### 1. Screening Quotidien
1. Aller sur "Vue d'ensemble"
2. Consulter top gagnants/perdants
3. Identifier actions intéressantes

### 2. Analyse Avant Achat
1. Sélectionner action sur "Analyser une action"
2. Vérifier le signal
3. Lire justifications
4. Examiner graphiques et indicateurs
5. Prendre décision informée

### 3. Suivi de Portfolio
1. Analyser chaque action du portfolio
2. Comparer scores
3. Identifier actions à vendre/conserver
4. Rééquilibrer portfolio

### 4. Détection d'Opportunités
1. Filtrer actions avec STRONG BUY
2. Vérifier justifications
3. Valider avec analyse fondamentale
4. Entrer position

---

## 📚 Ressources Additionnelles

### Documentation
- **README.md** - Vue d'ensemble projet
- **API_DOCUMENTATION.md** - Documentation API REST
- **PROJECT_OVERVIEW.md** - Architecture technique

### API REST Alternative
Si préférence pour API plutôt que dashboard:
```bash
# Lancer API
uvicorn api:app --reload --port 8000

# Accéder Swagger
http://localhost:8000/docs
```

### Tests
```bash
# Test système complet
python3 test_scoring.py

# Test API
python3 test_api.py
```

---

## 🔄 Prochaines Améliorations

**Fonctionnalités futures:**
- [ ] Export PDF des analyses
- [ ] Alertes email/SMS
- [ ] Comparaison multi-actions
- [ ] Backtesting stratégies
- [ ] Portfolio tracker
- [ ] Mode dark/light
- [ ] Graphiques avancés (Ichimoku, Fibonacci)
- [ ] Analyses fondamentales
- [ ] Intégration données réelles

---

## 📞 Support

**Problèmes ou questions:**
1. Vérifier logs console
2. Consulter documentation
3. Tester avec données mock
4. Vérifier connexion API (si applicable)

**Versions:**
- Application: 1.1.0
- Streamlit: 1.29.0
- Python: 3.11+

---

**Bon trading! 📈**
