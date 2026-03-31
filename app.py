import streamlit as st
import datetime
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Checklist con Alarmas", page_icon="✅", layout="centered")

# URLs de los sonidos (puedes cambiarlos por archivos locales o enlaces propios)
SONIDO_EXITO = "https://www.soundjay.com/buttons/sounds/button-09.mp3"
SONIDO_ALARMA = "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"

# Inicializar la base de datos temporal en session_state
if "tareas" not in st.session_state:
    st.session_state.tareas = []

st.title("✅ Checklist Interactivo")
st.markdown("Añade tus tareas, define una hora de aviso y escucha el sonido al completarlas.")

# ==========================================
# 1. FORMULARIO PARA AGREGAR TAREAS
# ==========================================
with st.form("nueva_tarea_form", clear_on_submit=True):
    col1, col2 = st.columns([3, 1])
    with col1:
        nueva_tarea = st.text_input("Nueva tarea", placeholder="Ej. Revisar inventario de vitrinas...")
    with col2:
        hora_alarma = st.time_input("Hora de alarma", datetime.datetime.now().time())
    
    submit = st.form_submit_button("Agregar Tarea")
    
    if submit and nueva_tarea:
        st.session_state.tareas.append({
            "id": len(st.session_state.tareas),
            "texto": nueva_tarea,
            "completada": False,
            "hora_alarma": hora_alarma.strftime("%H:%M")
        })
        st.success("Tarea agregada")

st.divider()

# ==========================================
# 2. MOSTRAR EL CHECKLIST
# ==========================================
if not st.session_state.tareas:
    st.info("No hay tareas pendientes. ¡Agrega una arriba!")
else:
    # Reproductor de sonido oculto para las tareas completadas
    reproducir_exito = st.empty()
    
    for i, tarea in enumerate(st.session_state.tareas):
        col_check, col_hora, col_del = st.columns([8, 2, 1])
        
        with col_check:
            # Usamos un key único para cada checkbox
            check = st.checkbox(tarea["texto"], value=tarea["completada"], key=f"check_{i}")
            
            # Si el estado del checkbox cambia a True (completado)
            if check and not tarea["completada"]:
                st.session_state.tareas[i]["completada"] = True
                # Inyectar audio que se reproduce automáticamente
                reproducir_exito.markdown(
                    f'<audio autoplay="true" src="{SONIDO_EXITO}"></audio>', 
                    unsafe_allow_html=True
                )
            # Si se desmarca
            elif not check and tarea["completada"]:
                st.session_state.tareas[i]["completada"] = False

        with col_hora:
            st.write(f"⏰ {tarea['hora_alarma']}")
            
        with col_del:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.tareas.pop(i)
                st.rerun()

# ==========================================
# 3. LÓGICA DE ALARMAS EN TIEMPO REAL (JavaScript)
# ==========================================
# Extraemos las alarmas de las tareas que NO están completadas
alarmas_pendientes = [t["hora_alarma"] for t in st.session_state.tareas if not t["completada"]]

# Inyectamos JavaScript para que el navegador verifique la hora cada segundo
# y reproduzca el sonido si coincide con alguna de las alarmas pendientes.
js_code = f"""
<script>
    const alarmas = {alarmas_pendientes};
    const sonidoAlarma = new Audio("{SONIDO_ALARMA}");
    let alarmasReproducidas = [];

    setInterval(() => {{
        let ahora = new Date();
        // Formatear hora a HH:MM para que coincida con Python
        let horas = String(ahora.getHours()).padStart(2, '0');
        let minutos = String(ahora.getMinutes()).padStart(2, '0');
        let horaActual = `${{horas}}:${{minutos}}`;

        if (alarmas.includes(horaActual) && !alarmasReproducidas.includes(horaActual)) {{
            sonidoAlarma.play();
            alarmasReproducidas.push(horaActual); // Evitar que suene varias veces en el mismo minuto
        }}
        
        // Limpiar el registro si cambiamos de minuto para que funcione al día siguiente
        if (!alarmas.includes(horaActual)) {{
            let index = alarmasReproducidas.indexOf(horaActual);
            if (index > -1) {{
                alarmasReproducidas.splice(index, 1);
            }}
        }}
    }}, 1000); // Se ejecuta cada 1000 milisegundos (1 segundo)
</script>
"""

st.components.v1.html(js_code, height=0, width=0)
