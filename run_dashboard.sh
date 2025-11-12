#!/bin/bash
# Script de lancement du dashboard Streamlit

echo "🚀 Lancement du Trading Assistant Dashboard..."
echo ""
echo "📊 URL: http://localhost:8501"
echo "🛑 Arrêt: CTRL+C"
echo ""

# Ensure database has data
if [ ! -f stocks.db ] || [ ! -s stocks.db ]; then
    echo "⚠️  Base de données vide ou inexistante"
    echo "📦 Création de données de test..."
    python3 test_scoring.py > /dev/null 2>&1
    echo "✅ Données de test créées"
    echo ""
fi

# Launch Streamlit
streamlit run app.py --server.port 8501 --server.headless true
