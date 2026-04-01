import streamlit as st
import barcode
from barcode.writer import ImageWriter
import io
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import urllib.parse

# Configuración de la página
st.set_page_config(page_title="Generador de Etiquetas", layout="centered")

st.title("Generador de Etiquetas 🏷️")
st.write("Ingresa el Nombre del Producto y su Código separados por una coma (,).")

# Área de texto con un ejemplo predeterminado
texto_entrada = st.text_area(
    "Formato: Nombre del Producto, CÓDIGO", 
    value="Jabón de Avena, JAB-001\nShampoo de Coco, SHA-002\nCrema Corporal, CREM-003",
    height=150
)

if st.button("Generar Archivo Word"):
    if texto_entrada.strip():
        # Crear documento de Word
        doc = Document()
        
        # Procesar línea por línea
        lineas = [linea.strip() for linea in texto_entrada.split('\n') if linea.strip()]
        
        # Clase del código de barras (Code128 acepta letras y números)
        code128 = barcode.get_barcode_class('code128')
        
        tarjetas_creadas = 0
        
        for linea in lineas:
            # Verificar que haya una coma para separar nombre y código
            if "," in linea:
                partes = linea.split(",", 1)
                nombre_producto = partes[0].strip()
                codigo_barras = partes[1].strip()
                
                # 1. Generar la imagen del código de barras
                buffer = io.BytesIO()
                mi_codigo = code128(codigo_barras, writer=ImageWriter())
                
                # Desactivamos el texto de la imagen para ponerlo nosotros en negritas en Word
                mi_codigo.write(buffer, options={
                    'write_text': False, 
                    'module_width': 0.3,
                    'module_height': 12,
                    'quiet_zone': 2
                })
                buffer.seek(0)
                
                # 2. Diseñar la tarjeta en Word
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                # Nombre del Producto en Negritas
                run_nombre = p.add_run(f"{nombre_producto}\n")
                run_nombre.bold = True
                run_nombre.font.size = Pt(16)
                
                # Insertar la imagen del código de barras (5x3 cm)
                run_img = p.add_run()
                run_img.add_picture(buffer, width=Cm(5), height=Cm(3))
                
                # Texto del Código de Barras en Negritas
                run_codigo = p.add_run(f"\n{codigo_barras}\n")
                run_codigo.bold = True
                run_codigo.font.size = Pt(14)
                
                # Separador visual entre tarjetas
                p.add_run("-" * 40 + "\n").font.size = Pt(8)
                
                tarjetas_creadas += 1

        if tarjetas_creadas > 0:
            # Guardar Word en memoria
            doc_buffer = io.BytesIO()
            doc.save(doc_buffer)
            doc_buffer.seek(0)
            
            st.success(f"¡Éxito! Se generaron {tarjetas_creadas} etiquetas.")
            
            # Contenedor para alinear los botones
            col1, col2 = st.columns(2)
            
            with col1:
                # Botón para descargar el Word
                st.download_button(
                    label="📥 Descargar Word",
                    data=doc_buffer,
                    file_name="etiquetas_productos.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            
            with col2:
                # Configurar enlace a WhatsApp (Número con Lada de México: 52 + 2283530069)
                numero_wa = "522283530069"
                mensaje = urllib.parse.quote("Hola, aquí tienes el archivo con las etiquetas generadas.")
                link_wa = f"https://wa.me/{numero_wa}?text={mensaje}"
                
                # Botón HTML personalizado para WhatsApp
                st.markdown(
                    f"""
                    <a href="{link_wa}" target="_blank" style="text-decoration: none;">
                        <button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%;">
                            📱 Enviar por WhatsApp
                        </button>
                    </a>
                    """, 
                    unsafe_allow_html=True
                )
        else:
            st.error("Por favor, asegúrate de usar el formato correcto: Nombre, Código")
    else:
        st.warning("El campo de texto está vacío.")
