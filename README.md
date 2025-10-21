# 📊 Trading Assistant - Bourse de Casablanca

Outil d'analyse automatisé pour la Bourse de Casablanca avec scraping temps réel, analyse technique et recommandations.

## 🎯 Fonctionnalités

- ✅ Scraping API Next.js (60 tickers validés)
- ✅ Surveillance API automatique (détection changements)
- ✅ Base SQLite avec historiques
- ✅ API REST FastAPI (8 endpoints)
- ✅ Tests automatisés complets
- ✅ Documentation Swagger complète
- ⏳ Dashboard React (à venir)
- ⏳ Système de scoring (à venir)
- ⏳ Job automatique collecte (à venir)

## 🚀 Quick Start

### Installation

```bash
# Installer dépendances
pip install -r requirements.txt

# Ou installer individuellement
pip install fastapi uvicorn sqlalchemy requests pandas tqdm pytz
```

### Utilisation

```bash
# 1. Tester scraper sur 3 actions
python3 scraper.py

# 2. Peupler DB avec tous les tickers (60 accessibles)
python3 test_all_tickers.py --save

# 3. Tester la base de données
python3 test_db.py

# 4. Lancer l'API
uvicorn api:app --reload --port 8000

# 5. Accéder à Swagger
open http://localhost:8000/docs
```

## 📁 Architecture Projet

```
trading-assistant-casablanca/
├── Core Scripts
│   ├── constants.py            # Configuration & tickers validés
│   ├── scraper.py              # Scraper avec monitoring API
│   ├── db.py                   # ORM SQLAlchemy + SQLite
│   └── api.py                  # API REST FastAPI
│
├── Testing
│   ├── test_all_tickers.py     # Population DB (60 tickers)
│   ├── test_db.py              # Tests DB fonctionnalité
│   └── test_api.py             # Tests API endpoints
│
├── Data
│   ├── stocks.db               # Base SQLite (gitignored)
│   └── working_tickers.txt     # Liste tickers (référence)
│
└── Docs
    ├── API_DOCUMENTATION.md    # API complète
    ├── PROJECT_OVERVIEW.md     # Vue d'ensemble
    ├── requirements.txt
    └── README.md
```

## 🎯 Tickers Disponibles

**60 tickers validés et opérationnels**

### Secteurs Couverts:
- 🏦 **Banques**: ATW (Attijariwafa), BOA (Bank of Africa), BCI, CIH
- 📱 **Telecom**: IAM (Maroc Telecom)
- 🏢 **Immobilier**: CIH, CDM
- 🏭 **Industrie**: ALM (Aluminium du Maroc), CTM
- 🏥 **Santé**: VCN (Vicenne), AKT
- ⚡ **Énergie**: GAZ, TGC
- 🍷 **Agro-alimentaire**: SNP
- Et 50+ autres

**Liste complète**: Voir `constants.py` (WORKING_TICKERS)
**Note**: Seuls les tickers validés sont utilisés pour optimiser les performances

## 📡 API REST - 8 Endpoints

### 1. Health Check
```bash
GET /health
```
Status API + nombre stocks en DB

### 2. Données Temps Réel
```bash
GET /stocks/{ticker}
# Exemple: GET /stocks/VCN
```
Dernières données (prix, variation, volume, etc.)

### 3. Historique
```bash
GET /stocks/{ticker}/history?days=30
# Exemple: GET /stocks/VCN/history?days=7
```
Données OHLCV sur N jours

### 4. Liste Complète
```bash
GET /stocks/list
```
Tous les stocks avec prix actuels

### 5. Statistiques Marché
```bash
GET /stats
```
Top gagnants et perdants du jour

### 6. Recherche
```bash
GET /stocks/search/{query}
# Exemple: GET /stocks/search/BANK
```
Recherche par ticker ou nom entreprise

### 7. Documentation Interactive
```
GET /docs      (Swagger UI)
GET /redoc     (ReDoc alternative)
```

## 💾 Base de Données

### SQLite (32 KB)

**Table: stocks** (60 records)
```
id | ticker | name | price | change_pct | volume | timestamp
```

**Table: history** (63+ records)
```
id | ticker | date | open | high | low | close | volume
```

**Indexes:**
- `ticker` (unique sur stocks)
- `ticker` + `date` (composite sur history)

## 📈 Performance

- **Scraper**: 1-2s par ticker (avec retry backoff)
- **API**: <100ms par requête
- **DB**: <50ms par query
- **Test complet**: ~4 minutes pour 73 tickers

## 🛠️ Stack Technique

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11+ |
| Framework | FastAPI + Uvicorn |
| Database | SQLite (MVP) / PostgreSQL (prod) |
| ORM | SQLAlchemy 2.0 |
| Scraping | Requests + Retry logic |
| Testing | pytest (à ajouter) |
| Documentation | Swagger/OpenAPI |

## 📖 Documentation Détaillée

Consultez les fichiers complets:
- **API_DOCUMENTATION.md** - Référence API complète
- **PROJECT_OVERVIEW.md** - Architecture & détails techniques

## 🔄 Workflow Git

```bash
# Initialiser repo
git init
git add .
git commit -m "Initial commit: Casablanca Stock Exchange API"

# Branche développement
git checkout -b develop
git checkout -b feature/dashboard
# ... développer
git push origin feature/dashboard
# ... PR review & merge
```

## 📋 Prochaines Étapes

- [x] ✅ Étape 1: Scraper données
- [x] ✅ Étape 2: Base SQLite
- [x] ✅ Étape 3: API REST
- [x] ✅ Étape 4: Tests
- [ ] Étape 5: Indicateurs techniques (RSI, MACD, MA)
- [ ] Étape 6: Système de scoring
- [ ] Étape 7: Job automatique (cron/scheduler)
- [ ] Étape 8: Dashboard React
- [ ] Étape 9: Intégration Telegram bot
- [ ] Étape 10: Déploiement production

## 🚀 Déploiement

### Local Development
```bash
uvicorn api:app --reload --port 8000
```

### Production (Gunicorn)
```bash
gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --port 8000
```

### Docker
```bash
docker build -t casablanca-api .
docker run -p 8000:8000 casablanca-api
```

## 🧪 Testing

```bash
# Test DB
python3 test_db.py

# Test tous tickers
python3 test_all_tickers.py --save

# Test API
python3 test_api.py
```

## 📞 Support

Pour des problèmes ou questions:
1. Vérifier les logs (`*.log`)
2. Consulter API_DOCUMENTATION.md
3. Tester avec Swagger UI (/docs)

## 📄 License

MIT - Libre d'utilisation

## 👤 Auteur

Projet personnel - Investisseur particulier
Casablanca, Maroc

---

**Status**: ✅ Production Ready (avec monitoring API)
**Version**: 1.0.1
**Last Update**: 21 Octobre 2025
**Tickers**: 60 validés
**API Monitoring**: ✅ Actif (build ID + structure)
