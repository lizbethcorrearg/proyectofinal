# -*- coding: utf-8 -*-
"""PROYECTO

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/17Mi2xvT_Xs9vYqcXwvnCt-LP_RNOfiY7
"""

pip install ete3 plotly biopython gradio

from ete3 import Tree
import plotly.graph_objects as go
from Bio import Entrez
import gradio as gr

# Configuración de correo para NCBI
Entrez.email = "correalizbeth633@gmail.com"

# Función para obtener el árbol Newick desde NCBI
def fetch_tree_from_ncbi(organism_name):
    try:
        # Buscar el organismo en NCBI
        search_handle = Entrez.esearch(db="taxonomy", term=organism_name, retmode="xml")
        search_results = Entrez.read(search_handle)
        search_handle.close()

        if len(search_results["IdList"]) == 0:
            return None, f"No se encontraron resultados para '{organism_name}'."

        # Obtener datos de taxonomía
        tax_id = search_results["IdList"][0]
        fetch_handle = Entrez.efetch(db="taxonomy", id=tax_id, retmode="xml")
        tax_record = Entrez.read(fetch_handle)
        fetch_handle.close()

        # Crear el árbol Newick basado en la jerarquía
        lineage = tax_record[0]["LineageEx"]
        newick_tree = "(" + ",".join([node["ScientificName"] for node in lineage]) + ");"
        return newick_tree, None
    except Exception as e:
        return None, f"Error al obtener datos de NCBI: {str(e)}"

# Función para generar el árbol
def generate_tree(organism_name, branch_color, node_color, node_size, line_width, branch_distance):
    try:
        if organism_name:
            newick_data, error = fetch_tree_from_ncbi(organism_name)
            if error:
                return error, None, None, None
        else:
            return "Por favor, introduce un nombre de organismo.", None, None, None

        # Procesar el árbol Newick
        try:
            tree = Tree(newick_data)
        except Exception as e:
            return f"Error en el formato del árbol Newick: {str(e)}", None, None, None

        # Indicadores del árbol
        total_nodes = len(tree)
        leaf_nodes = sum(1 for node in tree if node.is_leaf())
        max_depth = max(tree.get_distance(node) for node in tree.traverse())
        total_branches = sum(1 for node in tree.traverse() if not node.is_leaf())

        ascii_tree = tree.get_ascii(show_internal=True)

        # Generar gráfico 3D con Plotly
        fig = go.Figure()

        # Coordenadas de nodos y ramas
        x, y, z = [], [], []
        for i, node in enumerate(tree.traverse("preorder")):
            x.append(node.dist)
            y.append(i)
            z.append(tree.get_distance(node))

        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers+lines',
            line=dict(color=branch_color, width=line_width),
            marker=dict(size=node_size, color=node_color),
            text=[node.name for node in tree.traverse()],
            hoverinfo="text"
        ))

        # Diseño de la gráfica
        fig.update_layout(
            title="Árbol Filogenético 3D",
            title_x=0.5,
            scene=dict(
                xaxis_title="Distancia de Ramas",
                yaxis_title="Índice de Nodo",
                zaxis_title="Profundidad del Árbol",
                xaxis=dict(backgroundcolor="white"),
                yaxis=dict(backgroundcolor="white"),
                zaxis=dict(backgroundcolor="white")
            ),
            plot_bgcolor="white",
            paper_bgcolor="lavender",
        )

        # Guardar el árbol en formato Newick
        output_file = "tree_output.newick"
        tree.write(outfile=output_file, format=1)

        # Indicadores en HTML con estilo
        indicator_text = (
            f"<div style='font-size: 16px; font-family: Arial, sans-serif;'>"
            f"<p style='color: darkgreen;'><b>Total de Nodos:</b> {total_nodes}</p>"
            f"<p style='color: darkorange;'><b>Total de Hojas:</b> {leaf_nodes}</p>"
            f"<p style='color: darkred;'><b>Profundidad:</b> {max_depth}</p>"
            f"<p style='color: darkblue;'><b>Total de Ramas:</b> {total_branches}</p>"
            f"</div>"
        )

        return ascii_tree, fig, output_file, indicator_text

    except Exception as e:
        return f"Error general al generar el árbol: {str(e)}", None, None, None

# Interfaz de usuario con Gradio
def dashboard_interface():
    return gr.Interface(
        fn=generate_tree,
        inputs=[
            gr.Textbox(label="Introducir nombre del organismo (Requerido)"),
            gr.ColorPicker(label="Color de las Ramas", value="#1f77b4"),
            gr.ColorPicker(label="Color de los Nodos", value="#d62728"),
            gr.Slider(minimum=5, maximum=20, step=1, label="Tamaño de los Nodos", value=10),
            gr.Slider(minimum=1, maximum=10, step=1, label="Grosor de las Ramas", value=2),
            gr.Slider(minimum=0.1, maximum=2, step=0.1, label="Distancia entre Ramas", value=1),
        ],
        outputs=[
            gr.Textbox(label="Árbol en formato ASCII", elem_id="ascii-tree", interactive=False),
            gr.Plot(label="Árbol Filogenético Gráfico 3D", elem_id="phylogenetic-plot"),
            gr.File(label="Descargar árbol en formato Newick", elem_id="download-tree"),
            gr.HTML(label="Indicadores:", elem_id="indicators")
        ],
        title="Generador de Árbol Filogenético",
        description="Introduce el nombre de un organismo y visualiza el árbol filogenético en 3D."
    )

# Ejecutar la interfaz de Gradio
dashboard_interface().launch(share=True)

"""EQUIPO:  
Correa Arguelles Lizbeth Alexandra
Perez Silva Brenda Nayelli
Tostado Bórquez Jorge Francisco
"""