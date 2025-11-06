import gradio as gr

# Define a simple Gradio interface
def echo(text):
    return f"You said: {text}"

interface = gr.Interface(fn=echo, inputs="text", outputs="text")
