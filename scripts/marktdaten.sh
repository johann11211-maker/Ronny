#!/usr/bin/env bash
# Holt einen Marktdaten-Schnappschuss fuer die Bitcoin-Ereignispruefung.
# Nutzung: scripts/marktdaten.sh
# Gibt Klartext aus. Einzelne Ausfaelle sind kein Fehler: fehlende Werte
# werden als "n/v" gemeldet, damit die Pruefung mit Websuche weiterlaufen kann.

set -uo pipefail

CG="https://api.coingecko.com/api/v3"
UA="Mozilla/5.0 (compatible; bitcoin-ereignis-watch/1.0)"

# CoinGecko drosselt bei schnell aufeinanderfolgenden Anfragen (HTTP 429).
# Darum: bis zu 4 Versuche mit wachsender Wartezeit.
hole() {
  local url="$1" versuch antwort
  for versuch in 1 2 3 4; do
    antwort=$(curl -sS --max-time 30 -A "$UA" "$url" 2>/dev/null)
    if [ -n "$antwort" ] && ! printf '%s' "$antwort" | grep -q '"error_code":429'; then
      printf '%s' "$antwort"
      return 0
    fi
    sleep $((versuch * 4))
  done
  return 1
}

jq_wert() { printf '%s' "$1" | python3 -c "import sys,json;d=json.load(sys.stdin);print(eval(sys.argv[1],{'d':d}))" "$2" 2>/dev/null || echo "n/v"; }

echo "=== Marktdaten-Schnappschuss ==="
echo "Zeitpunkt (UTC):    $(date -u '+%Y-%m-%d %H:%M')"
echo "Zeitpunkt (Berlin): $(TZ=Europe/Berlin date '+%Y-%m-%d %H:%M %Z')"
echo

# --- Bitcoin-Preis, 24h und 7d ---
preis=$(hole "$CG/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=true&include_24hr_change=true")
if [ -n "${preis:-}" ]; then
  echo "BTC Preis (USD):    $(jq_wert "$preis" "round(d['bitcoin']['usd'])")"
  echo "BTC 24h-Aenderung:  $(jq_wert "$preis" "round(d['bitcoin']['usd_24h_change'],2)") %"
else
  echo "BTC Preis (USD):    n/v (API nicht erreichbar)"
fi
sleep 3

verlauf=$(hole "$CG/coins/bitcoin/market_chart?vs_currency=usd&days=7&interval=daily")
if [ -n "${verlauf:-}" ]; then
  echo "BTC 7d-Aenderung:   $(jq_wert "$verlauf" "round((d['prices'][-1][1]/d['prices'][0][1]-1)*100,2)") %"
else
  echo "BTC 7d-Aenderung:   n/v"
fi
sleep 3

# --- 52-Wochen-Spanne und Allzeithoch ---
detail=$(hole "$CG/coins/bitcoin?localization=false&tickers=false&community_data=false&developer_data=false")
if [ -n "${detail:-}" ]; then
  echo "Allzeithoch (USD):  $(jq_wert "$detail" "round(d['market_data']['ath']['usd'])") (Abstand: $(jq_wert "$detail" "round(d['market_data']['ath_change_percentage']['usd'],1)") %)"
  echo "52W Hoch/Tief:      $(jq_wert "$detail" "round(d['market_data']['high_24h']['usd'])") / $(jq_wert "$detail" "round(d['market_data']['low_24h']['usd'])") (24h)"
else
  echo "Allzeithoch (USD):  n/v"
fi
sleep 3

# --- Gesamtmarkt ---
global=$(hole "$CG/global")
if [ -n "${global:-}" ]; then
  echo "Kryptomarkt gesamt: $(jq_wert "$global" "round(d['data']['total_market_cap']['usd']/1e12,3)") Billionen USD"
  echo "BTC-Dominanz:       $(jq_wert "$global" "round(d['data']['market_cap_percentage']['btc'],1)") %"
else
  echo "Kryptomarkt gesamt: n/v"
fi

# --- Angst-und-Gier-Index ---
fng=$(hole "https://api.alternative.me/fng/?limit=8")
if [ -n "${fng:-}" ]; then
  echo "Angst & Gier heute: $(jq_wert "$fng" "d['data'][0]['value']+' ('+d['data'][0]['value_classification']+')'")"
  echo "Angst & Gier -7d:   $(jq_wert "$fng" "d['data'][-1]['value']+' ('+d['data'][-1]['value_classification']+')'")"
else
  echo "Angst & Gier:       n/v"
fi

echo
echo "Hinweis: Diese Zahlen sind nur die Vorpruefung. Ob ein Ereignis"
echo "meldepflichtig ist, entscheidet zusaetzlich die Nachrichtenlage."
