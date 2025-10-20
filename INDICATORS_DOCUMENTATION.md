# Documentation des Indicateurs Techniques

## Vue d'ensemble

Le module `indicators.py` fournit une suite complète d'indicateurs techniques pour l'analyse des actions de la Bourse de Casablanca. Ces indicateurs sont accessibles via l'API REST et peuvent être utilisés pour générer des signaux de trading automatiques.

## 📊 Indicateurs Disponibles

### 1. RSI (Relative Strength Index)
**Période par défaut : 14 jours**

L'indice de force relative mesure la vitesse et l'amplitude des mouvements de prix.

**Interprétation :**
- **RSI < 30** : Zone de survente → Signal d'achat potentiel
- **RSI > 70** : Zone de surachat → Signal de vente potentiel
- **30 < RSI < 70** : Zone neutre

**Formule :**
```
RSI = 100 - (100 / (1 + RS))
où RS = Moyenne des gains / Moyenne des pertes
```

### 2. MACD (Moving Average Convergence Divergence)
**Périodes par défaut : 12, 26, 9**

Indicateur de momentum qui suit la tendance en montrant la relation entre deux moyennes mobiles.

**Composantes :**
- **Ligne MACD** : EMA(12) - EMA(26)
- **Ligne de signal** : EMA(9) de la ligne MACD
- **Histogramme** : MACD - Signal

**Interprétation :**
- **MACD > Signal** : Tendance haussière → Signal d'achat
- **MACD < Signal** : Tendance baissière → Signal de vente
- **Croisement haussier** : MACD croise Signal vers le haut → Fort signal d'achat
- **Croisement baissier** : MACD croise Signal vers le bas → Fort signal de vente

### 3. SMA (Simple Moving Average)
**Périodes calculées : 20, 50, 200 jours**

Moyenne arithmétique simple des prix de clôture sur N périodes.

**Interprétation :**
- **Prix > SMA** : Tendance haussière
- **Prix < SMA** : Tendance baissière
- **SMA(20) > SMA(50)** : Momentum haussier
- **SMA(50) > SMA(200)** : Tendance long terme positive (Golden Cross)

### 4. EMA (Exponential Moving Average)
**Périodes calculées : 12, 26 jours**

Moyenne mobile exponentielle qui donne plus de poids aux prix récents.

**Avantages :**
- Plus réactive aux changements de prix récents
- Réduit le lag par rapport à la SMA

### 5. Bollinger Bands
**Périodes : 20 jours, ±2 écarts-types**

Bandes de volatilité placées au-dessus et au-dessous d'une moyenne mobile.

**Composantes :**
- **Bande supérieure** : SMA(20) + 2σ
- **Bande médiane** : SMA(20)
- **Bande inférieure** : SMA(20) - 2σ

**Interprétation :**
- **Prix touche bande inférieure** : Potentiellement survendu → Signal d'achat
- **Prix touche bande supérieure** : Potentiellement suracheté → Signal de vente
- **Bandes resserrées** : Faible volatilité, cassure probable
- **Bandes élargies** : Forte volatilité

### 6. Stochastic Oscillator
**Périodes : %K = 14, %D = 3**

Oscillateur de momentum comparant le prix de clôture à sa fourchette de prix.

**Formule :**
```
%K = (Prix actuel - Plus bas(14)) / (Plus haut(14) - Plus bas(14)) × 100
%D = Moyenne mobile de %K sur 3 périodes
```

**Interprétation :**
- **%K < 20** : Zone de survente → Signal d'achat
- **%K > 80** : Zone de surachat → Signal de vente
- **Croisement %K au-dessus de %D** : Signal d'achat
- **Croisement %K en-dessous de %D** : Signal de vente

## 🎯 Système de Signaux de Trading

### Scores et Signaux

Le système analyse tous les indicateurs et génère un score composite :

| Score | Signal | Confiance |
|-------|--------|-----------|
| ≥ +5 | STRONG BUY | HIGH |
| +2 à +4 | BUY | MEDIUM |
| -2 à +1 | HOLD | LOW |
| -5 à -3 | SELL | MEDIUM |
| ≤ -6 | STRONG SELL | HIGH |

### Pondération des Indicateurs

| Indicateur | Poids | Condition |
|------------|-------|-----------|
| RSI < 30 | +2 | Survente |
| RSI > 70 | -2 | Surachat |
| MACD Croisement Haussier | +3 | Crossover bullish |
| MACD Croisement Baissier | -3 | Crossover bearish |
| MACD > Signal | +1 | Au-dessus signal |
| MACD < Signal | -1 | En-dessous signal |
| Prix > SMA(20) | +1 | Au-dessus moyenne |
| Prix < SMA(20) | -1 | En-dessous moyenne |
| SMA(20) > SMA(50) | +1 | Uptrend |
| SMA(20) < SMA(50) | -1 | Downtrend |
| Prix < BB Inférieure | +2 | Survente |
| Prix > BB Supérieure | -2 | Surachat |
| Stochastic < 20 | +1 | Survente |
| Stochastic > 80 | -1 | Surachat |

## 📡 API Endpoints

### Endpoint 1 : Calculer les Indicateurs

```bash
GET /stocks/{ticker}/indicators?days=30
```

**Paramètres :**
- `ticker` (path) : Symbole du ticker (ex: VCN, ATW, BCP)
- `days` (query) : Nombre de jours d'historique (min: 20, max: 365, défaut: 30)

**Exemple de requête :**
```bash
curl http://localhost:8000/stocks/VCN/indicators?days=50
```

**Exemple de réponse :**
```json
{
  "success": true,
  "data": {
    "ticker": "VCN",
    "days": 50,
    "records": 50,
    "indicators": [
      {
        "date": "2025-10-20T00:00:00",
        "open": 470.0,
        "high": 471.0,
        "low": 462.3,
        "close": 471.0,
        "volume": 19286358.0,
        "rsi": 65.32,
        "macd": 2.45,
        "macd_signal": 1.89,
        "macd_histogram": 0.56,
        "sma_20": 465.8,
        "sma_50": 460.2,
        "sma_200": null,
        "ema_12": 468.5,
        "ema_26": 466.1,
        "bb_upper": 475.2,
        "bb_middle": 465.8,
        "bb_lower": 456.4,
        "stoch_k": 78.5,
        "stoch_d": 72.3
      }
      // ... autres jours
    ]
  },
  "timestamp": "2025-10-20T22:30:00.000000+00:00",
  "ticker": "VCN"
}
```

### Endpoint 2 : Obtenir les Signaux de Trading

```bash
GET /stocks/{ticker}/signals?days=30
```

**Paramètres :**
- `ticker` (path) : Symbole du ticker
- `days` (query) : Nombre de jours pour l'analyse (min: 20, max: 365, défaut: 30)

**Exemple de requête :**
```bash
curl http://localhost:8000/stocks/VCN/signals
```

**Exemple de réponse :**
```json
{
  "success": true,
  "data": {
    "ticker": "VCN",
    "current_price": 471.0,
    "signal": "BUY",
    "confidence": "MEDIUM",
    "score": 3,
    "analysis": [
      "RSI neutral (40-60) - No clear signal",
      "MACD above signal - Bullish",
      "Price above SMA(20) - Bullish",
      "SMA(20) > SMA(50) - Uptrend"
    ],
    "current_indicators": {
      "rsi": 65.32,
      "macd": 2.45,
      "macd_signal": 1.89,
      "price": 471.0,
      "sma_20": 465.8,
      "sma_50": 460.2
    }
  },
  "timestamp": "2025-10-20T22:30:00.000000+00:00",
  "ticker": "VCN"
}
```

## 💻 Utilisation Programmatique

### Python

```python
import requests

# Obtenir les indicateurs
response = requests.get('http://localhost:8000/stocks/VCN/indicators?days=50')
data = response.json()

if data['success']:
    indicators = data['data']['indicators']
    latest = indicators[-1]

    print(f"RSI: {latest['rsi']:.2f}")
    print(f"MACD: {latest['macd']:.4f}")
    print(f"Prix: {latest['close']:.2f}")

# Obtenir les signaux
response = requests.get('http://localhost:8000/stocks/VCN/signals')
data = response.json()

if data['success']:
    signal_data = data['data']
    print(f"\nSignal: {signal_data['signal']}")
    print(f"Confiance: {signal_data['confidence']}")
    print(f"Prix actuel: {signal_data['current_price']} MAD")

    print("\nAnalyse détaillée:")
    for analysis in signal_data['analysis']:
        print(f"  • {analysis}")
```

### JavaScript

```javascript
// Obtenir les indicateurs
const response = await fetch('http://localhost:8000/stocks/VCN/indicators?days=50');
const data = await response.json();

if (data.success) {
  const latest = data.data.indicators[data.data.indicators.length - 1];
  console.log(`RSI: ${latest.rsi.toFixed(2)}`);
  console.log(`MACD: ${latest.macd.toFixed(4)}`);
  console.log(`Prix: ${latest.close.toFixed(2)}`);
}

// Obtenir les signaux
const signalResponse = await fetch('http://localhost:8000/stocks/VCN/signals');
const signalData = await signalResponse.json();

if (signalData.success) {
  console.log(`\nSignal: ${signalData.data.signal}`);
  console.log(`Confiance: ${signalData.data.confidence}`);
  console.log(`Score: ${signalData.data.score}`);
}
```

## 🧪 Tests

### Lancer les tests

```bash
# Tester tous les indicateurs
python3 test_indicators.py

# Résultat attendu : 100% de réussite
```

### Tests inclus

1. **SMA** - Validation de la moyenne mobile simple
2. **EMA** - Validation de la moyenne mobile exponentielle
3. **RSI** - Validation de l'indice de force relative (0-100)
4. **MACD** - Validation MACD, Signal, Histogramme
5. **Bollinger Bands** - Validation des bandes (Upper > Middle > Lower)
6. **Stochastic** - Validation %K et %D (0-100)
7. **All Indicators** - Test du calcul combiné
8. **Trading Signals** - Validation de la génération de signaux
9. **Edge Cases** - Gestion des cas limites (données insuffisantes)

## 📈 Exemples de Stratégies

### Stratégie 1 : RSI + MACD
```
Achat si :
- RSI < 30 (survente)
- MACD croise signal vers le haut

Vente si :
- RSI > 70 (surachat)
- MACD croise signal vers le bas
```

### Stratégie 2 : Bollinger + Stochastic
```
Achat si :
- Prix touche bande inférieure
- Stochastic < 20

Vente si :
- Prix touche bande supérieure
- Stochastic > 80
```

### Stratégie 3 : Moyennes Mobiles
```
Achat si :
- Prix > SMA(20)
- SMA(20) > SMA(50)
- SMA(50) > SMA(200) (Golden Cross)

Vente si :
- Prix < SMA(20)
- SMA(20) < SMA(50)
```

## ⚠️ Avertissements

1. **Pas de conseil financier** : Ces indicateurs sont fournis à titre informatif uniquement
2. **Données historiques** : Les performances passées ne garantissent pas les résultats futurs
3. **Validation** : Toujours valider les signaux avec d'autres sources d'information
4. **Risques** : Le trading comporte des risques de perte en capital
5. **Données minimum** : Au moins 20 jours de données sont nécessaires pour des calculs fiables

## 🔧 Configuration Avancée

### Personnaliser les périodes

Modifiez les périodes par défaut dans `indicators.py` :

```python
# Dans calculate_all_indicators()
rsi_period = 14  # RSI
macd_fast = 12   # MACD rapide
macd_slow = 26   # MACD lent
macd_signal = 9  # Signal MACD
sma_periods = [20, 50, 200]  # SMAs
ema_periods = [12, 26]       # EMAs
```

### Ajuster les seuils de signaux

Modifiez les seuils dans `get_trading_signals()` :

```python
# RSI
if rsi < 30:  # Survente (changer à 25 pour plus strict)
    score += 2

# Stochastic
if stoch_k < 20:  # Survente (changer à 15 pour plus strict)
    score += 1
```

## 📚 Références

- **RSI** : J. Welles Wilder, "New Concepts in Technical Trading Systems" (1978)
- **MACD** : Gerald Appel (1979)
- **Bollinger Bands** : John Bollinger (1980s)
- **Stochastic** : George Lane (1950s)

## 🤝 Support

Pour toute question ou problème :

1. Consulter la documentation Swagger : `http://localhost:8000/docs`
2. Vérifier les logs de l'API
3. Tester avec `test_indicators.py`
4. Ouvrir une issue sur GitHub

---

**Dernière mise à jour** : 20 Octobre 2025
**Version** : 1.0.0
**Statut** : ✅ Production Ready
