import streamlit as st
from pptx import Presentation
from pptx.util import Inches, Pt
from moviepy.editor import ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip, AudioFileClip
from gtts import gTTS
from PIL import Image
import io
import tempfile
import os

# Configuración de la página adaptada para Champlitte
st.set_page_config(page_title="Capacitación Champlitte", layout="wide", page_icon="🥐")

st.title("🥐 Generador de Capacitaciones - Pastelería Champlitte")
st.write("Crea manuales operativos y videos con voz en off al instante. Ideal para explicar procesos en el sistema, cobros o armado de productos.")

# --- ENTRADAS DEL USUARIO ---
col1, col2 = st.columns(2)

with col1:
    st.info("💡 **Tip:** Escribe cada paso en una nueva línea. El sistema asignará una línea de texto a cada imagen que subas.")
    instrucciones = st.text_area(
        "Pasos del Proceso (Una línea por imagen)", 
        placeholder="Ejemplo:\nPaso 1: Entra al sistema e ingresa tu usuario.\nPaso 2: Haz clic en el módulo de 'Ventas'.\nPaso 3: Selecciona el producto y cobra el total en pesos.",
        height=200
    )

with col2:
    imagenes_subidas = st.file_uploader(
        "Sube las capturas de pantalla o fotos (en orden)", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True
    )

# --- FUNCIÓN: DIVIDIR TEXTO ---
def obtener_fragmentos_texto(texto, num_imagenes):
    """Asigna el texto a las imágenes. Prioriza separar por saltos de línea."""
    if not texto.strip():
        return ["Explicación visual del proceso."] * max(1, num_imagenes)
        
    lineas = [linea.strip() for linea in texto.split('\n') if linea.strip()]
    
    # Si el usuario escribió exactamente el mismo número de líneas que de imágenes
    if len(lineas) >= num_imagenes:
        return lineas[:num_imagenes]
    
    # Si hay menos líneas que imágenes, rellenamos las últimas con silencio/texto vacío
    fragmentos = lineas.copy()
    while len(fragmentos) < num_imagenes:
        fragmentos.append("Siguiente paso del proceso.")
    return fragmentos

# --- FUNCIÓN: CREAR POWERPOINT ---
def crear_pptx(texto, imagenes):
    prs = Presentation()
    fragmentos = obtener_fragmentos_texto(texto, len(imagenes))
    
    # Portada
    slide_layout = prs.slide_layouts[0] 
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Manual Operativo"
    slide.placeholders[1].text = "Pastelería Champlitte"

    # Diapositivas de contenido
    for i, img in enumerate(imagenes):
        # Usar layout de título y contenido
        slide = prs.slides.add_slide(prs.slide_layouts[5]) 
        slide.shapes.title.text = f"Paso {i + 1}"
        
        # Añadir la imagen
        img_stream = io.BytesIO(img.getvalue())
        pic = slide.shapes.add_picture(img_stream, Inches(1), Inches(1.5), height=Inches(4))
        
        # Añadir cuadro de texto explicativo debajo de la imagen
        txBox = slide.shapes.add_textbox(Inches(1), Inches(5.8), Inches(8), Inches(1))
        tf = txBox.text_frame
        p = tf.add_paragraph()
        p.text = fragmentos[i]
        p.font.size = Pt(24)

    pptx_io = io.BytesIO()
    prs.save(pptx_io)
    pptx_io.seek(0)
    return pptx_io

# --- FUNCIÓN: CREAR VIDEO CON VOZ Y SUBTÍTULOS ---
def crear_video_capacitacion(texto, imagenes):
    clips = []
    temp_files = [] 
    fragmentos = obtener_fragmentos_texto(texto, len(imagenes))

    for i, img in enumerate(imagenes):
        texto_mostrar = fragmentos[i]

        # 1. Audio gTTS (Voz en off)
        tts = gTTS(text=texto_mostrar, lang='es', tld='com.mx') 
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_audio.name)
        temp_audio.close()
        temp_files.append(temp_audio.name)
        
        clip_audio = AudioFileClip(temp_audio.name)
        # Darle 1 segundo extra para que el usuario asimile el paso
        duracion_clip = clip_audio.duration + 1.0 
        
        # 2. Imagen
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_img.write(img.getvalue())
        temp_img.close()
        temp_files.append(temp_img.name)
        
        clip_img = ImageClip(temp_img.name).set_duration(duracion_clip).resize(height=1080)
        
        # 3. Subtítulos
        try:
            clip_texto = TextClip(
                texto_mostrar, 
                fontsize=45, 
                color='white', 
                bg_color='rgba(0,0,0,0.7)', 
                size=(clip_img.w - 100, None), 
                method='caption',
                align='center'
            )
            # Colocamos el texto en la parte inferior
            clip_texto = clip_texto.set_position(('center', 850)).set_duration(duracion_clip)
            clip_visual = CompositeVideoClip([clip_img, clip_texto])
        except Exception:
            clip_visual = clip_img
            
        # 4. Unir todo
        clip_final = clip_visual.set_audio(clip_audio)
        clips.append(clip_final)
        
    if clips:
        video_final = concatenate_videoclips(clips, method="compose")
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        
        # Exportar
        video_final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        
        # Limpiar temporales
        for tf in temp_files:
            try:
                os.remove(tf)
            except:
                pass
                
        return output_path
    return None

# --- BOTONES DE EJECUCIÓN ---
st.markdown("---")
if st.button("🚀 Generar Material de Capacitación", type="primary"):
    if not imagenes_subidas:
        st.error("Por favor, sube al menos una imagen o captura de pantalla.")
    else:
        # Pestañas para organizar los resultados
        tab1, tab2 = st.tabs(["📊 Presentación PowerPoint", "🎬 Video Explicativo"])
        
        with tab1:
            with st.spinner("Armando el manual en PowerPoint..."):
                pptx_file = crear_pptx(instrucciones, imagenes_subidas)
                st.success("¡Manual listo!")
                st.download_button(
                    label="📥 Descargar Manual (.pptx)",
                    data=pptx_file,
                    file_name="manual_operativo_champlitte.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
                
        with tab2:
            with st.spinner("Grabando la voz en off y renderizando el video (esto tomará unos momentos)..."):
                video_path = crear_video_capacitacion(instrucciones, imagenes_subidas)
                
                if video_path:
                    st.success("¡Video generado exitosamente!")
                    with open(video_path, "rb") as v_file:
                        st.download_button(
                            label="🎬 Descargar Video de Capacitación (.mp4)",
                            data=v_file,
                            file_name="capacitacion_video_champlitte.mp4",
                            mime="video/mp4"
                        )
                    st.video(video_path)
                    os.remove(video_path)