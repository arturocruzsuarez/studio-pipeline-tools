import subprocess
import os
import argparse  # <-- 1. Importamos la librería para argumentos


def apply_watermark(
    input_video, watermark_image, output_video, position, width, height
):
    """
    Aplica una marca de agua a un video usando FFmpeg,
    con posición y tamaño dinámicos.
    """

    print(f"Iniciando proceso para: {input_video}")

    # --- 2. Lógica para la POSICIÓN ---
    # Mapeamos las opciones legibles a la sintaxis de FFmpeg
    position_map = {
        "top-left": "10:10",
        "top-right": "main_w-overlay_w-10:10",
        "bottom-left": "10:main_h-overlay_h-10",
        "bottom-right": "main_w-overlay_w-10:main_h-overlay_h-10",
        "center": "(main_w-overlay_w)/2:(main_h-overlay_h)/2",
    }
    overlay_position = position_map.get(
        position, "main_w-overlay_w-10:main_h-overlay_h-10"
    )  # Default a bottom-right

    # --- 3. Lógica para el TAMAÑO (Scaling) ---
    # Construimos el string del filtro dinámicamente

    # Si el usuario especificó un tamaño, creamos un filtro de escalado
    if width and height:
        # [1:v] es la marca de agua. La escalamos y le damos un nombre [wm]
        scale_filter = f"[1:v]scale={width}:{height}[wm];"
        # El input para el overlay ya no es [1:v], sino la versión escalada 
        # [wm]
        overlay_input = "[0:v][wm]"
    else:
        # Si no hay tamaño, no hay filtro de escalado
        scale_filter = ""
        # El input para el overlay es el original [1:v]
        overlay_input = "[0:v][1:v]"

    # Unimos todo en el string final de -filter_complex
    filter_string = f"{scale_filter}{overlay_input}overlay={overlay_position}"

    # --- 4. Comando de FFmpeg Actualizado ---
    command = [
        "ffmpeg",
        "-i",
        input_video,
        "-i",
        watermark_image,
        "-filter_complex",
        filter_string,  # <-- Usamos nuestro string dinámico
        "-codec:a",
        "copy",
        output_video,
    ]

    try:
        if os.path.exists(output_video):
            os.remove(output_video)

        print("Ejecutando FFmpeg... (esto puede tardar unos segundos)")
        print(f"Comando: {' '.join(command)}")  # <-- Útil para depurar

        subprocess.run(command, check=True, capture_output=True, text=True)

        print(f"¡Éxito! Video guardado en: {output_video}")

    except subprocess.CalledProcessError as e:
        print("ERROR: FFmpeg falló.")
        print("Error de FFmpeg:\n", e.stderr)
    except FileNotFoundError:
        print("ERROR: No se pudo encontrar FFmpeg.")
        print("Asegúrate de que esté instalado y en tu PATH del sistema.")


# --- 5. Punto de entrada del Script (Aquí definimos los argumentos) ---
if __name__ == "__main__":

    # Configuramos el parser de argumentos
    parser = argparse.ArgumentParser(description="Aplica marca de agua a video")

    parser.add_argument(
        "-p",
        "--position",
        choices=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
        default="bottom-right",
        help="Posición de la marca de agua (default: bottom-right)",
    )

    parser.add_argument(
        "-w", "--width", type=int, help="Ancho deseado para la marca de agua (ej. 150)"
    )

    parser.add_argument(
        "-ht", "--height", type=int, help="Alto deseado para la marca de agua (ej. 50)"
    )

    # Parseamos los argumentos que el usuario escribió en la terminal
    args = parser.parse_args()

    # Define los nombres de tus archivos (aún hard-coded)
    INPUT_FILE = "input.mp4"
    WATERMARK_FILE = "watermark.png"
    OUTPUT_FILE = "output.mp4"

    if not os.path.exists(INPUT_FILE):
        print(f"Error: No se encuentra el archivo '{INPUT_FILE}'.")
    elif not os.path.exists(WATERMARK_FILE):
        print(f"Error: No se encuentra el archivo '{WATERMARK_FILE}'.")
    else:
        # ¡Llamamos a la función principal pasando los argumentos!
        apply_watermark(
            INPUT_FILE,
            WATERMARK_FILE,
            OUTPUT_FILE,
            args.position,
            args.width,
            args.height,
        )
