#!/usr/bin/env python3
"""
Prueba simple de Google Gemini API - GRATIS y generoso
"""

from dotenv import load_dotenv
load_dotenv()

import requests
import json
import os

def test_gemini_simple():
    """Prueba muy simple de Gemini API"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No se encontró GEMINI_API_KEY")
        return
    
    print("🤖 PRUEBA SIMPLE DE GOOGLE GEMINI API")
    print("=" * 50)
    print("✅ Gemini es GRATIS y tiene límites generosos!")
    
    # URL de la API de Gemini - MODELO ACTUALIZADO
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # Prompt simple
    payload = {
        "contents": [{
            "parts": [{
                "text": "Eres un analista empresarial. En una frase corta: ¿qué significa vender $15,000 en un mes para una empresa pequeña?"
            }]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 100
        }
    }
    
    try:
        print("📤 Enviando prompt a Gemini...")
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0]['content']['parts'][0]['text']
                
                print("✅ ¡ÉXITO! Respuesta de Gemini:")
                print("-" * 40)
                print(f"🎯 {content}")
                print("-" * 40)
                print("💰 Costo: $0.00 (GRATIS)")
                print("🚀 ¡Gemini funciona perfectamente!")
                
            else:
                print("⚠️  Respuesta sin contenido válido")
                print(f"📄 Respuesta completa: {result}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_gemini_simple()
