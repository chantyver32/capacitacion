import streamlit as st
import barcode
from barcode.writer import ImageWriter
import io
import base64
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(page_title="Generador de Accesos", layout="centered")

st.title("Generador de Código de Barras Elegante")
st.write("Ingresa el texto para generar la tarjeta de acceso imprimible.")

# Controles de Streamlit
texto_entrada = st.text_input("Código o texto (letras y números):", value="ESTRELLA-2026")

if texto_entrada:
    # 1. Generar el código de barras (Formato Code128)
    code128 = barcode.get_barcode_class('code128')
    
    # Usamos un buffer de memoria en lugar de guardar un archivo físico
    buffer = io.BytesIO()
    
    # Generar la imagen con un diseño limpio
    mi_codigo = code128(texto_entrada, writer=ImageWriter())
    mi_codigo.write(buffer, options={
        'module_width': 0.25,
        'module_height': 10,
        'font_size': 8,
        'text_distance': 4,
        'quiet_zone': 2
    })
    
    # 2. Convertir la imagen a Base64 para incrustarla en HTML
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    img_data_uri = f"data:image/png;base64,{img_str}"

    # 3. Plantilla Elegante (HTML/CSS)
    html_template = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lato:wght@300;400&display=swap" rel="stylesheet">
        <style>
            :root {{
                --gold: #c5a059;
                --dark: #222222;
                --bg: #fcfcfc;
            }}
            body {{
                font-family: 'Lato', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                margin: 0;
                padding: 20px;
                background-color: transparent;
            }}
            .elegant-card {{
                border: 2px solid var(--gold);
                padding: 4px;
                width: 450px;
                height: 300px;
                background: var(--bg);
                box-sizing: border-box;
                margin-bottom: 20px;
            }}
            .elegant-inner {{
                border: 1px solid var(--gold);
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 20px;
                box-sizing: border-box;
                text-align: center;
            }}
            .elegant-title {{
                font-family: 'Playfair Display', serif;
                font-size: 22px;
                color: var(--dark);
                margin-bottom: 5px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            .elegant-subtitle {{
                font-family: 'Playfair Display', serif;
                font-style: italic;
                font-size: 14px;
                color: #666;
                margin-bottom: 20px;
            }}
            .barcode-container {{
                background: white;
                padding: 10px 20px;
                border: 1px solid #eee;
                box-shadow: 0 4px 10px rgba(0,0,0,0.03);
                display: flex;
                justify-content: center;
            }}
            .barcode-container img {{
                max-width: 100%;
                height: auto;
            }}
            .elegant-footer {{
                font-size: 11px;
                color: var(--dark);
                margin-top: 20px;
                letter-spacing: 1px;
                text-transform: uppercase;
            }}
            .print-btn {{
                background-color: var(--gold);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                font-family: 'Lato', sans-serif;
                transition: background 0.3s;
            }}
            .print-btn:hover {{
                background-color: #a88544;
            }}
            /* Estilos específicos para la hora de imprimir */
            @media print {{
                body {{
                    padding: 0;
                    margin: 0;
                    background: white;
                }}
                .print-btn {{
                    display: none !important; /* Oculta el botón al imprimir */
                }}
                .elegant-card {{
                    margin: 0 auto; /* Centra la tarjeta en la hoja impresa */
                }}
            }}
        </style>
    </head>
    <body>
        <div class="elegant-card">
            <div class="elegant-inner">
                <div class="elegant-title">Código de Acceso</div>
                <div class="elegant-subtitle">Presente este código al ingresar</div>
                
                <div class="barcode-container">
                    <img src="{img_data_uri}" alt="Código de Barras">
                </div>
                
                <div class="elegant-footer">Documento Oficial</div>
            </div>
        </div>
        
        <button class="print-btn" onclick="window.print()">🖨️ Imprimir Plantilla</button>
    </body>
    </html>
    """

    # 4. Mostrar el HTML dentro de Streamlit
    components.html(html_template, height=450)
