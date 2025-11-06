import gradio as gr

def some_function(input_text):
    return f"Received: {input_text}"

iface = gr.Interface(fn=some_function, inputs="text", outputs="text")
iface.launch(server_name="0.0.0.0", server_port=7860)
