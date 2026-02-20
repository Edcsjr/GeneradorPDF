from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from PIL import Image
import os

def build_pdf(dest_path, data):
    c = canvas.Canvas(dest_path, pagesize=A4)
    width, height = A4
    margin = 1.5 * cm

    # --- 1. Logo ---
    if data['logo'] and os.path.exists(data['logo']):
        c.drawImage(data['logo'], margin, height - 3.5 * cm, width=4.5*cm, height=2.5*cm, preserveAspectRatio=True, mask='auto')
    
    # --- 2. Encabezado ---
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.black)
    c.drawString(margin, height - 4.8 * cm, data['empresa'].upper())
    
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.grey)
    c.drawRightString(width - margin, height - 2 * cm, f"FECHA EMISIÓN: {data['emision']}")
    c.drawRightString(width - margin, height - 2.5 * cm, f"FECHA VENCIMIENTO: {data['vencimiento']}")

# --- 3. Tabla Contenedora (Con Bordes Redondeados) ---
    table_top = height - 5.5 * cm
    table_bottom = 3.5 * cm
    table_width = width - (2 * margin)
    r = 10  # El radio de 10px que solicitaste

    # Rectángulo principal con bordes redondeados
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.roundRect(margin, table_bottom, table_width, table_top - table_bottom, radius=r, stroke=1, fill=0)

    # Encabezado oscuro con bordes redondeados (solo arriba)
    # Para que encaje perfecto, dibujamos el encabezado y luego "limpiamos" la parte de abajo
    c.setFillColor(colors.black)
    c.roundRect(margin, table_top - 0.8 * cm, table_width, 0.8 * cm, radius=r, stroke=0, fill=1)
    
    # Truco visual: Dibujamos un rectángulo negro pequeño abajo del encabezado 
    # para que las esquinas de abajo del encabezado sean rectas y las de arriba redondeadas
    c.rect(margin, table_top - 0.8 * cm, table_width, 0.4 * cm, stroke=0, fill=1)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    y_head = table_top - 0.5 * cm
    c.drawString(margin + 0.3*cm, y_head, "#")
    c.drawString(margin + 1.2*cm, y_head, "VISTA")
    c.drawString(margin + 3.2*cm, y_head, "DESCRIPCIÓN")
    c.drawRightString(width - margin - 5.5*cm, y_head, "CANT.")
    c.drawRightString(width - margin - 3.0*cm, y_head, "PRECIO")
    c.drawRightString(width - margin - 0.4*cm, y_head, "SUBTOTAL")

    # --- 4. Listado de Ítems ---
    y_current = table_top - 0.8 * cm # Empezamos justo debajo del encabezado negro
    row_height = 1.6 * cm # Altura amplia para evitar solapamiento
    img_size = 1.2 * cm   # Tamaño de la imagen
    total_general = 0

    for i, item in enumerate(data['items']):
        # Verificar espacio (si la siguiente fila se sale del cuadro)
        if y_current - row_height < table_bottom:
            c.showPage()
            y_current = height - 3 * cm
            # Aquí se podría redibujar el marco, pero para 1 pag es ideal

        # Dibujar línea divisoria inferior (excepto en el último ítem para no pisar el borde)
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.3)
        c.line(margin, y_current - row_height, width - margin, y_current - row_height)

        # Determinar el centro vertical de la fila para alinear texto e imagen
        center_y = y_current - (row_height / 2)

        # ID del ítem
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.black)
        c.drawString(margin + 0.3*cm, center_y - 0.1*cm, str(i+1).zfill(2))

        # Imagen: Centrada en su cuadrado 1.2 x 1.2
        if item['img'] and os.path.exists(item['img']):
            try:
                # Dibujamos la imagen centrada verticalmente en la fila
                # El y de la imagen es y_current (techo) menos el alto de la fila más el margen
                img_y = y_current - row_height + (row_height - img_size) / 2
                c.drawImage(item['img'], margin + 1.2*cm, img_y, width=img_size, height=img_size, preserveAspectRatio=True)
            except:
                pass
        
        # Texto: Descripción (Alineada al centro vertical)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        desc = item['desc'][:60] + "..." if len(item['desc']) > 60 else item['desc']
        c.drawString(margin + 3.2*cm, center_y - 0.1*cm, desc)

        # Valores
        c.drawRightString(width - margin - 5.5*cm, center_y - 0.1*cm, f"{item['cant']:.0f}")
        c.drawRightString(width - margin - 3.0*cm, center_y - 0.1*cm, f"{item['monto']:,.2f}")
        
        sub = item['cant'] * item['monto']
        total_general += sub
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(width - margin - 0.4*cm, center_y - 0.1*cm, f"{sub:,.2f}")

        # Pasamos a la siguiente fila restando la altura completa
        y_current -= row_height

    # --- 5. Footer ---
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - margin, table_bottom - 1 * cm, f"TOTAL GENERAL: ${total_general:,.2f}")
    
    c.save()